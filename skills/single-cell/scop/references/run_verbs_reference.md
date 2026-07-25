# scop API Reference (verified against scop 0.8.9)

> **All Run\* verbs + helpers below verified via `getNamespaceExports("scop")` on scop 0.8.9** (314 total exports; 133 Run\* verbs). Re-verify after any scop upgrade by running `scripts/scop_api_check.R` (repo root).
>
> **Major change 0.8.0 → 0.8.9** (2026-07-26 upgrade): scop grew from 40 → 133 Run\* verbs. Almost every capability previously listed in the "Capability gaps" table (SCENIC+/Milo/RCTD/BANKSY/SecAct/EcoTyper/Giotto/SmoothClust/scCODA/CARD/SPOTlight/CytoSPACE/CNV/GSVA/Dorothea/Augur/scTenifoldKnk/…) is **now wrapped**. The gaps table below is correspondingly much shorter.

All verbs operate on a Seurat object `srt` (or SpatialExperiment for some spatial verbs — check `?scop::RunX`). **Always check `?scop::RunX` for the real signature** — each Run\* wraps a native R/Python function whose parameter names may differ from what you expect.

> Companion to `SKILL.md`. SKILL keeps `standard_scop()` (one-call pipeline), Python interop, decision tables, and pitfalls; this file enumerates the verified scop API.

## QC & Preprocessing (7)

```r
srt <- RunCellQC(srt, batch = "orig.ident",
                 nFeature_min = 300, mt_max = 20,
                 doublet_method = "Scrublet")   # "Scrublet" | "DoubletDetection" | "scDblFinder" | "scds"
srt <- RunDoubletCalling(srt, method = "Scrublet")
srt <- RunDecontX(srt, ...)                      # ambient RNA / contamination deconvolution (NEW in 0.8.9)
srt <- RecoverCounts(srt)                        # restore raw counts after transformations
# Spatial QC (for SpatialExperiment / spot data):
srt <- RunSpatialQM(srt, ...)
srt <- RunSpotQC(srt, ...)
srt <- RunSpotSweeper(srt, ...)
# ATAC QC:
srt <- RunATACQC(srt, ...)
```

> Cell cycle scoring now wrapped: `RunCellCycle(srt, method="Seurat"|"cyclone"|"tricycle")` (NEW — see Annotation section).

## Dimensionality Reduction (13)

```r
srt <- RunDimsEstimate(srt, ...)          # elbow/JackStraw-style dims estimation (NEW, replaces manual)
srt <- RunDimsReduction(srt, ...)         # unified DR dispatcher (was RunDimReduction in 0.8.0 — RENAMED)
srt <- RunPCA(srt, npcs = 50)
srt <- RunUMAP(srt, dims = 1:30)
srt <- RunUMAP2(srt, dims = 1:30)         # scop's umap2 variant
srt <- RunMDS(srt, dims = 1:30)
srt <- RunNMF(srt); srt <- RunGLMPCA(srt)
srt <- RunDM(srt); srt <- RunPHATE(srt); srt <- RunPaCMAP(srt)
srt <- RunTriMap(srt); srt <- RunLargeVis(srt)
srt <- RunPCAMap(srt)
```

> **API change**: 0.8.0's `RunDimReduction` was split into `RunDimsEstimate` (how many PCs) + `RunDimsReduction` (compute embeddings). Update old scripts.

## Clustering & Neighbors

```r
FindNeighbors(srt, dims = 1:30)            # Seurat-native
srt <- RunFR(srt, resolution = 0.6)        # scop's FindClusters wrapper
srt <- RunSpatialNeighborhood(srt, ...)    # spatial neighbor graph (NEW)
srt <- RunGiottoCluster(srt, ...)          # Giotto-style clustering (NEW)
srt <- RunSemlaRegionNeighbors(srt, ...)   # semla region neighbors (NEW)
srt <- RenameClusters(srt, new.names = c("T cell","B cell"))
srt <- RenameFeatures(srt, ...)
srt <- srt_reorder(srt, ...); srt <- srt_append(srt, ...)
```

