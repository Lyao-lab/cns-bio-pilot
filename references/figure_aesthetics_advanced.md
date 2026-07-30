# Advanced Figure Aesthetics: From "Not Ugly" to "Deliberately Beautiful"

> **Companion to** `figure_aesthetics.md` (compliance spec) — this file is the **positive design layer**. The compliance file tells you what NOT to do (no red/green, no jet, no overlap). This file tells you what TO do to make figures look *designed*, not *default*.
>
> **Reading rule**: read `figure_aesthetics.md` first (the floor), then this file (the ceiling). For multi-panel composition, also read `figure_layout.md`.
>
> **Tooling**: all functions referenced here are in `scripts/cns_style.py` — import and use them directly.

## 1. Color Narrative (beyond colorblind compliance)

### The three principles

**① Color temperature encoding** — use cool colors for "quiet/normal/background" and warm colors for "active/disease/focus":
```python
# Condition colors tell the story arc (independent of cell-type colors)
CONDITION_COLORS = {
    'Normal':  '#88C0D0',   # frost-blue = quiet
    'Disease': '#BF616A',   # dark-red = active
    'Treated': '#A3BE8C',   # moss-green = recovery
}
```

**② Saturation hierarchy** — focus cell types get their full Morlandi color; all others become grey. This creates an instant visual focal point:
```python
MORLANDI = ['#88C0D0','#BF616A','#A3BE8C','#D08770',
            '#B48EAD','#EBCB8B','#5E81AC','#D8DEE9']
MUTED = '#C8CDD3'  # all non-focus clusters

focus = {'Fibroblast': '#BF616A', 'Macrophage': '#5E81AC'}  # warm + cool contrast
palette = {ct: focus.get(ct, MUTED) for ct in adata.obs['celltype'].cat.categories}
sc.pl.umap(adata, color='celltype', palette=palette, show=False)
```

**③ The 5+1 discipline** — a single figure uses at most 5 named colors + 1 accent. Everything else is grey. This prevents the "rainbow UMAP" problem where 15 clusters in 15 equally-saturated colors = no hierarchy.
```python
def apply_5plus1_palette(categories, focus_list, base_palette=MORLANDI, accent='#BF616A'):
    """≤5 named colors from base_palette + 1 accent; rest = grey."""
    grey = '#C8CDD3'
    result = {}
    for i, cat in enumerate(focus_list[:5]):
        result[cat] = base_palette[i % len(base_palette)]
    if len(focus_list) > 5:
        result[focus_list[5]] = accent
    for cat in categories:
        if cat not in result:
            result[cat] = grey
    return result
```

### Desaturated background categories

When a UMAP has 15+ clusters but only 2-3 matter for the current figure:
```python
# Highlight 2-3 focus clusters, mute everything else
focus_clusters = ['Quiescent_1', 'Activated_Mac']
palette = {}
for ct in adata.obs['leiden'].cat.categories:
    if ct in focus_clusters:
        palette[ct] = MORLANDI[list(adata.obs['leiden'].cat.categories).index(ct) % len(MORLANDI)]
    else:
        palette[ct] = '#D8DEE9'  # Morlandi frost-grey (S≈8%)
```

### Sequential colormap perceptual check

Custom colormaps must be perceptually monotonic. Quick check:
```python
# Convert to grayscale — should be strictly monotonic (dark→light)
import numpy as np
from matplotlib.colors import to_rgba
def check_perceptual(cmap, name):
    greys = [0.2126*r + 0.7152*g + 0.0722*b for r,g,b,_ in [to_rgba(cmap(i/255)) for i in range(256)]]
    diffs = np.diff(greys)
    monotonic = np.all(diffs > -0.01) or np.all(diffs < 0.01)  # allow tiny noise
    print(f"{name}: perceptually monotonic = {monotonic}")
```

---

## 2. The "Polish Axes" Recipe (positive design after Tufte subtraction)

After removing chartjunk (Tufte), you don't leave bare axes — you add **subtle, deliberate** design elements:

### `polish_axes(ax)` — apply to every panel as the final step

```python
def polish_axes(ax, keep_spines=('left', 'bottom')):
    """CNS-grade axis styling: L-frame, outward ticks, subtle gridlines."""
    # Spine hierarchy: data-bearing axes get weight, others vanish
    for spine in ax.spines.values():
        spine.set_visible(False)
    for spine_name in keep_spines:
        ax.spines[spine_name].set_visible(True)
        ax.spines[spine_name].set_linewidth(0.8)
        ax.spines[spine_name].set_color('#2E3440')  # Morlandi near-black (not pure #000)

    # Outward ticks, no tick marks (label-only, ultra-clean)
    ax.tick_params(direction='out', length=0, labelsize=8, colors='#2E3440')

    # Subtle horizontal reference lines (NOT a grid — alpha=0.15 = barely visible)
    ax.yaxis.grid(True, linewidth=0.3, alpha=0.15, color='#4C566A')
    ax.set_axisbelow(True)  # gridlines behind data

    # Label offset (breathing room between axis and label)
    ax.set_xlabel(ax.get_xlabel(), labelpad=10)
    ax.set_ylabel(ax.get_ylabel(), labelpad=10)
```

