# Plotting Reference — 发表级绘图代码速查

> 本文件是 figure-production skill 的**代码层**：每种图型的精确参数 + 可跑模板。
> 配套：流程查 `skills/visualization/figure-production/SKILL.md`；原则/视觉规格查 `figure_guide.md`；外部参考查 `omicverse_skills_examples.md`。
> 所有模板假设已执行顶部 §1 的全局开头（import + set_cns_style_journal），且 `adata`/数据已就绪。
> 铁律：每张图用统一入口函数（plot_umap/plot_volcano/...），内部自动 ov.pl 优先 + mpl 兜底 + save_panel 收尾（finalize_figure → 建目录 → savefig），**不再手写 savefig、不再手动选 ov/mpl 路径**。

## 0. 速查卡（图型 → 统一入口 → 关键参数）

| 要画什么 | 统一入口（自动 ov/mpl 降级） | 关键参数 |
|---|---|---|
| UMAP / tSNE | `plot_umap(adata, color=..., save=...)` | basis 换 tSNE；labels=True 加 on-plot 标注 |
| Volcano | `plot_volcano(de, save=...)` | annotate_top=10；sig_pval/sig_fc 可调 |
| Dotplot | `plot_dotplot(adata, var_names=..., groupby=..., save=...)` | standard_scale='var'；dendrogram=False |
| Violin/Box | `plot_violin(adata, keys=..., groupby=..., save=...)` | violin_alpha=0.8；spine #b4aea9；wilcox 自动星号 |
| Heatmap | `plot_heatmap(adata, var_names=..., groupby=..., save=...)` | Z-score/row；vmin=-2,vmax=2；EXPR_CMAP |
| Spatial | `plot_spatial(adata_sp, color=..., save=...)` | scale bar 必须有；colorbar 横置 |
| Bar（比例） | `plot_bar(props, save=...)`（或 adata+groupby） | Y 从 0；95% CI；per-sample dots |
| 富集条形 | `plot_enrichment(enr, save=..., top_n=15)` | barh 按 -log10(FDR) 降序；条右标 gene count |
| L-R Bubble | `plot_lr_bubble(pair_labels, pathway_labels, sizes, mean_expr, save=...)` | size=-log10(p)；color=mean expr；x_idx/y_idx 可选 |
| Feature 矩阵 | `plot_feature_matrix(adata, genes, save=..., ncols=3)` | 共享 vmin/vmax=99th pct |
| PAGA | `plot_paga(adata, save=..., threshold=0.05)` | 前置 sc.tl.paga；threshold 滤噪声 |
| Chord / CCC | `plot_chord(weight_matrix, save=...)` | ≤8 cell types；lw∝weight |
| Pseudotime | `plot_pseudotime(adata, genes, save=...)` | LOESS lw=1.2；CI 带 alpha=0.15 |
| cellproportion | `plot_cellproportion(adata, groupby=..., save=...)` | stacked；MORLANDI |
| DE 分组散点 | `plot_de_scatter(de_dict, save=...)` | 多时点替代火山图；up红/down蓝 |
| 空间 CCC 共表达 | `plot_spatial_ccc(adata_sp, ligand, receptor, save=...)` | 双面板配受体共表达；scale bar |
| Milo beeswarm | `plot_milo(milo_result, save=...)` | 无预定义cluster的局部丰度；SpatialFDR着色 |
| 信号角色热图 | `plot_signaling_heatmap(comm_scores, save=...)` | outgoing/incoming；celltype×pathway |

## 1. 全局开头（每个脚本第一行）

```python
import sys; sys.path.insert(0, 'scripts/')
from cns_style import *
import matplotlib.pyplot as plt
import numpy as np
set_cns_style_journal('nature')   # 'nature'|'science'|'cell'|'generic'

# 统一入口函数（自动 ov.pl 优先 + mpl 兜底）
from cns_style import (plot_umap, plot_volcano, plot_dotplot, plot_violin,
                       plot_heatmap, plot_spatial, plot_bar, plot_enrichment,
                       plot_lr_bubble, plot_feature_matrix, plot_paga,
                       plot_chord, plot_pseudotime, plot_cellproportion)

# 绘图前校验（可选，新推荐，避免运行到一半 KeyError）
# assert_anndata_keys(adata, obs_cols=['celltype'], obsm_keys=['X_umap'])
```

