# Figure Guide — 生信发表级图表视觉规格（唯一参考）

> 本文件合并了原 figure_aesthetics / aesthetics_advanced / design / layout / recipes 五个文件。
> 画图时只需读这一个文件 + 用 `scripts/cns_style.py` 的函数。

---

## 0. Quick Reference Card（速查：画图前先看这里）

```python
# 每个绘图脚本的固定开头（3 行）：
import sys; sys.path.insert(0, 'scripts/')
from cns_style import *  # 或按需 import
set_cns_style_journal('nature')  # 'nature'|'science'|'cell'|'generic'
```

| 要画什么 | 首选（一行搞定） | 必须调的 cns_style 函数 | 最关键参数 |
|---|---|---|---|
| UMAP/tSNE | `ov.pl.embedding(adata, color='ct', frameon='small')` | `add_cluster_labels()` + `finalize_figure()` | size=point_size_for_n(n) |
| Volcano | `ov.pl.volcano(de_df, pval_name='padj', fc_name='log2FC')` | `volcano_colors()` + `polish_axes()` + `finalize_figure()` | figsize=(4,3.5) |
| Dotplot | `ov.pl.dotplot(adata, var_names=genes, groupby='ct')` | `finalize_figure()` | standard_scale='var' |
| Violin | `ov.pl.violin(adata, keys=genes, groupby='ct', alternating_background=True)` | `finalize_figure()` | violin_alpha=0.8, spine=#b4aea9 |
| Heatmap | `sc.pl.heatmap(adata, var_names=genes, groupby='ct')` | `add_elegant_colorbar()` + `finalize_figure()` | vmin=-2, vmax=2, cmap=EXPR_CMAP |
| Spatial | `ov.pl.plot_spatial(adata, color=gene)` | `add_scale_bar()` + `finalize_figure()` | alpha_img=1.0, scale bar 必须 |
| Bar (比例) | 手动 matplotlib | `polish_axes()` + `add_significance_bracket()` + `finalize_figure()` | y 从 0 开始, 95% CI |
| 富集条形图 | 手动 matplotlib | `polish_axes()` + `finalize_figure()` | 水平, -log10(FDR) 降序 |
| L-R Bubble | 手动 matplotlib | `add_elegant_colorbar()` + `polish_axes()` | size=-log10(p), color=mean |
| Feature 矩阵 | `ov.pl.embedding(adata, color=[g1,g2,...], ncols=3)` | `clean_umap_axes()` + `finalize_figure()` | 共享 vmin/vmax |

**铁律**：每张图 `savefig` 前必须调 `finalize_figure(fig)`。
**原则**：优先 `ov.pl.*`（自动 omicverse 风格）；`ov.pl` 不支持的才手动 matplotlib。
**拼图**：逐张独立出图 → 验证 → `scripts/main.py --input A.pdf B.pdf ... --output fig.pdf`

---

## 1. 全局设定（每个绘图脚本第一行）

```python
from cns_style import set_cns_style_journal
set_cns_style_journal('nature')  # 'nature'|'science'|'cell'|'generic'
```

这自动设好：Morlandi 配色 / Arial 字体 / modular scale 字号(7/8/10/12/14) / L-frame axes / outward ticks / 300-600 DPI / PDF 输出。

---

## 2. 配色

**Morlandi Nord**（离散/categorical）：
```python
MORLANDI = ['#88C0D0','#BF616A','#A3BE8C','#D08770','#B48EAD','#EBCB8B','#5E81AC','#81A1C1']
```

**连续表达**（heatmap/feature）：`EXPR_CMAP`（蓝→麦→暗红）
**Diverging**（log2FC）：`DIVERGING_CMAP`（蓝→白→红，0=白）

**配色示例**：
```python
# 好的配色（Morlandi + 色温叙事）
palette = {'Fibroblast': '#BF616A', 'Macrophage': '#5E81AC',  # 焦点：原色
           'T_cell': '#A3BE8C', 'B_cell': '#B48EAD',           # 配角：原色
           'Endothelial': '#C8CDD3', 'Epithelial': '#C8CDD3'}  # 非焦点：grey
# 坏的配色
palette = 'tab20'  # ← 高饱和霓虹，学生作业感
cmap = 'jet'       # ← 感知不均匀，Nature 明确反对
```

---

## 3. 排版

| 元素 | 字号 | 颜色 | 备注 |
|---|---|---|---|
| Tick labels | 7-8pt | #2E3440 | |
| Axis labels | 10pt | #2E3440 | labelpad=10 |
| Title | 12pt | #2E3440 | pad=8 |
| Panel label (A/B/C) | 12pt bold | #2E3440 | offset (-0.12, 1.08) |
| In-figure annotation | 7pt | #4C566A | gene names italic |
| Legend | 7-8pt | #2E3440 | frameon=False |

