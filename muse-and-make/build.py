# Generates the Muse & Make logo SVGs (static + animated).
FONT = "@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;1,9..144,400&family=Nunito:wght@700&display=swap');"
C = dict(bg="#FBF4EA", ink="#3D2C3E", coral="#E9806E", mustard="#EDB94F", sage="#97B694", lav="#B7A3D8", blue="#94C3D8", blush="#F6DCD3")

M_PATH = ("M62 168 C 64 128, 70 92, 82 72 C 92 56, 102 74, 108 98 "
          "C 113 118, 118 124, 122 108 C 128 84, 136 60, 150 58 "
          "C 166 56, 170 100, 172 136 C 173 158, 178 172, 192 168 "
          "C 202 165, 208 154, 212 144")
DOTS = [(70, 46, 11, "coral"), (104, 34, 9, "mustard"), (138, 32, 10, "sage"), (172, 42, 8, "lav")]
BLOB = ("M120 14 C 176 12, 222 50, 226 110 C 230 168, 190 222, 126 226 "
        "C 64 230, 16 192, 14 128 C 12 66, 60 16, 120 14 Z")

def sparkle(x, y, s, cls=""):
    return (f'<path class="{cls}" transform="translate({x} {y}) scale({s})" fill="{C["mustard"]}" '
            'd="M0 -10 C 1.5 -3, 3 -1.5, 10 0 C 3 1.5, 1.5 3, 0 10 C -1.5 3, -3 1.5, -10 0 C -3 -1.5, -1.5 -3, 0 -10 Z"/>')

def icon(anim):
    a = (lambda c: f' class="{c}"') if anim else (lambda c: "")
    dots = "".join(f'<circle{a("dot d%d" % i)} cx="{x}" cy="{y}" r="{r}" fill="{C[c]}"/>' for i, (x, y, r, c) in enumerate(DOTS))
    return f'''<g{a("icon")}>
  <path{a("blob")} d="{BLOB}" fill="{C["blush"]}"/>
  <circle{a("thumb")} cx="70" cy="196" r="12" fill="{C["bg"]}"/>
  {dots}
  <path{a("m")} d="{M_PATH}" pathLength="1" fill="none" stroke="{C["ink"]}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>
  {sparkle(206, 30, 1.1, "sp1" if anim else "")}{sparkle(30, 92, 0.7, "sp2" if anim else "")}
</g>'''

def wordmark(anim):
    a = (lambda c: f' class="{c}"') if anim else (lambda c: "")
    return f'''<g transform="translate(268 0)">
  <text{a("w1")} x="0" y="132" font-family="Fraunces, Georgia, serif" font-weight="500" font-size="78" fill="{C["ink"]}" letter-spacing="-1">Muse</text>
  <text{a("amp")} x="188" y="134" font-family="Fraunces, Georgia, serif" font-style="italic" font-size="84" fill="{C["coral"]}">&amp;</text>
  <text{a("w2")} x="246" y="132" font-family="Fraunces, Georgia, serif" font-weight="500" font-size="78" fill="{C["ink"]}" letter-spacing="-1">Make</text>
  <rect{a("rule")} x="2" y="156" width="430" height="3" rx="1.5" fill="{C["sage"]}"/>
  <text{a("tag")} x="2" y="190" font-family="Nunito, Arial, sans-serif" font-weight="700" font-size="17" letter-spacing="3.4" fill="{C["ink"]}" opacity=".75">ART · WORKSHOPS · GIFTS · GALLERY</text>
</g>'''