## Batch Integration

```r
# Unified entry — recommended:
integrated <- integration_scop(object_list, method = "Harmony",
                               batch = "orig.ident", reference = NULL, dims = 1:30)
# Direct per-method verbs (verified exports):
i <- Harmony_integrate(srt, batch = "orig.ident")
i <- fastMNN_integrate(obj_list);  i <- MNN_integrate(obj_list)
i <- LIGER_integrate(obj_list);    i <- Conos_integrate(obj_list)
i <- Scanorama_integrate(obj_list); i <- BBKNN_integrate(srt)
i <- scVI_integrate(obj_list);     i <- CSS_integrate(obj_list)
i <- Seurat_integrate(obj_list);   i <- ComBat_integrate(srt)
i <- Uncorrected_integrate(obj_list)   # control
# NEW in 0.8.9 — multi-modal / advanced integrations:
i <- CCA_integrate(obj_list)       # Seurat CCA integration
i <- WNN_integrate(srt)            # Weighted Nearest Neighbor (multi-modal)
i <- RPCA_integrate(obj_list)      # reciprocal PCA
i <- Harmony5_integrate(obj_list)  # harmony v5
i <- scVI5_integrate(obj_list)     # scvi v5
i <- fastMNN5_integrate(obj_list)  # fastMNN v5
i <- MultiMAP_integrate(obj_list)  # MultiMAP
i <- Coralysis_integrate(obj_list) # Coralysis
i <- GLUE_integrate(obj_list)      # GLUE (multi-omics, deep learning)
# Direct harmony call also available:
srt <- RunHarmony2(srt, batch = "orig.ident")   # NOTE: RunHarmony2, NOT RunHarmony
srt <- RunCCA(srt, ...)                          # direct CCA
```

> **Integration-method ranking (2024-2026 benchmarks)**: **Harmony / scVI / scANVI** are SOTA defaults. BBKNN only for ultra-fast >500k-cell alignment. fastMNN acceptable but no longer first-choice. **ComBat is for bulk only.** WNN for multi-modal (RNA+ATAC/protein).

## Cell Annotation (11)

```r
srt <- RunSingleR(srt, ref = "HumanPrimaryCellAtlas")        # celldex references
srt <- RunCellTypist(srt, model = "Immune_All_Low.pkl")      # Python CellTypist via reticulate
srt <- RunScmap(srt, ref = ref_srt)
srt <- RunKNNPredict(srt, ref = ref_srt, label = "cell_type")
srt <- RunLabelTransfer(srt, reference, method="Seurat"|"symphony"|...)  # NEW
srt <- RunReferenceMapping(srt, reference, ...)                          # NEW (scArches-style)
srt <- RunSciBet(srt, ref = ref_srt, label = "cell_type")                # NEW
srt <- RunCellCycle(srt, method = "Seurat"|"cyclone"|"tricycle")         # NEW (was Seurat-only)
# Malignant-cell identification (NEW):
srt <- RunscMalignantFinder(srt, ...)
srt <- RunscMalignantRegion(srt, ...)
srt <- RunscMalignantStates(srt, ...)
```

## Marker Genes & Differential Expression

```r
srt <- FindExpressedMarkers(srt, ...)        # scop variant
# Plus Seurat-native: FindAllMarkers / FindMarkers (called directly on srt)
FoldChange(srt, ...)                          # Seurat-native fold-change (now exported)
de <- RunDEtest(srt, group.by = "condition",
                method = "DESeq2",    # "DESeq2" | "edgeR" | "limma" | "MAST" | "Wilcox"
                cells.group.by = "cell_type",  # pseudobulk aggregate
                batch = "orig.ident")
de <- RunRareQ(srt, ...)                      # rare-population DE (NEW)
```

## Trajectory & Pseudotime (11)

