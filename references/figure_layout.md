# Figure Layout & Composition (omicverse-style)

> Multi-panel figure composition learned from omicverse 2.2.3 source + official plotting tutorials. The philosophy is *not* about layout APIs — it's about five visual decisions that make figures look clean even with plain matplotlib.
>
> **Companion files**: `figure_aesthetics.md` (technical spec: color/font/non-overlap), `figure_design.md` (what chart type + information hierarchy + statistics visualization). Three references together cover CNS-grade plotting end-to-end.

## The omicverse composition philosophy

**omicverse almost never hand-crafts fancy GridSpec layouts.** Its real approach:
1. Every `ov.pl.*` function accepts `ax=` → make single cells via `plt.subplots`, pass `ax=`, set `show=False`
2. Each subplot auto-applies omicverse's five signature decisions (below) → looks clean by default
3. Multi-panel happens in only three built-ins: `embedding(color=[...])`, `embedding_celltype` (UMAP + lollipop), and side-by-side volcanoes (via manual gridspec — `ov.pl.stacking_vol` does NOT exist in omicverse 2.2.3)
4. Cross-heterogeneous composition (UMAP + dotplot + violin) → hand-write GridSpec, but keep the five signatures

So "omicverse-style composite" = **clean single cells × N + external shared legend/colorbar**, not fancy grids.

## The five signature decisions (preserve these, don't override back to scanpy)

