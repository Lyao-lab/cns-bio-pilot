# Workflow Routing Decision Guide

Routing logic to decide which sub-skill handles a user request.

## Step 1: Identify Data Type

```
Does the data have spatial coordinates / tissue section images?
├─ YES → Spatial transcriptomics route (spatial/)
│   Identify platform:
│   ├─ Visium (10x) → spatial/omicverse-spatial (full pipeline incl. IO)
│   ├─ Xenium (10x) → spatial/omicverse-spatial
│   ├─ MERFISH → spatial/omicverse-spatial or spatial/multiomics (high-res)
│   ├─ Slide-seq / Stereo-seq / Visium HD → spatial/multiomics (high-res, needs cellpose)
│   ├─ CODEX/IMC/MIBI (protein) → spatial/proteomics
│   └─ Other → spatial/omicverse-spatial (generic)
│
└─ NO → Is there a cell × gene matrix?
    ├─ YES (single-cell level) → Single-cell route (single-cell/)
    └─ NO (bulk / sample-level matrix) → General bioinformatics route (general-bio/)
```

## Spatial Transcriptomics Route

```
1. Full-pipeline entry (IO→QC→spatial neighbors→SVG→spatial domains→communication→visualization)
   → spatial/omicverse-spatial (Visium/Xenium/Nanostring/VisiumHD, OmicVerse V2)

2. Branches (by goal):
   ├─ Estimate spot cell composition (deconvolution)
   │   → spatial/deconvolution (ov.space.Deconvolution wraps cell2location/Tangram/RCTD/Starfysh/flashdeconv)
   │   ⚠️ Mandatory marker-proportion QC + postcheck
   │
   ├─ High-res platforms (Stereo-seq/Visium HD/Slide-seq/MERFISH, needs cellpose segmentation)
   │   → spatial/multiomics (squidpy + cellpose + SpatialData)
   │
   ├─ Spatial proteomics (CODEX/IMC/MIBI)
   │   → spatial/proteomics (scimap phenotyping + gating)

3. Visualization   → ov.pl.plot_spatial or visualization/omicverse-plotting
```

## Single-cell Route

```
1. Full-pipeline entry (QC→doublet→dim reduction→clustering→annotation→batch→communication→trajectory)
   → single-cell/omicverse-pipeline (OmicVerse V2 unified API)
   └─ Multi-batch integration sub-decision:
       ├─ Fast / CPU → Harmony (ov.single.batch_correction(method='harmony'))
       ├─ Large-scale / GPU / complex batch → scVI (method='scvi')
       └─ Annotation has labels → scANVI

2. RNA velocity (needs spliced/unspliced) → single-cell/rna-velocity
   └─ Downstream fate inference → CellRank 2 (ov.single.cellrank_fate)

3. Downstream analysis (by goal):
   ├─ Cell-cell signaling → ov.single.run_liana (LIANA consensus) or run_cellphonedb_v5
   ├─ CRISPR perturbation (measured) → single-cell/perturb-seq
   ├─ Perturbation prediction (no experiment) → single-cell/perturbation-prediction (run linear baseline)
   └─ R/Seurat ecosystem or scop-only tools (CytoTRACE/Milo/SCENIC+) → single-cell/scop

4. DE analysis (key discipline)
   ├─ ⚠️ No per-cell Wilcoxon (pseudoreplication, meta-methodology principle ③)
   ├─ Use pseudobulk (aggregate by sample × cell_type → DESeq2/edgeR)
   └─ DE on raw counts, never on batch-corrected embedding

5. Study design (before analysis) → single-cell/research-planner (zero-code methodology)
```

## General Bioinformatics Route (bulk / other)

```
Expression matrix + grouping?
├─ Full pipeline → general-bio/omicverse-bulk (pyDESeq2/GSEApy/pyWGCNA/pyPPI/batch_correction, pure Python)
│   ├─ DE: ov.bulk.pyDEG (PyDESeq2-based, scverse-maintained)
│   ├─ Enrichment: ov.bulk.pyGSEA / GSEApy + decoupleR
│   ├─ Co-expression: pyWGCNA (bulk) / hdWGCNA (sc, via R/scop)
│   └─ PPI: ov.bulk.pyPPI / STRING
│
└─ Requires native R (DESeq2/clusterProfiler) → single-cell/scop (some bulk tools)
```

## Plotting Route

