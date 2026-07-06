---
name: omicverse-plotting
description: 统一科学绘图 API 基于 OmicVerse V2 的 ov.pl.* 模块（80+ 函数）。一个 ov.plot_set() 初始化即可覆盖单细胞/空间/bulk 全部常规图：embedding/dotplot/violin/volcano/heatmap/ccc/spatial/cellproportion。
---

## When NOT to use this skill
- 固定布局多面板拼图（6 面板 A–F、共享 legend、insets）→ 改用 `visualization/multi-panel-figures`
- 机制图/流程图/架构图（非数据驱动）→ 改用 `visualization/scientific-schematics`
- 论文图形摘要布局（从 abstract 推布局 + AI 提示词）→ 改用 `visualization/graphical-abstract`
- 重度交互仪表盘 → 导出 anndata 后用 cellxgene/CELESTE（不在本 skill 范围）

# OmicVerse 统一绘图

**合并自原 skill**：`visualization/heatmap`、`volcano-plot`、`specialized-omics-plots`、`interactive-visualization`。这些常用图类型在 OmicVerse V2 的 `ov.pl.*` 已有统一封装。**多面板拼图不在本 skill**——固定布局拼图用 `visualization/multi-panel-figures`；机制图/流程图用 `visualization/scientific-schematics`；图形摘要布局用 `visualization/graphical-abstract`。

`pip install omicverse`（V2）。基于 matplotlib + seaborn + PyComplexHeatmap。

## 0. 初始化（必做）

> **绘图审美规范**：发表级图必须遵循 CNS 标准（300 DPI、Arial、Okabe-Ito 色盲配色、矢量 PDF）。详见 `references/figure_aesthetics.md`——**绘图前必读**。

```python
import omicverse as ov
ov.plot_set()   # 全局：字体、字号、dpi、默认配色、矢量友好的 pdf 渲染
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# ov.plot_set() 不覆盖的发表级补充（CNS 必须）：
plt.rcParams.update({
    'figure.dpi': 300, 'savefig.dpi': 300,        # 默认100不够
    'savefig.bbox': 'tight',                       # 去白边（嵌PPT必做）
    'pdf.fonttype': 42, 'ps.fonttype': 42,         # TrueType嵌入（编辑可改）
    'font.family': 'Arial',                        # CNS强制 sans-serif
})

# 用户选定双轨配色（详见 references/figure_aesthetics.md）
# ① 离散分类（UMAP/聚类型/空间域）—— 莫兰迪 Nord 柔和
MORLANDI = ['#88C0D0','#BF616A','#A3BE8C','#D08770',
            '#B48EAD','#EBCB8B','#5E81AC','#D8DEE9']
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=MORLANDI)
# ② 连续表达（热图/表达量）—— 蓝-黄-红经典（低=蓝，中=黄，高=红）
EXPR_CMAP = LinearSegmentedColormap.from_list('byr',
    ['#2C5F8D','#5DA0C8','#F5F5DC','#E8B84A','#C0392B'], N=256)
# ③ 发散（log2FC）—— 蓝-白-红，0=白中点
DIVERGING_CMAP = LinearSegmentedColormap.from_list('log2fc',
    ['#2C5F8D','#88C0D0','#FFFFFF','#D08770','#8B2C2C'], N=256)
# 用法：离散用 MORLANDI（自动套 axes.prop_cycle）；热图 cmap=EXPR_CMAP；log2FC cmap=DIVERGING_CMAP
```

`ov.plot_set()` + 上述补充一次调用统一风格；之后所有 `ov.pl.*` 与 scanpy 图都自动套用。

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

# 火山图（deg DataFrame 列名必须为 'log2FC' 和 'qvalue'/'pvalue'，不符先 rename）
ov.pl.volcano(deg_df, pval_name='qvalue', fc_name='log2FC',
              pval_threshold=0.05, fc_min=-1.5, fc_max=1.5,
              plot_genes_num=10)  # 标注 top10 基因名

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

## Pre-Output Checklist（出图前必过）
- [ ] 数值完整性：每张定量图保留 N / 统计检验 / 误差线
- [ ] 轴标签/图例/色盲友好：坐标轴有标签与单位，图例可独立读懂，配色对色盲安全（避免纯红绿）
- [ ] 引用支撑：明确哪张图/哪个统计支持主结论
- [ ] 避免臆测：无显著差异时写 "No significant effect"，不硬编故事
- [ ] 关联≠因果：用 "associated with"，regulates/causes 需实验证据
- [ ] 跑 postcheck.py ✅

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
