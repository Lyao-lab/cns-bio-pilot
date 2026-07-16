# OmicVerse V2 API Quick Reference & Task Mapping

`pip install omicverse`. This file maps tasks → APIs; for full usage see the corresponding `skills/*/SKILL.md`.

## Basic Setup

```python
import omicverse as ov
ov.plot_set()                          # init unified style (required)
# Large data (million cells):
adata = ov.read('data.h5ad', backend='rust')   # AnnDataOOM, ~170× memory savings
# Regular data:
adata = ov.read('data.h5ad')
```

## Single-cell Task Mapping (see skills/single-cell/omicverse-pipeline)

| Task | omicverse API | Standalone tool it replaces |
|---|---|---|
| QC (mito/UMI/gene count) | `ov.pp.qc(adata, thresh={'mito_perc':20,'nUMIs':500,'detected_genes':250}, doublets_method='scrublet', batch_key='sample', filter_doublets=True)` | scanpy.pp.calculate_qc_metrics |
| Doublet detection | same `doublets_method='scrublet'\|'scdblfinder'\|'doubletfinder'` | scrublet/scDblFinder/DoubletFinder |
| Normalization | `ov.pp.preprocess(adata, mode='shiftlog'\|'pearson', n_HVGs=2000)` | scanpy normalize_total/log1p, scTransform |
| Recover raw counts | `ov.pp.recover_counts(adata)` | — |
| Scale (does not mutate X) | `ov.pp.scale(adata)` → stored in `layers['scaled']` | scanpy.pp.scale |
| PCA | `ov.pp.pca(adata, layer='scaled', n_pcs=50)` | scanpy.pp.pca |
| Neighbor graph | `ov.pp.neighbors(adata)` | scanpy.pp.neighbors |
| UMAP/tSNE | `ov.pp.umap(adata)` / `ov.pp.tsne(adata)` | scanpy.tl.umap |
| Clustering | `ov.pp.leiden(adata, resolution='auto')` (auto picks resolution) | scanpy.tl.leiden |
| Auto resolution | `ov.single.auto_resolution(adata)` | — |
| Cell cycle | `ov.pp.score_genes_cell_cycle(adata, species='human')` | scanpy.tl.score_genes_cell_cycle |
| Batch correction Harmony | `ov.single.batch_correction(adata, method='harmony')` | harmonypy |
| Batch correction scVI | `ov.single.batch_correction(adata, method='scvi')` | scvi-tools |
| Marker genes | `ov.single.find_markers(adata, method='wilcoxon'\|'t-test'\|'cosg')` | scanpy.tl.rank_genes_groups |
| Annotation (no reference) | `ov.single.pySCSA(adata)` / `MetaTiME` | SCSA |
| Annotation (with reference) | `ov.single.AnnotationRef(adata)` / `TOSICA` / `weighted_knn_transfer` | CellTypist |
| GPT annotation | `ov.single.gptcelltype(adata)` | GPTCelltype |
| Pseudotime / trajectory | `ov.single.Monocle(adata)` (py-monocle2, R ported) | Monocle2(R) |
| Pseudotime (others) | `Palantir` / `Slingshot` / `VIA` / `cytotrace2` | Palantir/Slingshot |
| RNA velocity | `ov.single.Velo(adata, mode='scvelo'\|'dynamo')` | scVelo (use native for deep tuning) |
| Cell-cell communication | `ov.single.run_cellphonedb_v5(adata)` / `run_liana(adata)` | CellPhoneDB/LIANA |
| GRN | `ov.single.SCENIC(adata)` | SCENIC |
| MetaCell | `ov.single.MetaCell(adata)` / `cNMF` / `SEACells` | MetaCell |
| One-shot lazy | `ov.single.lazy(adata)` | — |

## Spatial Transcriptomics Task Mapping (see skills/spatial/omicverse-spatial)

