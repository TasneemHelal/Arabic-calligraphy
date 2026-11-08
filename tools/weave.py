"""
Interwoven calligraphy composer.

Each word is shaped by HarfBuzz (so joins, dots and harakat are always correct),
lengthened with genuine kashida (tatweel) extensions, then bent as a whole along an
arc or S-curve so its strokes sweep. Words are woven into a silhouette in reading
order (top->bottom, right->left); extensions may cross neighbouring words, which is
what gives the interlaced look. Nothing is invented: only the phrase's own words,
with their own diacritics, are drawn.
"""
from __future__ import annotations

import io
import math
import random
from dataclasses import dataclass

import cairosvg
import numpy as np
from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from PIL import Image
from scipy.signal import fftconvolve

from calligraphy import Font, kashida_slots, with_kashida


class FlattenPen(BasePen):
    def __init__(self, glyphset, steps=10):
        super().__init__(glyphset)
        self.contours, self.cur, self.steps = [], [], steps

    def _moveTo(self, p):
        self.cur = [p]

    def _lineTo(self, p):
        self.cur.append(p)

    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3
            self.cur.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                             a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))

    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            a, b, c = (1 - t) ** 2, 2 * (1 - t) * t, t ** 2
            self.cur.append((a * p0[0] + b * p1[0] + c * p2[0],
                             a * p0[1] + b * p1[1] + c * p2[1]))

    def _closePath(self):
        if self.cur:
            self.contours.append(np.array(self.cur))
        self.cur = []

    _endPath = _closePath


def word_polys(font: Font, text: str):
    names, pos = font.shape(text)
    pen = FlattenPen(font.glyphset)
    x = y = 0
    for name, p in zip(names, pos):
        t = (1, 0, 0, -1, x + p.x_offset, -(y + p.y_offset))
        font.glyphset[name].draw(TransformPen(pen, t))
        x += p.x_advance
        y += p.y_advance
    return pen.contours


def warp(polys, bend=0.0, wave=0.0):
    """Bend the whole word along an arc (`bend` = total turn in radians; >0 smile,
    <0 frown) plus an optional S-wave (`wave` = amplitude as a fraction of length)."""
    allp = np.concatenate(polys)
    x0, x1 = allp[:, 0].min(), allp[:, 0].max()
    L = max(1.0, x1 - x0)
    xc = (x0 + x1) / 2
    out = []
    for c in polys:
        x, y = c[:, 0] - xc, c[:, 1]
        if abs(bend) > 1e-3:
            R = -L / bend
            phi = x / R
            r = R - y
            nx, ny = r * np.sin(phi), R - r * np.cos(phi)
        else:
            nx, ny = x, y.copy()
        if wave:
            u = (c[:, 0] - x0) / L
            ny = ny + wave * L * np.sin(2 * np.pi * u)
        out.append(np.stack([nx, ny], 1))
    return out


TATWEEL = "\u0640"


