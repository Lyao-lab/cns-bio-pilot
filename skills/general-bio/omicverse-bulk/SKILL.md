---
name: omicverse-bulk-pipeline
description: Bulk RNA-seq / 表达矩阵全流程（差异表达→富集→WGCNA→PPI→批次校正）基于 OmicVerse V2，纯 Python，无需 R 环境和 DESeq2/clusterProfiler/WGCNA R 包。一个 import omicverse as ov 覆盖 90% bulk 分析。
---

# OmicVerse Bulk 全流程

**合并自原 skill**：`general-bio/differential-expression`、`gokegg`、`gsea`、`wgcna`、`ppi-network`、`batch-correction`、`batch-correction-de`。OmicVerse V2 用 pyDESeq2/pyGSEApy/pyWGCNA 把这些 R 工具原生 Python 化，本 skill 是它们的统一入口。

`pip install omicverse`（V2）。完全无 R 依赖。

## 0. 初始化

```python
import omicverse as ov
ov.plot_set()
import pandas as pd
```

## 1. 输入约定

```python
# AnnData: adata.X = counts 矩阵（n_obs=样本, n_var=基因），adata.obs['condition'], adata.obs['batch']
# 或从 counts 表构建
import anndata as ad
adata = ad.AnnData(counts_df.T)   # 样本×基因
adata.obs['condition'] = ['ctrl','ctrl','treat','treat']
adata.layers['counts'] = adata.X.copy()
```

## 2. 批次校正（在 DE 之前）

```python
# ComBat（表达矩阵连续值）
ov.bulk.batch_correction(adata, batch_key='batch')
# 计数层用 ComBat-Seq：先转 counts 再调（pyDESeq2 友好）
```

决策点：连续 log 矩阵 → ComBat；原始整数 counts 且差异较大 → ComBat-Seq（保离散性，对 DESeq2 模型更稳）。一般主图用 ComBat 后矩阵，DE 用原始 counts + 把 batch 作为设计协变量。

## 3. 差异表达（pyDESeq2 封装，替代 DESeq2/edgeR/limma）

```python
ov.bulk.pyDEG(
    adata,
    groupby='condition',
    vs='treat',           # 对照组
    method='DEseq2',      # 默认；内部 pyDESeq2
)
deg = adata.uns['deg']   # DataFrame: log2FC, pvalue, padj
```

替代原 R：DESeq2(条件 ~ 条件) → results → 排序。pyDESeq2 数值结果一致，速度更快。

## 4. 富集分析（pyGSEA 封装，替代 clusterProfiler/fgsea）

```python
# ORA：超几何，输入上调/下调基因列表
ov.bulk.geneset_enrichment(gene_list=up_genes, org='human')   # GO/KEGG/Reactome

# GSEA：全排序列
ov.bulk.pyGSEA(rank_series=rank, org='human')
# rank_series: pd.Series(index=gene, values=metric)，常按 -log10(p)*sign(FC)

# 富集点/条图
ov.bulk.geneset_plot(adata)
```

替代原 R：clusterProfiler::enrichGO/enrichKEGG + gseGO/gseKEGG + dotplot。

## 5. 共表达网络（pyWGCNA 封装，替代 WGCNA R 包）

```python
ov.bulk.pyWGCNA(
    adata,
    method='signed',     # 'signed'|'unsigned'
    power=12,            # 软阈值；不传则自动 pickSoftThreshold
    minModuleSize=30,
)
# 结果落 adata.uns['WGCNA']: modules, MEs, hub genes
ov.bulk.geneset_plot(adata)  # 模块—性状关联热图
```

替代原 R：WGCNA blockwiseModules + moduleEigengenes + plotDendro。

## 6. PPI 网络（pyPPI 封装，替代 STRINGdb）

```python
net = ov.bulk.pyPPI(genes=hub_genes, species='human', score_thresh=400)
# 返回 DataFrame: source, target, combined_score
# 阈值：low(150)/medium(400)/high(700)/highest(900)
```

替代原 R：STRINGdb::map + get_interactions。后续可视化用 ov.pl 网络图或导出 Cytoscape。

## 7. 可视化（详见 visualization/omicverse-plotting）

```python
ov.pl.volcano(deg)                     # 火山图
ov.pl.complexheatmap(deg_top.T)        # 热图（PyComplexHeatmap 封装）
ov.pl.dotplot(adata, var_names=...)    # 基因—条件点图
```

## 决策速查

| 任务 | ov API | 原 R 工具 |
|---|---|---|
| 差异表达 | `ov.bulk.pyDEG` | DESeq2 / edgeR / limma |
| GO/KEGG ORA | `ov.bulk.geneset_enrichment` | clusterProfiler |
| GSEA | `ov.bulk.pyGSEA` | fgsea / clusterProfiler |
| WGCNA | `ov.bulk.pyWGCNA` | WGCNA |
| STRING PPI | `ov.bulk.pyPPI` | STRINGdb |
| 批次校正 | `ov.bulk.batch_correction` | sva::ComBat / ComBatSeq |
| 富集可视化 | `ov.bulk.geneset_plot` | dotplot |

## 关键坑

- `ov.bulk.pyDEG` 需要整数 counts（pyDESeq2 是负二项模型），不要喂 log 矩阵；批次效应放进设计矩阵而非先 ComBat。
- `pyGSEA` 的 rank 序列方向要一致（一致按 metric 降序或升序），符号反了富集方向全反。
- `pyWGCNA` 的 power 软阈值：样本量 <20 时自动选择不稳，建议手动指定 12-20。
- `pyPPI` species 参数务必对齐：human/mouse 基因符号大小写不同（human 全大写）。
- 批次效应如果与 condition 完全混杂（不可分离），任何校正都救不回——这是设计问题，不是工具问题。

## 前置依赖（从哪来）

- **counts 表达矩阵** → 样本×基因的整数 count 矩阵（FASTQ→STAR/HISAT 比对 + featureCounts 产出，或 GEO 下载）
- **`AnnData`：`adata.X` = counts，`adata.obs['condition']` 分组列，`adata.obs['batch']` 批次列**
- **`adata.layers['counts']`** 必须在归一化前保存（DE/批次协变量要用原始整数 counts）
- 若数据来自单细胞 → 先 `single-cell/omicverse-pipeline` 做 pseudobulk 聚合（`sc.pp.aggregate_and_filter`），再喂本 skill

## 何时离开本 skill（去哪）

- DEG/富集结果可视化 → `visualization/omicverse-plotting`（`ov.pl.volcano` / `ov.pl.complexheatmap` / `ov.pl.dotplot`）
- 组合成发表级 figure → `visualization/multi-panel-figures`
- 写 Methods 描述 bulk 流程 → `presentation/methods-writer`
- 写 Results 叙述 → `presentation/results-writer`
- 写图注 → `presentation/figure-legend-writer`
- 做成 talk slide → `presentation/scientific-slides`（DEG 火山图/热图用 `--attach` 嵌入 results slide）
