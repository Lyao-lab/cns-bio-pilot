#!/usr/bin/env python
"""deck_gate.py — programmatic acceptance gate for a built pptx (playbook §4).

Covers the three checks edge_sweep.py does not: per-slide panel geometry,
embed-integrity (embedded bytes == shrink-of-source chain), and speaker-note
structure. All return explicit PASS/FAIL and a nonzero exit on any failure.

Usage:
  python deck_gate.py deck.pptx \
      --expected '{3:3, 4:1}'           # 1-based slide -> expected picture count
      [--bounds 0.4,12.95,1.0,6.87]     # allowed content box (inches)
      [--embed-map '{"p3": "src.png"}']  # slide->source PNG for md5 chain check
      [--notes-block 方法,意义]          # required notes markers
Exit 0 = all checks pass.
"""
import argparse
import hashlib
import json
import sys
import glob

from pptx import Presentation

EMU_IN = 914400.0


def shp_rect(sh):
    return (sh.left / EMU_IN, sh.top / EMU_IN,
            (sh.left + sh.width) / EMU_IN, (sh.top + sh.height) / EMU_IN)


def check_geometry(prs, expected, bounds):
    fails = []
    x0_, x1_, y0_, y1_ = bounds
    for pg, n_exp in expected.items():
        sl = list(prs.slides)[pg - 1]
        pics = [sh for sh in sl.shapes if sh.shape_type == 13]
        if len(pics) != n_exp:
            fails.append(f'p{pg}: {len(pics)} pics, expected {n_exp}')
            continue
        for r in (shp_rect(sh) for sh in pics):
            if not (x0_ - 0.05 <= r[0] and r[2] <= x1_ + 0.05
                    and y0_ - 0.05 <= r[1] and r[3] <= y1_ + 0.05):
                fails.append(f'p{pg}: pic out of bounds {[round(v,2) for v in r]}')
        for i, a in enumerate(pics):
            ra = shp_rect(a)
            for b in pics[i + 1:]:
                rb = shp_rect(b)
                if not (ra[2] <= rb[0] + 0.01 or rb[2] <= ra[0] + 0.01
                        or ra[3] <= rb[1] + 0.01 or rb[3] <= ra[1] + 0.01):
                    fails.append(f'p{pg}: two pictures overlap')
    return fails


def check_embed(prs, embed_map, cache_dir, max_px_tag='1600'):
    """Embedded image on slide pg must equal the shrink-cache file derived
    from the given source (content-hash-keyed cache naming)."""
    from PIL import Image
    fails = []
    for pg, src in embed_map.items():
        sl = list(prs.slides)[pg - 1]
        emb = {hashlib.md5(sh.image.blob).hexdigest()
               for sh in sl.shapes if sh.shape_type == 13}
        key = hashlib.md5(open(src, 'rb').read()).hexdigest()[:12]
        stem = src.split('/')[-1].rsplit('.', 1)[0]
        cands = glob.glob(f'{cache_dir}/{stem}_{max_px_tag}_{key}.png')
        if not cands:
            fails.append(f'p{pg}: no cache file for {stem} key {key}')
            continue
        if not any(hashlib.md5(open(c, 'rb').read()).hexdigest() in emb
                   for c in cands):
            fails.append(f'p{pg}: embed md5 != shrink-of-source chain')
    return fails


def check_notes(prs, markers):
    fails = []
    for i, sl in enumerate(prs.slides, 1):
        nts = sl.notes_slide.notes_text_frame.text if sl.has_notes_slide else ''
        for m in markers:
            if m not in nts:
                fails.append(f'p{i}: notes missing {m}')
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('deck')
    ap.add_argument('--expected', default='{}')
    ap.add_argument('--bounds', default='0.4,12.95,1.0,6.87')
    ap.add_argument('--embed-map', default='{}')
    ap.add_argument('--cache-dir', default='/tmp/pptx_imgs_20260918')
    ap.add_argument('--max-px-tag', default='1600')
    ap.add_argument('--notes-block', default='')
    a = ap.parse_args()
    prs = Presentation(a.deck)
    expected = {int(k): v for k, v in json.loads(a.expected).items()}
    embed_map = {int(k): v for k, v in json.loads(a.embed_map).items()}
    bounds = [float(x) for x in a.bounds.split(',')]
    markers = [m for m in a.notes_block.split(',') if m]
    fails = (check_geometry(prs, expected, bounds)
             + check_embed(prs, embed_map, a.cache_dir, a.max_px_tag)
             + check_notes(prs, markers))
    print(f'deck_gate: {"FAIL" if fails else "PASS"} ({len(fails)} issues)')
    for f_ in fails:
        print('  -', f_)
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
