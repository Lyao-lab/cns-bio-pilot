# Publication-Grade Figure Aesthetics (CNS Standard)

> Based on Nature / Science / Cell / Journal of Cell Science official figure guidelines (2025). All figures (single-cell UMAP, spatial sections, volcano plots, heatmaps, PPT-embedded figures) must follow these rules.

## 1. Size & Resolution

| Journal | Single-column width | Double-column width | Photo DPI | Line-art DPI | Format |
|---|---|---|---|---|---|
| Nature | 88 mm | 180 mm | 300 | 600+ | TIFF/EPS/PDF |
| Cell | ~85 mm | ~180 mm | 300 | 600 | TIFF/EPS/PDF |
| Science | ~85 mm | ~180 mm | 300 | 300+ | EPS/PDF |
| J Cell Sci | — | 180×210 mm | 300 | 600 | TIFF/EPS |

**In practice** — set these uniformly when exporting from matplotlib / ov.pl:
```python
import matplotlib.pyplot as plt
plt.rcParams.update({
    'figure.dpi': 300,           # publication minimum
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',     # trim whitespace (mandatory for PPT embed)
    'savefig.format': 'pdf',     # vector preferred; TIFF for photos
    'pdf.fonttype': 42,          # TrueType embedding (editable)
    'ps.fonttype': 42,
})
# ov.plot_set() already sets most of this; the above are supplemental overrides
```

## 2. Fonts

| Requirement | Standard |
|---|---|
| Font family | **sans-serif**: Arial or Helvetica (Nature/Cell mandatory); no serif (Times only in Science body text) |
| Minimum font size (final print) | 6–7 pt; legends/axes ≥ 7.5 pt |
| Panel labels (A/B/C) | 8 pt bold |
| Size hierarchy | At most 2–3 sizes per figure (title/body/legend) |

**In practice**:
```python
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']  # English-only scenario
plt.rcParams['font.size'] = 8          # baseline
# title 10pt, axes 7.5pt, legend 7pt
```

### 中文场景字体兜底（必读，否则乱码）

`'font.family': 'Arial'` **不含中文字形**——只要图里有中文（汇报 PPT、中文图注、内部沟通图），
所有汉字会显示成方框（豆腐块）。本机（Windows）必须改用 sans-serif 列表，把中文优先字体放最前：

```python
plt.rcParams.update({
    'font.family': 'sans-serif',
    # Latin 走 Arial；中文走微软雅黑；DejaVu Sans 最后兜底
    'font.sans-serif': ['Microsoft YaHei', 'Arial', 'DejaVu Sans'],
    'axes.unicode_minus': False,   # 雅黑缺负号字形 → 用 ASCII '-'
})
```

| OS | 中文字体名 |
|---|---|
| Windows | `Microsoft YaHei`（微软雅黑）/ `SimHei`（黑体） |
| macOS | `PingFang SC` / `STHeiti` |
| Linux | `Noto Sans CJK SC`（需 `sudo apt install fonts-noto-cjk`）/ `WenQuanYi Zen Hei` |

**投稿 CNS 的最终版图**：英文期刊要求纯 Arial/Helvetica——届时把中文图注/标题改成英文，
并切回 `'font.family': 'Arial'`。中文兜底仅用于内部汇报、PPT、中文文稿配图。

> 这条规则排除了本 skill 测试中遇到的最常见乱码坑（Arial 不含 CJK 字形）。
> 凡是出图前先确认目标读者是中/英文，再选字体配置。

## 3. Color (Colorblind-Safe, CNS Hard Requirement)

Nature/Cell **explicitly forbid red/green combinations** for data encoding. Use colorblind-friendly palettes:

| Scenario | Recommended palette | Source |
|---|---|---|
| **Categorical (≤8 classes)** | **Morlandi Nord** (soft, refined; user-selected default) | Nord palette |
| Categorical (>8 classes) | tab20 or ov.pl.palette['red_blue'] | matplotlib/omicverse |
| Categorical (colorblind-compliant alt) | Okabe-Ito (8 colors, colorblind gold standard) | Nature Methods |
| **Sequential (expression / heatmap)** | **blue-white-red consensus gradient** (low=blue/white, high=red; bioinformatics consensus) | this skill, dual-track |
| Sequential (perceptually uniform alt) | viridis / magma | matplotlib |
| **Diverging (log2FC)** | **blue-white-red** (negative=blue, 0=white, positive=red) | this skill, dual-track |
| Spatial tissue sections | Morlandi discrete or blue-white-red sequential | — |

