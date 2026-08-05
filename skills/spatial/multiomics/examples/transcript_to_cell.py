"""Transcript → cell mask assignment (canonical example).

Env:        any env with numpy/pandas (sc or st); cellpose needs its own install
Packages: see compat.yaml for versions. Verify API with inspect.signature before first use.

Install (cellpose is NOT auto-installed in sc/st):
  conda activate sc && pip install cellpose   # for Option A only

Data assumption (USER must supply — these are NOT auto-generated):
  - `transcripts`: a pandas DataFrame, one row per transcript, with at least
                   x/y pixel columns (named `x`/`y` or as shown below) and a
                   `gene` column. Load it yourself, e.g.:
                     transcripts = pd.read_parquet('transcripts.parquet')
  - `image`:        a 2D/3D numpy array (HxW or HxWxC) of the paired nuclear
                   stain (DAPI/H&E/IF). Required only for Option A (cellpose).

Goal: for platforms that output individual transcripts (MERFISH / Xenium raw /
      Stereo-seq), assign each transcript to the cell whose mask contains its (x,y).
"""
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 0. Load the transcript table (USER: replace with your real path/columns)
# ---------------------------------------------------------------------------
transcripts = pd.read_parquet('transcripts.parquet')   # <-- replace
# Normalize coordinate column names (Xenium uses x/y; some platforms use X/Y):
for canon, alt in [('x', 'X'), ('y', 'Y')]:
    if canon not in transcripts.columns and alt in transcripts.columns:
        transcripts = transcripts.rename(columns={alt: canon})
assert {'x', 'y', 'gene'}.issubset(transcripts.columns), \
    "transcripts must have x, y, gene columns"

# ---------------------------------------------------------------------------
# Option A: cellpose on a paired image (needs H&E / DAPI / IF) — FRAGMENT
# ---------------------------------------------------------------------------
# image = np.load('nuclear_stain.npy')   # <-- USER: load the paired stain image
# from cellpose import models
# model = models.Cellpose(model_type='cyto2')   # or 'nuclei' for nuclear-only
# masks, flows, styles, diams = model.eval(image, diameter=30, channels=[0, 0])
# # masks: HxW int array, 0=background, 1..N=label per cell
# #
# # Assign each transcript to the cell whose mask contains its (x, y):
# transcripts['cell_id'] = masks[transcripts.y.astype(int), transcripts.x.astype(int)]
# assigned = transcripts[transcripts['cell_id'] > 0]
# print(f'Assigned: {len(assigned)}/{len(transcripts)} ({len(assigned)/len(transcripts):.1%})')

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
else:
    print('[skip] Option C: transcripts has no "cell_id" column '
          '(use Option A cellpose or Option B baysor to generate one first)')
