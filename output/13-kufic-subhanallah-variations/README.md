# Square Kufic 03b · سبحان الله, three compositions

These use the same verified letters as piece 03 (س ب ح ا | ن || ا ل ل ه; dots: ب 1 below, ن 1 inside). Every copy of the phrase is first built flat and passes the full letter check. Only then is it repeated or rotated. The composite then gets extra checks:
- No two copies overlap or touch, corners included.
- No dot touches ink.
- Every dot's nearest letter body is its own letter.
- Every dot keeps at least 2 empty cells between itself and any other copy.

| Piece | Idea | Grid | Palette |
|---|---|---|---|
| **A · Tasbih block** | The phrase three times, as a tasbih is repeated. The kashida is placed differently in each line, so the uprights of الله step sideways from line to line. All three lines are justified to one width, and the middle line is in a second tone. | 39 × 35 | deep green and walnut on ivory, ochre dots |
| **B · Pinwheel** | Four copies turning around a centre square. The top copy reads upright. The baselines face the centre and the uprights of الله rise toward the frame, so each copy stays in its own band and the corners never mix letters from two copies. The centre square is an ornament, not a letter. | 51 × 51 | navy on parchment, copper dots |
| **C · Two tiers** | «سبحان» on top. «الله» below at full width, with its lams raised as tall columns, in a second colour. | 22 × 25 | warm black and wine on cream, ochre dots |

## Corrections caught by the checks before export
- **B:** the first arrangement had uprights pointing inward, and the corners crowded letters of two copies together. It was rebuilt with uprights pointing outward. A new clearance check then found each copy's ب dot within 2 cells of the next copy. The channel between the bands was widened from 1 to 3 cells.
- **C:** the ب dot sat close to the top of the lam of الله. Two more rows were added between the tiers.

Each piece has `_letter-check`, `_one-colour`, `_reading-path`, `_small-size` and `_proof-sheet` files. `variations-overview.png` shows all three.

Regenerate: `python3 designs/kufic_03b_subhanallah_variations.py`
