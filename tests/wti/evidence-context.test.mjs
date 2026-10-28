import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const source = readFileSync(new URL('../../js/core.js', import.meta.url), 'utf8');

function contextFor(countries) {
  const sandbox = { window: { WTI_DATA: { countries } }, document: { addEventListener() {} } };
  vm.runInNewContext(`${source}\nwindow.subject = WTI;`, sandbox);
  return sandbox.window.subject.evidenceContext();
}

test('reports actual fallback and neutral-only counts without equating rows to evidence quality', () => {
  const text = contextFor({
    AA: { events: [{ category: 'neutral', attribution_method: 'heuristic-v1' }] },
    BB: { events: [{ category: 'conflict', attribution_method: 'openrouter' }] },
    CC: { events: [] },
  });
  assert.match(text, /1 of 2 retained events/);
  assert.match(text, /1 country row contains only events classified as neutral/);
  assert.match(text, /not the completeness or reliability/);
});

test('handles missing event details without presenting invented counts', () => {
  assert.match(contextFor({ AA: { events: [] } }), /No event attribution details/);
});
