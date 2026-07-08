---
name: omicverse-spatial-pipeline
description: 空间转录组全流程（IO→空间邻域→QC→空间域→SVG→通讯→可视化）基于 OmicVerse V2 统一 API，覆盖 Visium/Xenium/Nanostring/VisiumHD。一个 import omicverse as ov 完成 90% 常规空转分析。
---

## When NOT to use this skill
- Spot/cell deconvolution (cell2location/RCTD/Tangram to estimate cell composition) → use `spatial/deconvolution` (`ov.space.Deconvolution` wraps 5 methods)
- High-resolution platforms (Stereo-seq / Slide-seq / Visium HD subcellular) + cellpose segmentation → use `spatial/multiomics`
- Spatial proteomics (CODEX/IMC/MIBI) → use `spatial/proteomics` (scimap, not spatial transcriptomics)
- Conventional single-cell (no spatial coordinates) → use `single-cell/omicverse-pipeline`

# OmicVerse Spatial Transcriptomics Pipeline

**Merged from former skills**: original preprocessing / data-io / domains / neighbors / statistics / visualization / communication / image-analysis (these standalone skills no longer exist; functionality unified in OmicVerse V2). **Deconvolution is NOT in this skill** — cell2location/RCTD etc. go to `spatial/deconvolution`. High-resolution platforms: see `spatial/multiomics`; spatial proteomics: see `spatial/proteomics`.

`pip install omicverse` (V2). Built on scanpy/squidpy/anndata.

## 0. Initialization

```python
import omicverse as ov
ov.plot_set()
```

## 1. Data IO (by platform)

> **Network reachability, tested tiers** (2026-07, restricted-network environment):
> | Source | Reachability | Usage |
> |---|---|---|
> | `sc.datasets.visium_sge(sample_id)` | ✅ stable | 10x official CDN; first choice for public Visium samples |
> | `sq.datasets.visium_hne_adata()` | ❌ 403 | squidpy self-hosted CDN; unreachable on restricted networks |
> | `ov.datasets.hg_forebrain_glutamatergic()` | ❌ fails | loom download error |
> | Local spaceranger output | ✅ most reliable | `squidpy.read_visium('dir/')` |
> | GEO direct link (h5ad) | ⚠️ network-dependent | `sc.read_h5ad()` |
>
> **Strategy**: prefer `sc.datasets.visium_sge`; on failure, manually download spaceranger output from GEO/10x and read with `sq.read_visium()`. Same for single-cell references — prefer local; when CDN is unreliable, fetch raw fastq/counts via GEOparse and process yourself.

```python
# Standard Visium
adata = ov.space.read_visium_10x('visium_sample/')

# Next-gen platforms
adata = ov.io.read_visium_hd('hd_sample/')     # 8μm/2μm bin
adata = ov.io.read_xenium('xenium_out/')       # subcellular resolution
adata = ov.io.read_nanostring('cosmx/')        # GeoMx/CosMx
```

| Platform | Function | Resolution |
|---|---|---|
| Visium | `ov.space.read_visium_10x` | 55μm spot |
| Visium HD | `ov.io.read_visium_hd` | 2-8μm bin |
| Xenium | `ov.io.read_xenium` | subcellular |
| Nanostring | `ov.io.read_nanostring` | single-cell grade |

## 2. QC + preprocessing

```python
ov.pp.qc(adata, doublets_method='scrublet')   # same entry as single-cell
ov.pp.preprocess(adata, mode='shiftlog', n_HVGs=3000)
ov.pp.scale(adata); ov.pp.pca(adata, n_pcs=50)
adata.layers['counts']  # keep; required by deconvolution
```

## 3. Spatial neighbor graph (core)

```python
ov.pp.spatial_neighbors(adata, n_neighbors=6, method='knn')
# or coordinates with Delaunay: method='delaunay' (Visium hex grid: knn is fine)
# outputs adata.obsp['spatial_connectivities'] / ['distances']
```

All downstream SVG / spatial domain / communication methods depend on this graph.

## 4. Spatial domains / tissue regions

```python
# STAGATE (graph autoencoder, most common, robust to noise)
ov.space.pySTAGATE(adata)
ov.pp.neighbors(adata, use_rep='X_STAGATE'); ov.pp.umap(adata)
ov.pp.leiden(adata, resolution='auto')

# Alternative algorithms
ov.space.GraphST(adata)    # graph contrastive learning, better for large data
ov.space.BANKSY(adata)     # neighborhood-aware, sharp boundaries
ov.space.BINARY(adata)     # self-supervised, zero-shot
```

