---
name: bio-spatial-transcriptomics-spatial-multiomics
description: 高分辨率空转平台（Stereo-seq / Visium HD / Slide-seq / MERFISH）分析——亚细胞分割（cellpose）、binning、多模态对齐（SpatialData）。当用户要做高分辨率空转、subcellular analysis、Stereo-seq、Visium HD、cellpose 分割时触发。
tool_type: python
primary_tool: squidpy
---

## When NOT to use this skill
- Conventional Visium (55μm spot, no cellpose segmentation needed) → use `spatial/omicverse-spatial` (lighter)
- Estimating spot cell composition (deconvolution) → use `spatial/deconvolution` (cell2location/RCTD)
- Spatial proteomics (CODEX/IMC/MIBI) → use `spatial/proteomics`
- Conventional single-cell (not high-resolution spatial) → use `single-cell/omicverse-pipeline`

## Version Compatibility

Verify installed versions match before running: `pip show <pkg>` / `help(func)` to check signatures; adapt examples to your actual API rather than retrying on errors.

# Spatial Multi-omics Analysis

**"Analyze my high-resolution spatial data"** → Process subcellular-resolution spatial platforms (Xenium, MERFISH, Slide-seq, Stereo-seq) including cell segmentation, binning strategies, and multi-modal integration.
- Python: `spatialdata` + `squidpy` for unified multi-platform analysis

## Platform Comparison

| Platform | Resolution | Spots/Beads | Coverage |
|----------|------------|-------------|----------|
| Visium | 55 µm | ~5,000 | Tissue-wide |
| Visium HD | 2 µm | ~11M | Subcellular |
| Slide-seq | 10 µm | ~100,000 | High-density |
| Stereo-seq | 0.5 µm | >200M | Subcellular |
| MERFISH | Single-molecule | N/A | Targeted genes |

## Squidpy for High-Resolution Data

**Goal:** Run standard spatial analyses (autocorrelation, neighborhood enrichment, ligand-receptor) on high-resolution spatial data.

**Approach:** Adjust neighbor graph density for high-resolution platforms, then apply standard Squidpy workflows.

```python
import squidpy as sq
import scanpy as sc

# Load spatial data
adata = sc.read_h5ad('spatial_multiomics.h5ad')

# Spatial neighbors (for high-resolution, adjust n_neighs based on density)
sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=10, spatial_key='spatial')

# Spatial autocorrelation (Moran's I)
sq.gr.spatial_autocorr(adata, mode='moran', genes=adata.var_names[:100])

# Neighborhood enrichment analysis
sq.gr.nhood_enrichment(adata, cluster_key='cell_type')
sq.pl.nhood_enrichment(adata, cluster_key='cell_type')

# Ligand-receptor analysis
sq.gr.ligrec(adata, n_perms=100, cluster_key='cell_type')
```

## SpatialData Framework

**Goal:** Load and query multi-modal spatial data using the SpatialData unified representation.

**Approach:** Use spatialdata-io readers per platform, then access images, points, shapes, and tables through a single object with spatial queries.

```python
import spatialdata as sd
from spatialdata_io import read_visium, read_xenium

# Read Visium data
sdata = read_visium('visium_output/')

# Read Xenium data (10x Genomics subcellular)
sdata = read_xenium('xenium_output/')

# Read from Zarr
sdata = sd.read_zarr('experiment.zarr')

# Access different elements
images = sdata.images['morphology']
points = sdata.points['transcripts']
shapes = sdata.shapes['cell_boundaries']
table = sdata.tables['adata']

# Query by region
from spatialdata import bounding_box_query
roi = bounding_box_query(sdata, min_coordinate=[0, 0], max_coordinate=[1000, 1000], axes=['x', 'y'])
```

## Slide-seq/Stereo-seq Processing

```python
# For high-density data, bin spots into hexagonal grids
import numpy as np

# Create hexagonal bins
def hexbin_data(adata, gridsize=50):
    coords = adata.obsm['spatial']
    from matplotlib.pyplot import hexbin
    hb = hexbin(coords[:, 0], coords[:, 1], C=None, gridsize=gridsize, reduce_C_function=np.sum)
    return hb

# Squidpy visualization with hex binning
sq.pl.spatial_scatter(adata, shape='hex', size=50, color='cluster')

# Grid-based spatial neighbors for regular patterns
sq.gr.spatial_neighbors(adata, coord_type='grid', n_rings=1)
```

## Subcellular Analysis (MERFISH/Xenium)

**Goal:** Perform transcript-level and subcellular compartment analysis for single-molecule platforms.

**Approach:** Segment cells with Cellpose, then assign individual transcripts to cells based on mask coordinates.