自动设好：Morlandi 配色 / Arial 字体 / modular scale 字号 (7/8/10/12/14) / L-frame axes / outward ticks / 期刊 DPI / PDF 输出。下面所有模板都假设上面的 import 已执行。每个图型走统一入口函数：内部自动检测 omicverse 可用性（ov.pl 优先，mpl 兜底），返回 `(fig, ax)`，传 `save='...'` 自动过 `save_panel` 收尾。

## 2. 核心图型模板（已有，从 figure_guide 抽取并优化）

### 2.1 UMAP/tSNE

**统一入口**（自动 ov.pl 优先，mpl 兜底）：on-plot labels 代替 legend（铁律 1 例外）；无轴 + 圆形留白；大 cohort 不糊团（内部 `cohort_params(n_cells)` 联动 size/alpha/figsize）。

```python
assert_anndata_keys(adata, obs_cols=['celltype'], obsm_keys=['X_umap'])
fig, ax = plot_umap(adata, color='celltype', basis='X_umap',
                    save='A_umap', labels=True)
# 内部：ov 可用走 ov.pl.embedding（自动 omicverse 风格）；
#       ov 不可用走 mpl scatter + add_cluster_labels + clean_umap_axes + optical_margin
# tSNE：plot_umap(adata, basis='X_tsne', save='A_tsne')（需先跑 sc.tl.tsne，见 §3.4）
```

> **高级**：如需 ov.pl 原生精细控制（如自定义 legend 位置、手动点大小），可手动调
> `ov.pl.embedding(...)` + `add_cluster_labels(...)` + `clean_umap_axes(ax)` + `optical_margin(ax, 0.12)` + `save_panel(fig, name)`。

### 2.2 Volcano

**统一入口**（自动 ov.pl 优先，mpl 兜底）：列名必须是 `log2FC` / `padj`（可改名对齐）；`annotate_top=10` 自动标注 top 10 基因（italic）。

```python
de = pd.read_csv('de_results.csv')   # 列: gene, log2FC, padj
fig, ax = plot_volcano(de, pval_name='padj', fc_name='log2FC',
                       save='B_volcano', annotate_top=10)
# 内部：ov 可用走 ov.pl.volcano（figsize=recipe_figsize('volcano')）；
#       ov 不可用走 mpl scatter（volcano_colors 对齐 Up/Down/NS 色）+ polish_axes
# 阈值可调：sig_pval=0.05, sig_fc=1.0（默认）
```

> **高级**（手动 mpl 路径，可精调标注）：`volcano_colors()` 对齐 omicverse 默认色（Up=`#e25d5d`,
> Down=`#7388c1`, NS=`#d7d7d7`）；阈值线 `ls='--', lw=0.5, alpha=0.3`；top 基因用
> `gene_annotation_kwargs()` 标注；最后 `polish_axes(ax)` + `save_panel(fig, name)`。

### 2.3 Dotplot

**统一入口**（自动 ov.pl 优先，mpl 兜底）：`standard_scale='var'` 行标准化；`dendrogram=False`（列按生物学排序，不画聚类树）。

```python
fig, ax = plot_dotplot(adata, var_names=genes, groupby='celltype',
                       save='C_dotplot')
# 内部：ov 可用走 ov.pl.dotplot（standard_scale='var', dendrogram=False）；
#       ov 不可用走 mpl 兜底（点大小=%表达，色=均值）
# 如需统一量纲：内部用 num_categories=7（>7 类自动分组）
```

> **高级**：手动时 `ov.pl.dotplot(adata, var_names=genes, groupby='celltype', standard_scale='var',
> dendrogram=False)` + `fig = plt.gcf()` + `save_panel(fig, name)`。

### 2.4 Violin/Box

**统一入口**（自动 ov.pl 优先，mpl 兜底）：交替背景色带 + 暖灰 spine + wilcox 自动星号。

```python
fig, ax = plot_violin(adata, keys=['CD3D', 'MS4A1', 'LYZ', 'CD68'],
                      groupby='celltype', save='D_violin')
# 内部：ov 可用走 ov.pl.violin（violin_alpha=0.8, alternating_background=True,
#       spine #b4aea9, statistical_tests='wilcox'）；
#       ov 不可用走 mpl violinplot + 交替背景带 + strip 点（s=1, alpha=0.4）
# 手动星号：add_significance_bracket(ax, x1, x2, pval)（见 §4）
```

