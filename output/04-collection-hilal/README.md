# Collection 04: "Hilal" (هلال): five interwoven calligraphy studies (DRAFT)

Status: **first-round drafts.** These are not final. See "Known issues" below.

| # | Title | Exact wording | Silhouette | Front ink (gradient) | Back ink | Paper |
|---|---|---|---|---|---|---|
| 1 | Hilal Prayer | اللَّهُمَّ أَهِلَّهُ عَلَيْنَا بِالْيُمْنِ وَالْإِيمَانِ وَالسَّلَامَةِ وَالْإِسْلَامِ | Tall rectangle | `#8E1B3F → #6E1230` | `#4E0B1D` | `#F7F1E6` |
| 2 | Accepted Deeds | تَقَبَّلَ اللَّهُ مِنَّا وَمِنْكُمْ صَالِحَ الْأَعْمَالِ | Mihrab arch | `#9B1B30 → #7A1424` | `#5C0F1C` | `#F8F2E8` |
| 3 | Accepted Fast | صَوْمًا مَقْبُولًا وَذَنْبًا مَغْفُورًا | Vertical oval | `#8A1F3D → #6A1530` | `#B0475F` | `#F6EFE4` |
| 4 | Crescent Rising | هَلَّ هِلَالُكَ يَا رَمَضَانُ | Narrow column | `#A0182A → #7E1222` | `#6B0E1A` | `#FAF5EC` |
| 5 | Month of Blessings | أَهْلًا بِشَهْرِ الْخَيْرِ وَالْبَرَكَاتِ | Lantern (fanous) | `#6E1A3A → #521330` | `#3E0F25` | `#F3ECE0` |

Shared identity: Amiri (OFL) pen-contrast letters shaped by HarfBuzz, genuine kashida
extensions swept into arches and steps (letters stay rigid), words woven in reading
order with ribbons allowed to cross, alternating front/back tones (back drawn first),
and a fine paper grain over paper and ink.

Files per piece: SVG and PDF (vector lettering, embedded raster grain tile; PDF has
3 mm bleed and TrimBox = A1, RGB), plus a 300 DPI PNG (7016 × 9933) and a preview.

## Known issues (why these are drafts)
- The interweaving is simulated, not hand-made. It does not reach the reference's
  density of thin, hand-drawn interlaced strokes.
- Some word collisions hurt legibility (piece 1 bottom: والسلامة / والإسلام; piece 2:
  ومنكم; piece 5: أهلاً / بشهر). This conflicts with the readability rule.
- The silhouettes (arch, oval, column, lantern) read only weakly.

Regenerate: `python3 designs/collection_hilal.py [n ...]`
