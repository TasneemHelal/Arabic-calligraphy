# Muse & Co. — the paintbrush bends into the letters: handle -> M, band -> &, bristles -> "Co".
import re, math
C = dict(bg="#FBF4EA", ink="#3D2C3E", coral="#E9806E", mustard="#EDB94F", sage="#97B694", lav="#B7A3D8", blue="#94C3D8", blush="#F6DCD3")

M_PATH = ("M62 168 C 64 128, 70 92, 82 72 C 92 56, 102 74, 108 98 "
          "C 113 118, 118 124, 122 108 C 128 84, 136 60, 150 58 "
          "C 166 56, 170 100, 172 136 C 173 158, 178 172, 192 168 "
          "C 202 165, 208 154, 212 144")
AMP = "M 36 58 L 13 27 C 5 15, 10 4, 19 4 C 28 4, 31 13, 24 22 L 9 39 C 1 49, 6 59, 17 59 C 27 59, 33 51, 38 41"

def parse(d):
    t = re.findall(r"[MLC]|-?\d+\.?\d*", d); segs = []; i = 0; cur = None
    while i < len(t):
        c = t[i]; i += 1
        n = {"M": 1, "L": 1, "C": 3}[c]
        while i < len(t) and t[i] not in "MLC":
            pts = [(float(t[i + 2*k]), float(t[i + 2*k + 1])) for k in range(n)]; i += 2 * n
            if c == "M": cur = pts[0]; segs.append(("M", pts))
            else: segs.append((c, pts)); cur = pts[-1]
    return segs

def xf(segs, tx, ty, s, cx, cy):
    return [(c, [(round(tx + s*(x-cx), 2), round(ty + s*(y-cy), 2)) for x, y in p]) for c, p in segs]

def to_d(segs): return " ".join(c + " " + " ".join(f"{x} {y}" for x, y in p) for c, p in segs)

def length(segs):
    L = 0; cur = None
    for c, p in segs:
        if c == "M": cur = p[0]; continue
        if c == "L": L += math.dist(cur, p[0]); cur = p[0]; continue
        p0 = cur; prev = p0
        for k in range(1, 41):
            u = k / 40; a = [(1-u)**3, 3*u*(1-u)**2, 3*u*u*(1-u), u**3]
            q = tuple(a[0]*p0[j] + a[1]*p[0][j] + a[2]*p[1][j] + a[3]*p[2][j] for j in (0, 1))
            L += math.dist(prev, q); prev = q
        cur = p[2]
    return L


M1 = xf(parse(M_PATH), 66, 124, .4, 137, 113)
MIDS = {"amp": xf(parse(AMP), 120, 126, .74, 22, 31)}
# handwritten "Co" in one continuous stroke (C, then loops into o, ends in a flick)
CO_PATH = ("M 177 109 C 168 99, 146 101, 144 124 C 142 145, 160 152, 173 141 "
           "C 177 137, 180 129, 189 127 C 199 125, 204 135, 200 142 C 196 149, 184 149, 183 140 "
           "C 182 131, 192 127, 200 130 C 204 131, 207 129, 210 126")
