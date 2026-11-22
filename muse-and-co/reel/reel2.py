# Energetic, beat-synced "Coming soon" reel (1080x1920, 15 s) for Muse & Co. — timed to music.py (128 BPM).
import re, sys, math, random
sys.path.insert(0, "..")
from emblem import build, C

B = 60 / 128
bt = lambda b: b * B
random.seed(4)
FONT = "@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@600;700&family=Nunito:wght@800&display=swap');"
Q6 = 'font-family="Quicksand, Nunito, Arial, sans-serif" font-weight="600"'
Q7 = 'font-family="Quicksand, Nunito, Arial, sans-serif" font-weight="700"'
NU = 'font-family="Nunito, Arial, sans-serif" font-weight="800"'
PAL = [C["coral"], C["mustard"], C["sage"], C["lav"], C["blue"]]
SP = "M0 -10 C 1.5 -3, 3 -1.5, 10 0 C 3 1.5, 1.5 3, 0 10 C -1.5 3, -3 1.5, -10 0 C -3 -1.5, -1.5 -3, 0 -10 Z"

def show(t): return f'<set attributeName="opacity" to="1" begin="{t:.3f}s" fill="freeze"/>'
def hide(t): return f'<set attributeName="opacity" to="0" begin="{t:.3f}s" fill="freeze"/>'
def slam(t, s0=1.8, dur=.32, rot=0):
    a = (f'<animateTransform attributeName="transform" type="scale" values="{s0};.9;1.05;1" keyTimes="0;.45;.75;1" '
         f'calcMode="spline" keySplines=".2 .9 .3 1;.4 0 .6 1;.4 0 .6 1" begin="{t:.3f}s" dur="{dur}s" fill="freeze" additive="sum"/>')
    if rot: a += f'<animateTransform attributeName="transform" type="rotate" values="{rot};{-rot/3:.1f};0" keyTimes="0;.6;1" begin="{t:.3f}s" dur="{dur}s" fill="freeze" additive="sum"/>'
    return a
def pulse(t, n, amt=1.06): return (f'<animateTransform attributeName="transform" type="scale" values="{amt};1" keyTimes="0;1" calcMode="spline" keySplines=".2 .8 .3 1" '
                                    f'begin="{t:.3f}s" dur="{B:.5f}s" repeatCount="{n}" additive="sum"/>')
def shake(t, k=14): return (f'<animateTransform attributeName="transform" type="translate" values="0 0;{-k} {k*.6:.0f};{k*.85:.0f} {-k*.7:.0f};{-k*.55:.0f} {k*.4:.0f};{k*.3:.0f} {-k*.25:.0f};0 0" '
                            f'begin="{t:.3f}s" dur=".38s" additive="sum"/>')
def at(x, y, body, anim=""): return f'<g transform="translate({x} {y})"><g opacity="0">{anim}{body}</g></g>'

def confetti(cx, cy, t, n=26, dist=(320, 720), seed=0):
    rnd = random.Random(seed); out = []
    for i in range(n):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(*dist)
        dx, dy = d * math.cos(a), d * math.sin(a) * .8; fall = rnd.uniform(140, 320)
        r = rnd.uniform(9, 22); col = rnd.choice(PAL); dur = rnd.uniform(.9, 1.3)
        shape = (f'<circle r="{r:.1f}" fill="{col}"/>' if i % 3 else f'<path d="{SP}" fill="{col}" transform="scale({r/8:.2f})"/>')
        out.append(f'<g transform="translate({cx} {cy})"><g opacity="0">{show(t)}'
                   f'<animateMotion path="M 0 0 Q {dx*.6:.0f} {dy*.6-120:.0f} {dx:.0f} {dy+fall:.0f}" begin="{t:.3f}s" dur="{dur:.2f}s" calcMode="spline" keyTimes="0;1" keySplines=".1 .7 .4 1" fill="freeze"/>'
                   f'<animate attributeName="opacity" values="1;1;0" keyTimes="0;.7;1" begin="{t:.3f}s" dur="{dur:.2f}s" fill="freeze"/>{shape}</g></g>')
    return "".join(out)

