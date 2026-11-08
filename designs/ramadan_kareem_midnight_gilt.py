"""
Sample 01 · رمضان كريم · "Midnight Gilt"
A1 portrait (594 × 841 mm), 3 mm bleed, 8 % safe margin.
Composition: horizontal hero line + interlocking vertical and horizontal phrases.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

from calligraphy import Font, Leaf, Split, SIZES_MM, build_svg, export  # noqa: E402

FONT_DIR = os.environ.get("FONT_DIR", os.path.join(ROOT, "fonts"))
fonts = {
    "bold": Font(os.path.join(FONT_DIR, "ArefRuqaa-Bold.ttf")),
    "regular": Font(os.path.join(FONT_DIR, "ArefRuqaa-Regular.ttf")),
}

# ---------------------------------------------------------------- palette
MIDNIGHT = "#0F1A2B"
MIDNIGHT_LIFT = "#1A2A44"
GOLD_STOPS = [("0", "#F1D592"), ("0.4", "#D4A24C"), ("0.75", "#A97A2C"), ("1", "#7A5520")]
ANTIQUE_STOPS = [("0", "#C9A25A"), ("1", "#8C6526")]
PALE = "#F3E2B0"
GHOST = "#1D2C49"  # back-layer words, barely above the midnight ground


def defs(bx, by, bw, bh, W, H):
    def lin(id_, stops, x1, y1, x2, y2):
        s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
        return (f'<linearGradient id="{id_}" gradientUnits="userSpaceOnUse" '
                f'x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>')
    return "".join([
        # hero: diagonal gold sweep across the whole text block
        lin("gold", GOLD_STOPS, bx + bw, by, bx, by + bh),
        # supporting words: quieter antique gold, vertical
        lin("antique", ANTIQUE_STOPS, 0, by, 0, by + bh),
        f'<linearGradient id="pale"><stop offset="0" stop-color="{PALE}"/>'
        f'<stop offset="1" stop-color="{PALE}"/></linearGradient>',
        f'<linearGradient id="ghost"><stop offset="0" stop-color="{GHOST}"/>'
        f'<stop offset="1" stop-color="{GHOST}"/></linearGradient>',
        f'<radialGradient id="bg" gradientUnits="userSpaceOnUse" cx="{W/2}" cy="{H*0.45}" '
        f'r="{H*0.6}"><stop offset="0" stop-color="{MIDNIGHT_LIFT}"/>'
        f'<stop offset="1" stop-color="{MIDNIGHT}"/></radialGradient>',
    ])


def background(W, H):
    return f'<rect width="{W}" height="{H}" fill="url(#bg)"/>'


V = -90  # vertical: rotated so the line reads bottom → top
G = 3.5  # gutter in mm

tree = Split("rows", gap=G, parts=[
    (2.3, Split("cols", gap=G, parts=[
        (1.0, Leaf("شهر الخير", rot=V, fill="antique", font="regular")),
        (3.4, Split("rows", gap=G, parts=[
            (1.0, Leaf("أهلاً رمضان", fill="pale", font="regular")),
            (1.0, Leaf("رمضان مبارك", fill="antique")),
        ])),
        (1.0, Leaf("هلّ هلالُك", rot=V, fill="antique", font="regular")),
    ])),
    (2.7, Leaf("رمضان كريم", fill="gold", pad=0.0, max_kashida=8)),
    (3.0, Split("cols", gap=G, parts=[
        (1.0, Leaf("تقبّل الله منّا ومنكم", rot=V, fill="antique", font="regular")),
        (3.2, Split("rows", gap=G, parts=[
            (1.0, Leaf("كل عام وأنتم بخير", fill="pale", font="regular", grow=1.04)),
            (1.0, Leaf("صومًا مقبولًا", fill="antique", max_kashida=8, grow=1.04)),
        ])),
        (1.0, Leaf("رمضان يجمعنا", rot=V, fill="antique", font="regular")),
    ])),
    (1.6, Leaf("اللهم بلّغنا رمضان", fill="gold", font="regular", grow=1.03)),
])

# Back layer: the two words of the theme, huge and tone-on-tone (vertical + horizontal).
underlay = [
    (Leaf("رمضان", rot=V, fill="ghost", font="bold", max_kashida=4), 0.0, 0.0, 1.0, 0.56),
    (Leaf("كريم", rot=V, fill="ghost", font="bold", max_kashida=4), 0.0, 0.5, 1.0, 0.5),
]

SIZE = os.environ.get("SIZE", "A1")
spec = {
    "title": "Ramadan Kareem · Midnight Gilt",
    "size_mm": SIZES_MM[SIZE],
    "margin_frac": 0.08,
    "tree": tree,
    "underlay": underlay,
    "defs": defs,
    "background": background,
    "debug": bool(os.environ.get("DEBUG")),
}

if __name__ == "__main__":
    out_dir = os.environ.get("OUT", os.path.join(ROOT, "output", "01-ramadan-kareem"))
    os.makedirs(out_dir, exist_ok=True)
    svg, used = build_svg(spec, fonts)
    stem = os.path.join(out_dir, f"ramadan-kareem_midnight-gilt_{SIZE}")
    if os.environ.get("PREVIEW_ONLY"):
        import cairosvg
        cairosvg.svg2png(bytestring=svg.encode(), write_to=stem + "_draft.png",
                         output_width=1000)
        print("draft", stem + "_draft.png")
    else:
        print("png px:", export(svg, stem, spec["size_mm"]))
    for t in used:
        print(" ", t)
