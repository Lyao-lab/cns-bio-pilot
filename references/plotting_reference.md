# Plotting Reference — 发表级绘图代码速查

> 本文件是 figure-production skill 的**代码层**：每种图型的精确参数 + 可跑模板。
> 配套：流程查 `skills/visualization/figure-production/SKILL.md`；原则/视觉规格查 `figure_guide.md`；外部参考查 `omicverse_skills_examples.md`。
> 所有模板假设已执行顶部 §1 的全局开头（import + set_cns_style_journal），且 `adata`/数据已就绪。
> 铁律：每张图用统一入口函数（plot_umap/plot_volcano/...），内部自动 ov.pl 优先 + mpl 兜底 + save_panel 收尾（finalize_figure → 建目录 → savefig），**不再手写 savefig、不再手动选 ov/mpl 路径**。

## 0. 速查卡（图型 → 统一入口 → 关键参数）

| 要画什么 | 统一入口（自动 ov/mpl 降级） | 关键参数 |
|---|---|---|
| UMAP / tSNE | `plot_umap(adata, color=..., save=...)` | basis 换 tSNE；labels=True 加 on-plot 标注 |
| Volcano | `plot_volcano(de, save=...)` | annotate_top=10 防撞标注；sig_pval/sig_fc 可调 |
| Dotplot | `plot_dotplot(adata, var_names=..., groupby=..., save=...)` | standard_scale='var'；dendrogram=False |
| Violin/Box | `plot_violin(adata, keys=..., groupby=..., save=...)` | violin_alpha=0.8；spine #b4aea9；wilcox 自动星号 |
| Heatmap | `plot_heatmap(adata, var_names=..., groupby=..., save=...)` | Z-score/row；vmin=-2,vmax=2；EXPR_CMAP |
| Spatial | `plot_spatial(adata_sp, color=..., save=...)` | scale bar 必须有；colorbar 横置 |
| Bar（比例） | `plot_bar(props, save=...)`（或 adata+groupby） | Y 从 0；95% CI；per-sample dots |
| 富集条形 | `plot_enrichment(enr, save=..., top_n=15)` | barh -log10(FDR) 降序；group_col 分组模式；cap 轴封顶；pretty 术语清洗 |
| L-R Bubble | `plot_lr_bubble(pair_labels, pathway_labels, sizes, mean_expr, save=...)` | size=-log10(p)；color=mean expr；x_idx/y_idx 可选 |
| Feature 矩阵 | `plot_feature_matrix(adata, genes, save=..., ncols=3)` | 共享 vmin/vmax=99th pct+单一共享色条 |
| PAGA | `plot_paga(adata, save=..., threshold=0.05)` | 前置 sc.tl.paga；threshold 滤噪声 |
| Chord / CCC | `plot_chord(weight_matrix, labels=..., save=...)` | ≤8 节点；扇区弧长∝强度+贝塞尔 ribbon |
| Pseudotime | `plot_pseudotime(adata, genes, save=...)` | LOESS lw=1.2；CI 带 alpha=0.15 |
| cellproportion | `plot_cellproportion(adata, groupby=..., save=...)` | stacked；MORLANDI |
| DE 分组散点 | `plot_de_scatter(de_dict, save=...)` | 多时点替代火山图；抖动防熔柱 |
| 空间 CCC 共表达 | `plot_spatial_ccc(adata_sp, ligand, receptor, save=...)` | 双面板配受体共表达；scale bar |
| Milo beeswarm | `plot_milo(milo_result, save=...)` | 无预定义cluster的局部丰度；SpatialFDR着色 |
| 信号角色热图 | `plot_signaling_heatmap(comm_scores, save=...)` | outgoing/incoming；celltype×pathway |
| 山脊图 | `plot_ridge(adata, keys=..., groupby=..., save=...)` | >5组分布比较；overlap=0.6 |
| 箱线图 | `plot_boxplot(adata, keys=..., groupby=..., save=...)` | 抖动点+箱体；简洁替代violin |
| 云雨图 | `plot_raincloud(data, x=..., y=..., save=...)` | 半小提琴+箱线+雨点三合一；n≥5 才画琴；test='mwu' 参照组括号 |
| 核密度 | `plot_kde(data, x=..., y=..., hue=..., save=...)` | 单/双变量密度；data=DataFrame |
| 直方图 | `plot_histplot(data, x=..., hue=..., save=...)` | QC标配；bins='auto' |
| 抖动散点 | `plot_stripplot(data, x=..., y=..., hue=..., save=...)` | 每点可见；summary='mean' |
| 堆叠面积 | `plot_stackarea(adata, celltype_col=..., groupby=..., save=...)` | 比例随连续变量变化；inband_labels+number_legend 带内编号标签 |
| 柱+点组合 | `plot_bardotplot(adata, groupby=..., color=..., save=...)` | 均值柱+分布点 |
| 堆叠火山 | `plot_stacking_vol(data_dict, save=...)` | 多条件DE并排（ov优先/mpl兜底）；data_dict={条件:DE} |
| UpSet 图 | `plot_upset(sets, top_n=30, save=...)` | >3组交集；sets={名称:set} |
| Venn 图 | `plot_venn(sets, save=...)` | ≤4组交集；sets={名称:set} |
| 森林图 | `plot_forest(data, estimate=..., lower=..., upper=..., save=...)` | 无效线 auto（OR→1.0，log→0）；null_value 可覆盖 |
| 回归散点 | `plot_regplot(data, x=..., y=..., fit='linear', save=...)` | 相关性分析；95% CI 带；fit='lowess'可选 |
| 通讯热图 | `plot_ccc_heatmap(adata, plot_type='heatmap', save=...)` | 需liana预计算（缺失时明确报错）；plot_type='dot'/'tile' |
| PCA方差比 | `plot_pca_variance(adata, n_pcs=30, save=...)` | QC标配；方差比柱+累计线双轴 |
| HVG散点 | `plot_hvg_scatter(adata, save=...)` | QC标配；均值vs离散 |
| 雷达图（多指标方法对比） | `plot_radar(values, axis_labels, axis_ranges=...)` | 每辐条独立量程归一；整合基准对比首选 |
| 消融/组件对比 barh | `alpha_ramp(hex, n)` + `ax.barh(...)` | 首项最实=完整模型；数值标签在条外用 NEAR_BLACK |
| 曲线事件标注 | `mark_events(ax, x, y, events)` | label 加 '*' 抬高防撞 |
| 斜率图（组成 movers） | `plot_slope(wide_df, save=...)` | 端点直接标签带 Δ；top_n 选变化最大；emphasize 强调加粗 |
| 发散棒棒糖 | `plot_lollipop(df, label_col=..., value_col=..., save=...)` | 实心=主统计量+空心=第二统计量；null_band 置换零带；ref_line |
| QC 条形卡片 | `plot_qc_cards(metrics, covariate=..., save=...)` | 行=样本、列=指标；GA 渐变色块；数值直标+列顶范围 |
| 样本趋势小倍数 | `plot_trend_grid(df, x=..., y=..., by=..., save=...)` | 点径∝n_cells；标题内嵌 ρ+星；highlight 红描边 |
| 空间放大图（IF 风格） | `plot_spatial_zoom(adata_sp, color=..., save=...)` | 自动取框+inset 红框定位；物理点径；自适应比例尺 |
| 面板字母三件套 | `stamp_panel(fig, 'a', title, subtitle)` | 字母+版内标题+方法学灰副标题（≥8in 宽画布） |
| 画布级重叠断言 | `assert_no_text_overlap(fig)` | raise 版验收门；补查 fig.texts/title/tick/legend |
| 直接标签防撞 | `direct_label(ax, ys, texts, side=...)` | 端点标签像素级 stagger，gap_pt 最小行距 |
| 标签斥力求解 | `layout_labels(fig, ax, texts)` | on-plot 标签 bbox 实测推开（UMAP 标签救星） |
| bar 风坐标 | `polish_axes(ax, variant='bar', grid_axis='x')` | 只留灰底脊+值轴浅网格（barh 用 'x'，竖条 'y'） |
| Sankey 状态转换 | `plot_sankey(flows, save=...)` | 转移矩阵→节点+贝塞尔 ribbon；min_flow 去毛刺 |
| CNV 基因组热图 | `plot_cnv_heatmap(cnv, chrom=..., groups=..., save=...)` | inferCNV 式；染色体分隔线+分组色条；DIVERGING 0=白 |
| 轴向/距离梯度曲线 | `plot_axis_gradient(data, x, y, hue, save=...)` | zonation/边界带/病理共定位；LOWESS+分位带；norm='each' 每信号归一 |
| 克隆扩增追踪 | `plot_clone_expansion(clone_df, clone_col, group_col, save=...)` | composition=大小分类堆叠柱；track=top 克隆跨组折线 |

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

