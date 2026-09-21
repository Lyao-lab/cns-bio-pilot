---
name: omicverse-bulk
description: Bulk RNA-seq / 表达矩阵全流程（差异表达→富集→WGCNA→PPI→批次校正）基于 OmicVerse V2，纯 Python，无需 R 环境和 DESeq2/clusterProfiler/WGCNA R 包。一个 import omicverse as ov 覆盖 90% bulk 分析。
---

> **派发子任务自守**：本 skill 若再向下派发任何执行子任务，先把 `references/dispatch_cheatsheet.md` 的相关硬规则（A-E）写进子任务 spec——子智能体看不到本会话上下文，没写进 spec 的规则等于不存在。

## When NOT to use this skill
- Data is single-cell (cell × gene matrix) → use `single-cell/omicverse-pipeline`; for bulk-style DE, do pseudobulk aggregation first, then feed to this skill
- Data is spatial transcriptomics → use `spatial/omicverse-spatial`
- You insist on R (DESeq2/clusterProfiler/WGCNA native R packages) → use `single-cell/scop` (some bulk tools can run via R)
- Only GO/GSEA enrichment, with results from single-cell DEG → pseudobulk first, then use the enrichment section of this skill

# OmicVerse Bulk Pipeline

## 📋 Analysis Code Templates

All bulk analysis code templates live in `references/analysis/templates/bulk.md`:

| 内容 | 关键 API |
|---|---|
| DE | ov.bulk.pyDEG / deseq2_normalize |
| 富集/GSEA | ov.bulk.geneset_enrichment / pyGSEA / geneset_plot_multi |
| WGCNA | ov.bulk.pyWGCNA |
| 批次校正 | ov.bulk.batch_correction |
| PPI | ov.bulk.pyPPI |

**本文件只保留流程/决策指导；可执行代码一律以 references/analysis/templates/bulk.md 为权威。**

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

> 代码模板：references/analysis/templates/bulk.md「Batch correction + DE」节（count_df 构造）。

## 2. Batch correction (before DE)

> 代码模板：references/analysis/templates/bulk.md「Bulk 批次校正」。

Decision: continuous log matrix → ComBat; raw integer counts with large differences → ComBat-Seq (preserves discreteness, more stable for the DESeq2 model). Typically main figures use the ComBat-corrected matrix; DE uses raw counts with batch as a design covariate.

## 3. Differential expression (pyDESeq2 wrapper, replaces DESeq2/edgeR/limma)

> 代码模板：references/analysis/templates/bulk.md「Batch correction + DE」。

Replaces R: DESeq2(condition ~ condition) → results → sort. pyDESeq2 matches numerically and is faster.

## 4. Enrichment analysis (pyGSEA wrapper, replaces clusterProfiler/fgsea)

> 代码模板：references/analysis/templates/bulk.md「富集 + GSEA」。

Replaces R: clusterProfiler::enrichGO/enrichKEGG + gseGO/gseKEGG + dotplot.

## 5. Co-expression network (pyWGCNA wrapper, replaces WGCNA R package)

> 代码模板：references/analysis/templates/bulk.md「共表达网络」。

Replaces R: WGCNA blockwiseModules + moduleEigengenes + plotDendro.

> **Single-cell co-expression: hdWGCNA (R) is preferred**: pyWGCNA mainly targets bulk; **the standard for single-cell co-expression is hdWGCNA** (Cell Rep Methods 2023, R/Seurat). If the object is single-cell rather than a bulk matrix, run hdWGCNA via `single-cell/scop`, not pyWGCNA.

> **PyDESeq2 now lives under scverse (2025-12 Owkin donation)**: long-term maintenance is secured. The `ov.bulk.pyDEG` wrapper is built on PyDESeq2. Note PyDESeq2 differs numerically from R DESeq2 in small ways (different EM implementation); declare the version when comparing across languages.

## 6. PPI network (pyPPI wrapper, replaces STRINGdb)

> 代码模板：references/analysis/templates/bulk.md「其他 Bulk 工具」节（pyPPI）。

Replaces R: STRINGdb::map + get_interactions. Visualize with ov.pl network plots or export to Cytoscape.

## 7. Visualization (see visualization/figure-production)

> 代码模板：references/plotting_reference.md（plot_volcano/plot_heatmap 统一入口）。

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
