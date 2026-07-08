---
name: bio-spatial-transcriptomics-spatial-deconvolution
description: Visium 等多细胞 spot 的细胞类型去卷积。基于 OmicVerse V2 的 ov.space.Deconvolution（统一封装 cell2location/Tangram/RCTD/Starfysh/flashdeconv 五法）从 scRNA-seq 参考集推断 spot 细胞构成。当用户要做去卷积、estimate cell type composition、spot 细胞类型比例时触发。
---

## When NOT to use this skill
- Spatial data ready for spatial domains/SVG/communication (no cell composition estimation needed) → use `spatial/omicverse-spatial`
- High-resolution platforms (Xenium/Stereo-seq, already single-cell grade, no deconvolution needed) → use `spatial/multiomics`
- Spatial proteomics cell typing (CODEX/IMC) → use `spatial/proteomics` (scimap gating, not deconvolution)
- Conventional single-cell (not spatial spots) cell-type proportion comparison → use `single-cell/scop` (`RunProportionTest`/`RunMilo`) or omicverse

# Spatial Deconvolution

`pip install omicverse` (V2). OmicVerse unifies 5 mainstream deconvolution methods under `ov.space.Deconvolution`.

## 0. Verified environment (2026-07)

| Package | sc env version | Status |
|---|---|---|
| omicverse | 2.2.3 | ✅ |
| cell2location | 0.1.5 | ✅ coexists with omicverse (revises earlier "needs separate env" verdict) |
| scvi-tools | 1.4.2 | ✅ |
| tangram | 1.0.4 | ✅ |
| liana / cellrank | 1.7.3 / 2.0.7 | ✅ |

> **Important correction** (2026-07): earlier omicverse versions pinned anndata 0.10.x, conflicting with cell2location dependencies. **omicverse 2.2.3 resolves this conflict**; cell2location is directly usable in the `sc` env, **no separate c2l env required**. If your env still reports an anndata conflict, upgrade omicverse to ≥2.2.x.

## 1. Five-method main entry (`ov.space.Deconvolution`)

Source-verified (omicverse 2.2.3): `deconvolution(method=...)` supports 5 values.

| `method` | Algorithm | Best for | GPU |
|---|---|---|---|
| `'cell2location'` | cell2location (Bayesian) | **default baseline**; most accurate with good reference; top-tier in 2025 benchmark | strongly recommended |
| `'Tangram'` | Tangram (optimal transport) | fast, smaller reference; no scvi dependency | optional |
| `'RCTD'` | RCTD (R/spacexr wrapper) | doublet mode is its strength | none (CPU) |
| `'Starfysh'` | Starfysh | needs anchor-gene priors | optional |
| `'flashdeconv'` | flashdeconv | fast exploration | — |

```python
import omicverse as ov
# reference (cell_type annotated) + spatial data
deconv = ov.space.Deconvolution(adata_sp=adata_visium, adata_sc=adata_ref)
deconv.preprocess_sc(celltype_key_sc='cell_type')   # reference preprocessing
deconv.preprocess_sp()                                # spatial preprocessing
deconv.deconvolution(method='cell2location',
                     celltype_key_sc='cell_type',
                     N_cells_per_location=10,         # expected cells per spot
                     detection_alpha=200)
# result in adata_sp.obsm (per-spot × cell_type abundance matrix)
```

### cell2location staged (finer control)

To train reference signature and spatial decomposition separately (default `deconvolution()` does both in one call, but staged allows tuning):

```python
deconv.cell2location_inference(sample_kwargs={'num_samples': 1000})
# or load a trained model: deconv.load_cell2location_model('path/to/c2l_model')
```

## 2. Selection decision table

| Scenario | First-choice method | Reason |
|---|---|---|
| Conventional Visium + good scRNA reference | **`'cell2location'`** | most robust in 2025 benchmark |
| Small reference / no GPU | **`'Tangram'`** | fast, CPU-runnable |
| Detect intra-spot doublets | **`'RCTD'`** (doublet mode) | RCTD's specialty |
| Anchor-gene priors available | **`'Starfysh'`** | inject priors |
| Exploration, speed priority | **`'flashdeconv'`** | lightweight |

## 3. Quality assessment (required; run postcheck)

Deconvolution results vary; **unvalidated abundance maps mislead downstream**. For each cell_type, compute marker-proportion correlation:

```python
marker_genes = {'T_cell': ['CD3D','CD3E'], 'Macrophage': ['CD68','CD14']}
for ct, markers in marker_genes.items():
    available = [m for m in markers if m in adata_sp.var_names]
    if available:
        marker_expr = adata_sp[:, available].X.mean(axis=1).flatten()
        ct_prop = proportions[:, cell_types.index(ct)]
        corr = np.corrcoef(marker_expr, ct_prop)[0,1]
        print(f'{ct}: r={corr:.3f}')   # r>0.3 considered trustworthy
```

