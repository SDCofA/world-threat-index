import json
import shutil
import subprocess
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = json.loads((ROOT / "wti_data.json").read_text(encoding="utf-8"))


def _run_node(source):
    node = shutil.which("node")
    assert node, "Node.js is required for focused frontend behavior probes"
    completed = subprocess.run(
        [node, "-e", textwrap.dedent(source)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_generated_snapshot_locks_country_group_and_ranking_contracts():
    assert DATA["meta"]["countries_total"] == 195
    assert DATA["meta"]["countries_active"] == 195
    assert DATA["meta"]["coverage_ratio"] == 1.0
    assert len(DATA["countries"]) == 195
    assert len(DATA["groups"]) == 13
    assert len(DATA["rankings_table"]) == 195

    assert set(DATA) == {
        "meta",
        "countries",
        "groups",
        "rankings",
        "rankings_table",
        "methodology",
    }
    assert all(
        set(row) == {"iso2", "name", "index", "status"}
        for row in DATA["rankings_table"]
    )
    assert all(
        {"name", "index", "raw_score", "status", "events"} <= set(country)
        for country in DATA["countries"].values()
    )
    assert all(
        {"name", "index", "status", "member_count", "active_members", "members", "weighting"}
        <= set(group)
        for group in DATA["groups"].values()
    )


def test_search_filter_row_selection_and_status_palette_are_live():
    payload = _run_node(
        r"""
        const fs = require('fs');
        const vm = require('vm');
        const data = JSON.parse(fs.readFileSync('wti_data.json', 'utf8'));
        const table = {
          html: '',
          rows: [],
          set innerHTML(value) {
            this.html = value;
            this.rows = [...value.matchAll(/<tr data-iso="([^"]+)"/g)].map(match => {
              const listeners = {};
              return {
                dataset: { iso: match[1] },
                addEventListener(name, handler) { listeners[name] = handler; },
                click() { listeners.click?.(); },
              };
            });
          },
          get innerHTML() { return this.html; },
          querySelectorAll() { return this.rows; },
        };
        const search = {
          handler: null,
          addEventListener(name, handler) { if (name === 'input') this.handler = handler; },
        };
        const selected = [];
        global.window = {
          WTIMap: { selectCountry(iso) { selected.push(iso); } },
          WTI_DATA: data,
        };
        global.document = {
          addEventListener(name, handler) { if (name === 'DOMContentLoaded') handler(); },
          getElementById(id) {
            if (id === 'rankings-table') return table;
            if (id === 'country-search') return search;
            return { textContent: '', className: '' };
          },
        };
        vm.runInThisContext(fs.readFileSync('js/core.js', 'utf8'), { filename: 'js/core.js' });
        global.WTI = WTI;
        vm.runInThisContext(fs.readFileSync('js/rankings.js', 'utf8'), { filename: 'js/rankings.js' });

        const initialRows = table.querySelectorAll();
        initialRows[0].click();
        search.handler({ target: { value: 'türkiye' } });
        const filteredRows = table.querySelectorAll();
        filteredRows[0].click();
        console.log(JSON.stringify({
          initialRows: initialRows.length,
          filteredRows: filteredRows.length,
          filteredIso: filteredRows[0].dataset.iso,
          selected,
          colors: [WTI.colorForIndex(4), WTI.colorForIndex(5), WTI.colorForIndex(8)],
          statuses: [
            WTI.statusClass('STABLE'),
            WTI.statusClass('ELEVATED'),
            WTI.statusClass('CRITICAL'),
          ],
        }));
        """
    )

    assert payload == {
        "initialRows": 195,
        "filteredRows": 1,
        "filteredIso": "TR",
        "selected": [DATA["rankings_table"][0]["iso2"], "TR"],
        "colors": ["#6fae7e", "#d8a13f", "#cf5b4e"],
        "statuses": ["stable", "elevated", "critical"],
    }


def test_assessment_metadata_and_copy_do_not_claim_a_task3_forecast():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    methodology = (ROOT / "docs/wti-methodology.md").read_text(encoding="utf-8")

    assert DATA["meta"]["record_type"] == "assessment"
    assert DATA["meta"]["issued_at"] == DATA["meta"]["generated_at"]
    assert DATA["methodology"]["methodology_url"].startswith("https://")
    assert DATA["methodology"]["evidence_url_field"] == "countries.*.events[].link"
    assert DATA["methodology"]["forecast_classification"] == "not-a-forecast"
    assert "Forecasts and model-derived scores are probabilistic" not in readme
    assert "does not publish Task 3 forecast records" in readme
    assert "https://github.com/SDCofA/border-neighbor-threat-index" in readme
    for field in (
        "target",
        "issuedAt",
        "dataCutoff",
        "horizon",
        "distribution",
        "uncertainty",
        "assumptions",
        "method",
        "resolutionCriteria",
        "provenance",
    ):
        assert f"`{field}`" in methodology
    assert "https://www.gdeltproject.org/" in methodology