**统一入口**（自动 ov.pl 优先，mpl 兜底）：水平 barh；`-log10(FDR)` 降序；条右标 gene count；通路名 pretty 清洗（去 GOBP_/HALLMARK_ 前缀、介词小写、48 字符截断）；`polish_axes(variant='bar')`。
**升级**（fetal_heart ORA 系列）：`group_col` 分组模式（每组 per_group 条、组标题加粗着色+分隔线、组色跨 panel 一致、FDR>0.05 标签置灰）；`cap` 极端值轴封顶（核糖体类 -log10≈98 不再压扁其他条）；详见速查卡。

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

### 3.2 CCC 细胞通讯（统一入口 plot_ccc，layout 路由 chord/network）

**统一入口**——对齐 `ov.pl.ccc_network_plot` 的 `plot_type` 设计：一个函数支持多种布局，用 `layout` 参数路由。≤8 cell types 用 chord（再多糊成球）；复杂拓扑用 network。

```python
comm = pd.read_csv('lr_interactions.csv')   # 列: source, target, weight
weight = comm.pivot_table(index='source', columns='target', values='weight',
                          aggfunc='sum').fillna(0)

# chord 布局（环形弦图，展示"谁给谁收信号"）
fig, ax = plot_ccc(weight, layout='chord', save='L_chord')

# network 布局（力导向网络图，节点大小=加权度，适合复杂拓扑）
fig, ax = plot_ccc(weight, layout='network', save='L_ccc_net')
```