> **高级**（手动 mpl 路径，精细控制）：`palette_from_names(clusters[:6], ['霁蓝','藤黄','朱砂','青矾绿','胭脂紫','石英粉红'])`
> 取命名色板；`_lighten(color, 0.85)` 做交替背景带（`ax.axvspan(i-0.5, i+0.5)`）；`violinplot(showmedians=False,
> showextrema=False)` + strip（s=1, alpha=0.4）；spine `#b4aea9` + y-axis grid（alpha=0.3, lw=0.5）；
> 多基因每基因一行 subplot，figsize=(n_clusters×0.6+1, n_genes×2.8)。完整实现见 `omicverse_skills_examples.md`。

### 2.5 Heatmap

**统一入口**（自动 ov.pl 优先，mpl 兜底）：Z-score per row；`vmin=-2, vmax=2`；EXPR_CMAP；列注释条来自 manifest/cmap；`col_cluster=False` 按生物学排序。

```python
fig, ax = plot_heatmap(adata, var_names=genes, groupby='celltype',
                       save='E_heatmap')
# 内部：ov 不可用走 sc.pl.heatmap / sns.clustermap 兜底
#       （Z-score per row, vmin=-2, vmax=2, EXPR_CMAP, col_cluster=False, 白线分隔 groups）
```

> **高级**（sns.clustermap 手动、含列注释条）：`expr_z = mean_expr.apply(lambda r: (r-r.mean())/r.std(), axis=1)`+
> `sns.clustermap(expr_z, cmap=EXPR_CMAP, vmin=-2, vmax=2, col_colors=col_ann, col_cluster=False,
> row_cluster=True, figsize=recipe_figsize('heatmap', n_x=..., n_y=...))` + `save_panel(g.fig, name)`；
> scanpy 快速版：`sc.pl.heatmap(adata, var_names=genes, groupby='celltype', cmap=EXPR_CMAP, vmin=-2, vmax=2,
> swap_axes=True, show=False)` + `save_panel(plt.gcf(), name)`。

### 2.6 Spatial

**统一入口**（自动 ov.pl 优先，mpl 兜底）：组织 `alpha_img=1.0`（不透明）；spots `alpha=0.85`；**scale bar 必须有**（缺它 = 审稿人一眼扣分）；colorbar 横置。

```python
fig, ax = plot_spatial(adata_sp, color='Cxcl12', save='F_spatial')
# 内部：ov 可用走 ov.pl.plot_spatial（自动 tissue + spots + colorbar）；
#       ov 不可用走 squidpy sq.pl.spatial_scatter + add_scale_bar + add_elegant_colorbar
# 多基因：循环调用，每基因共享 vmin/vmax（99th pct clip）
```

> **高级**（squidpy 手动、组合拼图场景用）：`sq.pl.spatial_scatter(adata_sp, color=gene, ax=ax, size=1.2,
> cmap=EXPR_CMAP, vmin=0, alpha_img=1.0, alpha=0.85, title='', show=False)` +
> `add_scale_bar(ax, length_um=200, px_per_um=0.5)`（**必须**；长度取 100/200/500 中最接近图宽 1/5 者）+
> `add_elegant_colorbar(ax.collections[0], ax, label=gene, orientation='horizontal')` +
> `clean_umap_axes(ax, xlabel='', ylabel='')` + `save_panel(fig, name)`。

### 2.7 Bar（比例）

**统一入口**（自动 ov.pl 优先，mpl 兜底）：Y 从 0；95% CI error bars（capsize=3, lw=1）；per-sample dots overlay（s=15, alpha=0.7）。

```python
props = (adata.obs.groupby(['sample', 'celltype']).size()
         .unstack(fill_value=0).apply(lambda r: r / r.sum(), axis=1))  # 行=样本, 列=celltype
fig, ax = plot_bar(props, save='G_proportion')
# 或直接传 adata：plot_bar(adata, groupby='celltype', save='G_proportion')
# 内部：mpl 兜底 = bar + 1.96*sem error bars + per-sample dots + polish_axes
```

