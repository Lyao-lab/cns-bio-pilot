# Plotting Reference — 发表级绘图代码速查

> 本文件是 figure-production skill 的**代码层**：每种图型的精确参数 + 可跑模板。
> 配套：流程查 `skills/visualization/figure-production/SKILL.md`；原则/视觉规格查 `figure_guide.md`；外部参考查 `omicverse_skills_examples.md`。
> 所有模板假设已执行顶部 §1 的全局开头（import + set_cns_style_journal），且 `adata`/数据已就绪。
> 铁律：每张图统一用 `save_panel(fig, name)` 收尾（内部强制 finalize_figure → 建目录 → savefig），**不再手写 savefig**。

## 0. 速查卡（图型 → 一行调用 → 必须函数）

| 要画什么 | 首选 API | 必须调的 cns_style 函数 | 关键参数 |
|---|---|---|---|
| UMAP / tSNE | `ov.pl.embedding(adata, color=..., ax=ax)` | `assert_anndata_keys` + `cohort_params` + `add_cluster_labels` + `clean_umap_axes` | size/alpha 取 `cohort_params(n)`；tSNE 换 `basis='X_tsne'` |
| Volcano | `ov.pl.volcano(de, pval_name='padj', fc_name='log2FC')` | `volcano_colors` + `polish_axes` | figsize=`recipe_figsize('volcano')`；top10 标注 italic |
| Dotplot | `ov.pl.dotplot(adata, var_names=..., groupby=...)` | `save_panel` | `standard_scale='var'`；`dendrogram=False` |
| Violin/Box | `ov.pl.violin(adata, keys=..., groupby=...)` | `save_panel` | `violin_alpha=0.8`；spine `#b4aea9`；wilcox 自动星号 |
| Heatmap | `sc.pl.heatmap` / `sns.clustermap` | `add_elegant_colorbar` | Z-score/row；`vmin=-2,vmax=2`；EXPR_CMAP |
| Spatial | `sq.pl.spatial_scatter` / `ov.pl.plot_spatial` | `add_scale_bar`（必须）+ `add_elegant_colorbar` | `alpha_img=1.0`；colorbar 横置 |
| Bar（比例） | matplotlib | `polish_axes` | Y 从 0；95% CI error bars；per-sample dots |
| 富集条形 | matplotlib | `polish_axes` | barh；`-log10(FDR)` 降序；条右标 gene count |
| L-R Bubble | matplotlib | `add_elegant_colorbar` + `polish_axes` | size=`-log10(p)`；color=mean expr |
| Feature 矩阵 | `ov.pl.embedding(adata, color=[g1,...], ncols=3)` | `clean_umap_axes` | 共享 vmin/vmax=99th pct |
| PAGA | `sc.pl.paga(adata, colors=..., ax=ax)` | `polish_axes` | `threshold=0.05`；可 `pos=UMAP` 叠加 |
| Chord / CCC | `ov.pl.CellChatViz` → `netVisual_chord_cell` | `save_panel` | ≤8 cell types；lw∝weight |
| Pseudotime | matplotlib LOESS | `polish_axes` | lw=1.2；CI 带 alpha=0.15 |
| cellproportion | `ov.pl.cellproportion` / matplotlib 堆叠 | `palette_from_names` + `polish_axes` | stacked；MORLANDI |

## 1. 全局开头（每个脚本第一行）

```python
import sys; sys.path.insert(0, 'scripts/')
from cns_style import *
import matplotlib.pyplot as plt
import numpy as np
set_cns_style_journal('nature')   # 'nature'|'science'|'cell'|'generic'

# 绘图前校验（新推荐，避免运行到一半 KeyError）
# assert_anndata_keys(adata, obs_cols=['celltype'], obsm_keys=['X_umap'])
```

自动设好：Morlandi 配色 / Arial 字体 / modular scale 字号 (7/8/10/12/14) / L-frame axes / outward ticks / 期刊 DPI / PDF 输出。下面所有模板都假设这 6 行已执行。

## 2. 核心图型模板（已有，从 figure_guide 抽取并优化）

### 2.1 UMAP/tSNE

**ov 路径（优先）**。要点：`cohort_params(n_cells)` 一次联动 point_size / alpha / figsize（大 cohort 不糊团、不小到看不见）；`assert_anndata_keys` 先校验再画；on-plot labels 代替 legend（铁律 1 例外）；无轴 + 圆形留白。