```python
# Transcript-level analysis
# Assign transcripts to compartments
sq.gr.co_occurrence(adata, cluster_key='compartment', spatial_key='spatial')

# Cell segmentation integration
from cellpose import models
model = models.Cellpose(model_type='cyto2')
masks, flows, styles, diams = model.eval(image, diameter=30, channels=[0, 0])

# Map transcripts to cells
def assign_transcripts_to_cells(transcripts_df, masks):
    x, y = transcripts_df['x'].values.astype(int), transcripts_df['y'].values.astype(int)
    transcripts_df['cell_id'] = masks[y, x]
    return transcripts_df[transcripts_df['cell_id'] > 0]
```

## Multi-Modal Integration

**Goal:** Combine spatial gene expression with histological image features for integrated analysis.

**Approach:** Process and segment tissue images, extract image features, then correlate with gene expression.

```python
# Combine spatial transcriptomics with histology
sq.im.process(adata, layer='image', method='smooth', sigma=2)
sq.im.segment(adata, layer='image', method='watershed', thresh=0.1)

# Extract image features
sq.im.calculate_image_features(
    adata, layer='image', features=['texture', 'summary'],
    key_added='img_features', n_jobs=4
)

# Correlate image features with gene expression
from scipy.stats import pearsonr
for gene in ['marker1', 'marker2']:
    r, p = pearsonr(adata.obs['img_feature'], adata[:, gene].X.flatten())
    print(f'{gene}: r={r:.3f}, p={p:.3e}')
```

## Visium HD Specific

```python
# Visium HD produces bin files at multiple resolutions
# Load 8µm binned data (recommended starting point)
adata = sc.read_h5ad('visium_hd_8um.h5ad')

# Downsample to 16µm if needed for initial analysis
# Original 2µm data available for detailed analysis
```

## Cell Segmentation (bin → single-cell conversion)

> High-res platforms (Visium HD 2µm / Stereo-seq / Slide-seq / MERFISH) output **subcellular bins or transcripts**, not cells. To get single-cell resolution, you must segment. Method choice depends on platform + whether you have a nuclear/cell stain image.

### Segmentation method decision table

| Platform / data | First choice | Why | Tool |
|---|---|---|---|
| **Visium HD** (2µm bin + H&E) | **bin2cell** (Nature Methods 2024) | Specifically built for Visium HD: uses H&E nuclear stain → cellpose nuclear mask → expand to cells → aggregate 2µm bins into cells. Wrapped in `ov.space.bin2cell` | `ov.space.bin2cell` or standalone `pip install bin2cell` |
| **Xenium** | **Use built-in cell segmentation** (10x provides cell mask in output) | Xenium pipeline already segments; re-segmenting is usually worse unless you have a better stain | 10x cell_id column (no extra tool) |
| **Stereo-seq** | **SAW pipeline cell segmentation** (official) or cellpose on IF | SAW (Spatial Augmented Analysis) is the official Stereo-seq pipeline; its cell mask is usually better than re-segmenting | SAW / cellpose |
| **MERFISH / Slide-seq** (transcript-level) | **Baysor** (Bayesian, no image needed) or **cellpose** (needs IF image) | Baysor segments from transcript density alone — no image required; cellpose needs a nuclear stain | `pip install baysor` / cellpose |
| **Any platform + H&E/IF image** | **cellpose** (cyto2 / nuclei model) | Deep-learning segmentation; needs paired image; works on any platform | `pip install cellpose` |
| **No image, want fast estimate** | **SAINSC** (2024) or **stardist** | SAINSC does kernel-density cell calling from expression only (no image, no DL) | standalone |

### Visium HD: bin2cell workflow (most common segmentation need, 2024-2026)

`ov.space` wraps bin2cell for the Visium HD bin→cell pipeline. **Verified API** (omicverse 2.2.3):

```python
import omicverse as ov

# Step 1: Load Visium HD 2µm bin data + H&E image
adata = ov.io.read_visium_hd(path)   # 2µm resolution

# Step 2: Segment nuclei from H&E (cellpose, needs H&E image)
# cellpose nuclear segmentation on the H&E → labels_he
# (run cellpose separately: model_type='nuclei', diameter≈ H&E nuclei size)

# Step 3: Expand nuclear masks to approximate cell boundaries
ov.space.visium_10x_hd_cellpose_expand(adata,
    max_bin_distance=4,              # how many bins to expand beyond nucleus
    labels_key='labels_he',
    expanded_labels_key='labels_he_expanded')

# Step 4: Aggregate 2µm bins into cells (the core bin2cell step)
ov.space.bin2cell(adata,
    labels_key='labels_joint',       # the expanded cell labels
    spatial_keys=['spatial'],
    add_geometry=True)               # add polygon geometry for SpatialData

# Step 5: Sync segmentation geometries with SpatialData
ov.space.sync_visium_hd_seg_geometries(adata)
# Result: adata now has single-cell resolution (each obs row = one cell)
```

