"""
Sample 05 · رمضان كريم · "Vermilion Texture"
Client direction (after studying the red reference):
  * every word in the same font and the SAME size
  * words in different directions (straight, rising and falling diagonals) but each
    word whole and readable, never crossed by another word
  * the gaps are filled with harakat: fatha, damma, kasra, sukun, shadda
  * one compact rectangular block
A1 portrait by default, 3 mm bleed, 8 % safe margin.
"""
import os
import random
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
MARK_GAP_MM = 3.0   # breathing room around each haraka

PHRASES = [
    "رمضان كريم",
    "أهلاً رمضان",
    "شهر الخير",
    "رمضان مبارك",
    "هلّ هلالُك",
    "كل عام وأنتم بخير",
    "صومًا مقبولًا",
    "تقبّل الله منّا ومنكم",
    "رمضان يجمعنا",
    "اللهم بلّغنا رمضان",
    "شهر القرآن",
    "اللهم تقبّل صيامنا وقيامنا",
]
# Extra single Ramadan words (complete meanings) that fill open pockets, same size
EXTRA_WORDS = ["نور", "خير", "بركة", "رحمة", "صيام", "قيام", "هلال", "مغفرة", "سحور",
               "إفطار", "تراويح", "فانوس", "دعاء", "سكينة", "صدقة", "إيمان", "ذكر", "فرحة"]
# fatha, damma, kasra, sukun, shadda
MARKS = ["َ", "ُ", "ِ", "ْ", "ّ"]

# directions: straight, rising and falling diagonals, a few steep ones
WORD_ROTS = (0, -14, 14, -26, 26, -38, 38)
ROT_PENALTY = {0: 0, -14: 2, 14: 2, -26: 4, 26: 4, -38: 8, 38: 8}

MAX_MARKS = 230
SEED = int(os.environ.get("SEED", "21"))


def place_words(bw, bh, em, n_cycles=3):
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
        last = -1e9
        starts = set(ends_[:-1]) | {0}
        for i in range(count):
            w = Word(words[i][0], 1.0, rotations=WORD_ROTS)
            # inside a phrase the next word must follow the previous one; a new phrase
            # may start in an earlier gap nearby, so holes get filled
            slack = 150 if i in starts else 12
            p = pk.try_place(w, em, min_score=last - slack)
            if p is None:
                return pk, i
            last = p.score
        return pk, count

    pk, placed = run(len(words))
    complete = max([e for e in ends if e <= placed] or [0])
    if complete != placed:
        pk, _ = run(complete)
    return pk, complete


def make(size_name="A1", preview_only=False):
    PW, PH = SIZES_MM[size_name]
    margin = 0.08 * min(PW, PH)
    bw, bh = PW - 2 * margin, PH - 2 * margin

    # choose the one word size that fills the block best with complete phrases
    best = None
    for k in range(4):
        em = bw * (0.135 + 0.006 * k)
        pk, n = place_words(bw, bh, em)
        reach = pk.lowest_ink_mm() / bh
        score = pk.coverage() - (0.2 if reach < 0.9 else 0)
        print(f"  em={em:.1f}mm words={n} coverage={pk.coverage():.2f} reach={reach:.2f}")
        if best is None or score > best[0]:
            best = (score, em)
    em = best[1]
    pk, n = place_words(bw, bh, em)
    words_placed = [p for p in pk.placed]
    print(f"final em={em:.1f}mm words={n} coverage={pk.coverage():.2f}")

    # extra words, same size and directions, dropped into the open pockets
    rng_w = random.Random(SEED + 1)
    pool = EXTRA_WORDS[:]
    rng_w.shuffle(pool)
    extra = 0
    for t in pool + pool:
        if pk.try_place(Word(t, 1.0, rotations=WORD_ROTS, filler=True), em) is not None:
            extra += 1
    print(f"extra words placed={extra} coverage={pk.coverage():.2f}")
    words_placed = list(pk.placed)

    # harakat fill the gaps between words, inside the rectangular block only
    pk.gap = max(1, int(round(MARK_GAP_MM * RES)))
    rng = random.Random(SEED)
    misses = 0
    for _ in range(MAX_MARKS):
        size = rng.choice((0.44, 0.5, 0.56))
        mark = Word(rng.choice(MARKS), size, rotations=(0, -20, 20, -40), filler=True)
        if pk.try_place(mark, em * size) is None:
            misses += 1
            if misses > 200:
                break
    marks = pk.placed[len(words_placed):]
    print(f"harakat placed={len(marks)} final coverage={pk.coverage():.2f}")

    bleed = 3.0
    W, H = PW + 2 * bleed, PH + 2 * bleed
    o = bleed + margin
    stroke = STROKE * font.upem
    paths = [f'<path d="{p.d}" transform="translate({o:.3f} {o:.3f}) {p.transform}"/>'
             for p in pk.placed]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" '
           f'viewBox="0 0 {W} {H}">\n<title>Ramadan Kareem · Vermilion Texture</title>\n'
           f'<rect width="{W}" height="{H}" fill="{PAPER}"/>\n'
           f'<g fill="{INK}" stroke="{INK}" stroke-width="{stroke}" stroke-linejoin="round">\n'
           + "\n".join(paths) + "\n</g>\n</svg>\n")

    out_dir = os.path.join(ROOT, "output", "05-ramadan-kareem-texture")
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.join(out_dir, f"ramadan-kareem_vermilion-texture_{size_name}")
    if preview_only:
        import cairosvg
        cairosvg.svg2png(bytestring=svg.encode(), write_to=stem + "_draft.png", output_width=1100)
        print("draft", stem + "_draft.png")
    else:
        print("png px:", export(svg, stem, (PW, PH)))
    return stem


if __name__ == "__main__":
    make(os.environ.get("SIZE", "A1"), bool(os.environ.get("PREVIEW_ONLY")))
