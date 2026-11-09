# Sample 05: رمضان كريم · "Vermilion Texture" (direction from the red reference)

| Client rule | How it is built |
|---|---|
| Same font, same size for every word | **Amiri Bold (OFL), classical Naskh**, matching the Naskh lettering of the reference. One em size (56 mm at A1) for every word; some words carry a classical kashida (1–2 tatweel) for the reference's long extensions. `FONT=Gulzar-Regular.ttf` reproduces the earlier version |
| Different directions but readable | Words set at 0°, ±14°, ±26° or ±38°. No word is ever crossed by another (1.6 mm clearance), and words of a phrase follow in reading order |
| Gaps filled with harakat | 230 fatha, damma, kasra, sukun and shadda marks in three close sizes, with 3 mm breathing room (revision: fewer marks) |
| Extra words (revision) | Single Ramadan words at the same size and directions fill the open pockets: 5 fit at A1 in the Naskh version (e.g. صدقة · فرحة · سحور · دعاء) |
| Compact block | Rectangle inside an 8 % safe margin |

| Spec | Value |
|---|---|
| Size | A1 portrait, 594 × 841 mm, 3 mm bleed |
| Ink / paper | `#BF1219` on `#FBF4E7` |
| Text | The 12 Ramadan phrases in order, cycled, ending on complete phrases |

Files: SVG · PDF (vector, TrimBox = A1, RGB) · 300 DPI PNG (7016 × 9933) · preview.
Regenerate: `python3 designs/ramadan_kareem_red_dense.py` (`SEED=…` for another arrangement, `SIZE=A2` etc.).