```python
assert_anndata_keys(adata, obs_cols=['celltype'], obsm_keys=['X_umap'])
p = cohort_params(adata.n_obs)                       # {point_size, alpha, figsize}
fig, ax = plt.subplots(figsize=p['figsize'])
ov.pl.embedding(adata, basis='X_umap', color='celltype',
                size=p['point_size'], alpha=p['alpha'],
                ax=ax, show=False, legend_loc=None)  # on-plot labels 代替图例
add_cluster_labels(ax, adata, basis='umap', groupby='celltype')  # 白光晕
clean_umap_axes(ax)                                  # Nature 无轴
optical_margin(ax, 0.12)                             # 圆形数据留白
save_panel(fig, 'A_umap')                            # finalize → panels/A_umap.pdf
```

### 2.2 Volcano

**ov 路径（优先）**：列名必须是 `log2FC` / `padj`（可改名对齐）；`annotate_top=10` 自动标注 top 10 基因（italic）。ov 版自建 figure，用 `plt.gcf()` 取回后统一 `save_panel`。

```python
de = pd.read_csv('de_results.csv')   # 列: gene, log2FC, padj
ov.pl.volcano(de, pval_name='padj', fc_name='log2FC',
              sig_pvalue=0.05, sig_fc=1.0, annotate_top=10)
fig = plt.gcf()
fig.set_size_inches(*recipe_figsize('volcano'))      # (4, 3.5) @generic
save_panel(fig, 'B_volcano')
```

**matplotlib 路径（精细控制）**：用 `volcano_colors()` 对齐 omicverse 默认色（Up=`#e25d5d`, Down=`#7388c1`, NS=`#d7d7d7`）。

```python
colors = volcano_colors()
up = (de['padj'] < 0.05) & (de['log2FC'] >  1)
dn = (de['padj'] < 0.05) & (de['log2FC'] < -1)
ns = ~(up | dn)
fig, ax = plt.subplots(figsize=recipe_figsize('volcano'))
ax.scatter(de.loc[ns, 'log2FC'], -np.log10(de.loc[ns, 'padj']),
           s=4, alpha=colors['ns_alpha'], color=colors['ns'], edgecolor='none', rasterized=True)
ax.scatter(de.loc[up, 'log2FC'], -np.log10(de.loc[up, 'padj']), s=6, color=colors['up'], edgecolor='none')
ax.scatter(de.loc[dn, 'log2FC'], -np.log10(de.loc[dn, 'padj']), s=6, color=colors['down'], edgecolor='none')
ax.axhline(-np.log10(0.05), color=colors['threshold'], ls='--', lw=0.5, alpha=0.3)
for v in (1, -1):
    ax.axvline(v, color=colors['threshold'], ls='--', lw=0.5, alpha=0.3)
for _, r in de.loc[up].nlargest(10, 'log2FC').iterrows():
    ax.annotate(r['gene'], xy=(r['log2FC'], -np.log10(r['padj'])), **gene_annotation_kwargs())
ax.set_xlabel(r'log$_2$(Fold Change)'); ax.set_ylabel(r'$-$log$_{10}$(adjusted P)')
polish_axes(ax)
save_panel(fig, 'B_volcano_manual')
```

### 2.3 Dotplot

**ov 路径（优先）**：`standard_scale='var'` 行标准化；`dendrogram=False`（列按生物学排序，不画聚类树）。cmap 走 ov 默认即可，如需统一量纲用 `num_categories` 控制。

```python
ov.pl.dotplot(adata, var_names=genes, groupby='celltype',
              standard_scale='var', dendrogram=False)
fig = plt.gcf()
save_panel(fig, 'C_dotplot')
```

### 2.4 Violin/Box

**ov 路径（优先）**：交替背景色带 + 暖灰 spine + wilcox 自动星号（`statistical_tests='wilcox'`）。

```python
ov.pl.violin(adata, keys=['CD3D', 'MS4A1', 'LYZ', 'CD68'], groupby='celltype',
             stripplot=True, jitter=True, size=1, jitter_alpha=0.4,
             violin_alpha=0.8, alternating_background=True,
             spine_color='#b4aea9', grid_lines=True,
             statistical_tests='wilcox', show=False)
fig = plt.gcf()
save_panel(fig, 'D_violin')
```

