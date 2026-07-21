"""Image × expression integration with Squidpy (canonical example).

Reference: squidpy 1.3+ | scanpy 1.10+ | scipy 1.12+ | Verify API if version differs
Data assumption: adata with obsm['spatial'] AND an image layer accessible to
                 sq.im (typically loaded via SpatialData → squidpy integration,
                 or cached as adata.uns['image'] / adata.obsm['image']).

Goal: combine spatial gene expression with histological image features
      (texture / summary / segmentation) for integrated analysis.
"""
import squidpy as sq
import scanpy as sc
from scipy.stats import pearsonr

# ---------------------------------------------------------------------------
# 1. Image preprocessing (smooth + segment within sq.im)
# ---------------------------------------------------------------------------
sq.im.process(adata, layer='image', method='smooth', sigma=2)
sq.im.segment(adata, layer='image', method='watershed', thresh=0.1)

# ---------------------------------------------------------------------------
# 2. Extract image features per spot
# ---------------------------------------------------------------------------
sq.im.calculate_image_features(
    adata,
    layer='image',
    features=['texture', 'summary'],
    key_added='img_features',
    n_jobs=4,
)

# ---------------------------------------------------------------------------
# 3. Correlate image features with gene expression
# ---------------------------------------------------------------------------
adata.obs['img_feature'] = adata.obsm['img_features'].iloc[:, 0]
for gene in ['marker1', 'marker2']:
    r, p = pearsonr(adata.obs['img_feature'], adata[:, gene].X.flatten())
    print(f'{gene}: r={r:.3f}, p={p:.3e}')

# ---------------------------------------------------------------------------
# 4. Co-occurrence analysis (subcellular platforms with compartment labels)
# ---------------------------------------------------------------------------
# Requires obs['compartment'] (e.g. nuclear / cytoplasmic / membrane) per cell/spot
sq.gr.co_occurrence(adata, cluster_key='compartment', spatial_key='spatial')