### User-Selected Default: Dual-Track Palette (Morlandi + Blue-White-Red)

**Discrete categorical (UMAP / clusters / spatial domains) — soft Morlandi Nord**:
```python
MORLANDI = ['#88C0D0','#BF616A','#A3BE8C','#D08770',
            '#B48EAD','#EBCB8B','#5E81AC','#D8DEE9']
# frost-blue / dark-red / moss-green / terracotta / violet / wheat-yellow / deep-blue / frost-grey — low-saturation refinement
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=MORLANDI)
```

**Sequential expression (heatmap / expression) — Morlandi-style blue-yellow-red (low-saturation; low=blue / mid=wheat / high=dark-red; unified with the discrete palette)**:
```python
from matplotlib.colors import LinearSegmentedColormap
EXPR_CMAP = LinearSegmentedColormap.from_list('byr_morlandi',
    ['#5E81AC','#8FBCD4','#ECEFF4','#D08770','#9B5A5A'], N=256)
# Usage: ax.imshow(data, cmap=EXPR_CMAP) or sc.pl.heatmap(..., cmap=EXPR_CMAP)
```

**Diverging (log2FC volcano / heatmap) — blue-white-red, 0=white midpoint**:
```python
DIVERGING_CMAP = LinearSegmentedColormap.from_list('log2fc',
    ['#2C5F8D','#88C0D0','#FFFFFF','#D08770','#8B2C2C'], N=256)
# vmin=-3, vmax=3 keeps 0 centered at white
```

**Dual-track rationale**: soft Morlandi for discrete categories (clear separation, not harsh); blue-yellow-red for continuous values (matches the "high expression = red" bioinformatics reading instinct, with a natural yellow mid-transition — the classic single-cell heatmap gradient).

**Okabe-Ito alternative** (when strict colorblind compliance is required, e.g. journal mandate):
```python
OKABE_ITO = ['#E69F00','#56B4E9','#009E73','#F0E442',
             '#0072B2','#D55E00','#CC79A7','#000000']
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=OKABE_ITO)
```

