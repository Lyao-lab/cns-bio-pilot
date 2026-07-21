"""High-resolution spatial analysis with Squidpy (canonical example).

Reference: squidpy 1.2.2+ | scanpy 1.10+ | numpy 1.26+ | Verify API if version differs
Data assumption: h5ad with obsm['spatial'] holding x/y coordinates (microns)
                 for Slide-seq / Stereo-seq / Visium HD / MERFISH.
"""
import squidpy as sq
import scanpy as sc
import numpy as np

# ---------------------------------------------------------------------------
# 1. Load high-resolution spatial data
# ---------------------------------------------------------------------------
adata = sc.read_h5ad('spatial_highres.h5ad')
print(f'Spots/beads: {adata.n_obs}')
print(f'Coordinate range: {adata.obsm["spatial"].min(axis=0)} - {adata.obsm["spatial"].max(axis=0)}')

# ---------------------------------------------------------------------------
# 2. Standard preprocessing
# ---------------------------------------------------------------------------
sc.pp.filter_cells(adata, min_genes=50)
sc.pp.filter_genes(adata, min_cells=10)
sc.pp.normalize_total(adata)
sc.pp.log1p(adata)

# Optional: bin very dense data (Slide-seq/Stereo-seq) for noise reduction
def bin_spatial(adata, bin_size=50):
    coords = adata.obsm['spatial']
    bins_x = np.floor(coords[:, 0] / bin_size).astype(int)
    bins_y = np.floor(coords[:, 1] / bin_size).astype(int)
    adata.obs['bin_id'] = [f'{x}_{y}' for x, y in zip(bins_x, bins_y)]
    return adata
# adata = bin_spatial(adata, bin_size=50)

# ---------------------------------------------------------------------------
# 3. Spatial neighbor graph (tune n_neighs for platform density)
# ---------------------------------------------------------------------------
sq.gr.spatial_neighbors(
    adata,
    coord_type='generic',     # 'generic' for irregular; 'grid' for Visium
    n_neighs=15,              # higher for dense platforms
    spatial_key='spatial',
)

# ---------------------------------------------------------------------------
# 4. Spatial autocorrelation (Moran's I — spatially variable genes)
# ---------------------------------------------------------------------------
sq.gr.spatial_autocorr(adata, mode='moran', genes=adata.var_names[:500], n_perms=100)
moranI = adata.uns['moranI'].sort_values('I', ascending=False)
top_svg = moranI.head(50).index.tolist()
print(f'Top spatially variable genes: {top_svg[:10]}')

# ---------------------------------------------------------------------------
# 5. Clustering + visualization
# ---------------------------------------------------------------------------
sc.pp.pca(adata)
sc.pp.neighbors(adata)
sc.tl.leiden(adata, resolution=0.5)

sq.pl.spatial_scatter(adata, color='leiden', size=5, save='spatial_clusters.png')

# ---------------------------------------------------------------------------
# 6. Neighborhood enrichment + ligand-receptor
# ---------------------------------------------------------------------------
sq.gr.nhood_enrichment(adata, cluster_key='leiden')
sq.pl.nhood_enrichment(adata, cluster_key='leiden', save='nhood_enrichment.png')

sq.gr.ligrec(adata, n_perms=100, cluster_key='leiden')

# ---------------------------------------------------------------------------
# 7. Hex binning for very dense platforms (Slide-seq/Stereo-seq visualization)
# ---------------------------------------------------------------------------
sq.pl.spatial_scatter(adata, shape='hex', size=50, color='leiden')
sq.gr.spatial_neighbors(adata, coord_type='grid', n_rings=1)   # grid alternative
