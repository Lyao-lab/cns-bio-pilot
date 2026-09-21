#!/usr/bin/env python
"""render_slides.py — faithful pptx -> PNG previews (E3, E5 input).

Renders each slide from the pptx geometry with true point sizes,
paragraph-level font-size fallback, text wrapping at the TEXTBOX width
(PIL-measured, Bold/Oblique/BoldOblique families), italic captions in grey.
Font-size inflation (fs*100/72) or canvas-edge wrapping manufactures
phantom caption clipping — this renderer exists to prevent that.

Usage: python render_slides.py deck.pptx /tmp/preview_dir
Output: <dir>/slide_NN.png (100 dpi).
"""
import io
import os
import sys

from PIL import Image, ImageFont
from pptx import Presentation
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

_FDIR = matplotlib.get_data_path() + '/fonts/ttf/'
_FONTS = {}
SCALE = 10


def _font(px, italic, bold=False):
    key = (px, italic, bold)
    if key not in _FONTS:
        name = ('DejaVuSans-BoldOblique.ttf' if italic else
                'DejaVuSans-Bold.ttf') if bold else (
            'DejaVuSans-Oblique.ttf' if italic else 'DejaVuSans.ttf')
        _FONTS[key] = ImageFont.truetype(_FDIR + name, max(int(px), 1))
    return _FONTS[key]


def wrap_box(text, fs, w_in, italic, bold=False):
    f = _font(fs * SCALE, italic, bold)
    limit = w_in * 72 * SCALE
    lines, cur = [], ''
    for tok in text.split():
        cand = tok if not cur else cur + ' ' + tok
        if f.getlength(cand) <= limit or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = tok
    lines.append(cur)
    return '\n'.join(lines)


def main():
    pptx = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else '/tmp/ppt_png_v2'
    os.makedirs(out, exist_ok=True)
    prs = Presentation(pptx)
    EMU_IN = 914400.0
    W = prs.slide_width / EMU_IN
    H = prs.slide_height / EMU_IN
    for i, slide in enumerate(prs.slides):
        fig = plt.figure(figsize=(W, H), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, W)
        ax.set_ylim(0, H)
        ax.axis('off')
        fig.patch.set_facecolor('white')
        for shp in slide.shapes:
            x = shp.left / EMU_IN
            y = shp.top / EMU_IN
            w = shp.width / EMU_IN
            h = shp.height / EMU_IN
            if shp.shape_type == 13 or shp.__class__.__name__ == 'Picture':
                img = Image.open(io.BytesIO(shp.image.blob))
                ax.imshow(img, extent=(x, x + w, H - (y + h), H - y),
                          aspect='auto', interpolation='bilinear', zorder=2)
            elif shp.has_text_frame:
                txt = shp.text_frame.text.strip()
                if not txt:
                    continue
                sizes = [r.font.size.pt for p in shp.text_frame.paragraphs
                         for r in p.runs if r.font.size]
                psizes = [p.font.size.pt for p in shp.text_frame.paragraphs
                          if p.font.size]
                fs = max(sizes + psizes) if (sizes or psizes) else 12
                italic = any(p.font.italic for p in shp.text_frame.paragraphs)
                color, bold = '#1F3A5F', False
                for p in shp.text_frame.paragraphs:
                    bold = bold or bool(p.font.bold)
                    try:
                        if p.font.color and p.font.color.rgb:
                            color = '#' + str(p.font.color.rgb)
                    except Exception:
                        pass
                wrapped = wrap_box(txt, fs, max(w - 0.04, 0.5), italic, bold)
                ax.text(x + 0.02, H - y - 0.02, wrapped, fontsize=fs,
                        ha='left', va='top', zorder=3,
                        fontweight='bold' if bold else 'normal', color=color,
                        linespacing=1.3)
        fig.savefig(f'{out}/slide_{i + 1:02d}.png', dpi=100)
        plt.close(fig)
    print('done ->', out)


if __name__ == '__main__':
    main()
