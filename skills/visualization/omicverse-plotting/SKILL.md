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
    'font.sans-serif': ['Microsoft YaHei', 'Arial', 'DejaVu Sans'],  # YaHei as Chinese fallback
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

```python
ov.pl.palette   # Built-in: red_blue, scgpt, agora, etc.
ov.pl.embedding(adata, basis='X_umap', color='celltype',
                palette=ov.pl.palette['red_blue'])
# Custom continuous: cmap='viridis'/'RdBu_r'
```

## 4. Light multi-panel composition

```python
# ov.pl returns matplotlib axes; compose manually
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
ov.pl.embedding(adata, basis='X_umap', color='leiden', ax=axes[0], show=False)
ov.pl.embedding(adata, basis='X_umap', color='celltype', ax=axes[1], show=False)
plt.tight_layout(); plt.savefig('fig.pdf')
```

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