**matplotlib 路径（精细控制）**：模拟 omicverse 交替背景 + 极小点；用 `palette_from_names` 示范命名色板（omicverse 可用则精确色，否则近似 fallback，脚本不崩）。

```python
from matplotlib.colors import to_rgb
def _lighten(hex_color, amount=0.8):
    r, g, b = to_rgb(hex_color)
    return (r + (1-r)*amount, g + (1-g)*amount, b + (1-b)*amount)

clusters = adata.obs['celltype'].cat.categories
ct_colors = palette_from_names(clusters[:6], ['霁蓝', '藤黄', '朱砂', '青矾绿', '胭脂紫', '石英粉红'])
genes = ['CD3D', 'MS4A1', 'LYZ']
fig, axes = plt.subplots(len(genes), 1,
    figsize=(len(clusters)*0.6+1, len(genes)*2.8), sharex=True)
for row, g in enumerate(genes):
    ax = axes[row] if len(genes) > 1 else axes
    data_per_cl = [adata[adata.obs['celltype']==cl, g].X.toarray().ravel()
                   for cl in clusters]
    for i, cl in enumerate(clusters):                       # 交替背景带
        ax.axvspan(i-0.5, i+0.5, color=_lighten(ct_colors[cl], 0.85), alpha=0.5, zorder=0)
    parts = ax.violinplot(data_per_cl, positions=range(len(clusters)),
                          showmedians=False, showextrema=False)
    for i, pc in enumerate(parts['bodies']):
        c = ct_colors[clusters[i]]; pc.set_facecolor(c); pc.set_alpha(0.8)
        pc.set_edgecolor(c); pc.set_linewidth(1)
    for i, d in enumerate(data_per_cl):                     # strip: s=1, alpha=0.4
        jit = np.random.uniform(-0.15, 0.15, len(d))
        ax.scatter(np.full(len(d), i)+jit, d, s=1, alpha=0.4, color=ct_colors[clusters[i]],
                   edgecolor='none', rasterized=True, zorder=3)
    ax.yaxis.grid(True, alpha=0.3, lw=0.5, color='#b4aea9', zorder=0); ax.set_axisbelow(True)
    for sp in ax.spines.values(): sp.set_color('#b4aea9'); sp.set_linewidth(0.8)
    ax.set_ylabel(g, fontstyle='italic', fontsize=10, labelpad=10)
axes[-1].set_xticks(range(len(clusters)))
axes[-1].set_xticklabels(clusters, fontsize=7, rotation=45 if len(clusters) > 12 else 0)
save_panel(fig, 'D_violin_manual')
```

### 2.5 Heatmap

**matplotlib/sns 路径（含列注释条）**：Z-score per row；`vmin=-2, vmax=2`；EXPR_CMAP；列注释条来自 manifest/cmap；`col_cluster=False` 按生物学排序。

```python
import seaborn as sns
expr = adata[:, genes].to_df(); expr['ct'] = adata.obs['celltype'].values
mean_expr = expr.groupby('ct').mean().T                  # 行=基因, 列=celltype
expr_z = mean_expr.apply(lambda r: (r - r.mean()) / r.std(), axis=1)
col_ann = pd.DataFrame({'Condition': [cond_of_ct[ct] for ct in mean_expr.columns]},
                       index=mean_expr.columns)
g = sns.clustermap(expr_z, cmap=EXPR_CMAP, vmin=-2, vmax=2,
                   col_colors=col_ann, col_cluster=False, row_cluster=True,
                   figsize=recipe_figsize('heatmap', n_x=expr_z.shape[1], n_y=expr_z.shape[0]),
                   linewidths=0, cbar_pos=(0.02, 0.8, 0.03, 0.15))
save_panel(g.fig, 'E_heatmap_annotated')
```

**scanpy 路径（快速）**：

```python
sc.pl.heatmap(adata, var_names=genes, groupby='celltype', cmap=EXPR_CMAP,
              vmin=-2, vmax=2, swap_axes=True, show=False)
fig = plt.gcf()
save_panel(fig, 'E_heatmap_sc')
```

### 2.6 Spatial

**ov/squidpy 路径**：组织 `alpha_img=1.0`（不透明）；spots `alpha=0.85`；**scale bar 必须有**（缺它 = 审稿人一眼扣分）；colorbar 横置。