> **路由对照**（cns_style → omicverse）：`layout='chord'` ≈ `ov.pl.ccc_network_plot(plot_type='chord')`；
> `layout='network'` ≈ `plot_type='diff_network'`。cns_style 内部 `plot_chord` / `plot_ccc_network` 是
> 两种布局的具体实现，`plot_ccc` 是统一入口。
>
> **chord 高级**（networkx 兜底）：`G = nx.from_pandas_adjacency(weight)` + `G.subgraph(nodes[:8])` +
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

### 3.14 CCC network（plot_ccc layout='network'，力导向布局）

> §3.2 已介绍统一入口 `plot_ccc(layout='chord'|'network')`。本节补充 network 布局的细节。

**用法**：`plot_ccc(weight_mat, layout='network', labels=cell_types, ...)`，内部调 `plot_ccc_network`。
方阵互作强度 → 力导向网络图（节点=细胞类型/模块，边=互作强度）。与 chord 互补：网络图展示复杂拓扑、可容纳 >8 节点，节点大小∝加权度。来源：CoVarNet Nature 2025 `gr.igraph_global`（Fruchterman-Reingold 布局）。

```python
plot_ccc(weight_mat, layout='network', labels=cell_types,
         edge_threshold=0.1, node_size_scale=500, save='W_ccc_network')
# weight_mat: N×N 方阵（DataFrame 自动取 index 为标签）；layout='circle' 可切环形
# edge_threshold 过滤弱连接；边透明度/宽度∝权重，灰阶着色
```

### 3.15 Deconvolution pie grid（去卷积饼图网格）

**统一入口**（mpl)：空转 AnnData + 去卷积比例列 → 每个 spot 一个微型饼图（细胞类型比例）。来源：Redeconve Nat Commun 2023 `spatial.piechart`。细胞类型 >6 时自动聚合 <5% 为 'Other'；spot 数 >max_spots 随机采样防过密。

```python
from cns_style import plot_deconv_pie
plot_deconv_pie(adata_sp, prop_cols=None, max_spots=500, save='X_deconv_pie')
# prop_cols=None 自动检测 obs 中 prop/frac 开头的数值列；有离散 celltype 列时传 cluster_key 直接着色
# 图例外置右侧；半径按最近邻距离自适应
```

### 3.16 Ridge plot（山脊图——多组分布叠放比较）

**统一入口**（ov.pl.ridgeplot 优先，mpl 兜底）：>5 组时比 violin 更清晰——分布叠放避免遮挡，CNS marker 验证标配。

```python
from cns_style import plot_ridge
plot_ridge(adata, keys=['COL1A1'], groupby='celltype', save='Y_ridge')
# 多基因：keys=['COL1A1','DCN','PDGFRB']，逐基因叠放
# overlap=0.6 控制山脊重叠程度；order='median' 按中位数排序
```

### 3.17 Boxplot（箱线图+抖动点）

**统一入口**（ov.pl.boxplot 优先，mpl 兜底）：分布比较的简洁替代 violin——抖动点+箱体，信号更聚焦形状与异常值。

```python
from cns_style import plot_boxplot
plot_boxplot(adata, keys=['COL1A1'], groupby='celltype', save='Z_boxplot')
# 多基因：keys=['COL1A1','DCN','PDGFRB']；jitter=0.3 抖动宽度防重叠
# showfliers=False 隐藏异常点（CNS 常隐）；与 §3.16 ridge 二选一，不并列
```

### 3.18 KDE plot（核密度估计）

**统一入口**（ov.pl.kdeplot 优先，mpl 兜底）：单/双变量密度——data 是 tidy DataFrame（不是 AnnData），适合跨样本/跨条件分布叠加。

```python
from cns_style import plot_kde
plot_kde(data=df, x='expr', hue='group', save='AA_kde')
# data: tidy DataFrame，列含 x（数值）与 hue（分组）
# 双变量：plot_kde(data=df, x='g1', y='g2') 画等高密度；fill=True 填充曲线
```

### 3.19 Histogram（直方图——QC 标配）

**统一入口**（ov.pl.hist 优先，mpl 兜底）：QC 标配——n_genes/pct_mt/total_counts 分布必查。

```python
from cns_style import plot_histplot
plot_histplot(data=df, x='n_genes', hue='condition', bins=50, save='AB_hist_qc')
# data: tidy DataFrame；bins='auto' 或显式整数；hue 分组分色叠加
# 多指标并排 subplot：x=['n_genes','pct_mt','total_counts'] 逐列
```

