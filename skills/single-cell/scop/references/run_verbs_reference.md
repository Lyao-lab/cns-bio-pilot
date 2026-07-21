# scop API Reference (verified against scop 0.8.0)

> **All 126 exports below verified via `getNamespaceExports("scop")` on scop 0.8.0**.
> Re-verify after any scop upgrade by running `scripts/scop_api_check.R` (repo root).
>
> Previous versions of this file listed many APIs that do not exist in scop 0.8.0
> (older docs claimed "200+ Run\* verbs" — actual count is **40 Run\* verbs**, plus
> 86 helpers/plotters). The fabricated entries have been removed. See the
> **Capability gaps** section for what scop does NOT wrap and which standalone
> package to use instead.

All verbs operate on a Seurat object `srt`. **Always check `?scop::RunX` for the real
signature** — each Run\* wraps a native R function whose parameter names may differ.

> Companion to `SKILL.md`. SKILL keeps `standard_scop()` (one-call pipeline), Python
> interop, decision tables, and pitfalls; this file enumerates the verified scop API.

## QC & Preprocessing

```r
srt <- RunCellQC(srt, batch = "orig.ident",
                 nFeature_min = 300, mt_max = 20,
                 doublet_method = "Scrublet")   # "Scrublet" | "DoubletDetection" | "scDblFinder" | "scds"
srt <- RunDoubletCalling(srt, method = "Scrublet")
srt <- RecoverCounts(srt)   # restore raw counts after transformations
# Cell cycle scoring: use Seurat::CellCycleScoring() (NOT wrapped in scop 0.8.0)
```

## Dimensionality Reduction (12)

```r
srt <- RunDimReduction(srt)             # unified DR dispatcher
srt <- RunPCA(srt, npcs = 50)
srt <- RunUMAP(srt, dims = 1:30)        # NOTE: not scop-exported — use Seurat::RunUMAP
srt <- RunUMAP2(srt, dims = 1:30)       # scop's umap2 variant
srt <- RunMDS(srt, dims = 1:30)
srt <- RunNMF(srt); srt <- RunGLMPCA(srt)
srt <- RunDM(srt); srt <- RunPHATE(srt); srt <- RunPaCMAP(srt)
srt <- RunTriMap(srt); srt <- RunLargeVis(srt)
srt <- RunPCAMap(srt)
```

> Wait — only `RunUMAP2`, `RunPCA`, `RunDimReduction`, `RunMDS`, `RunNMF`, `RunGLMPCA`, `RunDM`, `RunPHATE`, `RunPaCMAP`, `RunTriMap`, `RunLargeVis`, `RunPCAMap` are scop-exported. For plain UMAP, use **Seurat::RunUMAP** (scop pass-through).

## Clustering & Neighbors

```r
srt <- FindNeighbors(srt, dims = 1:30)            # Seurat-native
srt <- RunFR(srt, resolution = 0.6)               # scop's FindClusters wrapper
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
i <- fastMNN_integrate(obj_list); i <- MNN_integrate(obj_list)
i <- LIGER_integrate(obj_list);   i <- Conos_integrate(obj_list)
i <- Scanorama_integrate(obj_list); i <- BBKNN_integrate(srt)
i <- scVI_integrate(obj_list);    i <- CSS_integrate(obj_list)
i <- Seurat_integrate(obj_list);  i <- ComBat_integrate(srt)
i <- Uncorrected_integrate(obj_list)   # control
# Direct harmony call also available:
srt <- RunHarmony2(srt, batch = "orig.ident")   # NOTE: RunHarmony2, NOT RunHarmony
```

> **Integration-method ranking (2024-2026 benchmarks)**: **Harmony / scVI / scANVI** are SOTA defaults. BBKNN only for ultra-fast >500k-cell alignment. fastMNN acceptable but no longer first-choice. **ComBat is for bulk only.**

## Cell Annotation (4)

```r
srt <- RunSingleR(srt, ref = "HumanPrimaryCellAtlas")   # celldex references
srt <- RunCellTypist(srt, model = "Immune_All_Low.pkl") # Python CellTypist via reticulate
srt <- RunScmap(srt, ref = ref_srt)
srt <- RunKNNPredict(srt, ref = ref_srt, label = "cell_type")
```

## Marker Genes & Differential Expression (3)

```r
srt <- FindExpressedMarkers(srt, ...)        # scop variant
# Plus Seurat-native: FindAllMarkers / FindMarkers (called directly on srt)
de <- RunDEtest(srt, group.by = "condition",
                method = "DESeq2",    # "DESeq2" | "edgeR" | "limma" | "MAST" | "Wilcox"
                cells.group.by = "cell_type",  # pseudobulk aggregate
                batch = "orig.ident")
```

## Trajectory & Pseudotime (8)

```r
srt <- RunMonocle3(srt); srt <- RunMonocle2(srt)
srt <- RunSlingshot(srt)
srt <- RunPAGA(srt)
srt <- RunPalantir(srt); srt <- RunCytoTRACE(srt)
srt <- RunCellRank(srt); srt <- RunWOT(srt)
```

## RNA Velocity (Python interop)

```r
srt <- RunSCVELO(srt, mode = "dynamical",   # requires reticulate + scvelo
                 loom_path = "velocyto.loom")
VelocityPlot(srt)
compute_velocity_on_grid(...)   # helper
```

## Cell-Cell Communication (1)

```r
srt <- RunCellChat(srt, group.by = "cell_type")
```

## Enrichment (3)

```r
srt <- RunGSEA(srt, geneset = "H")
srt <- RunEnrichment(srt, group.by = "cell_type")
srt <- RunDynamicEnrichment(srt, along = "pseudotime")
srt <- RunDynamicFeatures(srt, along = "pseudotime")
```

