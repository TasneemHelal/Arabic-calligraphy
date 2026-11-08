"""
Collection 04 · "Hilal" (هلال), five interwoven calligraphy artworks for Ramadan.

Shared identity: Amiri Bold pen-contrast lettering, genuine kashida extensions bent
into sweeping curves, words woven into one silhouette, burgundy two-tone ink on warm
ivory paper with a fine grain. Each piece has its own phrase, silhouette and palette.

Usage:  python3 designs/collection_hilal.py [piece-number ...]   (default: all)
        SIZE=A2 ... for another A-size. PREVIEW_ONLY=1 for quick drafts.
"""
import base64
import io
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

from calligraphy import Font, SIZES_MM, export  # noqa: E402
from weave import weave  # noqa: E402

FONT_DIR = os.environ.get("FONT_DIR", os.path.join(ROOT, "fonts"))
font = Font(os.path.join(FONT_DIR, os.environ.get("FONT", "Amiri-Regular.ttf")))

RES = 1.0  # px per mm for the weaving collision maps


# ------------------------------------------------------------------ silhouettes
def shape_mask(kind, W, H):
    """Silhouette as a boolean mask of W x H px (True = letters may go here)."""
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    if kind == "rect":
        d.rectangle([0, 0, W - 1, H - 1], fill=255)
    elif kind == "arch":                     # mihrab: rectangle with a round top
        r = W / 2
        d.rectangle([0, r, W - 1, H - 1], fill=255)
        d.ellipse([0, 0, W - 1, 2 * r], fill=255)
    elif kind == "oval":
        d.ellipse([0, 0, W - 1, H - 1], fill=255)
    elif kind == "column":                   # tall narrow column with round ends
        cw = W * 0.62
        x0 = (W - cw) / 2
        d.rounded_rectangle([x0, 0, x0 + cw, H - 1], radius=cw / 2, fill=255)
    elif kind == "lantern":                  # fanous: domed cap, wide body, tapered base
        pts = [(0.50, 0.00), (0.66, 0.10), (0.95, 0.24), (0.95, 0.76), (0.72, 0.94),
               (0.66, 1.00), (0.34, 1.00), (0.28, 0.94), (0.05, 0.76), (0.05, 0.24),
               (0.34, 0.10)]
        d.polygon([(x * (W - 1), y * (H - 1)) for x, y in pts], fill=255)
    return np.asarray(im) > 127


# ------------------------------------------------------------------ the five pieces
PIECES = {
    1: dict(
        slug="hilal-prayer", title="Hilal Prayer · دعاء الهلال",
        phrase="اللَّهُمَّ أَهِلَّهُ عَلَيْنَا بِالْيُمْنِ وَالْإِيمَانِ وَالسَّلَامَةِ وَالْإِسْلَامِ",
        shape="rect", paper="#F7F1E6", per_zone=2,
        front=("#8E1B3F", "#6E1230"), back="#4E0B1D", seed=4),
    2: dict(
        slug="accepted-deeds", title="Accepted Deeds · تقبّل الله",
        phrase="تَقَبَّلَ اللَّهُ مِنَّا وَمِنْكُمْ صَالِحَ الْأَعْمَالِ",
        shape="arch", paper="#F8F2E8", per_zone=2,
        front=("#9B1B30", "#7A1424"), back="#5C0F1C", seed=7),
    3: dict(
        slug="accepted-fast", title="Accepted Fast · صومًا مقبولًا",
        phrase="صَوْمًا مَقْبُولًا وَذَنْبًا مَغْفُورًا",
        shape="oval", paper="#F6EFE4",
        front=("#8A1F3D", "#6A1530"), back="#B0475F", seed=11),
    4: dict(
        slug="crescent-rising", title="Crescent Rising · هلّ هلالُك",
        phrase="هَلَّ هِلَالُكَ يَا رَمَضَانُ",
        shape="column", paper="#FAF5EC",
        front=("#A0182A", "#7E1222"), back="#6B0E1A", seed=5),
    5: dict(
        slug="month-of-blessings", title="Month of Blessings · شهر الخير",
        phrase="أَهْلًا بِشَهْرِ الْخَيْرِ وَالْبَرَكَاتِ",
        shape="lantern", paper="#F3ECE0",
        front=("#6E1A3A", "#521330"), back="#3E0F25", seed=9),
}


