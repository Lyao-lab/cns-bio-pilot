---
name: scop-single-cell
description: 用 scop R 包做单细胞全流程（基于 Seurat，40+ Run* 动词）——QC/整合/注释/DE/轨迹/通讯/velocity。当用户要用 R、Seurat、scop、R 单细胞、standard_scop/integration_scop/RunPCA/RunUMAP/RunCellChat/RunSCVELO/RunMonocle3 等 Run* 动词时触发。CytoTRACE/Palantir/CellChat 在 scop 有包装；SCENIC+/Milo/scCODA/RCTD/Giotto 等不在 scop，走独立包。
---

## When NOT to use this skill
- Pure Python/AnnData-native large-scale analysis (>1M cells, AnnDataOOM backend) → `single-cell/omicverse-pipeline`
- Spatial deconvolution (cell2location/Tangram/RCTD) → `spatial/deconvolution` (omicverse unified wrapper)
- Predict unmeasured perturbation experiments → `single-cell/perturbation-prediction`
- Downstream analysis of measured Perturb-seq data → `single-cell/perturb-seq`
- SCENIC+/Milo/scCODA/RCTD/Giotto/SecAct/EcoTyper/SmoothClust — **not wrapped in scop 0.8.0**, use standalone packages (see `references/run_verbs_reference.md` Capability gaps table)

# scop — Single-Cell Omics Analysis Pipeline (R)