```r
srt <- RunMonocle3(srt); srt <- RunMonocle2(srt)
srt <- RunSlingshot(srt)
srt <- RunPAGA(srt)
srt <- RunPalantir(srt); srt <- RunCytoTRACE(srt)
srt <- RunCellRank(srt); srt <- RunWOT(srt)
# NEW in 0.8.9:
srt <- RunFitDevo(srt, ...)     # developmental potential
srt <- RunVECTOR(srt, ...)      # RNA velocity-encoded trajectory
srt <- RuntAge(srt, ...)        # transcriptional age
```

## RNA Velocity

```r
srt <- RunSCVELO(srt, mode = "dynamical",   # requires reticulate + scvelo
                 loom_path = "velocyto.loom")
srt <- RunSecActVelocity(srt, ...)           # SecAct-based velocity (NEW)
VelocityPlot(srt)
```

## Cell-Cell Communication (13)

```r
srt <- RunCellChat(srt, group.by = "cell_type")               # classic
srt <- RunCCC(srt, ...)                                       # unified CCC dispatcher (NEW)
srt <- RunCellphoneDB(srt, group.by, species="Homo_sapiens")  # NEW (Python via reticulate)
srt <- RunLIANA(srt, group.by, method="natmi"|"connectome"|"logfc"|...)  # NEW
srt <- RunNichenetr(srt, ...)                                 # NEW
srt <- RunMultiNichenetr(srt, ...)                            # NEW (multi-sample)
srt <- RunMistyR(srt, ...)                                    # NEW (multiview)
srt <- RunGiottoCellProximity(srt, ...)                       # NEW
# SecAct family (NEW — spatially resolved signaling):
srt <- RunSecAct(srt, ...)
srt <- RunSecActCCC(srt, ...)
srt <- RunSecActPatternGenes(srt, ...)
srt <- RunSecActSignalingPattern(srt, ...)
# Spatial CCC:
srt <- RunSpatialCellChat(srt, ...)                           # NEW (was NOT wrapped in 0.8.0)
```

## Enrichment & Pathway (10)

```r
srt <- RunGSEA(srt, geneset = "H")
srt <- RunEnrichment(srt, group.by = "cell_type")
srt <- RunDynamicEnrichment(srt, along = "pseudotime")
srt <- RunDynamicFeatures(srt, along = "pseudotime")
# NEW in 0.8.9:
srt <- RunGSVA(srt, ...)           # gene-set variation analysis
srt <- RunDorothea(srt, ...)       # TF activity (dorothea)
srt <- RunAugur(srt, ...)          # cell-type prioritization
srt <- RunESTIMATE(srt, ...)       # tumor purity / immune infiltration
srt <- RunMetabolism(srt, ...)     # scMetabolism-style
srt <- RunFWP(srt, ...)            # functional whole-population
srt <- RunscFEA(srt, ...)          # metabolic flux (NEW)
```

## Composition / Differential Abundance (7)

```r
srt <- RunProportionTest(srt)                  # basic proportion test
# Compositional-rigorous DA (all NEW — were NOT wrapped in 0.8.0):
srt <- RunMilo(srt, group.by, split.by, sample.by, comparison = NULL)   # miloR
srt <- RunscCODA(srt, group.by, split.by, sample.by, comparison = NULL) # scCODA
srt <- RunPropeller(srt, ...)                                            # propeller
srt <- RunLISI(srt, ...)                                                 # local inverse Simpson
srt <- RunMDIC3(srt, ...)                                                # MDIC3
srt <- RunStatialKontextual(srt, ...)                                    # Statial
srt <- RunmcRigor(srt, ...)                                              # mcRigor
```

> **Compositional discipline (unchanged)**: cell-type proportions sum to 1 → chi-square/Fisher invalid → use Milo/scCODA/Propeller. These are now all wrapped in scop 0.8.9 (previously required standalone packages).

## Reference Mapping (scArches-style)

```r
srt <- RunSCExplorer(srt);  srt <- PrepareSCExplorer(srt)
srt <- RunKNNMap(srt);      srt <- RunSeuratMap(srt)
srt <- RunSymphonyMap(srt); srt <- RunCSSMap(srt)
```

## GRN / Regulome (7) — ALL NEW

