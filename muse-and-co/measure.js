// Measures rendered text widths (Fraunces/Nunito) so the rotating words can be positioned exactly.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.setContent(`<style>@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@600&family=Nunito:wght@700&display=swap');</style>
  <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><text id="t"></text></svg>`);
  await p.evaluate(() => document.fonts.load('600 72px Quicksand').then(() => document.fonts.load('700 17px Nunito')));
  await p.waitForTimeout(800);
  const items = [['Muse','fr'],['&','fr'],['Co','fr'],['lors','fr'],['llectives','fr'],['mmunities','fr'],['llaborations','fr'],['.','fr'],
                 ['Colors · Collectives · Communities · Collaborations','nu']];
  const out = await p.evaluate(items => { const t = document.getElementById('t'); const r = {};
    for (const [s, f] of items) {
      if (f === 'fr') { t.setAttribute('font-family','Quicksand'); t.setAttribute('font-weight','600'); t.setAttribute('font-size','72'); t.setAttribute('letter-spacing','-0.5'); t.removeAttribute('font-style'); }
      else { t.setAttribute('font-family','Nunito'); t.setAttribute('font-weight','700'); t.setAttribute('font-size','17'); t.setAttribute('letter-spacing','.6'); }
      t.textContent = s; r[s] = Math.round(t.getComputedTextLength() * 10) / 10; }
    return r; }, items);
  console.log(JSON.stringify(out)); await b.close();
})();
