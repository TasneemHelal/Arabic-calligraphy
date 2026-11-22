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
.s1,.s2,.s3{stroke-dasharray:1 1;stroke-dashoffset:1;opacity:0;transform-box:fill-box;transform-origin:50% 100%}
.s1{animation:show 0s .3s both,draw .38s .3s cubic-bezier(.5,0,.2,1) both,boing .45s .68s cubic-bezier(.3,1.8,.5,1)}
.s2{animation:show 0s .62s both,draw .26s .62s cubic-bezier(.5,0,.2,1) both,boing .45s .88s cubic-bezier(.3,1.8,.5,1)}
.s3{animation:show 0s .84s both,draw .38s .84s cubic-bezier(.5,0,.2,1) both,boing .45s 1.22s cubic-bezier(.3,1.8,.5,1)}
.blob{transform-origin:120px 120px;animation:spinpop .5s cubic-bezier(.3,1.6,.5,1) both}
.thumb{transform-box:fill-box;transform-origin:center;animation:pop .3s .25s cubic-bezier(.3,1.8,.5,1) both}
.dot{transform-box:fill-box;transform-origin:center;animation:drop .38s cubic-bezier(.3,1.9,.5,1) both}
.d0{animation-delay:1.25s}.d1{animation-delay:1.32s}.d2{animation-delay:1.39s}.d3{animation-delay:1.46s}
.sp1,.sp2{transform-box:fill-box;transform-origin:center;opacity:0;animation:twinkle 1.4s 1.5s ease-in-out infinite}
.sp2{animation-delay:1.9s}
.icon{transform-origin:120px 200px;animation:jump .55s 1.55s cubic-bezier(.3,1.5,.5,1),wiggle 2.2s 2.2s ease-in-out infinite}
@keyframes show{to{opacity:1}}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes pop{from{transform:scale(0)}to{transform:scale(1)}}
@keyframes spinpop{from{transform:scale(0) rotate(-35deg)}to{transform:scale(1) rotate(0)}}
@keyframes boing{0%{transform:none}30%{transform:scale(1.18,.82)}60%{transform:scale(.92,1.12) translateY(-4px)}100%{transform:none}}
@keyframes drop{from{transform:scale(0) translateY(-40px)}to{transform:scale(1) translateY(0)}}
@keyframes jump{0%,100%{transform:none}40%{transform:translateY(-8px) scale(1.04,.97)}}
@keyframes twinkle{0%,100%{opacity:0;transform:scale(.3) rotate(0)}40%,60%{opacity:1;transform:scale(1.15) rotate(90deg)}}
@keyframes wiggle{0%,100%{transform:rotate(0)}25%{transform:rotate(-3deg)}75%{transform:rotate(3deg)}}
@media (prefers-reduced-motion:reduce){*{animation-duration:.01s!important;animation-delay:0s!important;animation-iteration-count:1!important}}
'''

for mid, name in [("amp", "muse-and-make-monogram"), ("n", "muse-and-make-monogram-n")]:
    open(f"{name}.svg", "w").write(svg(240, mono(mid, False)))
    open(f"{name}-animated.svg", "w").write(svg(240, mono(mid, True), CSS))
print("ok")
