---
name: scop-single-cell
description: 用 scop R 包做单细胞 + 空间转录组全流程（200+ Run* 动词，基于 Seurat）——QC/整合/注释/DE/轨迹/通讯/GRN/CNV/代谢/空转。当用户要用 R、Seurat、scop、R 单细胞、RunPCA/RunUMAP/RunHarmony/RunCellChat/RunSCENIC/standard_scop/integration_scop 等 Run* 动词、或在 R 生态做 CytoTRACE/Milo/SecAct/Giotto/SmoothClust 等 omicverse 无对应工具时触发。
---

## When NOT to use this skill
- Pure Python/AnnData-native large-scale analysis (>1M cells, AnnDataOOM backend) → `single-cell/omicverse-pipeline`
- cell2location deconvolution (not registered in omicverse, absent from scop too) → `spatial/deconvolution`
- Predict unmeasured perturbation experiments → `single-cell/perturbation-prediction`
- Downstream analysis of measured Perturb-seq data → `single-cell/perturb-seq`

# scop — Single-Cell & Spatial Omics Analysis Pipeline (R)

`scop` is an R package ([mengxu98/scop](https://github.com/mengxu98/scop), v0.8.9, GPL-3) providing a unified, end-to-end pipeline for single-cell and spatial omics. It wraps hundreds of community tools under consistent `Run*` verbs on the **Seurat** object. Use this when the user prefers R/Seurat or needs a tool that omicverse does not cover.

## Installation

```r
if (!requireNamespace("remotes", quietly = TRUE)) install.packages("remotes")
remotes::install_github("mengxu98/scop")

# Python interop (scop calls some Python tools via reticulate):
scop::check_python()           # verify reticulate + Python env
scop::PrepareEnv("scvelo")     # install a Python tool into the scop env
scop::ListEnv()                # list installed Python tools
```

Key R deps: `Seurat`, `SeuratObject`, `Signac`, `ggplot2`, `ComplexHeatmap`, `reticulate`. scop also ships its own `thisplot` + `thisutils` helpers.

## Interop with Python / AnnData

```r
library(scop)
srt  <- adata_to_srt(adata)        # AnnData (Python) -> Seurat (via reticulate)
adata <- srt_to_adata(srt)         # Seurat -> AnnData
srt  <- h5ad_to_srt("data.h5ad"); srt_to_h5ad(srt, "out.h5ad")
srt  <- spe_to_srt(spe); srt_to_spe(srt)                       # SpatialExperiment
adata <- loom_to_adata("data.loom"); srt <- loom_to_srt("data.loom")
```

## Standard Pipeline (one call)

`standard_scop()` runs QC → normalization → HVG → scaling → PCA → neighbors → UMAP → Leiden/Louvain clustering in one go. This is the canonical entry; for fine control run steps individually (see `references/run_verbs_reference.md`).

```r
srt <- standard_scop(
  srt,
  assay = "RNA",
  batch = "orig.ident",            # batch key for QC/scaling
  cluster_resolution = 0.6,        # single value or vector
  nFeature_min = 300, nFeature_max = Inf,
  nCount_min = 500,  nCount_max = Inf,
  mt_max = 20,                     # max mito % (tissue-dependent — diagnose first, see omicverse-pipeline §2 tissue table)
  normalization = "LogNormalize",  # or "SCT" via SCTransform
  nVariableFeatures = 2000,
  npca = 50,
  reduction = "umap",              # "umap" | "umap2" | "tsne" | "phate" | "pacmap" | "trimap" | "largevis"
  dims_estimation = TRUE,          # auto-estimate optimal PC number
  cluster = TRUE,
  redo_reduction = FALSE
)
```

> **Full Run\* verb enumeration** (QC / DR / Clustering / 20+ Integration methods / Annotation / DE / Trajectory / Velocity / CCC / GRN / Enrichment / CNV / Composition / 30+ Spatial verbs / 35+ Plotters / Datasets): see `references/run_verbs_reference.md`. That file is the API lookup; this SKILL is the workflow + decisions.

## Integration method ranking (2024-2026 benchmarks)

**Harmony / scVI / scANVI** are the SOTA defaults for the vast majority of single-cell integration. BBKNN is **only** worth considering for ultra-fast >500k-cell alignment (Luecken et al. Nat Methods 2022; OpenProblems v2 show it is otherwise outperformed). fastMNN is acceptable but no longer first-choice. **Combat is for bulk only — not recommended for scRNA-seq.** Full verb list: `Harmony_integrate` / `scVI_integrate` / `CCA_integrate` / `RPCA_integrate` / `BBKNN_integrate` / `fastMNN_integrate` / `LIGER_integrate` / `Scanorama_integrate` / `WNN_integrate` / `CSS_integrate` / `GLUE_integrate` / etc.

## When to Use scop vs omicverse

| Situation | Use |
|---|---|
| Python-only environment, large-scale, AnnData-native | `omicverse-pipeline` skill |
| R/Seurat environment, or user prefers R | **scop (this skill)** |
| Tool only in scop (e.g., CytoTRACE, Milo, scCODA, SecAct, Giotto, SmoothClust, EcoTyper, scTenifold) | **scop** |
| Tool only in omicverse (AnnDataOOM million-cell backend) | `omicverse-pipeline` |
| Need both ecosystems | Convert via `srt_to_adata` / `adata_to_srt` |

## Discipline (apply throughout)

- **DE rigor**: `RunDEtest` with `cells.group.by` for pseudobulk; avoid per-cell Wilcoxon for publication DE.
- **Batch-corrected embeddings for visualization/clustering only** — never feed integrated reductions into `RunDEtest`.
- **Preserve raw**: keep a non-normalized assay; `RecoverCounts()` to restore.
- **Conservative claims**: communication/trajectory/CNV are hypotheses — "associated with", not "regulates".
- **Spatial deconvolution**: report method + reference + quality metric; cross-check with marker co-expression.
- **Reproducibility**: record scop + Seurat versions; `sessionInfo()`; set seeds where tools expose them.

## Prerequisites (where data comes from)

- **scRNA-seq raw data** → 10x matrices from Cell Ranger / STARsolo (`Read10X`), or `.h5`/`.loom`/`.h5ad` (`h5ad_to_srt` / `loom_to_srt`)
- **Spatial data** → Visium/Xenium output (`Load10X_Spatial`), or convert from AnnData via `adata_to_srt`
- **Annotation reference** (optional, for `RunSingleR`/`RunSciBet`/`RunCellTypist`) → annotated reference Seurat object or celldex/CellTypist model
- **loom file** (for RNA velocity) → produced by velocyto, consumed by `RunSCVELO`
- **Spatial neighbor graph** (for the spatial workflow) → `RunSpatialNeighborhood` MUST run first; all spatial domain / SVG / communication steps depend on it

## When to leave this skill (where to go)

- Python/AnnData-native large-scale analysis (>1M cells) → `single-cell/omicverse-pipeline` (AnnDataOOM backend)
- Standalone cell2location deconvolution (not registered in omicverse) → `spatial/deconvolution`
- Dedicated high-res spatial workflow (Stereo-seq / Visium HD) → `spatial/multiomics`
- Spatial proteomics (CODEX/IMC) → `spatial/proteomics`
- Perturbation prediction (unmeasured experiments) → `single-cell/perturbation-prediction`; measured-perturbation analysis → `single-cell/perturb-seq`
- Move Seurat results back to Python for plotting → `srt_to_adata`, then `visualization/omicverse-plotting`
- Assemble publication-grade multi-panel figures → `visualization/multi-panel-figures`
- Write Methods / figure legends → `presentation/methods-writer` / `presentation/figure-legend-writer`

## Key pitfalls

- **scop ≠ Seurat**: scop is a wrapper layer with 200+ Run\* verbs; calling Seurat functions directly does NOT go through this skill — LLMs easily confuse `RunPCA(scop)` with `Seurat::RunPCA`.
- **Python ↔ R object conversion**: `srt_to_adata` / `adata_to_srt` is the boundary and may drop metadata/assay — verify obs/var columns before and after conversion.
- **Run\* argument pass-through**: each Run\* wraps a native R function whose parameter names may differ (e.g. `RunHarmony` vs `harmony::RunHarmony`) — check `?scop::RunX` for the real signature, do not rely on memory.
- **SCENIC+/CellChat and similar downstream tools are version-sensitive**: scop depends on SCENIC+ v1.x and CellChat v2; mismatched versions crash Run\* — confirm the R environment versions.
- **DE still requires pseudobulk**: `RunDEtest` defaults to per-cell Wilcoxon; for publication-grade single-cell DE switch to pseudobulk (aggregate by sample × cell type, then DESeq2/edgeR) — meta-methodology principle ③.
- **scop-only tools are the differentiator**: CytoTRACE/Milo/SecAct/EcoTyper/Giotto/SmoothClust have no omicverse equivalent — when the user wants these, route to scop, not omicverse.
- **Spatial analysis lives in scop**: RunGiotto/RunBayesSpace/RunRCTD here vs the omicverse-spatial Python route — results are not directly comparable.
- After finishing, run `scripts/postcheck.py` (repo root) to verify: DE used pseudobulk, Padj reported, integration diagnostics done.

## Resources
- `references/run_verbs_reference.md` — 200+ Run\* verbs by domain (QC / DR / Clustering / Integration / Annotation / DE / Trajectory / Velocity / CCC / GRN / Enrichment / CNV / Composition / Spatial / 35+ Plotters / Datasets)