def resample(c, step):
    """Subdivide long straight segments so the sweep bends them smoothly."""
    pts = [c[0]]
    nxt = np.roll(c, -1, 0)
    for p0, p1 in zip(c, nxt):
        n = int(np.hypot(*(p1 - p0)) // step)
        for i in range(1, n + 1):
            pts.append(p0 + (p1 - p0) * i / (n + 1))
        pts.append(p1)
    return np.array(pts[:-1])


def ribbon_word(font: Font, word: str, slot=None, k=0, arch=0.0, step=0.0):
    """Shape `word` with k tatweels after character index `slot`, then sweep only the
    kashida: inside the kashida span points are displaced vertically by
        step * smoothstep(t) + arch * L * sin(pi t)
    (t = position along the span, L = span length). Letters outside the span move
    rigidly, so every letterform, dot and haraka stays exactly as designed."""
    import uharfbuzz as hb
    text = word if not k or slot is None else word[: slot + 1] + TATWEEL * k + word[slot + 1:]
    buf = hb.Buffer()
    buf.add_str(text)
    buf.direction, buf.script, buf.language = "rtl", "Arab", "ar"
    hb.shape(font.hb_font, buf, {})
    infos, pos = buf.glyph_infos, buf.glyph_positions
    kset = set(range(slot + 1, slot + 1 + k)) if k and slot is not None else set()
    pen = FlattenPen(font.glyphset, steps=8)
    x = 0
    span = [None, None]
    for info, p in zip(infos, pos):
        name = font.tt.getGlyphName(info.codepoint)
        if info.cluster in kset:
            span[0] = x if span[0] is None else min(span[0], x)
            span[1] = x + p.x_advance if span[1] is None else max(span[1], x + p.x_advance)
        t = (1, 0, 0, -1, x + p.x_offset, -p.y_offset)
        font.glyphset[name].draw(TransformPen(pen, t))
        x += p.x_advance
    polys = pen.contours
    if span[0] is None or (not arch and not step):
        return polys
    a, b = span
    L = max(1.0, b - a)
    polys = [resample(c, 12.0) for c in polys]
    out = []
    for c in polys:
        t = np.clip((c[:, 0] - a) / L, 0, 1)
        sm = t * t * (3 - 2 * t)
        dy = step * sm + arch * L * np.sin(np.pi * t)
        out.append(np.stack([c[:, 0], c[:, 1] + dy], 1))
    return out


def polys_d(polys):
    parts = []
    for c in polys:
        pts = " ".join(f"{px:.1f} {py:.1f}" for px, py in c)
        parts.append(f"M{pts}Z")
    return "".join(parts)


def polys_bounds(polys):
    a = np.concatenate(polys)
    return a[:, 0].min(), a[:, 1].min(), a[:, 0].max(), a[:, 1].max()


def raster(d, bounds, s, rot, res, stroke=0.0):
    x0, y0, x1, y1 = bounds
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    k = s * res
    a = math.radians(rot)
    hw, hh = (x1 - x0) / 2 * k + 2, (y1 - y0) / 2 * k + 2
    W = abs(hw * math.cos(a)) + abs(hh * math.sin(a))
    H = abs(hw * math.sin(a)) + abs(hh * math.cos(a))
    w, h = int(math.ceil(2 * W)) + 2, int(math.ceil(2 * H)) + 2
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">'
           f'<path d="{d}" fill="#000" stroke="#000" stroke-width="{stroke}" '
           f'transform="translate({w/2} {h/2}) rotate({rot}) scale({k}) '
           f'translate({-cx} {-cy})"/></svg>')
    png = cairosvg.svg2png(bytestring=svg.encode())
    m = np.asarray(Image.open(io.BytesIO(png)).split()[-1]) > 96
    return m, (w / 2, h / 2), (cx, cy)


@dataclass
class Placed:
    text: str
    d: str
    transform: str
    index: int