### 3.20 Strip plot（抖动散点）

**统一入口**（ov.pl.stripplot 优先，mpl 兜底）：每点可见——样本量小时比 box/violin 更诚实。

```python
from cns_style import plot_stripplot
plot_stripplot(data=df, x='group', y='expr', hue='condition', save='AC_strip')
# data: tidy DataFrame；jitter 自动加横向抖动防重叠
# summary='mean' 叠加均值线；点过多自动 alpha 降密度
```

### 3.21 Stacked area（堆叠面积图——比例随连续变量变化）

**统一入口**（mpl，ov 无对应函数）：celltype 比例随连续变量（pseudotime/层级）变化——轨迹组成分析标配。

```python
from cns_style import plot_stackarea
plot_stackarea(adata, celltype_col='celltype', groupby='pseudotime', save='AD_stackarea')
# 内部：按 groupby 分箱 → 每 bin 各 celltype 比例 → 堆叠面积
# bin 数过多自动合并；x 轴标签取 bin 中点
# 升级（fetal_heart fig1d）：inband_labels=True 带内标签（字色按底色亮度自适应）、
# number_legend=True 带内编号+图例 "编号 全名"（类型>10 时唯一可读形态）、
# groups_of={类型: 大类} 大类边界白粗线
```

### 3.22 Bar-dot plot（柱+点组合）

**统一入口**（mpl，ov 无对应函数）：均值柱 + 分布点——同时给集中趋势与个体分布。

```python
from cns_style import plot_bardotplot
plot_bardotplot(adata, groupby='celltype', color='COL1A1', save='AE_bardot')
# 柱=均值（±1.96*SEM error bar），点=每样本/每细胞原始值
# color 为基因时按基因名标注单位；多基因循环调用
```

### 3.23 Stacking volcano（堆叠火山图——多条件 DE 并排）

**统一入口**（mpl，ov 无对应函数）：多条件 DE 并排对比——单火山图一次一张，堆叠版可直接比条件间方向/幅度。

```python
from cns_style import plot_stacking_vol
de_dict = {'W1': de_df1, 'W2': de_df2, 'W3': de_df3}   # 每张: gene, log2FC, padj
plot_stacking_vol(de_dict, save='AF_stacking_vol')
# 内部：ov.pl.stacking_vol 优先（列名自动映射），ov 失败走 mpl 兜底
# （每条件一列 mini 火山、共享 y 轴、显著点着色），绝不静默返回
```

### 3.24 UpSet plot（UpSet 图——>3 组交集）

**统一入口**（upsetplot 优先，mpl 兜底）：>3 组交集比 Venn 清晰——交集条形 + 组大小横条。

```python
from cns_style import plot_upset
sets = {'Up_DE': set(de_genes_1), 'Down_DE': set(de_genes_2),
        'Pathway_A': set(pathway_genes)}
plot_upset(sets, top_n=30, save='AG_upset')
# sets={名称: set}；top_n=30 只画前 30 大交集
# 交集点阵左侧组大小条；内部用 upsetplot.UpSet 兜底
```

### 3.25 Venn diagram（Venn 图——≤4 组交集）

**统一入口**（matplotlib_venn 优先，mpl 兜底）：≤4 组交集——>4 组改用 §3.24 UpSet。

```python
from cns_style import plot_venn
plot_venn({'Cluster1': set(markers_1), 'Cluster2': set(markers_2)}, save='AH_venn')
# sets={名称: set}；2/3 组用 matplotlib_venn，4 组用 mpl 圆形兜底
# set_labels 缺省取 key；交叠数字为两集合交集大小
```

### 3.26 Forest plot（森林图——meta-analysis）

**统一入口**（mpl，ov 无对应函数）：meta-analysis 标配——效应量 + 95% CI 横排。

```python
from cns_style import plot_forest
plot_forest(data=meta_df, estimate='effect', lower='ci_low', upper='ci_high',
            label='study', save='AI_forest')
# data: DataFrame 含 effect/ci_low/ci_high/study 列
# 垂直线画在 0（或 OR/RR 时 1）；label 列作为行标签
```

### 3.27 Regression plot（回归散点）

**统一入口**（ov.pl.regression 优先，mpl 兜底）：相关性分析标配——散点 + 拟合线 + CI 带。

```python
from cns_style import plot_regplot
plot_regplot(data=df, x='gene_A_expr', y='gene_B_expr', fit='linear', save='AJ_regplot')
# data: tidy DataFrame；fit='linear'（默认）| 'lowess'（非线性可选）
# 图上标注 r + p（pearson 默认）；off-diagonal 用 regplot 替代 scatter
```

### 3.28 CCC heatmap（通讯热图——liana 结果多模式可视化）

**统一入口**（对齐 ov.pl.ccc_heatmap）：liana 预计算后，CCC 强度的 heatmap/dot/tile 多模式展示。

