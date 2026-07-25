"""Image × expression integration with Squidpy (canonical example).

Reference: squidpy 1.2.2 (verified API) | scanpy 1.9+ | scipy 1.10+
Env:       conda env `st` (squidpy's home env) — see skill env table

Key correction (2026-07 audit): squidpy's image API operates on an
**ImageContainer**, NOT on the AnnData directly. Earlier versions of this
example passed `adata` to `sq.im.process/segment/calculate_image_features`,
which is a type error (squidpy 1.2.2 signatures all take `img: ImageContainer`).

Data assumption (user must supply):
  - `adata`:   AnnData with `obsm['spatial']` (spot coords) and, for Visium,
               an H&E image. Load it yourself first:
                 import scanpy as sc
                 adata = sc.read_h5ad('your_spatial.h5ad')
               or for 10x Visium use `sq.read.visium()` which attaches the image.
  - `img`:     either built from a loaded image array, OR obtained from the
               SpatialData/squidpy reader. The container holds the H&E/IF image
               aligned to `adata` (same library_id, same coordinate frame).

Goal: combine spatial gene expression with histological image features
      (texture / summary / segmentation) for integrated analysis.
"""
import numpy as np
import squidpy as sq
import scanpy as sc
from scipy.stats import pearsonr

# ---------------------------------------------------------------------------
# 0. Load data + build the ImageContainer (USER: replace with your real paths)
# ---------------------------------------------------------------------------
# Option A — 10x Visium (image auto-attached by the reader):
#   adata = sq.read.visium('path/to/visium_outs/')
#   img = adata.uns['spatial'][<library_id>]['images']['hires']   # ndarray (H, W, 3)
#   img_container = sq.im.ImageContainer(img, layer='image')
#   # access layers via img_container['image'] (returns xarray.DataArray), NOT .layers

# Option B — generic: you already have adata + a registered H&E ndarray:
adata = sc.read_h5ad('your_spatial.h5ad')   # <-- replace
# image_array shape: (H, W, C) uint8, registered to adata.obsm['spatial']
image_array = np.load('your_he_image.npy')  # <-- replace

img_container = sq.im.ImageContainer(image_array, layer='image')

# ---------------------------------------------------------------------------
# 1. Image preprocessing (smooth + segment INSIDE the container, not on adata)
# ---------------------------------------------------------------------------
sq.im.process(
    img_container,
    layer='image',
    method='smooth',
    sigma=2,
    layer_added='smooth',          # smoothed output written here, input preserved
)
sq.im.segment(
    img_container,
    layer='smooth',                # segment the smoothed layer
    method='watershed',
    thresh=0.1,
    layer_added='segmented',       # mask written here
)

# ---------------------------------------------------------------------------
# 2. Extract image features PER SPOT (writes into adata.obsm['img_features'])
# ---------------------------------------------------------------------------
sq.im.calculate_image_features(
    adata,
    img_container,                 # <-- second positional arg is the container
    layer='image',
    library_id=list(adata.uns['spatial'].keys())[0] if 'spatial' in adata.uns else None,
    features=['texture', 'summary'],
    key_added='img_features',
    n_jobs=4,
)

# ---------------------------------------------------------------------------
# 3. Correlate one image feature with gene expression
#    (obsm['img_features'] is a pandas DataFrame here — .iloc is valid)
# ---------------------------------------------------------------------------
img_features_df = adata.obsm['img_features']
adata.obs['img_feature_0'] = img_features_df.iloc[:, 0].values

# Pick real marker genes from adata.var_names — do NOT hardcode placeholder names.
candidate_genes = [g for g in ['EPCAM', 'PECAM1', 'PTPRC', 'COL1A1']
                   if g in adata.var_names]
for gene in candidate_genes:
    expr = adata[:, gene].X.toarray().flatten() if hasattr(adata[:, gene].X, 'toarray') \
           else np.asarray(adata[:, gene].X).flatten()
    r, p = pearsonr(adata.obs['img_feature_0'], expr)
    print(f'{gene}: r={r:.3f}, p={p:.3e}')

# ---------------------------------------------------------------------------
# 4. Co-occurrence analysis (subcellular platforms with compartment labels)
#    Requires obs['compartment'] (e.g. nuclear / cytoplasmic / membrane) per cell/spot
# ---------------------------------------------------------------------------
if 'compartment' in adata.obs.columns:
    sq.gr.co_occurrence(adata, cluster_key='compartment', spatial_key='spatial')
else:
    print('[skip] co_occurrence: obs["compartment"] not present '
          '(only relevant for subcellular platforms with compartment labels)')
