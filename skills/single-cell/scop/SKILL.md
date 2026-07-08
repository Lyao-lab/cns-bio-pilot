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
# Release from GitHub (requires R >= 4.1.0)
if (!requireNamespace("remotes", quietly = TRUE)) install.packages("remotes")
remotes::install_github("mengxu98/scop")

# Python interop (scop calls some Python tools via reticulate):
scop::check_python()        # verify reticulate + Python env
scop::PrepareEnv("scvelo")  # install a Python tool into the scop env
scop::ListEnv()             # list installed Python tools
scop::remove_python("scvelo")  # remove
```

Key R deps: `Seurat`, `SeuratObject`, `Signac`, `ggplot2`, `ComplexHeatmap`, `reticulate`. scop also ships its own `thisplot` + `thisutils` helpers.

## Interop with Python / AnnData

scop is Seurat-centric but converts freely:

```r
library(scop)
srt  <- adata_to_srt(adata)   # AnnData (Python) -> Seurat (via reticulate)
adata <- srt_to_adata(srt)    # Seurat -> AnnData
srt  <- h5ad_to_srt("data.h5ad")
srt_to_h5ad(srt, "out.h5ad")
# SpatialExperiment interop
srt  <- spe_to_srt(spe); srt_to_spe(srt)
# Loom
adata <- loom_to_adata("data.loom"); srt <- loom_to_srt("data.loom")
```

## Standard Pipeline (one call)

`standard_scop()` runs QC → normalization → HVG → scaling → PCA → neighbors → UMAP → Leiden/Louvain clustering in one go:

```r
library(scop)
srt <- standard_scop(
  srt,
  assay = "RNA",
  batch = "orig.ident",     # batch key for QC/scaling
  cluster_resolution = 0.6, # single value or vector
  nFeature_min = 300, nFeature_max = Inf,
  nCount_min = 500,  nCount_max = Inf,
  mt_max = 20,              # max mito %
  normalization = "LogNormalize",  # or "SCT" via SCTransform
  nVariableFeatures = 2000,
  npca = 50,
  reduction = "umap",       # "umap" | "umap2" | "tsne" | "phate" | "pacmap" | "trimap" | "largevis"
  dims_estimation = TRUE,   # auto-estimate optimal PC number
  cluster = TRUE,
  redo_reduction = FALSE
)
```

For fine control, run the steps individually (sections below).

## QC & Preprocessing

```r
# Cell QC (mito/UMI/gene thresholds; doublet calling)
srt <- RunCellQC(srt, batch = "orig.ident",
                 nFeature_min = 300, mt_max = 20,
                 doublet_method = "Scrublet")  # "Scrublet" | "DoubletDetection" | "scDblFinder" | "scds"
