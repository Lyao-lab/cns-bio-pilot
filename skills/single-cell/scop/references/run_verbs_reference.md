# scop Run\* Verb Reference

API quick-reference for scop ([mengxu98/scop](https://github.com/mengxu98/scop), v0.8.9).
All verbs operate on a Seurat object `srt`. **Always check `?scop::RunX` for the real
signature** — each Run\* wraps a native R function whose parameter names may differ
(e.g. `scop::RunHarmony` vs `harmony::RunHarmony`).

> This file is the enumeration companion to `SKILL.md`. The SKILL keeps
> `standard_scop()` (one-call pipeline), Python interop, decision tables, and
> pitfalls; this file lists the 200+ Run\* verbs by domain so you don't have to
> grep the R package.

## QC & Preprocessing

```r
srt <- RunCellQC(srt, batch = "orig.ident",
                 nFeature_min = 300, mt_max = 20,
                 doublet_method = "Scrublet")   # "Scrublet" | "DoubletDetection" | "scDblFinder" | "scds"
srt <- RunDoubletCalling(srt, method = "Scrublet")
srt <- NormalizeData(srt, normalization.method = "LogNormalize")
srt <- FindVariableFeatures(srt, nfeatures = 2000)
srt <- ScaleData(srt, vars.to.regress = c("nCount_RNA","percent.mt"), do.scale = TRUE)
srt <- RunCellCycle(srt, species = "human", group.by = "orig.ident")
srt <- SCTransform(srt, vars.to.regress = "percent.mt")
srt <- RecoverCounts(srt)   # restore raw counts after transformations
```

## Dimensionality Reduction

```r
srt <- RunPCA(srt, npcs = 50)
srt <- RunDimsEstimate(srt)         # elbow + JackStraw to pick PCs
srt <- RunUMAP(srt, dims = 1:30)    # or RunUMAP2 (umap2)
srt <- RunMDS(srt, dims = 1:30)
srt <- RunNMF(srt); srt <- RunGLMPCA(srt)
srt <- RunPHATE(srt); srt <- RunPaCMAP(srt); srt <- RunTriMap(srt); srt <- RunLargeVis(srt)
```

## Clustering & Neighbors

```r
srt <- FindNeighbors(srt, dims = 1:30)
srt <- RunFR(srt, resolution = 0.6)        # FindClusters wrapper
srt <- RenameClusters(srt, new.names = c("T cell","B cell"))
```

## Batch Integration (20+ methods, consistent interface)

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
i <- CSS_integrate(obj_list); i <- GLUE_integrate(obj_list)
i <- Harmony5_integrate(obj_list); i <- Seurat_integrate(obj_list)
i <- Uncorrected_integrate(obj_list)                          # control
LISIPlot(i, group.by = "orig.ident")                          # integration diagnostics
```

> **Integration-method ranking (2024-2026 benchmarks)**: **Harmony / scVI / scANVI** are the SOTA defaults for the vast majority of single-cell integration. BBKNN is **only** worth considering for ultra-fast >500k-cell alignment; Luecken et al. (Nat Methods 2022) and OpenProblems v2 show it is otherwise outperformed. fastMNN is acceptable but no longer first-choice. **Combat is for bulk only — not recommended for scRNA-seq.**

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
srt <- ConvertHomologs(srt, from = "human", to = "mouse")   # cross-species
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
srt <- RunCellRank(srt); srt <- RunWOT(srt)   # Wagner / optimal transport
```

## RNA Velocity (Python interop)

```r
srt <- RunSCVELO(srt, mode = "dynamical",   # requires reticulate + scvelo
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
srt <- RunDorothea(srt)   # TF activity (DoRothEA)
```

## CNV / Metabolism / Malignancy

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

## Spatial Transcriptomics (Visium / Xenium / high-res)

```r
# Loading + QC
srt <- RunSpotQC(srt); srt <- RunSpatialQM(srt)
# Spatial neighborhood / SVGs / domains
srt <- RunSpatialNeighborhood(srt)       # spatial neighbor graph (MUST run first)
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
# Cell-level
CellDimPlot(srt, group.by = "cell_type", reduction = "umap")
CellDimPlot3D(srt, reduction = "umap2")
FeatureDimPlot(srt, features = c("CD3D","MS4A1"))
FeatureHeatmap(srt, features = markers, group.by = "cell_type")
GroupHeatmap(srt, group.by = "cell_type")
# DE
VolcanoPlot(de)
DEtestPlot(de); DEtestManhattanPlot(de); DEtestRingPlot(de)
# Trajectory
PseudotimeProjectionPlot(srt)
PAGAPlot(srt); LineagePlot(srt); BranchStreamPlot(srt)
CytoTRACEPlot(srt); FitDevoPlot(srt)
# Communication
CCCHeatmap(ccc); CCCNetworkPlot(ccc); CCCStatPlot(ccc); FerrisWheelPlot(ccc)
SCENICPlot(regulonAUC)
# Enrichment
GSEAPlot(gsea); GSVAPlot(gsva); EnrichmentPlot(enr)
DynamicHeatmap(srt, along = "pseudotime")
# Stats / clustering
CellStatPlot(srt, group.by = "cell_type")
CellDensityPlot(srt, reduction = "umap")
ClusterTreePlot(srt)
LISIPlot(integrated, group.by = "orig.ident")
ProjectionPlot(srt, ref = ref_srt)       # reference mapping viz
CellCorHeatmap(srt)
# Spatial
SpatialSpotPlot(srt)
SpatialVariableFeaturePlot(srt)
SpatialNeighborhoodPlot(srt)
SpatialIntegrationPlot(srt)
GiottoPlot(giotto_obj)
STdeconvolvePlot(srt)
SpatialGradientPlot(srt)
SpatialEcoTyperSpatialPlot(srt); SpatialEcoTyperCompositionPlot(srt)
# Other omics
ScissorPlot(srt); CNVPlot(srt)
MetabolismPlot(srt)
# ...and more: NMFHeatmap, DynamicHeatmap, TACSPlot, VECTORPlot, etc.
```

## Built-in Datasets

```r
ListScopDatasets()                # list available demo datasets
srt <- LoadScopDataset("pbmc3k")
```
