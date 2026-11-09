"""
Square Kufic 03 · سبحان الله ("Glory be to God")
Letterforms: tools/foks.py (F.o.K.S. chart, cross-checked with Nihad Nadam's letter sheet).
Checks: tools/kufic_verify.py — export is refused on any failure.
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from kufic_verify import build_line, verify  # noqa: E402
from kufic_render import export_all  # noqa: E402

PHRASE = "سبحان الله"
TALL = 11
BASE = TALL - 1
# one line, right→left. kashida: after ح (index 2) in سبحان; after each ل in الله
LETTERS, xl = build_line([("سبحان", {2: 2}), ("الله", {1: 3, 2: 3})],
                         baseline=BASE, tall_h=TALL, right_edge=200, word_gap=3)
# shift so the leftmost cell is column 0
minc = min(c for l in LETTERS for r, c in l["ink"] | l["dots"])
for l in LETTERS:
    for k in ("ink", "dots", "conn"):
        l[k] = {(r, c - minc) for r, c in l[k]}
W = 1 + max(c for l in LETTERS for r, c in l["ink"] | l["dots"])
H = 1 + max(r for l in LETTERS for r, c in l["ink"] | l["dots"])

STYLE = dict(ink="#1F3D2E", dot="#B8892F", paper="#F4EEDF", U=50, gap=2, border=1, inner_border=0, mat=3)

if __name__ == "__main__":
    errs = verify(LETTERS, PHRASE)
    grid = [["."] * W for _ in range(H)]
    for l in LETTERS:
        for r, c in l["ink"]: grid[r][c] = "#"
        for r, c in l["dots"]: grid[r][c] = "o"
    print("\n".join("".join(r) for r in grid)); print(W, "x", H)
    if errs:
        raise SystemExit("REJECTED:\n  " + "\n  ".join(errs))
    export_all(LETTERS, W, H, PHRASE, "subhanallah", os.path.join(ROOT, "output", "12-kufic-subhanallah"), **STYLE)
    print("all checks passed:", ", ".join(f"{l['ch']}({l['form']})" for l in LETTERS))
