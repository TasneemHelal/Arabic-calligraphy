"""
Arabic calligraphy composition engine.

Each phrase is shaped by HarfBuzz (correct joining, ligatures, dots and diacritics),
converted to true vector outlines, and placed into a slicing-tree layout that mixes
horizontal and vertical (rotated) words. Output: SVG (vector), PDF (vector, with bleed
and TrimBox) and PNG at 300 DPI (trimmed to final size).
"""
from __future__ import annotations

import io
import math
from dataclasses import dataclass, field

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

TATWEEL = "ـ"
# Letters that never connect to the following letter, so no kashida after them.
NON_JOINING_LEFT = set("اأإآدذرزوؤةءى")
ARABIC_LETTERS = set(chr(c) for c in range(0x0621, 0x064B)) - {TATWEEL}
HARAKAT = set(chr(c) for c in range(0x064B, 0x0653)) | {"ٰ"}

SIZES_MM = {
    "A0": (841, 1189), "A1": (594, 841), "A2": (420, 594),
    "A3": (297, 420), "A4": (210, 297),
}


class Font:
    def __init__(self, path: str):
        self.path = path
        blob = hb.Blob.from_file_path(path)
        self.hb_font = hb.Font(hb.Face(blob))
        self.tt = TTFont(path)
        self.glyphset = self.tt.getGlyphSet()
        self.upem = self.tt["head"].unitsPerEm

    def shape(self, text: str):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.direction, buf.script, buf.language = "rtl", "Arab", "ar"
        hb.shape(self.hb_font, buf, {"kern": True, "liga": True, "calt": True})
        names = [self.tt.getGlyphName(i.codepoint) for i in buf.glyph_infos]
        return names, buf.glyph_positions

    def outline(self, text: str):
        """Return (svg_path_d, bbox) in font units with the y axis flipped (SVG down)."""
        names, pos = self.shape(text)
        pen = SVGPathPen(self.glyphset)
        bpen = BoundsPen(self.glyphset)
        x = y = 0
        for name, p in zip(names, pos):
            t = (1, 0, 0, -1, x + p.x_offset, -(y + p.y_offset))
            self.glyphset[name].draw(TransformPen(pen, t))
            self.glyphset[name].draw(TransformPen(bpen, t))
            x += p.x_advance
            y += p.y_advance
        return pen.getCommands(), bpen.bounds


def kashida_slots(text: str):
    """Indices after which a tatweel may legally be inserted (inside a joined word)."""
    slots = []
    chars = list(text)
    for i, ch in enumerate(chars):
        if ch not in ARABIC_LETTERS or ch in NON_JOINING_LEFT:
            continue
        # skip trailing diacritics to find the next base letter
        j = i + 1
        while j < len(chars) and chars[j] in HARAKAT:
            j += 1
        if j >= len(chars) or chars[j] not in ARABIC_LETTERS:
            continue
        # never split lam-alef ligature or touch the hamza-only letter
        if ch == "ل" and chars[j] in "اأإآ":
            continue
        if chars[j] == "ء":
            continue
        slots.append(j - 1 if j - 1 > i else i)
    return slots


def with_kashida(text: str, n: int, prefer_last: bool = True):
    """Insert n tatweels spread over legal slots (classical preference: later in the word)."""
    if n <= 0:
        return text
    slots = kashida_slots(text)
    if not slots:
        return text
    order = list(reversed(slots)) if prefer_last else slots
    counts = {s: 0 for s in slots}
    for k in range(n):
        counts[order[k % len(order)]] += 1
    out = []
    for i, ch in enumerate(text):
        out.append(ch)
        out.append(TATWEEL * counts.get(i, 0))
    return "".join(out)


# ---------------------------------------------------------------- layout tree

@dataclass
class Leaf:
    text: str
    font: str = "bold"
    rot: int = 0            # 0 horizontal, -90 reads bottom->top, 90 reads top->bottom
    fill: str = "ink"       # gradient/colour id
    pad: float = 0.02       # padding as a fraction of the cell's short side
    max_kashida: int = 6
    align: str = "center"
    grow: float = 1.0       # >1 lets strokes reach slightly past the cell (interlocking)


@dataclass
class Split:
    axis: str               # "rows" (stacked) or "cols" (side by side, right to left)
    parts: list = field(default_factory=list)   # list of (weight, node)
    gap: float = 0.0        # mm


def layout(node, x, y, w, h, out):
    if isinstance(node, Leaf):
        out.append((node, x, y, w, h))
        return
    total = sum(wt for wt, _ in node.parts)
    n = len(node.parts)
    avail = (h if node.axis == "rows" else w) - node.gap * (n - 1)
    if node.axis == "rows":
        cy = y
        for wt, child in node.parts:
            ch = avail * wt / total
            layout(child, x, cy, w, ch, out)
            cy += ch + node.gap
    else:  # columns are laid out right-to-left, matching Arabic reading order
        cx = x + w
        for wt, child in node.parts:
            cw = avail * wt / total
            cx -= cw
            layout(child, cx, y, cw, h, out)
            cx -= node.gap


