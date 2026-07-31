#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
figure-production assembly — compose pre-rendered panels into a composite.

Usage:
    python main.py --input A.png B.png C.png D.png --output figure1.png
    python main.py --input panels/*.png --output figure1.pdf --layout 2x3 --dpi 300
    python main.py --input A.png B.png C.png --output fig.pdf --label-size 14

Rules:
- Input = pre-rendered, pre-verified panel files (PNG/JPG/TIFF; PDF via pdf2image)
- Assembly only does LAYOUT (labels, spacing, output) — does NOT modify panel content
- Preserves each panel's aspect ratio (no forced resize)
- Supports any N panels (not fixed at 6)
"""
import argparse
import math
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. pip install Pillow")
    sys.exit(1)

import matplotlib.pyplot as plt
import numpy as np


def load_image(path):
    """Load image as numpy array. PNG/JPG/TIFF native; PDF via pdf2image."""
    path = Path(path)
    if path.suffix.lower() == '.pdf':
        try:
            from pdf2image import convert_from_path
            pages = convert_from_path(str(path), dpi=300)
            if pages:
                return np.array(pages[0])
        except ImportError:
            print(f"WARNING: pdf2image not installed, cannot read {path}. "
                  f"Export as PNG, or: pip install pdf2image")
            return None
    try:
        img = Image.open(path)
        return np.array(img.convert('RGBA' if img.mode == 'RGBA' else 'RGB'))
    except Exception as e:
        print(f"ERROR: cannot read {path}: {e}")
        return None


def compute_layout(n, layout_str=None):
    """Compute (nrows, ncols). Prefer wider than tall."""
    if layout_str:
        parts = layout_str.lower().split('x')
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
    ncols = math.ceil(math.sqrt(n * 1.5))
    nrows = math.ceil(n / ncols)
    return nrows, ncols


def assemble(inputs, output, layout=None, dpi=300, label_size=12,
             label_bold=True, padding=0.02, bg_color='white'):
    """Assemble N panels into composite. Preserves aspect ratio — no forced resize."""
    images = []
    for path in inputs:
        img = load_image(path)
        if img is None:
            continue
        images.append((Path(path).stem, img))

    n = len(images)
    if n == 0:
        print("ERROR: no valid images loaded")
        return False

    nrows, ncols = compute_layout(n, layout)

    # Figure size from median aspect ratio
    aspects = [img.shape[1] / img.shape[0] for _, img in images]
    median_aspect = np.median(aspects)
    cell_w = 3.5
    cell_h = cell_w / median_aspect
    fig_w = ncols * cell_w * (1 + padding)
    fig_h = nrows * cell_h * (1 + padding)

    fig, axes = plt.subplots(nrows, ncols, figsize=(fig_w, fig_h))
    fig.patch.set_facecolor(bg_color)

    if nrows == 1 and ncols == 1:
        axes_flat = [axes]
    else:
        axes_flat = axes.flatten() if hasattr(axes, 'flatten') else [axes]

    labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for i, (name, img) in enumerate(images):
        ax = axes_flat[i]
        ax.imshow(img)
        ax.set_axis_off()
        if i < len(labels):
            ax.text(0.02, 0.98, labels[i], transform=ax.transAxes,
                    fontsize=label_size,
                    fontweight='bold' if label_bold else 'normal',
                    va='top', ha='left', color='#2E3440', fontfamily='Arial')

    for j in range(n, len(axes_flat)):
        axes_flat[j].set_axis_off()

    plt.subplots_adjust(wspace=padding, hspace=padding,
                        left=0.01, right=0.99, top=0.99, bottom=0.01)

    fig.savefig(str(output), dpi=dpi, bbox_inches='tight',
                pad_inches=0.05, facecolor=bg_color)
    plt.close(fig)
    print(f"Saved: {output} ({n} panels, {nrows}x{ncols}, {dpi} DPI)")
    return True


def main():
    ap = argparse.ArgumentParser(description="Assemble pre-rendered panels into composite")
    ap.add_argument("--input", nargs='+', required=True, help="Panel files (PNG/JPG/TIFF/PDF)")
    ap.add_argument("--output", required=True, help="Output path")
    ap.add_argument("--layout", default=None, help="'2x3'/'3x2' etc (auto if omitted)")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--label-size", type=int, default=12)
    ap.add_argument("--label-bold", action="store_true", default=True)
    ap.add_argument("--no-label-bold", dest="label_bold", action="store_false")
    ap.add_argument("--padding", type=float, default=0.02)
    args = ap.parse_args()

    ok = assemble(args.input, args.output, args.layout, args.dpi,
                  args.label_size, args.label_bold, args.padding)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
