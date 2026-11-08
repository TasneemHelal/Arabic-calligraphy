# Sample 03: رمضان كريم · "Vermilion Block, Justified" (client revision of 02)

Changes requested on sample 02 and how they were applied:

| Feedback | Change |
|---|---|
| Words intersect too much and are hard to read | Words never cross. A clear 2.5 mm gap is kept around the real ink of every word, and phrases always read in order, top→bottom and right→left. |
| Word sizes are not the same | Every word is set at one size (51 mm em at A1). There is no hero word and there are no small filler words. |
| Too many gaps, wants a nicer frame | The text is set in justified lines (straight right *and* left edges), and each line nests into the one above using real ink shapes. Spare height is shared evenly between the lines, so the top and bottom edges are straight too, giving a clean rectangle. |
| Felt distracting | No rotated or diagonal words. Only a few small harakat sit in the larger counters, all the same size. |

| Spec | Value |
|---|---|
| Size | A1 portrait 594 × 841 mm, 3 mm bleed, 8 % safe margin (block 499 × 746 mm) |
| Lettering | Gulzar (OFL), HarfBuzz-shaped, vector outlines, emboldened with a matching 1 % stroke |
| Ink / paper | `#BF1219` on `#FBF4E7` (flat) |
| Text | The 12 phrases, repeated in reading order, ending on complete phrases (finished with نور · خير) |

Files: SVG (vector) · PDF (vector, TrimBox = A1, RGB) · 300 DPI PNG (7016 × 9933) · preview.
Regenerate: `python3 designs/ramadan_kareem_red_justified.py`. `VERTICAL_EVERY=4` adds a rotated vertical phrase column, which is not recommended in this script because it hurts legibility.
