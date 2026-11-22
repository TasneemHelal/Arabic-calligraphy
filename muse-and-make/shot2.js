const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 480, height: 480 } });
  for (const f of ['muse-and-make-monogram', 'muse-and-make-monogram-n']) {
    await p.goto(`file://${process.cwd()}/${f}.svg`); await p.waitForTimeout(800);
    await p.screenshot({ path: `${f}.png`, omitBackground: true });
  }
  b.close();
})();
