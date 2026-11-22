const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1440, height: 480 } });
  const dir = process.cwd();
  for (const [f, w, bg] of [['muse-and-make-logo', 1440, '#FBF4EA'], ['muse-and-make-icon', 480, '#FBF4EA']]) {
    await p.setViewportSize({ width: w, height: 480 });
    await p.goto(`file://${dir}/${f}.svg`); await p.waitForTimeout(1500);
    await p.screenshot({ path: `${f}.png`, omitBackground: true });
  }
  b.close();
})();
