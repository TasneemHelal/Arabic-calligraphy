"""
Square Kufic 03b · سبحان الله, three compositions.
Every instance of the phrase is first built flat and passes tools/kufic_verify.verify().
Only then is it rotated or repeated, and the composite gets extra checks: copies never
touch, and every dot is still nearest to its own letter.
"""
import os, sys, copy
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from kufic_verify import build_line, verify  # noqa: E402
from kufic_render import export_all  # noqa: E402

PHRASE = "سبحان الله"
OUT = os.path.join(ROOT, "output", "13-kufic-subhanallah-variations")


def normalise(letters):
    r0 = min(r for l in letters for r, c in l["ink"] | l["dots"])
    c0 = min(c for l in letters for r, c in l["ink"] | l["dots"])
    for l in letters:
        for k in ("ink", "dots", "conn"):
            l[k] = {(r - r0, c - c0) for r, c in l[k]}
    return letters


def size(letters):
    return (1 + max(c for l in letters for r, c in l["ink"] | l["dots"]),
            1 + max(r for l in letters for r, c in l["ink"] | l["dots"]))


def phrase_line(kash1, kash2, tall, word_gap=2, right_edge=200, baseline=None):
    L, _ = build_line([("سبحان", kash1), ("الله", kash2)], baseline=baseline or tall - 1,
                      tall_h=tall, right_edge=right_edge, word_gap=word_gap)
    errs = verify(L, PHRASE)
    if errs: raise SystemExit("REJECTED instance:\n  " + "\n  ".join(errs))
    return L


def transform(letters, f):
    out = copy.deepcopy(letters)
    for l in out:
        for k in ("ink", "dots", "conn"):
            l[k] = {f(r, c) for r, c in l[k]}
    return out


def check_composite(instances):
    """instances: list of letter lists. Copies must not touch (8-neighbourhood) and each
    dot's nearest letter body must be its own letter."""
    errs = []
    owner = {}
    for i, inst in enumerate(instances):
        for j, l in enumerate(inst):
            for c in l["ink"] | l["dots"]:
                if c in owner: errs.append(f"overlap at {c}")
                owner[c] = (i, j)
    ink = {c: owner[c] for inst in instances for l in inst for c in l["ink"]}
    conn = {c for inst in instances for l in inst for c in l["conn"]}
    for (r, c), (i, j) in ink.items():
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                o = ink.get((r + dr, c + dc))
                if o and o[0] != i: errs.append(f"copies {i} and {o[0]} touch at {(r, c)}")
    body = [(c, o) for c, o in ink.items() if c not in conn]
    for i, inst in enumerate(instances):
        for j, l in enumerate(inst):
            if l.get("ornament"): continue
            for (r, c) in l["dots"]:
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if (r + dr, c + dc) in ink: errs.append(f"dot of {l['ch']} in copy {i} touches ink")
                # clearance from other copies: at least 2 empty cells in every direction
                for (a, b), o in ink.items():
                    if o[0] != i and max(abs(a - r), abs(b - c)) <= 2:
                        errs.append(f"dot of {l['ch']} in copy {i} within 2 cells of copy {o[0]}")
                d = min((r - a) ** 2 + (c - b) ** 2 for (a, b), _ in body)
                near = {o for (a, b), o in body if (r - a) ** 2 + (c - b) ** 2 == d}
                if near != {(i, j)}: errs.append(f"dot of {l['ch']} in copy {i} is as close to another letter")
    return errs


def export(name, instances, style):
    errs = check_composite(instances)
    if errs: raise SystemExit(f"REJECTED {name}:\n  " + "\n  ".join(sorted(set(errs))[:20]))
    letters = [l for inst in instances for l in inst]
    W, H = size(letters)
    export_all(letters, W, H, PHRASE, name, OUT, **style)
    print(f"{name}: {len(instances)} verified copies, {W}x{H}, composite checks passed")


# ── A · «Tasbih» — the phrase three times, kashida shifted so the uprights step across ──
def tasbih_block():
    W = 39
    specs = [({2: 6}, {}), ({2: 2}, {1: 2, 2: 2}), ({0: 2, 2: 1}, {2: 3})]
    tones = ["#1F3D2E", "#6E3B1E", "#1F3D2E"]
    inst, top = [], 0
    for (k1, k2), tone in zip(specs, tones):
        L = phrase_line(k1, k2, tall=9, word_gap=2)
        L = normalise(L)
        w, h = size(L)
        pad = W - w
        assert pad >= 0, w
        # absorb any leftover width in the word gap so every line is justified
        if pad:
            L = phrase_line(k1, k2, tall=9, word_gap=2 + pad); L = normalise(L)
        for l in L: l["color"] = tone
        L = transform(L, lambda r, c, t=top: (r + t, c))
        inst.append(L)
        top = 1 + max(r for l in L for r, c in l["ink"] | l["dots"]) + 1
    export("A-tasbih-block", inst,
           dict(ink="#1F3D2E", dot="#B8892F", paper="#F4EEDF", U=40, gap=2, border=1, mat=3))


# ── B · Pinwheel — the phrase stands on each edge and turns four times around the centre ──
TALL_B = 13


def pinwheel():
    base = normalise(phrase_line({}, {}, tall=TALL_B))
    w, h = size(base)
    S = w + h + 3          # 3-cell channel between bands keeps every dot clear of the next copy
    # top edge, upright; baselines face the centre and uprights rise toward the frame
    strip = transform(base, lambda r, c: (r, c + S - w))
    rot = lambda r, c: (c, S - 1 - r)                          # 90° clockwise
    inst = [strip]
    for _ in range(3):
        inst.append(transform(inst[-1], rot))
    # small central square: an ornament, not a letter
    m = S // 2
    centre = [dict(ch="■", form="-", ink=set(), dots={(m + a, m + b) for a in (-1, 0, 1) for b in (-1, 0, 1)}, conn=set(), ornament=True)]
    inst_all = inst + [centre]
    export("B-pinwheel", inst_all,
           dict(ink="#1C2B4A", dot="#B5652F", paper="#EFE6D6", U=30, gap=2, border=1, mat=3))


# ── C · Two tiers — سبحان above, الله below as a colonnade the full width ──
def two_tier():
    L1, _ = build_line([("سبحان", {})], baseline=6, tall_h=7, right_edge=21)
    L2, _ = build_line([("الله", {1: 6, 2: 7})], baseline=24, tall_h=13, right_edge=21)  # 3 clear rows under the dot of ب
    L = L1 + L2
    errs = verify(L, PHRASE)
    if errs: raise SystemExit("REJECTED two-tier:\n  " + "\n  ".join(errs))
    for l in L2: l["color"] = "#7A1E2B"
    export("C-two-tier", [L], dict(ink="#2A2320", dot="#B8892F", paper="#F5EFE3", U=50, gap=2, border=2, mat=3))


if __name__ == "__main__":
    tasbih_block(); pinwheel(); two_tier()