```python
import squidpy as sq
fig, ax = plt.subplots(figsize=recipe_figsize('spatial'))
sq.pl.spatial_scatter(adata_sp, color=gene, ax=ax, size=1.2, cmap=EXPR_CMAP,
                      vmin=0, alpha_img=1.0, alpha=0.85, title='', show=False)
add_scale_bar(ax, length_um=200, px_per_um=0.5)          # 必须；长度取 100/200/500 中最接近图宽 1/5 者
add_elegant_colorbar(ax.collections[0], ax, label=gene, orientation='horizontal')
clean_umap_axes(ax, xlabel='', ylabel='')
save_panel(fig, 'F_spatial')
```

### 2.7 Bar（比例）

**matplotlib 路径**：Y 从 0；95% CI error bars（capsize=3, lw=1）；per-sample dots overlay（s=15, alpha=0.7）。

```python
props = (adata.obs.groupby(['sample', 'celltype']).size()
         .unstack(fill_value=0).apply(lambda r: r / r.sum(), axis=1))  # 行=样本, 列=celltype
fig, ax = plt.subplots(figsize=recipe_figsize('bar', n_x=len(props.columns)))
for i, ct in enumerate(props.columns):
    mean, sem = props[ct].mean(), props[ct].sem()
    ax.bar(i, mean, yerr=1.96*sem, capsize=3, width=0.6,
           color=MORLANDI[i % len(MORLANDI)], edgecolor='white', linewidth=0.5,
           label=ct, error_kw=dict(lw=1, ecolor=NEAR_BLACK))
    ax.scatter(np.full(len(props), i), props[ct], s=15, alpha=0.7,
               color=NEAR_BLACK, edgecolor='none', zorder=3)
ax.set_xticks(range(len(props.columns)))
ax.set_xticklabels(props.columns, rotation=30, ha='right')
ax.set_ylabel('Proportion'); ax.set_ylim(0, ax.get_ylim()[1])
ax.legend(bbox_to_anchor=(1.02, 0.5), loc='center left', frameon=False)
polish_axes(ax)
save_panel(fig, 'G_proportion')
```

### 2.8 富集条形图（GO/KEGG）

**matplotlib 路径**：水平 barh；`-log10(FDR)` 降序；条右标 gene count；通路名 ≤40 字符截断；`polish_axes` 无 grid。

```python
terms = enr.nsmallest(15, 'FDR')          # enr: pandas DataFrame, 列 Term/FDR/Gene_count
fig, ax = plt.subplots(figsize=(4.5, 0.35*len(terms) + 1))
y_pos = range(len(terms))
bars = ax.barh(y_pos, -np.log10(terms['FDR']), color='#BF616A', height=0.6, edgecolor='none')
ax.set_yticks(y_pos)
ax.set_yticklabels([t[:40] for t in terms['Term']], fontsize=7)
ax.set_xlabel(r'$-$log$_{10}$(FDR)', labelpad=10)
ax.invert_yaxis()                          # top = most significant
for b, n in zip(bars, terms['Gene_count']):
    ax.text(b.get_width()+0.1, b.get_y()+b.get_height()/2, str(n),
            va='center', fontsize=6, color=GREY)
polish_axes(ax, subtle_grid=False)
save_panel(fig, 'H_enrichment')
```

### 2.9 L-R Bubble

**matplotlib 路径**：x = cell-type pair (sender→receiver)；y = pathway；size=`-log10(p)` 映射 `s∈[20,200]`；color=mean expr（EXPR_CMAP）；≤10 pairs × ≤15 pathways。

```python
fig, ax = plt.subplots(figsize=(max(5, n_pairs*0.6), max(4, n_pathways*0.35)))
scatter = ax.scatter(x_idx, y_idx, s=sizes, c=mean_expr, cmap=EXPR_CMAP,
                     edgecolor='#2E3440', linewidth=0.3, alpha=0.85)
ax.set_xticks(x_idx); ax.set_xticklabels(pair_labels, rotation=45, ha='right', fontsize=6)
ax.set_yticks(y_idx); ax.set_yticklabels(pathway_names, fontsize=7)
add_elegant_colorbar(scatter, ax, label='Mean expression')
polish_axes(ax, subtle_grid=False)
save_panel(fig, 'I_lr_bubble')
```