### `clean_umap_axes(ax)` — Nature sc-paper convention

UMAP/tSNE plots in Nature/Cell papers have **no axes, no ticks** — just data + minimal "UMAP1/2" text:
```python
def clean_umap_axes(ax):
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('UMAP1', labelpad=4, fontsize=7, color='#4C566A')
    ax.set_ylabel('UMAP2', labelpad=4, fontsize=7, color='#4C566A')
```

### Annotation placement art

Arrows/labels go in **sparse regions**, pointing to **dense regions**. Use subtle styling:
```python
ax.annotate('CXCL12$^+$ Fibroblasts',
            xy=(2.8, 3.1),           # arrow tip: cluster center (dense)
            xytext=(5.5, 4.5),       # text: sparse region
            fontsize=7, color='#4C566A',
            arrowprops=dict(
                arrowstyle='-', lw=0.6, color='#4C566A',
                connectionstyle='arc3,rad=0.1'  # slight curve = elegant
            ))
```

### Volcano threshold lines (informational, not chartjunk)

Statistical thresholds ARE data-ink — keep them but make them subtle:
```python
ax.axhline(-np.log10(0.05), ls='--', lw=0.5, alpha=0.3, color='#4C566A')
ax.axvline([-1, 1], ls='--', lw=0.5, alpha=0.3, color='#4C566A')
```

---

## 3. Panel Visual Hierarchy

### Anchor panel principle

Every composite figure has **exactly one visual anchor** — the panel the reader's eye lands on first. It gets 40-50% of total area:

```python
# UMAP as anchor (45% of width), dotplot + violin as supporting
fig = plt.figure(figsize=(14, 5))
gs = gridspec.GridSpec(1, 3, figure=fig,
                       width_ratios=[1.8, 1, 1],  # ≈ 45:28:27
                       wspace=0.35)
```

### Golden ratio for 2-panel

Two panels at 1:1 look "no hierarchy". Use 1.618:1:
```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4),
                                gridspec_kw={'width_ratios': [1.618, 1]})
# ax1 = UMAP (anchor), ax2 = proportion bar (supporting)
```

### Height compensation for heterogeneous panels

Scatter (UMAP) fills its bounding box densely; violin/bar plots have whitespace. Compensate:
```python
fig = plt.figure(figsize=(12, 5))
gs = gridspec.GridSpec(2, 2, figure=fig,
                       height_ratios=[1.2, 1],   # top row (violin) 20% taller
                       width_ratios=[1.5, 1],
                       hspace=0.4, wspace=0.35)
```

### Baseline alignment check

All panels' x-axis baselines must be horizontally aligned:
```python
for ax in fig.axes:
    pos = ax.get_position()
    # All should have same y0 (bottom); adjust if not:
    # ax.set_position([pos.x0, 0.12, pos.width, pos.height])
```

### Density rhythm

Don't put two high-density panels adjacent (UMAP next to 50×50 heatmap = visual fatigue). Alternate high/low:
```
[UMAP (high)] → [bar chart (low)] → [heatmap (high)] → [schematic (low)]
```

---

## 4. Whitespace Philosophy

### Three principles

**① Optical margin for irregular shapes** — circular/convex data (UMAP) looks smaller than square data at the same bounding box. Expand by 15% (not 10%):
```python
xlim = ax.get_xlim(); ylim = ax.get_ylim()
xpad = (xlim[1] - xlim[0]) * 0.15
ypad = (ylim[1] - ylim[0]) * 0.15
ax.set_xlim(xlim[0] - xpad, xlim[1] + xpad)
ax.set_ylim(ylim[0] - ypad, ylim[1] + ypad)
```

**② Asymmetric whitespace = importance signal** — the anchor panel gets more surrounding whitespace than supporting panels:
```python
gs = gridspec.GridSpec(1, 3, figure=fig,
                       wspace=0.45,              # generous inter-panel
                       left=0.06, right=0.94,    # outer frame margin
                       top=0.90, bottom=0.12)    # top/bottom breathing
```

**③ Group spacing > intra-group spacing** (Gestalt proximity) — logically paired panels are closer together:
```python
# A+B are overview (tight), C is mechanism (separated)
gs = gridspec.GridSpec(1, 3, figure=fig,
                       wspace=0.25,              # tight within A-B
                       width_ratios=[1, 1, 1.3]) # C gets extra space = separation
```

---

## 5. Typographic Rhythm

### Modular scale (1.2x from 7pt base)

Font sizes are NOT arbitrary — they follow a ratio system:
```python
SCALE = 1.2
BASE = 7
TYPE_SCALE = {
    'caption':     BASE,              # 7pt  — figure legend text
    'tick':        BASE * SCALE,      # 8.4 → 8pt
    'axis_label':  BASE * SCALE**2,   # 10pt
    'title':       BASE * SCALE**3,   # 12pt
    'panel_label': BASE * SCALE**3,   # 12pt bold
    'suptitle':    BASE * SCALE**4,   # 14.4 → 14pt
}
```

**Rule**: only these sizes are allowed: 7, 8, 10, 12, 14. Never 9pt or 11pt (breaks the rhythm).