- 字号只用 7/8/10/12/14；期刊 preset（6/7/8）覆盖此规则
- 多行 title: linespacing=1.4
- 文字颜色 #2E3440（不用纯黑 #000000）

---

## 4. 轴与留白

```python
polish_axes(ax)       # L-frame + outward ticks + alpha=0.15 参考线（非 UMAP）
clean_umap_axes(ax)   # 去所有轴/ticks，只留 "UMAP1/2"（UMAP/tSNE 专用）
optical_margin(ax, 0.12)  # 圆形数据多留 12% 呼吸空间
```

- 锚点 panel 占总面积 40-50%（`width_ratios=[1.8, 1, 1]`）
- 逻辑相关 panel 间距 < 逻辑分组间距
- savefig: `bbox_inches='tight', pad_inches=0.1`

---

## 5. 图型速查（每种图的精确参数）

### UMAP/tSNE — omicverse 风格
- **优先用 `ov.pl.embedding()`**（自动应用 omicverse 5 签名：`frameon='small'` / grid off / `legend_fontweight='bold'` / mini colorbar / cluster names on plot）
- omicverse 默认：`legend_loc='right margin'`, `na_color='lightgray'`, `edges=False`
- 手动 sc.pl.umap 时：`size`: <10k→8, 10-50k→3, 50-200k→1, >200k→0.3
- `alpha=0.7, edgecolor='none'`
- On-plot labels: `add_cluster_labels()`（白色光晕，median 定位）或 scanpy `legend_loc='on data'`
- 轴风格二选一：`frameon='small'`（omicverse L 型小轴）或 `clean_umap_axes()`（Nature 无轴）
- `optical_margin(ax, 0.12)`

### Volcano — omicverse 风格
- **优先用 `ov.pl.volcano()`**（自动配色 + top-10 标注 + legend 下方）
- 手动时对齐 omicverse 默认色：Up=`#e25d5d`, Down=`#7388c1`, NS=`#d7d7d7`
- figsize: **(4, 3.5)**（与 `recipe_figsize('volcano')` 一致）
- 阈值线: `ls='--', lw=0.5, alpha=0.3`
- Gene labels: **top 10**（不是 5），fontsize=10，italic
- Legend: **图下方**（`bbox_to_anchor=(0.8, -0.2), ncol=2, fontsize=12`）
- Title: weight='normal'（不 bold），size=14
- `polish_axes(ax)`

### Heatmap — omicverse/scanpy 风格
- omicverse 无独立 heatmap 函数——用 `sc.pl.heatmap()` 或 `seaborn.clustermap()`
- Z-score per row, `vmin=-2, vmax=2`
- cmap=EXPR_CMAP 或 'RdBu_r'; row-clustered, **column-fixed by biology**（omicverse dotplot 也是 `dendrogram=False`）
- 白线分隔 groups: `linewidths=0.5, linecolor='white'`
- Gene names italic; `add_elegant_colorbar(label='Scaled expression')`
- 2024 顶刊趋势：**不画列 dendrogram**（列按生物学排序），行注释色条

### Dotplot — omicverse 风格
- **优先用 `ov.pl.dotplot()`**（自动标准：colorbar_title='Mean expression in group', size_title='Fraction of cells in group (%)'）
- `num_categories=7`（>7 类时 omicverse 自动分组）
- `standard_scale='var'`（行标准化）；cmap=EXPR_CMAP 或 'Reds'
- `edge_color='#2E3440', edge_lw=0.3`；`dendrogram=False`
- 统一 vmin/vmax across genes

### Violin/Box (gene expression per cluster) — omicverse 风格
- **交替背景色带**（omicverse 标志性特征）：white + group_color 淡化 80%（`_lighten_color(color, 0.8)`）
- Violin fill **α=0.8**（较不透明，omicverse 默认），edge 同色 lw=1
- Spine 颜色: **#b4aea9**（暖灰，不是纯黑）
- **水平 grid lines: True**（`alpha=0.3, lw=0.5`，帮助读数）
- Box overlay: **默认不加**（omicverse `show_boxplot=False`）；需要时 widths=0.15
- Individual points: **s=1**, α=0.4, jitter（omicverse 默认极小点）
- 统计检验: 内置（`statistical_tests='wilcox'`）或手动 `add_significance_bracket()`
- Y 轴: log-normalized expression
- X 轴: cluster names（≤12 rotation=0；>12 rotation=45）
- 多基因: 每基因一行 subplot（共享 x 轴），figsize=(n_clusters×0.6+1, n_genes×2.8)