| Task | omicverse API | Standalone tool it replaces |
|---|---|---|
| Read Visium HD | `ov.io.read_visium_hd(path)` | squidpy.read_visium |
| Read Xenium | `ov.io.read_xenium(path)` | squidpy.read_xenium |
| Read NanoString | `ov.io.read_nanostring(path)` | squidpy.read_nanostring |
| Read Visium 10x | `ov.space.read_visium_10x(path)` | squidpy |
| Spatial neighbor graph | `ov.space.spatial_neighbors(adata)` (NOT `ov.pp` — verified) | squidpy.gr.spatial_neighbors |
| SVG (spatially variable genes) | `ov.space.spatial_autocorr(adata, mode='moran')` / `ov.space.moranI` | squidpy.gr.spatial_autocorr |
| Spatial domains (wrapped) | `ov.space.pySTAGATE` / `pySTAligner` / `pySpaceFlow` | STAGATE/STAligner/SpaceFlow |
| Spatial domains (standalone) | BANKSY / GraphST / BINARY / MENDER / SpatialGlue (NOT wrapped — install separately) | — |
| Spatial alignment | `ov.space.pySTAligner` / SLAT | STAligner |
| Spatial communication | `ov.space.Cal_Spatial_Net(adata)` + `create_communication_anndata` (COMMOT standalone: `pip install commot`) | COMMOT |
| Spatial tensor | `STT` (Spatial Transition Tensor) | STT |
| **Deconvolution** | `ov.space.Deconvolution` (unifies cell2location/Tangram/RCTD/Starfysh/flashdeconv) | cell2location / RCTD standalone |

## Bulk Task Mapping (see skills/general-bio/omicverse-bulk)

| Task | omicverse API | Standalone tool it replaces |
|---|---|---|
| Differential expression | `ov.bulk.pyDEG(adata)` (pyDESeq2 wrapper) | DESeq2(R) / pydeseq2 |
| Batch correction | `ov.bulk.batch_correction(adata)` | ComBat / inmoose |
| GO/KEGG enrichment | `ov.bulk.geneset_enrichment(genes)` + `geneset_plot()` | clusterProfiler(R) |
| GSEA | `ov.bulk.pyGSEA(ranked_list)` (GSEApy wrapper) | fgsea(R) / GSEApy |
| Pathway database | `ov.utils.download_pathway_database()` + `geneset_prepare()` | — |
| WGCNA | `ov.bulk.pyWGCNA(adata)` (pyWGCNA wrapper) | WGCNA(R) |
| PPI | `ov.bulk.pyPPI(genes)` + `string_interaction()` | STRINGdb(R) |
| TCGA | `ov.bulk.pyTCGA()` | TCGA biolinks(R) |
| Bulk deconvolution | `ov.bulk.Deconvolution` / Scaden / BayesPrime | CIBERSORT |

## Multi-omics Task Mapping (see skills/single-cell/omicverse-pipeline §9b)

| Task | omicverse API | Alternative standalone |
|---|---|---|
| MOFA+ (joint factor model, RNA+ATAC+protein) | `ov.single.pyMOFA(omics, omics_name)` / `ov.single.pyMOFAART(model_path)` (load pretrained) | muon / MOFA2(R) |
| RNA+ATAC regulatory GRN | `ov.single.GLUE_pair(adata_rna, adata_atac)` | GLUE standalone; SCENIC+ for enhancer-level |
| Multi-omics embedding (gene/region/cell joint space) | `ov.single.pySIMBA(adata, workdir)` | SIMBA standalone |
| Causal GRN inference | `ov.single.pyCEFCON(adata)` | CEFCON standalone |
| Metabolic flux scoring | `ov.single.Metabolism(adata)` | scMetabolism / compass |
| Metabolite-based cell-cell communication | `ov.single.MetaboliteCCC(adata)` (note spelling: Metabol**i**teCCC, verified) | — |
| Differential metabolism | `ov.single.differential_metabolism(adata, ...)` | — |
| CITE-seq multimodal annotation | `ov.single.Annotation` (multimodal) + totalVI via `lazy_step_scvi` | totalVI / WNN |
| TCGA bulk multi-omics | `ov.bulk.pyTCGA()` | TCGAbiolinks(R) |
| Cross-omics pathway concat | `ov.bulk.enrichment_multi_concat()` / `ov.bulk.geneset_plot_multi()` | — |

