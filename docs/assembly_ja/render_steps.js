// Screenshot assembly steps 1..10 from the viewer (#stepN) and the overview views.
// Needs: npm i three@0.147.0 playwright-core ; a Chromium binary (CHROME env).
// Usage: CHROME=/path/to/chrome THREE_DIR=/path/to/node_modules/three node docs/assembly_ja/render_steps.js
const fs = require('fs'), path = require('path');
const { chromium } = require(process.env.PW || 'playwright-core');
const ROOT = path.resolve(__dirname, '..', '..');
const THREE = process.env.THREE_DIR;
(async () => {
  let html = fs.readFileSync(path.join(ROOT, 'viewer/ix73_picker_viewer.html'), 'utf8');
  html = html.replaceAll('https://cdn.jsdelivr.net/npm/three@0.147.0/', 'file://' + THREE + '/')
             .replace(/<link rel="stylesheet" href="https:\/\/fonts[^>]*>/, '');
  const local = path.join(require('os').tmpdir(), 'picker_viewer_local.html');
  fs.writeFileSync(local, html);
  const b = await chromium.launch({ executablePath: process.env.CHROME,
    args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const shoot = async (hash, file, w, h) => {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.goto('file://' + local + '#' + hash);
    await p.waitForTimeout(2500);
    await (await p.$('#stage')).screenshot({ path: file });
    await p.close();
  };
  for (let n = 1; n <= 10; n++)
    await shoot('step' + n, path.join(ROOT, 'docs/assembly_ja/img', `step${String(n).padStart(2, '0')}.png`), 1200, 800);
  for (const v of ['iso', 'top', 'front', 'side', 'head'])
    await shoot(v + '-render', path.join(ROOT, 'docs/img', `view_${v}.png`), 1500, 1000);
  await b.close();
})();