```python
# 方式 A: 直接用 ov.pl.violin（推荐——自动应用 omicverse 全部样式）
ov.pl.violin(adata, keys=['CD3D','MS4A1','LYZ','CD68'], groupby='leiden',
             stripplot=True, jitter=True, size=1, jitter_alpha=0.4,
             violin_alpha=0.8, alternating_background=True,
             spine_color='#b4aea9', grid_lines=True,
             statistical_tests='wilcox',  # 自动加星号
             show=False, save='panels/violin_markers.pdf')

# 方式 B: matplotlib 精细版（完全控制，模拟 omicverse 风格）
from cns_style import MORLANDI, GREY, finalize_figure
import matplotlib.patheffects as pe

def _lighten_color(hex_color, amount=0.8):
    """Lighten a color towards white (omicverse's background band logic)."""
    import matplotlib.colors as mcolors
    r, g, b = mcolors.to_rgb(hex_color)
    return (r + (1-r)*amount, g + (1-g)*amount, b + (1-b)*amount)

genes = ['CD3D', 'MS4A1', 'LYZ']
clusters = adata.obs['leiden'].cat.categories
ct_colors = {cl: MORLANDI[i % len(MORLANDI)] for i, cl in enumerate(clusters)}

fig, axes = plt.subplots(len(genes), 1,
    figsize=(len(clusters)*0.6+1, len(genes)*2.8), sharex=True)
for row, gene in enumerate(genes):
    ax = axes[row] if len(genes) > 1 else axes
    data_per_cl = [adata[adata.obs['leiden']==cl, gene].X.toarray().ravel()
                   if hasattr(adata.X,'toarray')
                   else adata[adata.obs['leiden']==cl, gene].X.ravel()
                   for cl in clusters]
    # 交替背景色带（omicverse 标志性）
    for i, cl in enumerate(clusters):
        bg_color = _lighten_color(ct_colors[cl], 0.85)
        ax.axvspan(i-0.5, i+0.5, color=bg_color, alpha=0.5, zorder=0)
    # Violin (alpha=0.8, omicverse default)
    parts = ax.violinplot(data_per_cl, positions=range(len(clusters)),
                          showmeans=False, showmedians=False, showextrema=False)
    for i, pc in enumerate(parts['bodies']):
        c = ct_colors[clusters[i]]
        pc.set_facecolor(c); pc.set_alpha(0.8)
        pc.set_edgecolor(c); pc.set_linewidth(1)
    # Strip plot (s=1, alpha=0.4, omicverse default)
    for i, d in enumerate(data_per_cl):
        jit = np.random.uniform(-0.15, 0.15, len(d))
        ax.scatter(np.full(len(d), i)+jit, d, s=1, alpha=0.4,
                   color=ct_colors[clusters[i]], edgecolor='none', rasterized=True, zorder=3)
    # Grid + spine (omicverse style)
    ax.yaxis.grid(True, alpha=0.3, lw=0.5, color='#b4aea9', zorder=0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_color('#b4aea9'); spine.set_linewidth(0.8)
    ax.set_ylabel(gene, fontstyle='italic', fontsize=10, labelpad=10)
axes[-1].set_xticks(range(len(clusters)))
axes[-1].set_xticklabels(clusters, fontsize=7, rotation=45 if len(clusters)>12 else 0)
finalize_figure(fig, move_legend_right=False)
fig.savefig('panels/violin_markers.pdf', dpi=300, bbox_inches='tight', pad_inches=0.1)
plt.close(fig)
```

### Spatial — omicverse 风格
- **优先用 `ov.pl.plot_spatial()`**（自动处理 tissue + spots + colorbar）
- 手动时：Tissue `alpha_img=1.0`（不透明）; spots `alpha=0.85`, s=1.5 (Visium) / s=0.3 (high-res)
- **Scale bar 必须有**（缺它审稿人立刻扣分）; colorbar 横置于图下方（`orientation='horizontal'`）
- 一基因一 panel; shared vmin/vmax (99th percentile clip)
- `add_elegant_colorbar(label=gene_name)`
- omicverse spatial 默认：`frameon='small'`, `colorbar_loc='right'`

```python
# 完整可跑示例：空间基因表达 overlay
import squidpy as sq
fig, ax = plt.subplots(figsize=(5, 4.5))
sq.pl.spatial_scatter(adata_sp, color='Cxcl12', ax=ax, size=1.2,
                      cmap=EXPR_CMAP, vmin=0, alpha_img=1.0, alpha=0.85,
                      title='', show=False)
add_scale_bar(ax, length_um=200, px_per_um=0.5)
add_elegant_colorbar(ax.collections[0], ax, label='Expression', orientation='horizontal')
clean_umap_axes(ax, xlabel='', ylabel='')
finalize_figure(fig)
fig.savefig('panels/spatial_cxcl12.pdf', dpi=300, bbox_inches='tight', pad_inches=0.1)
plt.close(fig)
```

