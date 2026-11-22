const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
  await p.setContent(`<style>svg{width:960px;height:960px}</style><body style="margin:0;background:#FBF4EA;display:grid;place-items:center;height:1080px"><div style="width:960px;height:960px;line-height:0">${require('fs').readFileSync('muse-and-make-emblem-animated.svg','utf8')}</div></body>`);
  await p.waitForTimeout(1500);
  const fps = 30, secs = 5;
  for (let i = 0; i < fps * secs; i++) {
    await p.evaluate(t => document.getAnimations().forEach(a => { a.pause(); a.currentTime = t; }), i * 1000 / fps); await p.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
    await p.screenshot({ path: `/tmp/claude-0/frames/f${String(i).padStart(3,'0')}.png` });
  }
  b.close();
})();
