# Sample 06: رمضان كريم · "Vermilion Texture, Framed"

Built from the client-chosen dense-harakat draft of sample 05.

| Client rule | Implementation |
|---|---|
| Rectangular outer border | Edge words slide out to touch the block edges, and harakat fill to the edges, so all four sides are straight with square corners (approved on the corner proof) |
| Padding | 3 in (76.2 mm) on every side of the A1 sheet (approved). `PADDING_IN=…` changes it |
| Vowel marks lighter, not too light | 800 marks with a 1.4 mm gap (the chosen draft had about 1400 with a 0.9 mm gap) |
| No repeated word in the same area | Two copies of any word (ignoring harakat and kashida) keep their centres at least 2.6 em (≈160 mm) apart |
| Words intersect without covering each other | Thin strokes may cross thin strokes (≤ 4 % of a word's ink). Letter bodies, loops and dots (strokes thicker than ≈3 mm) are protected: no other ink may touch them |
| Reading order | Each word of a phrase sits to the left of the previous one or on a lower line |
| Same font, same size | Gulzar, one em (62 mm) for every word |

Extra single words placed in this run: صدقة · سكينة · فرحة · سحور · دعاء · رحمة · خير · نور

Files: SVG · PDF (vector, 3 mm bleed, TrimBox = A1, RGB) · 300 DPI PNG (7016 × 9933) · preview · corner proof · interlace close-up.
Regenerate: `python3 designs/ramadan_kareem_red_framed.py`
