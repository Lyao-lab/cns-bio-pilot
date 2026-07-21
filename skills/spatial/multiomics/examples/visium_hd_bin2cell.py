"""Visium HD bin → single-cell segmentation with bin2cell (canonical example).

Reference: omicverse 2.2.3+ (wraps bin2cell) | bin2cell 1.x+ | cellpose 3.0+ | Verify API if version differs

Install (NOT auto-installed in the sc/st envs):
  pip install bin2cell cellpose

Data assumption: Visium HD output directory with 2µm bin data + paired H&E image.

Pipeline: 2µm bins → cellpose nuclei on H&E → expand to cells → aggregate bins into cells
"""
import omicverse as ov
# from cellpose import models  # for the nuclei segmentation step (run separately)

# ---------------------------------------------------------------------------
# Step 1. Load Visium HD 2µm bin data
# ---------------------------------------------------------------------------
adata = ov.io.read_visium_hd('/path/to/visium_hd_output')   # 2µm resolution

# ---------------------------------------------------------------------------
# Step 2. Segment nuclei from H&E (cellpose, run separately on the H&E image)
# ---------------------------------------------------------------------------
# model = models.Cellpose(model_type='nuclei')
# labels_he, _, _, _ = model.eval(he_image, diameter=<nuclei_diameter>, channels=[0, 0])
# Attach labels_he to adata.obs or a spatial labels layer as 'labels_he'.
# (The cellpose step is intentionally separate — H&E preprocessing varies by stain.)

# ---------------------------------------------------------------------------
# Step 3. Expand nuclear masks to approximate cell boundaries
# ---------------------------------------------------------------------------
ov.space.visium_10x_hd_cellpose_expand(
    adata,
    max_bin_distance=4,                # how many bins to expand beyond nucleus
    labels_key='labels_he',
    expanded_labels_key='labels_he_expanded',
)

# ---------------------------------------------------------------------------
# Step 3.5. Join expanded H&E labels with any existing Visium high-res labels
#           (e.g. from 10x cellpose output) to produce a unified 'labels_joint'
#           column. Skip if you only have H&E labels — in that case set
#           labels_joint = labels_he_expanded directly in adata.obs.
# ---------------------------------------------------------------------------
# b2c.merge_all_labels(adata, labels_he='labels_he_expanded',
#                      labels_hr='labels_hr', out_key='labels_joint')
adata.obs['labels_joint'] = adata.obs['labels_he_expanded']   # fallback: single-source labels

# ---------------------------------------------------------------------------
# Step 4. Aggregate 2µm bins into cells (the core bin2cell step)
# ---------------------------------------------------------------------------
ov.space.bin2cell(
    adata,
    labels_key='labels_joint',         # the joint cell labels from Step 3.5
    spatial_keys=['spatial'],
    add_geometry=True,                 # add polygon geometry for SpatialData
)

# ---------------------------------------------------------------------------
# Step 5. Sync segmentation geometries with SpatialData
# ---------------------------------------------------------------------------
ov.space.sync_visium_hd_seg_geometries(adata)
# Result: adata now has single-cell resolution (each obs row = one cell)

# ---------------------------------------------------------------------------
# Step 6. Segmentation quality check (mandatory — see SKILL.md)
# ---------------------------------------------------------------------------
print(f'Cells: {adata.n_obs}, Median genes/cell: {adata.obs["n_genes_by_counts"].median()}')
ov.pl.plot_spatial(adata, color='n_genes_by_counts', basis='spatial')

# Flag low-gene edge cells (often artifacts)
adata.obs['is_edge_low'] = adata.obs['n_genes_by_counts'] < 50

# ---------------------------------------------------------------------------
# Standalone fallback (if omicverse wrapper has issues):
#   pip install bin2cell
#   import bin2cell as b2c
#   b2c.bin2cell(adata, labels_key='labels_joint', ...)
# ---------------------------------------------------------------------------
