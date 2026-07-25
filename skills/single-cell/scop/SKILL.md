---
name: scop-single-cell
description: 用 scop R 包做单细胞/空转全流程（基于 Seurat，133 verified Run* 动词 in scop 0.8.9）——QC/整合/注释/DE/轨迹/通讯/velocity/GRN/空间域/去卷积/组成型 DA。当用户要用 R、Seurat、scop、R 单细胞、standard_scop/integration_scop/RunPCA/RunUMAP/RunCellChat/RunSCVELO/RunMonocle3/RunSCENICPlus/RunMilo/RunRCTD/RunBANKSY 等 Run* 动词时触发。0.8.9 起 SCENIC+/Milo/scCODA/RCTD/BANKSY/SecAct/Giotto/EcoTyper/SCENIC 等已被 scop 包装。
---

## When NOT to use this skill
- Pure Python/AnnData-native large-scale analysis (>1M cells, AnnDataOOM backend) → `single-cell/omicverse-pipeline`
- Python-only spatial deconvolution via omicverse unified wrapper → `spatial/deconvolution` (but scop ALSO wraps RCTD/cell2location/SPOTlight/etc since 0.8.9)
- Predict unmeasured perturbation experiments → `single-cell/perturbation-prediction`
- Downstream analysis of measured Perturb-seq data → `single-cell/perturb-seq`
- moscot / CellOracle / SpatialGlue / MENDER / BINARY / GraphST / COMMOT / Baysor / bin2cell / cellpose — **NOT wrapped in scop 0.8.9**, use standalone packages (see `references/run_verbs_reference.md` Capability gaps table)

# scop — Single-Cell Omics Analysis Pipeline (R)