**Forbidden**:
- ❌ Red/green side-by-side encoding (protanopia/deuteranopia cannot distinguish)
- ❌ jet/rainbow (perceptually non-uniform, repeatedly criticized by Nature)
- ❌ Default matplotlib palette (over-saturated, unprofessional)
- ❌ Green-black-red heatmaps (legacy consensus, but red-green colorblind users can't read them — blue-white-red is safer)

## 4. Legends & Annotations

| Element | Requirement |
|---|---|
| N / sample size | Must be labeled (in figure or legend) |
| Statistical test | State method (Wilcoxon/t-test/ANOVA) + Padj threshold |
| Error bars | State SD vs SEM + n |
| Axes | Label + unit (e.g. log2 Expression) |
| Colorbar | Label stating what the value means |
| Scale bar (microscopy) | Mandatory (also recommended for spatial H&E alignment) |

### Title Must Not Overlap the Figure (multi-panel — read this)

matplotlib's default `set_title()` `pad` is too small, so titles often stick to the axes/data; in multi-panel layouts (`GridSpec` / `subplots`) the suptitle can crash into the first row of subplots, and the bottom of one row can squeeze the title of the next. **Two mandatory rules**:

```python
# (1) Pad every subplot title (in points)
ax.set_title('...', pad=8)

# Or set it once globally:
plt.rcParams['axes.titlepad'] = 8

# (2) In multi-panel layouts, widen row spacing and lift the suptitle
gs = gridspec.GridSpec(nrows, ncols, hspace=0.55, wspace=0.35)
fig.suptitle('...', y=0.98)   # closer to 1 = nearer the top, leaving room for row 1
```

| Parameter | Recommended value | Effect |
|---|---|---|
| `axes.titlepad` | 6–10 | safe gap between subplot title and axes top |
| `GridSpec(hspace=)` | 0.45–0.65 | vertical whitespace (prevents row crowding in multi-panel) |
| `GridSpec(wspace=)` | 0.30–0.40 | horizontal whitespace (colorbar/legend needs more) |
| `suptitle(y=)` | 0.97–0.99 | suptitle position, paired with top figure margin |
| `figure(figsize=)` | add height accordingly | larger hspace needs a taller canvas, else the data area shrinks |

**Pre-export self-check**: visually confirm every title has "breathing room" on all sides — no overlap with in-figure elements, neighboring subplots, colorbars, or legends. Overlap = editor will request a redo; very visible when embedded in PPT.

### Legend / Colorbar Must Not Overlap Data (multi-panel — read this)

matplotlib's default `legend(loc='best')` often covers data on small or dense scatter plots (UMAP / volcano are the classic cases). **Pick one of three**, ordered by least destructive:

| Option | Suited for | Code |
|---|---|---|
| **① Expand data range to create empty space** (preferred, loses no info) | scatter (UMAP/tSNE/volcano) | `ax.set_xlim(xmin-0.8, xmax+2.5)` then drop the legend into the empty zone |
| **② Move outside the axes** | large legend / many panels | `ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left')` + increase `wspace` |
| **③ Compact layout + transparent frame** | small legend, little whitespace | `frameon=False, borderaxespad=0`, pick a data-sparse corner (volcano upper-left is often empty) |

**Same for colorbar**: `plt.colorbar(..., pad=0.02)` sits close to the main plot by default; with many color levels use `pad=0.08` or control width with `fraction=0.04`.

```python
# Scatter preferred: expand xlim to reserve a legend zone
ax.set_xlim(data[:,0].min()-0.8, data[:,0].max()+2.5)
ax.legend(loc='lower right', bbox_to_anchor=(1.0, 0.0),
          frameon=False, markerscale=2, borderaxespad=0)

# Volcano: legend in a data-sparse corner (upper-left often empty), transparent frame
ax.legend(loc='upper left', frameon=False, borderaxespad=0.3)

# Many/large legends: move outside, widen wspace
ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', frameon=False)
gs = gridspec.GridSpec(n, m, wspace=0.45)   # reserve space on the right
```

**Forbidden**:
- ❌ Default `loc='best'` on dense scatter still covers data (matplotlib's 'best' is not smart enough)
- ❌ Legend dropped on a cluster center (even semi-transparent it occludes)
- ❌ No gap between colorbar and main plot (`pad<0.02`)

**Pre-export self-check**: every legend / colorbar must show a clear "whitespace zone" around it — covering no data points, clusters, or axis labels.

## 5. Cross-Figure Consistency (within one paper / report)

| Dimension | Unified requirement |
|---|---|
| Color | The same cell type has the same color across all figures (build a cell_type → color map, reuse globally) |
| Font | Same family and size system across all figures |
| Axis range | The same gene's expression has the same colorbar range across figures (avoid misleading) |
| Style | `ov.plot_set()` initialized once, never reset |

```python
# Global cell_type → color map (paper-level consistency)
CELL_TYPE_COLORS = {
    'CD4 T': '#E69F00', 'CD14+ Mono': '#56B4E9', 'B': '#009E73',
    'CD8 T': '#F0E442', 'NK': '#0072B2', 'Platelet': '#D55E00',
}
sc.pl.umap(adata, color='cell_type', palette=CELL_TYPE_COLORS)
# Reuse this map in every subsequent figure
```

## 6. Aligning ov.pl with This Spec

omicverse `ov.plot_set()` already sets:
- ✅ Fonts (sans-serif)
- ✅ Palette (built-in ov.pl.palette)
- ✅ Vector-friendly PDF rendering

**Must be added manually** (not covered by ov.plot_set):
- DPI 300+ (default 100, below publication grade)
- Okabe-Ito override (default palette is not colorblind-safe)
- font.type=42 (TrueType embedding)
- bbox_inches='tight' (trim whitespace)

## 7. Extra Requirements for PPT-Embedded Figures

Figures embedded in PPT (scientific-figure variant of the scientific-slides skill):
- Export with `bbox_inches='tight'` + `trim_image_whitespace` (no white frame)
- Aspect ratio matches the slide slot (16:9 or 4:3)
- Font size stays ≥7.5pt after slide scaling (readability contract)
- Max 4 panels per slide (qa_deck errors beyond that)

## References

- [Nature figure guidelines](https://figureguild.com/journals/nature)
- [Cell figure guidelines](https://figureguild.com/journals/cell)
- [Science/AAAS submission guide](https://www.science.org/content/page/instructions-preparing-initial-manuscript)
- [Journal of Cell Science manuscript preparation](https://journals.biologists.com/jcs/pages/manuscript-prep)
- [Nature/Science/Cell figure-spec comparison](https://conceptviz.app/blog/how-to-make-figures-for-nature-science-journals)
- Okabe-Ito palette: [Nature Methods 2007 colorblind guide](https://www.nature.com/articles/nmeth.1618)