class Weaver:
    def __init__(self, font, shape_mask, res=1.0, weave=0.06, seed=3, flow=0.35,
                 variants=48, kashida=(0, 4, 8, 12, 16), arches=(-0.55, -0.3, 0, 0.3, 0.55),
                 steps=(-700, -350, 0, 350), bends=(-0.25, 0, 0.25), rots=(0, -10, 10)):
        self.font = font
        self.res = res
        self.shape = shape_mask.astype(bool)          # True = inside the silhouette
        self.H, self.W = shape_mask.shape
        self.ink = np.zeros_like(self.shape)
        self.outside = (~self.shape).astype(np.float32)
        self.weave = weave
        self.rng = random.Random(seed)
        self.flow = flow
        self.nvar = variants
        self.kash, self.arches, self.steps = kashida, arches, steps
        self.bends, self.rots = bends, rots
        self.placed: list[Placed] = []
        self._poly_cache = {}

    def _variants(self, word):
        slots = kashida_slots(word) or [None]
        combos = []
        for sl in slots:
            for k in (self.kash if sl is not None else (0,)):
                for ar in (self.arches if k else (0,)):
                    for st in (self.steps if k else (0,)):
                        for b in self.bends:
                            for r in self.rots:
                                combos.append((sl, k, ar, st, b, r))
        self.rng.shuffle(combos)
        return [(slots[-1], 0, 0, 0, 0, 0)] + combos[: self.nvar]

    def _shape(self, word, sl, k, ar, st, bend):
        key = (word, sl, k, ar, st, bend)
        if key not in self._poly_cache:
            polys = ribbon_word(self.font, word, sl, k, ar, st)
            if bend:
                polys = warp(polys, bend, 0)
            self._poly_cache[key] = (polys_d(polys), polys_bounds(polys))
        return self._poly_cache[key]

    def place(self, word, em_mm, index, min_score=-1e9, target=None, zone=None):
        """target: (x, y) mm the word's centre should gravitate to; zone: (y0, y1) mm
        band its centre must stay in. Without them, reading-order packing is used."""
        s = em_mm / self.font.upem
        best = None
        inkf = self.ink.astype(np.float32)
        for (sl, k, ar, st, bend, rot) in self._variants(word):
            d, b = self._shape(word, sl, k, ar, st, bend)
            m, (ox, oy), (cx, cy) = raster(d, b, s, rot, self.res)
            mh, mw = m.shape
            if mh >= self.H or mw >= self.W:
                continue
            mf = m[::-1, ::-1].astype(np.float32)
            area = m.sum()
            out = fftconvolve(self.outside, mf, mode="valid")
            cross = fftconvolve(inkf, mf, mode="valid")
            ok = (out <= 0.004 * area + 0.5) & (cross <= self.weave * area + 0.5)
            if not ok.any():
                continue
            if zone is not None:
                cy_all = (np.arange(ok.shape[0]) + mh / 2) / self.res
                ok &= ((cy_all >= zone[0]) & (cy_all <= zone[1]))[:, None]
                if not ok.any():
                    continue
            ys, xs = np.nonzero(ok)
            right_gap = (self.W - (xs + mw)) / self.res
            if target is not None:
                pos = 0.6 * np.hypot((xs + mw / 2) / self.res - target[0],
                                     (ys + mh / 2) / self.res - target[1])
            else:
                pos = ys / self.res + self.flow * right_gap
            # position, then prefer long sweeping variants (more ink = longer strokes)
            score = (pos
                     - 1.0 * math.sqrt(area) / self.res
                     - 30 * np.minimum(cross[ys, xs] / area, self.weave)  # reward some interlacing
                     + 3 * abs(rot) / 10 + 4 * abs(bend))
            sel = score >= min_score
            if not sel.any():
                continue
            i = int(np.argmin(np.where(sel, score, np.inf)))
            cand = (score[i], xs[i], ys[i], m, ox, oy, cx, cy, d, rot)
            if best is None or cand[0] < best[0]:
                best = cand
        if best is None:
            return None
        sc, px, py, m, ox, oy, cx, cy, d, rot = best
        mh, mw = m.shape
        self.ink[py:py + mh, px:px + mw] |= m
        X, Y = (px + ox) / self.res, (py + oy) / self.res
        tf = (f"translate({X:.2f} {Y:.2f}) rotate({rot}) scale({s:.6f}) "
              f"translate({-cx:.1f} {-cy:.1f})")
        self.placed.append(Placed(word, d, tf, index))
        return sc

    def coverage(self):
        return self.ink[self.shape].mean()


def zones_for(n_words, per_zone, W_mm, H_mm, shape):
    """Reading-order targets: zones top->bottom, words right->left inside a zone."""
    groups = []
    i = 0
    for z in range(math.ceil(n_words / per_zone)):
        m = min(per_zone, n_words - i)
        groups.append(list(range(i, i + m)))
        i += m
    nz = len(groups)
    out = {}
    rows = shape.any(1)
    top, bot = np.nonzero(rows)[0][[0, -1]]
    zh = (bot - top) / nz
    for z, g in enumerate(groups):
        y0, y1 = top + z * zh, top + (z + 1) * zh
        yc = (y0 + y1) / 2
        cols = np.nonzero(shape[int(yc)])[0]
        x0, x1 = (cols.min(), cols.max()) if len(cols) else (0, shape.shape[1])
        m = len(g)
        for j, wi in enumerate(g):
            xc = x1 - (j + 0.5) * (x1 - x0) / m
            out[wi] = ((xc, yc), (y0 - 0.5 * zh, y1 + 0.5 * zh))
    return out


def weave(font, words, shape_mask, em_mm, seed=3, shrink=0.9, min_size=0.6,
          per_zone=1, res=1.0, **kw):
    wv = Weaver(font, shape_mask, seed=seed, res=res, **kw)
    H, W = shape_mask.shape
    tz = zones_for(len(words), per_zone, W / res, H / res, shape_mask)
    for i, (w, size) in enumerate(words):
        (tx, ty), (z0, z1) = tz[i]
        sz, sc = size, None
        while sz >= min_size and sc is None:
            sc = wv.place(w, em_mm * sz, i, target=(tx / res, ty / res),
                          zone=(z0 / res, z1 / res))
            sz *= shrink
        if sc is None:
            return wv, False
    return wv, True