```r
srt <- RunSCENIC(srt, ...)        # classic SCENIC (pySCENIC wrapper)
srt <- RunSCENICPlus(srt, rna_assay="RNA", atac_assay="peaks", ...)  # multi-omics GRN
srt <- RunCisTarget(srt, ...)     # cisTarget motif enrichment
srt <- RunGENIE3(srt, ...)        # GENIE3
srt <- RunGRNBoost2(srt, ...)     # GRNBoost2
srt <- RunGRN(srt, ...)           # unified GRN dispatcher
srt <- RunGNIPLR(srt, ...)        # GNIPLR
srt <- RunscTenifoldKnk(srt, ...) # GRN KO ranking (perturbation prediction Route B)
srt <- RunscTenifoldNet(srt, ...) # GRN construction
```

## Spatial domains / SVG / network (15) — ALL NEW (most were NOT wrapped in 0.8.0)

```r
srt <- RunBANKSY(srt, assay=NULL, layer="data", features=NULL, ...)   # BANKSY domain
srt <- RunBayesSpace(srt, ...)                                        # BayesSpace domain
srt <- RunSmoothClust(srt, ...)                                       # SmoothClust
srt <- RunMERINGUE(srt, ...)                                          # MERINGUE
srt <- RunSpaNorm(srt, ...)                                           # SpaNorm normalization
srt <- RunSpatialNetwork(srt, ...)                                    # spatial graph
srt <- RunSpatialVariableFeatures(srt, ...)                           # SVG
srt <- RunSpatialGradientFeatures(srt, ...)                           # spatial gradient
srt <- RunSpatialIntegration(srt, ...)                                # multi-section spatial integration
# Giotto workflow family:
srt <- RunGiottoWorkflow(x, steps=c("basic","full"), group.by=NULL, return_seurat=TRUE)
srt <- RunGiottoSpatialGenes(srt, ...)
srt <- RunGiottoSpatialModules(srt, ...)
# Semla family:
srt <- RunSemlaLocalG(srt, ...)
srt <- RunSemlaRadialDistance(srt, ...)
srt <- RunSemlaSpatialNetwork(srt, ...)
srt <- RunSpatialEcoTyper(srt, ...)                                    # spatial EcoTyper
```

## Spatial deconvolution (8) — ALL NEW (were NOT wrapped in 0.8.0)

```r
srt <- RunDeconvolution(srt, method=..., ...)    # unified dispatcher
srt <- RunRCTD(srt, reference, reference_label="celltype", ...)      # spacexr RCTD
srt <- RunCell2location(srt, ...)                                     # cell2location (Python via reticulate)
srt <- RunSPOTlight(srt, ...)                                         # SPOTlight
srt <- RunSTdeconvolve(srt, ...)                                      # STdeconvolve (reference-free)
srt <- RunCytoSPACE(srt, ...)                                         # CytoSPACE
srt <- RunCARD(srt, ...)                                              # CARD
srt <- RunSpatialDWLS(srt, ...)                                       # spatial DWLS
# CSIDE (differential expression within deconvolution):
srt <- RunCSIDE(srt, ...)
```

> **Python parallel**: omicverse `ov.space.Deconvolution` also wraps cell2location/Tangram/RCTD/Starfysh/flashdeconv in Python. For R/Seurat workflows, use the scop verbs above.

## CNV / malignant inference

```r
srt <- RunCNV(srt, method = "copykat"|"fastCNV"|"scevan"|"infercnv", ...)  # NEW
```

## Benchmark / permutation

```r
RunBenchmark(srt, ...)        # NEW — benchmark wrapper
RunPermutation(srt, ...)      # NEW — permutation testing
```

## Other analysis verbs

```r
srt <- RunCIBERSORT(srt, ...)       # bulk-style deconvolution (NEW)
srt <- RunCoEmbedding(srt, ...)     # cross-modality co-embedding (NEW)
srt <- RunDynamicFeatures(srt, along="pseudotime")
srt <- RunMetaCell(srt, ...)        # MetaCell (NEW)
srt <- RunScissor(srt, ...)         # Scissor (bulk-scRNA integration, NEW)
srt <- RunscOMM(srt, ...)           # scOMM (NEW)
srt <- RunscPagwas(srt, ...)        # scPagwas GWAS integration (NEW)
```

