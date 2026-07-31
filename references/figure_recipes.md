# Figure Recipes: Exact Visual Specifications for Each Bio Figure Type

> **This file answers**: "I have [this type of data/result] — what should the figure **concretely look like**?"
> Not "what chart type to use" (that's `figure_design.md`). This gives **exact parameters**: point size, alpha, colors, label placement, figsize, spacing — down to the number.
>
> **Companion files**: `cns_style.py` (utility functions), `figure_aesthetics_advanced.md` (design principles), `figure_design.md` (chart-type selection).
>
> **Rule**: every recipe below is the CNS default. Deviate only with explicit justification.

---

## 1. UMAP / tSNE Embedding (cell-type overview)

### The spec

| Parameter | Value | Why |
|---|---|---|
| figsize | (4.5, 4) per panel | slightly wider than tall (room for on-plot labels) |
| point size | `n_obs < 10k → s=8`; `10k-50k → s=3`; `50k-200k → s=1`; `>200k → s=0.3` | prevent blob at high cell counts |
| point alpha | 0.7 (overlapping points create density gradient naturally) | 1.0 = harsh; 0.5 = too faint |
| edges | `edgecolor='none'` | borders on 100k points = visual noise |
| axes | **NONE** — `clean_umap_axes()` (no ticks, no spines, just "UMAP1/2" in 7pt grey) | Nature sc convention |
| labels | **on-plot** at cluster centroids (adjustText), 8pt bold, `color=NEAR_BLACK` | no external legend (legend steals space + disconnects label from cluster) |
| legend | **only if** >8 clusters AND labels don't fit → external right, `frameon=False` | prefer on-plot labels |
| background | white (`facecolor='white'`) | not grey, not off-white |
| colorbar (continuous) | mini, right side, `fraction=0.046, pad=0.04`, 3 ticks, no border | `add_elegant_colorbar()` |
| optical margin | `optical_margin(ax, 0.12)` | circular data needs breathing room |

### The code

```python
from cns_style import set_cns_style_journal, clean_umap_axes, optical_margin, \
                      apply_5plus1_palette, add_elegant_colorbar, safe_scanpy_plot
import scanpy as sc
import matplotlib.pyplot as plt

set_cns_style_journal('nature')

fig, ax = plt.subplots(figsize=(4.5, 4))

# Determine point size by cell count
n = adata.n_obs
s = 8 if n < 10_000 else (3 if n < 50_000 else (1 if n < 200_000 else 0.3))

# Option A: categorical (cell types) — on-plot labels, no legend
palette = apply_5plus1_palette(
    adata.obs['celltype'].cat.categories,
    focus_list=['Fibroblast', 'Macrophage', 'T cell']  # your focus types
)
safe_scanpy_plot(sc.pl.umap, adata, color='celltype', palette=palette,
                 size=s, alpha=0.7, edgecolor='none',
                 legend_loc=None, ax=ax, show=False)
# Add on-plot labels at centroids
from adjustText import adjust_text
centroids = adata.obsm['X_umap']  # compute per-cluster mean
texts = []
for ct in adata.obs['celltype'].cat.categories:
    mask = adata.obs['celltype'] == ct
    cx, cy = adata.obsm['X_umap'][mask].mean(axis=0)
    texts.append(ax.text(cx, cy, ct, fontsize=8, fontweight='bold',
                         color='#2E3440', ha='center', va='center'))
adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle='-', color='#4C566A', lw=0.5))

clean_umap_axes(ax)
optical_margin(ax, 0.12)
fig.savefig('panels/A_umap_celltype.pdf', dpi=300, bbox_inches='tight', pad_inches=0.1)
plt.close(fig)
```

### Ugly vs beautiful

| ❌ Ugly (default) | ✅ Beautiful (CNS) |
|---|---|
| s=15 for 100k cells (blob) | s=1 for 100k cells (texture) |
| edgecolor='black' (noise) | edgecolor='none' (clean) |
| All 4 spines + ticks + grey background | No axes, white background |
| External legend with 15 entries (disconnects) | On-plot labels at centroids |
| All clusters equally saturated | Focus clusters saturated, rest grey |
| Default matplotlib palette (harsh) | Morlandi Nord (soft, refined) |

---

## 2. Volcano Plot (differential expression)

### The spec

| Parameter | Value | Why |
|---|---|---|
| figsize | (4, 3.5) | slightly wider than tall |
| point size | 4 (sig) / 2 (non-sig) | sig points larger = visual hierarchy |
| colors | sig up = `#BF616A` (warm red); sig down = `#5E81AC` (cool blue); non-sig = `#D8DEE9` (grey, alpha=0.4) | temperature narrative: up=active/warm, down=suppressed/cool |
| threshold lines | `axhline(-log10(0.05))` + `axvline(±1)`: `ls='--', lw=0.5, alpha=0.3, color='#4C566A'` | informational, not chartjunk |
| top hit labels | top 5-8 genes by `-log10(padj) * abs(log2FC)`; `fontsize=7, fontstyle='italic', color='#2E3440'`; connected with `arrowprops(lw=0.5, color='#4C566A', connectionstyle='arc3,rad=0.1')` | gene names italic (HGNC) |
| axes | `polish_axes(ax)` — L-frame + outward ticks + subtle y-grid | clean but readable |
| x-axis label | "log₂(Fold Change)" | subscript via LaTeX |
| y-axis label | "−log₁₀(adjusted P)" | subscript |
| xlim | symmetric: `(-max_abs_fc * 1.2, max_abs_fc * 1.2)` | centered at 0 |

### The code

```python
fig, ax = plt.subplots(figsize=(4, 3.5))

# Classify points
sig_up = (de['padj'] < 0.05) & (de['log2FC'] > 1)
sig_down = (de['padj'] < 0.05) & (de['log2FC'] < -1)
non_sig = ~sig_up & ~sig_down

ax.scatter(de.loc[non_sig, 'log2FC'], -np.log10(de.loc[non_sig, 'padj']),
           s=2, alpha=0.4, color='#D8DEE9', edgecolor='none', rasterized=True)
ax.scatter(de.loc[sig_down, 'log2FC'], -np.log10(de.loc[sig_down, 'padj']),
           s=4, alpha=0.8, color='#5E81AC', edgecolor='none', label='Down')
ax.scatter(de.loc[sig_up, 'log2FC'], -np.log10(de.loc[sig_up, 'padj']),
           s=4, alpha=0.8, color='#BF616A', edgecolor='none', label='Up')

# Threshold lines (subtle, informational)
ax.axhline(-np.log10(0.05), ls='--', lw=0.5, alpha=0.3, color='#4C566A')
ax.axvline([-1, 1], ls='--', lw=0.5, alpha=0.3, color='#4C566A')

# Top hit labels (top 5 by combined score)
de['score'] = -np.log10(de['padj'].clip(lower=1e-300)) * de['log2FC'].abs()
top = de.nlargest(5, 'score')
for _, row in top.iterrows():
    ax.annotate(row['gene'], xy=(row['log2FC'], -np.log10(row['padj'])),
                xytext=(row['log2FC'] + 0.3, -np.log10(row['padj']) + 0.5),
                fontsize=7, fontstyle='italic', color='#2E3440',
                arrowprops=dict(arrowstyle='-', lw=0.5, color='#4C566A',
                                connectionstyle='arc3,rad=0.1'))

ax.set_xlabel(r'log$_2$(Fold Change)', labelpad=10)
ax.set_ylabel(r'$-$log$_{10}$(adjusted P)', labelpad=10)
polish_axes(ax)
fig.savefig('panels/C_volcano.pdf', dpi=300, bbox_inches='tight', pad_inches=0.1)
plt.close(fig)
```

---

## 3. Heatmap (gene × cell-type expression matrix)

### The spec

| Parameter | Value | Why |
|---|---|---|
| figsize | (width = n_genes × 0.18, height = n_celltypes × 0.35) — auto-compute | proportional to content |
| color scale | z-score per row; `vmin=-2, vmax=2` (clip extremes) | row-relative, comparable across genes |
| cmap | `EXPR_CMAP` (Morlandi blue-yellow-red) or `RdBu_r` | NOT green-black-red (colorblind) |
| row clustering | `scipy.cluster.hierarchy`, method='ward', metric='euclidean' on z-scored rows | groups co-expressed genes |
| column order | fixed by cell-type hierarchy (not clustered) — keep biological grouping | don't let clustering scramble cell types |
| dendrogram | left side, `linkage_color='#4C566A'`, `linewidth=0.5` | subtle, not dominant |
| colorbar | top or right, `add_elegant_colorbar()`, label "z-score" | slim, no border |
| x-tick labels | cell-type names, `rotation=45, ha='right', fontsize=7` | readable at print size |
| y-tick labels | gene names, `fontstyle='italic', fontsize=6-7` | italic = gene (HGNC) |
| cell separators | thin white lines between cell-type groups: `ax.vlines(group_boundaries, ...)` with `color='white', lw=1.5` | visual grouping |

### The code

```python
import seaborn as sns
from cns_style import EXPR_CMAP, add_elegant_colorbar, cns_seaborn_context

set_cns_style_journal('nature')
cns_seaborn_context('nature')

# Prepare z-scored matrix (rows=genes, cols=cell_types)
expr_df = pd.DataFrame(
    adata[:, marker_genes].X.toarray() if hasattr(adata.X, 'toarray') else adata[:, marker_genes].X,
    index=adata.obs_names, columns=marker_genes
).groupby(adata.obs['celltype']).mean().T  # genes × celltypes
from scipy.stats import zscore
expr_z = expr_df.apply(zscore, axis=1).clip(-2, 2)

fig_w = expr_z.shape[1] * 0.5 + 2   # +2 for dendrogram + colorbar
fig_h = expr_z.shape[0] * 0.22
fig, ax = plt.subplots(figsize=(fig_w, fig_h))

sns.heatmap(expr_z, cmap=EXPR_CMAP, vmin=-2, vmax=2,
            linewidths=0, linecolor='white',
            xticklabels=True, yticklabels=True,
            cbar=False,  # we'll add elegant one manually
            ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=7)
ax.set_yticklabels(ax.get_yticklabels(), fontstyle='italic', fontsize=6.5)

# Elegant colorbar
mappable = ax.collections[0]
add_elegant_colorbar(mappable, ax, label='z-score', ticks=[-2, 0, 2])

fig.savefig('panels/D_heatmap_markers.pdf', dpi=300, bbox_inches='tight', pad_inches=0.1)
plt.close(fig)
```

---

## 4. Dotplot (marker genes × cell types)

### The spec

| Parameter | Value | Why |
|---|---|---|
| figsize | auto: (n_genes × 0.3 + 2, n_celltypes × 0.3 + 1) | proportional |
| point size encoding | % expressing: `size_min=15, size_max=150` (area, not radius) | area ∝ fraction |
| color encoding | mean expression: `EXPR_CMAP`, `vmin=0, vmax=3` (unified across genes) | comparable |
| point edge | `edgecolor='#2E3440', linewidth=0.3` | subtle definition against white |
| group separators | horizontal lines between cell-type groups: `color='#D8DEE9', lw=0.8` | visual grouping |
| x labels | gene names, `rotation=45, ha='right', fontstyle='italic', fontsize=7` | italic = gene |
| y labels | cell-type names, `fontsize=7` | |
| colorbar | right, slim, label "Mean expression" | `add_elegant_colorbar()` |
| size legend | separate small legend: 3 reference circles (25%, 50%, 75%) | explains size encoding |

### The code

```python
# Use scanpy's dotplot with custom styling
fig, ax = plt.subplots(figsize=(n_genes * 0.3 + 2, n_celltypes * 0.3 + 1))
dp = sc.pl.dotplot(adata, var_names=marker_dict, groupby='celltype',
                   standard_scale='var',  # or use raw mean
                   dot_max=0.999, smallest_dot=15,
                   color_map=EXPR_CMAP,
                   ax=ax, show=False, return_fig=True)
dp.style(color_map=EXPR_CMAP, edge_color='#2E3440', edge_lw=0.3,
         size_exponent=1.0, grid_line_width=0.8,
         x_label_rotation=45)
dp.savefig('panels/B_dotplot_markers.pdf', dpi=300, bbox_inches='tight')
plt.close('all')
```

---

## 5. Violin / Box Plot (gene expression per cluster OR proportion per condition)

### The spec

| Parameter | Value | Why |
|---|---|---|
| figsize | (n_groups × 0.7 + 1, 3) | width scales with groups |
| violin fill | Morlandi color per group, `alpha=0.3` | soft fill, not solid |
| violin edge | same Morlandi color, `lw=0.8` | definition |
| inner | `inner=None` (no inner box) — add box+points separately | layering control |
| box | `plt.boxplot(..., widths=0.15, flierprops={'markersize':0})` overlaid | compact median/IQR |
| individual points | `stripplot` or `ax.scatter`, `s=2, alpha=0.5, jitter=True, color='#2E3440'` | show every observation |
| significance brackets | `lw=0.8, color='#2E3440'`; stars: `fontsize=8, fontweight='bold'` | clean annotation |
| y-axis | starts at 0 (for proportions) or auto (for expression); `polish_axes()` | no misleading truncation |
| x labels | group names, `fontsize=7, rotation=0` (if ≤6 groups) or `rotation=45` (if >6) | |

### The code

```python
import seaborn as sns
fig, ax = plt.subplots(figsize=(n_groups * 0.7 + 1, 3))

# Violin (soft fill)
parts = ax.violinplot([data[g] for g in groups], positions=range(len(groups)),
                      showmeans=False, showmedians=False, showextrema=False)
for i, pc in enumerate(parts['bodies']):
    pc.set_facecolor(MORLANDI[i % len(MORLANDI)])
    pc.set_alpha(0.3)
    pc.set_edgecolor(MORLANDI[i % len(MORLANDI)])
    pc.set_linewidth(0.8)

# Box (compact)
bp = ax.boxplot([data[g] for g in groups], positions=range(len(groups)),
                widths=0.15, patch_artist=True,
                boxprops=dict(facecolor='white', edgecolor='#2E3440', lw=0.8),
                medianprops=dict(color='#BF616A', lw=1.2),
                whiskerprops=dict(color='#2E3440', lw=0.6),
                capprops=dict(color='#2E3440', lw=0.6),
                flierprops={'markersize': 0})

# Individual points (jittered)
for i, g in enumerate(groups):
    x_jitter = np.random.normal(i, 0.04, size=len(data[g]))
    ax.scatter(x_jitter, data[g], s=2, alpha=0.5, color='#2E3440',
               edgecolor='none', rasterized=True)

ax.set_xticks(range(len(groups)))
ax.set_xticklabels(groups, fontsize=7, rotation=0)
polish_axes(ax)
fig.savefig('panels/E_violin_proportion.pdf', dpi=300, bbox_inches='tight', pad_inches=0.1)
plt.close(fig)
```

---

## 6. Spatial (tissue image + gene expression overlay)

### The spec

| Parameter | Value | Why |
|---|---|---|
| figsize | match tissue aspect ratio (usually ~(5, 4.5) for Visium) | don't distort tissue |
| tissue image | shown at `alpha=0.4` as background | context without overwhelming |
| spots/cells | `size=1.5` (Visium) / `size=0.3` (high-res); `edgecolor='none'` | proportional to resolution |
| color scale | `EXPR_CMAP`, `vmin=0, vmax=99th_percentile` (clip top 1%) | avoid outlier domination |
| one gene per panel | NEVER overlay multiple genes on one tissue image | cross-gene comparison needs shared scale |
| shared vmin/vmax | across multi-gene panels: compute global 99th percentile, use for all | comparability |
| colorbar | mini, right, `add_elegant_colorbar()`, label = gene name | |
| axes | `clean_umap_axes(ax)` but with scale bar (if H&E registration known) | spatial context |
| title | gene name in `fontstyle='italic', fontsize=10` above panel | |

---

## 7. Bar Chart (cell-type proportions across conditions)

### The spec

| Parameter | Value | Why |
|---|---|---|
| figsize | (n_conditions × 1.2 + 1, 3.5) | |
| bar width | 0.6 (grouped) / full (stacked) | |
| bar fill | Morlandi per cell type; `edgecolor='white', lw=0.5` (stacked) or per-condition color (grouped) | separation between segments |
| error bars | 95% CI: `plt.errorbar(..., capsize=3, lw=1, color='#2E3440')` | NOT SEM alone |
| individual points | overlay per-sample dots: `s=15, alpha=0.7, color='#2E3440', edgecolor='white', lw=0.3` | show biological replicates |
| y-axis | **starts at 0** (proportions); label "Fraction of cells" | no truncation |
| significance | brackets + stars between conditions | `lw=0.8` |
| legend | external right or top, `frameon=False, ncol=2` | |

---

## 8. Chord / Circle Plot (cell-cell communication)

### The spec

| Parameter | Value | Why |
|---|---|---|
| max cell types | **≤8** — collapse rare types or switch to heatmap | readability limit |
| line width | proportional to interaction strength: `lw = strength × 3` (max lw=4) | encode magnitude |
| line color | source cell type's Morlandi color, `alpha=0.5` | directionality by color |
| node (cell type) | colored arc, width proportional to total interactions | |
| labels | outside the circle, `fontsize=7, fontweight='bold'` | |
| figsize | (5, 5) — always square | circular layout |
| background | white, no grid | |

---

## 9. Trajectory / Pseudotime (PAGA + colored UMAP)

### The spec

| Parameter | Value | Why |
|---|---|---|
| Panel 1: PAGA graph | `figsize=(3.5, 3)`; node size ∝ cluster size; edge width ∝ connectivity; node color = cluster Morlandi | topology overview |
| Panel 2: UMAP + pseudotime | `figsize=(4.5, 4)`; cells colored by pseudotime; cmap = `viridis` or `EXPR_CMAP`; `s=1-3` | continuous gradient |
| pseudotime colorbar | bottom or right, label "Pseudotime" | |
| branch labels | at branch tips, `fontsize=8, fontweight='bold'` | |
| NEVER | a single linear curve for branched topology | misrepresents biology |
| gene-along-pseudotime | companion panel: line plot, `lw=1.2`, shaded 95% CI `alpha=0.15` | molecular mechanism |

---

## 10. Feature Plot (gene expression on UMAP)

### The spec

| Parameter | Value | Why |
|---|---|---|
| figsize per gene | (3, 3) in a grid; `ncols=3` for 6 genes | compact matrix |
| point size | same as UMAP recipe (by n_obs) | consistency with overview UMAP |
| color | `EXPR_CMAP` (blue→yellow→red); `vmin=0, vmax=unified` across all gene panels | comparability |
| grey for zero | cells with 0 expression: `color='#D8DEE9'` (plot order: zero first, nonzero on top) | "negative" is visible |
| title | gene name, `fontstyle='italic', fontsize=10, pad=6` | HGNC convention |
| colorbar | **shared** (one for the whole grid, not per panel) — or mini per panel with same vmin/vmax | Tufte: no redundant ink |
| axes | `clean_umap_axes()` on all | |

---

## Universal rules (apply to ALL figure types)

1. **`plt.close(fig)` after every `savefig`** — prevents memory leaks + state pollution
2. **`bbox_inches='tight', pad_inches=0.1`** — always
3. **`rasterized=True` for scatter with >10k points** — keeps PDF small
4. **Gene names italic** (`fontstyle='italic'`); protein names roman
5. **No pure black** (`#000000`) — use `#2E3440` (Morlandi near-black) for all text/lines
6. **No default matplotlib palette** — always Morlandi or Okabe-Ito
7. **Every quantitative panel has N + stat test + error bar type** in the legend
8. **One figure = one message** — if you need two sentences, split into two figures
