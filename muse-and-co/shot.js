const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  for (const [f, w, h] of process.argv.slice(2).map(s => s.split(':'))) {
    await p.setViewportSize({ width: +w, height: +h });
    await p.goto(`file://${process.cwd()}/${f}.svg`); await p.waitForTimeout(1200);
    await p.screenshot({ path: `${f}.png`, omitBackground: true });
  }
  await b.close();
})();