```python
from cns_style import plot_ccc_heatmap
plot_ccc_heatmap(adata, plot_type='heatmap', save='AK_ccc_heatmap')
# 前置：需先跑 liana（结果存 adata.uns['liana_res']）
# plot_type: 'heatmap'(默认) | 'dot' | 'tile' | 'focused_heatmap'
# 对齐 ov.pl.ccc_heatmap；celltype×celltype 强度矩阵
```

### 3.29 PCA variance ratio（PCA 方差比——QC 标配）

**统一入口**（ov.pl.pca_variance_ratio 优先，mpl 兜底）：QC 标配——看前 n 个 PC 解释方差，决定选多少个 PCs。

```python
from cns_style import plot_pca_variance
plot_pca_variance(adata, n_pcs=30, save='AL_pca_variance')
# 前置：需先跑 sc.pp.pca；n_pcs=30 默认展示前 30 个
# 常用：拐点前保留 PCs；neighbors 用同一 n_pcs
```

### 3.30 HVG scatter（HVG 均值-离散散点——QC 标配）

**统一入口**（mpl，ov 无对应函数）：QC 标配——基因均值 vs 离散度（方差/均值），看 HVG 选择质量。

```python
from cns_style import plot_hvg_scatter
plot_hvg_scatter(adata, save='AM_hvg_scatter')
# 内部：x=log mean，y=log variance（或 dispersion），HVG 着红色
# 常用：可结合 sc.pp.highly_variable_genes 结果着色
```

### 3.31 Radar plot（雷达图——多指标/整合基准方法对比）

**统一入口**（mpl 手绘 polar，ov 无对应函数）：多辐条雷达图——每根辐条按自己的量程归一化（`axis_ranges={轴名:(lo,hi)}`，缺省按各轴数据 min/max），归一后统一映射到 [r_lo, r_hi]；异量纲指标（如 iLISI/cLISI/ASW_batch/ASW_celltype/GraphConn 整合基准对比）可一图比完。

```python
import sys; sys.path.insert(0, 'scripts/')
from cns_style import *
set_cns_style_journal('nature')
import numpy as np

labels = ['iLISI', 'cLISI', 'ASW_batch', 'ASW_celltype', 'GraphConn']
vals = np.array([
    [0.82, 0.74, 0.62, 0.68, 86.2],   # Harmony
    [0.79, 0.77, 0.66, 0.71, 80.1],   # scVI
    [0.35, 0.31, 0.12, 0.52, 93.4],   # 未校正
])
ranges = {'iLISI': (0, 1), 'cLISI': (0, 1), 'ASW_batch': (0, 1),
          'ASW_celltype': (0, 1), 'GraphConn': (0, 100)}   # ⚠️ 异量纲轴各按合理范围
fig, ax = plot_radar(vals, labels, series_names=['Harmony', 'scVI', '未校正'],
                     axis_ranges=ranges)
save_panel(fig, 'integration_radar', fmt='png')
```

**注意**：异量纲指标必须显式传 `axis_ranges`（GraphConn 0-100 与 0-1 混排时缺省归一会压扁前者）；≤3 系列最佳，>4 会糊；spoke 标签已按 |sin(angle)| 加 offset 防挤；辐条 GREY lw=0.4、外环 NEAR_BLACK lw=0.6（grid off 后手绘补回）；图例右外置（铁律 1）。

### 3.32 消融/对比柱——alpha_ramp / focus_ramp 两个食谱

**α 编码消融完整度**（barh）：`alpha_ramp(hex_color, n, lo=0.25, hi=1.0)` → 同一色相 n 个 RGBA，首项最实(hi)→末项最透明(lo)；数据按"完整模型在前、消融越多越靠后"排列后直接 zip。

```python
colors = alpha_ramp('#0F4D92', 6)          # 首项 alpha=1.0（完整模型），逐项变透明
# vals/stds 按同一顺序排列：完整模型在前，消融越多越靠后
bars = ax.barh(range(len(vals)), vals, xerr=stds, color=colors,
               ecolor='#4C566A', capsize=3, error_kw=dict(lw=0.8))
for b, v, s in zip(bars, vals, stds):      # 标签在条外（白底）→ 一律深字
    ax.text(b.get_width() + s + 0.015, b.get_y() + b.get_height() / 2,
            f'{v:.3f}', va='center', fontsize=6, color=NEAR_BLACK)
# ⚠️ is_dark(hex) 只在标签压色块上时用（选白/黑字）；条外白底用白字 = 不可见（真实踩坑）
```

**焦点+渐褪"本方法 vs 基线"**（柱）：`focus_ramp(focus_hex, base_hex, n, lighten_step=0.11)` → `[focus_hex] + (n-1) 个逐步提亮的 base_hex`——焦点饱和、基线可辨识的单色渐褪（比全灰好在基线仍可指认）。

```python
colors = focus_ramp('#0F4D92', '#D4685F', 5)    # 第 0 项=焦点色原样，其余逐步提亮
ax.bar(x, y, color=colors,
       error_kw=dict(elinewidth=0.8, capthick=0.8, capsize=2))
```

