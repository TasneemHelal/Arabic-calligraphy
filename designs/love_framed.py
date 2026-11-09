"""
Sample 07 · الحبّ · "Vermilion Love, Framed"
Topic: love. Same method as sample 06 (framed rectangle, 3 in padding, one font, one
size, varied directions, no nearby repeats), with the client's new direction:
  * individual words instead of phrases, so the words are the focus
  * stronger interlacing: thin strokes cross thin strokes; letter bodies, loops and dots
    are never covered
  * far fewer harakat: a light sprinkle of small marks only
A1 portrait by default, 3 mm bleed.
"""
import os
import random

import numpy as np
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

from calligraphy import Font, SIZES_MM, export  # noqa: E402
from pack import Packer, Word  # noqa: E402

FONT_DIR = os.environ.get("FONT_DIR", os.path.join(ROOT, "fonts"))
font = Font(os.path.join(FONT_DIR, "Gulzar-Regular.ttf"))

INK = "#BF1219"
PAPER = "#FBF4E7"
STROKE = 0.01
RES = 1.5           # px per mm for collision maps
WORD_GAP_MM = 1.6   # clear space between words (keeps every word readable)
MARK_GAP_MM = 1.8   # clearance between a mark and the words around it

# 40 classical and everyday words of love (each a complete meaning on its own)
LOVE_WORDS = ["غرام", "شغف", "حب", "ودّ", "اشتياق", "لهفة", "مودّة", "ألفة", "وصال",
              "لقاء", "قلب", "روح", "أمان", "دفء", "سكن", "غزل"]   # client's selection
_order = LOVE_WORDS[:]
random.Random(7).shuffle(_order)
PHRASES = _order                 # every word is its own unit
EXTRA_WORDS = LOVE_WORDS[:]      # second pass fills pockets (never near its twin)
# fatha, damma, kasra, sukun, shadda
MARKS = ["َ", "ُ", "ِ", "ْ", "ّ"]

# directions: straight, rising and falling diagonals, a few steep ones
WORD_ROTS = (0, -14, 14, -26, 26, -38, 38)
ROT_PENALTY = {0: 0, -14: 2, 14: 2, -26: 4, 26: 4, -38: 8, 38: 8}

MAX_MARKS = 700
NEAR_MM = 24.0         # marks only in gaps within this distance of a word
MARK_SPACING_MM = 5.5  # minimum distance between two marks (no clusters)
EXTRA_REPEAT_DIST_EM = 1.0
POCKET_REPEAT_DIST_EM = 0.55
POCKET_MIN_MM = 5.0   # a pocket = point at least this far from any ink
CORE_MM = float(os.environ.get("CORE_MM", "1.6"))        # thicker strokes = protected letter bodies
CROSS_TOL = float(os.environ.get("CROSS_TOL", "0.07"))   # share of a word's ink allowed to cross
SAME_WORD_DIST_EM = 2.6   # two copies of a word stay at least this far apart (centres)
PADDING_IN = float(os.environ.get("PADDING_IN", "3"))   # paper edge -> content
SEED = int(os.environ.get("SEED", "34"))
# vertical ink gradient, bright red at the top to deep maroon at the bottom (reference)
GRADIENT = [("0", "#E0222B"), ("0.45", "#B5121E"), ("1", "#6A0D1A")]


