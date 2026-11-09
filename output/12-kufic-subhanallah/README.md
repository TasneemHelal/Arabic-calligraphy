# Square Kufic 03 · سبحان الله ("Glory be to God")

**Phrase:** سبحان الله (tasbih), standard spelling.

**Letters in order (9):** س · ب · ح · ا | ن || ا · ل · ل · ه

| # | Letter | Position | Joins next? | Dots | Form (F.o.K.S. chart, matches Nihad Nadam's sheet) |
|---|--------|----------|-------------|------|------|
| 1 | س | initial | yes | none | three teeth |
| 2 | ب | medial | yes | 1 below | tooth, dot under it |
| 3 | ح | medial | yes | none | bar, right side and base, open to the left (コ) |
| 4 | ا | final | **no** | none | tall upright joined at its foot |
| 5 | ن | isolated | n/a (end of word) | 1 | cup, dot inside |
| 6 | ا | isolated | **no** | none | tall upright |
| 7 | ل | initial | yes | none | tall upright |
| 8 | ل | medial | yes | none | tall upright |
| 9 | ه | final | n/a | none | loop with the top flag |

**Composition:** a wide horizontal panel on a 42 × 13 grid. A square was not forced, following Nihad Nadam's advice. «سبحان» runs low and long on the right. The single alif of سبحان and the three uprights of الله rise to the same height, so the eye travels from the low word up into the tall one. The panel is deep green `#1F3D2E` on ivory, the two dots are in ochre `#B8892F`, and a single thin frame surrounds it.

## Proofs
| File | What it shows |
|---|---|
| `subhanallah_letter-check.png` | every letter outlined and numbered |
| `subhanallah_one-colour.png` | dots in the ink colour; they are still separated by the gap alone |
| `subhanallah_reading-path.png` | arrows 1→9 in reading order |
| `subhanallah_small-size.png` | the piece about 3 cm wide |
| `subhanallah_proof-sheet.png` | all of the above on one sheet |

## Automated verification (passed)
- The sequence equals «سبحانالله».
- The join groups are exactly {س ب ح ا} {ن} {ا} {ل ل ه}.
- Dots: ب 1, ن 1, and no others. No dot touches ink, and each dot's nearest letter body is its own.
- Unjoined shapes never touch, not even at corners.

Regenerate: `python3 designs/kufic_03_subhanallah.py`
