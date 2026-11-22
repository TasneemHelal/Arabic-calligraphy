# Muse & Make — the paintbrush itself bends into the letters M & M (handle -> M, ferrule -> &, bristles -> M).
import math
from build import C
from brush import M1, M2, MIDS, to_d, length

LA, RB = (30, 131), (208, 109)          # brush axis: handle end (left) -> bristle tip (right)
SPLIT = [0, .5, .63, .93]                  # handle | ferrule | bristles
lerp = lambda f: (round(LA[0] + (RB[0]-LA[0])*f, 2), round(LA[1] + (RB[1]-LA[1])*f, 2))

def straight(segs, f0, f1):
    """Same commands as `segs`, but every point laid on the brush axis between f0..f1 (by arc length)."""
    lens, cur = [], None
    for c, p in segs:
        if c == "M": cur = p; continue
        lens.append(length([("M", cur), (c, p)])); cur = [p[-1]]
    tot, acc, out = sum(lens), 0, []
    for c, p in segs:
        if c == "M": out.append(("M", [lerp(f0)])); continue
        L = lens[len(out) - 1]; a = f0 + (f1-f0)*acc/tot; b = f0 + (f1-f0)*(acc+L)/tot; acc += L
        out.append((c, [lerp(a + (b-a)*k/3) for k in (1, 2, 3)] if c == "C" else [lerp(b)]))
    return out

