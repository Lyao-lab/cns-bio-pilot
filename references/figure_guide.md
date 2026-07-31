# Figure Guide — 生信发表级图表视觉规格（唯一参考）

> 本文件合并了原 figure_aesthetics / aesthetics_advanced / design / layout / recipes 五个文件。
> 画图时只需读这一个文件 + 用 `scripts/cns_style.py` 的函数。

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
MORLANDI = ['#88C0D0','#BF616A','#A3BE8C','#D08770','#B48EAD','#EBCB8B','#5E81AC','#D8DEE9']
```

**连续表达**（heatmap/feature）：`EXPR_CMAP`（蓝→麦→暗红）
**Diverging**（log2FC）：`DIVERGING_CMAP`（蓝→白→红，0=白）

**规则**：
- 5+1 纪律：≤5 主色 + 1 强调色，其余 grey (#C8CDD3)
- 色温叙事：Normal=冷色(#88C0D0)，Disease=暖色(#BF616A)
- 饱和度层级：焦点 cluster 原色，非焦点 grey
- 禁止：jet/rainbow、红绿搭配、默认 matplotlib 调色板

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

- 只用 7/8/10/12/14（1.2x modular scale），不许 9pt/11pt
- **优先级**：`set_cns_style_journal('nature')` 的期刊字号（6/7/8）**覆盖** modular scale。Modular scale 仅在 `generic` 模式下生效。投稿时以期刊 preset 为准。
- 多行 title: linespacing=1.4
- 不用纯黑 #000000，用 #2E3440

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

### UMAP/tSNE
- `size`: <10k→8, 10-50k→3, 50-200k→1, >200k→0.3
- `alpha=0.7, edgecolor='none'`
- On-plot labels（adjustText），不用外部 legend
- `clean_umap_axes()` + `optical_margin(ax, 0.12)`

### Volcano
- Up=#BF616A (s=4), Down=#5E81AC (s=4), NS=#D8DEE9 (s=2, α=0.4)
- 阈值线: `ls='--', lw=0.5, alpha=0.3`
- Top-5 labels: italic, arrowprops `rad=0.1, lw=0.5`
- `polish_axes(ax)`

### Heatmap
- Z-score per row, `vmin=-2, vmax=2`
- cmap=EXPR_CMAP; row-clustered, column-fixed by biology
- 白线分隔 groups: `linewidths=0, ax.vlines(bounds, color='white', lw=1.5)`
- Gene names italic; `add_elegant_colorbar(label='z-score')`

### Dotplot
- `size_min=15, size_max=150`; cmap=EXPR_CMAP
- `edge_color='#2E3440', edge_lw=0.3`
- 统一 vmin/vmax across genes

### Violin/Box
- Fill α=0.3 (Morlandi color), edge lw=0.8
- Box: widths=0.15, median color=#BF616A lw=1.2
- Individual points: s=2, α=0.5, color=#2E3440, jitter

### Spatial
- Tissue `alpha_img=1.0`（不透明）; spots `alpha=0.85`, s=1.5 (Visium) / s=0.3 (high-res)
- **Scale bar 必须有**（缺它审稿人立刻扣分）; colorbar 横置于图下方
- 一基因一 panel; shared vmin/vmax (99th percentile clip)
- `add_elegant_colorbar(label=gene_name)`

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
# 手动 bracket（不依赖 statannotations 包）
def add_significance_bracket(ax, x1, x2, y, pval, height=0.05):
    """Add bracket + star annotation between two groups."""
    if pval < 0.0001: star = '****'
    elif pval < 0.001: star = '***'
    elif pval < 0.01:  star = '**'
    elif pval < 0.05:  star = '*'
    else:              star = 'ns'
    # Bracket lines
    ax.plot([x1, x1, x2, x2], [y, y+height, y+height, y],
            lw=0.8, color='#2E3440', clip_on=False)
    # Star text
    ax.text((x1+x2)/2, y+height, star, ha='center', va='bottom',
            fontsize=8, fontweight='bold', color='#2E3440')

# Usage (after bar/violin plot):
add_significance_bracket(ax, x1=0, x2=1, y=0.85, pval=3.2e-5)
# Multiple brackets: stagger y heights to avoid overlap
add_significance_bracket(ax, x1=0, x2=2, y=0.95, pval=0.003)
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

**禁止**：
- ❌ `loc='best'`（matplotlib 的 'best' 经常把 legend 盖在数据上）
- ❌ `loc='upper right'` 在 scatter 图内（遮挡数据点）
- ❌ legend 在图内且 `frameon=True`（视觉噪音）

**例外**：UMAP 用 on-plot labels 代替 legend（见 §5 UMAP 规则）。只有 >8 clusters 且标签放不下时才用外置 legend。

### 铁律 2: 文字不重叠

```python
# 每张图存之前必须调用（cns_style.py 提供）：
from cns_style import finalize_figure
finalize_figure(fig)  # 自动检查 + 修复重叠
fig.savefig('panel.pdf', dpi=300, bbox_inches='tight', pad_inches=0.1)
```

**最小间距规则**（`finalize_figure` 自动检查）：
- Title ↔ axes top: ≥ 8pt（`axes.titlepad=8`）
- Axis label ↔ tick label: ≥ 10pt（`labelpad=10`）
- Panel label ↔ 数据区: offset ≥ (-0.12, 1.08)
- Legend ↔ 数据区: `bbox_to_anchor` 外置（不在图内）
- 相邻 panel title ↔ 上一行数据: `hspace ≥ 0.45`

**如果仍有重叠**（`finalize_figure` 会 warn）：
- 加大 `figsize` 高度（不是缩小字号）
- 缩短 title 文字（不是让它挤在一起）
- 减少 panel 数（不是硬塞）

### 铁律 3: 比例不畸形

| 图型 | 宽高比规则 | 代码 |
|---|---|---|
| UMAP/tSNE | **必须正方形**（1:1），不许拉成椭圆 | `figsize=(4.5, 4.5)` + `ax.set_aspect('equal')` |
| Spatial tissue | **匹配组织实际形状**（不裁不拉） | `figsize` 按 H&E 的 W/H 比例设 |
| Heatmap | cell 接近正方形（aspect ≈ 1）或明确控制 | `ax.set_aspect('auto')` 但 figsize 配合 |
| Volcano | 略宽于高（4:3.5） | `recipe_figsize('volcano')` |
| Bar/Violin | 宽度随组数增长，高度固定 3-3.5 | `recipe_figsize('bar', n_x=N)` |

**禁止**：
- ❌ 把正方形 UMAP 放进 (6, 3) 的 figsize（拉成椭圆）
- ❌ `savefig(bbox_inches='tight')` 后不检查实际输出比例
- ❌ 多 panel 中某张被 `subplots_adjust` 挤压变形
- ❌ heatmap 的 cell 宽高比 >3:1 或 <1:3（看起来像条纹而非格子）

**修复**：每张图存完后 `finalize_figure(fig)` 会检查 axes 的 data ratio vs figure ratio，不匹配时 warn。
