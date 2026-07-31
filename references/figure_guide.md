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
- Tissue α=0.4 background; spots s=1.5 (Visium) / s=0.3 (high-res)
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
