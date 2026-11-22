// Renders the reel SVG frame-by-frame (SMIL clock) to PNGs. Usage: node frames.js <svg> <outdir> <secs>
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [file, out, secs] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.setContent(`<style>body{margin:0}svg{display:block}</style>${fs.readFileSync(file, 'utf8')}`);
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(1500);
  await p.evaluate(() => document.querySelector('svg').pauseAnimations());
  const fps = 30;
  for (let i = 0; i < fps * +secs; i++) {
    await p.evaluate(t => document.querySelector('svg').setCurrentTime(t), i / fps);
    await p.screenshot({ path: `${out}/f${String(i).padStart(4, '0')}.png` });
  }
  await b.close();
})();
