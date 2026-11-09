"""
Square Kufic 02 · الوقت كالسيف ("Time is a sword")
Letterforms: tools/foks.py (F.o.K.S. chart). Checks: tools/kufic_verify.py.
Export is refused if any check fails.
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from kufic_verify import build_line, verify  # noqa: E402

OUT = os.path.join(ROOT, "output", "11-kufic-alwaqt")
PHRASE = "الوقت كالسيف"
W = 27          # grid width
TALL = 10       # alif / lam height

# line 1: الوقت  — kashida after ل and ق; a 2-cell gap after و keeps the dots of ق clear of it
L1, x1 = build_line([("الوقت", {1: 3, 2: 1, 3: 4})], baseline=9, tall_h=TALL, right_edge=W - 1)
# line 2: كالسيف — natural width fills the line
L2, x2 = build_line([("كالسيف", {})], baseline=20, tall_h=TALL, right_edge=W - 1)
LETTERS = L1 + L2
H = 1 + max(r for l in LETTERS for r, c in l["ink"] | l["dots"])
assert x1 == 0 and x2 == 0, (x1, x2)   # both lines exactly fill the width

INK, DOT, PAPER = "#1D2B45", "#B5652F", "#F1E9DA"
U, GAP, BORDER, MAT = 50, 2, 2, 3


def svg(guides=False):
    off = MAT + BORDER + GAP
    TW, TH = (W + 2 * off) * U, (H + 2 * off) * U
    o, t = MAT * U, BORDER * U
    fw, fh = (W + 2 * (GAP + BORDER)) * U, (H + 2 * (GAP + BORDER)) * U
    p = [f'<rect width="{TW}" height="{TH}" fill="{PAPER}"/>',
         f'<path fill="{INK}" fill-rule="evenodd" d="M{o} {o}h{fw}v{fh}h{-fw}z'
         f'M{o+t} {o+t}v{fh-2*t}h{fw-2*t}v{-(fh-2*t)}z"/>']
    cell = lambda cs, col: f'<path fill="{col}" d="' + "".join(
        f"M{(c+off)*U} {(r+off)*U}h{U}v{U}h{-U}z" for r, c in cs) + '"/>'
    p.append(cell([c for l in LETTERS for c in l["ink"]], INK))
    p.append(cell([c for l in LETTERS for c in l["dots"]], DOT))
    if guides:
        cols = ["#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#e07b00", "#17becf",
                "#e377c2", "#8c564b", "#bcbd22", "#7f7f7f", "#d62728"]
        for i, l in enumerate(LETTERS):
            cs = l["ink"] | l["dots"]
            r0, r1 = min(r for r, c in cs), max(r for r, c in cs)
            c0, c1 = min(c for r, c in cs), max(c for r, c in cs)
            col = cols[i % len(cols)]
            p.append(f'<rect x="{(c0+off)*U+5}" y="{(r0+off)*U+5}" width="{(c1-c0+1)*U-10}" '
                     f'height="{(r1-r0+1)*U-10}" fill="none" stroke="{col}" stroke-width="6" stroke-dasharray="14 8"/>')
            p.append(f'<text x="{(c1+1+off)*U-6}" y="{(r0+off)*U-10}" font-size="40" font-family="Amiri" '
                     f'text-anchor="end" fill="{col}">{i+1} {l["ch"]}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TW} {TH}" width="{TW}" height="{TH}" '
            f'shape-rendering="crispEdges"><title>{PHRASE}</title>{"".join(p)}</svg>')


if __name__ == "__main__":
    errs = verify(LETTERS, PHRASE)
    grid = [["."] * W for _ in range(H)]
    for l in LETTERS:
        for r, c in l["ink"]: grid[r][c] = "#"
        for r, c in l["dots"]: grid[r][c] = "o"
    print("\n".join("".join(r) for r in grid))
    if errs:
        raise SystemExit("REJECTED:\n  " + "\n  ".join(errs))
    import cairosvg
    os.makedirs(OUT, exist_ok=True)
    for name, g in (("alwaqtu-kassayf", False), ("alwaqtu-kassayf_letter-check", True)):
        s = svg(g)
        open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8").write(s)
        cairosvg.svg2png(bytestring=s.encode(), write_to=os.path.join(OUT, name + ".png"), output_width=1400)
    print("all checks passed:", ", ".join(f"{l['ch']}({l['form']})" for l in LETTERS))