srt <- RunDoubletCalling(srt, method = "Scrublet")
# Normalization & HVG
srt <- NormalizeData(srt, normalization.method = "LogNormalize")
srt <- FindVariableFeatures(srt, nfeatures = 2000)
srt <- ScaleData(srt, vars.to.regress = c("nCount_RNA","percent.mt"), do.scale = TRUE)
# Cell cycle scoring
srt <- RunCellCycle(srt, species = "human", group.by = "orig.ident")
# SCTransform alternative
srt <- SCTransform(srt, vars.to.regress = "percent.mt")
# Recover raw counts after transformations
srt <- RecoverCounts(srt)
```

## Dimensionality Reduction

```r
srt <- RunPCA(srt, npcs = 50)
srt <- RunDimsEstimate(srt)         # elbow + JackStraw to pick PCs
srt <- RunUMAP(srt, dims = 1:30)    # or RunUMAP2 (umap2)
srt <- RunMDS(srt, dims = 1:30)
srt <- RunNMF(srt)                  # also RunGLMPCA
srt <- RunPHATE(srt); srt <- RunPaCMAP(srt); srt <- RunTriMap(srt); srt <- RunLargeVis(srt)
```

## Clustering & Neighbors

```r
srt <- FindNeighbors(srt, dims = 1:30)
srt <- RunFR(srt, resolution = 0.6)        # FindClusters wrapper
srt <- RenameClusters(srt, new.names = c("T cell","B cell"))  # rename after annotation
```

## Batch Integration (15+ methods, consistent interface)

```r
integrated <- integration_scop(           # unified entry, auto-pick method
  object_list, method = "Harmony",
  batch = "orig.ident", reference = NULL, dims = 1:30
)
# Or call each directly:
i <- Harmony_integrate(srt, batch = "orig.ident")
i <- CCA_integrate(obj_list, reference = NULL, dims = 1:30)   # Seurat anchor CCA
i <- RPCA_integrate(obj_list, dims = 1:30)                    # reciprocal PCA
i <- scVI_integrate(obj_list); i <- scVI5_integrate(obj_list)
i <- BBKNN_integrate(srt); i <- MNN_integrate(obj_list)
i <- fastMNN_integrate(obj_list); i <- fastMNN5_integrate(obj_list)
i <- LIGER_integrate(obj_list); i <- Scanorama_integrate(obj_list)
i <- Conos_integrate(obj_list); i <- Coralysis_integrate(obj_list)
i <- MultiMAP_integrate(obj_list); i <- WNN_integrate(obj_list)  # weighted multi-modal
```

> **Integration-method ranking (2024-2026 benchmarks)**: **Harmony / scVI / scANVI** are the SOTA defaults for the vast majority of single-cell integration. BBKNN is **only** worth considering for ultra-fast >500k-cell alignment; Luecken et al. (Nat Methods 2022) and OpenProblems v2 show it is otherwise outperformed. fastMNN is acceptable but no longer first-choice. **Combat is for bulk only — not recommended for scRNA-seq.**
i <- CSS_integrate(obj_list); i <- GLUE_integrate(obj_list)
i <- Harmony5_integrate(obj_list); i <- Seurat_integrate(obj_list)
i <- Uncorrected_integrate(obj_list)                          # control
# Integration diagnostics
LISIPlot(i, group.by = "orig.ident")
```

## Cell Annotation

```r
srt <- RunSingleR(srt, ref = "HumanPrimaryCellAtlas")   # celldex references
srt <- RunCellTypist(srt, model = "Immune_All_Low.pkl") # Python CellTypist via reticulate
srt <- TrainCellTypist(srt, label = "cell_type")        # train a custom model
srt <- RunSciBet(srt, ref = ref_srt, label = "cell_type")
srt <- RunScmap(srt, ref = ref_srt)
srt <- RunKNNPredict(srt, ref = ref_srt, label = "cell_type")
srt <- RunLabelTransfer(srt, ref = ref_srt)
srt <- RunReferenceMapping(srt, ref_key = "azimuth")
srt <- RunAugur(srt, label = "condition")               # cell-type prioritize
# Convert homologs (cross-species)
srt <- ConvertHomologs(srt, from = "human", to = "mouse")
```

## Marker Genes & Differential Expression

```r
# Per-cell Wilcoxon (exploratory); for rigorous DE prefer pseudobulk (RunDEtest)
srt <- FindAllMarkers(srt, only.pos = TRUE, min.pct = 0.25)
srt <- FindMarkers(srt, ident.1 = "T cell", ident.2 = "B cell")
# Rigorous DE (pseudobulk, bulk, or per-cell with proper model)
de <- RunDEtest(srt, group.by = "condition",
                method = "DESeq2",    # "DESeq2" | "edgeR" | "limma" | "MAST" | "Wilcox"
                cells.group.by = "cell_type",  # pseudobulk aggregate
                batch = "orig.ident")
fc <- FoldChange(srt, ident.1 = "A", ident.2 = "B")
```

## Trajectory & Pseudotime

```r
srt <- RunMonocle3(srt); srt <- RunMonocle2(srt)
srt <- RunSlingshot(srt)
srt <- RunPAGA(srt)
srt <- RunPalantir(srt); srt <- RunCytoTRACE(srt)
srt <- RunCellRank(srt); srt <- RunWOT(srt)        # Wagner/Optimal transport
```