| # | Decision | omicverse default | Why it's cleaner than scanpy |
|---|---|---|---|
| 1 | **`frameon='small'`** | L-shaped axes (only left+bottom, mini scale bar) | Emphasizes data, not the box |
| 2 | **Grid off** | `axes.grid=False` (plot_set overrides scanpy's True at the end) | Less visual noise |
| 3 | **Bold legend** | `legend_fontweight='bold'` | Readable at slide distance |
| 4 | **Mini colorbar** (continuous) | Manual bar at right, height = axis × 0.3, only 3 ticks | Compact, doesn't dominate |
| 5 | **Cluster names on plot** | `embedding_adjust` (adjustText) places labels at centroids | No external legend needed for UMAP |

Source: `omicverse/pl/_single.py`, `_embedding.py`, `_plot_backend.py` (verified line by line).

## Spacing & sizing defaults (from source, not invented)

### Multi-gene embedding matrix (`ov.pl.embedding(color=[...])`)
When you pass a list of genes, omicverse builds the grid internally:
- `ncols=4` (override with `ncols=3` for 2×3)
- `hspace=0.25`
- `wspace` = auto-computed as `0.75/figsize[0] + 0.02`
- Single cell `figsize=(4,4)`; whole figure = `ncols×4×(1+wspace)` × `nrows×4`
- **Always pass unified `vmin`/`vmax`** so panels are comparable
- Each panel auto-gets a mini colorbar (no shared one)

```python
ov.pl.embedding(adata, basis='X_umap',
                color=['Sox4','Sox11','Neurod1','Tubb3','Dcx','Map2'],  # 6 genes
                ncols=3, hspace=0.25, frameon='small',
                cmap='Reds',   # omicverse has no get_cmap_seg(); use standard cmap
                vmin=0, vmax=3,               # UNIFIED range — critical for comparability
                show=False)
```

### `embedding_celltype` (UMAP + side lollipop) — omicverse's only built composite
Uses `plt.GridSpec(10,10)`:
```python
fig, (ax1, ax2) = ov.pl.embedding_celltype(
    adata, figsize=(7,4), basis='X_umap',
    celltype_key='clusters',
    celltype_range=(1,10),     # lollipop rows (default 2,9)
    embedding_range=(4,10))    # UMAP columns (default 3,10)
```

### Do NOT use `subplots_adjust`
omicverse tutorials never call it — each function computes its own figsize and relies on `bbox_inches='tight'` at save. If you hand-write a composite, set figsize + wspace/hspace in GridSpec and let `tight` finish; don't fight it with `subplots_adjust`.

## Font-size scaling for composites

omicverse's rule: **keep rcParams font globally consistent, scale via figsize — not per-axis font sizes.** Set one `fontsize=` value for the whole figure.

| Composite scale | `ov.ov_plot_set(fontsize=)` | Per-cell figsize | Note |
|---|---|---|---|
| Single (main figure) | 14 | (4,4) | omicverse default |
| 2 panels (side-by-side) | 12 | (4,4) each | slightly reduced |
| 4 panels (2×2) | 11–12 | (3.5,3.5) each | whole ~7×7 |
| 6 panels (2×3 gene matrix) | 10–11 | (3,3) each | use `embedding(color=[...], ncols=3)` |
| 8+ panels | 10 | (3,3) | ticks/legend follow rcParams |

Relative hierarchy (keep this when scaling): **title ≈ axis ≈ tick = F**; **legend = 0.92F**; **panel letter (A/B/C) = 1.3F bold**; **mini colorbar ticks ≈ 0.7F**.

## Panel labels (A/B/C/D) — omicverse has NO API for this

**Important negative finding**: `ov.pl.embedding_adjust` / `gen_mpl_labels` sound like panel-label functions but **actually place cluster names on the UMAP** (adjustText at centroids), NOT A/B/C/D letters. Do not search for `ov.pl.add_labels` — it does not exist.

Use the standard inline `ax.text` (CNS/Cell convention, works with omicverse palettes):
```python
for ax, label in zip([ax1, ax2, ax3], ['A','B','C']):
    ax.text(-0.08, 1.05, label,
            transform=ax.transAxes, fontsize=16, fontweight='bold',
            va='top', ha='right')
```

## Shared legend / colorbar (cross-heterogeneous figures)

omicverse has **no built-in shared legend across heterogeneous panels** (UMAP + dotplot + violin). Use standard matplotlib:

```python
# Shared categorical legend (cell-type colors) — external, figure-level
from matplotlib.lines import Line2D
palette = dict(zip(adata.obs['clusters'].cat.categories, ov.pl.sc_color))
handles = [Line2D([0],[0], marker='o', ls='', color=c, markersize=8, label=k)
           for k, c in palette.items()]
fig.legend(handles=handles, bbox_to_anchor=(1.01, 0.5),
           loc='center left', frameon=False, fontsize=10, title='Cell type')
fig.savefig('fig.pdf', bbox_inches='tight')   # tight makes room for the legend
```

For continuous colorbars in composites: omicverse prefers **per-panel mini colorbars** (auto from `embedding`); only share if all panels use identical vmin/vmax/cmap.

## Five composite templates (with real figsize + gridspec values)

### Template A — UMAP + dotplot + violin trio (marker overview)
omicverse has no built-in trio; hand-write GridSpec. The three panels have different natural widths, so use `width_ratios`:

```python
fig = plt.figure(figsize=(13, 4.5))
gs = gridspec.GridSpec(1, 3, figure=fig, wspace=0.35, width_ratios=[1, 1.3, 1.2])
axA = fig.add_subplot(gs[0,0])
ov.pl.embedding(adata, basis='X_umap', color='clusters', frameon='small', ax=axA, show=False)
axB = fig.add_subplot(gs[0,1])
ov.pl.dotplot(adata, markers, groupby='clusters', ax=axB, show=False)
axC = fig.add_subplot(gs[0,2])
ov.pl.violin(adata, keys='CD3D', groupby='clusters', ax=axC, show=False)
# panel letters + shared legend (see above sections)
```

### Template B — Multi-gene expression matrix (use built-in)
```python
ov.pl.embedding(adata, basis='X_umap',
                color=['gene1','gene2','gene3','gene4','gene5','gene6'],
                ncols=3, frameon='small', cmap='Reds',
                vmin=0, vmax=3, show=False)   # unified range
```

### Template C — Proportion bar + UMAP + heatmap
omicverse proportion plots are naturally narrow (`figsize=(1.5,4)` vertical bar), good as left column of a composite:

```python
fig = plt.figure(figsize=(11, 4.5))
gs = gridspec.GridSpec(1, 3, width_ratios=[0.6, 1, 1.4], wspace=0.3)
axA = fig.add_subplot(gs[0,0])   # narrow proportion bar
ov.pl.cellproportion(adata, celltype_clusters='clusters', groupby='condition',
                     ax=axA, legend=False)
axB = fig.add_subplot(gs[0,1])
ov.pl.embedding(adata, basis='X_umap', color='clusters', frameon='small', ax=axB, show=False)
axC = fig.add_subplot(gs[0,2])
ov.pl.marker_heatmap(adata)   # or complexheatmap
```

### Template D — Side-by-side volcanoes (manual gridspec; no built-in)
> `ov.pl.stacking_vol` does NOT exist in omicverse 2.2.3. Use manual gridspec with `ov.pl.volcano` per panel.
```python
fig, axes = plt.subplots(1, n_datasets, figsize=(5*n_datasets, 4))
for ax, (name, df) in zip(axes, data_dict.items()):
    ov.pl.volcano(df, ax=ax, show=False, title=name)
```

### Template E — Spatial sections multi-panel (hand-write)
omicverse has no built-in spatial multi-panel; hand-write GridSpec, each cell `ax=` to `ov.pl.plot_spatial` (NOT `ov.pl.space` — that doesn't exist) / `sq.pl.spatial_scatter`, unified `vmin/vmax`, shared colorbar on the right.

## Self-check before exporting a composite

- [ ] Every panel has `frameon='small'` (not full box) — unless reproducing scanpy exactly
- [ ] Continuous panels share `vmin`/`vmax` (or each has its own mini colorbar, labeled)
- [ ] Panel letters (A/B/C) added via inline `ax.text`, NOT via non-existent `ov.pl.add_labels`
- [ ] Cluster labels on UMAP via `embedding_adjust`, NOT manual `ax.text`
- [ ] One global `fontsize=` set via `ov.ov_plot_set(fontsize=...)` — no per-axis font fiddling
- [ ] `bbox_inches='tight'` at save (no `subplots_adjust` fighting)
- [ ] Shared legend external (figure-level), not duplicated per panel
- [ ] Titles have `pad` (see `figure_aesthetics.md` §4) — no title/data overlap
