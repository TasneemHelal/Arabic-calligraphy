"""
Square Kufic (Kufi Murabba') construction kit.

Every letter is drawn by hand on a square grid: one cell = one stroke width = one gap.
Nothing here comes from a font. Rows 0-6 are the letter body (row 6 = baseline),
rows 7-8 hold descenders (ر، و) and dots below (ب، ي).
  '#' = ink   'o' = dot (drawn in the accent color)   '.' = empty
Row 1 only ever holds tall verticals (ا، ل، ك), so a line is made taller by repeating
row 1: alif and lam grow, everything else keeps its proportions.
"""
import numpy as np

ROWS = 9
BASE = 6

def _g(*rows):
    w = max(len(r) for r in rows) if rows else 1
    rows = list(rows) + [""] * (ROWS - len(rows))
    return [r.ljust(w, ".") for r in rows]

E = ""  # empty row shorthand

def tooth(form, dots_above="", dots_below=""):
    base = "###" if form == "M" else "##."
    return _g(E, E, dots_above or "...", E, ".#.", ".#.", base, E, dots_below or "...")

def bowl(dots_in="", dots_below=""):          # final / isolated ب ت ن
    return _g(E, E, E, E, "#" + (dots_in or "....")[0:4], "#....", "#####", E, dots_below or ".....")

def head(form, dots):                          # initial / medial ف ق
    base = "###" if form == "M" else "#.."
    return _g(dots, E, "###", "#.#", "###", "#..", base)

def head_final(dots, isolated=False):         # final / isolated ف ق
    base = "####.." if isolated else "######"
    return _g(dots, E, "...###", "...#.#", "...###", "#..#..", base)

ALEF = _g(*["#"] * 7)
LAM_F = _g("..#", "..#", "..#", "..#", "#.#", "#.#", "###")
MEEM = _g(E, E, E, E, "###", "#.#", "###")
SEEN = _g(E, E, E, E, E, "#.#.#", "#####")
SHEEN = _g("..o..", E, ".o.o.", E, E, "#.#.#", "#####")
SAD = _g(E, E, E, E, "..####", "#.#..#", "######")
HAH_N = lambda dot="": _g(E, E, E, "####", "#..#", "#...", "#." + (dot or ".") + ".")
HAH_M = lambda dot="": _g(E, E, E, "#####", "#...#", "#." + (dot or ".") + ".#", "#...#")
WAW = _g(E, E, E, E, "...###", "...#.#", "######", "#.....", "#.....")
REH = _g(E, E, E, E, E, E, "###", "#..", "#..")
DAL = _g(E, E, E, E, "###", "..#", "###")
HEH_M = _g(E, E, "###", "#.#", "###", "#.#", "###")
HEH_F = _g(E, E, E, "###", "#.#", "#.#", "###")
KAF = _g("#####", "....#", "....#", "..###", "....#", "....#", "#####")

NON_JOINING = set("اأإآدذرزو")   # never connect to the following letter

def glyph(ch, form):
    """form: I isolated, N initial, M medial, F final."""
    joined_next = form in "NM"
    if ch in "اأإآ": return ALEF
    if ch == "ل": return ALEF if joined_next else LAM_F
    if ch in "بتثنيى":
        above = {"ت": "o.o", "ن": ".o.", "ث": "ooo"}.get(ch, "")
        below = {"ب": ".o.", "ي": "o.o"}.get(ch, "")
        if joined_next: return tooth(form, above, below)
        ins = {"ت": ".o.o", "ن": ".o..", "ث": ".ooo"}.get(ch, "")
        return bowl(ins, "..o.." if ch == "ب" else "")
    if ch == "س": return SEEN
    if ch == "ش": return SHEEN
    if ch == "ص": return SAD
    if ch in "حجخ":
        dot = "o" if ch == "ج" else ""
        g = HAH_N(dot) if form == "N" else HAH_M(dot)
        if ch == "خ": g = g[:]; g[0] = ".o".ljust(len(g[0]), ".")
        return g
    if ch == "م": return MEEM
    if ch == "و": return WAW
    if ch in "رز": return REH
    if ch in "دذ": return DAL
    if ch == "ه": return HEH_M if joined_next else HEH_F
    if ch == "ك": return KAF
    if ch in "فق":
        dots = ".o." if ch == "ف" else "o.o"
        if joined_next: return head(form, dots)
        return head_final("..." + dots, isolated=(form == "I"))
    raise KeyError(ch)