> 数值标在 `height+std+2%` 处，fontsize 6（条上白底 → NEAR_BLACK）。

### 3.33 累计/趋势曲线 + 事件标注（mark_events）

**统一入口**（mpl）：`mark_events(ax, x, y, events, dy=0.06, fontsize=7, arrow_lw=0.6, color='#2E3440')` 在曲线 y(x) 上标注事件（给药、发病、模型发布时间点）；`events: dict {x_value: label}`；白色描边光晕文字 + `'-|>'` 箭头（shrinkA=shrinkB=0）；label 中每个 `'*'` 把文字再抬高一个 `dy*(ylim span)`——手工防撞梯。

```python
from cns_style import _lighten_color            # ⚠️ import * 不带下划线名，需具名导入
from matplotlib.colors import to_rgb

light_fill = _lighten_color(MORLANDI[0], 0.6)                # 浅填充
dark_edge = tuple(c * 0.5 for c in to_rgb(MORLANDI[0]))      # 同色相加深描边
ax.fill_between(x, 0, y, color=light_fill, linewidth=0)
ax.plot(x, y, color=dark_edge, lw=1.2)
ax.set_ylim(0, y.max() * 1.45)          # 先定 ylim，mark_events 要读它
mark_events(ax, x, y, {3: '处理开始', 8: '模型A*', 16: '模型B**'})  # '*'越多抬越高
```

> **图案小贴士（hatch 双序列区分——黑白打印/色盲友好）**：`ax.fill_between(..., hatch='//', edgecolor='black')` 后叠一层同形状 `facecolor='none', edgecolor='white', linewidth=2`，白描边视觉擦除 hatch 边框（源自 figures4papers）。

### 3.34 Raincloud（云雨图——半小提琴+箱线+雨点三合一）

**统一入口**（mpl 直绘，ov 无对应函数）：一组一列，左半小提琴（分布形状）+ 白底箱线（分位数）+ 右侧雨点（每点=一观测/一样本）——分组分布对比的高信息密度形态。单细胞数据**必须先聚合到样本级**（每点=一供体中位数）再画，禁止细胞级混样当重复。

```python
from cns_style import plot_raincloud
# 样本级聚合：每 donor 每组中位数（每 donor ≥10 细胞）
df = (obs.groupby(['donor', 'cell_state'])['score']
         .median().reset_index())
plot_raincloud(df, x='cell_state', y='score',
               order=['vCM1', 'vCM2', 'vCM4'],
               colors={'vCM1': '#b8bcc2', 'vCM2': '#b8bcc2', 'vCM4': '#C0392B'},
               test='mwu', save='AH_raincloud')
# data: tidy DataFrame（x=分组列, y=数值列）；AnnData 自动转 tidy
# 左琴仅 n≥5（kde_min_n）组绘制，小组自动退化为箱线+雨点；kde_bw 控制平滑度
# test='mwu' → 各组 vs 第一组（ref=... 可换参照）Mann-Whitney U 错位括号，标星+p 值
# show_n=True x 刻度附 (n=..)；highlight 组用红/其余灰是 CNS 常用强调法
# 源自 mHeart 外部验证 149f/149g 实战（EV Fig 1A/1C、2A/2B 同款）
```

### 3.35 Slope chart（斜率图——组成 movers / 跨条件变化）

**统一入口**（mpl 直绘）：每实体一条跨 2-4 个时间点/条件的折线，**无图例**，端点直接标注（带 Δ）；多轮人工验证的最终形态（fetal_heart fig1d2/fig2k1，面条图+图例被淘汰）。

```python
from cns_style import plot_slope
# ① wide：index=类型, columns=时间点（值=占比/得分）② tidy+entity/group/value 三列
plot_slope(wide, top_n=8, order=['13w', '19w', '24w'],
           emphasize=['VIC'], colors={'VIC': '#B5432F'},
           label_deltas=True, save='D2_movers')
# top_n 按距行均值最大偏差选（净变化与中途峰都抓得到）
# emphasize 实体加粗 2.6 置顶，其余灰 1.6——层级一眼可读
# 端点标签 direct_label 像素防撞（gap_pt=11），右端自动附 +Δ
# 源自 fetal_heart draw_fig1d2_movers / draw_fig2k1_trajectories 实战
```

### 3.36 Diverging lollipop（发散棒棒糖——模块/TF-性状相关 + 置换零带）

**统一入口**（mpl 直绘）：每实体一行，stem 从 0 到 r（正红负蓝），实心大点=主统计量、空心小点=第二统计量（Pearson 实心 + Spearman 空心是 WGCNA/pyscenic 系标准形态）。