def emblem_at(offset):
    s = re.sub(r'^<svg[^>]*>|</svg>\s*$', '', build("amp", True).strip())
    s = re.sub(r'begin="([\d.]+)s"', lambda m: f'begin="{float(m.group(1)) + offset:.3f}s"', s)
    return s.replace('id="c"', 'id="badgeclip"').replace('url(#c)', 'url(#badgeclip)')

def reel():
    o = []
    # background blobs: drift + pulse on every beat after the drop
    for i, (x, y, r, c) in enumerate([(110, 250, 250, "coral"), (990, 560, 220, "lav"), (60, 1480, 290, "sage"), (1010, 1760, 270, "mustard"), (1040, 1060, 110, "coral")]):
        dx, dy = (40, -30) if i % 2 else (-35, 40)
        o.append(f'<g transform="translate({x} {y})"><g><animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" dur="{6+i}s" repeatCount="indefinite"/>'
                 f'<g>{pulse(bt(8), 20, 1.1)}<circle r="{r}" fill="{C[c]}" opacity=".18"/></g></g></g>')

    scene = []
    # ---- DROP: badge slams in, brush morphs (emblem timeline shifted so the morph lands on beat 10)
    off = bt(10) - 1.12
    scene.append(f'<g transform="translate(540 470)"><g opacity="0">{show(bt(8))}{slam(bt(8), 1.35, .4)}'
                 f'<g transform="translate(-276 -276) scale(2.3)">{emblem_at(off)}</g></g></g>')
    scene.append(confetti(540, 470, bt(8) + .02, 22, (330, 650), 1))

    # ---- "Muse &" + Co words snapping in on each kick, then lockup
    scene.append(at(540, 905, f'<text text-anchor="middle" {Q6} font-size="108" fill="{C["ink"]}">Muse <tspan fill="{C["coral"]}">&amp;</tspan></text>',
                    show(bt(12)) + slam(bt(12), 1.6) + hide(bt(17))))
    for i, w in enumerate(["Colors", "Collectives", "Communities", "Collaborations"]):
        t = bt(13 + i)
        scene.append(at(540, 1030, f'<text text-anchor="middle" {Q6} font-size="104" fill="{C["ink"]}">Co<tspan fill="{C["coral"]}">{w[2:]}</tspan></text>',
                        show(t) + slam(t, 1.5, .25, -5 if i % 2 else 5) + hide(t + B)))
    scene.append(at(540, 985, f'<text text-anchor="middle" {Q6} font-size="116" fill="{C["ink"]}">Muse <tspan fill="{C["coral"]}">&amp;</tspan> Co.</text>',
                    show(bt(17)) + slam(bt(17), 1.7, .35)))
    scene.append(at(540, 1090, f'<text text-anchor="middle" {NU} font-size="46" fill="{C["ink"]}" fill-opacity=".75">something creative is…</text>',
                    show(bt(18)) + slam(bt(18), 1.3, .3)))

    # ---- IMPACT (beat 20): COMING SOON + flash + shake + confetti, then pulses on the beat
    cs = []
    for j, (word, col, y) in enumerate([("COMING", C["ink"], 1295), ("SOON", C["coral"], 1450)]):
        cs.append(at(540, y - 55, f'<g>{pulse(bt(22), 6, 1.05)}<text y="55" text-anchor="middle" {Q7} font-size="{168 if j == 0 else 190}" letter-spacing="6" fill="{col}">{word}</text></g>',
                     show(bt(20) + j * .1) + slam(bt(20) + j * .1, 2.2, .38, -6 if j == 0 else 6)))
    scene += cs
    scene.append(f'<path d="M 330 1492 C 430 1467, 640 1463, 752 1479" pathLength="1" fill="none" stroke="{C["mustard"]}" stroke-width="18" stroke-linecap="round" '
                 f'stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0">{show(bt(21))}<animate attributeName="stroke-dashoffset" from="1" to="0" begin="{bt(21):.3f}s" dur=".3s" fill="freeze"/></path>')
    scene.append(confetti(540, 1330, bt(20) + .03, 34, (380, 760), 2))
    for k, (x, y, s) in enumerate([(190, 1230, 2.6), (890, 1370, 2.0), (220, 1470, 1.5), (870, 1200, 1.4)]):
        scene.append(f'<g transform="translate({x} {y}) scale({s})"><path d="{SP}" fill="{C["mustard"]}" opacity="0">'
                     f'<animate attributeName="opacity" values="0;1;0" dur="{2*B:.4f}s" begin="{bt(21)+k*B/2:.3f}s" repeatCount="indefinite"/>'
                     f'<animateTransform attributeName="transform" type="rotate" values="0;90" dur="{2*B:.4f}s" begin="{bt(21)+k*B/2:.3f}s" repeatCount="indefinite"/></path></g>')

    # ---- domain pill (beat 24) + final hit confetti (beat 28)
    scene.append(at(540, 1598, f'<g>{pulse(bt(28), 1, 1.12)}<rect x="-215" y="-42" width="430" height="84" rx="42" fill="{C["coral"]}"/>'
                    f'<text y="15" text-anchor="middle" {NU} font-size="42" fill="{C["bg"]}" letter-spacing="1">museandco.art</text></g>',
                    show(bt(24)) + slam(bt(24), 0, .4)))
    scene.append(confetti(540, 1598, bt(28) + .02, 24, (300, 620), 3))

    o.append(f'<g>{shake(bt(8), 10)}{shake(bt(20), 18)}{shake(bt(28), 8)}{"".join(scene)}</g>')
    # coral flash on the impact
    o.append(f'<rect width="1080" height="1920" fill="{C["coral"]}" opacity="0"><animate attributeName="opacity" values=".85;0" begin="{bt(20):.3f}s" dur=".35s"/></rect>')
    o.append(f'<rect width="1080" height="1920" fill="#fff" opacity="0"><animate attributeName="opacity" values=".9;0" begin="{bt(8):.3f}s" dur=".3s"/></rect>')

    # ---- INTRO (beats 0-7): colour bursts + big words, zoom on the riser, cut to cream before the drop
    intro = []
    words = [("Paint!", C["coral"], C["bg"], -7), ("Draw!", C["sage"], C["ink"], 6), ("Color!", C["mustard"], C["ink"], -5), ("Create!", C["lav"], C["ink"], 4)]
    for i, (w, bg, fg, rot) in enumerate(words):
        t = bt(2 * i)
        intro.append(f'<circle cx="540" cy="960" r="0" fill="{bg}"><animate attributeName="r" values="0;1150" begin="{t:.3f}s" dur=".24s" calcMode="spline" keyTimes="0;1" keySplines=".3 .7 .3 1" fill="freeze"/></circle>')
        dots = "".join(f'<circle cx="{random.randint(-380, 380)}" cy="{random.choice([-1, 1]) * random.randint(170, 330)}" r="{random.randint(14, 30)}" fill="{c}"/>'
                       for c in random.sample([p for p in PAL if p != bg], 3))
        zoom = (f'<animateTransform attributeName="transform" type="scale" values="1;1.3" begin="{bt(6.4):.3f}s" dur="{bt(7.5)-bt(6.4):.3f}s" fill="freeze" additive="sum"/>' if i == 3 else "")
        intro.append(at(540, 960, f'<g>{zoom}<g>{dots}</g><text y="70" text-anchor="middle" {Q7} font-size="220" fill="{fg}">{w}</text></g>',
                        show(t) + slam(t, 2.4, .34, rot)))
    o.append(f'<g>{hide(bt(7.5))}{"".join(intro)}</g>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920">'
            f'<style><![CDATA[{FONT}]]></style><rect width="1080" height="1920" fill="{C["bg"]}"/>{"".join(o)}</svg>\n')

open("muse-and-co-coming-soon.svg", "w").write(reel())
print("reel2 ok")