def forms(word):
    """Arabic joining: returns [(letter, form, joins_next)]."""
    out = []
    letters = [c for c in word if c != "_"]
    for i, c in enumerate(letters):
        prev_joins = i > 0 and letters[i - 1] not in NON_JOINING
        next_exists = i < len(letters) - 1
        joins_next = next_exists and c not in NON_JOINING
        form = {(False, False): "I", (False, True): "N", (True, True): "M", (True, False): "F"}[(prev_joins, joins_next)]
        out.append((c, form, joins_next))
    return out

def to_arr(g):
    return np.array([[{"#": 1, "o": 2}.get(ch, 0) for ch in row] for row in g], dtype=np.int8)

class Line:
    """One line of text, built right-to-left and justified with kashida.
    In the word string '_' after a letter marks a preferred kashida slot."""
    def __init__(self, text, word_gap=2):
        self.items = []   # visual right-to-left sequence: ('g', arr) | ('c', min, pref) | ('s', min)
        words = text.split()
        for wi, w in enumerate(words):
            prefs, k = set(), 0
            for c in w:
                if c == "_": prefs.add(k - 1)
                else: k += 1
            fs = forms(w)
            for i, (c, f, jn) in enumerate(fs):
                self.items.append(["g", to_arr(glyph(c, f))])
                if i < len(fs) - 1:
                    self.items.append(["c", 1, i in prefs] if jn else ["s", 1, False])
            if wi < len(words) - 1:
                self.items.append(["w", word_gap, False])

    def natural(self):
        return sum(it[1].shape[1] if it[0] == "g" else it[1] for it in self.items)

    def render(self, width=None, height=7, dist=None, shift=0):
        """stretch: dict item-kind -> weight; default kashida on preferred slots, then all."""
        nat = self.natural()
        width = width or nat
        extra = width - nat
        assert extra >= 0, f"line needs {nat} columns, got {width}"
        slots = [i for i, it in enumerate(self.items) if it[0] == "c" and it[2]]
        if not slots: slots = [i for i, it in enumerate(self.items) if it[0] == "c"]
        if not slots: slots = [i for i, it in enumerate(self.items) if it[0] in "ws"]
        if extra and not slots:
            raise ValueError("nothing to stretch")
        items = [list(it) for it in self.items]
        if dist is None:
            for n in range(extra - shift):
                items[slots[n % len(slots)]][1] += 1
        else:
            for i, n in dist.items(): items[i][1] += n
        grid = np.zeros((ROWS, width), dtype=np.int8)
        x = width - shift  # right edge
        for it in items:
            if it[0] == "g":
                a = it[1]; w = a.shape[1]
                grid[:, x - w:x] = np.maximum(grid[:, x - w:x], a)
                x -= w
            else:
                if it[0] == "c": grid[BASE, x - it[1]:x] = 1
                x -= it[1]
        return stretch_rows(grid, height)

def stretch_rows(grid, height):
    extra = height - 7
    if extra > 0:
        grid = np.vstack([grid[:1]] + [grid[1:2]] * (extra + 1) + [grid[2:]])
    return grid

def trim_rows(grid):
    """Drop empty descender rows at the bottom."""
    while grid.shape[0] > 1 and not grid[-1].any():
        grid = grid[:-1]
    return grid

def stack(lines, gap=1, align="justify"):
    w = max(l.shape[1] for l in lines)
    out = []
    for i, l in enumerate(lines):
        if l.shape[1] < w:
            pad = w - l.shape[1]
            l = np.hstack([np.zeros((l.shape[0], pad), np.int8), l])  # RTL: flush right
        out.append(l)
        if i < len(lines) - 1:
            out.append(np.zeros((gap, w), np.int8))
    return np.vstack(out)

def pad(grid, n):
    return np.pad(grid, n)

