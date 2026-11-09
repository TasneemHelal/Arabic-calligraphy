"""
Square Kufic 01 · بسم الله
Every letter is listed separately with its own grid cells, so the artwork can be checked
letter by letter. The script refuses to export if a check fails.

Grid: one cell = stroke width = minimum gap. Columns run left→right on screen;
Arabic is read from the right edge (col 10) leftwards.
"""
import os
import numpy as np


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output", "10-kufic-bismillah")

PHRASE = "بسم الله"
W, H = 11, 14


def vline(c, r0, r1): return [(r, c) for r in range(r0, r1 + 1)]
def hline(r, c0, c1): return [(r, c) for c in range(c0, c1 + 1)]
def ring(r0, c0, h=3, w=3):
    return hline(r0, c0, c0 + w - 1) + hline(r0 + h - 1, c0, c0 + w - 1) + \
           vline(c0, r0, r0 + h - 1) + vline(c0 + w - 1, r0, r0 + h - 1)


# ---- Line 1: بسم  (baseline = row 2) --------------------------------------
# ---- Line 2: الله (baseline = row 13; two empty rows above it so the dot of ب cannot be read as belonging to ا) -------------------------------------
# Each letter: (letter, position, ink cells, dot cells). Connecting strokes (kashida)
# belong to the letter they leave from.
LETTERS = [
    ("ب", "initial", vline(10, 0, 2) + hline(2, 9, 9), [(4, 10)]),          # tooth, 1 dot below
    ("س", "medial",  vline(8, 1, 2) + vline(6, 1, 2) + vline(4, 1, 2) + hline(2, 3, 8), []),  # 3 teeth
    ("م", "final",   ring(0, 0) + vline(0, 3, 4), []),                       # loop + descending tail
    ("ا", "isolated", vline(10, 7, 13), []),                                 # does not join
    ("ل", "initial", vline(8, 7, 13) + hline(13, 6, 7), []),
    ("ل", "medial",  vline(5, 7, 13) + hline(13, 3, 4), []),
    ("ه", "final",   ring(11, 0), []),                                       # closed loop on baseline
]

# expected linguistic facts, written independently of the drawing
EXPECTED_LETTERS = list("بسمالله")
EXPECTED_JOIN_GROUPS = [["ب", "س", "م"], ["ا"], ["ل", "ل", "ه"]]   # ا never joins the next letter
EXPECTED_DOTS = {"ب": 1}


def check():
    errors = []
    seq = [l[0] for l in LETTERS]
    if seq != EXPECTED_LETTERS:
        errors.append(f"letter sequence {seq} != {EXPECTED_LETTERS}")
    if "".join(seq) != PHRASE.replace(" ", ""):
        errors.append("letters do not spell the phrase")
    owner = {}
    for i, (ch, _, ink, dots) in enumerate(LETTERS):
        for cell in ink + dots:
            r, c = cell
            if not (0 <= r < H and 0 <= c < W): errors.append(f"{ch} cell {cell} outside grid")
            if cell in owner and owner[cell] != i:
                errors.append(f"{ch} overlaps {LETTERS[owner[cell]][0]} at {cell}")
            owner[cell] = i
        n = len(dots)
        if n != EXPECTED_DOTS.get(ch, 0): errors.append(f"{ch} has {n} dots")
    # connected ink components must equal the joining groups exactly
    ink = np.zeros((H, W), int)
    for i, (ch, _, cells, _) in enumerate(LETTERS):
        for r, c in cells: ink[r, c] = 1
    lab, n = _label(ink)
    groups = {}
    for i, (ch, _, cells, _) in enumerate(LETTERS):
        ids = {lab[r, c] for r, c in cells}
        if len(ids) != 1: errors.append(f"{ch} (#{i}) is broken into pieces")
        groups.setdefault(ids.pop(), []).append(ch)
    got = sorted(groups.values(), key=lambda g: seq.index(g[0]))
    if got != EXPECTED_JOIN_GROUPS: errors.append(f"joins {got} != {EXPECTED_JOIN_GROUPS}")
    # every dot must be isolated from ink (incl. diagonals) so it reads as a dot
    for ch, _, _, dots in LETTERS:
        for r, c in dots:
            near = ink[max(r - 1, 0):r + 2, max(c - 1, 0):c + 2]
            if near.any(): errors.append(f"dot of {ch} touches ink at {(r, c)}")
    return errors, ink