M2 = parse(CO_PATH)
end = lambda s: s[-1][1][-1]
LA, RB = (54, 128), (192, 111)          # brush axis: handle end (left) -> bristle tip (right)
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
    T_IN, T_M = .3, 1.12                                   # brush lands, morph starts
    ang = math.degrees(math.atan2(RB[1]-LA[1], RB[0]-LA[0]))
    out = []
    for i, ((segs, col, w0, w1), f0, f1) in enumerate(zip(parts, SPLIT, SPLIT[1:])):
        b = T_M + i * .08
        sseg = straight(segs, f0, f1)
        st, fin = to_d(sseg), to_d(segs)
        over = to_d([(c, [(round(x + .14*(x-sx), 2), round(y + .14*(y-sy), 2)) for (x, y), (sx, sy) in zip(p, sp)]) for (c, p), (_, sp) in zip(segs, sseg)])
        cx = round(sum(x for _, p in segs for x, _ in p) / sum(len(p) for _, p in segs), 1)
        by = round(max(y for _, p in segs for _, y in p), 1)
        if anim:
            a = (f'<animate attributeName="d" values="{st};{over};{fin}" keyTimes="0;.6;1" begin="{b:.2f}s" dur=".55s" calcMode="spline" keySplines=".65 0 .35 1;.4 0 .3 1" fill="freeze"/>'
                 f'<animate attributeName="stroke-width" values="{w0};{w1}" begin="{b:.2f}s" dur=".4s" fill="freeze"/>')
            boing = f'<animateTransform attributeName="transform" type="scale" values="1 1;1.16 .84;.94 1.1;1 1" keyTimes="0;.3;.65;1" begin="{b+.55:.2f}s" dur=".4s"/>'
        else: a = boing = ""
        out.append(f'<g transform="translate({cx} {by})"><g>{boing}<g transform="translate({-cx} {-by})">'
                   f'<path d="{st if anim else fin}" fill="none" stroke="{col}" stroke-width="{w0 if anim else w1}" stroke-linecap="round" stroke-linejoin="round">{a}</path></g></g></g>')

    # brush-only details that dissolve as it bends: bristle taper, handle shine, ferrule rivets
    fade = lambda d=.18: f'<animate attributeName="opacity" to="0" begin="{T_M:.2f}s" dur="{d}s" fill="freeze"/>' if anim else ""
    bx0, bx1 = lerp(SPLIT[2]), RB
    details = f'''<g transform="rotate({ang:.2f} {bx0[0]} {bx0[1]})">
      <path d="M {bx0[0]-1} {bx0[1]-6.5} C {bx0[0]+11} {bx0[1]-11}, {bx0[0]+31} {bx0[1]-10}, {bx0[0]+60} {bx0[1]} C {bx0[0]+31} {bx0[1]+10}, {bx0[0]+11} {bx0[1]+11}, {bx0[0]-1} {bx0[1]+6.5} Z" fill="{C["ink"]}">{fade()}</path>
    </g>
    <path d="M {lerp(.06)[0]} {lerp(.06)[1]-2.2} L {lerp(.44)[0]} {lerp(.44)[1]-2.2}" stroke="{C["bg"]}" stroke-width="1.6" stroke-linecap="round" opacity=".5">{fade(.12)}</path>
    <g fill="{C["mustard"]}">{"".join(f'<circle cx="{lerp(f)[0]}" cy="{lerp(f)[1]}" r="1.8">{fade(.12)}</circle>' for f in (.535, .565, .595))}</g>'''
    if not anim: details = ""

    END = T_M + .16 + .55
    dots = [(90, 70, 6.5, "coral"), (110, 62, 5.5, "mustard"), (130, 62, 6, "sage"), (150, 70, 5, "lav")]
    dot_svg = ""
    srcs = [lerp(.565), lerp(.8), lerp(.88), lerp(.93)]
    for i, (x, y, r, c) in enumerate(dots):
        b = T_M + .12 + i * .06
        sx, sy = srcs[i][0] - x, srcs[i][1] - y
        an = (f'<animateMotion path="M {sx:.1f} {sy:.1f} Q {sx*.4:.1f} {min(sy, 0)-34:.1f} 0 0" begin="{b:.2f}s" dur=".5s" calcMode="spline" keyTimes="0;1" keySplines=".2 .7 .3 1" fill="freeze"/>'
              f'<animate attributeName="r" values="1.5;{r*1.35:.1f};{r}" keyTimes="0;.75;1" begin="{b:.2f}s" dur=".5s" fill="freeze"/>'
              f'<set attributeName="opacity" to="1" begin="{b:.2f}s" fill="freeze"/>') if anim else ""
        dot_svg += f'<circle cx="{x}" cy="{y}" r="{r}" fill="{C[c]}" opacity="{0 if anim else 1}">{an}</circle>'
    hole_an = f'<animate attributeName="r" values="0;12.5;9;10" keyTimes="0;.5;.8;1" begin="{END-.05:.2f}s" dur=".4s" fill="freeze"/>' if anim else ""
    hole = f'<circle cx="94" cy="190" r="{0 if anim else 10}" fill="{C["bg"]}">{hole_an}</circle>'

    def spark(x, y, s, beg):
        an = (f'<animate attributeName="opacity" values="0;1;0" dur="1.4s" begin="{beg:.2f}s" repeatCount="indefinite"/>'
              f'<animateTransform attributeName="transform" type="rotate" values="0;90" dur="1.4s" begin="{beg:.2f}s" repeatCount="indefinite"/>') if anim else ""
        return (f'<g transform="translate({x} {y}) scale({s})"><path opacity="{0 if anim else 1}" fill="{C["mustard"]}" '
                f'd="M0 -10 C 1.5 -3, 3 -1.5, 10 0 C 3 1.5, 1.5 3, 0 10 C -1.5 3, -3 1.5, -10 0 C -3 -1.5, -1.5 -3, 0 -10 Z">{an}</path></g>')

    if anim:   # brush tosses in, lands with a bounce, does a quick "flourish" shake, then bends into letters
        enter = (f'<animateTransform attributeName="transform" type="translate" values="-170 110;8 -8;-3 2;0 0" keyTimes="0;.55;.8;1" begin="{T_IN-.05:.2f}s" dur=".55s" calcMode="spline" keySplines=".2 .8 .3 1;.4 0 .6 1;.4 0 .6 1" fill="freeze"/>'
                 f'<animateTransform attributeName="transform" type="rotate" values="-220 120 120;10 120 120;-4 120 120;0 120 120" keyTimes="0;.55;.8;1" begin="{T_IN-.05:.2f}s" dur=".55s" calcMode="spline" keySplines=".2 .8 .3 1;.4 0 .6 1;.4 0 .6 1" fill="freeze" additive="sum"/>'
                 f'<animateTransform attributeName="transform" type="translate" values="0 0;-12 4;0 0" keyTimes="0;.7;1" begin="{T_M-.22:.2f}s" dur=".26s" additive="sum"/>'
                 f'<animateTransform attributeName="transform" type="rotate" values="0 120 120;-6 120 120;0 120 120" keyTimes="0;.7;1" begin="{T_M-.22:.2f}s" dur=".26s" additive="sum"/>'
                 f'<set attributeName="opacity" to="1" begin="{T_IN-.05:.2f}s" fill="freeze"/>')
        jump = ""   # badge stays still
        pop = ""    # circle is present from the start, no pop-in
    else: enter = jump = pop = ""

    body = f'''<defs><clipPath id="c"><circle cx="120" cy="120" r="116"/></clipPath></defs>
<g transform="translate(120 120)"><g>{pop}<g transform="translate(-120 -120)"><g clip-path="url(#c)">
  <circle cx="120" cy="120" r="116" fill="{C["blush"]}"/>
  <circle cx="120" cy="120" r="104" fill="none" stroke="{C["bg"]}" stroke-width="2" stroke-dasharray="1 7" stroke-linecap="round" opacity=".9"/>
  <g>{jump}{hole}{dot_svg}
    <g opacity="{0 if anim else 1}">{enter}{"".join(out)}{details}</g>
  </g>
  {spark(178, 70, .75, END)}{spark(58, 150, .5, END+.6)}{spark(176, 176, .4, END+1)}
</g></g></g></g>'''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="480" height="480" role="img" aria-label="Muse &amp; Make">'
            f'<title>Muse &amp; Make</title>{body}</svg>\n')


if __name__ == "__main__":
    open("muse-and-co-emblem.svg", "w").write(build("amp", False))
    open("muse-and-co-emblem-animated.svg", "w").write(build("amp", True))
    print("emblem ok")
