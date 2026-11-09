"""
Square Kufic letterforms transcribed from the F.o.K.S. Kufic Font Chart
(Friends of Kufi Square; chart by Muhammad Sobirin Abdul Hamid, redesigned by Uzaini Amir),
supplied by the client as the reference alphabet.

Only letters that have been transcribed and checked against the chart are listed.
Each glyph: rows top→bottom, '#' ink, 'o' dot, '.' empty; `base` = index of the baseline row
(rows after it are below the baseline). Joins happen on the baseline row.
Tall letters (ا ل) are generated at the line's ascender height.
"""

def _G(rows, base=None):
    w = max(len(r) for r in rows)
    rows = [r.ljust(w, ".") for r in rows]
    return {"rows": rows, "base": len(rows) - 1 if base is None else base}

def tall(h):
    return _G(["#"] * h)

GLYPHS = {
    # ب ت ث ن ي family --------------------------------------------------
    ("ت", "F"): _G(["#.o.o.#", "#.....#", "#######"]),      # cup, two dots inside
    ("ت", "I"): _G(["#.o.o.#", "#.....#", "#######"]),
    ("ي", "M"): _G(["..#..", "..#..", "#####", ".....", ".o.o."], base=2),   # tooth, two dots below
    ("ي", "N"): _G(["..#..", "..#..", "###..", ".....", ".o.o."], base=2),
    ("ب", "M"): _G([".#.", ".#.", "###", "...", ".o."], base=2),
    ("ب", "N"): _G([".#.", ".#.", "##.", "...", ".o."], base=2),
    ("ن", "M"): _G([".o.", "...", ".#.", ".#.", "###"]),
    ("ن", "N"): _G([".o.", "...", ".#.", ".#.", "##."]),
    # س ----------------------------------------------------------------
    ("س", "M"): _G(["#.#.#", "#.#.#", "#####"]),             # three teeth
    ("س", "N"): _G(["#.#.#", "#.#.#", "#####"]),
    # و ف ق --------------------------------------------------------------
    ("و", "F"): _G(["###", "#.#", "###", "..#", "###"]),     # loop on a stem, flat foot
    ("و", "I"): _G(["###", "#.#", "###", "..#", "###"]),
    ("ق", "N"): _G(["o.o", "...", "###", "#.#", "###", "..#", "###"]),
    ("ق", "M"): _G(["o.o", "...", "###", "#.#", "###", "..#", "###"]),
    ("ف", "N"): _G([".o.", "...", "###", "#.#", "###", "..#", "###"]),
    ("ف", "M"): _G([".o.", "...", "###", "#.#", "###", "..#", "###"]),
    ("ف", "F"): _G(["...o.", ".....", "..###", "..#.#", "#.###", "#...#", "#####"]),  # bowl + raised loop
    # ك ------------------------------------------------------------------
    ("ك", "N"): _G(["###.#", "#...#", "###.#", "....#", "#####"]),   # tall stem, inner hook
    ("ك", "M"): _G(["###.#", "#...#", "###.#", "....#", "#####"]),
    # م ه د ------------------------------------------------------------------
    ("م", "N"): _G(["###", "#.#", "###"]),
    ("م", "M"): _G(["###", "#.#", "###"]),
    ("ه", "M"): _G(["###", "#.#", "###", "#.#", "###"]),
    ("ه", "F"): _G(["###", "#..", "###", "#.#", "###"]),     # top flag + loop
    ("د", "F"): _G(["###", "..#", "#.#", "###"]),
    ("د", "I"): _G(["###", "..#", "#.#", "###"]),
}

NON_JOINING = set("ادذرزوة")

# letters whose correct anatomy has a detached stroke (not a dot)
PIECES = {"ك": 2}   # inner hook of kaf is drawn separately, as in the chart

def forms(word):
    out = []
    for i, c in enumerate(word):
        pj = i > 0 and word[i - 1] not in NON_JOINING
        nj = i < len(word) - 1 and c not in NON_JOINING
        out.append((c, {(0, 0): "I", (0, 1): "N", (1, 1): "M", (1, 0): "F"}[(pj, nj)]))
    return out

def glyph(ch, form, tall_h):
    if ch == "ا" or (ch == "ل" and form in "NM"):
        return tall(tall_h)
    return GLYPHS[(ch, form)]
