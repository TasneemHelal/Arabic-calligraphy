# "Coming soon" Instagram reel (1080x1920) built from the Muse & Co. logo. Run from muse-and-co/.
import re, sys
sys.path.insert(0, ".")
from emblem import build, C

FONT = "@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@600;700&family=Nunito:wght@700;800&display=swap');"
Q = 'font-family="Quicksand, Nunito, Arial, sans-serif" font-weight="600"'
Q7 = 'font-family="Quicksand, Nunito, Arial, sans-serif" font-weight="700"'
N = 'font-family="Nunito, Arial, sans-serif" font-weight="800"'
WORDS = ["Colors", "Collectives", "Communities", "Collaborations"]

def inner(svg): return re.sub(r'^<svg[^>]*>|</svg>\s*$', '', svg.strip())

def rise(beg, dy=40, dur=.5):
    return (f'<set attributeName="opacity" to="1" begin="{beg:.2f}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 {dy};0 -6;0 0" keyTimes="0;.7;1" begin="{beg:.2f}s" dur="{dur}s" '
            f'calcMode="spline" keySplines=".2 .8 .3 1;.4 0 .6 1" fill="freeze" additive="sum"/>')

def fade_out(beg, dur=.3):
    return f'<animate attributeName="opacity" to="0" begin="{beg:.2f}s" dur="{dur}s" fill="freeze"/>'

def pop(beg, dur=.55):
    return (f'<animateTransform attributeName="transform" type="scale" values="0;1.18;.94;1" keyTimes="0;.55;.8;1" '
            f'begin="{beg:.2f}s" dur="{dur}s" fill="freeze" additive="sum"/>')

def build_reel():
    out = []
    # drifting background paint blobs
    blobs = [(120, 260, 260, "coral"), (980, 520, 230, "lav"), (60, 1500, 300, "sage"), (1010, 1750, 280, "mustard"), (1030, 1020, 110, "coral")]
    for i, (x, y, r, c) in enumerate(blobs):
        dx, dy = (40, -30) if i % 2 else (-35, 40)
        out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{C[c]}" opacity=".16">'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" dur="{7+i}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></circle>')

    # 1) badge: brush bends into M&Co (its own timeline starts at 0)
    out.append(f'<g transform="translate(270 200) scale(2.25)">{inner(build("amp", True))}</g>')

    # 2) "Muse &" + rotating Co words (Co plum, ending coral), then single-line lockup
    t_line1, t0, step = 1.55, 2.05, .9
    out.append(f'<g opacity="0">{rise(t_line1)}{fade_out(t0 + 4*step - .05)}'
               f'<text x="540" y="905" text-anchor="middle" {Q} font-size="104" fill="{C["ink"]}">Muse <tspan fill="{C["coral"]}">&amp;</tspan></text></g>')
    out.append('<defs><clipPath id="wordband"><rect x="0" y="930" width="1080" height="125"/></clipPath></defs><g clip-path="url(#wordband)">')
    for i, w in enumerate(WORDS):
        t = t0 + i * step
        out.append(f'<text x="540" y="1025" text-anchor="middle" {Q} font-size="104" fill="{C["ink"]}" opacity="0">Co<tspan fill="{C["coral"]}">{w[2:]}</tspan>'
                   f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.18;.82;1" begin="{t:.2f}s" dur="{step}s"/>'
                   f'<animateTransform attributeName="transform" type="translate" values="0 110;0 -6;0 0;0 0;0 -110" keyTimes="0;.18;.26;.82;1" '
                   f'calcMode="spline" keySplines=".2 .8 .3 1;.4 0 .6 1;0 0 1 1;.6 0 .8 .4" begin="{t:.2f}s" dur="{step}s"/></text>')
    out.append('</g>')
    t_lock = t0 + 4 * step
    out.append(f'<g opacity="0">{rise(t_lock, 30)}<text x="540" y="975" text-anchor="middle" {Q} font-size="112" fill="{C["ink"]}">Muse <tspan fill="{C["coral"]}">&amp;</tspan> Co.</text></g>')

    # 3) COMING SOON — each word pops, brush-stroke underline paints in
    t_cs = t_lock + .9
    for j, (word, col, y) in enumerate([("Coming", C["ink"], 1215), ("soon", C["coral"], 1345)]):
        out.append(f'<g transform="translate(540 {y-45})"><g opacity="0"><set attributeName="opacity" to="1" begin="{t_cs + j*.35:.2f}s" fill="freeze"/>{pop(t_cs + j*.35)}'
                   f'<text x="0" y="45" text-anchor="middle" {Q7} font-size="150" fill="{col}">{word}</text></g></g>')
    sw = "M 362 1392 C 440 1370, 600 1366, 722 1380"
    out.append(f'<path d="{sw}" pathLength="1" fill="none" stroke="{C["mustard"]}" stroke-width="16" stroke-linecap="round" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0">'
               f'<set attributeName="opacity" to="1" begin="{t_cs+.75:.2f}s" fill="freeze"/>'
               f'<animate attributeName="stroke-dashoffset" from="1" to="0" begin="{t_cs+.75:.2f}s" dur=".45s" calcMode="spline" keyTimes="0;1" keySplines=".6 0 .2 1" fill="freeze"/></path>')
    for k, (x, y, s) in enumerate([(250, 1170, 1.6), (850, 1290, 1.2), (300, 1360, .9)]):   # sparkles around "coming soon"
        out.append(f'<g transform="translate({x} {y}) scale({s})"><path opacity="0" fill="{C["mustard"]}" d="M0 -10 C 1.5 -3, 3 -1.5, 10 0 C 3 1.5, 1.5 3, 0 10 C -1.5 3, -3 1.5, -10 0 C -3 -1.5, -1.5 -3, 0 -10 Z" transform="scale(2.2)">'
                   f'<animate attributeName="opacity" values="0;1;0" dur="1.6s" begin="{t_cs+1+k*.35:.2f}s" repeatCount="indefinite"/></path></g>')

    # 4) what's coming + domain
    t_sub = t_cs + 1.35
    out.append(f'<g opacity="0">{rise(t_sub, 30)}<text x="540" y="1480" text-anchor="middle" {N} font-size="40" fill="{C["ink"]}" fill-opacity=".8">Art workshops · Baby gift boxes</text></g>')
    out.append(f'<g opacity="0">{rise(t_sub+.15, 30)}<text x="540" y="1534" text-anchor="middle" {N} font-size="40" fill="{C["ink"]}" fill-opacity=".8">Art products · Gallery</text></g>')
    t_dom = t_sub + .55
    out.append(f'<g transform="translate(540 1622)"><g opacity="0"><set attributeName="opacity" to="1" begin="{t_dom:.2f}s" fill="freeze"/>{pop(t_dom)}'
               f'<rect x="-205" y="-40" width="410" height="80" rx="40" fill="{C["coral"]}"/>'
               f'<text x="0" y="14" text-anchor="middle" {N} font-size="40" fill="{C["bg"]}" letter-spacing="1">museandco.art</text></g></g>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920">'
            f'<style><![CDATA[{FONT}]]></style><rect width="1080" height="1920" fill="{C["bg"]}"/>' + "".join(out) + '</svg>\n'), t_dom

svg, t_end = build_reel()
open("reel/muse-and-co-coming-soon.svg", "w").write(svg)
print("reel ok; last element at", round(t_end, 2), "s")