ANIM_CSS = '''
.m{stroke-dasharray:1 1;stroke-dashoffset:1;opacity:0;animation:show 0s .5s both,draw 1.6s .5s cubic-bezier(.6,0,.3,1) both}
@keyframes show{to{opacity:1}}
.blob{transform-origin:120px 120px;transform:scale(0);animation:pop .7s cubic-bezier(.3,1.5,.6,1) both}
.thumb{transform-origin:70px 196px;transform:scale(0);animation:pop .4s .4s cubic-bezier(.3,1.5,.6,1) both}
.dot{transform-box:fill-box;transform-origin:center;transform:scale(0) translateY(-30px);animation:drop .6s cubic-bezier(.3,1.6,.5,1) both}
.d0{animation-delay:1.9s}.d1{animation-delay:2.05s}.d2{animation-delay:2.2s}.d3{animation-delay:2.35s}
.sp1,.sp2{transform-box:fill-box;transform-origin:center;opacity:0;animation:twinkle 2.4s 2.6s ease-in-out infinite}
.sp2{animation-delay:3.4s}
.w1,.amp,.w2,.tag{opacity:0;animation:rise .8s cubic-bezier(.2,.8,.2,1) both}
.w1{animation-delay:1.2s}.amp{animation-delay:1.5s}.w2{animation-delay:1.8s}.tag{animation-delay:2.5s}
.amp{transform-box:fill-box;transform-origin:center}
.rule{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:grow .9s 2.2s cubic-bezier(.6,0,.2,1) both}
.icon{transform-origin:120px 120px;animation:breathe 4s 3.2s ease-in-out infinite}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes fade{to{opacity:1}}
@keyframes pop{to{transform:scale(1)}}
@keyframes drop{to{transform:scale(1) translateY(0)}}
@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes grow{to{transform:scaleX(1)}}
@keyframes twinkle{0%,100%{opacity:0;transform:scale(.4) rotate(0)}40%,60%{opacity:1;transform:scale(1) rotate(45deg)}}
@keyframes breathe{0%,100%{transform:rotate(0)}50%{transform:rotate(-2deg)}}
@media (prefers-reduced-motion:reduce){*{animation-duration:.01s!important;animation-iteration-count:1!important}}
'''

def svg(w, body, css=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 240" width="{w*2}" height="480" role="img" aria-label="Muse &amp; Make">
<title>Muse &amp; Make</title>
<style><![CDATA[{FONT}{css}]]></style>
{body}
</svg>
'''

EM_DOTS = [(86, 50, 8.5, "coral"), (108, 39, 7, "mustard"), (133, 37, 7.5, "sage"), (156, 44, 6, "lav")]

def emblem(anim):
    a = (lambda c: f' class="{c}"') if anim else (lambda c: "")
    dots = "".join(f'<circle{a("dot d%d" % i)} cx="{x}" cy="{y}" r="{r}" fill="{C[c]}"/>' for i, (x, y, r, c) in enumerate(EM_DOTS))
    f = 'font-family="Fraunces, Georgia, serif"'
    return f'''<g{a("icon")}>
  <path{a("blob")} d="{BLOB}" fill="{C["blush"]}"/>
  <circle class="{"thumb" if anim else ""}" style="transform-origin:202px 116px" cx="202" cy="116" r="10" fill="{C["bg"]}"/>
  {dots}
  <g transform="translate(118 101) scale(0.56) translate(-137 -113)">
    <path{a("m")} d="{M_PATH}" pathLength="1" fill="none" stroke="{C["ink"]}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
  <text{a("w1")} x="106" y="182" text-anchor="end" {f} font-weight="500" font-size="27" fill="{C["ink"]}">Muse</text>
  <text{a("amp")} x="120" y="183" text-anchor="middle" {f} font-style="italic" font-size="29" fill="{C["coral"]}">&amp;</text>
  <text{a("w2")} x="133" y="182" {f} font-weight="500" font-size="27" fill="{C["ink"]}">Make</text>
  <rect{a("rule")} x="92" y="195" width="56" height="2.4" rx="1.2" fill="{C["sage"]}"/>
  {sparkle(206, 30, 1.1, "sp1" if anim else "")}{sparkle(30, 92, 0.7, "sp2" if anim else "")}
</g>'''

open("muse-and-make-emblem.svg", "w").write(svg(240, emblem(False)))
open("muse-and-make-emblem-animated.svg", "w").write(svg(240, emblem(True), ANIM_CSS))
open("muse-and-make-logo.svg", "w").write(svg(720, icon(False) + wordmark(False)))
open("muse-and-make-icon.svg", "w").write(svg(240, icon(False)))
open("muse-and-make-logo-animated.svg", "w").write(svg(720, icon(True) + wordmark(True), ANIM_CSS))
print("ok")