> **bin2cell standalone** (if omicverse wrapper has issues): `pip install bin2cell` → `import bin2cell as b2c` → `b2c.bin2cell(adata, labels_key=...)`. Same algorithm, more control over parameters.

### Xenium / MERFISH / Stereo-seq: transcript-to-cell assignment

For platforms that output individual transcripts (not bins):

```python
# Option A: Use platform's built-in segmentation (Xenium default)
# Xenium output already has 'cell_id' per transcript — just aggregate:
adata = ov.io.read_xenium(path)   # cells already segmented

# Option B: Baysor (no image needed — segments from transcript density)
# baysor run -c config.toml  (CLI; outputs cell_ids per transcript)
# Then read the Baysor-assigned cell x gene matrix

# Option C: cellpose on nuclear stain + assign transcripts to masks
from cellpose import models
model = models.Cellpose(model_type='nuclei')   # or 'cyto2' for full cells
masks, _, _, _ = model.eval(nuclear_image, diameter=30, channels=[0,0])
# Assign each transcript to the cell whose mask contains its (x,y):
transcripts['cell_id'] = masks[transcripts.y.astype(int), transcripts.x.astype(int)]
```

### Segmentation quality assessment (mandatory after segmenting)

```python
# 1. Cell count sanity: ~cell density × tissue area
#    Too few cells (e.g. 500 from a 6mm² tissue) = under-segmentation
#    Too many (e.g. 2M from same area) = over-segmentation / debris
print(f'Cells: {adata.n_obs}, Median genes/cell: {adata.obs["n_genes_by_counts"].median()}')

# 2. Compare segmentation to H&E morphology (visual check)
ov.pl.plot_spatial(adata, color='n_genes_by_counts', basis='spatial')

# 3. Border-cell handling: cells at tissue edge may be truncated
#    Flag low-gene-count edge cells (often artifacts), don't silently keep
edge_cells = adata.obs['n_genes_by_counts'] < 50
adata.obs['is_edge_low'] = edge_cells
```

### When NOT to segment

- **Conventional Visium (55µm spot)**: spot is already the unit; segmenting within spot = deconvolution (`spatial/deconvolution`), not cell segmentation
- **Xenium with good built-in mask**: re-segmenting is usually worse than the 10x-provided mask unless you have a superior custom stain
- **Stereo-seq with SAW output**: trust the official pipeline unless you have a specific reason

## Quality Metrics

| Metric | Visium | High-Resolution |
|--------|--------|-----------------|
| Genes/spot | >2000 | >500 |
| UMI/spot | >5000 | >1000 |
| Spatial coverage | >80% | >50% |

## Related Skills

- **Conventional Visium/Xenium (no segmentation)** → `spatial/omicverse-spatial` (lighter; includes SVG/domains/communication)
- **Deconvolution to estimate cell composition** → `spatial/deconvolution` (cell2location/RCTD, unified wrapper)

## Prerequisites (where it comes from)

- **Raw high-resolution spatial data**: Stereo-seq (SAW pipeline output) / Visium HD (2µm/8µm bin) / Slide-seq / MERFISH
- **Paired H&E or IF images** (optional, aids cellpose segmentation)
- **SpatialData framework**: `pip install spatialdata` to load multimodal alignment
- Tools: squidpy (core) + cellpose (segmentation) + spatialdata (multimodal integration)

## When to leave this skill (where to go)

- Once high-resolution data is segmented into single cells → go to `single-cell/omicverse-pipeline` (analyze as single-cell)
- Estimate spot/cell type composition → `spatial/deconvolution`
- Write Methods → `presentation/methods-writer`
- Multi-panel high-resolution section figures → `visualization/multi-panel-figures`

## Key pitfalls

- **Visium HD bin size choice**: start at 8µm (balances resolution vs noise); 2µm only for segmentation (bin2cell) or detail review; raw 2µm for clustering is too noisy
- **Segmentation method must match platform**: bin2cell for Visium HD, Baysor for image-less transcript data, built-in mask for Xenium — don't apply cellpose blindly to every platform
- **cellpose segmentation needs H&E/IF registration** — pure transcriptome without image gives poor segmentation (use Baysor instead for image-less)
- **bin2cell is NOT installed by default** — `ov.space.bin2cell` is a wrapper entry; you need `pip install bin2cell` for the actual algorithm. Same for cellpose (`pip install cellpose`)
- **Re-segmenting Xenium/Stereo-seq is usually worse** than the platform's built-in cell mask — only re-segment if you have a superior custom stain
- **Cell count sanity check is mandatory**: too few cells = under-segmentation; too many = debris/over-segmentation. Compare to H&E morphology.
- **Stereo-seq V2 FFPE vs total RNA** use different pipelines; confirm SAW version
- **SpatialData multimodal alignment** requires coordinate registration first (ground-truth check, meta-methodology principle ①)
- After finishing, run `scripts/postcheck.py` to verify spatial-coordinate integrity