> **高级**：手动时 `ax.bar(i, mean, yerr=1.96*sem, capsize=3, width=0.6, color=MORLANDI[i%len(MORLANDI)],
> error_kw=dict(lw=1, ecolor=NEAR_BLACK))` + `ax.scatter(np.full(len(props), i), props[ct], s=15, alpha=0.7,
> color=NEAR_BLACK, edgecolor='none', zorder=3)` + legend 右侧外置（铁律 1）+ `polish_axes(ax)` + `save_panel(fig, name)`。

### 2.8 富集条形图（GO/KEGG）

**统一入口**（自动 ov.pl 优先，mpl 兜底）：水平 barh；`-log10(FDR)` 降序；条右标 gene count；通路名 ≤40 字符截断；`polish_axes` 无 grid。

```python
# enr: pandas DataFrame, 列 Term/FDR/Gene_count（来自 gseapy/GO 工具输出）
fig, ax = plot_enrichment(enr, save='H_enrichment', top_n=15)
# 内部：mpl 兜底 = barh（top_n 条, -log10(FDR) 降序）+ 条右 gene count + polish_axes(subtle_grid=False)
```

> **高级**：手动时 `terms = enr.nsmallest(15, 'FDR')` + `ax.barh(y_pos, -np.log10(terms['FDR']),
> color='#BF616A', height=0.6)` + 条右 `ax.text(b.get_width()+0.1, ..., str(n), fontsize=6, color=GREY)` +
> 通路名 `t[:40]` 截断 + `polish_axes(ax, subtle_grid=False)` + `save_panel(fig, name)`。

### 2.9 L-R Bubble

**统一入口**（自动 ov.pl 优先，mpl 兜底）：x = cell-type pair (sender→receiver)；y = pathway；size=`-log10(p)` 映射 `s∈[20,200]`；color=mean expr（EXPR_CMAP）；≤10 pairs × ≤15 pathways。

```python
fig, ax = plot_lr_bubble(x_idx, y_idx, sizes, mean_expr,
                         pair_labels, pathway_labels, save='I_lr_bubble')
# 内部：mpl 兜底 = ax.scatter(s=sizes, c=mean_expr, cmap=EXPR_CMAP, edgecolor='#2E3440', linewidth=0.3,
#       alpha=0.85) + add_elegant_colorbar + polish_axes(subtle_grid=False)
```

> **高级**：手动时 pair 标签 `rotation=45, ha='right', fontsize=6`，pathway 标签 `fontsize=7`；
> `add_elegant_colorbar(scatter, ax, label='Mean expression')` + `polish_axes(ax, subtle_grid=False)` + `save_panel(fig, name)`。

### 2.10 Feature Plot 矩阵（多基因 UMAP）

**统一入口**（自动 ov.pl 优先，mpl 兜底）：`ncols=3`；所有 panel 共享 `vmin=0, vmax=99th percentile`（跨基因可比）；每 panel `clean_umap_axes`。

```python
fig, ax = plot_feature_matrix(adata, genes, basis='X_umap',
                              save='J_feature_matrix', ncols=3)
# 内部：ov 可用走 ov.pl.embedding(adata, color=genes, ncols=3, vmin=0, vmax=p99)；
#       ov 不可用走 mpl scatter 逐基因面板 + 共享 vmax + clean_umap_axes
```

> **高级**：手动时 `p99 = np.percentile(expr_mat, 99)` + `ov.pl.embedding(adata, color=genes, ncols=3,
> vmin=0, vmax=p99, show=False)` + 遍历 `axs` 调 `clean_umap_axes(a)` + `save_panel(plt.gcf(), name)`。

## 3. 补充图型模板

### 3.1 PAGA（轨迹抽象图）

**统一入口**（自动 ov.pl 优先，mpl 兜底）。前置必须算 PAGA 拓扑：`sc.tl.paga(adata, groups='leiden')`（结果存 `adata.uns['paga']`）。

```python
sc.tl.paga(adata, groups='leiden')        # 前置：一次，基于 connectivities
fig, ax = plot_paga(adata, save='K_paga', threshold=0.05)
# 内部：mpl/scanpy 兜底 = sc.pl.paga(adata, colors='leiden', ax=ax, show=False, threshold=0.05) + polish_axes
# 叠加到 UMAP 展示：plot_umap(adata, color='leiden', save='K_paga_umap') 后再手动叠加 PAGA 连线（见高级）
```