### 2.10 Feature Plot 矩阵（多基因 UMAP）

**ov 路径（优先）**：`color=[g1, g2, ...]` + `ncols=3`；所有 panel 共享 `vmin=0, vmax=99th percentile`（跨基因可比）；每 panel `clean_umap_axes`。

```python
expr_mat = adata[:, genes].X
if hasattr(expr_mat, 'toarray'):
    expr_mat = expr_mat.toarray()
p99 = np.percentile(expr_mat, 99)
axs = ov.pl.embedding(adata, basis='X_umap', color=genes, ncols=3,
                      vmin=0, vmax=p99, show=False)   # 多 color 返回 axes 列表
axs = np.atleast_1d(axs).ravel()
for a in axs:
    clean_umap_axes(a)
fig = plt.gcf()
save_panel(fig, 'J_feature_matrix')
```

## 3. 补充图型模板（当前缺失，重点新增）

### 3.1 PAGA（轨迹抽象图）

**scanpy 路径**。前置必须算 PAGA 拓扑：`sc.tl.paga(adata, groups='leiden')`（结果存 `adata.uns['paga']`）。注意 scanpy 参数名是 `colors`（**不是** `color`）。

```python
sc.tl.paga(adata, groups='leiden')        # 前置：一次，基于 connectivities

# 路径 A — 独立 PAGA 拓扑图
assert_anndata_keys(adata, obs_cols=['leiden'], obsm_keys=['X_umap'])
fig, ax = plt.subplots(figsize=recipe_figsize('paga'))   # (3.5, 3.0) @generic
sc.pl.paga(adata, colors='leiden', ax=ax, show=False, threshold=0.05)
polish_axes(ax)
save_panel(fig, 'K_paga')

# 路径 B — 叠加到 UMAP（PAGA 连线 + 散点，推荐展示用）
fig, ax = plt.subplots(figsize=recipe_figsize('umap'))
ov.pl.embedding(adata, basis='X_umap', color='leiden', size=3, alpha=0.5,
                ax=ax, show=False, legend_loc=None)
sc.pl.paga(adata, colors='leiden', pos=adata.obsm['X_umap'], ax=ax,
           show=False, threshold=0.05, edge_width_scale=0.5)
clean_umap_axes(ax)
save_panel(fig, 'K_paga_umap')
```

### 3.2 Chord / CCC（细胞通讯弦图）

要点：≤8 cell types（再多糊成球）；边颜色 = source 色、alpha=0.5；lw ∝ 通讯强度。

**ov 路径 A（推荐，需 omicverse + CellChat 结果）**：

```python
import omicverse as ov
viz = ov.pl.CellChatViz(adata_cpdb, palette=None)     # adata_cpdb: CellChat/cellphonedb 结果
# 下游绘图方法随 ov 版本而异，常见为 netVisual_chord_cell / netVisual_bubble_marsilea：
# fig = viz.netVisual_chord_cell(...)   —— 签名以实际 ov 版本为准
# bubble = viz.netVisual_bubble_marsilea(...)
```

**matplotlib-networkx 路径 B（兜底，可直接跑）**：circular layout 下节点间连线即弦（chord），无需额外贝塞尔。

```python
import networkx as nx
comm = pd.read_csv('lr_interactions.csv')   # 列: source, target, weight
weight = comm.pivot_table(index='source', columns='target', values='weight',
                          aggfunc='sum').fillna(0)
G = nx.from_pandas_adjacency(weight)
nodes = list(G.nodes)[:8]                    # 只画 ≤8 个 cell types
G = G.subgraph(nodes)
palette = {n: MORLANDI[i % len(MORLANDI)] for i, n in enumerate(nodes)}

fig, ax = plt.subplots(figsize=recipe_figsize('chord'))   # (5, 5) 正方形
pos = nx.circular_layout(G)
for n in nodes:                              # 节点
    x, y = pos[n]
    ax.scatter(x, y, s=800, color=palette[n], edgecolor='white', linewidth=1.5, zorder=5)
    ax.text(x, y, n, ha='center', va='center', fontsize=7, color='white', zorder=6)
maxw = max((d['weight'] for _, _, d in G.edges(data=True)), default=1)
for u, v, d in G.edges(data=True):           # 弦：source-colored, alpha=0.5, lw∝weight
    w = d.get('weight', 0)
    if w > 0:
        x1, y1 = pos[u]; x2, y2 = pos[v]
        ax.plot([x1, x2], [y1, y2], color=palette[u], alpha=0.5,
                lw=0.5 + 3*w/maxw, solid_capstyle='round', zorder=2)
ax.set_aspect('equal'); ax.axis('off')
save_panel(fig, 'L_chord')
```

