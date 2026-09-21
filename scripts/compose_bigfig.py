"""compose_bigfig.py — sectioned big-figure composer (E1/E6).

Assembles per-panel PNGs into one labelled big figure: lettered section
header bands, per-row uniform heights with gap-aware row width
((W − gaps)/Σar — gap-omission is the #1 edge-clip cause), optional
max_row_h caps, white outer margin, PNG + vector PDF twins.

Usage: python compose_bigfig.py sections.json outdir
sections.json = [["Section I. Title", ["panelA.png", "panelB.png"]], ...]
Panel paths may be absolute or relative to sections.json's directory.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import matplotlib

Image.MAX_IMAGE_PIXELS = None

W_IN, GAP_IN, HDR_IN, DPI, MARGIN_IN = 18.0, 0.18, 0.42, 300, 0.15
FDIR = matplotlib.get_data_path() + '/fonts/ttf/'
f_hdr = ImageFont.truetype(FDIR + 'DejaVuSans-Bold.ttf', 78)


def compose(sections, out_png, w_in=W_IN, gap_in=GAP_IN, hdr_in=HDR_IN,
            margin_in=MARGIN_IN, dpi=DPI, max_row_h=None):
    max_row_h = max_row_h or {}
    rows = []
    for title, names in sections:
        rows.append([Image.open(p).convert('RGB') for p in names])
    heights = []
    for ri, ims in enumerate(rows):
        ars = [im.width / im.height for im in ims]
        # gaps inside the row must be paid for from the row budget
        h = (w_in - gap_in * (len(ims) - 1)) / sum(ars)
        heights.append(min(h, max_row_h.get(ri, 99)))
    total = sum(heights) + hdr_in * len(rows) + gap_in * (len(rows) - 1)
    canvas = Image.new('RGB',
                       (round((w_in + 2 * margin_in) * dpi),
                        round((total + 2 * margin_in) * dpi)), 'white')
    draw = ImageDraw.Draw(canvas)
    y = 0.0
    for title, ims, h in zip([s[0] for s in sections], rows, heights):
        draw.text((round(margin_in * dpi) + 30, round((y + margin_in) * dpi) + 18),
                  title, font=f_hdr, fill='#1F3A5F')
        y += hdr_in
        ars = [im.width / im.height for im in ims]
        block_w = h * sum(ars) + gap_in * (len(ims) - 1)
        x = (w_in - block_w) / 2
        for im, a in zip(ims, ars):
            w = h * a
            canvas.paste(im.resize((round(w * dpi), round(h * dpi)),
                                   Image.LANCZOS),
                         (round((x + margin_in) * dpi),
                          round((y + margin_in) * dpi)))
            x += w + gap_in
        y += h + gap_in
    out_png = Path(out_png)
    canvas.save(out_png, 'PNG', optimize=True)
    canvas.save(out_png.with_suffix('.pdf'), 'PDF', resolution=dpi)
    print(f'bigfig: {canvas.size[0]}x{canvas.size[1]} px '
          f'({w_in + 2 * margin_in:.1f}x{total + 2 * margin_in:.1f} in)')


def main():
    spec = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    base = Path(sys.argv[1]).parent
    sections = [[t, [str((base / n) if not Path(n).is_absolute()
                         else Path(n)) for n in names]] for t, names in spec]
    compose(sections, sys.argv[2])


if __name__ == '__main__':
    main()
