---
name: spatial-multiomics-highres
description: 高分辨率空转平台（Stereo-seq / Visium HD / Slide-seq / MERFISH）分析——亚细胞分割（cellpose）、binning、多模态对齐（SpatialData）。当用户要做高分辨率空转、subcellular analysis、Stereo-seq、Visium HD、cellpose 分割时触发。
tool_type: python
primary_tool: squidpy
---

## When NOT to use this skill
- Conventional Visium (55μm spot, no cellpose segmentation needed) → use `spatial/omicverse-spatial` (lighter)
- Estimating spot cell composition (deconvolution) → use `spatial/deconvolution` (cell2location/RCTD)
- Spatial proteomics (CODEX/IMC/MIBI) → use `spatial/proteomics`
- Conventional single-cell (not high-resolution spatial) → use `single-cell/omicverse-pipeline`

# Spatial Multi-omics Analysis

**"Analyze my high-resolution spatial data"** → Process subcellular-resolution spatial platforms (Xenium, MERFISH, Slide-seq, Stereo-seq, Visium HD) including cell segmentation, binning strategies, and multi-modal integration.

**Engines**: `squidpy` (spatial statistics) + `spatialdata` (multi-platform unified representation) + `cellpose`/`bin2cell`/`baysor` (segmentation).

## Platform Comparison

| Platform | Resolution | Spots/Beads | Coverage |
|----------|------------|-------------|----------|
| Visium | 55 µm | ~5,000 | Tissue-wide |
| Visium HD | 2 µm | ~11M | Subcellular |
| Slide-seq | 10 µm | ~100,000 | High-density |
| Stereo-seq | 0.5 µm | >200M | Subcellular |
| MERFISH | Single-molecule | N/A | Targeted genes |

## Core workflow (5 steps)

| Step | What | Engine | Key discipline |
|---|---|---|---|
| 1 | Load via SpatialData | `spatialdata_io.read_xenium` / `read_visium_hd` / `read_visium` | use top-level reader functions (NOT legacy `xenium.xenium(...)`) |
| 2 | (If subcellular) Segment into cells | platform decision table below | method must match platform — don't apply cellpose blindly |
| 3 | Spatial neighbor graph | `sq.gr.spatial_neighbors` | tune `n_neighs` for density; `coord_type='generic'` (irregular) or `'grid'` (Visium) |
| 4 | Spatial variable genes + clusters | `sq.gr.spatial_autocorr` (Moran's I) → `sc.tl.leiden` | top SVGs by Moran's I |
| 5 | Neighborhood enrichment / ligand-receptor | `sq.gr.nhood_enrichment` / `sq.gr.ligrec` | cluster-level spatial interactions |

**Canonical entry** (squidpy spatial stats):
```python
import squidpy as sq
sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=15, spatial_key='spatial')
sq.gr.spatial_autocorr(adata, mode='moran', genes=adata.var_names[:500])
```

> **Full runnable workflows**:
> - squidpy end-to-end (load → SVG → cluster → nhood → ligrec → hex bin) → `examples/squidpy_highres.py`
> - SpatialData multi-platform load + region query + transcript aggregation → `examples/spatialdata_workflow.py`
> - Visium HD bin2cell segmentation (bin → cellpose nuclei → expand → aggregate) → `examples/visium_hd_bin2cell.py`

## Cell Segmentation (bin/transcript → single-cell)

> High-res platforms output **subcellular bins or transcripts**, not cells. To get single-cell resolution you must segment. Method choice depends on platform + whether you have a nuclear/cell stain image.

### Segmentation method decision table

| Platform / data | First choice | Why | Tool |
|---|---|---|---|
| **Visium HD** (2µm bin + H&E) | **bin2cell** (Nature Methods 2024) | Built for Visium HD: H&E nuclear stain → cellpose nuclear mask → expand → aggregate 2µm bins. Wrapped in `ov.space.bin2cell` | `ov.space.bin2cell` or `pip install bin2cell` |
| **Xenium** | **Use built-in cell segmentation** (10x provides cell mask) | Xenium pipeline already segments; re-segmenting is usually worse unless you have a better stain | 10x cell_id column |
| **Stereo-seq** | **SAW pipeline cell segmentation** (official) or cellpose on IF | SAW is the official Stereo-seq pipeline; its mask usually beats re-segmenting | SAW / cellpose |
| **MERFISH / Slide-seq** (transcript-level) | **Baysor** (Bayesian, no image) or **cellpose** (needs IF) | Baysor segments from transcript density alone; cellpose needs a nuclear stain | `pip install baysor` / cellpose |
| **Any platform + H&E/IF image** | **cellpose** (cyto2 / nuclei model) | Deep-learning segmentation; needs paired image | `pip install cellpose` |
| **No image, want fast estimate** | **SAINSC** (2024) or **stardist** | SAINSC: kernel-density cell calling from expression only | standalone |

> **Visium HD bin2cell**: full workflow (load → cellpose nuclei → expand → aggregate → sync geometries → quality check) is in `examples/visium_hd_bin2cell.py`. **Verified API** (omicverse 2.2.3): `ov.io.read_visium_hd` / `ov.space.visium_10x_hd_cellpose_expand` / `ov.space.bin2cell` / `ov.space.sync_visium_hd_seg_geometries`.

### Segmentation quality assessment (mandatory after segmenting)

1. **Cell count sanity**: too few cells (e.g. 500 from 6mm²) = under-segmentation; too many (e.g. 2M) = debris/over-segmentation. Compare to H&E morphology.
2. **Visual check**: `ov.pl.plot_spatial(adata, color='n_genes_by_counts')` — segmentation should follow tissue architecture.
3. **Border-cell handling**: cells at tissue edge may be truncated. Flag low-gene-count edge cells (`n_genes_by_counts < 50`), don't silently keep.

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
- After finishing, run `scripts/postcheck.py` (repo root) to verify spatial-coordinate integrity

## Resources
- `examples/squidpy_highres.py` — squidpy end-to-end (SVG / nhood / ligrec / hex bin)
- `examples/spatialdata_workflow.py` — SpatialData multi-platform load + region query + transcript aggregation
- `examples/visium_hd_bin2cell.py` — Visium HD bin→cell segmentation (bin2cell wrapped in omicverse)
- `examples/image_expression_integration.py` — histology image × gene expression integration (sq.im.process / segment / calculate_image_features + co_occurrence)
- `examples/transcript_to_cell.py` — transcript → cell mask assignment (cellpose / Baysor / built-in cell_id aggregation)