### 3.3 Pseudotime gene-along-trajectory

**matplotlib 路径**：每基因一行 subplot；raw scatter(s=3, alpha=0.3) + LOESS 平滑线 lw=1.2 + 95% CI 带 alpha=0.15；statsmodels 可用则用之，否则 numpy polyfit(deg=3) 兜底（try import，不崩）。

```python
try:
    import statsmodels.api as sm
    HAS_SM = True
except ImportError:
    HAS_SM = False

def loess_ci(x, y, frac=0.3):
    """LOESS 平滑 + 95% CI 带。statsmodels 优先，numpy polyfit 兜底。"""
    x = np.asarray(x); y = np.asarray(y)
    order = np.argsort(x); x, y = x[order], y[order]
    if HAS_SM:
        yhat = sm.nonparametric.lowess(y, x, frac=frac, it=1, return_sorted=True)[:, 1]
    else:
        yhat = np.polyval(np.polyfit(x, y, 3), x)
    resid = y - yhat
    se = np.sqrt(np.convolve(resid**2, np.ones(50)/50, mode='same'))
    return x, yhat, 1.96 * se

genes = ['Gata4', 'Tbx5', 'Nppa']
fig, axes = plt.subplots(len(genes), 1, figsize=(4.5, 2.2*len(genes)), sharex=True)
for row, g in enumerate(genes):
    ax = axes[row]
    x = adata.obs['pseudotime'].values
    y = adata[:, g].X.toarray().ravel()
    ax.scatter(x, y, s=3, alpha=0.3, color=GREY, edgecolor='none', rasterized=True)
    xs, yh, band = loess_ci(x, y)
    ax.plot(xs, yh, lw=1.2, color='#BF616A')
    ax.fill_between(xs, yh - band, yh + band, alpha=0.15, color='#BF616A', lw=0)
    ax.set_ylabel(g, fontstyle='italic', fontsize=8, labelpad=6)
    polish_axes(ax)
axes[-1].set_xlabel('Pseudotime')
save_panel(fig, 'M_pseudotime')
```

### 3.4 tSNE 专属

**ov 路径（优先）**：参数同 UMAP，差别只有 `basis='X_tsne'` + 轴标签 `TSNE1/TSNE2` + 前置 `sc.tl.tsne`。figsize 同 UMAP 正方形（`cohort_params` 联动）。

```python
sc.tl.tsne(adata, n_pcs=30)                 # 前置：tSNE 计算（慢，一次即可）

assert_anndata_keys(adata, obs_cols=['celltype'], obsm_keys=['X_tsne'])
p = cohort_params(adata.n_obs)
fig, ax = plt.subplots(figsize=p['figsize'])
ov.pl.embedding(adata, basis='X_tsne', color='celltype',
                size=p['point_size'], alpha=p['alpha'],
                ax=ax, show=False, legend_loc=None)
add_cluster_labels(ax, adata, basis='tsne', groupby='celltype')
clean_umap_axes(ax, xlabel='TSNE1', ylabel='TSNE2')
optical_margin(ax, 0.12)
save_panel(fig, 'A_tsne')
```

### 3.5 cellproportion（细胞比例堆叠柱）

**ov 路径（一行）**：签名以实际 ov 版本为准，示例为常见用法。

```python
ov.pl.cellproportion(adata, groupby='condition', ...)   # 签名以实际 ov 版本为准
fig = plt.gcf()
save_panel(fig, 'N_cellproportion_ov')
```

**matplotlib 路径（手动，可直接跑）**：分组 × celltype 堆叠比例柱；用 `palette_from_names` 命名色板，超出部分灰掉（5+1 纪律）。