> After finishing, run `scripts/postcheck.py --type deconv <result.h5ad>`: checks each cell type has a quality-assessment column and whether r is too low.

## 4. Visualization (see `visualization/omicverse-plotting`)

```python
# one spatial section per cell type
for ct in ['T_cell','Macrophage','Epithelial']:
    adata_sp.obs[f'{ct}_prop'] = proportions[:, cell_types.index(ct)]
    sc.pl.spatial(adata_sp, color=f'{ct}_prop', cmap='Reds', vmin=0, vmax=1)

# Pie chart per spot (advanced, all cell types in one figure)
# see references/deconv_visualization.md
```

## 5. Multi-method consensus (recommended; avoids single-method bias)

Different methods can diverge sharply. **For key findings (cell-fate conclusions) run at least 2 methods**; commit only for cell types where cell2location + Tangram correlate well:

```python
import numpy as np
for i, ct in enumerate(cell_types):
    c2l = adata_sp.obsm['c2l_prop'][:, i]
    tg = adata_sp.obsm['tg_prop'][:, i]
    r = np.corrcoef(c2l, tg)[0,1]
    print(f'{ct}: cell2location vs tangram r={r:.3f}')
```

## 6. When to fall back to native cell2location

Deep tuning not exposed by `ov.space.Deconvolution`:
- custom RegressionModel `max_epochs`, `node_b1`, `node_b2` network structure
- custom `filter_genes` thresholds (`cell_count_cutoff`, `nonz_mean_cutoff`)
- direct manipulation of `mod.export_posterior()` `ref_sig` (`varm['means_per_cluster_mu_fg']`)
- joint cross-sample training (multi-section)

```python
# fall back to native cell2location
from cell2location.models import RegressionModel, Cell2location
from cell2location.utils.filtering import filter_genes
selected = filter_genes(adata_ref, cell_count_cutoff=5, cell_percentage_cutoff2=0.03,
                        nonz_mean_cutoff=1.12)
adata_ref = adata_ref[:, selected].copy()
RegressionModel.setup_anndata(adata_ref, labels_key='cell_type')
mod = RegressionModel(adata_ref); mod.train(max_epochs=250, use_gpu=True)
adata_ref = mod.export_posterior(adata_ref, sample_kwargs={'num_samples':1000})
ref_sig = adata_ref.varm['means_per_cluster_mu_fg']
# then build the Cell2location spatial model; see official cell2location tutorial
```

## 7. RCTD / SPOTlight (R path)

If you prefer R/spacexr (RCTD's native env), use `single-cell/scop` `RunRCTD` — smoother:
- RCTD (spacexr): doublet mode detects two cells per spot
- SPOTlight: NMF-based, old but usable
- CARD (2022+): R package with spatial prior

## Output keys quick-reference

| Location | Key | Meaning |
|---|---|---|
| `adata_sp.obsm` | `q05_cell_abundance_w_sf` (cell2location) | per-spot cell-type abundance |
| `adata_sp.obsm` | `tangram_ct_pred` (Tangram) | per-spot cell-type proportion |
| `adata_sp.obs` | `dominant_cell_type` (user-computed) | dominant cell type per spot |

## Prerequisites (where it comes from)

- **Spatial data loading/preprocessing** → `spatial/omicverse-spatial` (`ov.io.read_visium` + QC)
- **Single-cell reference annotation** → `single-cell/omicverse-pipeline` (reference must be annotated with `cell_type` first)
- **layers['counts']** must exist in both reference and spatial data (cell2location trains on raw counts)

## When to leave this skill (where to go)

- Deconvolution result visualization → `spatial/omicverse-spatial` (`ov.pl.plot_spatial`) or `visualization/omicverse-plotting`
- Compose publication-grade figure → `visualization/multi-panel-figures`
- Cross-sample cell-type proportion comparison → `single-cell/scop` (`RunProportionTest`/`RunMilo`) or omicverse
- Write Methods describing the deconvolution workflow → `presentation/methods-writer`
- **After finishing, run `scripts/postcheck.py --type deconv <result.h5ad>` to verify the quality-assessment column**

## Key pitfalls

- **omicverse already wraps cell2location** — don't reinvent in raw `cell2location` API unless deep tuning is needed (see Section 6)
- **The reference is a strong prior**: must match tissue/state and cover target cell types, otherwise it confidently fabricates proportions (meta-methodology principle ①)
- **`N_cells_per_location` affects results**: ~10-20 for Visium, adjust by tissue density; too small overestimates rare types
- **Multi-method consensus > single method**: directional conclusions ("X enriched in Y region") need at least 2 methods for cross-check
- **Quality assessment is mandatory**: cell types with r<0.3 are untrustworthy — likely reference mismatch or non-specific markers
- **GPU strongly recommended**: cell2location CPU training is 10-50× slower; use Tangram without GPU
- **Reference cell-type annotation must be reliable** — bad annotation breaks deconvolution end-to-end (garbage in, garbage out)
