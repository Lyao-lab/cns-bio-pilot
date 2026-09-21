#!/usr/bin/env python
"""edge_sweep.py — pixel-level clipping gate for rendered slide previews.

Scans rendered slide PNGs for text touching the slide border (bottom/right/
top). Font-level QA (font size, box overlap) cannot detect captions clipped
by the slide edge; this is the E5 check made executable.

Usage:
  python edge_sweep.py <render_dir>          # scans *.png in dir
  python edge_sweep.py <render_dir> --thresh 0.01

Exit 0 = all clean; 1 = at least one page flagged.
"""
import sys
import argparse
import glob

import numpy as np
from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('render_dir')
    ap.add_argument('--thresh', type=float, default=0.01,
                    help='dark-pixel fraction that flags an edge')
    a = ap.parse_args()
    flagged = []
    for p in sorted(glob.glob(f'{a.render_dir}/*.png')):
        img = np.asarray(Image.open(p).convert('L'))
        bot = (img[-4:, :] < 120).mean()
        rgt = (img[:, -6:] < 120).mean()
        top = (img[:4, :] < 120).mean()
        if bot > a.thresh or rgt > a.thresh or top > a.thresh:
            flagged.append((p.split('/')[-1], round(float(bot), 3),
                            round(float(rgt), 3), round(float(top), 3)))
    for name, b, r, t in flagged:
        print(f'CLIP {name}: bottom={b} right={r} top={t}')
    print('edge_sweep:', 'FAIL' if flagged else 'PASS',
          f'({len(flagged)} flagged)')
    sys.exit(1 if flagged else 0)


if __name__ == '__main__':
    main()