> **MuData**: omicverse does not expose `muon`/`MuData` at top level. `pyMOFA` builds MuData internally; for direct MuData manipulation `pip install muon`.
> **Spatial multi-omics** (Stereo-seq/Visium HD multi-modality) → `spatial/multiomics` (cellpose + SpatialData), not this table.

## Plotting Task Mapping (see skills/visualization/omicverse-plotting)

```python
ov.plot_set()  # init (required)
```

| Figure type | API | Alternative tool |
|---|---|---|
| UMAP/tSNE scatter | `ov.pl.embedding(adata, basis='X_umap', color=...)` | scanpy.pl.umap |
| dotplot | `ov.pl.dotplot(adata)` / `markers_dotplot` | scanpy.pl.dotplot |
| violin/box/bar | `ov.pl.violin` / `boxplot` / `bardotplot` | scanpy.pl.violin |
| Volcano | `ov.pl.volcano(df)` | hand-rolled matplotlib |
| Heatmap | `ov.pl.complexheatmap(data)` (PyComplexHeatmap wrapper) | seaborn / ComplexHeatmap |
| Marker heatmap | `ov.pl.marker_heatmap(adata)` | scanpy.pl.heatmap |
| Feature heatmap | `ov.pl.feature_heatmap(adata)` | — |
| Cell-cell communication | `ov.pl.ccc_heatmap` / `ccc_network_plot` / `CellChatViz` | CellChat visualization |
| Spatial visualization | `ov.pl.plot_spatial(adata)` + `add_pie2spatial` / `add_density_contour` | squidpy.pl.spatial_scatter |
| Cell proportion | `ov.pl.cellproportion(adata)` / `plot_cellproportion` | — |
| Circular UMAP | `ov.pl.plot1cell(adata)` | scCIRCULAR |
| Palettes | `ov.pl.palette` / `ForbiddenCity` palette system | — |

## R → Python Ported List (RebuildR / R-bridges, no R environment needed)

| R package | omicverse entry | Status |
|---|---|---|
| Monocle 2 | `ov.single.Monocle` | ✅ 30–100× faster, correlation ≥0.99 |
| DoubletFinder | `ov.pp.qc(doublets_method='doubletfinder')` | ✅ pip: pydoubletfinder |
| scDblFinder | `ov.pp.qc(doublets_method='scdblfinder')` | ✅ pip: pyscdblfinder |
| WGCNA | `ov.bulk.pyWGCNA` (wraps pyWGCNA) | ✅ |
| hdWGCNA | standalone `py-hdWGCNA` repo | ✅ single-cell version |
| inferCNV | standalone `py-inferCNV` repo | ✅ |
| CopyKAT | standalone `py-CopyKAT` repo | ✅ |
| scMetabolism | standalone `py-scmetabolism` repo | ✅ |
| NMF | standalone `rust-NMF` repo | ✅ Rust, 76–218× speedup |
| CellChat | `py-CellChat` (planned); use LIANA/CellPhoneDB v5 for now | 🟡 in progress |

## AnnDataOOM Use Cases

| Scenario | Usage |
|---|---|
| Million-scale cells (>100k) | `ov.read(path, backend='rust')`, ~170× memory savings |
| Large spatial data | same, sparse supported |
| Standard PCA precision required | preprocess with AnnDataOOM then `adata.to_adata()` to standard AnnData |
| **Limitations** | score_genes_cell_cycle / find_markers / non-Harmony batch correction materialize into memory; read-only by default |

## Not Covered by omicverse (Kept as Separate Skills)

| Capability | Kept skill / tool |
|---|---|
| cell2location spatial deconvolution | `spatial/deconvolution` |
| Perturb-seq | `single-cell/perturb-seq` (pertpy) |
| scVelo deep tuning | `single-cell/rna-velocity` (fallback hint) |
| High-res spatial (Stereo-seq/Visium HD) | `spatial/multiomics` |
| Spatial proteomics (CODEX/IMC/MIBI) | `spatial/proteomics` (scimap) |
| ATAC / epigenome downstream | (not integrated, needs ArchR/Signac/SnapATAC2) |
| Methylation | (not covered) |
| Proteomics | (not covered) |
| GWAS/eQTL | (not covered) |
