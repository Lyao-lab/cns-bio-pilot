"""Transcript → cell mask assignment (canonical example).

Reference: cellpose 3.0+ | numpy 1.26+ | pandas 2.2+ | Verify API if version differs
Data assumption: a transcript-level DataFrame `transcripts` with x/y pixel columns
                 AND a nuclear/cell stain image for cellpose segmentation
                 (OR a precomputed mask array for Option C).

Goal: for platforms that output individual transcripts (MERFISH / Xenium raw /
      Stereo-seq), assign each transcript to the cell whose mask contains its (x,y).
"""
import numpy as np
import pandas as pd
from cellpose import models

# ---------------------------------------------------------------------------
# Option A: cellpose on a paired image (needs H&E / DAPI / IF)
# ---------------------------------------------------------------------------
model = models.Cellpose(model_type='cyto2')   # or 'nuclei' for nuclear-only
masks, flows, styles, diams = model.eval(image, diameter=30, channels=[0, 0])
# masks: HxW int array, 0=background, 1..N=label per cell

# Assign each transcript to the cell whose mask contains its (x, y)
transcripts['cell_id'] = masks[transcripts.y.astype(int), transcripts.x.astype(int)]
assigned = transcripts[transcripts['cell_id'] > 0]
print(f'Assigned: {len(assigned)}/{len(transcripts)} ({len(assigned)/len(transcripts):.1%})')

# ---------------------------------------------------------------------------
# Option B: Baysor (no image — segments from transcript density alone)
# ---------------------------------------------------------------------------
# Run externally: baysor run -c config.toml   (CLI; outputs cell_ids per transcript)
# Then read the Baysor-assigned cell × gene matrix:
# import scanpy as sc
# adata = sc.read_h5ad('baysor_cell_by_gene.h5ad')

# ---------------------------------------------------------------------------
# Option C: aggregate when a cell_id column already exists (Xenium default)
# ---------------------------------------------------------------------------
# Xenium output ships 'cell_id' per transcript — just group:
if 'cell_id' in transcripts.columns:
    cell_by_gene = transcripts.groupby(['cell_id', 'gene']).size().unstack(fill_value=0)
    print(f'Cells: {cell_by_gene.shape[0]}, Mean transcripts/cell: {cell_by_gene.sum(axis=1).mean():.0f}')
