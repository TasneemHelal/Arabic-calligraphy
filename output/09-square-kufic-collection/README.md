# Collection 09 · Square Kufic (Kufi Murabba'), Collection 01

Ten original compositions. Every letter is built by hand on a square grid in `tools/kufic.py`: one cell is one stroke width and also one gap. No font is used. Dots are square cells in an accent color. Kashida (horizontal extension) justifies each line, and in pieces 01, 05 and 07 each line slides up into the free space of the line above it (interlocking).

| # | Phrase | Meaning | Theme / source | Composition | Palette |
|---|--------|---------|----------------|-------------|---------|
| 01 | فَصَبْرٌ جَمِيلٌ | "So patience is most fitting" | Qur'an, Yusuf 12:18 (exact wording) | Square, two interlocked lines, heavy black frame | Black on ivory, oxblood dots |
| 02 | شوق | Longing | Love, single word | Small horizontal piece, no frame | Ivory on deep burgundy, gold dots |
| 03 | لا مستحيل | Nothing is impossible | Motivation, contemporary | Wide banner; the tall لا and final ل bracket the word | Navy on warm beige |
| 04 | سَلَامٌ قَوْلًا مِّن رَّبٍّ رَّحِيمٍ | "Peace: a word from a Merciful Lord" | Qur'an, Ya-Sin 36:58 (exact wording) | Tall vertical, four justified lines, kept un-interlocked so the verse reads clearly | Forest green and terracotta |
| 05 | الحمد لله | Praise be to God | Gratitude | Square; tall alif and lams form a colonnade, لله nests under الحمد in a second color | Dark brown and ochre on sand |
| 06 | نور | Light | Spirituality, minimal | Four-fold pinwheel: the word stands on each edge and turns around a central square | Monochrome teal |
| 07 | لكل مجتهد نصيب | Every striver gets a share | Arabic heritage proverb | Square, three interlocked lines, each line a different earth tone | Three browns, rust frame |
| 08 | الوقت كالسيف | Time is a sword | Classical proverb (opening of «الوقت كالسيف إن لم تقطعه قطعك») | Wide horizontal band, double frame | Classic black and white |
| 09 | ابتسم | Smile | Positive energy, minimal | Long kashida between ت and س, alif rising at the start | Terracotta and saffron on cream |
| 10 | حلم | A dream, also forbearance | Minimal, double meaning | Tall portrait; the lam rises across the whole frame | Pale blue-grey on midnight navy |

## Accuracy notes
- The phrases contain no hamza, so nothing had to be dropped. In ابتسم the alif is hamzat al-wasl, which is not written.
- Qur'anic text is spelled exactly as in the mushaf. Harakat are left out, following square-Kufic convention.
- Letter joining comes from the standard Arabic rules (ا د ر و never join the following letter). Dot counts and positions follow the letters: ب one below, ت two above, ن one above, ي two below, ش three, ف one, ق two, ج one.
- Grid letterforms: و = ring with a descending tail; م = closed ring; final ه = taller ring; ك = Ǝ with an inner bar; initial ح/ج = hooked bar; medial ح/ج = arch.

Regenerate: `python3 designs/square_kufic_collection_01.py` (writes the SVG, a 1600 px preview PNG and the contact sheet).
