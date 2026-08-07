---
name: omicverse-bulk
description: Bulk RNA-seq / 表达矩阵全流程（差异表达→富集→WGCNA→PPI→批次校正）基于 OmicVerse V2，纯 Python，无需 R 环境和 DESeq2/clusterProfiler/WGCNA R 包。一个 import omicverse as ov 覆盖 90% bulk 分析。
---

## When NOT to use this skill
- Data is single-cell (cell × gene matrix) → use `single-cell/omicverse-pipeline`; for bulk-style DE, do pseudobulk aggregation first, then feed to this skill
- Data is spatial transcriptomics → use `spatial/omicverse-spatial`
- You insist on R (DESeq2/clusterProfiler/WGCNA native R packages) → use `single-cell/scop` (some bulk tools can run via R)
- Only GO/GSEA enrichment, with results from single-cell DEG → pseudobulk first, then use the enrichment section of this skill

# OmicVerse Bulk Pipeline

**Merged from former skills**: original differential-expression / gokegg / gsea / wgcna / ppi-network / batch-correction / batch-correction-de (these standalone skills no longer exist; functionality unified in OmicVerse V2). OmicVerse V2 ports these R tools to native Python via pyDESeq2/pyGSEApy/pyWGCNA; this skill is the unified entry.

`pip install omicverse` (V2). Fully R-free.

> **Iteration reminder (Core Rule 8)**: This pipeline is run in batches. After each major step batch (e.g., QC+cluster+annotation; or DE+enrichment), return to `research-planner` Phase R to review results with the researcher before the next batch. Do not auto-run end-to-end.

> **Hypothesis ledger** (Core Rule 7): If you did NOT come from `research-planner`, create a mini `hypothesis_ledger.md` now (H1 + status:pending + unexpected-finding slot). Phase R R1 will update it.

## 0. Initialization

```python
import omicverse as ov
ov.plot_set()
import pandas as pd
```

## 1. Input convention

```python
# AnnData: adata.X = counts matrix (n_obs=samples, n_var=genes), adata.obs['condition'], adata.obs['batch']
# or build from a counts table
import anndata as ad
adata = ad.AnnData(counts_df.T)   # samples × genes
adata.obs['condition'] = ['ctrl','ctrl','treat','treat']
adata.layers['counts'] = adata.X.copy()
```

## 2. Batch correction (before DE)

```python
# ComBat (continuous expression matrix)
ov.bulk.batch_correction(adata, batch_key='batch')
# For counts layer use ComBat-Seq: convert to counts first (pyDESeq2-friendly)
```

Decision: continuous log matrix → ComBat; raw integer counts with large differences → ComBat-Seq (preserves discreteness, more stable for the DESeq2 model). Typically main figures use the ComBat-corrected matrix; DE uses raw counts with batch as a design covariate.

## 3. Differential expression (pyDESeq2 wrapper, replaces DESeq2/edgeR/limma)

```python
ov.bulk.pyDEG(
    adata,
    groupby='condition',
    vs='treat',           # control group
    method='DEseq2',      # default; pyDESeq2 inside
)
deg = adata.uns['deg']   # DataFrame: log2FC, pvalue, padj
```

Replaces R: DESeq2(condition ~ condition) → results → sort. pyDESeq2 matches numerically and is faster.

## 4. Enrichment analysis (pyGSEA wrapper, replaces clusterProfiler/fgsea)

```python
# ORA: hypergeometric, input up/down gene list
ov.bulk.geneset_enrichment(gene_list=up_genes, org='human')   # GO/KEGG/Reactome

# GSEA: full ranked list
ov.bulk.pyGSEA(rank_series=rank, org='human')
# rank_series: pd.Series(index=gene, values=metric), often -log10(p)*sign(FC)

# Enrichment dot/bar plot
ov.bulk.geneset_plot(adata)
```

Replaces R: clusterProfiler::enrichGO/enrichKEGG + gseGO/gseKEGG + dotplot.

## 5. Co-expression network (pyWGCNA wrapper, replaces WGCNA R package)

```python
ov.bulk.pyWGCNA(
    adata,
    method='signed',     # 'signed'|'unsigned'
    power=12,            # soft threshold; omit to auto pickSoftThreshold
    minModuleSize=30,
)
# result in adata.uns['WGCNA']: modules, MEs, hub genes
ov.bulk.geneset_plot(adata)  # module-trait association heatmap
```

