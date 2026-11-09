"""Render a verified letter list: artwork, letter check, one-colour proof, small-size proof, reading path."""
import os

PAL = ["#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#e07b00", "#17becf",
       "#e377c2", "#8c564b", "#bcbd22", "#7f7f7f", "#d62728", "#1f77b4"]


def svg(letters, W, H, title, ink, dot, paper, U=50, gap=2, border=1, mat=3,
        mode="art", frame_ink=None, inner_border=0):
    off = mat + border + gap + (inner_border + 1 if inner_border else 0)
    TW, TH = (W + 2 * off) * U, (H + 2 * off) * U
    p = [f'<rect width="{TW}" height="{TH}" fill="{paper}"/>']
    fi = frame_ink or ink
    def ring(o, t, w, h):
        return (f'<path fill="{fi}" fill-rule="evenodd" d="M{o} {o}h{w}v{h}h{-w}z'
                f'M{o+t} {o+t}v{h-2*t}h{w-2*t}v{-(h-2*t)}z"/>')
    o = mat * U
    fw, fh = TW - 2 * o, TH - 2 * o
    p.append(ring(o, border * U, fw, fh))
    if inner_border:
        o2 = o + (border + 1) * U
        p.append(ring(o2, inner_border * U, TW - 2 * o2, TH - 2 * o2))
    cell = lambda cs, col: f'<path fill="{col}" d="' + "".join(
        f"M{(c+off)*U} {(r+off)*U}h{U}v{U}h{-U}z" for r, c in cs) + '"/>'
    p.append(cell([c for l in letters for c in l["ink"]], ink))
    p.append(cell([c for l in letters for c in l["dots"]], ink if mode == "mono" else dot))
    def bbox(l):
        cs = l["ink"] | l["dots"]
        return (min(r for r, c in cs), max(r for r, c in cs), min(c for r, c in cs), max(c for r, c in cs))
    if mode == "check":
        for i, l in enumerate(letters):
            r0, r1, c0, c1 = bbox(l); col = PAL[i % len(PAL)]
            p.append(f'<rect x="{(c0+off)*U+5}" y="{(r0+off)*U+5}" width="{(c1-c0+1)*U-10}" height="{(r1-r0+1)*U-10}" '
                     f'fill="none" stroke="{col}" stroke-width="6" stroke-dasharray="14 8"/>')
            p.append(f'<text x="{(c1+1+off)*U-4}" y="{(r0+off)*U-10}" font-size="40" font-family="Amiri" '
                     f'text-anchor="end" fill="{col}">{i+1} {l["ch"]}</text>')
    if mode == "path":
        pts = []
        for l in letters:
            body = [c for c in l["ink"] if c not in l.get("conn", set())] or list(l["ink"])
            r = sum(a for a, b in body) / len(body); c = sum(b for a, b in body) / len(body)
            pts.append(((c + off + .5) * U, (r + off + .5) * U))
        p.append('<defs><marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" '
                 'orient="auto"><path d="M0 0L10 5L0 10z" fill="#E0115F"/></marker></defs>')
        for i in range(len(pts) - 1):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            p.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="#E0115F" stroke-width="7" '
                     f'marker-end="url(#a)" opacity=".9"/>')
        for i, (x, y) in enumerate(pts):
            p.append(f'<circle cx="{x}" cy="{y}" r="26" fill="#E0115F"/><text x="{x}" y="{y+12}" font-size="32" '
                     f'font-family="Amiri" text-anchor="middle" fill="#fff">{i+1}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TW} {TH}" width="{TW}" height="{TH}" '
            f'shape-rendering="crispEdges"><title>{title}</title>{"".join(p)}</svg>')


def export_all(letters, W, H, title, stem, outdir, **kw):
    import cairosvg
    from PIL import Image
    os.makedirs(outdir, exist_ok=True)
    files = {}
    for mode, suffix, width in (("art", "", 1600), ("check", "_letter-check", 1600),
                                ("mono", "_one-colour", 1600), ("path", "_reading-path", 1600)):
        s = svg(letters, W, H, title, mode=mode, **kw)
        base = os.path.join(outdir, stem + suffix)
        open(base + ".svg", "w", encoding="utf-8").write(s)
        cairosvg.svg2png(bytestring=s.encode(), write_to=base + ".png", output_width=width)
        files[mode] = base + ".png"
    # small-size proof: ~3 cm wide at 96 dpi (~113 px), shown 1:1 on a white card
    s = svg(letters, W, H, title, mode="art", **kw)
    small = os.path.join(outdir, stem + "_small-size.png")
    cairosvg.svg2png(bytestring=s.encode(), write_to=small, output_width=113)
    files["small"] = small
    # proof sheet
    ims = [Image.open(files[m]).convert("RGB") for m in ("art", "check", "mono", "path")]
    for im in ims: im.thumbnail((800, 800))
    sm = Image.open(small).convert("RGB")
    w = sum(i.width for i in ims[:2]) + 30; h = ims[0].height + ims[2].height + 30
    sheet = Image.new("RGB", (w + sm.width + 40, h), "#DDDDDD")
    sheet.paste(ims[0], (0, 0)); sheet.paste(ims[1], (ims[0].width + 30, 0))
    sheet.paste(ims[2], (0, ims[0].height + 30)); sheet.paste(ims[3], (ims[2].width + 30, ims[0].height + 30))
    sheet.paste(sm, (w + 20, 20))
    sheet.save(os.path.join(outdir, stem + "_proof-sheet.png"))
    return files
