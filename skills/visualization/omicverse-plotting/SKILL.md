---
name: omicverse-plotting
description: 统一科学绘图 API 基于 OmicVerse V2 的 ov.pl.* 模块（80+ 函数）。一个 ov.plot_set() 初始化即可覆盖单细胞/空间/bulk 全部常规图：embedding/dotplot/violin/volcano/heatmap/ccc/spatial/cellproportion。
---

## When NOT to use this skill
- Fixed-layout multi-panel assembly (6 panels A–F, shared legend, insets) → use `visualization/multi-panel-figures`
- Mechanism/flowchart/architecture diagrams (non-data-driven) → use `visualization/scientific-schematics`
- Paper graphical-abstract layout (abstract→layout + AI prompts) → use `visualization/scientific-schematics` (graphical-abstract mode)
- Heavy interactive dashboards → export anndata and use cellxgene/CELESTE (out of scope)

# OmicVerse Unified Plotting

**Merged from former skills**: originally heatmap / volcano-plot / specialized-omics-plots / interactive-visualization (these standalone skills no longer exist; functionality is unified under OmicVerse V2 `ov.pl.*`). **Multi-panel assembly is NOT in this skill** — for fixed-layout assembly use `visualization/multi-panel-figures`; for mechanism/flowchart/graphical-abstract use `visualization/scientific-schematics`.

`pip install omicverse` (V2). Built on matplotlib + seaborn + PyComplexHeatmap.

## 0. Initialization (required)

> **Plotting aesthetics**: publication-grade figures must follow CNS standards (300 DPI, Arial, Okabe-Ito colorblind palette, vector PDF). See `references/figure_aesthetics.md` — **read before plotting**.

```python
import omicverse as ov
ov.plot_set()   # Global: fonts, sizes, dpi, default palette, vector-friendly pdf rendering
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Publication-grade supplements not covered by ov.plot_set() (required for CNS):
plt.rcParams.update({
    'figure.dpi': 300, 'savefig.dpi': 300,        # default 100 is insufficient
    'savefig.bbox': 'tight',                       # trim margins (required for PPT embedding)
    'pdf.fonttype': 42, 'ps.fonttype': 42,         # TrueType embedding (editor-editable)
    'font.family': 'sans-serif',                   # don't write 'Arial' directly: garbled with Chinese
    'font.sans-serif': ['SimHei', 'Microsoft YaHei', 'Arial', 'DejaVu Sans'],  # SimHei first (matplotlib sees it more reliably than YaHei)
    'axes.unicode_minus': False,                   # YaHei lacks the minus glyph
})
# Final version for an English journal: set font.sans-serif back to ['Arial']; translate Chinese legends to English

# User-selected dual-track palette (see references/figure_aesthetics.md)
# ① Discrete categorical (UMAP / clusters / spatial domains) — Morandi Nord soft
MORLANDI = ['#88C0D0','#BF616A','#A3BE8C','#D08770',
            '#B48EAD','#EBCB8B','#5E81AC','#D8DEE9']
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=MORLANDI)
# ② Continuous expression (heatmap / expression level) — Morandi-fied blue-yellow-red (low saturation, unified with discrete)
EXPR_CMAP = LinearSegmentedColormap.from_list('byr_morlandi',
    ['#5E81AC','#8FBCD4','#ECEFF4','#D08770','#9B5A5A'], N=256)
# ③ Diverging (log2FC) — blue-white-red, 0 = white midpoint
DIVERGING_CMAP = LinearSegmentedColormap.from_list('log2fc',
    ['#2C5F8D','#88C0D0','#FFFFFF','#D08770','#8B2C2C'], N=256)
# Usage: discrete → MORLANDI (auto-applied via axes.prop_cycle); heatmap → cmap=EXPR_CMAP; log2FC → cmap=DIVERGING_CMAP
```

`ov.plot_set()` + the above supplements unify the style in one call; all subsequent `ov.pl.*` and scanpy plots inherit it automatically.

## 1. Common plot types — API cheat sheet