> **高级**（UMAP 叠加 PAGA 连线，推荐展示用）：`ov.pl.embedding(adata, basis='X_umap', color='leiden',
> size=3, alpha=0.5, ax=ax, show=False, legend_loc=None)` + `sc.pl.paga(adata, colors='leiden',
> pos=adata.obsm['X_umap'], ax=ax, show=False, threshold=0.05, edge_width_scale=0.5)` +
> `clean_umap_axes(ax)` + `save_panel(fig, name)`。

### 3.2 Chord / CCC（细胞通讯弦图）

**统一入口**（自动 ov.pl 优先，mpl 兜底）：≤8 cell types（再多糊成球）；边颜色 = source 色、alpha=0.5；lw ∝ 通讯强度。

```python
comm = pd.read_csv('lr_interactions.csv')   # 列: source, target, weight
weight = comm.pivot_table(index='source', columns='target', values='weight',
                          aggfunc='sum').fillna(0)
fig, ax = plot_chord(weight, save='L_chord')
# 内部：ov 可用走 ov.pl.CellChatViz → netVisual_chord_cell（签名以实际 ov 版本为准）；
#       ov 不可用走 networkx circular layout 兜底（≤8 节点, 弦线 lw∝weight, alpha=0.5）
```

> **高级**（networkx 兜底实现）：`G = nx.from_pandas_adjacency(weight)` + `G.subgraph(nodes[:8])` +
> `pos = nx.circular_layout(G)` + 节点 `ax.scatter(s=800, color=palette[n], edgecolor='white', zorder=5)` +
> 弦 `ax.plot([x1,x2],[y1,y2], color=palette[u], alpha=0.5, lw=0.5+3*w/maxw, solid_capstyle='round')` +
> `ax.set_aspect('equal'); ax.axis('off')` + `save_panel(fig, name)`。

### 3.3 Pseudotime gene-along-trajectory

**统一入口**（自动 ov.pl 优先，mpl 兜底）：每基因一行 subplot；LOESS 平滑线 lw=1.2 + 95% CI 带 alpha=0.15；statsmodels 可用则用之，否则 numpy polyfit(deg=3) 兜底（try import，不崩）。

```python
fig, ax = plot_pseudotime(adata, genes=['Gata4', 'Tbx5', 'Nppa'],
                          pseudotime_col='pseudotime', save='M_pseudotime')
# 内部：raw scatter(s=3, alpha=0.3) + LOESS 平滑（statsmodels lowess 优先，polyfit 兜底）+ CI 带
# 分支拓扑 → 绝不用单线性曲线（多分支用分面或树状叠加，见 figure_guide §5.11）
```

> **高级**（手动 LOESS）：`sm.nonparametric.lowess(y, x, frac=0.3)`（ImportError 时 `np.polyfit(x, y, 3)` 兜底）+
> `ax.plot(xs, yh, lw=1.2, color='#BF616A')` + CI 带 `ax.fill_between(xs, yh-1.96*se, yh+1.96*se,
> alpha=0.15, color='#BF616A', lw=0)` + 每基因 `polish_axes(ax)` + `save_panel(fig, name)`。

### 3.4 tSNE 专属

**统一入口**：tSNE 与 UMAP 共用 `plot_umap`，差别只有 `basis='X_tsne'` + 前置 `sc.tl.tsne` + 轴标签 `TSNE1/TSNE2`。figsize 同 UMAP 正方形（内部 `cohort_params` 联动）。

```python
sc.tl.tsne(adata, n_pcs=30)                 # 前置：tSNE 计算（慢，一次即可）
fig, ax = plot_umap(adata, color='celltype', basis='X_tsne',
                    save='A_tsne', labels=True)
# 内部：ov 可用走 ov.pl.embedding；mpl 兜底走 add_cluster_labels +
#       clean_umap_axes(xlabel='TSNE1', ylabel='TSNE2') + optical_margin
```

> 参数与 §2.1 完全一致，仅 basis/轴标签不同。

### 3.5 cellproportion（细胞比例堆叠柱）

