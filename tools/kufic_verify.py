"""Builds a line of real letters on the grid and verifies the result letter by letter."""
import numpy as np
from foks import forms, glyph, NON_JOINING, PIECES

def build_line(word_specs, baseline, tall_h, right_edge, word_gap=2):
    """word_specs: list of (word, {letter_index: extra kashida after that letter}).
    Returns a list of letters: dict(ch, form, ink=set, dots=set) placed right→left."""
    letters = []
    x = right_edge + 1
    for wi, (word, kash) in enumerate(word_specs):
        fs = forms(word)
        for i, (ch, f) in enumerate(fs):
            g = glyph(ch, f, tall_h)
            w = len(g["rows"][0])
            x0 = x - w
            ink, dots, conn = set(), set(), set()
            for r, row in enumerate(g["rows"]):
                for c, v in enumerate(row):
                    cell = (baseline - g["base"] + r, x0 + c)
                    if v == "#": ink.add(cell)
                    elif v == "o": dots.add(cell)
            x = x0
            if i < len(fs) - 1:
                n = 1 + kash.get(i, 0)
                if ch not in NON_JOINING:          # connector on the baseline
                    for k in range(n): conn.add((baseline, x - 1 - k))
                    ink |= conn
                x -= n
            letters.append(dict(ch=ch, form=f, ink=ink, dots=dots, conn=conn))
        if wi < len(word_specs) - 1:
            x -= word_gap
    return letters, x

def _components(cells):
    cells = set(cells); seen = {}; n = 0
    for s in cells:
        if s in seen: continue
        n += 1; st = [s]; seen[s] = n
        while st:
            r, c = st.pop()
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (r + d[0], c + d[1])
                if q in cells and q not in seen: seen[q] = n; st.append(q)
    return seen

DOTS = {"ب": 1, "ت": 2, "ث": 3, "ن": 1, "ي": 2, "ج": 1, "خ": 1, "ذ": 1, "ز": 1, "ش": 3,
        "ض": 1, "ظ": 1, "غ": 1, "ف": 1, "ق": 2}

def verify(letters, phrase):
    errs = []
    seq = "".join(l["ch"] for l in letters)
    if seq != phrase.replace(" ", ""):
        errs.append(f"sequence {seq!r} != {phrase!r}")
    owner = {}
    for i, l in enumerate(letters):
        for cell in l["ink"] | l["dots"]:
            if cell in owner: errs.append(f"{l['ch']}#{i} overlaps {letters[owner[cell]]['ch']} at {cell}")
            owner[cell] = i
        if len(l["dots"]) != DOTS.get(l["ch"], 0):
            errs.append(f"{l['ch']}#{i} has {len(l['dots'])} dots, needs {DOTS.get(l['ch'], 0)}")
    ink = {c for l in letters for c in l["ink"]}
    conns = {c for l in letters for c in l["conn"]}
    comp = _components(ink)
    # expected join groups from the words themselves
    expected, cur = [], []
    words = phrase.split()
    for w in words:
        for i, ch in enumerate(w):
            cur.append(ch)
            if ch in NON_JOINING or i == len(w) - 1:
                expected.append(cur); cur = []
    got, idx = [], {}
    for i, l in enumerate(letters):
        ids = {comp[c] for c in l["ink"]}
        if len(ids) != PIECES.get(l["ch"], 1):
            errs.append(f"{l['ch']}#{i} is in {len(ids)} pieces, needs {PIECES.get(l['ch'], 1)}")
        # the joining piece is the one that holds the letter's baseline cells
        base_ids = {comp[c] for c in l["ink"] if c[0] == max(r for r, _ in l["ink"] if (r, _) not in l["dots"])} or ids
        k = min(base_ids)
        if k not in idx: idx[k] = len(got); got.append([])
        got[idx[k]].append(l["ch"])
    if got != expected: errs.append(f"joins {got} != expected {expected}")
    # dots: no contact with ink (8-neighbourhood), and the nearest ink must be their own letter
    for i, l in enumerate(letters):
        for (r, c) in l["dots"]:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if (r + dr, c + dc) in ink: errs.append(f"dot of {l['ch']}#{i} touches ink at {(r, c)}")
            # nearest letter body (shared baseline connectors excluded), Euclidean
            body = [(a, b) for a, b in ink if (a, b) not in conns]
            best = min((r - a) ** 2 + (c - b) ** 2 for a, b in body)
            near = {owner[(a, b)] for a, b in body if (r - a) ** 2 + (c - b) ** 2 == best}
            if near != {i}:
                errs.append(f"dot of {l['ch']}#{i} at {(r, c)} is as close to "
                            f"{[letters[j]['ch'] for j in near if j != i]}")
    # separate letter groups must not touch, even at corners
    for a in ink:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                b = (a[0] + dr, a[1] + dc)
                same_letter = owner.get(a) == owner.get(b)
                if b in ink and comp[a] != comp[b] and not same_letter:
                    errs.append(f"unjoined shapes touch at {a}/{b}")
    return errs
