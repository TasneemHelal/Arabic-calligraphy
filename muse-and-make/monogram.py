# Muse & Make monogram: brush-drawn M · & · M inside the palette, drawn one after another.
from build import C, BLOB, M_PATH, sparkle, svg, FONT

AMP = "M 36 58 L 13 27 C 5 15, 10 4, 19 4 C 28 4, 31 13, 24 22 L 9 39 C 1 49, 6 59, 17 59 C 27 59, 33 51, 38 41"
N   = "M 6 58 L 6 30 C 6 16, 33 12, 33 30 L 33 58"
DOTS = [(76, 64, 8, "coral"), (104, 54, 6.5, "mustard"), (136, 54, 7, "sage"), (164, 64, 5.5, "lav")]

def mono(mid, anim):
    a = (lambda c: f' class="{c}"') if anim else (lambda c: "")
    dots = "".join(f'<circle{a("dot d%d" % i)} cx="{x}" cy="{y}" r="{r}" fill="{C[c]}"/>' for i, (x, y, r, c) in enumerate(DOTS))
    stroke = f'fill="none" stroke-linecap="round" stroke-linejoin="round" pathLength="1"'
    midpath = AMP if mid == "amp" else N
    mt = "translate(120 126) scale(0.74) translate(-22 -31)" if mid == "amp" else "translate(120 132) scale(0.62) translate(-19.5 -37)"
    mw = 10 if mid == "amp" else 12
    return f'''<g{a("icon")}>
  <path{a("blob")} d="{BLOB}" fill="{C["blush"]}"/>
  <circle{a("thumb")} cx="120" cy="196" r="10" fill="{C["bg"]}"/>
  {dots}
  <g transform="translate(66 124) scale(0.4) translate(-137 -113)"><path{a("s1")} d="{M_PATH}" stroke="{C["ink"]}" stroke-width="20" {stroke}/></g>
  <g transform="{mt}"><path{a("s2")} d="{midpath}" stroke="{C["coral"]}" stroke-width="{mw}" {stroke}/></g>
  <g transform="translate(174 124) scale(0.4) translate(-137 -113)"><path{a("s3")} d="{M_PATH}" stroke="{C["ink"]}" stroke-width="20" {stroke}/></g>
  {sparkle(206, 30, 1.1, "sp1" if anim else "")}{sparkle(30, 92, 0.7, "sp2" if anim else "")}
</g>'''

CSS = '''
.s1,.s2,.s3{stroke-dasharray:1 1;stroke-dashoffset:1;opacity:0}
.s1{animation:show 0s .6s both,draw 1.1s .6s cubic-bezier(.6,0,.3,1) both}
.s2{animation:show 0s 1.8s both,draw .8s 1.8s cubic-bezier(.6,0,.3,1) both}
.s3{animation:show 0s 2.7s both,draw 1.1s 2.7s cubic-bezier(.6,0,.3,1) both}
.blob{transform-origin:120px 120px;transform:scale(0);animation:pop .7s cubic-bezier(.3,1.5,.6,1) both}
.thumb{transform-box:fill-box;transform-origin:center;animation:pop .4s .4s cubic-bezier(.3,1.5,.6,1) both}
.dot{transform-box:fill-box;transform-origin:center;animation:drop .6s cubic-bezier(.3,1.6,.5,1) both}
.d0{animation-delay:3.7s}.d1{animation-delay:3.85s}.d2{animation-delay:4s}.d3{animation-delay:4.15s}
.sp1,.sp2{transform-box:fill-box;transform-origin:center;opacity:0;animation:twinkle 2.4s 4.3s ease-in-out infinite}
.sp2{animation-delay:5.1s}
.icon{transform-origin:120px 120px;animation:breathe 4s 4.8s ease-in-out infinite}
@keyframes show{to{opacity:1}}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes pop{from{transform:scale(0)}to{transform:scale(1)}}
@keyframes drop{from{transform:scale(0) translateY(-30px)}to{transform:scale(1) translateY(0)}}
@keyframes twinkle{0%,100%{opacity:0;transform:scale(.4) rotate(0)}40%,60%{opacity:1;transform:scale(1) rotate(45deg)}}
@keyframes breathe{0%,100%{transform:rotate(0)}50%{transform:rotate(-2deg)}}
@media (prefers-reduced-motion:reduce){*{animation-duration:.01s!important;animation-delay:0s!important;animation-iteration-count:1!important}}
'''

for mid, name in [("amp", "muse-and-make-monogram"), ("n", "muse-and-make-monogram-n")]:
    open(f"{name}.svg", "w").write(svg(240, mono(mid, False)))
    open(f"{name}-animated.svg", "w").write(svg(240, mono(mid, True), CSS))
print("ok")