def fit_leaf(leaf: Leaf, fonts: dict, x, y, w, h):
    font = fonts[leaf.font]
    pad = leaf.pad * min(w, h)
    W, H = w - 2 * pad, h - 2 * pad
    if leaf.rot in (90, -90):
        W, H = H, W  # fit in the word's own frame
    best = None
    for k in range(0, leaf.max_kashida + 1):
        txt = with_kashida(leaf.text, k)
        d, (x0, y0, x1, y1) = font.outline(txt)
        bw, bh = x1 - x0, y1 - y0
        s = min(W / bw, H / bh)
        area = (bw * s) * (bh * s)
        # small penalty per kashida so they are only used when they really help
        score = area * (1 - 0.015 * k)
        if best is None or score > best[0]:
            best = (score, txt, d, (x0, y0, x1, y1), s)
        if bw * (H / bh) > W:  # already width-bound; more kashida only shrinks it
            break
    _, txt, d, (x0, y0, x1, y1), s = best
    s *= leaf.grow
    cx, cy = x + w / 2, y + h / 2
    bcx, bcy = (x0 + x1) / 2, (y0 + y1) / 2
    tf = (f"translate({cx:.3f} {cy:.3f}) rotate({leaf.rot}) "
          f"scale({s:.6f}) translate({-bcx:.2f} {-bcy:.2f})")
    return txt, d, tf


# ---------------------------------------------------------------- rendering

def build_svg(spec: dict, fonts: dict, bleed_mm: float = 3.0) -> str:
    PW, PH = spec["size_mm"]
    margin = spec.get("margin_frac", 0.08) * min(PW, PH)
    W, H = PW + 2 * bleed_mm, PH + 2 * bleed_mm
    ox, oy = bleed_mm, bleed_mm  # trim origin inside the bleed canvas

    bx, by = ox + margin, oy + margin
    bw, bh = PW - 2 * margin, PH - 2 * margin
    cells = []
    layout(spec["tree"], bx, by, bw, bh, cells)

    defs = [spec["defs"](bx, by, bw, bh, W, H)]
    body = [spec["background"](W, H)]
    used = []
    # back layer: large, low-contrast words behind the main composition (depth, as in
    # two-tone layered calligraphy). Rects are fractions of the text block.
    for leaf, fx, fy, fw, fh in spec.get("underlay", []):
        txt, d, tf = fit_leaf(leaf, fonts, bx + fx * bw, by + fy * bh, fw * bw, fh * bh)
        used.append(txt)
        body.append(f'<path d="{d}" transform="{tf}" fill="url(#{leaf.fill})"/>')
    for leaf, x, y, w, h in cells:
        txt, d, tf = fit_leaf(leaf, fonts, x, y, w, h)
        used.append(txt)
        body.append(f'<path d="{d}" transform="{tf}" fill="url(#{leaf.fill})"/>')
    if spec.get("debug"):
        for _, x, y, w, h in cells:
            body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" '
                        f'stroke="#f0f" stroke-width="0.5"/>')

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" '
           f'viewBox="0 0 {W} {H}">\n<title>{spec["title"]}</title>\n'
           f'<defs>{"".join(defs)}</defs>\n' + "\n".join(body) + "\n</svg>\n")
    return svg, used


def export(svg: str, stem: str, size_mm, bleed_mm=3.0, dpi=300, preview_px=1600):
    import cairosvg
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import RectangleObject

    with open(stem + ".svg", "w", encoding="utf-8") as f:
        f.write(svg)

    # PDF (vector) with bleed; TrimBox marks the final A-size page
    pdf_bytes = cairosvg.svg2pdf(bytestring=svg.encode())
    r = PdfReader(io.BytesIO(pdf_bytes))
    wtr = PdfWriter()
    page = r.pages[0]
    pt = 72 / 25.4
    b = bleed_mm * pt
    pw, ph = float(page.mediabox.width), float(page.mediabox.height)
    page.trimbox = RectangleObject([b, b, pw - b, ph - b])
    page.bleedbox = RectangleObject([0, 0, pw, ph])
    wtr.add_page(page)
    wtr.add_metadata({"/Title": stem.split("/")[-1]})
    with open(stem + ".pdf", "wb") as f:
        wtr.write(f)

    # PNG at full print resolution, trimmed (no bleed)
    PW, PH = size_mm
    px_w = round(PW / 25.4 * dpi)
    px_h = round(PH / 25.4 * dpi)
    W, H = PW + 2 * bleed_mm, PH + 2 * bleed_mm
    trimmed = svg.replace(f'viewBox="0 0 {W} {H}"',
                          f'viewBox="{bleed_mm} {bleed_mm} {PW} {PH}"', 1)
    trimmed = trimmed.replace(f'width="{W}mm" height="{H}mm"',
                              f'width="{PW}mm" height="{PH}mm"', 1)
    cairosvg.svg2png(bytestring=trimmed.encode(), write_to=stem + "_300dpi.png",
                     output_width=px_w, output_height=px_h, dpi=dpi)
    cairosvg.svg2png(bytestring=trimmed.encode(), write_to=stem + "_preview.png",
                     output_width=preview_px,
                     output_height=round(preview_px * PH / PW))
    # tag 300 DPI in the PNG metadata
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(stem + "_300dpi.png")
    im.save(stem + "_300dpi.png", dpi=(dpi, dpi), optimize=True)
    return px_w, px_h