## Python interop (verified)

```r
library(scop)
srt    <- adata_to_srt(adata)        # AnnData (Python) -> Seurat
adata  <- srt_to_adata(srt)          # Seurat -> AnnData
# NEW in 0.8.9 — more conversions now wrapped (previously NOT):
srt    <- h5ad_to_srt(h5ad_path)     # h5ad file -> Seurat
adata  <- loom_to_adata(loom_path)   # .loom -> AnnData
srt    <- loom_to_srt(loom_path)     # .loom -> Seurat
srt    <- spe_to_srt(spe)            # SpatialExperiment -> Seurat
spe    <- srt_to_spe(srt)            # Seurat -> SpatialExperiment
srt    <- spata2_to_srt(spata2_obj)  # spata2 -> Seurat
spata2 <- srt_to_spata2(srt)         # Seurat -> spata2
srt    <- srt_to_h5ad(srt, path)     # Seurat -> h5ad file
srt    <- srt_to_giotto(srt)         # Seurat -> Giotto
srt    <- giotto_to_srt(giotto_obj)  # Giotto -> Seurat
srt    <- AddGiottoToSeurat(srt, giotto_obj)
# Python env management:
scop::check_python(); scop::PrepareEnv("scvelo"); scop::ListEnv(); scop::RemoveEnv()
scop::remove_python("scvelo")
# Cross-species homolog conversion (NEW — was biomaRt standalone):
srt <- ConvertHomologs(srt, from_species, to_species)
```

## Visualization (thisplot integration)

> scop 0.8.9 exports a large set of plotters via the `thisplot` package. Representative ones:

```r
CellDimPlot(srt, group.by = "cell_type", reduction = "umap")
CellDimPlot3D(srt, reduction = "umap2")
FeatureDimPlot(srt, features = c("CD3D","MS4A1"))
FeatureHeatmap(srt, features = markers, group.by = "cell_type")
GroupHeatmap(srt, group.by = "cell_type")
VolcanoPlot(de)
DEtestPlot(de); DEtestManhattanPlot(de); DEtestRingPlot(de)    # NEW
ClusterTreePlot(srt)                                            # NEW (dendrogram)
PseudotimeProjectionPlot(srt)                                   # NEW
DynamicHeatmap(srt, along = "pseudotime"); DynamicPlot(srt)
PAGAPlot(srt); LineagePlot(srt); TACSPlot(srt)
CytoTRACEPlot(srt); PalantirTrajectoryPlot(srt)                # NEW
CellStatPlot(srt, group.by = "cell_type"); CellDensityPlot(srt)
GSEAPlot(gsea); EnrichmentPlot(enr)
GSVAPlot(srt); DorotheaPlot(srt)                               # NEW (Augur has no dedicated Plot verb; use RunAugur result + generic plotting)
# CCC plots (NEW):
CCCHeatmap(srt); CCCNetworkPlot(srt); CCCStatPlot(srt)
SpatialCellChatPlot(srt)                                        # renamed from CellChatPlot in 0.8.0
# Spatial plots (NEW):
SpatialSpotPlot(srt); SpatialCellPlot(srt); SpatialNetworkPlot(srt)
SpatialDeconvolutionPlot(srt); Cell2locationPlot(srt); DeconvolutionPlot(srt)
SpatialGradientPlot(srt); SpatialVariableFeaturePlot(srt); SpatialNeighborhoodPlot(srt)
SpatialIntegrationPlot(srt); SpatialCoordinates(srt)
SpatialEcoTyperSpatialPlot(srt); SpatialEcoTyperCompositionPlot(srt)
# CNV / malignant:
CNVPlot(srt)
# Other:
NMFHeatmap(srt); MetaCellPlot(srt); LISIPlot(srt)
ImmuneAbundancePlot(srt); GeneImmuneCorPlot(srt)
StatialKontextualPlot(srt); VECTORPlot(srt); FitDevoPlot(srt)
ScissorPlot(srt); tAgePlot(srt)
scFEAHeatmap(srt); scFEAVolcanoPlot(srt); scFEABalanceBarPlot(srt)
scTenifoldKnkPlot(srt); scTenifoldNetPlot(srt)
EstimateGenePlot(srt); EstimateScorePlot(srt)
FerrisWheelPlot(srt); MistyRPlot(srt); SCENICPlot(srt)
CoverageTrackPlot(srt); GiottoPlot(srt)
ProjectionPlot(srt, ref = ref_srt)
VelocityPlot(srt)
```