```python
from cns_style import plot_lollipop
# null 带：对相关矩阵列做 2000 次置换取中位数的 2.5-97.5% 分位
null = np.percentile([np.median(np.diag(R[:, rng.permutation(R.shape[1])]))
                      for _ in range(2000)], [2.5, 97.5])
plot_lollipop(trait_corr, label_col='module', value_col='pearson',
              value2_col='spearman', pval_col='p', tag_col='ORA_identity',
              ref_line=0.8, null_band=null, save='E1_lollipop')
# pval_col → 值旁 *** 星；tag_col → 右缘身份标签（ORA/功能注释列）
# ref_line=0.8 等虚参考；null_band 灰底+斜体 'random matching' 注释
# 跨物种保守性/方法对比：value=r，null_band=置换零带——成对条形可换本入口
# 源自 fetal_heart draw_fig2e1_hdwgcna / draw_fig1g_v4_bars 实战
```

### 3.37 QC bar cards（样本×指标条形卡片——QC 总览标配）

**统一入口**（mpl 直绘）：行=样本、列=指标，首列样本名+协变量渐变色块（如供体 GA），每指标横条+右端数值直标+列顶范围注释；全轴隐藏的"表格化条形图"，3 秒可读。

```python
from cns_style import plot_qc_cards
metrics = obs.groupby('donor').agg(cells='n_cells', median_genes='n_genes',
                                   mito_pct='pct_mt')          # index=donor
ga = donors.set_index('donor')['ga_weeks']                     # 协变量
plot_qc_cards(metrics, covariate=ga, covariate_label='GA (w)',
              formats={'mito_pct': '{:.1f}'}, highlight=['D07'],
              save='I1_qc_cards')
# 行默认按协变量升序（最小在上）；highlight 样本整行红底纹
# 源自 fetal_heart draw_fig1i1_qc 实战（15 供体×3 指标主图面板）
```

### 3.38 Trend grid（样本级小倍数趋势——供体验证标准形态）

**统一入口**（mpl 直绘）：每模块/基因/通路一面板，样本级散点+拟合线；点径∝每样本细胞数（权重可视化）；标题内嵌 Spearman ρ+显著性星。**小倍数替代面条图**——原始数据与统计量一体呈现。

```python
from cns_style import plot_trend_grid
df = usage_long   # 列: program / donor / ga / score / n_cells
plot_trend_grid(df, x='ga', y='score', by='program', size_col='n_cells',
                ncols=4, fit='lowess', highlight=['M1'],
                shared_ylim=(-2.9, 2.9), save='E1_usage_trends')
# fit='ols'|'lowess'|None；highlight 实体红描边+红标题
# 每面板标题自带统计（现场算 ρ，或 stat_col/pval_col 传预计算列）
# 源自 fetal_heart draw_fig2e_hdwgcna_merged / draw_fig2i_temporal 实战
```

### 3.39 Spatial zoom（IF 风格空间放大图——局部信号 + inset 定位）

**统一入口**（mpl 直绘）：高信号区自动取框（top 分位掩码→闭运算→最大连通域+buffer），窗内按值着色（低值先画不遮高值）、窗外浅灰 context；inset 全片缩略图红框定位；点径按物理密度恒定缩放；比例尺自适应。

```python
from cns_style import plot_spatial_zoom
plot_spatial_zoom(adata_sp, color='vic_score', threshold_pct=90,
                  vmax='p98', unit_per_um=0.5, save='C_vic_zoom')
# color: obs 列或数组；spot_units=每点物理宽度（数据单位）→ 放大倍率变、观感不变
# vmax 跨图请显式传数（多时间点/多样本可比）；unit_per_um 换算比例尺
# 源自 fetal_heart draw_fig2c_vic_zoom / draw_fig2j1_maps 实战
```

### 3.40 工具层四件套（stamp_panel / assert_no_text_overlap / direct_label / layout_labels）

```python
from cns_style import (stamp_panel, assert_no_text_overlap,
                       direct_label, layout_labels, polish_axes)
stamp_panel(fig, 'a', 'Composition movers across development',
            'per-donor medians; n=15; MWU')     # 字母+标题+方法学灰副标题
polish_axes(ax, variant='bar', grid_axis='x')   # barh 风坐标（灰底脊+浅网格）
direct_label(ax, ends, [f'{n} {d:+.1f}' ...])    # 端点标签像素级 stagger
layout_labels(fig, ax, ax.texts)                 # on-plot 标签 bbox 斥力排开
assert_no_text_overlap(fig)                      # 保存前机械验收门（raise）
# stamp/assert 是 fetal_heart 62+ 脚本的固定开头+收尾组合（2026-09 回灌）
```

### 3.41 Sankey 状态转换（命运流/转变矩阵 alluvial）

**统一入口**（mpl 直绘）：转移矩阵 → 左右节点 + 贝塞尔 ribbon。适用：PAGA/CellRank 转移概率、最优传输转变矩阵、治疗前→后 alluvial、命运概率流。源自 15 领域调研中频图型（肾/心/衰老/发育 ~15-25% 论文）。深度 ≥3 阶段拆多个两阶段面板（CNS 惯例）。