def place_words(bw, bh, em, n_cycles=7):
    """Place phrase words in reading order at ONE size. Stops at the first word that
    no longer fits, then keeps only complete phrases."""
    words = []
    for _ in range(n_cycles):
        for pid, ph in enumerate(PHRASES):
            for w in ph.split():
                words.append((w, len(words), ph))
    ends, n = [], 0
    for _ in range(n_cycles):
        for ph in PHRASES:
            n += len(ph.split())
            ends.append(n)

    ends_ = [0] + ends

    def run(count):
        pk = Packer(font, (bw, bh), res=RES, gap_mm=WORD_GAP_MM, overlap=0.0,
                    stroke_frac=STROKE, seed=SEED, rot_penalty=ROT_PENALTY, flow=0.32)
        # client rules: words interlace (thin strokes cross thin strokes only, letter
        # bodies and dots never covered), and a word never repeats in the same area
        pk.enable_interlace(core_mm=CORE_MM, cross_tol=CROSS_TOL, reward=30.0)
        pk.same_word_r = SAME_WORD_DIST_EM * em * RES
        last = -1e9
        starts = set(ends_[:-1]) | {0}
        prev = None
        for i in range(count):
            w = Word(words[i][0], 1.0, rotations=WORD_ROTS)
            # inside a phrase the next word must follow the previous one; a new phrase
            # may start in an earlier gap nearby, so holes get filled
            slack = 150 if i in starts else 12
            after = None if i in starts else prev
            p = pk.try_place(w, em, min_score=last - slack, after=after)
            if p is None:
                return pk, i
            last = p.score
            g = p.geom
            prev = (g["px"] + g["m"].shape[1] / 2, g["py"] + g["m"].shape[0] / 2,
                    0.9 * em * RES)
        return pk, count

    pk, placed = run(len(words))
    complete = max([e for e in ends if e <= placed] or [0])
    if complete != placed:
        pk, _ = run(complete)
    return pk, complete