def frame(grid, gap=1, thick=1, value=1):
    g = np.pad(grid, gap)
    h, w = g.shape
    out = np.full((h + 2 * thick, w + 2 * thick), value, np.int8)
    out[thick:thick + h, thick:thick + w] = g
    return out

def rotate_pinwheel(strip, side):
    """Place a text strip along the bottom edge (letters standing on the edge, pointing
    inward) and repeat it four times by 90° rotation."""
    h, w = strip.shape
    g = np.zeros((side, side), np.int8)
    g[side - h:, :w] = strip
    acc = g.copy()
    r = g
    for _ in range(3):
        r = np.rot90(r, -1)
        acc = np.maximum(acc, r)
    return acc

def svg(grid, unit, colors, bg, margin=0, title="", extra=""):
    """colors: {cell value: hex}. Draws each color as one path of merged horizontal runs."""
    h, w = grid.shape
    W, H = (w + 2 * margin) * unit, (h + 2 * margin) * unit
    paths = {}
    for y in range(h):
        x = 0
        while x < w:
            v = grid[y, x]
            if v == 0: x += 1; continue
            x0 = x
            while x < w and grid[y, x] == v: x += 1
            paths.setdefault(v, []).append(
                f"M{(x0 + margin) * unit} {(y + margin) * unit}h{(x - x0) * unit}v{unit}h{-(x - x0) * unit}z")
    body = "".join(f'<path fill="{colors[v]}" d="{"".join(d)}"/>' for v, d in sorted(paths.items()))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'shape-rendering="crispEdges"><title>{title}</title>'
            f'<rect width="{W}" height="{H}" fill="{bg}"/>{extra}{body}</svg>')

def ascii(grid):
    return "\n".join("".join(" #o3456789"[v] for v in row) for row in grid)


def variants(line, width, height=7, n=150, seed=0):
    """Different kashida distributions (and small shifts) of one line, same width."""
    import random
    rnd = random.Random(seed)
    nat = line.natural(); extra = width - nat
    stretchable = [i for i, it in enumerate(line.items) if it[0] in "cws"]
    weights = [6 if line.items[i][0] == "c" and line.items[i][2] else
               3 if line.items[i][0] == "c" else 1 for i in stretchable]
    out = [trim_rows(line.render(width, height))]
    for _ in range(n):
        shift = rnd.randint(0, min(extra, 2)) if extra else 0
        dist = {}
        for _ in range(extra - shift):
            i = rnd.choices(stretchable, weights)[0]
            dist[i] = dist.get(i, 0) + 1
        g = np.zeros((ROWS, width), np.int8)
        g[:, :] = 0
        r = line.render(width, height, dist=dist, shift=0)
        if shift:
            r = np.hstack([r[:, shift:], np.zeros((r.shape[0], shift), np.int8)])
            if r[:, -shift:].any(): continue
        out.append(trim_rows(r))
    return out


def _dilate(m):
    d = m.copy()
    d[1:] |= m[:-1]; d[:-1] |= m[1:]
    d2 = d.copy()
    d2[:, 1:] |= d[:, :-1]; d2[:, :-1] |= d[:, 1:]
    return d2


def interlock(cands_per_line, gap=1, max_rise=3):
    """Stack lines, sliding each one up into the empty space of the one above it
    (keeping a one-cell gap everywhere, corners included). For each line the kashida
    variant that nests deepest is chosen."""
    first = cands_per_line[0][0]
    canvas = first.copy()
    for cands in cands_per_line[1:]:
        best = None
        for c in cands:
            H = canvas.shape[0]
            occ = _dilate(canvas > 0)
            # lowest allowed top position for c
            top = H + gap
            while top - 1 >= max(0, H + gap - max_rise):
                t = top - 1
                ov_h = min(H - t, c.shape[0])
                if ov_h > 0 and (occ[t:t + ov_h] & (c[:ov_h] > 0)).any():
                    break
                top = t
            total = max(H, top + c.shape[0])
            if best is None or total < best[0]:
                best = (total, top, c)
        total, top, c = best
        new = np.zeros((total, canvas.shape[1]), np.int8)
        new[:canvas.shape[0]] = canvas
        new[top:top + c.shape[0]] = np.maximum(new[top:top + c.shape[0]], c)
        canvas = new
    return canvas