```python
assert_anndata_keys(adata, obs_cols=['condition', 'celltype'])
props = (adata.obs.groupby('condition').apply(
    lambda df: df['celltype'].value_counts(normalize=True))
    .unstack(fill_value=0))                   # 行=condition, 列=celltype
ct_colors = palette_from_names(props.columns[:6], ['霁蓝', '藤黄', '朱砂', '青矾绿', '胭脂紫', '石英粉红'])
bottom = np.zeros(len(props))
fig, ax = plt.subplots(figsize=recipe_figsize('bar', n_x=len(props.index)))
for ct in props.columns:
    ax.bar(range(len(props)), props[ct], bottom=bottom, width=0.6,
           color=ct_colors.get(ct, MUTED), edgecolor='white', linewidth=0.5, label=ct)
    bottom += props[ct].values
ax.set_xticks(range(len(props)))
ax.set_xticklabels(props.index, fontsize=8)
ax.set_ylabel('Cell proportion'); ax.set_ylim(0, 1)
ax.legend(bbox_to_anchor=(1.02, 0.5), loc='center left', frameon=False, fontsize=6)
polish_axes(ax)
save_panel(fig, 'N_cellproportion')
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

以下三个脚本是完整可跑的（含 §1 全局开头），可直接复制成 `.py`。

### Example 1: UMAP（用 cohort_params + save_panel）

```python
import sys; sys.path.insert(0, 'scripts/')
from cns_style import *
import scanpy as sc
import omicverse as ov

set_cns_style_journal('nature')

# 假设 adata 已完成 QC → normalize → PCA → neighbors → leiden → UMAP
assert_anndata_keys(adata, obs_cols=['celltype'], obsm_keys=['X_umap'])
p = cohort_params(adata.n_obs)                       # size/alpha/figsize 联动
fig, ax = plt.subplots(figsize=p['figsize'])
ov.pl.embedding(adata, basis='X_umap', color='celltype',
                size=p['point_size'], alpha=p['alpha'],
                ax=ax, show=False, legend_loc=None)
add_cluster_labels(ax, adata, basis='umap', groupby='celltype', fontsize=7)
clean_umap_axes(ax)
optical_margin(ax, 0.12)
save_panel(fig, 'A_umap')                            # → panels/A_umap.pdf
```

### Example 2: 分组散点图（多时点 DE）

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

### Example 3: 空间表达 + scale bar + 配对箱线

```python
import sys; sys.path.insert(0, 'scripts/')
from cns_style import *
import squidpy as sq

set_cns_style_journal('nature')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=recipe_figsize('bar', n_x=2),
                               gridspec_kw={'width_ratios': [1.2, 1]})

# 左：空间 overlay + scale bar + 横置 colorbar
sq.pl.spatial_scatter(adata_sp, color='Cxcl12', ax=ax1, size=1.2, cmap=EXPR_CMAP,
                      vmin=0, alpha_img=1.0, alpha=0.85, title='', show=False)
add_scale_bar(ax1, length_um=200, px_per_um=0.5)
clean_umap_axes(ax1, xlabel='', ylabel='')
add_elegant_colorbar(ax1.collections[0], ax1, label='Expression', orientation='horizontal')

# 右：niche 内 vs 外的表达分布（配对箱线 + 显著性 bracket）
ge = adata_sp[:, 'Cxcl12'].X.toarray().ravel()
in_niche = (adata_sp.obs['niche'] == 'fibrotic').values
bp = ax2.boxplot([ge[~in_niche], ge[in_niche]], positions=[0, 1], widths=0.4,
                 patch_artist=True, showfliers=False,
                 boxprops=dict(facecolor='#88C0D0', edgecolor=NEAR_BLACK, lw=0.8),
                 medianprops=dict(color='#BF616A', lw=1.5))
bp['boxes'][1].set_facecolor('#BF616A')
for i, mask in enumerate([~in_niche, in_niche]):
    jit = np.random.uniform(-0.1, 0.1, mask.sum())
    ax2.scatter(np.full(mask.sum(), i) + jit, ge[mask], s=3, alpha=0.4,
                color=NEAR_BLACK, edgecolor='none', rasterized=True)
ax2.set_xticks([0, 1]); ax2.set_xticklabels(['Other', 'Fibrotic niche'], fontsize=8)
ax2.set_ylabel('Cxcl12 expression', fontsize=9, labelpad=8, fontstyle='italic')
add_significance_bracket(ax2, 0, 1, pval=1e-6)
polish_axes(ax2)
save_panel(fig, 'C_spatial_quant')
```