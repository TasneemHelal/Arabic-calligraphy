# Wide Muse & Co. logo: animated emblem + wordmark + tagline + domain.
import re
from emblem import build, C
FONT = "@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;1,9..144,400&family=Nunito:wght@700&display=swap');"

def inner(svg):  # emblem contents without its outer <svg> wrapper
    return re.sub(r'^<svg[^>]*>|</svg>\s*$', '', svg.strip())

def wide(anim):
    def rise(beg):
        if not anim: return ""
        return (f'<set attributeName="opacity" to="1" begin="{beg}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" values="0 22;0 -3;0 0" keyTimes="0;.7;1" begin="{beg}s" dur=".45s" calcMode="spline" keySplines=".2 .8 .3 1;.4 0 .6 1" fill="freeze"/>')
    o = ' opacity="0"' if anim else ""
    f = 'font-family="Fraunces, Georgia, serif"'
    rule = (f'<animate attributeName="width" from="0" to="420" begin="1.75s" dur=".5s" calcMode="spline" keyTimes="0;1" keySplines=".6 0 .2 1" fill="freeze"/>' if anim else "")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 240" width="1480" height="480" role="img" aria-label="Muse &amp; Co.">
<title>Muse &amp; Co.</title>
<style><![CDATA[{FONT}]]></style>
<g>{inner(build("amp", anim))}</g>
<g transform="translate(272 0)">
  <g{o}>{rise(1.25)}<text x="0" y="122" {f} font-weight="500" font-size="80" fill="{C["ink"]}" letter-spacing="-1">Muse</text></g>
  <g{o}>{rise(1.4)}<text x="194" y="124" {f} font-style="italic" font-size="86" fill="{C["coral"]}">&amp;</text></g>
  <g{o}>{rise(1.55)}<text x="254" y="122" {f} font-weight="500" font-size="80" fill="{C["ink"]}" letter-spacing="-1">Co.</text></g>
  <rect x="2" y="144" width="{0 if anim else 420}" height="3" rx="1.5" fill="{C["sage"]}">{rule}</rect>
  <g{o}>{rise(1.95)}<text x="2" y="178" font-family="Nunito, Arial, sans-serif" font-weight="700" font-size="17" letter-spacing="3.4" fill="{C["ink"]}" fill-opacity=".75">ART · WORKSHOPS · GIFTS · GALLERY</text></g>
  <g{o}>{rise(2.1)}<text x="2" y="206" font-family="Nunito, Arial, sans-serif" font-weight="700" font-size="16" letter-spacing="1.5" fill="{C["coral"]}">museandco.art</text></g>
</g>
</svg>
'''
open("muse-and-co-logo.svg", "w").write(wide(False))
open("muse-and-co-logo-animated.svg", "w").write(wide(True))
print("wide ok")