**统一入口**（自动 ov.pl 优先，mpl 兜底）：分组 × celltype 堆叠比例柱；`palette_from_names` 命名色板，超出 6 类灰掉（5+1 纪律）。

```python
assert_anndata_keys(adata, obs_cols=['condition', 'celltype'])
fig, ax = plot_cellproportion(adata, groupby='condition', save='N_cellproportion')
# 内部：ov 可用走 ov.pl.cellproportion（签名以实际 ov 版本为准）；
#       ov 不可用走 mpl 堆叠柱兜底（bottom 累加 + palette_from_names + y 从 0 到 1）
# 无重复的条件比较只能放 supplement（见 figure_guide §0.1 决策表）
```

> **高级**（手动 mpl 堆叠）：`props = adata.obs.groupby('condition').apply(
> lambda df: df['celltype'].value_counts(normalize=True)).unstack(fill_value=0)` +
> `ax.bar(range(len(props)), props[ct], bottom=bottom, width=0.6, color=ct_colors.get(ct, MUTED))` +
> `ax.set_ylim(0, 1)` + legend 右侧外置 + `polish_axes(ax)` + `save_panel(fig, name)`。

### 3.6 DE 分组散点（多时点/多条件）

**统一入口**（mpl，ov 无对应函数）：火山图在多时点/多组比较时不可读——分组散点（x=组别，y=logFC，每点=一基因）直接可比。

```python
import pandas as pd
de_dict = {tp: pd.read_csv(f'de_{tp}.csv') for tp in ['13w', '24w', '36w']}  # 每张: gene, log2FC, padj
fig, ax = plot_de_scatter(de_dict, save='O_de_scatter',
                          sig_pval=0.05, sig_fc=1.0, annotate_top=3)
# 内部：显著=彩色大点(up红/down蓝)，ns=灰小点，每组标注 top3
```

### 3.7 空间 CCC 共表达（空转特异）

**统一入口**（mpl，ov/sq 无直接函数）：配体/受体空间共表达双面板——空转 CCC 的最低证据要求。

```python
fig, (ax1, ax2) = plot_spatial_ccc(adata_sp, ligand='Cxcl12', receptor='Cxcr4',
                                   save='P_spatial_ccc')
# 内部：左=ligand 空间表达，右=receptor 空间表达，共享 colorscale + scale bar
```

### 3.8 Milo beeswarm（局部丰度，无预定义 cluster）

**统一入口**（mpl，ov 无对应函数）：Milo 差异丰度——KNN 节点 logFC 按 population 分组，SpatialFDR 着色。2024-2026 Nature/Cell 高频出现。

```python
fig, ax = plot_milo(milo_result, save='Q_milo', sig_threshold=0.1)
# milo_result: DataFrame, 列 Population/logFC/SpatialFDR（miloR 输出）
```

### 3.9 CCC 信号角色热图

**统一入口**（mpl，ov 无对应函数）：每细胞类型的 outgoing/incoming 通讯强度热图。

```python
fig, ax = plot_signaling_heatmap(comm_scores, save='R_signaling_heatmap', mode='outgoing')
# comm_scores: DataFrame, 行=cell type, 列=pathway, 值=通讯分数
```

### 3.10 Distance distribution（细胞间距离分布——空转标配）

**统一入口**（mpl + scipy cKDTree）：组 A 每个 spot 到组 B 最近邻的欧氏距离箱线图 + 置换检验 p 值。A/B 距离偏近 = 共定位，偏远 = 互斥。

```python
from cns_style import plot_distance_distribution
plot_distance_distribution(adata_sp, group_a='Macrophage', group_b='Fibroblast',
                           groupby='condition', save='S_distance_mac_fib')
# 需 obsm['spatial']；groupby=None 时不分组合一个箱线图；p 值标在图上方（置换 n 次）
```

### 3.11 Neighborhood enrichment（邻域富集热图）

**统一入口**（squidpy.gr.nhood_enrichment → mpl 手动共邻兜底）：哪些细胞类型显著共邻。

```python
from cns_style import plot_nhood_enrichment
plot_nhood_enrichment(adata_sp, cluster_key='celltype', save='T_nhood_enrich')
# 需先跑 ov.space.spatial_neighbors / sq.gr.spatial_neighbors（obsp['spatial_connectivities']）
```
z-score 方形热图（cluster × cluster），|z|>1.96 标 *、|z|>2.58 标 **，DIVERGING_CMAP。