```python
from cns_style import plot_sankey
flows = pd.DataFrame({          # 转移矩阵：index=source, columns=target
    'Quiescent': {'Quiescent': 5, 'Activated': 30, 'Matrix': 3},
    'Cycling':   {'Quiescent': 1, 'Activated': 12, 'Matrix': 6},
}).T
plot_sankey(flows, min_flow=0.01, save='AI_sankey')
# min_flow：低于该比例的 ribbon 不画（去毛刺）；节点默认按流量降序，
# order_top/order_bottom 可覆盖；ribbon 按 source 着色（MORLANDI_EXTENDED）
```

### 3.42 CNV 基因组热图（inferCNV 式）

**统一入口**（mpl 直绘）：行=细胞（先按分组排序再传入），列=基因组位置序基因；染色体白线分隔+顶注染色体号；左侧可选分组色条。DIVERGING_CMAP（0=白，红=扩增，蓝=缺失，与 inferCNV 惯例一致）。肿瘤领域 ~40% 论文、血液克隆演化标配。

```python
from cns_style import plot_cnv_heatmap
# cnv: DataFrame(index=细胞, columns=基因, 值=inferCNV/copyKAT expr 或 log-ratio)
# chrom: 与 columns 对齐的染色体标签（如 adata.var['chrom']）
# groups: 与 index 对齐的分组（恶性/非恶性、克隆、样本）→ 左侧色条
plot_cnv_heatmap(cnv_df, chrom=adata.var['chrom'], groups=cell_groups,
                 vmin=-1.5, vmax=1.5, save='AJ_cnv_heatmap')
```

### 3.43 轴向/距离梯度曲线（连续组织轴通用图型）

**统一入口**（mpl 直绘）：信号沿连续轴（µm 距离/zone 位置/皮层深度/伪时间）的梯度曲线——肝 zonation、皮质-髓质肾轴、病理-分子距离梯度（Aβ/pTau）、肿瘤边界带、母胎界面距离分箱的**跨领域通用形态**。每信号：散点（超 4000 点自动降密度）+ LOWESS 曲线（statsmodels 优先，滑窗中位兜底）+ p25-p75 带；x=0 画解剖标志虚线。

```python
from cns_style import plot_axis_gradient
# data: tidy DataFrame；x=轴坐标，y=信号值，hue=信号名
plot_axis_gradient(zonation_df, x='cv_distance_um', y='expr', hue='gene',
                   norm='each',               # 'each'=每信号 min-max（多基因比形状）
                   xlabel='Distance from central vein (µm)',
                   landmark_label='central vein', save='AK_axis_gradient')
```

### 3.44 克隆扩增追踪（TCR/BCR/肿瘤克隆）

**统一入口**（mpl 直绘）：免疫/血液/感染的"克隆-表型-空间"三连图之一。`mode='composition'`：分组堆叠柱（每组细胞按克隆大小分类 singleton/small/medium/large，bins 可调）——展示"哪群在克隆性扩增"；`mode='track'`：top_n 大克隆跨组折线（时间点/组织演化，端点 direct_label 防撞直标）。

```python
from cns_style import plot_clone_expansion
# clone_df: 每行=克隆×分组记录（clone_col/group_col/size）；传每细胞一行也可（自动计数）
plot_clone_expansion(tcr_df, clone_col='clone_id', group_col='celltype',
                     mode='composition', save='AL_clone_comp')   # 大小分类堆叠
plot_clone_expansion(tcr_df, clone_col='clone_id', group_col='timepoint',
                     mode='track', top_n=6, save='AM_clone_track')  # top 克隆演化
```

### 3.45 低频领域特色图型指引（降优先度——不建代码模板）

> 源自 15 领域调研：<10% 论文出现的特色图型。**仅当领域卡（figure_templates.md §3）明确列出且用户点名时才做**；默认用中高频图型替代（克隆树→plot_sankey；oncoprint→plot_heatmap+注释条）。

| 低频图型 | 外部工具/替代 |
|---|---|
| fishplot / 克隆演化树 | R `fishplot` / `cloneevolve`；简化用 plot_sankey |
| oncoprint | R ComplexHeatmap `oncoPrint()`；简化用 plot_heatmap+分组注释条 |
| 克隆 Voronoi 空间图 | scipy `Voronoi` + ax.add_patch（肿瘤/肠克隆空间） |
| 3D 器官/胚胎重建 | napari / BioIO / 3D viewer；静态图导出 |
| 4D mapping / 最优传输 | moscot（发育时空对齐） |
| 空间衰老时钟 | 自研回归+GNN 扰动（SpatialSmooth 思路） |
| scWGS 突变签名 | SigProfiler / Signatures；与表达偶联画散点 |
| FICTURE 像素级空间图 | ficture CLI（原厂 pipeline 出图） |
| 宿主-病原共检测 | 平台原厂 pipeline；物种-面积曲线用 plot_regplot |
| dMRI-空转配准 | ANTs 配准 + 空间散点 |

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

> 统一入口为 plot_de_scatter（见 §3.6 与 §0 速查卡）；下方手动实现供需要精细控制时参考。

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