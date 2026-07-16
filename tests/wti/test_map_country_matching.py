import json
import shutil
import subprocess
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FALLBACK_FILL = "#2a3140"


def _exercise_real_map_module():
    node = shutil.which("node")
    assert node, "Node.js is required to execute the frontend map contract"

    harness = textwrap.dedent(
        r"""
        const fs = require('fs');
        const vm = require('vm');

        (async () => {
          const currentFeature = {
            properties: {
              'ISO3166-1-Alpha-2': 'ID',
              ISO_A2: 'PK',
            },
          };
          const legacyA2Feature = { properties: { ISO_A2: 'pk' } };
          const legacyEhFeature = { properties: { ISO_A2_EH: ' tr ' } };
          const invalidPrimaryWithFallback = {
            properties: {
              'ISO3166-1-Alpha-2': '-99',
              ISO_A2: ' pk ',
            },
          };
          const invalidFeature = {
            properties: {
              'ISO3166-1-Alpha-2': ' ',
              ISO_A2: '-99',
              ISO_A2_EH: ' -99 ',
            },
          };
          const missingFeature = { properties: {} };

          const attributes = {};
          const handlers = {};
          const pathSelection = {
            data() { return this; },
            join() { return this; },
            attr(name, value) {
              attributes[name] = value;
              return this;
            },
            on(name, handler) {
              handlers[name] = handler;
              return this;
            },
          };
          const svg = {
            selectAll() { return pathSelection; },
            append() {
              throw new Error('Unexpected map fallback while exercising successful render');
            },
          };

          const colorCalls = [];
          global.window = {};
          global.document = { addEventListener() {} };
          global.WTI = {
            data: { countries: { ID: { index: 6.2 }, PK: { index: 5.1 }, TR: { index: 4.4 } } },
            getIndex(country) { return country.index; },
            colorForIndex(index) {
              colorCalls.push(index);
              return 'resolved:' + index;
            },
          };
          global.d3 = {
            select() { return svg; },
            geoNaturalEarth1() {
              return { fitSize() { return this; } };
            },
            geoPath() { return () => ''; },
            async json() { return { features: [currentFeature] }; },
          };

          vm.runInThisContext(
            fs.readFileSync('js/map.js', 'utf8'),
            { filename: 'js/map.js' },
          );

          const map = window.WTIMap;
          const originalResolver = typeof map.resolveFeatureIso === 'function'
            ? map.resolveFeatureIso.bind(map)
            : () => null;
          let resolverCalls = 0;
          map.resolveFeatureIso = feature => {
            resolverCalls += 1;
            return originalResolver(feature);
          };

          const selected = [];
          map.selectCountry = iso => selected.push(iso);
          await map.init();

          resolverCalls = 0;
          const currentFill = attributes.fill(currentFeature);
          const fillResolverCalls = resolverCalls;

          resolverCalls = 0;
          handlers.click({}, currentFeature);
          const clickResolverCalls = resolverCalls;

          const currentDataIso = attributes['data-iso']
            ? attributes['data-iso'](currentFeature)
            : null;
          const invalidDataIso = attributes['data-iso']
            ? attributes['data-iso'](invalidFeature)
            : null;
          const invalidFill = attributes.fill(invalidFeature);
          handlers.click({}, invalidFeature);

          console.log(JSON.stringify({
            resolver: {
              current: originalResolver(currentFeature),
              legacyA2: originalResolver(legacyA2Feature),
              legacyEh: originalResolver(legacyEhFeature),
              invalidPrimaryWithFallback: originalResolver(invalidPrimaryWithFallback),
              invalid: originalResolver(invalidFeature),
              missing: originalResolver(missingFeature),
            },
            render: {
              currentDataIso,
              invalidDataIso,
              currentFill,
              invalidFill,
              fillResolverCalls,
              clickResolverCalls,
              selected,
              colorCalls,
            },
          }));
        })().catch(error => {
          console.error(error);
          process.exitCode = 1;
        });
        """
    )
    completed = subprocess.run(
        [node, "-e", harness],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_live_and_legacy_geojson_identifiers_drive_fill_and_selection():
    result = _exercise_real_map_module()

    assert result["resolver"] == {
        "current": "ID",
        "legacyA2": "PK",
        "legacyEh": "TR",
        "invalidPrimaryWithFallback": "PK",
        "invalid": None,
        "missing": None,
    }

    render = result["render"]
    assert render["currentDataIso"] == "ID"
    assert render["currentFill"] == "resolved:6.2"
    assert render["currentFill"] != FALLBACK_FILL
    assert render["invalidDataIso"] is None
    assert render["invalidFill"] == FALLBACK_FILL
    assert render["selected"] == ["ID"]
    assert render["colorCalls"] == [6.2]
    assert render["fillResolverCalls"] == 1
    assert render["clickResolverCalls"] == 1
