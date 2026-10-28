import assert from 'node:assert/strict';
import test from 'node:test';
import { versionAssets } from '../../scripts/version-assets.mjs';

test('deployed URLs change with source content and replace old versions', () => {
  const html = '<script src="wti_data.js"></script><script src="js/core.js?v=old"></script>';
  const first = versionAssets(html, { 'wti_data.js': 'first', 'js/core.js': 'script' });
  const second = versionAssets(html, { 'wti_data.js': 'second', 'js/core.js': 'script' });
  assert.match(first, /wti_data\.js\?v=[a-f0-9]{16}/);
  assert.match(first, /core\.js\?v=[a-f0-9]{16}/);
  assert.notEqual(first, second);
  assert.equal(versionAssets(first, { 'wti_data.js': 'first', 'js/core.js': 'script' }), first);
  assert.throws(() => versionAssets(html, { 'absent.js': 'script' }), /Expected one reference/);
});