### 3.12 Colocalization score（空间共定位散点）

**统一入口**（mpl）：per-spot 双信号相关散点（基因名或去卷积比例列），>5000 点自动转 hexbin。

```python
from cns_style import plot_colocalization
plot_colocalization(adata_sp, var_x='CD68', var_y='Macrophage_frac', save='U_coloc')
# var_x/var_y 可为基因（var_names）或 obs 比例列；图上标注 ρ + p（Spearman 默认）
```

### 3.13 Enrichment scatter（富集气泡散点）

**统一入口**（mpl）：富集结果 5 维气泡图（x=GeneRatio, y=-log10(FDR), 点大小=Count, 颜色=FDR），比条形图信息密度高。

```python
from cns_style import plot_enrichment_scatter
plot_enrichment_scatter(enr_df, x='GeneRatio', y='FDR', size='Count',
                        color='FDR', top_n=15, save='V_enrich_bubble')
# enr_df: GO/KEGG/GSEA 输出 DataFrame；top_n 条通路名标注在点旁
```

## 4. 统计标注（add_significance_bracket）

**规则**：
- Star 定义写在 legend：`*P<0.05, **P<0.01, ***P<0.001, ****P<0.0001`
- 优先报 exact P（`P=3.2×10⁻⁵`），star 是辅助
- bracket 线 `lw=0.8, color='#2E3440'`（不用纯黑）
- 多组比较时 bracket 高度错开，避免交叉；`ns` 也标（不显著也是信息）

```python
# 单组比较：y 不传时自动定位（数据最大值上方 2%）
add_significance_bracket(ax, x1=0, x2=1, pval=3.2e-5)

# 多组比较：自动错开高度，ns 也标
add_significance_bracket(ax, x1=0, x2=2, pval=0.003)
add_significance_bracket(ax, x1=1, x2=2, pval=0.21)   # → 'ns'
```

## 5. Worked Example（三个端到端，从数据到 PDF）

以下脚本是完整可跑的（含 §1 全局开头），可直接复制成 `.py`。

### Example 1: UMAP（统一入口 + save_panel）

```python
import sys; sys.path.insert(0, 'scripts/')
from cns_style import *
import scanpy as sc

set_cns_style_journal('nature')

# 假设 adata 已完成 QC → normalize → PCA → neighbors → leiden → UMAP
assert_anndata_keys(adata, obs_cols=['celltype'], obsm_keys=['X_umap'])
fig, ax = plot_umap(adata, color='celltype', basis='X_umap',
                    save='A_umap', labels=True)   # → panels/A_umap.pdf
# 内部已自动：ov.pl.embedding 优先（cohort_params 联动 size/alpha）或 mpl 兜底 + save_panel 收尾
```

### Example 2: 分组散点图（多时点 DE）

> 注：多时点/多组 DE 分组散点（figure_guide §11.3）**无对应统一入口**（14 个统一入口不含此自定义图型），
> 保持手动路径；单对比 volcano 用 `plot_volcano(de, save=...)`。

