"""
Justified, interlocking word-block composer.

Every word is set at ONE size. Words run in justified lines (right and left edges
aligned, so the block reads as a clean rectangle). Some words are set vertically and
span several lines. Lines are pulled up until their ink almost touches the line above
(shape-aware), so the texture is dense, but words never cross: a clear gap is kept
around every word. Reading order is always top->bottom, right->left.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import binary_dilation
from scipy.signal import fftconvolve

from calligraphy import Font, with_kashida
from pack import _raster

VMARK = "|"   # prefix: this token is a whole phrase set vertically


@dataclass
class Glyph:
    text: str
    rot: int
    m: np.ndarray       # ink mask (px)
    ox: float           # mask centre (px)
    oy: float
    cx: float           # bbox centre (font units)
    cy: float
    base: float         # baseline row inside the mask (px), horizontal words only
    s: float


@dataclass
class Item:
    g: Glyph
    x: int              # mask top-left inside the page (px)
    y: int
    pid: int = -1       # phrase index this word belongs to


class RowComposer:
    def __init__(self, font: Font, block_mm, em_mm, res=2.0, gap_mm=2.5,
                 stroke_frac=0.01, row_pitch=1.25, vertical_every=3):
        self.font, self.res = font, res
        self.W, self.H = int(block_mm[0] * res), int(block_mm[1] * res)
        self.em, self.s = em_mm, em_mm / font.upem
        self.gap = max(1, int(round(gap_mm * res)))
        self.stroke = stroke_frac * font.upem
        self.pitch = int(row_pitch * em_mm * res)
        self.vertical_every = vertical_every
        self.min_fill = 0.85
        self._c = {}

    # ------------------------------------------------------------ glyphs
    def glyph(self, text, rot=0):
        key = (text, rot)
        if key not in self._c:
            d, b = self.font.outline(text)
            m, (ox, oy), (cx, cy) = _raster(d, b, self.s, rot, self.stroke, self.res)
            base = oy - cy * self.s * self.res
            self._c[key] = (Glyph(text, rot, m, ox, oy, cx, cy, base, self.s), d)
        return self._c[key][0]

    def path(self, g):
        return self._c[(g.text, g.rot)][1]

    # ------------------------------------------------------------ one line
    def line(self, words, width):
        """Fill one line right->left from `words` (list of str). Returns (items, n_used)."""
        cap = int(self.em * self.res * 3.2)          # canvas height for one line
        base = int(cap * 0.55)
        R = np.zeros((cap, width), bool)
        items, prev_left = [], width
        for n, (w, pid) in enumerate(words):
            g = self.glyph(w)
            mh, mw = g.m.shape
            y = int(round(base - g.base))
            if y < 0 or y + mh > cap or mw > width:
                return items, n, R, base
            slab = binary_dilation(R[y:y + mh], iterations=self.gap)
            ov = fftconvolve(slab.astype(np.float32), g.m[::-1, ::-1].astype(np.float32),
                             mode="valid")[0]
            ok = ov < 0.5
            # keep reading order: the new word's centre must be left of the previous ink start
            xs = np.arange(len(ok))
            ok &= (xs + mw / 2) < prev_left
            if not ok.any():
                return items, n, R, base
            x = int(np.nonzero(ok)[0].max())
            R[y:y + mh, x:x + mw] |= g.m
            items.append(Item(g, x, y, pid))
            cols = np.nonzero(g.m.any(0))[0]
            prev_left = x + cols.min()
        return items, len(words), R, base

    def justify(self, items, width):
        """Spread leftover space evenly between words so the line touches both edges."""
        if not items:
            return items
        lefts = [it.x + np.nonzero(it.g.m.any(0))[0].min() for it in items]
        rights = [it.x + np.nonzero(it.g.m.any(0))[0].max() for it in items]
        shift_r = (width - 1) - rights[0]
        for it in items:
            it.x += shift_r
        left = min(l + shift_r for l in lefts)
        if len(items) > 1 and left > 0:
            n = len(items) - 1
            for i, it in enumerate(items):
                it.x -= int(round(left * i / n))
        return items

    @staticmethod
    def stamp(items, h, w):
        M = np.zeros((h, w), bool)
        for it in items:
            mh, mw = it.g.m.shape
            y0, x0 = max(0, it.y), max(0, it.x)
            y1, x1 = min(h, it.y + mh), min(w, it.x + mw)
            if y1 > y0 and x1 > x0:
                M[y0:y1, x0:x1] |= it.g.m[y0 - it.y:y1 - it.y, x0 - it.x:x1 - it.x]
        return M

    # ------------------------------------------------------------ the block
    def compose(self, phrases, vertical_ok=lambda ph: False, every=3, lookahead=4):
        """phrases: list of phrase strings in reading order.
        Every `every`-th band opens with a vertical phrase: the next eligible phrase
        (within `lookahead` phrases) is set vertically as one unit, never split, and
        justified lines are stacked beside it. Returns bands (lists of Items)."""
        W = self.W
        queue = [(w, pid) for pid, ph in enumerate(phrases) for w in ph.split()]
        bands, k, side = [], 0, 0
        while queue:
            k += 1
            vpid = None
            at_boundary = (sum(1 for _, q in queue if q == queue[0][1])
                           == len(phrases[queue[0][1]].split()))
            if every and k % every == 0 and not at_boundary:
                k -= 1      # never interrupt a phrase that wraps onto the next line
            elif every and k % every == 0:
                started = {queue[0][1]} if queue else set()
                seen = []
                for w, pid in queue:
                    if pid not in seen:
                        seen.append(pid)
                    if len(seen) > lookahead:
                        break
                for pid in seen:
                    if vertical_ok(phrases[pid]) and pid not in started:
                        vpid = pid
                        break
                    if vertical_ok(phrases[pid]) and pid in started and \
                            sum(1 for _, q in queue if q == pid) == len(phrases[pid].split()):
                        vpid = pid          # phrase not begun yet: it is at the front
                        break
            if vpid is not None:
                queue = [t for t in queue if t[1] != vpid]
                side += 1
                band, used = self._vertical_band(phrases[vpid], vpid, queue,
                                                 right=side % 2 == 1)
            else:
                items, used, _, _ = self.line(queue, W)
                if used == 0:
                    break
                if every and (k + 1) % every == 0 and used < len(queue) \
                        and queue[used][1] == queue[used - 1][1]:
                    # a vertical band is due next: try to end this line on a phrase
                    # boundary, as long as the line stays well filled
                    ends = [j + 1 for j in range(used - 1) if queue[j + 1][1] != queue[j][1]]
                    if ends:
                        it2, u2, _, _ = self.line(queue[:ends[-1]], W)
                        left = min(it.x + np.nonzero(it.g.m.any(0))[0].min() for it in it2)
                        if (W - left) / W >= self.min_fill:
                            items, used = it2, u2
                band = self.justify(items, W)
            if not band:
                break
            bands.append(band)
            queue = queue[used:]
        return bands

    def _vertical_band(self, vtext, vpid, toks, right=True):
        """A vertical phrase on one side, with justified lines stacked beside it until
        the lines are as tall as the phrase."""
        W = self.W
        g = self.glyph(vtext, -90)
        vh, vw = g.m.shape
        inner_w = W - vw - self.gap * 4
        lines, used = [], 0
        while used < len(toks):
            line_items, n, _, _ = self.line(toks[used:], inner_w)
            if n == 0:
                break
            lines.append(self.justify(line_items, inner_w))
            used += n
            _, P = self.stack(lines, inner_w)
            rows = np.nonzero(P.any(1))[0]
            if rows.max() - rows.min() >= 0.92 * vh or len(lines) >= 6:
                break
        if not lines:
            return [], 0
        placed, P = self.stack(lines, inner_w)
        rows = np.nonzero(P.any(1))[0]
        ox = 0 if right else W - inner_w
        items = []
        for ln in placed:
            for it in ln:
                it.x += ox
                items.append(it)
        mid = (rows.min() + rows.max()) / 2
        v = Item(g, W - vw if right else 0, int(round(mid - vh / 2)), vpid)
        return [v] + items, used

    def stack(self, bands, W=None):
        """Pull each band up until it nearly touches what is above. Returns placed items."""
        W = W or self.W
        page_h = self.H * 3
        P = np.zeros((page_h, W), bool)
        placed, tops = [], []
        prev_y = None
        for band in bands:
            ys = [it.y for it in band]
            y_min = min(ys)
            for it in band:
                it.y -= y_min
            bh = max(it.y + it.g.m.shape[0] for it in band)
            B = self.stamp(band, bh, W)
            if prev_y is None:
                y = 0
            else:
                lo = prev_y + int(0.45 * self.pitch)
                Pd = binary_dilation(P[: lo + bh * 3 + self.pitch * 2], iterations=self.gap)
                ov = fftconvolve(Pd.astype(np.float32), B[::-1, ::-1].astype(np.float32),
                                 mode="valid")[:, 0]
                cand = np.nonzero(ov[lo:] < 0.5)[0]
                y = lo + (int(cand[0]) if len(cand) else len(ov) - lo)
            for it in band:
                it.y += y
            P[y:y + bh] |= B[: max(0, min(bh, page_h - y))]
            placed.append(band)
            tops.append(y)
            prev_y = y
        return placed, P