## Utilities & DB

```r
GeneConvert(srt, ...)              # gene ID conversion
ConvertHomologs(srt, ...)          # cross-species homologs (NEW)
AnnotateFeatures(srt, ...); AddFeaturesData(srt, ...)
GetAssayData5(srt, ...); GetFeaturesData(srt, ...); FetchDataZero(srt, ...)
DefaultReduction(srt); RenameFeatures(srt, ...)
ListDB(); PrepareDB(...); ListEnv(); ListScopDatasets(); LoadScopDataset()
ListSpatialMethods()               # NEW
CheckDataList(...); CheckDataMerge(...); CheckDataType(...)
CreateDataFile(...); CreateMetaFile(...)
FetchH5(...)
scop_logo(); env_requirements()
db_Scrublet / db_DoubletDetection / db_scDblFinder / db_scds   # doublet backends
CycGenePrefetch(...)
GetSimilarFeatures(...); CellTypistModels(); TrainCellTypist(srt, ...)
SpatialBackendStatus()             # NEW — check spatial backend availability
GetSpatialGraph(srt); GetSpatialResult(srt); SpatialResultInfo(srt)
ccc_to_adata(ccc); ccc_to_liana(ccc)   # CCC result conversion
```

---

## Capability gaps — NOT in scop 0.8.9 (use standalone packages)

> **0.8.0 → 0.8.9 change**: this table shrank dramatically. Most previously-listed gaps (SCENIC+/Milo/RCTD/BANKSY/SecAct/EcoTyper/Giotto/SmoothClust/scCODA/CARD/SPOTlight/CytoSPACE/CNV/GSVA/Dorothea/Augur/scTenifoldKnk) are now wrapped. Remaining gaps:

| Capability | Use instead |
|---|---|
| **moscot** (optimal transport trajectory) | `moscot` Python package — not wrapped in scop or omicverse; feeds CellRank's RealTimeKernel |
| **CellOracle** (GRN virtual KO, Python) | `celloracle` Python package — for perturbation-prediction Route B with only WT scRNA-seq |
| **SpatialGlue / MENDER / BINARY / GraphST** (spatial domain, Python) | standalone Python packages — scop wraps BANKSY/BayesSpace/Giotto but not these Python-native methods; or `ov.space` wrappers |
| **STAGATE / SpaceFlow / STAligner / GASTON** (spatial domain, omicverse) | `ov.space.pySTAGATE` / `pySpaceFlow` / `pySTAligner` / `GASTON` in omicverse — scop does not wrap these |
| **COMMOT** (spatial CCC) | `COMMOT` Python package — scop's spatial CCC is via `RunSpatialCellChat`/`RunSecActCCC`, not COMMOT |
| **Baysor** (image-less segmentation) | `baysor` Julia/CLI — not an R package; run externally |
| **bin2cell** (Visium HD) | `bin2cell` Python — wrapped in `ov.space.bin2cell`, not scop |
| **cellpose** (segmentation) | `cellpose` Python — used via `ov.space.visium_10x_hd_cellpose_expand`, not scop |
| **Multi-modal WNN beyond Seurat** | Seurat-native `FindMultiModalNeighbors` — scop's `WNN_integrate` wraps it; for non-Seurat multi-omics use `muon`/`scglue` |

> **Rule**: if you see a `RunX` verb not in this file, **verify it exists** before using:
> `exists("RunX", where = asNamespace("scop"))`. Re-run `scripts/scop_api_check.R` after any scop upgrade.