```python
import sys; sys.path.insert(0, 'scripts/')
from cns_style import *
import pandas as pd

set_cns_style_journal('nature')

# 多时点 DE：x=组别，y=log2FC，每点=一个基因
comparisons = ['13w', '24w', '36w']                  # vs ctrl
de_dict = {tp: pd.read_csv(f'de_{tp}.csv') for tp in comparisons}  # 每张: gene, log2FC, padj

fig, ax = plt.subplots(figsize=recipe_figsize('bar', n_x=len(comparisons)))
for i, tp in enumerate(comparisons):
    de = de_dict[tp]
    sig = (de['padj'] < 0.05) & (de['log2FC'].abs() > 0.5)
    ns = ~sig
    ax.scatter(np.full(ns.sum(), i) + np.random.uniform(-0.15, 0.15, ns.sum()),
               de.loc[ns, 'log2FC'], s=8, alpha=0.3, color='#d7d7d7',
               edgecolor='none', rasterized=True)
    cols = np.where(de.loc[sig, 'log2FC'] > 0, '#e25d5d', '#7388c1')
    ax.scatter(np.full(sig.sum(), i) + np.random.uniform(-0.15, 0.15, sig.sum()),
               de.loc[sig, 'log2FC'], s=20, alpha=0.7, c=cols,
               edgecolor='white', linewidth=0.3, zorder=3)
    top3 = de.loc[sig].reindex(
        de.loc[sig, 'log2FC'].abs().sort_values(ascending=False).index[:3])
    for _, r in top3.iterrows():
        ax.annotate(r['gene'], xy=(i, r['log2FC']), xytext=(i+0.15, r['log2FC']+0.2),
                    fontsize=6, fontstyle='italic', color=NEAR_BLACK,
                    arrowprops=dict(arrowstyle='-', lw=0.4, color=GREY))
ax.axhline(0, color=GREY, lw=0.5)
ax.axhline(1, color=GREY, lw=0.4, ls='--', alpha=0.3)
ax.axhline(-1, color=GREY, lw=0.4, ls='--', alpha=0.3)
ax.set_xticks(range(len(comparisons)))
ax.set_xticklabels([f'{c} vs ctrl' for c in comparisons], fontsize=8, rotation=20, ha='right')
ax.set_ylabel(r'log$_2$(Fold Change)', fontsize=10, labelpad=10)
polish_axes(ax)
save_panel(fig, 'B_de_scatter')
```

### Example 3: 空间表达（统一入口）—— 组合拼图用手动路径

```python
import sys; sys.path.insert(0, 'scripts/')
from cns_style import *

set_cns_style_journal('nature')

# 单图场景 —— 统一入口（自动 ov.pl 优先 / squidpy 兜底 + scale bar + 横置 colorbar + 去轴）
fig, ax = plot_spatial(adata_sp, color='Cxcl12', save='C_spatial')
# → panels/C_spatial.pdf
```

> **组合拼图场景**（空间 overlay + 配对箱线共用 1×2 figure）：`plot_spatial` 不暴露 ax 参数，组合图走手动 squidpy 路径：
>
> ```python
> import squidpy as sq
> fig, (ax1, ax2) = plt.subplots(1, 2, figsize=recipe_figsize('bar', n_x=2),
>                                gridspec_kw={'width_ratios': [1.2, 1]})
>
> # 左：空间 overlay + scale bar + 横置 colorbar
> sq.pl.spatial_scatter(adata_sp, color='Cxcl12', ax=ax1, size=1.2, cmap=EXPR_CMAP,
>                       vmin=0, alpha_img=1.0, alpha=0.85, title='', show=False)
> add_scale_bar(ax1, length_um=200, px_per_um=0.5)
> clean_umap_axes(ax1, xlabel='', ylabel='')
> add_elegant_colorbar(ax1.collections[0], ax1, label='Expression', orientation='horizontal')
>
> # 右：niche 内 vs 外的表达分布（配对箱线 + 显著性 bracket）
> ge = adata_sp[:, 'Cxcl12'].X.toarray().ravel()
> in_niche = (adata_sp.obs['niche'] == 'fibrotic').values
> bp = ax2.boxplot([ge[~in_niche], ge[in_niche]], positions=[0, 1], widths=0.4,
>                  patch_artist=True, showfliers=False,
>                  boxprops=dict(facecolor='#88C0D0', edgecolor=NEAR_BLACK, lw=0.8),
>                  medianprops=dict(color='#BF616A', lw=1.5))
> bp['boxes'][1].set_facecolor('#BF616A')
> for i, mask in enumerate([~in_niche, in_niche]):
>     jit = np.random.uniform(-0.1, 0.1, mask.sum())
>     ax2.scatter(np.full(mask.sum(), i) + jit, ge[mask], s=3, alpha=0.4,
>                 color=NEAR_BLACK, edgecolor='none', rasterized=True)
> ax2.set_xticks([0, 1]); ax2.set_xticklabels(['Other', 'Fibrotic niche'], fontsize=8)
> ax2.set_ylabel('Cxcl12 expression', fontsize=9, labelpad=8, fontstyle='italic')
> add_significance_bracket(ax2, 0, 1, pval=1e-6)
> polish_axes(ax2)
> save_panel(fig, 'C_spatial_quant')
> ```