### Bar (proportions)
- 95% CI error bars (capsize=3, lw=1)
- Per-sample dots overlay (s=15, α=0.7)
- Y-axis starts at 0

### Chord/Circle (CCC)
- ≤8 cell types; lw ∝ strength; source-colored α=0.5
- figsize=(5,5) square

### Trajectory
- PAGA (3.5×3) + pseudotime UMAP (4.5×4)
- 分支拓扑 → 绝不用单线性曲线
- Gene-along-pseudotime: LOESS 平滑线 `lw=1.2` + 95% CI 带 `alpha=0.15`

### Enrichment Bar (GO/KEGG)
- **水平条形**，按 -log10(FDR) 降序排列
- 条色 = -log10(FDR) 映射（单暖色 `#BF616A` 或 EXPR_CMAP）
- x 轴: "-log₁₀(FDR)"；条右端标 gene count（`fontsize=6, color=GREY`）
- Top 10-15 条；通路名 ≤40 字符截断（`textwrap.shorten`）
- figsize: (4.5, 0.35×n_terms + 1)
- `polish_axes(ax)`；无 grid
```python
terms = enr.nsmallest(15, 'FDR')
fig, ax = plt.subplots(figsize=(4.5, 0.35*len(terms)+1))
y_pos = range(len(terms))
bars = ax.barh(y_pos, -np.log10(terms['FDR']), color='#BF616A', height=0.6, edgecolor='none')
ax.set_yticks(y_pos)
ax.set_yticklabels([t[:40] for t in terms['Term']], fontsize=7)
ax.set_xlabel(r'$-$log$_{10}$(FDR)', labelpad=10)
ax.invert_yaxis()  # top = most significant
for i, (b, n) in enumerate(zip(bars, terms['Gene_count'])):
    ax.text(b.get_width()+0.1, b.get_y()+b.get_height()/2, str(n), va='center', fontsize=6, color=GREY)
polish_axes(ax)
```

### Heatmap + Annotation Bar
- 列注释条（condition/celltype/batch）：高 0.1 inch/条，色来自 manifest
- 注释条与热图间留 0.5pt 白缝
- 用 `seaborn.clustermap(col_colors=...)` 或 GridSpec `height_ratios`
```python
import seaborn as sns
# col_colors: DataFrame, columns=annotation names, index=same as heatmap columns
col_ann = pd.DataFrame({'Condition': conditions}, index=celltypes)
col_ann_colors = {'Condition': CONDITION_COLORS}
g = sns.clustermap(expr_z, cmap=EXPR_CMAP, vmin=-2, vmax=2,
                   col_colors=col_ann, col_cluster=False, row_cluster=True,
                   figsize=recipe_figsize('heatmap', n_x=expr_z.shape[1], n_y=expr_z.shape[0]),
                   linewidths=0, cbar_pos=(0.02, 0.8, 0.03, 0.15))
```

### Spatial + Scale Bar
- H&E `alpha_img=1.0`（不透明！当前 guide 写 0.4 太淡）；spots `alpha=0.85`
- **Scale bar 必须有**（缺它 = 审稿人一眼扣分）
- Colorbar 横置于图下方：`orientation='horizontal', fraction=0.046, pad=0.08`
- Scale bar 长度取 100/200/500µm 中最接近图宽 1/5 者
```python
from cns_style import NEAR_BLACK
def add_scale_bar(ax, length_um=200, px_per_um=1.0, color='white', fontsize=7):
    length_px = length_um * px_per_um
    xlim = ax.get_xlim(); ylim = ax.get_ylim()
    x0 = xlim[0] + (xlim[1]-xlim[0])*0.05
    y0 = ylim[0] + (ylim[1]-ylim[0])*0.05
    ax.plot([x0, x0+length_px], [y0, y0], color=color, lw=2, solid_capstyle='butt')
    ax.text(x0+length_px/2, y0+(ylim[1]-ylim[0])*0.02, f'{length_um} μm',
            ha='center', va='bottom', fontsize=fontsize, color=color,
            path_effects=[__import__('matplotlib.patheffects',fromlist=['withStroke']).withStroke(linewidth=2, foreground='black')])
```

