"""
Sample 03 · رمضان كريم · "Vermilion Block, Justified"
Client revision of sample 02:
  * words must not cross each other, so every word stays readable
  * every word is set at the same size
  * fewer gaps and a clean rectangular frame (justified lines, straight edges)
Style is unchanged: flat vermilion on cream, flowing pen-contrast script, horizontal
lines mixed with vertical words, small decorative harakat in the counters.
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
from rows import RowComposer  # noqa: E402

FONT_DIR = os.environ.get("FONT_DIR", os.path.join(ROOT, "fonts"))
font = Font(os.path.join(FONT_DIR, "Gulzar-Regular.ttf"))

INK = "#BF1219"
PAPER = "#FBF4E7"
STROKE = 0.01
RES = 2.0          # px per mm for collision tests
GAP_MM = 2.5       # clear space kept around every word

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
# Complete one-word meanings used only to finish the last line cleanly.
TAIL_WORDS = ["نور", "خير", "بركة", "رحمة", "سكينة", "مغفرة", "هلال", "دعاء"]
MARKS = ["َ", "ُ", "ِ", "ّ", "ْ"]


# Short phrases that may be set vertically (whole phrase, same size as every word).
VERTICAL_OK = {"كل عام وأنتم بخير", "تقبّل الله منّا ومنكم", "اللهم بلّغنا رمضان",
               "اللهم تقبّل صيامنا وقيامنا"}
VERTICAL_EVERY = int(os.environ.get("VERTICAL_EVERY", "0"))  # 0 = no rotated phrases (most readable in this script)


def fitting(rc, bands):
    keep = []
    for band in bands:
        if max(it.y + it.g.m.shape[0] for it in band) > rc.H:
            break
        keep.append(band)
    return keep


def layout(bw, bh, em, cycles=4):
    rc = RowComposer(font, (bw, bh), em, res=RES, gap_mm=GAP_MM, stroke_frac=STROKE)
    ok = lambda ph: ph in VERTICAL_OK
    phrases = PHRASES * cycles
    placed, _ = rc.stack(rc.compose(phrases, ok, VERTICAL_EVERY))
    keep = fitting(rc, placed)
    # end on complete phrases only: drop any phrase cut by the bottom edge, then let
    # complete single words finish the last line
    counts = {}
    for b in keep:
        for it in b:
            counts[it.pid] = counts.get(it.pid, 0) + (len(phrases[it.pid].split()) if it.g.rot else 1)
    complete = [i for i, ph in enumerate(phrases) if counts.get(i, 0) == len(ph.split())]
    phrases2 = [phrases[i] for i in complete]
    n_main = len(phrases2)
    phrases2 += TAIL_WORDS
    bands = rc.compose(phrases2, ok, VERTICAL_EVERY)
    # keep bands up to the one holding the last real phrase word (no tail-only lines)
    last = max(i for i, b in enumerate(bands) if any(it.pid < n_main for it in b))
    placed, _ = rc.stack(bands[: last + 1])
    keep = fitting(rc, placed)
    bottom = max(it.y + it.g.m.shape[0] for b in keep for it in b)
    leftover = rc.H - bottom
    n = len(keep) - 1
    for i, band in enumerate(keep):
        dy = int(round(leftover * i / n)) if n else 0
        for it in band:
            it.y += dy
    return rc, keep, leftover / rc.H


def make(size_name="A1", out_dir=None, preview_only=False, seed=5):
    PW, PH = SIZES_MM[size_name]
    margin = 0.08 * min(PW, PH)
    bw, bh = PW - 2 * margin, PH - 2 * margin

    # choose the word size that leaves the least spare height (= tightest block)
    best = None
    for k in range(12):
        em = bw * (0.085 + 0.003 * k)
        rc, bands, spare = layout(bw, bh, em)
        nv = sum(1 for b in bands for it in b if it.g.rot)
        score = spare + (0.05 if VERTICAL_EVERY and nv < 2 else 0)
        print(f"  em={em:.1f}mm bands={len(bands)} verticals={nv} spare={spare:.3f}")
        if best is None or score < best[0]:
            best = (score, em)
    em = best[1]
    rc, bands, spare = layout(bw, bh, em)
    items = [it for b in bands for it in b]
    words = [it.g.text + ("↕" if it.g.rot else "") for it in items]
    print(f"final em={em:.1f}mm spare={spare:.3f} words={len(words)}")

    # decorative harakat in the larger holes, all the same small size
    pk = Packer(font, (bw, bh), res=RES, gap_mm=3.0, overlap=0.0, stroke_frac=STROKE, seed=seed)
    pk.occ = rc.stamp(items, rc.H, rc.W)
    rng = random.Random(seed)
    for _ in range(70):
        pk.try_place(Word(rng.choice(MARKS), 0.38, rotations=(0, 12, -12), filler=True),
                     em * 0.38)

    bleed = 3.0
    W, H = PW + 2 * bleed, PH + 2 * bleed
    o = bleed + margin
    stroke = STROKE * font.upem
    paths = []
    for it in items:
        g = it.g
        X = (it.x + g.ox) / RES
        Y = (it.y + g.oy) / RES
        paths.append(f'<path d="{rc.path(g)}" transform="translate({o + X:.3f} {o + Y:.3f}) '
                     f'rotate({g.rot}) scale({g.s:.6f}) translate({-g.cx:.1f} {-g.cy:.1f})"/>')
    for p in pk.placed:
        paths.append(f'<path d="{p.d}" transform="translate({o:.3f} {o:.3f}) {p.transform}"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" '
           f'viewBox="0 0 {W} {H}">\n<title>Ramadan Kareem · Vermilion Block</title>\n'
           f'<rect width="{W}" height="{H}" fill="{PAPER}"/>\n'
           f'<g fill="{INK}" stroke="{INK}" stroke-width="{stroke}" stroke-linejoin="round">\n'
           + "\n".join(paths) + "\n</g>\n</svg>\n")

    out_dir = out_dir or os.path.join(ROOT, "output", "03-ramadan-kareem-justified")
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.join(out_dir, f"ramadan-kareem_vermilion-justified_{size_name}")
    if preview_only:
        import cairosvg
        cairosvg.svg2png(bytestring=svg.encode(), write_to=stem + "_draft.png", output_width=1100)
        print("draft", stem + "_draft.png")
    else:
        print("png px:", export(svg, stem, (PW, PH)))
    print(" ".join(words))
    return stem


if __name__ == "__main__":
    make(os.environ.get("SIZE", "A1"), os.environ.get("OUT"), bool(os.environ.get("PREVIEW_ONLY")))