## RNA Velocity (Python interop)

```r
srt <- RunSCVELO(srt, mode = "dynamical",     # requires reticulate + scvelo
                 loom_path = "velocyto.loom")
VelocityPlot(srt)
```

## Cell-Cell Communication (10+ tools)

```r
srt <- RunCellChat(srt, group.by = "cell_type")
srt <- RunCellphoneDB(srt, group.by = "cell_type")
srt <- RunLIANA(srt)
srt <- RunNichenetr(srt); srt <- RunMultiNichenetr(srt)
srt <- RunSecAct(srt)            # signaling activity
srt <- RunSecActCCC(srt)         # CCC with signaling activity
```

## Gene Regulatory Network

```r
srt <- RunSCENIC(srt); srt <- RunSCENICPlus(srt)   # SCENIC/SCENIC+ (Python interop)
srt <- RunGENIE3(srt); srt <- RunGRNBoost2(srt)
```

## Enrichment & Pathway

```r
srt <- RunGSEA(srt, geneset = "H")
srt <- RunGSVA(srt, geneset = "C2")
srt <- RunEnrichment(srt, group.by = "cell_type")
srt <- RunDynamicEnrichment(srt, along = "pseudotime")
srt <- RunDorothea(srt)          # TF activity (DoRothEA)
```

## CNV, Metabolism, Malignancy

```r
srt <- RunCNV(srt)                       # inferCNV-style
srt <- RunMetabolism(srt)                # scMetabolism-style
srt <- RunscMalignantFinder(srt); srt <- RunscMalignantRegion(srt)
srt <- RunscTenifoldKnk(srt)             # malignant gene-module knockout (R scTenifoldKnk)
```

> **Note**: `scTenifoldKnk` is the R lightweight screening path within GRN-based virtual knockout. For Python GRN-KO (CellOracle / SCENIC+) or ML-based perturbation prediction (GEARS / CPA / scGPT), use `single-cell/perturbation-prediction` Route B / Route A instead.

## Composition / Differential Abundance

```r
srt <- RunMilo(srt)                      # neighborhood-level DA
srt <- RunscCODA(srt)                    # compositional analysis
srt <- RunPropeller(srt)                 # cell-type proportion
srt <- RunProportionTest(srt)
```

## Spatial Transcriptomics (Visium/Xenium/high-res)

scop unifies spatial tools on the same Seurat object:

```r
# Loading + QC
srt <- RunSpotQC(srt); srt <- RunSpatialQM(srt)
# Spatial neighborhood / SVGs / domains
srt <- RunSpatialNeighborhood(srt)       # spatial neighbor graph
srt <- RunSpatialVariableFeatures(srt)   # SVGs
srt <- RunBayesSpace(srt); srt <- RunBANKSY(srt)   # spatial domains
# Deconvolution (many methods)
srt <- RunSpatialDWLS(srt); srt <- RunRCTD(srt)
srt <- RunCARD(srt); srt <- RunSPOTlight(srt)
srt <- RunSTdeconvolve(srt); srt <- RunCytoSPACE(srt)
srt <- RunDeconvolution(srt, method = "RCTD")
srt <- RunSmoothClust(srt)               # smooth expression
srt <- RunCSIDE(srt)                     # differential expression in spatial
srt <- RunSpaNorm(srt)                   # spatial normalization
# Giotto workflow (high-res: Stereo-seq / Visium HD)
srt <- RunGiottoWorkflow(srt)
srt <- RunGiottoCluster(srt); srt <- RunGiottoSpatialGenes(srt)
srt <- RunGiottoSpatialModules(srt); srt <- RunGiottoCellProximity(srt)
# Spatial integration across sections
srt <- RunSpatialIntegration(srt, batch = "section")
# Region-level analyses
srt <- RunSpatialEcoTyper(srt)
srt <- RunSpatialGradientFeatures(srt)
srt <- RunSemlaLocalG(srt); srt <- RunSemlaRadialDistance(srt)
srt <- RunSemlaRegionNeighbors(srt); srt <- RunSemlaSpatialNetwork(srt)
srt <- RunMERINGUE(srt)                  # spatially variable genes
```