### L-R Bubble Plot (pathway × cell-type pair)
- x = cell-type pair (sender→receiver)；y = pathway
- size = -log10(p-value)，映射到 `s ∈ [20, 200]`
- color = mean expression（EXPR_CMAP）
- ≤10 pairs × ≤15 pathways；pair 标签 `rotation=45, ha='right', fontsize=6`
```python
fig, ax = plt.subplots(figsize=(max(5, n_pairs*0.6), max(4, n_pathways*0.35)))
scatter = ax.scatter(x_idx, y_idx, s=sizes, c=mean_expr, cmap=EXPR_CMAP,
                     edgecolor='#2E3440', linewidth=0.3, alpha=0.85)
ax.set_xticks(x_idx); ax.set_xticklabels(pair_labels, rotation=45, ha='right', fontsize=6)
ax.set_yticks(y_idx); ax.set_yticklabels(pathway_names, fontsize=7)
add_elegant_colorbar(scatter, ax, label='Mean expression')
polish_axes(ax, subtle_grid=False)
```

### Feature Plot Matrix (多基因 UMAP)
- `ncols=min(3, n_genes)`；每 panel (3, 3)
- 所有 panel 共享 `vmin=0, vmax=99th_percentile`（跨基因可比）
- 基因名斜体作 title（`fontstyle='italic', fontsize=10, pad=4`）
- 矩阵级单 colorbar（仅当基因同量纲）或 per-panel mini colorbar
- `clean_umap_axes(ax)` on all panels

---

## 6. 拼图规则

- 输入 = 已独立渲染+验证的 PDF/PNG（不是 live axes）
- Panel labels: 12pt bold, top-left
- wspace=0.35, hspace=0.45
- 共享 colorbar 合并（同 scale 不重复）
- 某张比例不对 → 回去重画那张，不在拼图时缩放

---

## 7. 报告级

- Figure 1 = atlas (2-3 panels) → 中间 = mechanism (4-6) → 最后 = validation (2-3)
- 全论文锁 `manifest.yaml`（cell_type_colors / condition_colors / cmap）
- 同一 cell type 全论文同色；同一 gene 全论文同 colorbar range

---

## 8. Ugly → Beautiful 速记

| ❌ 丑 | ✅ 美 |
|---|---|
| 默认 matplotlib 调色板 | Morlandi Nord |
| s=15 for 100k cells (blob) | s=1 (texture) |
| 4 个 spine + ticks + grey bg | L-frame / 去轴 (UMAP) |
| 外部 legend 15 entries | On-plot labels |
| 所有 cluster 同等饱和 | 焦点饱和 + 其余 grey |
| 纯黑 #000 | #2E3440 |
| 默认 fat colorbar with border | slim, no border, 3 ticks |
| 字号随意 (9pt, 11pt) | Modular scale 7/8/10/12/14 |
| 一边画一边拼 | 逐张独立出图验证后再拼 |

---

## 9. 统计标注（p-value bracket / star）

```python
# 使用 cns_style.py 的函数（签名：ax, x1, x2, pval, y=None, height_frac=0.03）
from cns_style import add_significance_bracket

# y 不传时自动定位（数据最大值上方 2%）
add_significance_bracket(ax, x1=0, x2=1, pval=3.2e-5)
# 多组比较：自动错开高度
add_significance_bracket(ax, x1=0, x2=2, pval=0.003)
```

**规则**：
- Star 定义写在 legend：`*P<0.05, **P<0.01, ***P<0.001, ****P<0.0001`
- 优先报 exact P（`P=3.2×10⁻⁵`），star 是辅助
- bracket 线 `lw=0.8, color='#2E3440'`（不用纯黑）
- 多组比较时 bracket 高度错开（每层 +0.1），避免交叉
- `ns` 也标出来（不显著也是信息）

---

## 10. Layout 三铁律（legend / 文字 / 比例）

### 铁律 1: Legend 永远在右侧外置

```python
# 唯一正确的 legend 放置方式：
ax.legend(frameon=False, fontsize=7,
          bbox_to_anchor=(1.02, 0.5), loc='center left',  # 右侧外置，垂直居中
          borderaxespad=0)
# 如果 legend 太长（>8 entries），用 ncol=2 或缩小到 6pt
# 如果用 legend 导致右侧被截：figsize 宽度 +1 inch，或 wspace 加大
```

**反例**（这些做法会把 legend 盖在数据上）：
```python
# ❌ loc='best' — matplotlib 的 'best' 经常把 legend 盖在数据上
ax.legend(loc='best')
# ❌ 图内 legend + 边框 — 视觉噪音
ax.legend(loc='upper right', frameon=True)
```

**例外**：UMAP 用 on-plot labels 代替 legend（见 §5 UMAP 规则）。

### 铁律 2: 文字不重叠

```python
# 每张图 savefig 前调用：
from cns_style import finalize_figure
finalize_figure(fig)  # 自动检测文字 bbox 重叠 + legend 位置 + rasterize
fig.savefig('panel.pdf', dpi=300, bbox_inches='tight', pad_inches=0.1)
```

