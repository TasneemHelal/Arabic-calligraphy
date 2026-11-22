# Muse & Make — "brush paints the letters" monogram. Everything is clipped to one circle.
import re, math
from build import C, M_PATH
from monogram import AMP, N

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
M2 = xf(parse(M_PATH), 174, 124, .4, 137, 113)
MIDS = {"amp": xf(parse(AMP), 120, 126, .74, 22, 31), "n": xf(parse(N), 120, 132, .62, 19.5, 37)}
start = lambda s: s[0][1][0]
end = lambda s: s[-1][1][-1]

BRUSH = f'''<g transform="rotate(-38) scale(1.45)">
  <path d="M0 0 C -3 -6, -4.5 -14, -3.6 -20 L 3.6 -20 C 4.5 -14, 3 -6, 0 0 Z" fill="{C["ink"]}">
    TIPANIM
  </path>
  <rect x="-4" y="-30" width="8" height="11" rx="1.5" fill="{C["mustard"]}"/>
  <path d="M-3.4 -30 L -2.4 -78 C -2.2 -82, 2.2 -82, 2.4 -78 L 3.4 -30 Z" fill="{C["sage"]}"/>
</g>'''

def build(mid, anim):
    letters = [(M1, C["ink"], 8), (MIDS[mid], C["coral"], 7.4), (M2, C["ink"], 8)]
    # timeline (seconds)
    T0, IN, LIFT, OUT = .35, .22, .1, .22
    durs = [.45, .26, .45]
    lens = [length(s) for s, _, _ in letters]
    entry_from, exit_to = (210, 230), (230, 10)
    hops = [math.dist(entry_from, start(M1)), math.dist(end(M1), start(MIDS[mid])),
            math.dist(end(MIDS[mid]), start(M2)), math.dist(end(M2), exit_to)]
    motion = (f"M {entry_from[0]} {entry_from[1]} L {start(M1)[0]} {start(M1)[1]} " + to_d(M1)[1:].split(" ", 3)[3] +
              f" L {start(MIDS[mid])[0]} {start(MIDS[mid])[1]} " + to_d(MIDS[mid]).split(" ", 3)[3] +
              f" L {start(M2)[0]} {start(M2)[1]} " + to_d(M2).split(" ", 3)[3] + f" L {exit_to[0]} {exit_to[1]}")
    pieces = [(hops[0], IN), (lens[0], durs[0]), (hops[1], LIFT), (lens[1], durs[1]), (hops[2], LIFT), (lens[2], durs[2]), (hops[3], OUT)]
    total_len = sum(p[0] for p in pieces); total_t = sum(p[1] for p in pieces)
    kp, kt, a, b = ["0"], ["0"], 0, 0
    for L, t in pieces:
        a += L; b += t; kp.append(f"{min(a/total_len,1):.4f}"); kt.append(f"{min(b/total_t,1):.4f}")
    kp[-1] = kt[-1] = "1"
    draw_begin = [T0 + IN, T0 + IN + durs[0] + LIFT, T0 + IN + durs[0] + LIFT + durs[1] + LIFT]
    END = T0 + total_t

    out = []
    for (segs, col, w), beg, du in zip(letters, draw_begin, durs):
        base = end(segs)
        dash = (f'stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><set attributeName="opacity" to="1" begin="{beg:.3f}s" fill="freeze"/><animate attributeName="stroke-dashoffset" from="1" to="0" begin="{beg:.3f}s" dur="{du}s" fill="freeze"/></path>'
                if anim else ">" + "</path>")
        boing = (f'<animateTransform attributeName="transform" type="scale" values="1 1;1.16 .84;.94 1.1;1 1" keyTimes="0;.3;.65;1" begin="{beg+du:.3f}s" dur=".4s"/>' if anim else "")
        cx = round((min(x for _, p in segs for x, _ in p) + max(x for _, p in segs for x, _ in p)) / 2, 1)
        by = round(max(y for _, p in segs for _, y in p), 1)
        out.append(f'''<g transform="translate({cx} {by})"><g>{boing}<g transform="translate({-cx} {-by})">
    <path d="{to_d(segs)}" pathLength="1" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {dash}
  </g></g></g>''')

    dots = [(90, 70, 6.5, "coral"), (110, 62, 5.5, "mustard"), (130, 62, 6, "sage"), (150, 70, 5, "lav")]
    dot_svg = ""
    for i, (x, y, r, c) in enumerate(dots):
        an = (f'<animateTransform attributeName="transform" type="translate" values="0 -26;0 3;0 0" keyTimes="0;.7;1" begin="{END-.15+i*.07:.2f}s" dur=".35s" fill="freeze"/>'
              f'<set attributeName="opacity" to="1" begin="{END-.15+i*.07:.2f}s" fill="freeze"/>') if anim else ""
        dot_svg += f'<circle cx="{x}" cy="{y}" r="{r}" fill="{C[c]}" opacity="{0 if anim else 1}">{an}</circle>'

    def spark(x, y, s, beg):
        an = (f'<animate attributeName="opacity" values="0;1;0" dur="1.4s" begin="{beg}s" repeatCount="indefinite"/>'
              f'<animateTransform attributeName="transform" type="rotate" values="0;90" dur="1.4s" begin="{beg}s" repeatCount="indefinite" additive="sum"/>') if anim else ""
        return (f'<g transform="translate({x} {y}) scale({s})"><path opacity="{0 if anim else 1}" fill="{C["mustard"]}" '
                f'd="M0 -10 C 1.5 -3, 3 -1.5, 10 0 C 3 1.5, 1.5 3, 0 10 C -1.5 3, -3 1.5, -10 0 C -3 -1.5, -1.5 -3, 0 -10 Z">{an}</path></g>')

    tip = ""
    t_mid0 = (draw_begin[1] - .05 - T0) / total_t; t_mid1 = (draw_begin[2] - .05 - T0) / total_t
    if anim:
        tip = f'<animate attributeName="fill" values="{C["ink"]};{C["coral"]};{C["ink"]}" keyTimes="0;{t_mid0:.3f};{t_mid1:.3f}" calcMode="discrete" begin="{T0}s" dur="{total_t:.3f}s" fill="freeze"/>'
    brush = ""
    if anim:
        brush = (f'<g opacity="0"><set attributeName="opacity" to="1" begin="{T0}s"/><set attributeName="opacity" to="0" begin="{END:.3f}s"/>'
                 f'<animateMotion path="{motion}" keyPoints="{";".join(kp)}" keyTimes="{";".join(kt)}" calcMode="linear" begin="{T0}s" dur="{total_t:.3f}s" fill="freeze"/>'
                 + BRUSH.replace("TIPANIM", tip) + '</g>')

    pop = (f'<animateTransform attributeName="transform" type="scale" values="0;1.08;.97;1" keyTimes="0;.6;.85;1" dur="{T0+.1}s" fill="freeze"/>' if anim else "")
    jump = (f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -5;0 0" keyTimes="0;.4;1" begin="{END+.25:.2f}s" dur=".4s"/>' if anim else "")
    body = f'''<defs><clipPath id="c"><circle cx="120" cy="120" r="116"/></clipPath></defs>
<g transform="translate(120 120)"><g>{pop}<g transform="translate(-120 -120)">
<g clip-path="url(#c)">
  <circle cx="120" cy="120" r="116" fill="{C["blush"]}"/>
  <circle cx="120" cy="120" r="104" fill="none" stroke="{C["bg"]}" stroke-width="2" stroke-dasharray="1 7" stroke-linecap="round" opacity=".9"/>
  <g>{jump}
  {dot_svg}
  {"".join(out)}
  </g>
  {spark(178, 70, .75, END)}{spark(64, 168, .5, END+.6)}{spark(176, 176, .4, END+1)}
  {brush}
</g></g></g></g>'''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="480" height="480" role="img" aria-label="Muse &amp; Make">'
            f'<title>Muse &amp; Make</title>{body}</svg>\n'), END

for mid, name in [("amp", "muse-and-make-brush")]:
    s, end_t = build(mid, False); open(f"{name}.svg", "w").write(s)
    s, end_t = build(mid, True); open(f"{name}-animated.svg", "w").write(s)
print("ok", round(end_t, 2))
