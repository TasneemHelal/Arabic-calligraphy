"""
Dense interlocking word-block composer (free-Diwani / "text as texture" style).

Words are shaped with HarfBuzz, rasterised only for collision tests, and placed
greedily in Arabic reading order (top->bottom, right->left) using the real ink shape
of every word, not its bounding box. Strokes are allowed to nestle into each other's
counters and to cross very slightly, which is what makes the block interlock.
The final artwork is written as vector paths.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

import cairosvg
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation, binary_opening
from scipy.signal import fftconvolve

from calligraphy import Font


@dataclass
class Word:
    text: str
    size: float = 1.0                 # relative to the base em size
    rotations: tuple = (0, 0, 10, 22, -10, -90)
    phrase: int = 0                   # phrase index (keeps word order inside phrases)
    filler: bool = False
    stretches: tuple = (1.0,)         # horizontal extension factors to try (letters stay joined)


@dataclass
class Placed:
    word: Word
    d: str
    transform: str
    score: float


def _raster(d, bounds, s, rot, stroke_units, res, sx=1.0):
    """Rasterise one word: returns (mask bool array, centre offset in px)."""
    x0, y0, x1, y1 = bounds
    pad = stroke_units
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    k = s * res                      # font units -> px
    a = math.radians(rot)
    hw, hh = (x1 - x0) / 2 * k * sx, (y1 - y0) / 2 * k
    W = abs(hw * math.cos(a)) + abs(hh * math.sin(a))
    H = abs(hw * math.sin(a)) + abs(hh * math.cos(a))
    w, h = max(2, int(math.ceil(2 * W)) + 2), max(2, int(math.ceil(2 * H)) + 2)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">'
           f'<path d="{d}" fill="#000" stroke="#000" stroke-width="{stroke_units}" '
           f'stroke-linejoin="round" transform="translate({w/2} {h/2}) rotate({rot}) '
           f'scale({k * sx} {k}) translate({-cx} {-cy})"/></svg>')
    png = cairosvg.svg2png(bytestring=svg.encode())
    import io
    m = np.asarray(Image.open(io.BytesIO(png)).split()[-1]) > 96
    return m, (w / 2, h / 2), (cx, cy)


class Packer:
    def __init__(self, font: Font, block_mm, res=1.0, gap_mm=1.0, overlap=0.006,
                 stroke_frac=0.018, seed=7, rot_penalty=None, flow=0.30):
        self.font = font
        self.bw, self.bh = block_mm
        self.res = res                                   # px per mm
        self.W, self.H = int(self.bw * res), int(self.bh * res)
        self.occ = np.zeros((self.H, self.W), bool)
        self.gap = max(0, int(round(gap_mm * res)))
        self.overlap = overlap
        self.stroke_frac = stroke_frac
        self.rng = random.Random(seed)
        self.flow = flow
        self.rot_penalty = rot_penalty or {0: 0, 10: 6, -10: 6, 22: 14, -22: 14,
                                           -90: 10, 90: 18, 35: 22}
        self.placed: list[Placed] = []
        self._cache = {}
        # interlacing (off by default): thin strokes may cross thin strokes, never thick
        # letter bodies or dots. See enable_interlace().
        self.interlace = None
        self.core = np.zeros((self.H, self.W), bool)
        # minimum distance between two copies of the same word (0 = no rule)
        self.same_word_r = 0
        self.centers = {}

    def enable_interlace(self, core_mm=2.0, cross_tol=0.035, reward=20.0):
        """core_mm: strokes thicker than ~2*core_mm count as letter bodies (protected).
        cross_tol: max share of a word's ink that may cross other words' thin strokes."""
        self.interlace = dict(r=max(1, int(round(core_mm * self.res))),
                              tol=cross_tol, reward=reward)

    @staticmethod
    def word_key(text):
        return "".join(ch for ch in text
                       if not (0x064B <= ord(ch) <= 0x0652 or ch in "\u0670\u0640"))

    def rebuild_occ(self):
        self.occ[:] = False
        for p in self.placed:
            g = getattr(p, "geom", None)
            if g is not None:
                mh, mw = g["m"].shape
                self.occ[g["py"]:g["py"] + mh, g["px"]:g["px"] + mw] |= g["m"]

    def _shape(self, text):
        if text not in self._cache:
            if len(text) == 1 and 0x064B <= ord(text) <= 0x0652:
                self._cache[text] = self.font.glyph_outline(text)   # decorative mark
            else:
                self._cache[text] = self.font.outline(text)
        return self._cache[text]

    def try_place(self, word: Word, em_mm: float, min_score=-1e9, max_score=1e9, after=None,
                  rot_pen=None):
        """after=(cx, cy, line) px: centre of the previous word of the same phrase; the new
        word must come after it in reading order (to its left, or on a lower line)."""
        d, bounds = self._shape(word.text)
        upem = self.font.upem
        s = em_mm / upem                                  # font units -> mm
        stroke_units = self.stroke_frac * upem
        occ = binary_dilation(self.occ, iterations=self.gap) if self.gap else self.occ
        occ_f = occ.astype(np.float32)
        best = None
        rots = list(dict.fromkeys(word.rotations))
        combos = [(r, sx) for sx in dict.fromkeys(word.stretches) for r in rots]
        for rot, sx in combos:
            m, (ox, oy), (cx, cy) = _raster(d, bounds, s, rot, stroke_units, self.res, sx)
            mh, mw = m.shape
            if mh >= self.H or mw >= self.W:
                continue
            ink = m.sum()
            mk = m[::-1, ::-1].astype(np.float32)
            il = self.interlace if not word.filler else None
            if il is None:
                ov = fftconvolve(occ_f, mk, mode="valid")
                ok = ov <= self.overlap * ink + 0.5
                cross = None
            else:
                # 1) new ink keeps clear of existing letter bodies and dots
                core_d = binary_dilation(self.core, iterations=self.gap) if self.gap else self.core
                ok = fftconvolve(core_d.astype(np.float32), mk, mode="valid") < 0.5
                # 2) new letter bodies keep clear of all existing ink
                mcore = binary_opening(m, iterations=il["r"])
                ok &= fftconvolve(occ_f, mcore[::-1, ::-1].astype(np.float32),
                                  mode="valid") < 0.5
                # 3) thin-over-thin crossings are allowed, but only a little
                cross = fftconvolve(self.occ.astype(np.float32), mk, mode="valid")
                ok &= cross <= il["tol"] * ink + 0.5
            if after is not None:
                pcx, pcy, line = after
                cy_ = (np.arange(ok.shape[0]) + mh / 2)[:, None]
                cx_ = (np.arange(ok.shape[1]) + mw / 2)[None, :]
                ok &= ((cx_ < pcx) & (np.abs(cy_ - pcy) < 1.4 * line)) | (cy_ > pcy + 0.35 * line)
            if self.same_word_r and not word.filler:
                key = self.word_key(word.text)
                cy_ = (np.arange(ok.shape[0]) + mh / 2)[:, None]
                cx_ = (np.arange(ok.shape[1]) + mw / 2)[None, :]
                for (qx, qy) in self.centers.get(key, ()):
                    ok &= (cx_ - qx) ** 2 + (cy_ - qy) ** 2 >= self.same_word_r ** 2
            if not ok.any():
                continue
            ys, xs = np.nonzero(ok)
            # reading order: top first, then right-most; flow < 1 lets a line drift
            right_gap = (self.W - (xs + mw)) / self.res
            score = (ys / self.res + self.flow * right_gap + (rot_pen or self.rot_penalty).get(rot, 20)
                     + 6 * (sx - 1))
            score = score + np.array([self.rng.uniform(0, 3) for _ in range(1)])[0]
            if cross is not None and il["reward"]:
                score = score - il["reward"] * np.minimum(cross[ys, xs] / ink, il["tol"]) / il["tol"]
            sel = (score >= min_score) & (score <= max_score)
            if not sel.any():
                continue
            if word.filler:
                # fillers go to a random valid hole so they spread evenly over the block
                idx = np.nonzero(sel)[0]
                i = idx[self.rng.randrange(len(idx))]
                score = np.full_like(score, self.rng.uniform(0, 1))
            else:
                i = np.argmin(np.where(sel, score, np.inf))
            cand = (score[i], rot, xs[i], ys[i], m, ox, oy, cx, cy, sx)
            if best is None or cand[0] < best[0]:
                best = cand
        if best is None:
            return None
        sc, rot, px, py, m, ox, oy, cx, cy, sx = best
        mh, mw = m.shape
        self.occ[py:py + mh, px:px + mw] |= m
        if self.interlace is not None and not word.filler:
            self.core[py:py + mh, px:px + mw] |= binary_opening(m, iterations=self.interlace["r"])
        if not word.filler:
            self.centers.setdefault(self.word_key(word.text), []).append((px + mw / 2, py + mh / 2))
        X = (px + ox) / self.res
        Y = (py + oy) / self.res
        tf = (f"translate({X:.3f} {Y:.3f}) rotate({rot}) scale({s * sx:.6f} {s:.6f}) "
              f"translate({-cx:.1f} {-cy:.1f})")
        p = Placed(word, d, tf, sc)
        p.geom = dict(m=m, px=int(px), py=int(py), ox=ox, oy=oy, rot=rot, s=s, cx=cx, cy=cy, sx=sx)
        self.placed.append(p)
        return p

    def coverage(self):
        return self.occ.mean()

    def snap_to_edges(self, reach_mm, passes=2):
        """Slide words that sit near a block edge outward until their ink touches that
        edge, never closer than the word gap to any other ink. Gives straight sides."""
        reach = int(reach_mm * self.res)
        for _ in range(passes):
            for p in self.placed:
                g = getattr(p, "geom", None)
                if g is None or p.word.filler:
                    continue
                m = g["m"]
                mh, mw = m.shape
                ys, xs = np.nonzero(m)
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    px, py = g["px"], g["py"]
                    if dx < 0:
                        dist = px + xs.min()
                    elif dx > 0:
                        dist = self.W - 1 - (px + xs.max())
                    elif dy < 0:
                        dist = py + ys.min()
                    else:
                        dist = self.H - 1 - (py + ys.max())
                    if dist <= 0 or dist > reach:
                        continue
                    self.occ[py:py + mh, px:px + mw] &= ~m
                    best = 0
                    for step in range(dist, 0, -1):
                        nx, ny = px + dx * step, py + dy * step
                        y0, y1 = max(0, ny - self.gap), min(self.H, ny + mh + self.gap)
                        x0, x1 = max(0, nx - self.gap), min(self.W, nx + mw + self.gap)
                        win = binary_dilation(self.occ[y0:y1, x0:x1], iterations=self.gap) \
                            if self.gap else self.occ[y0:y1, x0:x1]
                        sub = win[ny - y0:ny - y0 + mh, nx - x0:nx - x0 + mw]
                        if sub.shape == m.shape and not (sub & m).any():
                            best = step
                            break
                    g["px"], g["py"] = px + dx * best, py + dy * best
                    self.occ[g["py"]:g["py"] + mh, g["px"]:g["px"] + mw] |= m
                X = (g["px"] + g["ox"]) / self.res
                Y = (g["py"] + g["oy"]) / self.res
                p.transform = (f"translate({X:.3f} {Y:.3f}) rotate({g['rot']}) "
                               f"scale({g['s'] * g.get('sx', 1.0):.6f} {g['s']:.6f}) "
                               f"translate({-g['cx']:.1f} {-g['cy']:.1f})")

    def lowest_ink_mm(self):
        rows = np.nonzero(self.occ.any(1))[0]
        return rows.max() / self.res if len(rows) else 0


def compose(font, block_mm, words, fillers, marks_font=None, em_mm=60.0, seed=7,
            shrink=0.88, min_size=0.45, **kw):
    """Place phrase words in order, then filler words, then decorative marks."""
    pk = Packer(font, block_mm, seed=seed, **kw)
    failed = []
    last_score = -1e9
    for w in words:
        size = w.size
        placed = None
        while size >= min_size and placed is None:
            # keep words of the same phrase in reading order
            placed = pk.try_place(w, em_mm * size, min_score=last_score - 15)
            size *= shrink
        if placed is None:
            failed.append(w.text)
        else:
            last_score = placed.score
    # fillers: smaller meaningful words, anywhere they fit
    for w in fillers:
        size = w.size
        while size >= min_size * 0.6:
            if pk.try_place(w, em_mm * size):
                break
            size *= shrink
    return pk, failed