| Plot type | API | Typical use |
|---|---|---|
| Embedding (UMAP/tSNE) | `ov.pl.embedding(adata, basis='X_umap', color=...)` | Cluster/annotation display |
| Embedding auto-labels | `ov.pl.embedding_adjust(adata, groupby=, basis=, ax=)` | Auto-place cluster labels at centroids (adjustText); no manual `ax.text` |
| Atlas-scale embedding (>100k cells) | `ov.pl.embedding_atlas(adata, basis=, color=, cmap='RdBu_r', how='eq_hist')` | Datashader density-aware render; million-cell plots stay sharp |
| Dot plot | `ov.pl.dotplot(adata, var_names=..., groupby=...)` | marker × cluster |
| Violin | `ov.pl.violin(adata, keys=..., groupby=...)` | Marker expression distribution |
| Volcano | `ov.pl.volcano(deg_df)` | DE results |
| Marker heatmap | `ov.pl.marker_heatmap(adata)` | top markers × clusters |
| Feature heatmap | `ov.pl.feature_heatmap(adata)` | Arbitrary gene heatmap |
| Generic complex heatmap | `ov.pl.complexheatmap(data)` | PyComplexHeatmap wrapper |
| Cell communication | `ov.pl.ccc_heatmap(adata)` | LR pair × cluster |
| Spatial | `ov.pl.plot_spatial(adata, color=...)` | Tissue section |
| Cell proportion | `ov.pl.cellproportion(adata)` | Sample—cluster proportion |
| Bar+dot | `ov.pl.bardotplot(adata)` | Proportion + significance |

## 2. Examples

```python
# UMAP coloring
ov.pl.embedding(adata, basis='X_umap', color='celltype', frameon='small')

# Marker dot plot
ov.pl.dotplot(adata, var_names=['CD3D','MS4A1','CD68'], groupby='celltype')

# Volcano (deg DataFrame columns must be 'log2FC' and 'qvalue'/'pvalue'; rename first if not)
ov.pl.volcano(deg_df, pval_name='qvalue', fc_name='log2FC',
              pval_threshold=0.05, fc_min=-1.5, fc_max=1.5,
              plot_genes_num=10)  # annotate top10 gene names

# Heatmap (PyComplexHeatmap wrapper)
ov.pl.marker_heatmap(adata, n_top=5, groupby='celltype')

# Cell proportion
ov.pl.cellproportion(adata, groupby='celltype', sample='sample')

# Spatial
ov.pl.plot_spatial(adata, color='leiden')
```

## 3. Palette system

**Default = user-selected Morlandi dual-track** (set in init block §0; full spec in `references/figure_aesthetics.md` §3):
- Discrete categorical → `MORLANDI` (8 colors, soft Nord)
- Sequential expression → `EXPR_CMAP` (blue-yellow-red, low-saturation)
- Diverging log2FC → `DIVERGING_CMAP` (blue-white-red)

**omicverse native palettes** (alternatives; full hex + usage in `references/figure_aesthetics.md` §7):

```python
ov.pl.sc_color           # 28-color default cycle (first '#1F577B'); omicverse signature
ov.pl.red_color          # 10-shade single-hue (also green/orange/blue/purple)
ov.pl.optim_palette(adata, groupkey='celltype')  # 28 or 112 (spaco) auto-pick by #categories
ov.pl.get_forbidden()    # 384 traditional Chinese colors (oriental aesthetic)
```

> **Rule**: ≤28 categories → `sc_color` or Morlandi; **>28 → let `optim_palette` auto-expand to 112** (never force `sc_color` on 50 clusters — it cycles and collides).

## 4. Light multi-panel composition

> **Full layout guide**: `references/figure_layout.md` — covers omicverse's 5 signature decisions, multi-gene matrix defaults, font-size scaling, panel labels (A/B/C), shared legend, 5 composite templates. Read it before assembling any composite.

omicverse's composition philosophy: **clean single cells × N + external shared legend** (not fancy grids). Every `ov.pl.*` accepts `ax=`; make cells via `plt.subplots`, pass `ax=`, `show=False`.

```python
# Two-panel side-by-side
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
ov.pl.embedding(adata, basis='X_umap', color='leiden',   ax=axes[0], show=False, frameon='small')
ov.pl.embedding(adata, basis='X_umap', color='celltype', ax=axes[1], show=False, frameon='small')
plt.savefig('fig.pdf', bbox_inches='tight')   # omicverse style: tight, no tight_layout()
```

### Multi-gene matrix (use built-in — don't hand-write GridSpec)
```python
ov.pl.embedding(adata, basis='X_umap',
                color=['CD3D','CD4','CD8A','MS4A1','CD14','NCAM1'],  # 6 genes
                ncols=3, frameon='small',
                cmap=ov.pl.get_cmap_seg(),   # segmented cmap (omicverse-recommended)
                vmin=0, vmax=3,              # UNIFIED range — critical for comparability
                show=False)
```

