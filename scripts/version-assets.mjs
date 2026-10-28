import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export function versionAssets(html, assets) {
  for (const [asset, content] of Object.entries(assets)) {
    const hash = createHash('sha256').update(content).digest('hex').slice(0, 16);
    const escaped = asset.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const pattern = new RegExp(`(src=["'](?:\\./)?${escaped})(?:\\?[^"']*)?(["'])`, 'g');
    let count = 0;
    html = html.replace(pattern, (_, prefix, quote) => {
      count += 1;
      return `${prefix}?v=${hash}${quote}`;
    });
    if (count !== 1) throw new Error(`Expected one reference to ${asset}, found ${count}`);
  }
  return html;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const root = path.resolve(process.argv[2] || '.');
  const names = ['wti_data.js', 'js/core.js'];
  const assets = Object.fromEntries(names.map(name => [name, readFileSync(path.join(root, name))]));
  const index = path.join(root, 'index.html');
  writeFileSync(index, versionAssets(readFileSync(index, 'utf8'), assets));
}