def grain_tile(px=512, seed=1):
    """Fine paper grain: transparent PNG of soft warm specks (embedded, tiled)."""
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (px, px))
    # soften slightly so it reads as paper tooth, not digital noise
    k = np.ones((3, 3)) / 9
    from scipy.signal import convolve2d
    n = convolve2d(n, k, mode="same", boundary="wrap")
    a = np.clip(np.abs(n) * 46, 0, 60).astype(np.uint8)
    dark = n < 0
    rgba = np.zeros((px, px, 4), np.uint8)
    rgba[..., 0] = np.where(dark, 120, 255)
    rgba[..., 1] = np.where(dark, 100, 252)
    rgba[..., 2] = np.where(dark, 80, 245)
    rgba[..., 3] = a
    buf = io.BytesIO()
    Image.fromarray(rgba, "RGBA").save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


def build(n, size_name="A1"):
    P = PIECES[n]
    PW, PH = SIZES_MM[size_name]
    margin = 0.08 * min(PW, PH)
    bw, bh = PW - 2 * margin, PH - 2 * margin
    mask = shape_mask(P["shape"], int(bw * RES), int(bh * RES))
    words = P["phrase"].split()

    # largest letter size at which the whole phrase weaves into the silhouette
    best = None
    lo, hi = bw * 0.08, bw * float(os.environ.get("EM_CAP", "0.42"))
    for _ in range(6):
        em = (lo + hi) / 2
        wv, ok = weave(font, [(w, 1.0) for w in words], mask, em, seed=P["seed"], res=RES,
                       per_zone=P.get("per_zone", 1))
        cov = wv.coverage()
        print(f"   piece {n}: em={em:.0f}mm ok={ok} coverage={cov:.2f}")
        if ok:
            lo = em
            if best is None or cov > best[1]:
                best = (em, cov, wv)
        else:
            hi = em
    em, cov, wv = best

    bleed = 3.0
    W, H = PW + 2 * bleed, PH + 2 * bleed
    o = bleed + margin
    f1, f2 = P["front"]
    tile = grain_tile(seed=n)
    defs = (f'<linearGradient id="front" gradientUnits="userSpaceOnUse" x1="0" y1="{o}" '
            f'x2="0" y2="{o + bh}"><stop offset="0" stop-color="{f1}"/>'
            f'<stop offset="1" stop-color="{f2}"/></linearGradient>'
            f'<pattern id="grain" patternUnits="userSpaceOnUse" width="60" height="60">'
            f'<image width="60" height="60" href="data:image/png;base64,{tile}" '
            f'xlink:href="data:image/png;base64,{tile}"/></pattern>')
    # two tones, alternating word by word; back-tone words are drawn first so the
    # front words lie over them where strokes cross (woven depth)
    back = [p for p in wv.placed if p.index % 2 == 1]
    front = [p for p in wv.placed if p.index % 2 == 0]
    body = [f'<rect width="{W}" height="{H}" fill="{P["paper"]}"/>',
            f'<rect width="{W}" height="{H}" fill="url(#grain)" opacity="0.55"/>']
    body.append(f'<g fill="{P["back"]}">' + "".join(
        f'<path d="{p.d}" transform="translate({o:.2f} {o:.2f}) {p.transform}"/>' for p in back)
        + "</g>")
    body.append('<g fill="url(#front)">' + "".join(
        f'<path d="{p.d}" transform="translate({o:.2f} {o:.2f}) {p.transform}"/>' for p in front)
        + "</g>")
    # a whisper of grain over the ink too, like pigment on textured paper
    body.append(f'<rect width="{W}" height="{H}" fill="url(#grain)" opacity="0.18"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">\n'
           f'<title>{P["title"]}</title>\n<defs>{defs}</defs>\n' + "\n".join(body) + "\n</svg>\n")

    out_dir = os.path.join(ROOT, "output", "04-collection-hilal")
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.join(out_dir, f"{n:02d}-{P['slug']}_{size_name}")
    if os.environ.get("PREVIEW_ONLY"):
        import cairosvg
        cairosvg.svg2png(bytestring=svg.encode(), write_to=stem + "_draft.png", output_width=900)
        print("draft", stem + "_draft.png")
    else:
        print("png px:", export(svg, stem, (PW, PH)))
    print(f"piece {n} done: em={em:.0f}mm coverage={cov:.2f} words={[p.text for p in wv.placed]}")
    return stem


if __name__ == "__main__":
    which = [int(a) for a in sys.argv[1:]] or sorted(PIECES)
    for n in which:
        build(n, os.environ.get("SIZE", "A1"))