`scop` is an R package ([mengxu98/scop](https://github.com/mengxu98/scop), **v0.8.0** verified, GPL-3) providing a unified pipeline for single-cell omics. It wraps ~40 community tools under consistent `Run*` verbs on the **Seurat** object, plus a one-call `standard_scop()` pipeline. Use this when the user prefers R/Seurat.

> **Capability honesty**: scop 0.8.0 has **~40 Run\* verbs** (not 200+, despite some older docs claiming that). It covers QC / DR / clustering / integration (via `integration_scop`) / annotation (SingleR/CellTypist/Scmap) / DE / trajectory (Monocle2/3, Slingshot, PAGA, Palantir, CytoTRACE, CellRank, WOT) / velocity (SCVELO) / CellChat / GSEA / proportion test. SCENIC+/Milo/scCODA/SecAct/Giotto/RCTD/BayesSpace/BANKSY and many others are **NOT wrapped** — see the Capability gaps table in `references/run_verbs_reference.md` for the standalone package to install.

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
srt    <- adata_to_srt(adata)        # AnnData (Python) -> Seurat (verified)
adata  <- srt_to_adata(srt)          # Seurat -> AnnData (verified)
# Python env management (verified):
scop::check_python(); scop::PrepareEnv("scvelo"); scop::ListEnv(); scop::RemoveEnv()
```

> **NOT in scop 0.8.0** (despite older docs): `h5ad_to_srt` / `srt_to_h5ad`, `spe_to_srt` / `srt_to_spe`, `loom_to_adata` / `loom_to_srt`. For these, save in Python (anndata/sceasy) then read into R, or use `adata_to_srt(srt_to_adata(...))` round-trip via reticulate.

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

> **Full Run\* verb enumeration** (verified against scop 0.8.0; ~40 verbs across QC / DR / Clustering / Integration / Annotation / DE / Trajectory / Velocity / CCC / Enrichment / Composition / Reference mapping / Datasets): see `references/run_verbs_reference.md`. That file also has the **Capability gaps** table — capabilities NOT wrapped in scop and the standalone package to use instead. SKILL is the workflow + decisions; that file is the API lookup.

## Integration method ranking (2024-2026 benchmarks)

**Harmony / scVI / scANVI** are the SOTA defaults for the vast majority of single-cell integration. BBKNN is **only** worth considering for ultra-fast >500k-cell alignment (Luecken et al. Nat Methods 2022; OpenProblems v2 show it is otherwise outperformed). fastMNN is acceptable but no longer first-choice. **Combat is for bulk only — not recommended for scRNA-seq.** In scop, the unified entry is `integration_scop(object_list, method='Harmony', ...)` — `method` accepts Harmony / fastMNN / LIGER / scVI etc. (verify the method string against `?integration_scop` for your scop version).

## When to Use scop vs omicverse

| Situation | Use |
|---|---|
| Python-only environment, large-scale, AnnData-native | `omicverse-pipeline` skill |
| R/Seurat environment, or user prefers R | **scop (this skill)** |
| Tool wrapped in scop (CytoTRACE, Palantir, CellChat, Monocle3, WOT, Slingshot, SCVELO) | **scop** |
| Tool NOT in scop (SCENIC+, Milo, scCODA, SecAct, Giotto, SmoothClust, EcoTyper, RCTD, BayesSpace, BANKSY) | **standalone packages** — see Capability gaps in `references/run_verbs_reference.md` |
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
- **Annotation reference** (optional, for `RunSingleR` / `RunCellTypist` / `RunScmap`) → annotated reference Seurat object or celldex/CellTypist model
- **loom file** (for RNA velocity) → produced by velocyto, consumed by `RunSCVELO`

## When to leave this skill (where to go)

- Python/AnnData-native large-scale analysis (>1M cells) → `single-cell/omicverse-pipeline` (AnnDataOOM backend)
- Spatial transcriptomics (Visium/Xenium/high-res) → `spatial/omicverse-spatial` / `spatial/deconvolution` / `spatial/multiomics` (omicverse Python unified; scop does NOT wrap spatial tools in 0.8.0)
- Spatial proteomics (CODEX/IMC) → `spatial/proteomics`
- Perturbation prediction (unmeasured experiments) → `single-cell/perturbation-prediction`; measured-perturbation analysis → `single-cell/perturb-seq`
- Move Seurat results back to Python for plotting → `srt_to_adata`, then `visualization/omicverse-plotting`
- Assemble publication-grade multi-panel figures → `visualization/multi-panel-figures`
- Write Methods / figure legends → `presentation/methods-writer` / `presentation/figure-legend-writer`

## Key pitfalls

- **scop ≠ Seurat**: scop is a wrapper layer with **~40 Run\* verbs** (verified 0.8.0); calling Seurat functions directly does NOT go through this skill — LLMs easily confuse `RunPCA(scop)` with `Seurat::RunPCA`.
- **Verify before trusting any Run\* verb**: scop has fewer verbs than some tutorials claim. Before using a `RunX` not in `references/run_verbs_reference.md`, check `exists("RunX", where = asNamespace("scop"))` or run `scripts/scop_api_check.R`.
- **Python ↔ R object conversion**: `srt_to_adata` / `adata_to_srt` is the boundary and may drop metadata/assay — verify obs/var columns before and after conversion.
- **Run\* argument pass-through**: each Run\* wraps a native R function whose parameter names may differ (e.g. `RunHarmony2` vs `harmony::RunHarmony`) — check `?scop::RunX` for the real signature, do not rely on memory.
- **RunHarmony does not exist** — scop 0.8.0 ships `RunHarmony2` and the unified `integration_scop(method='Harmony', ...)`. Prefer `integration_scop` as the entry.
- **DE still requires pseudobulk**: `RunDEtest` defaults to per-cell Wilcoxon; for publication-grade single-cell DE switch to pseudobulk (aggregate by sample × cell type, then DESeq2/edgeR) — meta-methodology principle ③.
- **SCENIC+/Milo/scCODA/RCTD/Giotto/SecAct are NOT in scop** — these tools require standalone installation. See Capability gaps table.
- **Spatial is NOT scop's strength in 0.8.0** — many `RunSpatial*` verbs listed in older docs do not exist. Prefer omicverse-spatial Python route for spatial work.
- After finishing, run `scripts/postcheck.py` (repo root) to verify: DE used pseudobulk, Padj reported, integration diagnostics done.

## Resources
- `references/run_verbs_reference.md` — ~40 verified Run\* verbs by domain + Capability gaps table (what's NOT in scop and the standalone package to use instead)
- `scripts/scop_api_check.R` (repo root) — re-verify scop API surface after any scop upgrade
