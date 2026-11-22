const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [name, out] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1600, height: 560 } });
  await p.setContent(`<style>body{margin:0;background:#FBF4EA;display:grid;place-items:center;height:560px}svg{width:1480px;height:480px}</style>${fs.readFileSync(name, 'utf8')}`);
  await p.evaluate(() => document.querySelector('svg').pauseAnimations());
  const fps = 60, secs = 3.5;
  for (let i = 0; i < fps * secs; i++) {
    await p.evaluate(t => document.querySelector('svg').setCurrentTime(t), i / fps);
    await p.screenshot({ path: `${out}/f${String(i).padStart(3, '0')}.png` });
  }
  await b.close();
})();