```
What to plot?
├─ Data-driven figures (UMAP/volcano/heatmap/dot/violin) → visualization/omicverse-plotting (ov.pl.* 80+ functions)
├─ 6-panel publication figures (A-F assembly) → visualization/multi-panel-figures
├─ Mechanism / workflow / architecture schematics → visualization/scientific-schematics (AI generate→review loop)
└─ Paper Graphical Abstract → visualization/scientific-schematics (graphical-abstract mode)

> Read references/figure_aesthetics.md before any plotting (dual-track palette + CJK fallback + no title/legend overlap)
```

## Publication Output Route

```
What to produce after analysis?
├─ Formal presentation PPT → presentation/scientific-slides (beamer/pptx)
├─ Lab-meeting slides → presentation/scientific-slides (lab-meeting mode)
├─ Methods text → presentation/methods-writer
├─ Results narrative → presentation/results-writer
├─ Figure legends → presentation/figure-legend-writer
└─ Study design (before analysis) → single-cell/research-planner
```

## Common Pitfalls & Mandatory Rules

1. **Never DE on batch-corrected data**: Harmony/scVI-corrected embeddings are for clustering/visualization only; DE uses raw counts (pseudobulk)
2. **Validate spatial deconvolution**: report cell2location reconstruction quality, cross-check known markers
3. **Spatial domains ≠ clustering**: must use spatial-aware methods (squidpy spatial neighbors + graph clustering), not plain Leiden
4. **RNA velocity needs splicing info**: spliced/unspliced layers must exist (velocyto/KB output); otherwise scvelo cannot run
5. **Conservative annotation**: reference-based (CellTypist/SingleR) beats manual markers; mark low-confidence as "Unknown"
6. **All figures preserve raw data**: N, statistical test, Padj must be visible in figure or legend

## Signal Patterns & Pitfall Checks

Results look right but the analysis is broken. When you see the left column, run the right column to verify.

| Symptom (looks fine) | Typical stage | Key signal | How to verify |
|---|---|---|---|
| UMAP clusters clear, but DE all non-significant | scRNA DE | batch-corrected embedding wrongly used for DE | `grep "use_rep.*X_scVI\|X_harmony" script.py`; should be raw counts + pseudobulk |
| Doublet rate suddenly >15% | QC | ambient RNA or polyploid cells, not true doublets | check cell cycle score; rerun scrublet at lower threshold |
| cell2location abundance all NaN/0 | spatial deconv | reference signature not trained on raw_counts | check ref_adata.X is log-transformed (should be raw) |
| Clustering resolution won't rise | scRNA clustering | too few HVGs or batch effect dominates | check n_hvg; run batch_integration first |
| Annotation confidence all low | annotation | reference/query species or tissue mismatch | ConvertHomologs check; switch to matched reference |
| RNA velocity directions scrambled | velocity | spliced/unspliced ratio skewed | check velocyto/kb output; scv.pl.proportions |
| Spatial domains don't match histology | spatial domains | method ignores space (pure expression clustering) | confirm spatial-aware method (STAGATE/BayesSpace, not K-means) |
| Enrichment full of housekeeping pathways | GO/KEGG | too few DE genes or no background correction | check universe; use padj<0.05 genes |
| CellChat p<0.001 everywhere | communication | too few permutations or cell-count imbalance | nboot>=100; check group sizes |
| WGCNA modules all correlate with batch | WGCNA | batch effect leakage | add batch covariate to trait correlation |
| Cell types unseparable after batch correction | integration | over-correction (removed biology) | evaluate with scIB: batch ASW down + cell type ASW down = over-correction |
| Volcano genes bunched at center | DE viz | Log2FC threshold too strict or normalization issue | check counts distribution; relax to |Log2FC|>0.58 for exploratory |
| Pseudobulk DE replicates/samples = 0 | scRNA DE | missing sample column or samples dropped at cell-type aggregation | check `adata.obs['sample']`; ≥3 bio replicates per condition |
| Perturbation prediction "beats baseline" | perturbation | training set leaked target perturbation or eval is i.i.d. | check held-out contains target perturbation; report o.o.d. metrics |
| Trajectory root-cell markers low | trajectory | wrong root or reversed ordering | check progenitor markers; swap root/diffusers |
| Spatial neighbor graph errors on isolated nodes | spatial | flipped coordinates or n_neighbors too small | check `adata.obsm['spatial']`; raise n_neighbors to 6 |
