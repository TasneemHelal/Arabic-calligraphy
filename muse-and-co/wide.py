# Wide Muse & Co. logo. Static version + animated version where the word after "&" rolls through
# Colors -> Collectives -> Communities -> Collaborations and lands on "Co." (the "Co" stays fixed).
import re, json
from emblem import build, C
FONT = "@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;1,9..144,400&family=Nunito:wght@700&display=swap');"
W = json.load(open("widths.json"))
WORDS = ["Colors", "Collectives", "Communities", "Collaborations"]
FR = 'font-family="Fraunces, Georgia, serif" font-weight="500" font-size="72" letter-spacing="-1"'
X_AMP, X_CO = 180, 246
X_SUF = X_CO + W["Co"]
TAG_W = W[" · ".join(WORDS)]

def inner(svg): return re.sub(r'^<svg[^>]*>|</svg>\s*$', '', svg.strip())

def tagline():
    co = f'<tspan fill="{C["coral"]}">Co</tspan>'
    sep = f'<tspan fill="{C["sage"]}"> · </tspan>'
    line = sep.join(co + f'<tspan>{w[2:]}</tspan>' for w in WORDS)
    return f'<text x="2" y="178" font-family="Nunito, Arial, sans-serif" font-weight="700" font-size="17" letter-spacing=".6" fill="{C["ink"]}">{line}</text>'

def rise(beg):
    return (f'<set attributeName="opacity" to="1" begin="{beg}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 22;0 -3;0 0" keyTimes="0;.7;1" begin="{beg}s" dur=".45s" calcMode="spline" keySplines=".2 .8 .3 1;.4 0 .6 1" fill="freeze"/>')

def wordmark(anim, suffix_block=""):
    o = ' opacity="0"' if anim else ""
    r = rise if anim else (lambda b: "")
    rule_an = (f'<animate attributeName="width" from="0" to="{TAG_W}" begin="{T_FINAL+.2:.2f}s" dur=".5s" calcMode="spline" keyTimes="0;1" keySplines=".6 0 .2 1" fill="freeze"/>' if anim else "")
    return f'''<g transform="translate(272 0)">
  <g{o}>{r(1.25)}<text x="0" y="122" {FR} fill="{C["ink"]}">Muse</text></g>
  <g{o}>{r(1.4)}<text x="{X_AMP}" y="124" font-family="Fraunces, Georgia, serif" font-style="italic" font-size="78" fill="{C["coral"]}">&amp;</text></g>
  <g{o}>{r(1.55)}<text x="{X_CO}" y="122" {FR} fill="{C["ink"]}">Co</text></g>
  {suffix_block if anim else f'<text x="{X_SUF}" y="122" {FR} fill="{C["ink"]}">.</text>'}
  <rect x="2" y="144" width="{0 if anim else TAG_W}" height="3" rx="1.5" fill="{C["sage"]}">{rule_an}</rect>
  <g{o}>{r(round(T_FINAL+.45, 2))}{tagline()}</g>
  <g{o}>{r(round(T_FINAL+.6, 2))}<text x="2" y="206" font-family="Nunito, Arial, sans-serif" font-weight="700" font-size="16" letter-spacing="1.5" fill="{C["coral"]}">museandco.art</text></g>
</g>'''

# word timeline
T0, STEP, HOLD = 1.95, .95, .76            # each word: slides in, holds, slides out
starts = [T0 + i * STEP for i in range(len(WORDS))]
T_FINAL = T0 + len(WORDS) * STEP

def suffixes():
    out = [f'<defs><clipPath id="band"><rect x="{X_SUF-4}" y="46" width="420" height="102"/></clipPath></defs><g clip-path="url(#band)">']
    for w, t in zip(WORDS, starts):
        out.append(f'<text x="{X_SUF}" y="122" {FR} fill="{C["ink"]}" opacity="0">{w[2:]}'
                   f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.18;.8;1" begin="{t:.2f}s" dur="{STEP}s"/>'
                   f'<animateTransform attributeName="transform" type="translate" values="0 56;0 -5;0 0;0 0;0 -56" keyTimes="0;.18;.26;.8;1" '
                   f'calcMode="spline" keySplines=".2 .8 .3 1;.4 0 .6 1;0 0 1 1;.6 0 .8 .4" begin="{t:.2f}s" dur="{STEP}s"/></text>')
    out.append(f'<text x="{X_SUF}" y="122" {FR} fill="{C["ink"]}" opacity="0">.'
               f'<set attributeName="opacity" to="1" begin="{T_FINAL:.2f}s" fill="freeze"/>'
               f'<animateTransform attributeName="transform" type="translate" values="0 56;0 -5;0 0" keyTimes="0;.7;1" calcMode="spline" keySplines=".2 .8 .3 1;.4 0 .6 1" begin="{T_FINAL:.2f}s" dur=".25s" fill="freeze"/></text></g>')
    return "".join(out)

def static():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 240" width="1480" height="480" role="img" aria-label="Muse &amp; Co.">
<title>Muse &amp; Co.</title><style><![CDATA[{FONT}]]></style>
<g>{inner(build("amp", False))}</g>{wordmark(False)}
</svg>
'''

def animated(CW=1000):
    comp = lambda suf_w: 272 + max(X_SUF + suf_w, TAG_W)
    shift = lambda suf_w: round((CW - comp(suf_w)) / 2, 1)
    final = shift(W["."])
    times, vals = [0], [final]
    for w, t in zip(WORDS, starts):            # glide so the logo stays centred as the word length changes
        times += [t - .12, t + .22]; vals += [vals[-1], shift(W[w[2:]])]
    times += [T_FINAL - .12, T_FINAL + .25]; vals += [vals[-1], final]
    dur = times[-1]
    kt = ";".join(f"{x/dur:.4f}" for x in times); kv = ";".join(f"{v} 0" for v in vals)
    ks = ";".join(".45 0 .25 1" for _ in times[1:])
    glide = f'<animateTransform attributeName="transform" type="translate" values="{kv}" keyTimes="{kt}" calcMode="spline" keySplines="{ks}" dur="{dur:.2f}s" fill="freeze"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CW} 240" width="{CW*2}" height="480" role="img" aria-label="Muse &amp; Co.">
<title>Muse &amp; Co.</title><style><![CDATA[{FONT}]]></style>
<g transform="translate({final} 0)">{glide}
<g>{inner(build("amp", True))}</g>{wordmark(True, suffixes())}
</g>
</svg>
'''

open("muse-and-co-logo.svg", "w").write(static())
open("muse-and-co-logo-animated.svg", "w").write(animated())
print("wide ok; final word at", round(T_FINAL, 2), "s")