`finalize_figure` 自动检查：title/label/annotation 的 bbox 两两交叉；>50k 点未 rasterize 警告；legend 覆盖数据自动移到右侧。

**如果仍有重叠**（`finalize_figure` 会 warn）：
- 加大 `figsize` 高度（不是缩小字号）
- 缩短 title 文字（不是让它挤在一起）
- 减少 panel 数（不是硬塞）

### 铁律 3: 比例不畸形

| 图型 | 宽高比 | 代码 |
|---|---|---|
| UMAP/tSNE | 正方形（1:1） | `figsize=recipe_figsize('umap')` → (4.5, 4.5) |
| Spatial tissue | 匹配组织形状 | `figsize` 按 H&E 的 W/H 比例设 |
| Heatmap | cell 接近正方形 | `figsize` 配合 `ax.set_aspect('auto')` |
| Volcano | 4:3.5 | `recipe_figsize('volcano')` |
| Bar/Violin | 宽度随组数增长 | `recipe_figsize('bar', n_x=N)` |

```python
# ❌ 反例：UMAP 被拉成椭圆
fig, ax = plt.subplots(figsize=(6, 3))  # 太扁
# ✅ 正例：
fig, ax = plt.subplots(figsize=recipe_figsize('umap'))  # (4.5, 4.5) 正方形
```

---

## 11. 实战教训（从真实 PPT 迭代中提炼）

> 以下教训来自一次 16-slide 瓣膜发育 PPT 的完整迭代过程（11 张脚本、15 张图、多轮返工）。每条都是真实踩过的坑。

### 11.1 空间散点图（spatial scatter）的 7 个陷阱

| # | 陷阱 | 表现 | 解决 |
|---|---|---|---|
| 1 | **niche bins 太少被背景淹没** | 13w 仅 687/41923 bins，niche 散点几乎不可见 | niche 点 s≥12 + 背景减到 ≤30000 subsample + alpha 0.15 |
| 2 | **细长 niche 的 bbox 计算错误** | niche 19850×9150px，buffer=max(W,H)*0.25=4962 → bbox 太大 | buffer=`min(W,H)*0.15`（用短边，更紧凑） |
| 3 | **全切片散点 s 太大糊成色块** | 483646 bins × s=1 → 点重叠 | s=0.3-0.5（>20 万 bins）；niche 放大图 s=8-15 |
| 4 | **convex hull 轮廓遮挡数据** | 在散点上画黑色多边形 → 用户反感 | 不要主动画 hull；如需标 niche 用文字注释或 inset |
| 5 | **多 panel 统一 colorscale** | 三时点各自 vmax → 不可比 | `vmax = max(三时点 p95)`，共享 |
| 6 | **scale bar 缺失** | 审稿人一眼扣分 | `add_scale_bar()` 必须有；坐标→μm 换算需平台元数据 |
| 7 | **24w niche 细长导致 panel "空"** | niche 占 panel 面积 <5% | 放大到 niche bbox（不是全切片）；或改为梯度曲线 |

### 11.2 dotplot 的 4 个陷阱

| # | 陷阱 | 解决 |
|---|---|---|
| 1 | **点太大**（s=420 for frac=100%）→ 重叠 | `s = 8 + frac/100 * 100`（max s=108，不是 420） |
| 2 | **26 类×26 基因糊成一团** | 行/列分组（按 lineage 排序）+ 分隔线 |
| 3 | **legend 挤压数据区** | finalize_figure 自动移 legend → 预先放好（底部/右侧外置） |
| 4 | **行名/列名消失** | set_yticklabels 后检查渲染（finalize_figure 可能移位） |

### 11.3 火山图 → 分组散点图的替代决策

**教训**：火山图在 niche DE / 多时点 / 多组间比较场景经常**丑且不可读**——基因标注重叠、灰点密集、关键基因挤在 FDR 地板。多组比较时火山图无法并列展示。