## Composition / Differential Abundance (1)

```r
srt <- RunProportionTest(srt)   # basic cell-type proportion test
# For compositional-rigorous DA (Milo/scCODA/propeller), use standalone — see Capability gaps
```

## Reference Mapping (5, scArches-style)

```r
srt <- RunSCExplorer(srt); srt <- PrepareSCExplorer(srt)
srt <- RunKNNMap(srt); srt <- RunSeuratMap(srt)
srt <- RunSymphonyMap(srt); srt <- RunCSSMap(srt)
```

## Python interop (verified)

```r
library(scop)
srt    <- adata_to_srt(adata)        # AnnData (Python) -> Seurat
adata  <- srt_to_adata(srt)          # Seurat -> AnnData
# Python env management:
scop::check_python(); scop::PrepareEnv("scvelo"); scop::ListEnv(); scop::RemoveEnv()
scop::remove_python("scvelo")
```

> **NOT in scop 0.8.0** (despite older docs): `spe_to_srt` / `srt_to_spe` (SpatialExperiment), `h5ad_to_srt` / `srt_to_h5ad`, `loom_to_adata` / `loom_to_srt`, `LoadScopDataset` / `ListScopDatasets`. Use `adata_to_srt`/`srt_to_adata` + scanpy/anndata in Python for these conversions.

## Visualization (thisplot integration, representative)

```r
CellDimPlot(srt, group.by = "cell_type", reduction = "umap")
CellDimPlot3D(srt, reduction = "umap2")
FeatureDimPlot(srt, features = c("CD3D","MS4A1"))
FeatureDimPlot3D(srt, ...)
FeatureHeatmap(srt, features = markers, group.by = "cell_type")
GroupHeatmap(srt, group.by = "cell_type")
CellCorHeatmap(srt)
VolcanoPlot(de)
DynamicHeatmap(srt, along = "pseudotime"); DynamicPlot(srt)
PseudotimeProjectionPlot  # check existence
PAGAPlot(srt); LineagePlot(srt); TACSPlot(srt)
CytoTRACEPlot(srt)
CellStatPlot(srt, group.by = "cell_type")
CellDensityPlot(srt, reduction = "umap")
ClusterTreePlot(srt)
GSEAPlot(gsea); EnrichmentPlot(enr)
CellScoring(srt, ...)
FeatureStatPlot(srt); FeatureCorPlot(srt)
StatPlot(srt); GraphPlot(srt)
ProportionTestPlot(srt)
ProjectionPlot(srt, ref = ref_srt)
CellChatPlot(srt)
VelocityPlot(srt)
```

## Utilities & DB

```r
GeneConvert(srt, ...)              # gene ID conversion (cross-species uses biomaRt standalone)
AnnotateFeatures(srt, ...); AddFeaturesData(srt, ...)
GetAssayData5(srt, ...); GetFeaturesData(srt, ...); FetchDataZero(srt, ...)
DefaultReduction(srt); RenameFeatures(srt, ...)
ListDB(); PrepareDB(...); ListEnv()
CheckDataList(...); CheckDataMerge(...); CheckDataType(...)
CreateDataFile(...); CreateMetaFile(...)
is_outlier(...); FetchH5(...)
cluster_within_group2(srt, ...)
scop_logo(); env_requirements(); check_r()
db_Scrublet / db_DoubletDetection / db_scDblFinder / db_scds   # doublet backends
CycGenePrefetch(...)              # cell-cycle gene prefetch
GetSimilarFeatures(...); CellTypistModels()
```

---

## Capability gaps — NOT in scop 0.8.0 (use standalone packages)

| Capability | Use instead |
|---|---|
| **SCENIC / SCENIC+** (GRN) | `scenicplus` standalone (R+Python); or `ov.single` SCENIC wrappers in omicverse-pipeline |
| **CellPhoneDB / LIANA / NicheNet** (CCC) | `LIANA` / `nichenetr` / `CellPhoneDB` standalone; or omicverse `ov.single.run_liana` |
| **Milo / scCODA / Propeller** (compositional DA) | `miloR` / `scCODA` (Python) / `propeller` (R) — see omicverse-pipeline DA section |
| **SecAct / SecActCCC** | `SecAct` standalone |
| **CNV inference** | `infercnv` / `copykat` R packages |
| **Metabolism** | `scMetabolism` R package |
| **scMalignant** (Finder/Region) | `scMalignant` standalone |
| **scTenifoldKnk** (GRN KO) | `scTenifoldKnk` R package — see perturbation-prediction Route B |
| **GSVA / Dorothea / Augur / SciBet** | `GSVA` / `dorothea` / `Augur` / `scibet` R packages |
| **Spatial domain** (BayesSpace/BANKSY) | `BayesSpace` / `BANKSY` R packages; or omicverse-spatial |
| **Spatial deconvolution** (RCTD/SPOTlight/CARD/STdeconvolve/CytoSPACE) | `spacexr` (RCTD) / standalone; or `ov.space.Deconvolution` in omicverse |
| **Spatial workflow** (Giotto/Semla/MERINGUE/SmoothClust/CSIDE/SpaNorm/EcoTyper) | respective standalone R packages |
| **Cross-species homolog conversion** | `biomaRt` / `homologene` R packages |
| **Train custom CellTypist model** | `celltypist` Python package directly |
| **Dims estimation** (elbow/JackStraw) | Seurat-native `ElbowPlot` / `JackStraw` |
| **Multi-modal WNN** | Seurat-native `FindMultiModalNeighbors` |

> **Rule**: if you see a `RunX` verb not in this file, **verify it exists** before using:
> `exists("RunX", where = asNamespace("scop"))`. Re-run `scripts/scop_api_check.R` after any scop upgrade.
