# Square Kufic 02 · الوقت كالسيف ("Time is a sword")

**Phrase:** الوقت كالسيف. This is the opening of the classical Arabic proverb «الوقت كالسيف إن لم تقطعه قطعك» ("Time is like a sword: if you do not cut it, it cuts you"). The short form is used here. It is a proverb, so it is not attributed to any author.

**Letterforms:** taken from the F.o.K.S. Kufic Font Chart the client supplied, and transcribed into `tools/foks.py`.

**Letters in order (11):** ا · ل · و · ق · ت | ك · ا · ل · س · ي · ف

| # | Letter | Position | Joins next? | Dots | Chart form used |
|---|--------|----------|-------------|------|-----------------|
| 1 | ا | isolated | **no** | none | tall upright |
| 2 | ل | initial | yes | none | tall upright, foot on the baseline |
| 3 | و | final | **no** (waw never joins) | none | loop on a stem with a flat foot |
| 4 | ق | initial | yes | 2 above | loop on a stem (same body as و), 2 dots over the loop |
| 5 | ت | final | n/a | 2 above | wide cup, 2 dots inside |
| 6 | ك | initial | yes | none | tall right stem and bottom bar, with the detached inner hook |
| 7 | ا | final | **no** | none | tall upright joined at its foot |
| 8 | ل | initial | yes | none | tall upright |
| 9 | س | medial | yes | none | three teeth |
| 10 | ي | medial | yes | 2 below | tooth, 2 dots under it |
| 11 | ف | final | n/a | 1 above | bowl with a raised loop, dot over the loop |

**Composition:** a near-square, two lines on a 27 × 23 grid. «الوقت» sits on top, with kashida after ل and after ق so that it spans the full width. «كالسيف» fills its line at natural width. The two alif–lam pairs form tall uprights on the right of each line. Palette: navy `#1D2B45` on parchment `#F1E9DA`, dots in copper `#B5652F`, with a heavy navy frame.

## Verification (automated; export is refused on any failure)
- The drawn sequence equals «الوقتكالسيف».
- The joined groups are exactly {ا} {ل و} {ق ت} {ك ا} {ل س ي ف}, following the rule that ا and و never join the next letter.
- Every letter is one piece, except ك, whose inner hook is a separate stroke as in the chart.
- The dots are ق 2, ت 2, ي 2, ف 1, and no others. No dot touches ink, and each dot's nearest letter body is its own letter.
- Unjoined shapes never touch, not even at corners.

### Corrections made during checking (the first draft was rejected)
1. The dots of ق were exactly as close to the loop of و as to the loop of ق. The gap after و was widened to 2 cells.
2. The two dots of ي overhung so far that they were as close to س and ف as to ي. The medial/initial ي was widened so that its dots sit directly beside its own tooth.

`alwaqtu-kassayf_letter-check.png` outlines and numbers every letter.

Regenerate: `python3 designs/kufic_02_alwaqt.py`
