# Sample 01: رمضان كريم · "Midnight Gilt"

| Spec | Value |
|---|---|
| Size | A1 portrait, 594 × 841 mm (3 mm bleed → 600 × 847 mm canvas) |
| Safe margin | 8 % of the short side (47.5 mm). All main text sits inside it. |
| Composition | Mix of horizontal and vertical (rotated, reading bottom→top) lines, plus two huge tone-on-tone words (رمضان / كريم) in the back layer |
| Lettering | Ruqʿah (Aref Ruqaa Bold / Regular, OFL), shaped by HarfBuzz, outlines converted to vector paths (no live text, no fonts needed to open) |
| Background | Midnight `#0F1A2B`, radial lift to `#1A2A44` at the center |
| Hero gold gradient | `#F1D592` 0% → `#D4A24C` 40% → `#A97A2C` 75% → `#7A5520` 100%, diagonal across the text block |
| Antique gold (supporting) | `#C9A25A` → `#8C6526`, vertical |
| Pale gold (highlights) | `#F3E2B0` |
| Ghost layer | `#1D2C49` |

Phrases: رمضان كريم · أهلاً رمضان · رمضان مبارك · شهر الخير · هلّ هلالُك · كل عام وأنتم بخير · صومًا مقبولًا · تقبّل الله منّا ومنكم · رمضان يجمعنا · اللهم بلّغنا رمضان

## Files
- `*_A1.svg`: true vector, with bleed
- `*_A1.pdf`: vector PDF, MediaBox 600 × 847 mm and TrimBox 594 × 841 mm (RGB)
- `*_A1_300dpi.png`: 7016 × 9933 px, 300 DPI, trimmed to A1
- `*_preview.png`: screen preview

The PDF is RGB. Convert it to CMYK with the printer's ICC profile, or ask the print shop to. For a true metallic look, print the gold as a foil layer: the SVG paths can be separated into a spot/foil plate.

Regenerate with `python3 designs/ramadan_kareem_midnight_gilt.py` (`SIZE=A2`, etc. for other A-sizes).