## Visualization (thisplot integration)

scop pairs with `thisplot`. Representative plotters (consistent ggplot grammar):

```r
CellDimPlot(srt, group.by = "cell_type", reduction = "umap")
CellDimPlot3D(srt, reduction = "umap2")
FeatureDimPlot(srt, features = c("CD3D","MS4A1"))
FeatureHeatmap(srt, features = markers, group.by = "cell_type")
GroupHeatmap(srt, group.by = "cell_type")
VolcanoPlot(de)
DEtestPlot(de); DEtestManhattanPlot(de); DEtestRingPlot(de)
PseudotimeProjectionPlot(srt)
PAGAPlot(srt); LineagePlot(srt); BranchStreamPlot(srt)
CytoTRACEPlot(srt); FitDevoPlot(srt)
CCCHeatmap(ccc); CCCNetworkPlot(ccc); CCCStatPlot(ccc); FerrisWheelPlot(ccc)
SCENICPlot(regulonAUC)
GSEAPlot(gsea); GSVAPlot(gsva); EnrichmentPlot(enr)
DynamicHeatmap(srt, along = "pseudotime")
CellStatPlot(srt, group.by = "cell_type")
CellDensityPlot(srt, reduction = "umap")
ClusterTreePlot(srt)
LISIPlot(integrated, group.by = "orig.ident")
ProjectionPlot(srt, ref = ref_srt)       # reference mapping viz
CellCorHeatmap(srt)
# Spatial plotters
SpatialSpotPlot(srt)
SpatialVariableFeaturePlot(srt)
SpatialNeighborhoodPlot(srt)
SpatialIntegrationPlot(srt)
GiottoPlot(giotto_obj)
STdeconvolvePlot(srt)
SpatialGradientPlot(srt)
SpatialEcoTyperSpatialPlot(srt); SpatialEcoTyperCompositionPlot(srt)
ScissorPlot(srt); CNVPlot(srt)
MetabolismPlot(srt)
# ...and more: NMFHeatmap, DynamicHeatmap, TACSPlot, VECTORPlot, etc.
```

## Built-in Datasets

```r
ListScopDatasets()           # list available demo datasets
srt <- LoadScopDataset("pbmc3k")
```

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

- **scop ≠ Seurat**: scop is a wrapper layer with 200+ Run* verbs; calling Seurat functions directly does NOT go through this skill — LLMs easily confuse `RunPCA(scop)` with `Seurat::RunPCA`.
- **Python ↔ R object conversion**: `srt_to_adata` / `adata_to_srt` is the boundary and may drop metadata/assay — verify obs/var columns before and after conversion.
- **Run* argument pass-through**: each Run* wraps a native R function whose parameter names may differ (e.g. `RunHarmony` vs `harmony::RunHarmony`) — check `?scop::RunX` for the real signature, do not rely on memory.
- **SCENIC+/CellChat and similar downstream tools are version-sensitive**: scop depends on SCENIC+ v1.x and CellChat v2; mismatched versions crash Run* — confirm the R environment versions.
- **DE still requires pseudobulk**: `RunDEtest` defaults to per-cell Wilcoxon; for publication-grade single-cell DE switch to pseudobulk (aggregate by sample × cell type, then DESeq2/edgeR) — meta-methodology principle ③.
- **scop-only tools are the differentiator**: CytoTRACE/Milo/SecAct/EcoTyper/Giotto/SmoothClust have no omicverse equivalent — when the user wants these, route to scop, not omicverse.
- **Spatial analysis lives in scop**: RunGiotto/RunBayesSpace/RunRCTD here vs the omicverse-spatial Python route — results are not directly comparable.
