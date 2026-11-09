# Square Kufic 01 · بسم الله ("In the name of God")

**Phrase (standard spelling):** بسم الله. This is the opening of the basmala. In the basmala, «بسم» is written without an alif, which is the correct Qur'anic spelling.

**Letters in order (7):** ب · س · م | ا · ل · ل · ه

| # | Letter | Position | Joins next? | Dots | Grid construction |
|---|--------|----------|-------------|------|-------------------|
| 1 | ب | initial | yes | 1 below | Tooth, 3 cells tall. Dot two rows below the baseline |
| 2 | س | medial | yes | none | Three teeth, 2 cells tall, so they read lower than the ب tooth |
| 3 | م | final | n/a (last letter) | none | Closed 3×3 loop with the final-mim tail dropping below the baseline |
| 4 | ا | isolated | **no** (alif never joins) | none | Full-height stroke. The baseline is broken next to it |
| 5 | ل | initial | yes | none | Full-height stroke |
| 6 | ل | medial | yes | none | Full-height stroke |
| 7 | ه | final | n/a (last letter) | none | Closed 3×3 loop on the baseline, with no tail (this is what separates it from the م above) |

**Composition:** a tall rectangle on an 11 × 14 grid, inside a single frame. «بسم» forms a compact top line with a long kashida through the teeth of س. «الله» stands beneath it as a colonnade of three equal uprights. Every stroke and every gap is exactly one cell, and all angles are 90°. Palette: deep burgundy `#5B0F1A` on ivory `#F5EEDF`, with the single dot in ochre `#B8862F`.

## Verification (automated, in `designs/kufic_01_bismillah.py`; export is refused if any check fails)
- The drawn letter sequence equals «بسمالله» exactly, with no missing, extra or swapped letters.
- The connected ink shapes are exactly {ب س م}, {ا}, {ل ل ه}. So ا is detached and every other join is present.
- Dot count: one dot, owned by ب. No other letter has dots.
- The dot touches no ink, diagonals included. It sits 2 rows under ب and 3 rows above ا, so it cannot be read as belonging to the alif. (This was corrected during the check: the first draft had the dot equally far from both.)
- No letter overlaps another, and no letter is broken into pieces.

`bismillah_letter-check.png` outlines and numbers every letter for visual review.