def build(mid, anim):
    parts = [(M1, C["ink"], 10, 8), (MIDS[mid], C["coral"], 13, 7.4), (M2, C["ink"], 7, 8)]
    T_IN, T_M = .3, 1.05                                   # brush lands, morph starts
    ang = math.degrees(math.atan2(RB[1]-LA[1], RB[0]-LA[0]))
    out = []
    for i, ((segs, col, w0, w1), f0, f1) in enumerate(zip(parts, SPLIT, SPLIT[1:])):
        b = T_M + i * .08
        st, fin = to_d(straight(segs, f0, f1)), to_d(segs)
        cx = round(sum(x for _, p in segs for x, _ in p) / sum(len(p) for _, p in segs), 1)
        by = round(max(y for _, p in segs for _, y in p), 1)
        if anim:
            a = (f'<animate attributeName="d" values="{st};{fin}" begin="{b:.2f}s" dur=".5s" calcMode="spline" keySplines=".7 0 .2 1" fill="freeze"/>'
                 f'<animate attributeName="stroke-width" values="{w0};{w1}" begin="{b:.2f}s" dur=".4s" fill="freeze"/>')
            boing = f'<animateTransform attributeName="transform" type="scale" values="1 1;1.16 .84;.94 1.1;1 1" keyTimes="0;.3;.65;1" begin="{b+.5:.2f}s" dur=".4s"/>'
        else: a = boing = ""
        out.append(f'<g transform="translate({cx} {by})"><g>{boing}<g transform="translate({-cx} {-by})">'
                   f'<path d="{st if anim else fin}" fill="none" stroke="{col}" stroke-width="{w0 if anim else w1}" stroke-linecap="round" stroke-linejoin="round">{a}</path></g></g></g>')

    # brush-only details that dissolve as it bends: bristle taper, handle shine, ferrule rivets
    fade = lambda d=.18: f'<animate attributeName="opacity" to="0" begin="{T_M:.2f}s" dur="{d}s" fill="freeze"/>' if anim else ""
    bx0, bx1 = lerp(SPLIT[2]), RB
    details = f'''<g transform="rotate({ang:.2f} {bx0[0]} {bx0[1]})">
      <path d="M {bx0[0]-1} {bx0[1]-6.5} C {bx0[0]+14} {bx0[1]-11}, {bx0[0]+40} {bx0[1]-10}, {bx0[0]+78} {bx0[1]} C {bx0[0]+40} {bx0[1]+10}, {bx0[0]+14} {bx0[1]+11}, {bx0[0]-1} {bx0[1]+6.5} Z" fill="{C["ink"]}">{fade()}</path>
    </g>
    <path d="M {lerp(.06)[0]} {lerp(.06)[1]-2.2} L {lerp(.44)[0]} {lerp(.44)[1]-2.2}" stroke="{C["bg"]}" stroke-width="1.6" stroke-linecap="round" opacity=".5">{fade(.12)}</path>
    <g fill="{C["mustard"]}">{"".join(f'<circle cx="{lerp(f)[0]}" cy="{lerp(f)[1]}" r="1.8">{fade(.12)}</circle>' for f in (.535, .565, .595))}</g>'''
    if not anim: details = ""

    END = T_M + .16 + .5
    dots = [(90, 70, 6.5, "coral"), (110, 62, 5.5, "mustard"), (130, 62, 6, "sage"), (150, 70, 5, "lav")]
    dot_svg = ""
    for i, (x, y, r, c) in enumerate(dots):
        an = (f'<animateTransform attributeName="transform" type="translate" values="0 -26;0 3;0 0" keyTimes="0;.7;1" begin="{END+i*.07:.2f}s" dur=".35s" fill="freeze"/>'
              f'<set attributeName="opacity" to="1" begin="{END+i*.07:.2f}s" fill="freeze"/>') if anim else ""
        dot_svg += f'<circle cx="{x}" cy="{y}" r="{r}" fill="{C[c]}" opacity="{0 if anim else 1}">{an}</circle>'

    def spark(x, y, s, beg):
        an = (f'<animate attributeName="opacity" values="0;1;0" dur="1.4s" begin="{beg:.2f}s" repeatCount="indefinite"/>'
              f'<animateTransform attributeName="transform" type="rotate" values="0;90" dur="1.4s" begin="{beg:.2f}s" repeatCount="indefinite"/>') if anim else ""
        return (f'<g transform="translate({x} {y}) scale({s})"><path opacity="{0 if anim else 1}" fill="{C["mustard"]}" '
                f'd="M0 -10 C 1.5 -3, 3 -1.5, 10 0 C 3 1.5, 1.5 3, 0 10 C -1.5 3, -3 1.5, -10 0 C -3 -1.5, -1.5 -3, 0 -10 Z">{an}</path></g>')

    if anim:   # brush tosses in, lands with a bounce, does a quick "flourish" shake, then bends into letters
        enter = (f'<animateTransform attributeName="transform" type="translate" values="40 -150;0 6;0 -3;0 0" keyTimes="0;.6;.85;1" begin="{T_IN-.05:.2f}s" dur=".5s" fill="freeze"/>'
                 f'<animateTransform attributeName="transform" type="rotate" values="-50 120 120;4 120 120;-2 120 120;0 120 120" keyTimes="0;.6;.85;1" begin="{T_IN-.05:.2f}s" dur=".5s" fill="freeze" additive="sum"/>'
                 f'<animateTransform attributeName="transform" type="rotate" values="0 120 120;-5 120 120;4 120 120;0 120 120" begin="{T_M-.25:.2f}s" dur=".25s" additive="sum"/>'
                 f'<set attributeName="opacity" to="1" begin="{T_IN-.05:.2f}s" fill="freeze"/>')
        jump = f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -5;0 0" keyTimes="0;.4;1" begin="{END+.3:.2f}s" dur=".4s"/>'
        pop = f'<animateTransform attributeName="transform" type="scale" values="0;1.08;.97;1" keyTimes="0;.6;.85;1" dur=".45s" fill="freeze"/>'
    else: enter = jump = pop = ""

    body = f'''<defs><clipPath id="c"><circle cx="120" cy="120" r="116"/></clipPath></defs>
<g transform="translate(120 120)"><g>{pop}<g transform="translate(-120 -120)"><g clip-path="url(#c)">
  <circle cx="120" cy="120" r="116" fill="{C["blush"]}"/>
  <circle cx="120" cy="120" r="104" fill="none" stroke="{C["bg"]}" stroke-width="2" stroke-dasharray="1 7" stroke-linecap="round" opacity=".9"/>
  <g>{jump}{dot_svg}
    <g opacity="{0 if anim else 1}">{enter}{"".join(out)}{details}</g>
  </g>
  {spark(178, 70, .75, END)}{spark(64, 168, .5, END+.6)}{spark(176, 176, .4, END+1)}
</g></g></g></g>'''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="480" height="480" role="img" aria-label="Muse &amp; Make">'
            f'<title>Muse &amp; Make</title>{body}</svg>\n')

for mid, name in [("amp", "muse-and-make-morph"), ("n", "muse-and-make-morph-n")]:
    open(f"{name}.svg", "w").write(build(mid, False)); open(f"{name}-animated.svg", "w").write(build(mid, True))
print("morph ok")
