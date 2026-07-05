---
name: omicverse-plotting
description: 统一科学绘图 API 基于 OmicVerse V2 的 ov.pl.* 模块（80+ 函数）。一个 ov.plot_set() 初始化即可覆盖单细胞/空间/bulk 全部常规图：embedding/dotplot/violin/volcano/heatmap/ccc/spatial/cellproportion。
---

# OmicVerse 统一绘图

**合并自原 skill**：`visualization/heatmap`、`volcano-plot`、`specialized-omics-plots`、`interactive-visualization`。这些常用图类型在 OmicVerse V2 的 `ov.pl.*` 已有统一封装。**多面板拼图不在本 skill**——固定布局拼图用 `visualization/multi-panel-figures`；机制图/流程图用 `visualization/scientific-schematics`；图形摘要布局用 `visualization/graphical-abstract`。

`pip install omicverse`（V2）。基于 matplotlib + seaborn + PyComplexHeatmap。

## 0. 初始化（必做）

```python
import omicverse as ov
ov.plot_set()   # 全局：字体、字号、dpi、默认配色、矢量友好的 pdf 渲染
import matplotlib.pyplot as plt
```

`ov.plot_set()` 一次调用统一风格；之后所有 `ov.pl.*` 与 scanpy 图都自动套用。

## 1. 常用图类型 API 速查

| 图类型 | API | 典型用途 |
|---|---|---|
| Embedding (UMAP/tSNE) | `ov.pl.embedding(adata, basis='X_umap', color=...)` | 聚类/注释展示 |
| Dot plot | `ov.pl.dotplot(adata, var_names=..., groupby=...)` | marker × cluster |
| Violin | `ov.pl.violin(adata, keys=..., groupby=...)` | marker 表达分布 |
| Volcano | `ov.pl.volcano(deg_df)` | DE 结果 |
| Marker heatmap | `ov.pl.marker_heatmap(adata)` | top markers × clusters |
| Feature heatmap | `ov.pl.feature_heatmap(adata)` | 任意基因热图 |
| 通用 complex heatmap | `ov.pl.complexheatmap(data)` | PyComplexHeatmap 封装 |
| Cell communication | `ov.pl.ccc_heatmap(adata)` | LR pair × cluster |
| Spatial | `ov.pl.plot_spatial(adata, color=...)` | 组织切片 |
| Cell proportion | `ov.pl.cellproportion(adata)` | 样本—cluster 比例 |
| Bar+dot | `ov.pl.bardotplot(adata)` | 比例 + 显著性 |

## 2. 示例

```python
# UMAP 着色
ov.pl.embedding(adata, basis='X_umap', color='celltype', frameon='small')

# Marker 点图
ov.pl.dotplot(adata, var_names=['CD3D','MS4A1','CD68'], groupby='celltype')

# 火山图（deg DataFrame: log2FC, pvalue/padj）
ov.pl.volcano(adata.uns['deg'], pval_thresh=0.05, log2fc_thresh=1)

# 热图（PyComplexHeatmap 封装）
ov.pl.marker_heatmap(adata, n_top=5, groupby='celltype')

# 细胞比例
ov.pl.cellproportion(adata, groupby='celltype', sample='sample')

# 空间
ov.pl.plot_spatial(adata, color='leiden')
```

## 3. 配色系统

```python
ov.pl.palette   # 内置：red_blue, scgpt, agora, etc.
ov.pl.embedding(adata, basis='X_umap', color='celltype',
                palette=ov.pl.palette['red_blue'])
# 自定义连续：cmap='viridis'/'RdBu_r'
```

## 4. 多面板组合（轻量）

```python
# ov.pl 返回 matplotlib axes，可手动组合
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
ov.pl.embedding(adata, basis='X_umap', color='leiden', ax=axes[0], show=False)
ov.pl.embedding(adata, basis='X_umap', color='celltype', ax=axes[1], show=False)
plt.tight_layout(); plt.savefig('fig.pdf')
```

> 复杂固定布局（6 面板 ABCDEF、共享 legend、Insets）请走 `visualization/multi-panel-figures`（PIL/GridSpec）。

## 5. 交互式探索（轻量）

`ov.pl.*` 默认静态；快速交互可用 `adata` 的 `ov.pl.embedding(..., interactive=True)`（基于 plotly 后端）。**重度交互仪表盘仍建议导出 anndata 后用 cellxgene/CELESTE**，不在本 skill 范围。

## 决策速查：何时离开本 skill

| 需求 | 去 |
|---|---|
| 6 面板组合 / 共享 legend | `visualization/multi-panel-figures` |
| 机制图 / 流程图 / 架构图 | `visualization/scientific-schematics` |
| 图形摘要（Graphical Abstract） | `visualization/graphical-abstract` |

## 关键坑

- 任何 ov.pl 之前先 `ov.plot_set()`，否则字体/dpi 不统一，多图拼接会错位。
- `ov.pl.volcano` 的输入是 DataFrame，列名要带 `log2FC` 与 `pvalue`/`padj`；命名不符需先 rename。
- `complexheatmap` 等同 PyComplexHeatmap，多分组注释通过 `row_split`/`col_split` 传，不是 seaborn 的 row_cluster。
- 输出矢量图统一用 `.pdf`（论文）/`.svg`（PPT 二次编辑），`dpi=300` 仅栅格时需要。
- matplotlib 中文/特殊字符需额外配字体，`ov.plot_set()` 默认西文，含中文时手动 `plt.rcParams['font.family']`。