**替代方案**：**分组散点图**（y=logFC，x=各时点/组别，每点=一个基因）：
```python
# 多时点/多组别 DE 结果：x=组别，y=logFC，每点=一个基因
fig, ax = plt.subplots(figsize=recipe_figsize('bar', n_x=len(comparisons)))
for i, comp in enumerate(comparisons):  # ['13w_vs_ctrl', '24w_vs_ctrl', '36w_vs_ctrl']
    de = de_dict[comp]
    sig = de['padj'] < 0.05
    # 显著基因：彩色散点
    ax.scatter(np.full(sig.sum(), i) + np.random.uniform(-0.15, 0.15, sig.sum()),
               de.loc[sig, 'log2FC'], s=20, alpha=0.7,
               color=UP_COLOR, edgecolor='white', linewidth=0.3, zorder=3)
    # ns 基因：灰色散点
    ns = ~sig
    ax.scatter(np.full(ns.sum(), i) + np.random.uniform(-0.15, 0.15, ns.sum()),
               de.loc[ns, 'log2FC'], s=8, alpha=0.3,
               color=NS_COLOR, edgecolor='none', zorder=2)
    # 标注 top-3 基因
    top3 = de.loc[sig].nlargest(3, 'log2FC')
    for _, r in top3.iterrows():
        ax.annotate(r['gene'], xy=(i, r['log2FC']),
                    xytext=(i+0.2, r['log2FC']+0.3), fontsize=6,
                    fontstyle='italic', color=NEAR_BLACK,
                    arrowprops=dict(arrowstyle='-', lw=0.4, color=GREY))

ax.axhline(0, color=GREY, lw=0.5, ls='-')
ax.axhline([1, -1], color=GREY, lw=0.4, ls='--', alpha=0.3)  # logFC threshold
ax.set_xticks(range(len(comparisons)))
ax.set_xticklabels(comparisons, fontsize=8, rotation=30, ha='right')
ax.set_ylabel(r'log$_2$(Fold Change)', fontsize=10, labelpad=10)
polish_axes(ax)
finalize_figure(fig)
```
**优势**：多时点/多组直接可比；无标注重叠；显著 vs ns 用颜色+大小区分；每个组别的 DE 分布一目了然。

### 11.4 UMAP 双层次注释的陷阱

| 陷阱 | 解决 |
|---|---|
| 26 亚型 on-plot labels 互相遮挡 | 只标 n>2000 的主要亚型 + VIC 焦点；其余靠颜色 |
| labels 被散点挡住 | `zorder=12` + `path_effects=[withStroke(linewidth=3, foreground='white')]` |
| 同色系深浅区分度差 | 用**不同色相**而非微调深浅（CM 蓝 vs EC 青是完全不同色相） |
| 外置图例 26 行太挤 | 按大类分组（5 个 header + 子条目），fontsize=5.5 |

### 11.5 颜色编码的纪律

- **不要在散点上画圈/轮廓**——用户普遍反感（除非主动要求）
- **VIC/焦点色用最饱和**（#E64B35 亮珊瑚），非焦点用同系浅色或灰
- **三时点对比用 alpha 渐变**（0.5→0.75→1.0），不用完全不同颜色
- **显著=彩色，ns=灰**（不要给 ns 也上色）

### 11.6 finalize_figure 的自动干预

`finalize_figure(fig)` 会自动移动重叠的 legend——但有时把 legend 移到意外位置导致 panel 被挤压。

**对策**：
- 画图前预先规划 legend 位置（`bbox_to_anchor` 底部或右外置）
- 跑完后检查 finalize 的 warning（"Legend moved to outside-right"）
- 如果 Panel B 因为 legend 移位变空 → 去掉 Panel B（信息冗余时）或把 legend 放 Panel A 内

---

## 12. 完整 Worked Example（三个图从数据到 PDF）

> 官方最佳实践："三个 worked example 胜过二十条约束。" 以下是三个最高频图型的完整端到端代码。

### Example 1: UMAP（5000 cells → PDF）

```python
import sys; sys.path.insert(0, 'scripts/')
from cns_style import *
import scanpy as sc
import omicverse as ov

set_cns_style_journal('nature')

# 假设 adata 已完成 QC + normalize + PCA + neighbors + leiden
# UMAP 全宽展示，on-plot labels
fig, ax = plt.subplots(figsize=recipe_figsize('umap'))

# 用 ov.pl.embedding（自动 frameon='small' + bold legend）
ov.pl.embedding(adata, basis='X_umap', color='celltype',
                size=point_size_for_n(adata.n_obs),
                alpha=0.7, ax=ax, show=False, legend_loc=None)

# on-plot labels with white halo
add_cluster_labels(ax, adata, basis='umap', groupby='celltype', fontsize=7)
clean_umap_axes(ax)
optical_margin(ax, 0.12)
finalize_figure(fig)
fig.savefig('panels/A_umap.pdf', dpi=300, bbox_inches='tight', pad_inches=0.1)
plt.close(fig)
```

### Example 2: 分组散点图（多时点 DE → PDF）