def make(size_name="A1", preview_only=False):
    PW, PH = SIZES_MM[size_name]
    margin = PADDING_IN * 25.4
    bw, bh = PW - 2 * margin, PH - 2 * margin

    # choose the one word size that fills the block best with complete phrases
    best = None
    for k in range(4):
        em = bw * (0.135 + 0.006 * k)
        pk, n = place_words(bw, bh, em)
        reach = pk.lowest_ink_mm() / bh
        score = pk.coverage() - (0.2 if reach < 0.96 else 0)
        print(f"  em={em:.1f}mm words={n} coverage={pk.coverage():.2f} reach={reach:.2f}")
        if best is None or score > best[0]:
            best = (score, em)
    em = best[1]
    pk, n = place_words(bw, bh, em)
    words_placed = [p for p in pk.placed]
    print(f"final em={em:.1f}mm words={n} coverage={pk.coverage():.2f}")

    # extra single Ramadan words (same size, same interlace + no-repeat rules) fill pockets
    rng_w = random.Random(SEED + 1)
    pool = EXTRA_WORDS[:]
    rng_w.shuffle(pool)
    extra = [t for t in pool if pk.try_place(Word(t, 1.0, rotations=WORD_ROTS), em) is not None]
    # second pass: open patches get a word, not a heap of marks (repeat distance relaxed)
    pk.same_word_r = EXTRA_REPEAT_DIST_EM * em * RES
    pk.interlace["tol"] = CROSS_TOL * 1.6
    for t in pool + pool + pool:
        if pk.try_place(Word(t, 1.0, rotations=WORD_ROTS + (-52, 52, -90)), em) is not None:
            extra.append(t)
    # final pass for narrow pockets (client-circled): short words, many more angles
    pk.same_word_r = POCKET_REPEAT_DIST_EM * em * RES
    pk.interlace["tol"] = CROSS_TOL * 2.5
    # a pocket word is kept only if its centre lands in a real empty pocket
    from scipy.ndimage import distance_transform_edt
    import copy
    hole = distance_transform_edt(~pk.occ) / RES > POCKET_MIN_MM
    short = sorted(LOVE_WORDS, key=len)
    angles = tuple(range(-70, 71, 7)) + (90, -90)
    for _ in range(6):
        got = 0
        for t in short:
            snap = (pk.occ.copy(), pk.core.copy(), copy.deepcopy(pk.centers), len(pk.placed))
            p_ = pk.try_place(Word(t, 1.0, rotations=angles), em)
            if p_ is None:
                continue
            g = p_.geom
            cy, cx = int(g["py"] + g["m"].shape[0] / 2), int(g["px"] + g["m"].shape[1] / 2)
            if hole[min(cy, hole.shape[0] - 1), min(cx, hole.shape[1] - 1)]:
                extra.append(t)
                got += 1
                hole = distance_transform_edt(~pk.occ) / RES > POCKET_MIN_MM
            else:      # would only crowd an area that is already full: undo
                pk.occ, pk.core, pk.centers = snap[0], snap[1], snap[2]
                del pk.placed[snap[3]:]
        if not got:
            break
    print(f"extra words placed={len(extra)}: {' '.join(extra)}")

    # straight sides: slide edge words out to the rectangle's edges
    pk.snap_to_edges(reach_mm=em * 0.9)
    pk.rebuild_occ()
    words_placed = list(pk.placed)

    # harakat fill the SMALL gaps between words only, spread evenly (client): a mark may
    # sit only within NEAR_MM of a word's ink, and marks keep MARK_SPACING_MM apart
    from scipy.ndimage import distance_transform_edt
    words_occ = pk.occ.copy()
    dist = distance_transform_edt(~words_occ) / RES
    far = dist > NEAR_MM
    pk.gap = max(1, int(round(MARK_GAP_MM * RES)))
    rng = random.Random(SEED)
    sp = int(MARK_SPACING_MM * RES)
    yy, xx = np.ogrid[-sp:sp + 1, -sp:sp + 1]
    disk = xx ** 2 + yy ** 2 <= sp ** 2
    taken = np.zeros_like(words_occ)
    misses = 0
    for _ in range(MAX_MARKS):
        size = rng.choice((0.36, 0.42, 0.48))
        mark = Word(rng.choice(MARKS), size, rotations=(0, -20, 20, -40), filler=True)
        base = pk.occ.copy()
        pk.occ = base | far | taken          # forbidden for this mark only
        n_before = len(pk.placed)
        ok = pk.try_place(mark, em * size)
        pk.occ = base
        if ok is None:
            misses += 1
            if misses > 300:
                break
            continue
        g = ok.geom
        mh, mw = g["m"].shape
        pk.occ[g["py"]:g["py"] + mh, g["px"]:g["px"] + mw] |= g["m"]
        cy, cx = int(g["py"] + mh / 2), int(g["px"] + mw / 2)
        y0, y1 = max(0, cy - sp), min(taken.shape[0], cy + sp + 1)
        x0, x1 = max(0, cx - sp), min(taken.shape[1], cx + sp + 1)
        taken[y0:y1, x0:x1] |= disk[y0 - (cy - sp):y1 - (cy - sp), x0 - (cx - sp):x1 - (cx - sp)]
    marks = pk.placed[len(words_placed):]
    print(f"harakat placed={len(marks)} final coverage={pk.coverage():.2f}")

    bleed = 3.0
    W, H = PW + 2 * bleed, PH + 2 * bleed
    o = bleed + margin
    stroke = STROKE * font.upem
    paths = [f'<path d="{p.d}" transform="translate({o:.3f} {o:.3f}) {p.transform}"/>'
             for p in pk.placed]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" '
           f'viewBox="0 0 {W} {H}">\n<title>Love · Vermilion, Framed</title>\n'
           f'<defs><linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="0" y1="{o}" '
           f'x2="0" y2="{o + bh}">'
           + "".join(f'<stop offset="{a}" stop-color="{c}"/>' for a, c in GRADIENT)
           + '</linearGradient>'
           # the letters are a mask, so ONE gradient runs over the whole block
           f'<mask id="letters" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
           f'<g fill="#fff" stroke="#fff" stroke-width="{stroke}" stroke-linejoin="round">\n'
           + "\n".join(paths) + "\n</g></mask></defs>\n"
           f'<rect width="{W}" height="{H}" fill="{PAPER}"/>\n'
           f'<rect width="{W}" height="{H}" fill="url(#ink)" mask="url(#letters)"/>\n</svg>\n')

    out_dir = os.path.join(ROOT, "output", "07-love-framed")
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.join(out_dir, f"love_framed_{size_name}")
    if preview_only:
        import cairosvg
        cairosvg.svg2png(bytestring=svg.encode(), write_to=stem + "_draft.png", output_width=2200)
        print("draft", stem + "_draft.png")
    else:
        print("png px:", export(svg, stem, (PW, PH)))
    return stem


if __name__ == "__main__":
    make(os.environ.get("SIZE", "A1"), bool(os.environ.get("PREVIEW_ONLY")))
