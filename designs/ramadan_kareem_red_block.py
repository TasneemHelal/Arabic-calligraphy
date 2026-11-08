"""
Sample 02 · رمضان كريم · "Vermilion Block"
Style matched to the client's reference: a dense, interlocking free-hand word block,
flat vermilion ink on warm cream, words flowing in reading order with mixed
horizontal, diagonal and vertical directions, and small decorative marks
(harakat) filling the counters.
A1 portrait by default (594 × 841 mm), 3 mm bleed, 8 % safe margin.
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

from calligraphy import Font, SIZES_MM, export  # noqa: E402
from pack import Word, compose  # noqa: E402

FONT_DIR = os.environ.get("FONT_DIR", os.path.join(ROOT, "fonts"))
font = Font(os.path.join(FONT_DIR, "Gulzar-Regular.ttf"))

INK = "#BF1219"        # vermilion-crimson (measured from the reference)
PAPER = "#FBF4E7"      # warm cream

# Phrases, in reading order. The theme phrase opens the block, larger.
PHRASES = [
    ("رمضان كريم", 1.3),
    ("أهلاً رمضان", 1.0),
    ("شهر الخير", 1.0),
    ("رمضان مبارك", 1.0),
    ("هلّ هلالُك", 1.0),
    ("كل عام وأنتم بخير", 1.0),
    ("صومًا مقبولًا", 1.0),
    ("تقبّل الله منّا ومنكم", 1.0),
    ("رمضان يجمعنا", 1.0),
    ("اللهم بلّغنا رمضان", 1.0),
    ("شهر القرآن", 1.0),
    ("اللهم تقبّل صيامنا وقيامنا", 1.0),
    ("رمضان كريم", 1.0),
]
# Small meaningful Ramadan words used to fill remaining space (never letter soup).
FILLER_WORDS = ["نور", "خير", "بركة", "رحمة", "صيام", "قيام", "هلال", "مغفرة",
                "سحور", "إفطار", "تراويح", "فانوس", "دعاء", "سكينة"]
MARKS = ["َ", "ُ", "ِ", "ّ", "ْ"]  # fatha damma kasra shadda sukun

STROKE = 0.01  # slight emboldening, as a fraction of the em
SEED = int(os.environ.get("SEED", "11"))
rng = random.Random(SEED)

# Mostly horizontal, with diagonals and verticals mixed in (client: verticals + horizontals)
ROTS = (0, 0, 10, -10, 22, -90)


def build_words():
    words = []
    for i, (ph, size) in enumerate(PHRASES):
        for w in ph.split():
            jitter = 1.0 if size > 1 else rng.uniform(0.88, 1.15)
            rots = (0, 10, -10) if size > 1 else ROTS
            words.append(Word(w, size * jitter, rotations=rots, phrase=i))
    fillers = []
    medium = FILLER_WORDS[:]
    rng.shuffle(medium)
    fillers += [Word(t, rng.uniform(0.6, 0.75), rotations=ROTS, filler=True) for t in medium]
    for _ in range(2):
        pool = FILLER_WORDS[:]
        rng.shuffle(pool)
        fillers += [Word(t, rng.uniform(0.38, 0.5), rotations=ROTS, filler=True) for t in pool]
    fillers += [Word(rng.choice(MARKS), rng.uniform(0.35, 0.5),
                     rotations=(0, 15, -15), filler=True) for _ in range(140)]
    return words, fillers


def make(size_name="A1", out_dir=None, preview_only=False):
    PW, PH = SIZES_MM[size_name]
    margin = 0.08 * min(PW, PH)
    bw, bh = PW - 2 * margin, PH - 2 * margin
    words, fillers = build_words()

    # scan base sizes: keep the largest one where every phrase word fits and the
    # phrases alone reach close to the bottom of the block (fillers do the rest)
    best = None
    for k in range(14):
        em = bw * (0.14 + 0.006 * k)
        pk, failed = compose(font, (bw, bh), words, [], em_mm=em, seed=SEED, stroke_frac=STROKE)
        reach = pk.lowest_ink_mm() / bh
        print(f"  em={em:.1f}mm failed={len(failed)} reach={reach:.2f}")
        if not failed and reach >= 0.95:
            best = (em, reach)     # smallest size that fills the block: nothing squeezed
            break
    em = best[0]
    pk, failed = compose(font, (bw, bh), words, fillers, em_mm=em, seed=SEED, stroke_frac=STROKE)
    assert not failed, failed
    print(f"final em={em:.1f}mm coverage={pk.coverage():.2f}")

    bleed = 3.0
    W, H = PW + 2 * bleed, PH + 2 * bleed
    ox = bleed + margin
    stroke = STROKE * font.upem
    paths = []
    for p in pk.placed:
        paths.append(f'<path d="{p.d}" transform="translate({ox:.3f} {ox:.3f}) {p.transform}"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" '
           f'viewBox="0 0 {W} {H}">\n<title>Ramadan Kareem · Vermilion Block</title>\n'
           f'<rect width="{W}" height="{H}" fill="{PAPER}"/>\n'
           f'<g fill="{INK}" stroke="{INK}" stroke-width="{stroke}" stroke-linejoin="round">\n'
           + "\n".join(paths) + "\n</g>\n</svg>\n")

    out_dir = out_dir or os.path.join(ROOT, "output", "02-ramadan-kareem-red-block")
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.join(out_dir, f"ramadan-kareem_vermilion-block_{size_name}")
    if preview_only:
        cairosvg_preview(svg, stem + "_draft.png")
    else:
        print("png px:", export(svg, stem, (PW, PH)))
    return stem, pk


def cairosvg_preview(svg, path):
    import cairosvg
    cairosvg.svg2png(bytestring=svg.encode(), write_to=path, output_width=1100)
    print("draft", path)


if __name__ == "__main__":
    make(os.environ.get("SIZE", "A1"), os.environ.get("OUT"),
         bool(os.environ.get("PREVIEW_ONLY")))
