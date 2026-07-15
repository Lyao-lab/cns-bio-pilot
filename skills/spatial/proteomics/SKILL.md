---
name: bio-spatial-transcriptomics-spatial-proteomics
description: 空间蛋白组（CODEX / IMC / MIBI）分析——细胞分割、phenotyping（scimap）、蛋白共定位、与空转整合。当用户要做空间蛋白、multiplexed imaging、CODEX/IMC/MIBI、蛋白 gating、protein colocalization 时触发。
tool_type: python
primary_tool: scimap
---

## When NOT to use this skill
- Data is spatial transcriptomics (Visium/Xenium/Stereo-seq), not protein → use `spatial/omicverse-spatial` or `spatial/multiomics`
- Estimating spatial spot cell-type composition (deconvolution) → use `spatial/deconvolution`
- Conventional single-cell scRNA-seq (protein intensity matrix without spatial coordinates) → use `single-cell/omicverse-pipeline`
- Plain flow/CyTOF protein-expression analysis (non-spatial) → out of scope for this skill

## Version Compatibility

Verify installed versions match before running: `pip show <pkg>` / `help(func)` to check signatures; adapt examples to your actual API rather than retrying on errors.

# Spatial Proteomics Analysis

**"Analyze my CODEX/IMC spatial proteomics data"** → Process multiplexed imaging data including cell segmentation, protein phenotyping, spatial neighborhood analysis, and protein colocalization scoring.
- Python: `scimap.tl.phenotype_cells()`, `squidpy.gr.nhood_enrichment()`

## Data Loading

**Goal:** Process multiplexed spatial proteomics data (CODEX/IMC/MIBI) through cell phenotyping, spatial neighborhood analysis, and protein colocalization scoring.

**Approach:** Load the cell-by-marker intensity matrix with spatial coordinates into AnnData, normalize and rescale marker intensities, phenotype cells by marker expression gating, then analyze spatial neighborhoods and cell-cell interactions using scimap and squidpy.

```python
import scimap as sm
import anndata as ad

# Load CODEX/IMC data (cell x marker matrix with spatial coordinates)
adata = ad.read_h5ad('spatial_proteomics.h5ad')

# Required: spatial coordinates in adata.obsm['spatial']
# Required: protein intensities in adata.X
```

## Preprocessing

```python
# Log transform intensities
sm.pp.log1p(adata)

# Rescale markers (0-1 per marker)
sm.pp.rescale(adata)

# Combat batch correction if multiple FOVs
sm.pp.combat(adata, batch_key='fov')
```

## Phenotyping Cells

```python
# Manual gating approach
phenotype_markers = {
    'T_cell': ['CD3', 'CD45'],
    'B_cell': ['CD20', 'CD45'],
    'Macrophage': ['CD68', 'CD163'],
    'Tumor': ['panCK', 'Ki67']
}

sm.tl.phenotype_cells(adata, phenotype=phenotype_markers,
                      gate=0.5, label='phenotype')

# Clustering-based phenotyping
sm.tl.cluster(adata, method='leiden', resolution=1.0)
```

## Spatial Analysis

```python
# Build spatial neighbors graph
sm.tl.spatial_distance(adata, x_coordinate='X', y_coordinate='Y')

# Neighborhood enrichment
sm.tl.spatial_interaction(adata, phenotype='phenotype',
                          method='knn', knn=10)

# Spatial clustering (communities of cells)
sm.tl.spatial_cluster(adata, phenotype='phenotype')
```

## Visualization

```python
# Spatial scatter plot
sm.pl.spatial_scatterPlot(adata, colorBy='phenotype',
                          x='X', y='Y', s=5)

# Heatmap of spatial interactions
sm.pl.spatial_interaction(adata)

# Marker expression overlay
sm.pl.image_viewer(adata, markers=['CD3', 'CD20', 'panCK'])
```

## Integration with Transcriptomics

```python
import squidpy as sq

# If matched spatial transcriptomics available
# Transfer labels or integrate modalities
sq.gr.spatial_neighbors(adata_protein)
sq.gr.spatial_neighbors(adata_rna)

# Compare spatial patterns across modalities
```

## Platform-Specific Notes

| Platform | Markers | Resolution | Notes |
|----------|---------|------------|-------|
| CODEX | 40-60 | Subcellular | Cyclic staining |
| IMC | 40+ | 1 um | Metal-tagged antibodies |
| MIBI | 40+ | 260 nm | Mass spectrometry |

## Related Skills

- **Paired spatial transcriptomics integration** → `spatial/multiomics` (SpatialData multimodal)
- **Spatial neighborhood/domains/communication** → `spatial/omicverse-spatial` (squidpy general API)

## Prerequisites (where it comes from)

- **Raw spatial proteomics data**: CODEX / IMC / MIBI multichannel images + segmented single-cell masks
- **Antibody panel metadata** (marker → cell type mapping, for gating/phenotyping)
- Tools: `scimap` (phenotyping workhorse) + `squidpy` (spatial analysis) + `SpatialData` (multimodal integration)

## When to leave this skill (where to go)

- Write Methods describing protein gating/phenotyping → `presentation/methods-writer`
- Multi-panel protein-expression spatial figures → `visualization/multi-panel-figures`
- Paired spatial transcriptomics integration → `spatial/multiomics`

## Key pitfalls

- **Gating thresholds are experimental design** — copying generic thresholds fails (marker intensity depends on platform/batch); set per-sample
- **After phenotyping, run a marker-proportion sanity check** (meta-methodology principle ①)
- **CODEX/IMC channel crosstalk**: check compensation between adjacent fluorophores
- **Protein ≠ mRNA**: don't directly apply transcriptomics annotations; use protein markers (CD3/CD20/CD68...)
- After finishing, run `scripts/postcheck.py` to verify spatial coordinates + proportion sanity