`scop` is an R package ([mengxu98/scop](https://github.com/mengxu98/scop), **v0.8.9** verified 2026-07-26, GPL-3) providing a unified pipeline for single-cell + spatial omics. It wraps **133 community tools** under consistent `Run*` verbs on the **Seurat** object (314 total exports), plus a one-call `standard_scop()` pipeline. Use this when the user prefers R/Seurat.

> **Capability scope (0.8.9)**: scop wraps QC / DR / clustering / integration (Harmony/scVI/fastMNN/WNN/CCA/RPCA/MultiMAP/Coralysis/GLUE and more) / annotation (SingleR/CellTypist/Scmap/SciBet/LabelTransfer/ReferenceMapping/CellCycle/scMalignant) / DE (pseudobulk + RareQ) / trajectory (Monocle2/3, Slingshot, PAGA, Palantir, CytoTRACE, CellRank, WOT, FitDevo, VECTOR, tAge) / velocity (SCVELO + SecActVelocity) / CCC (CellChat/CellphoneDB/LIANA/NicheNet/MultiNichenetr/MistyR/SecAct×5/SpatialCellChat/GiottoCellProximity) / GRN (SCENIC/SCENICPlus/CisTarget/GENIE3/GRNBoost2/scTenifoldKnk/Net) / spatial domains (BANKSY/BayesSpace/SmoothClust/MERINGUE/Giotto/Semla) / spatial deconvolution (RCTD/cell2location/SPOTlight/STdeconvolve/CytoSPACE/CARD/SpatialDWLS/CSIDE) / compositional DA (Milo/scCODA/Propeller/LISI/MDIC3/Statial/mcRigor) / CNV / pathway (GSVA/Dorothea/Augur/ESTIMATE/Metabolism/scFEA). Remaining gaps: see the **Capability gaps** table in `references/run_verbs_reference.md` (much shorter than 0.8.0).

## Installation

```r
if (!requireNamespace("remotes", quietly = TRUE)) install.packages("remotes")
remotes::install_github("mengxu98/scop")
# NOTE for upgraders: 0.8.0 → 0.8.9 pulls in heavy new deps (thisplot/thisutils/
# Signac/etc). If install fails on dependency resolution, install Seurat from
# CRAN first as BINARY (type="binary") to avoid source-compile timeouts, then
# install_github("mengxu98/scop", upgrade=FALSE) to avoid re-touching deps.

# Python interop (scop calls some Python tools via reticulate):
scop::check_python()           # verify reticulate + Python env
scop::PrepareEnv("scvelo")     # install a Python tool into the scop env
scop::ListEnv()                # list installed Python tools
```

Key R deps: `Seurat` (>=5.0.2; CRAN), `SeuratObject`, `Signac`, `ggplot2`, `ComplexHeatmap`, `reticulate`, plus scop's own `thisplot` (>=0.4.3) + `thisutils` (>=0.4.8) + `uwot`.

## Interop with Python / AnnData

```r
library(scop)
srt    <- adata_to_srt(adata)        # AnnData (Python) -> Seurat (verified)
adata  <- srt_to_adata(srt)          # Seurat -> AnnData (verified)
# Python env management (verified):
scop::check_python(); scop::PrepareEnv("scvelo"); scop::ListEnv(); scop::RemoveEnv()
```

> **NEW in 0.8.9** (previously NOT in scop 0.8.0): direct file/object converters `h5ad_to_srt` / `srt_to_h5ad`, `loom_to_adata` / `loom_to_srt`, `spe_to_srt` / `srt_to_spe` (SpatialExperiment), `spata2_to_srt` / `srt_to_spata2`, `srt_to_giotto` / `giotto_to_srt`, `ConvertHomologs` (cross-species). No more manual round-trip needed.

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

> **Full Run\* verb enumeration** (verified against scop 0.8.9; 133 Run\* verbs + 181 helpers across QC / DR / Clustering / Integration / Annotation / DE / Trajectory / Velocity / CCC / GRN / Spatial domains / Spatial deconvolution / Compositional DA / CNV / Pathway / Reference mapping / Datasets): see `references/run_verbs_reference.md`. That file also has the (now much shorter) **Capability gaps** table — capabilities NOT wrapped in scop and the standalone package to use instead. SKILL is the workflow + decisions; that file is the API lookup.

## Integration method ranking (2024-2026 benchmarks)

**Harmony / scVI / scANVI** are the SOTA defaults for the vast majority of single-cell integration. BBKNN is **only** worth considering for ultra-fast >500k-cell alignment (Luecken et al. Nat Methods 2022; OpenProblems v2 show it is otherwise outperformed). fastMNN is acceptable but no longer first-choice. **Combat is for bulk only — not recommended for scRNA-seq.** In scop, the unified entry is `integration_scop(object_list, method='Harmony', ...)` — `method` accepts Harmony / fastMNN / LIGER / scVI etc. (verify the method string against `?integration_scop` for your scop version).

## When to Use scop vs omicverse

| Situation | Use |
|---|---|
| Python-only environment, large-scale, AnnData-native | `omicverse-pipeline` skill |
| R/Seurat environment, or user prefers R | **scop (this skill)** |
| Tool wrapped in BOTH (CellChat, SCENIC+, Milo, RCTD, BANKSY, SecAct, cell2location, GSVA, Augur, …) | **either** — pick by your primary ecosystem. Since 0.8.9 scop wraps nearly everything omicverse does for these tools |
| Tool NOT in scop (moscot / CellOracle / SpatialGlue / MENDER / BINARY / GraphST / COMMOT / Baysor / bin2cell / cellpose) | **standalone packages** — see Capability gaps in `references/run_verbs_reference.md` |
| Python-native spatial workflow (Visium HD bin2cell, cellpose pipeline) | `spatial/multiomics` (omicverse Python) |
| Tool only in omicverse (AnnDataOOM million-cell backend, STAGATE/SpaceFlow/GASTON Python spatial) | `omicverse-pipeline` / `spatial/omicverse-spatial` |
| Need both ecosystems | Convert via `srt_to_adata` / `adata_to_srt` (or new `h5ad_to_srt` / `spe_to_srt` etc in 0.8.9) |

## Discipline (apply throughout)

- **DE rigor**: `RunDEtest` with `cells.group.by` for pseudobulk; avoid per-cell Wilcoxon for publication DE.
- **Batch-corrected embeddings for visualization/clustering only** — never feed integrated reductions into `RunDEtest`.
- **Preserve raw**: keep a non-normalized assay; `RecoverCounts()` to restore.
- **Conservative claims**: communication/trajectory/CNV are hypotheses — "associated with", not "regulates".
- **Spatial deconvolution**: report method + reference + quality metric; cross-check with marker co-expression.
- **Reproducibility**: record scop + Seurat versions; `sessionInfo()`; set seeds where tools expose them.

## Prerequisites (where data comes from)

- **scRNA-seq raw data** → 10x matrices from Cell Ranger / STARsolo (`Seurat::Read10X`), or convert h5ad/loom/SPE directly via `h5ad_to_srt` / `loom_to_srt` / `spe_to_srt` (all wrapped since 0.8.9)
- **Spatial data** → SpatialExperiment object (for `RunSpatial*` verbs) or Seurat with spatial coords; Giotto/Stereo-seq via `RunGiottoWorkflow`
- **Annotation reference** (optional, for `RunSingleR` / `RunCellTypist` / `RunScmap` / `RunLabelTransfer` / `RunReferenceMapping`) → annotated reference Seurat object, celldex/CellTypist model, or pre-trained scArches model
- **loom file** (for RNA velocity) → produced by velocyto, consumed by `RunSCVELO`; or use `loom_to_srt` / `loom_to_adata`

## When to leave this skill (where to go)

- Python/AnnData-native large-scale analysis (>1M cells) → `single-cell/omicverse-pipeline` (AnnDataOOM backend)
- Python-native spatial workflows (Visium HD bin2cell, cellpose segmentation, STAGATE/SpaceFlow/GASTON) → `spatial/multiomics` / `spatial/omicverse-spatial` (scop wraps BANKSY/BayesSpace/Giotto in R, but Python-native platforms need omicverse)
- Spatial proteomics (CODEX/IMC) → `spatial/proteomics`
- Perturbation prediction (unmeasured experiments; GRN-based virtual KO) → `single-cell/perturbation-prediction`; measured-perturbation analysis → `single-cell/perturb-seq`
- Move Seurat results back to Python for plotting → `srt_to_adata`, then `visualization/omicverse-plotting`
- Assemble publication-grade multi-panel figures → `visualization/multi-panel-figures`
- Write Methods / figure legends → `presentation/methods-writer` / `presentation/figure-legend-writer`

## Key pitfalls

- **scop ≠ Seurat**: scop is a wrapper layer with **133 Run\* verbs** (verified 0.8.9); calling Seurat functions directly does NOT go through this skill — LLMs easily confuse `RunPCA(scop)` with `Seurat::RunPCA`.
- **Verify before trusting any Run\* verb**: 0.8.9 added 94 new Run\* vs 0.8.0 — some tutorials may still reference the old surface. Before using a `RunX` not in `references/run_verbs_reference.md`, check `exists("RunX", where = asNamespace("scop"))` or run `scripts/scop_api_check.R`.
- **0.8.0 → 0.8.9 renames**: `RunDimReduction` was split into `RunDimsEstimate` + `RunDimsReduction`; `CellChatPlot` → `SpatialCellChatPlot`. Update old scripts.
- **Heavy dependency tree**: 0.8.9 introduces thisplot/thisutils/Signac + many tool-specific deps. If install fails, install Seurat as CRAN **binary** first, then `install_github(..., upgrade=FALSE)` to avoid source-compile timeouts.
- **Python ↔ R object conversion**: `srt_to_adata` / `adata_to_srt` is the boundary and may drop metadata/assay — verify obs/var columns before and after conversion.
- **Run\* argument pass-through**: each Run\* wraps a native R/Python function whose parameter names may differ (e.g. `RunHarmony2` vs `harmony::RunHarmony`, `RunSCENICPlus` vs `scenicplus.SCENIC+`) — check `?scop::RunX` for the real signature, do not rely on memory.
- **RunHarmony does not exist** — scop ships `RunHarmony2` and the unified `integration_scop(method='Harmony', ...)`. Prefer `integration_scop` as the entry.
- **DE still requires pseudobulk**: `RunDEtest` defaults to per-cell Wilcoxon; for publication-grade single-cell DE switch to pseudobulk (aggregate by sample × cell type, then DESeq2/edgeR) — meta-methodology principle ③.
- **Spatial backend check**: before spatial `Run*` verbs, run `SpatialBackendStatus()` to confirm the spatial backend (SpatialExperiment etc) is wired up.
- After finishing, run `scripts/postcheck.py` (repo root) to verify: DE used pseudobulk, Padj reported, integration diagnostics done, deconvolution quality assessed.

## Resources
- `references/run_verbs_reference.md` — 133 verified Run\* verbs organized by domain (QC/DR/Integration/Annotation/DE/Trajectory/Velocity/CCC/GRN/Spatial/Deconvolution/Composition/CNV/Pathway) + (short) Capability gaps table
- `scripts/scop_api_check.R` (repo root) — re-verify scop API surface after any scop upgrade