```python
# 多时点 DE：x=组别，y=log2FC，每点=一个基因
import pandas as pd

comparisons = ['13w', '24w', '36w']  # vs ctrl
de_dict = {tp: pd.read_csv(f'de_{tp}.csv') for tp in comparisons}  # each has gene, log2FC, padj

fig, ax = plt.subplots(figsize=recipe_figsize('bar', n_x=len(comparisons)))
for i, tp in enumerate(comparisons):
    de = de_dict[tp]
    sig = (de['padj'] < 0.05) & (de['log2FC'].abs() > 0.5)
    ns = ~sig
    # ns: 小灰点
    jitter_ns = np.random.uniform(-0.15, 0.15, ns.sum())
    ax.scatter(np.full(ns.sum(), i) + jitter_ns, de.loc[ns,'log2FC'],
               s=8, alpha=0.3, color='#d7d7d7', edgecolor='none', rasterized=True)
    # sig: 大彩色点
    jitter_sig = np.random.uniform(-0.15, 0.15, sig.sum())
    colors = np.where(de.loc[sig,'log2FC'] > 0, '#e25d5d', '#7388c1')
    ax.scatter(np.full(sig.sum(), i) + jitter_sig, de.loc[sig,'log2FC'],
               s=20, alpha=0.7, c=colors, edgecolor='white', linewidth=0.3, zorder=3)
    # top-3 标注
    top3 = de.loc[sig].reindex(de.loc[sig,'log2FC'].abs().sort_values(ascending=False).index[:3])
    for _, r in top3.iterrows():
        ax.annotate(r['gene'], xy=(i, r['log2FC']),
                    xytext=(i+0.15, r['log2FC']+0.2), fontsize=6,
                    fontstyle='italic', color='#2E3440',
                    arrowprops=dict(arrowstyle='-', lw=0.4, color='#4C566A'))

ax.axhline(0, color='#4C566A', lw=0.5)
ax.axhline(1, color='#4C566A', lw=0.4, ls='--', alpha=0.3)
ax.axhline(-1, color='#4C566A', lw=0.4, ls='--', alpha=0.3)
ax.set_xticks(range(len(comparisons)))
ax.set_xticklabels([f'{c} vs ctrl' for c in comparisons], fontsize=8, rotation=20, ha='right')
ax.set_ylabel(r'log$_2$(Fold Change)', fontsize=10, labelpad=10)
polish_axes(ax)
finalize_figure(fig)
fig.savefig('panels/B_de_scatter.pdf', dpi=300, bbox_inches='tight', pad_inches=0.1)
plt.close(fig)
```

### Example 3: 空间表达 + scale bar + 比例定量

```python
# 空间基因表达 + scale bar + 配对箱线图（niche 内 vs 外）
import squidpy as sq

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=recipe_figsize('bar', n_x=2),
                                gridspec_kw={'width_ratios': [1.2, 1]})

# 左：空间 overlay
sq.pl.spatial_scatter(adata_sp, color='Cxcl12', ax=ax1, size=1.2,
                      cmap=EXPR_CMAP, vmin=0, alpha_img=1.0, alpha=0.85,
                      title='', show=False)
add_scale_bar(ax1, length_um=200, px_per_um=0.5)
clean_umap_axes(ax1, xlabel='', ylabel='')
add_elegant_colorbar(ax1.collections[0], ax1, label='Expression',
                     orientation='horizontal')

# 右：niche 内 vs 外的表达分布（配对箱线）
niche_cells = adata_sp.obs['niche'] == 'fibrotic'
expr_niche = adata_sp[niche_cells, 'Cxcl12'].X.toarray().ravel() if hasattr(adata_sp.X, 'toarray') else adata_sp[niche_cells, 'Cxcl12'].X.ravel()
expr_other = adata_sp[~niche_cells, 'Cxcl12'].X.toarray().ravel() if hasattr(adata_sp.X, 'toarray') else adata_sp[~niche_cells, 'Cxcl12'].X.ravel()

bp = ax2.boxplot([expr_other, expr_niche], positions=[0, 1], widths=0.4,
                 patch_artist=True, showfliers=False,
                 boxprops=dict(facecolor='#88C0D0', edgecolor='#2E3440', lw=0.8),
                 medianprops=dict(color='#BF616A', lw=1.5))
bp['boxes'][1].set_facecolor('#BF616A')
# 散点叠加
for i, data in enumerate([expr_other, expr_niche]):
    jit = np.random.uniform(-0.1, 0.1, len(data))
    ax2.scatter(np.full(len(data), i) + jit, data, s=3, alpha=0.4,
                color='#2E3440', edgecolor='none', rasterized=True)
ax2.set_xticks([0, 1])
ax2.set_xticklabels(['Other', 'Fibrotic niche'], fontsize=8)
ax2.set_ylabel('Cxcl12 expression', fontsize=9, labelpad=8, fontstyle='italic')
add_significance_bracket(ax2, 0, 1, pval=1e-6)
polish_axes(ax2)
finalize_figure(fig, move_legend_right=False)
fig.savefig('panels/C_spatial_quant.pdf', dpi=300, bbox_inches='tight', pad_inches=0.1)
plt.close(fig)
```