### Line spacing

Multi-line titles need `linespacing=1.4` (matplotlib default 1.2 is too tight):
```python
ax.set_title('Fibroblast subtypes\nshow quiescent rewiring',
             linespacing=1.4, pad=10)
```

### In-figure annotation vs axis label distinction

| Element | Size | Color | Weight |
|---|---|---|---|
| Axis label (x/y) | 10pt | `#2E3440` (near-black) | normal |
| Tick label | 8pt | `#2E3440` | normal |
| In-figure annotation (arrows) | 7pt | `#4C566A` (grey) | medium |
| Gene name | 7pt italic | `#4C566A` | normal |
| Panel letter (A/B/C) | 12pt | `#2E3440` | **bold** |
| Suptitle | 14pt | `#2E3440` | bold |

### Gene/protein naming convention (HGNC)
```python
# Gene = italic; Protein = roman (non-italic)
ax.annotate('CXCL12', fontsize=7, fontstyle='italic')   # gene
ax.annotate('CXCL12 protein', fontsize=7)                # protein
```

---

## 6. Report-Level Composition (multi-figure narrative)

### Figure narrative arc (CNS implicit convention)

| Position | Role | Panels | Complexity | Example |
|---|---|---|---|---|
| **Figure 1** | Atlas / overview | 2-3 | Low (UMAP + proportion) | "Here are the cell types in this tissue" |
| **Figure 2-N** | Mechanism (one per figure) | 4-6 | Medium-high | "This pathway drives this phenotype" |
| **Last Figure** | Integration / validation / model | 2-3 | Low (schematic + spatial validation) | "Here's the model, validated in situ" |

### Panel density rhythm

After two consecutive figures with ≥5 panels, insert a "breathing figure" (≤3 panels, lots of whitespace) to prevent reviewer visual fatigue.

### `manifest.yaml` — paper-level visual DNA

Create at project start; every figure script imports it:
```yaml
# manifest.yaml — lock visual identity for the entire paper
cell_type_colors:
  Fibroblast: '#BF616A'
  Macrophage: '#5E81AC'
  T_cell: '#A3BE8C'
  SMC: '#D08770'
  B_cell: '#B48EAD'
  Endothelial: '#88C0D0'
  Epithelial: '#EBCB8B'
  Mast: '#D8DEE9'

condition_colors:
  Normal: '#88C0D0'    # cool = quiet
  Disease: '#BF616A'   # warm = active

sequential_cmap: 'byr_morlandi'    # all heatmaps
diverging_cmap: 'log2fc'           # all volcano/FC plots

font_base: 8
scale_ratio: 1.2
panel_label_style: 'bold'          # A, B, C in bold
```

```python
import yaml
with open('manifest.yaml') as f:
    style = yaml.safe_load(f)
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=list(style['cell_type_colors'].values()))
```

### Visual consistency audit (before submitting)

- [ ] Same cell type = same color in ALL figures (check against manifest)
- [ ] Same condition = same color (Normal always cool, Disease always warm)
- [ ] Same gene's heatmap uses same cmap + same vmin/vmax across figures
- [ ] Panel label style (bold/position) identical across all figures
- [ ] Font sizes from the modular scale only (7/8/10/12/14)

---

## 7. The One-Shot Style Function

All of the above is codified in `scripts/cns_style.py`. Usage:
```python
import sys; sys.path.insert(0, 'scripts/')
from cns_style import set_cns_style, polish_axes, add_elegant_colorbar, safe_scanpy_plot

set_cns_style()  # call ONCE at the top of every plotting script

# Then for each panel:
fig, ax = plt.subplots(figsize=(5, 5))
safe_scanpy_plot(sc.pl.umap, adata, color='celltype', ax=ax, show=False)
clean_umap_axes(ax)  # or polish_axes(ax) for non-UMAP panels

# Colorbar:
add_elegant_colorbar(mappable, ax, label='log2 Expression')

plt.savefig('figure1.pdf')
```

---

## Self-check: "Does this look designed?"

After applying all compliance rules (figure_aesthetics.md), ask these additional questions:

- [ ] **Color narrative**: is there a clear focal point (2-3 saturated colors + grey background)? Or is everything equally loud?
- [ ] **Anchor panel**: does one panel clearly dominate (40-50% area)? Or are all panels equal (no hierarchy)?
- [ ] **Whitespace**: is there breathing room around the anchor? Or is everything crammed edge-to-edge?
- [ ] **Axes polish**: L-frame + outward ticks + subtle gridlines? Or default matplotlib axes with all 4 spines + inward ticks?
- [ ] **Typography rhythm**: are font sizes from the 1.2x scale (7/8/10/12/14)? Or random sizes (9pt here, 11pt there)?
- [ ] **Colorbar**: slim (fraction=0.046) + no border + 3 ticks? Or default fat box?
- [ ] **Report consistency**: do all figures in this paper share the same cell_type_colors / condition_colors / cmap? Or does each figure pick its own?
- [ ] **Narrative arc**: does Figure 1 = overview, middle = mechanism, last = validation? Or is the order arbitrary?