def _label(a):
    lab = np.zeros_like(a); n = 0
    for r in range(a.shape[0]):
        for c in range(a.shape[1]):
            if a[r, c] and not lab[r, c]:
                n += 1; st = [(r, c)]; lab[r, c] = n
                while st:
                    y, x = st.pop()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        yy, xx = y + dy, x + dx
                        if 0 <= yy < a.shape[0] and 0 <= xx < a.shape[1] and a[yy, xx] and not lab[yy, xx]:
                            lab[yy, xx] = n; st.append((yy, xx))
    return lab, n


INK, DOT, PAPER, FRAME = "#5B0F1A", "#B8862F", "#F5EEDF", "#5B0F1A"
U, GAP, BORDER, MAT = 60, 2, 1, 2   # px/cell, frame gap, frame thickness, outer margin (cells)


def svg(guides=False):
    off = MAT + BORDER + GAP
    TW, TH = W + 2 * off, H + 2 * off
    parts = [f'<rect width="{TW*U}" height="{TH*U}" fill="{PAPER}"/>']
    o = MAT * U; t = BORDER * U
    fw, fh = (W + 2 * (GAP + BORDER)) * U, (H + 2 * (GAP + BORDER)) * U
    parts.append(f'<path fill="{FRAME}" fill-rule="evenodd" d="M{o} {o}h{fw}v{fh}h{-fw}z'
                 f'M{o+t} {o+t}v{fh-2*t}h{fw-2*t}v{-(fh-2*t)}z"/>')
    def cells(cs, color):
        d = "".join(f"M{(c+off)*U} {(r+off)*U}h{U}v{U}h{-U}z" for r, c in cs)
        return f'<path fill="{color}" d="{d}"/>'
    allink = [cl for l in LETTERS for cl in l[2]]
    parts.append(cells(allink, INK))
    parts.append(cells([d for l in LETTERS for d in l[3]], DOT))
    if guides:
        cols = ["#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#ff7f0e", "#17becf", "#e377c2"]
        for i, (ch, pos, ink, dots) in enumerate(LETTERS):
            rs = [r for r, c in ink + dots]; cs_ = [c for r, c in ink + dots]
            x0, y0 = (min(cs_) + off) * U, (min(rs) + off) * U
            x1, y1 = (max(cs_) + 1 + off) * U, (max(rs) + 1 + off) * U
            parts.append(f'<rect x="{x0+4}" y="{y0+4}" width="{x1-x0-8}" height="{y1-y0-8}" fill="none" '
                         f'stroke="{cols[i]}" stroke-width="6" stroke-dasharray="14 8"/>')
            parts.append(f'<text x="{x1-6}" y="{y0-10 if y0 > 60 else y1+50}" font-size="44" '
                         f'font-family="Amiri" text-anchor="end" fill="{cols[i]}">{i+1} {ch}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TW*U} {TH*U}" width="{TW*U}" '
            f'height="{TH*U}" shape-rendering="crispEdges"><title>{PHRASE}</title>{"".join(parts)}</svg>')


if __name__ == "__main__":
    errs, ink = check()
    if errs:
        raise SystemExit("REJECTED:\n  " + "\n  ".join(errs))
    import cairosvg
    os.makedirs(OUT, exist_ok=True)
    for name, g in (("bismillah", False), ("bismillah_letter-check", True)):
        s = svg(g)
        open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8").write(s)
        cairosvg.svg2png(bytestring=s.encode(), write_to=os.path.join(OUT, name + ".png"), output_width=1200)
    grid = [["." for _ in range(W)] for _ in range(H)]
    for _, _, ink_, dots in LETTERS:
        for r, c in ink_: grid[r][c] = "#"
        for r, c in dots: grid[r][c] = "o"
    print("\n".join("".join(r) for r in grid))
    print("all checks passed")