### omicverse's only built composite — `embedding_celltype` (UMAP + side lollipop)
```python
fig, (ax1, ax2) = ov.pl.embedding_celltype(
    adata, figsize=(7,4), basis='X_umap', celltype_key='clusters')
```

### Composite font rule
Keep ONE global `fontsize=` via `ov.ov_plot_set(fontsize=12)`; scale via figsize, not per-axis fonts. Relative hierarchy: title≈axis≈tick=F, legend=0.92F, panel letter=1.3F bold.

> For complex fixed layouts (6 panels ABCDEF, shared legend, insets) use `visualization/multi-panel-figures` (PIL/GridSpec).

## 5. Interactive exploration (light)

`ov.pl.*` is static by default; for quick interactivity use `ov.pl.embedding(..., interactive=True)` (plotly backend). **Heavy interactive dashboards should still export anndata and use cellxgene/CELESTE** — out of scope.

## Pre-Output Checklist (must pass before exporting a figure)
- [ ] Numerical integrity: each quantitative plot retains N / statistical test / error bars
- [ ] Axis labels / legend / colorblind-friendly: axes have labels and units, legend is self-contained, palette is colorblind-safe (avoid pure red-green)
- [ ] Citation support: clearly indicate which figure / statistic supports the main conclusion
- [ ] Avoid speculation: when no significant difference, write "No significant effect"; don't fabricate a story
- [ ] Correlation ≠ causation: use "associated with"; regulates/causes requires experimental evidence
- [ ] Run postcheck.py ✅

## Prerequisites (where inputs come from)

- **Analyzed AnnData** (with UMAP/clustering/annotation/DE) → from `single-cell/omicverse-pipeline` / `spatial/omicverse-spatial` / `general-bio/omicverse-bulk`
- **DE table / marker table** → from each analysis skill's `rank_genes_groups` or pseudobulk DE output
- **Spatial slice coordinates** → `adata.obsm['spatial']` + `uns['spatial']` H&E
- **Must read before any plotting** `references/figure_aesthetics.md` (dual-track palette + Chinese fallback + title/legend non-overlap)

## Decision cheat sheet: when to leave this skill

| Need | Go to |
|---|---|
| 6-panel composition / shared legend | `visualization/multi-panel-figures` |
| Mechanism / flowchart / architecture diagram | `visualization/scientific-schematics` |
| Graphical Abstract | `visualization/scientific-schematics` (graphical-abstract mode) |

## Key pitfalls

- Run `ov.plot_set()` before any ov.pl call; otherwise fonts/dpi are inconsistent and multi-panel assembly misaligns.
- `ov.pl.volcano` input is a DataFrame with columns `log2FC` and `pvalue`/`padj`; rename first if naming differs.
- `complexheatmap` equals PyComplexHeatmap; multi-group annotation via `row_split`/`col_split`, not seaborn's row_cluster.
- Export vector figures as `.pdf` (paper) / `.svg` (PPT re-editing); `dpi=300` only needed for raster output.
- matplotlib Chinese/special characters need extra font config; `ov.plot_set()` defaults to Western fonts — manually set `plt.rcParams['font.family']` when Chinese is present.
- **`ov.plot_set()` does NOT set `pdf.fonttype=42`** (verified in source `_plot_backend.py`) — manually add it, else PDF embeds Type-3 fonts (journals reject). See `references/figure_aesthetics.md` §6.
- **`ov.plot_set()` auto-downloads Arial from GitHub** (`font_path='arial'` default) — in offline/air-gapped envs it fails; use `ov.style(font_path=None)` or pass a local TTF path.
- **>28 categories**: do NOT force `palette=sc_color` on 50-cluster plots — it cycles and collides. Let `optim_palette` auto-expand to 112 colors, or split into multiple panels.
- **>100k cells on embedding**: regular `ov.pl.embedding` scatters into a blob — use `ov.pl.embedding_atlas` (Datashader density-aware render) instead.
- **Avoid manual `ax.text` for cluster labels**: use `ov.pl.embedding_adjust` (adjustText auto-placement at centroids) — manual labels overlap and drift when data changes.
- **`frameon='small'` is omicverse's signature** (L-shaped axes) — don't override back to `frameon=True` (full box) unless reproducing scanpy exactly. See `references/figure_aesthetics.md` §8.
