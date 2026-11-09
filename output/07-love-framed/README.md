# Sample 07: الحبّ · "Vermilion Love, Framed"

Same method as sample 06, changed to the client's new direction:
- Topic is love. Single words instead of phrases, so the words are the focus.
- Stronger interlacing: up to 7 % of a word's ink may cross other words' thin strokes. Letter bodies, loops and dots are never covered.
- Far fewer harakat: 260 small marks (sample 06 had 800).
- Kept: framed rectangle with 3 in padding, Gulzar at one size (60 mm em at A1), varied directions, and no copy of a word within about 160 mm of another.

**Revision 2:** only the client's 16 words, a new arrangement (seed 34), and a top-to-bottom ink gradient `#E0222B` (0 %) → `#B5121E` (45 %) → `#6A0D1A` (100 %) across the whole block. The letters are an SVG mask over one gradient.

Words (16): غرام · شغف · حب · ودّ · اشتياق · لهفة · مودّة · ألفة · وصال · لقاء · قلب · روح · أمان · دفء · سكن · غزل

Words in revision 1 (40): حبّ · هوى · عشق · شوق · غرام · وجد · هيام · شغف · صبابة · ولع · كلف · جوى · لوعة · حنين · وله · ودّ · تتيّم · اشتياق · لهفة · وداد · مودّة · ألفة · حنان · وصال · لقاء · قلب · روح · نبض · فؤاد · وفاء · أمان · دفء · سكن · أنس · نجوى · غزل · دلال · ميل · سهر · عناق

Paper `#FBF4E7`. Files: SVG · PDF (3 mm bleed, TrimBox = A1, RGB) · 300 DPI PNG · preview.
Regenerate: `python3 designs/love_framed.py` (`SEED`, `CROSS_TOL`, `PADDING_IN`, `SIZE`).

**Revision 3 (marks spread evenly):** harakat are allowed only within 7 mm of a word's ink, so they sit in the small gaps between words and never in open patches. They keep at least 9 mm from each other, so they never cluster (320 marks). Open patches are filled with an extra word instead (repeat distance relaxed to 1.25 em for this pass only).

**Revision 4 (fill the circled gaps):** built on the revision 2 arrangement, which the client prefers. Extra words go into open patches first (repeat distance 1.0 em, crossing tolerance raised to 11 % for this pass only). Then 520 harakat fill the remaining small gaps: each within 14 mm of a word, and at least 6.5 mm from the next mark, so they spread evenly with no clusters.

**Revision 5 (second set of circled pockets):** a last pass tries the 9 shortest words at 7° steps from −70° to +70° (and ±90°), with crossing tolerance 2× and repeat distance 0.75 em. A word is kept only if its centre lands at least 6 mm from existing ink. In practice only ودّ fits pockets that small.

**Revision 6 (edge pockets):** the pocket pass now tries all 16 words with repeat distance 0.55 em, crossing tolerance 2.5× and a 5 mm pocket test. Harakat may sit up to 24 mm from words, at 5.5 mm minimum spacing (700 marks), so the top and bottom edge strips are evenly filled.

**Revision 7 (more words, more crossing, fewer marks):** new arrangement (seed 41) with an em of 54 mm, chosen as the size that places the most words while the block stays full: 81 placed in order plus 14 in pockets, 95 in total. Words may be extended horizontally by 1.3–1.7×; Gulzar has no tatweel glyph, so kashida would break the joins. Crossing tolerance is raised to 12 % of a word's ink, thin strokes only; letter bodies and dots remain protected, so no word blocks another. 300 harakat, each within 12 mm of a word and at least 9 mm apart.

**Revision 8 (lighter):** the client found revision 7 heavy. The largest size that still fills the block is chosen: em 73 mm, giving 41 words in order plus 8 in pockets, 49 in total. Crossing, extension and the 300 light harakat are unchanged.

**Revision 9 (weak points):** horizontal extension is capped at 1.3× in every pass. No upright words: angles stay within ±48°. A longer pocket pass (8 rounds) fills the left-edge pockets.