Decision: default STAGATE; large samples (>1M spot) → GraphST; sharp tissue boundaries → BANKSY; **cell-type-aware domains with speed → MENDER** (2024, Nat Commun; fast, cell-type-aware); **multi-omics (e.g. spatial RNA+ATAC) → SpatialGlue** (2024, Nat Methods; dual-attention multimodal domain).

> **2025 benchmark consensus** (Genome Biol / iMeta, 26 methods / 63 sections): no single SOTA; results vary by tissue/platform. **Run at least 2 methods for key domain conclusions**; commit only when directions agree.

## 5. Spatially variable genes (SVG)

```python
ov.space.spatial_autocorr(adata, mode='moran')   # Moran's I; mode='geary' for Geary's C
# adds to adata.var: moranI, moranI_pval, spatial_high_variable
svg = adata.var.query('moranI > 0.3').index
```

> **Windows + squidpy gotcha**: when using `squidpy.gr.spatial_autocorr`, `n_perms>=1` triggers multiprocessing that hangs under stdin/heredoc mode. **Write the script to a `.py` file** and run `python script.py`, wrapped in `if __name__=='__main__':`. Also `sq.pl.spatial_scatter(save='x.png')` writes to a `figures/` subdir, not the current dir. 10x Visium data often has duplicate var_names — first run `adata = adata[:, ~adata.var_names.duplicated()].copy()`.

## 6. Spatial cell-cell communication

```python
# Build spatial network (ligand-receptor + spatial neighbors)
ov.space.Cal_Spatial_Net(adata)
# Inference
ov.space.COMMOT(adata)   # anisotropic OT communication, mainstream spatial choice
# Alternatives: LIANA+ (spatial mode, unified framework), DeepTalk (single-cell-res spatial CCC)
```

> **Spatial CCC ranking (2024-2026)**: **COMMOT** (OT-based) and **LIANA+ spatial mode** (Mol Syst Biol 2024, 251+ citations, unified framework that internally runs multiple methods) are the SOTA for spatially-aware communication. **CellChat spatial / CellPhoneDB v5 are NOT spatial-native** — they were built for dissociated scRNA-seq; using them on spatial data is fallback only. **DeepTalk** (Nat Commun 2024, 93+ citations) is a newer option for single-cell-resolution spatial CCC. The first systematic spatial-CCC benchmark (bioRxiv 2026.05.19.724475) confirmed no single winner — run ≥2 methods and report consensus.

## 7. Visualization (see visualization/omicverse-plotting)

```python
ov.pl.plot_spatial(adata, color='leiden')           # tissue section clusters
ov.pl.plot_spatial(adata, color='moranI_top_genes') # SVG expression
ov.pl.embedding(adata, basis='X_umap', color='leiden')
```

H&E / IF image analysis: ov V2 integrates basic registration; complex registration (StarFusion/SpacesID) still possible via `squidpy.pl.spatial_scatter` + the `adata.uns['spatial']` image stack returned by `ov.io.read_*`.

## Prerequisites (where it comes from)

- **Raw spatial data** (spaceranger / star-solo / SAW output) → contains `adata.obsm['spatial']` coordinates + `uns['spatial']` H&E images
- **`layers['counts']` must be preserved** — SVG/deconvolution predecessors use raw counts
- **Spatial neighbor graph**: `ov.pp.spatial_neighbors` must run before spatial domains/SVG/communication (all spatial methods consume this graph)
- **High-resolution platforms** (Stereo-seq/Visium HD) → `spatial/multiomics` (cellpose segmentation)
- **Spot cell composition estimation** → `spatial/deconvolution`

## Decision quick-reference: when to leave this skill

| Need | Go to |
|---|---|
| Spot/cell deconvolution (cell2location etc.) | `spatial/deconvolution` |
| Stereo-seq / high-resolution platform workflow | `spatial/multiomics` |
| Spatial proteomics (CODEX/IMC/MIBI) | `spatial/proteomics` |

## Key pitfalls

- `ov.pp.spatial_neighbors` must run before spatial domains/SVG/communication — all spatial methods consume this graph.
- Default n_neighbors differs by platform: Visium hex grid uses 6; Xenium/HD try 4-8.
- SVG uses Moran's I, threshold starts at 0.3; too strict misses weak-spatial-pattern genes.
- Before deconvolution, confirm `adata.layers['counts']` was not overwritten by normalization.
- Visium HD uses `read_visium_hd`; do not downgrade to `read_visium_10x` — bin metadata is lost.
