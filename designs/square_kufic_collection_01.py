"""
Collection 01 · Square Kufic (Kufi Murabba')
Ten original grid-built compositions. Every letter is constructed on the grid in
tools/kufic.py (no font). Run: python3 designs/square_kufic_collection_01.py
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import kufic as K  # noqa: E402

OUT = os.path.join(ROOT, "output", "09-square-kufic-collection")
U = 40  # px per grid cell in the SVG


def lines(texts, width=None, height=7, gap=1, nest=True, heights=None):
    """Justify every line to one width; with nest=True each line slides up into the
    free space of the line above (interlocking), choosing the best kashida layout."""
    ls = [K.Line(t) for t in texts]
    w = width or max(l.natural() for l in ls)
    heights = heights or [height] * len(ls)
    if not nest:
        return K.stack([K.trim_rows(l.render(w, h)) for l, h in zip(ls, heights)], gap=gap)
    cands = [K.variants(l, w, h, seed=i) for i, (l, h) in enumerate(zip(ls, heights))]
    return K.interlock(cands, gap=gap)


def recolor(grid, rows, value):
    g = grid.copy(); r0, r1 = rows
    sub = g[r0:r1]; sub[sub == 1] = value
    return g


pieces = []

# 1 · فصبر جميل — Yusuf 12:18
g = lines(["فص_بر", "جمي_ل"], height=9, width=20)
g = K.frame(g, gap=2, thick=2)
pieces.append(("01-fasabrun-jamil", "فَصَبْرٌ جَمِيلٌ", g, 0,
               {1: "#141414", 2: "#8C1C1C"}, "#F5F0E6"))

# 2 · شوق — longing
g = lines(["ش_وق"])
pieces.append(("02-shawq", "شوق", g, 3, {1: "#F1E6D2", 2: "#C9A06A"}, "#5A0C16"))

# 3 · لا مستحيل — nothing is impossible
g = lines(["لا مس_تحيل"], height=12)
g = K.frame(g, gap=2, thick=1)
pieces.append(("03-la-mustahil", "لا مستحيل", g, 2, {1: "#1E2A45", 2: "#B8835A"}, "#EADFCB"))

# 4 · سلام قولا من رب رحيم — Ya-Sin 36:58
g = lines(["س_لام", "ق_ولا", "م_ن رب", "رح_يم"], heights=[9, 9, 7, 7], nest=False)
g = K.frame(g, gap=2, thick=2)
pieces.append(("04-salamun-qawlan", "سَلَامٌ قَوْلًا مِّن رَّبٍّ رَّحِيمٍ", g, 2,
               {1: "#2E5B45", 2: "#B4623A"}, "#F3EEE2"))

# 5 · الحمد لله — praise be to God
top = K.trim_rows(K.Line("الحم_د").render(None, 11))
w = top.shape[1]
bot = [b.copy() for b in K.variants(K.Line("ل_ل_ه"), w, 9)]
for b in bot: b[b == 1] = 3
g = K.interlock([[top], bot])
g = K.frame(g, gap=2, thick=1)
pieces.append(("05-alhamdu-lillah", "الحمد لله", g, 2,
               {1: "#3A2315", 3: "#B5761E"}, "#EAD9B6"))

# 6 · نور — light, four-fold pinwheel
strip = K.trim_rows(K.Line("ن_ور").render(19))
side = strip.shape[1] + strip.shape[0] + 1
g = K.rotate_pinwheel(strip, side)
c = side // 2
g[c - 1:c + 1, c - 1:c + 1] = 2
g = K.frame(g, gap=2, thick=1)
pieces.append(("06-nur-pinwheel", "نور", g, 2, {1: "#D3E4DD", 2: "#79AE9F"}, "#0F3A39"))

# 7 · لكل مجتهد نصيب — every striver has a share
ls = ["ل_كل", "مج_تهد", "نص_يب"]
L = [K.Line(t) for t in ls]
w = max(l.natural() for l in L)
cands = [K.variants(l, w, 9 if i == 0 else 7, seed=i) for i, l in enumerate(L)]
for i, cs in enumerate(cands):
    for r in cs: r[r == 1] = [1, 3, 4][i]
g = K.interlock(cands)
g = K.frame(g, gap=2, thick=2, value=5)
pieces.append(("07-likulli-mujtahid", "لكل مجتهد نصيب", g, 2,
               {1: "#4A2C17", 3: "#7B4A22", 4: "#A8692B", 2: "#C08A3E", 5: "#8E4B16"}, "#FBF7F0"))

# 8 · الوقت كالسيف — time is a sword
g = lines(["الو_قت كال_سيف"], height=9)
g = K.frame(g, gap=1, thick=1)
g = K.frame(g, gap=1, thick=2)
pieces.append(("08-alwaqtu-kassayf", "الوقت كالسيف", g, 2, {1: "#101010", 2: "#101010"}, "#FFFFFF"))

# 9 · ابتسم — smile
g = lines(["ابتس_م"], width=23, height=9)
pieces.append(("09-ibtasim", "ابتسم", g, 3, {1: "#C2602A", 2: "#E3A33A"}, "#F8F0E3"))

# 10 · حلم — a dream (and forbearance)
g = lines(["حلم"], height=24)
g = K.frame(g, gap=3, thick=1)
pieces.append(("10-hilm", "حلم", g, 2, {1: "#D9DFEA", 2: "#D9DFEA"}, "#14213B"))


def main():
    import cairosvg
    os.makedirs(OUT, exist_ok=True)
    for stem, text, g, margin, colors, bg in pieces:
        s = K.svg(g, U, colors, bg, margin=margin, title=text)
        p = os.path.join(OUT, stem)
        open(p + ".svg", "w", encoding="utf-8").write(s)
        h, w = g.shape
        scale = 1600 / max(h + 2 * margin, w + 2 * margin) / U
        cairosvg.svg2png(bytestring=s.encode(), write_to=p + "_preview.png",
                         output_width=round((w + 2 * margin) * U * scale),
                         output_height=round((h + 2 * margin) * U * scale))
        print(stem, g.shape)
    contact()


def contact():
    from PIL import Image
    ims = [Image.open(os.path.join(OUT, s + "_preview.png")).convert("RGB") for s, *_ in pieces]
    cell, padd, cols = 520, 30, 5
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (cell + padd) + padd, rows * (cell + padd) + padd), "#2B2B2B")
    for i, im in enumerate(ims):
        im.thumbnail((cell, cell))
        x = padd + (i % cols) * (cell + padd) + (cell - im.width) // 2
        y = padd + (i // cols) * (cell + padd) + (cell - im.height) // 2
        sheet.paste(im, (x, y))
    sheet.save(os.path.join(OUT, "collection-contact-sheet.png"))


if __name__ == "__main__":
    main()