Replaces R: WGCNA blockwiseModules + moduleEigengenes + plotDendro.

> **Single-cell co-expression: hdWGCNA (R) is preferred**: pyWGCNA mainly targets bulk; **the standard for single-cell co-expression is hdWGCNA** (Cell Rep Methods 2023, R/Seurat). If the object is single-cell rather than a bulk matrix, run hdWGCNA via `single-cell/scop`, not pyWGCNA.

> **PyDESeq2 now lives under scverse (2025-12 Owkin donation)**: long-term maintenance is secured. The `ov.bulk.pyDEG` wrapper is built on PyDESeq2. Note PyDESeq2 differs numerically from R DESeq2 in small ways (different EM implementation); declare the version when comparing across languages.

## 6. PPI network (pyPPI wrapper, replaces STRINGdb)

```python
net = ov.bulk.pyPPI(genes=hub_genes, species='human', score_thresh=400)
# returns DataFrame: source, target, combined_score
# thresholds: low(150)/medium(400)/high(700)/highest(900)
```

Replaces R: STRINGdb::map + get_interactions. Visualize with ov.pl network plots or export to Cytoscape.

## 7. Visualization (see visualization/figure-production)

```python
ov.pl.volcano(deg)                     # volcano plot
ov.pl.complexheatmap(deg_top.T)        # heatmap (PyComplexHeatmap wrapper)
ov.pl.dotplot(adata, var_names=...)    # gene-condition dot plot
```

## Decision quick-reference

| Task | ov API | Original R tool |
|---|---|---|
| Differential expression | `ov.bulk.pyDEG` | DESeq2 / edgeR / limma |
| GO/KEGG ORA | `ov.bulk.geneset_enrichment` | clusterProfiler |
| GSEA | `ov.bulk.pyGSEA` | fgsea / clusterProfiler |
| WGCNA | `ov.bulk.pyWGCNA` | WGCNA |
| STRING PPI | `ov.bulk.pyPPI` | STRINGdb |
| Batch correction | `ov.bulk.batch_correction` | sva::ComBat / ComBatSeq |
| Enrichment visualization | `ov.bulk.geneset_plot` | dotplot |

## Key pitfalls

- `ov.bulk.pyDEG` needs integer counts (pyDESeq2 is a negative-binomial model); don't feed a log matrix. Put batch into the design matrix instead of pre-applying ComBat.
- `pyGSEA` rank-series direction must be consistent (sort by metric all-descending or all-ascending); a flipped sign flips enrichment direction.
- `pyWGCNA` soft-power threshold: auto-selection is unstable with <20 samples; manually set 12-20.
- `pyPPI` species must align: human/mouse gene symbols differ in case (human all-uppercase).
- If batch is fully confounded with condition (non-separable), no correction can rescue it — that's a design problem, not a tool problem.

## Prerequisites (where it comes from)

- **Counts expression matrix** → sample × gene integer count matrix (FASTQ→STAR/HISAT alignment + featureCounts, or downloaded from GEO)
- **`AnnData`: `adata.X` = counts, `adata.obs['condition']` group column, `adata.obs['batch']` batch column**
- **`adata.layers['counts']`** must be saved before normalization (DE/batch covariate uses raw integer counts)
- If data comes from single-cell → first run `single-cell/omicverse-pipeline` §8.5 for pseudobulk aggregation (`sc.get.aggregate(adata, by=['sample','celltype'], func='sum', layer='counts')`), then feed to this skill

## When to leave this skill (where to go)

- After each analysis batch — **before the next batch** → `single-cell/research-planner` **Phase R** (Review & Re-plan, Core Rule 8): interpret results, discuss with researcher, revise plan
- DEG/enrichment result visualization → `visualization/figure-production` (`ov.pl.volcano` / `ov.pl.complexheatmap` / `ov.pl.dotplot`)
- Compose publication-grade figure → `visualization/figure-production`
- Write Methods describing the bulk workflow → `presentation/manuscript-writing`
- Write Results narrative → `presentation/manuscript-writing`
- Write figure legends → `presentation/manuscript-writing`
- Build talk slides → `presentation/scientific-slides` (add DEG volcano/heatmap as `"image"` in outline.json)
