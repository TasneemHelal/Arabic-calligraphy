const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1600, height: 560 } });
  await p.setContent(`<body style="margin:0;background:#FBF4EA;display:grid;place-items:center;height:560px">${require('fs').readFileSync('muse-and-make-logo-animated.svg','utf8')}</body>`);
  await p.waitForTimeout(1500);
  const fps = 30, secs = 5;
  for (let i = 0; i < fps * secs; i++) {
    await p.evaluate(t => document.getAnimations().forEach(a => { a.pause(); a.currentTime = t; }), i * 1000 / fps); await p.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
    await p.screenshot({ path: `/tmp/claude-0/frames/f${String(i).padStart(3,'0')}.png` });
  }
  b.close();
})();
