# OmicVerse V2 API 速查与任务映射

`pip install omicverse`。本文件是任务→API 的快速映射，详细用法见对应 `skills/*/SKILL.md`。

## 基础设置

```python
import omicverse as ov
ov.plot_set()                          # 初始化统一样式（必须）
# 大数据（百万细胞）：
adata = ov.read('data.h5ad', backend='rust')   # AnnDataOOM，170× 节省内存
# 常规数据：
adata = ov.read('data.h5ad')
```

## 单细胞任务映射（见 skills/single-cell/omicverse-pipeline）

| 任务 | omicverse API | 替代的独立工具 |
|---|---|---|
| QC（线粒体/UMI/基因数） | `ov.pp.qc(adata, thresh={'mito_perc':20,'nUMIs':500,'detected_genes':250}, doublets_method='scrublet', batch_key='sample', filter_doublets=True)` | scanpy.pp.calculate_qc_metrics |
| doublet 检测 | 同上 `doublets_method='scrublet'\|'scdblfinder'\|'doubletfinder'` | scrublet/scDblFinder/DoubletFinder |
| 归一化 | `ov.pp.preprocess(adata, mode='shiftlog'\|'pearson', n_HVGs=2000)` | scanpy normalize_total/log1p, scTransform |
| 还原 raw counts | `ov.pp.recover_counts(adata)` | — |
| scale（不改X） | `ov.pp.scale(adata)` → 存 `layers['scaled']` | scanpy.pp.scale |
| PCA | `ov.pp.pca(adata, layer='scaled', n_pcs=50)` | scanpy.pp.pca |
| 邻居图 | `ov.pp.neighbors(adata)` | scanpy.pp.neighbors |
| UMAP/tSNE | `ov.pp.umap(adata)` / `ov.pp.tsne(adata)` | scanpy.tl.umap |
| 聚类 | `ov.pp.leiden(adata, resolution='auto')` （auto 自动选分辨率） | scanpy.tl.leiden |
| 自动分辨率 | `ov.single.auto_resolution(adata)` | — |
| 细胞周期 | `ov.pp.score_genes_cell_cycle(adata, species='human')` | scanpy.tl.score_genes_cell_cycle |
| 批次校正 Harmony | `ov.single.batch_correction(adata, method='harmony')` | harmonypy |
| 批次校正 scVI | `ov.single.batch_correction(adata, method='scvi')` | scvi-tools |
| marker 基因 | `ov.single.find_markers(adata, method='wilcoxon'\|'t-test'\|'cosg')` | scanpy.tl.rank_genes_groups |
| 注释（无参考） | `ov.single.pySCSA(adata)` / `MetaTiME` | SCSA |
| 注释（有参考） | `ov.single.AnnotationRef(adata)` / `TOSICA` / `weighted_knn_transfer` | CellTypist |
| GPT 注释 | `ov.single.gptcelltype(adata)` | GPTCelltype |
| 拟时序/轨迹 | `ov.single.Monocle(adata)` （py-monocle2，R 已移植） | Monocle2(R) |
| 拟时序（其他） | `Palantir` / `Slingshot` / `VIA` / `cytotrace2` | Palantir/Slingshot |
| RNA velocity | `ov.single.Velo(adata, mode='scvelo'\|'dynamo')` | scVelo（深度调参用原生） |
| 细胞通讯 | `ov.single.run_cellphonedb_v5(adata)` / `run_liana(adata)` | CellPhoneDB/LIANA |
| GRN | `ov.single.SCENIC(adata)` | SCENIC |
| MetaCell | `ov.single.MetaCell(adata)` / `cNMF` / `SEACells` | MetaCell |
| 一站式懒人 | `ov.single.lazy(adata)` | — |

## 空间转录组任务映射（见 skills/spatial/omicverse-spatial）

| 任务 | omicverse API | 替代的独立工具 |
|---|---|---|
| 读 Visium HD | `ov.io.read_visium_hd(path)` | squidpy.read_visium |
| 读 Xenium | `ov.io.read_xenium(path)` | squidpy.read_xenium |
| 读 NanoString | `ov.io.read_nanostring(path)` | squidpy.read_nanostring |
| 读 Visium 10x | `ov.space.read_visium_10x(path)` | squidpy |
| 空间邻域图 | `ov.pp.spatial_neighbors(adata)` | squidpy.gr.spatial_neighbors |
| SVG（空间变异基因） | `ov.space.spatial_autocorr(adata, mode='moran')` | squidpy.gr.spatial_autocorr |
| 空间域 | pySTAGATE / GraphST / BINARY / BANKSY / CAST / GASTON | STAGATE/GraphST |
| 空间对齐 | `pySTAligner` / SLAT | STAligner |
| 空间通讯 | `ov.space.Cal_Spatial_Net(adata)` + COMMOT / flowsig | COMMOT |
| 空间张量 | `STT` (Spatial Transition Tensor) | STT |
| **去卷积** | `ov.space.Deconvolution` / Tangram / RCTD / FlashDeconv（**无 cell2location**） | **cell2location（保留独立 skill）** |

## bulk 任务映射（见 skills/general-bio/omicverse-bulk）

| 任务 | omicverse API | 替代的独立工具 |
|---|---|---|
| 差异表达 | `ov.bulk.pyDEG(adata)` （pyDESeq2 封装） | DESeq2(R) / pydeseq2 |
| 批次校正 | `ov.bulk.batch_correction(adata)` | ComBat / inmoose |
| GO/KEGG 富集 | `ov.bulk.geneset_enrichment(genes)` + `geneset_plot()` | clusterProfiler(R) |
| GSEA | `ov.bulk.pyGSEA(ranked_list)` （GSEApy 封装） | fgsea(R) / GSEApy |
| 通路数据库 | `ov.utils.download_pathway_database()` + `geneset_prepare()` | — |
| WGCNA | `ov.bulk.pyWGCNA(adata)` （pyWGCNA 封装） | WGCNA(R) |
| PPI | `ov.bulk.pyPPI(genes)` + `string_interaction()` | STRINGdb(R) |
| TCGA | `ov.bulk.pyTCGA()` | TCGA biolinks(R) |
| bulk 去卷积 | `ov.bulk.Deconvolution` / Scaden / BayesPrime | CIBERSORT |

## 绘图任务映射（见 skills/visualization/omicverse-plotting）

```python
ov.plot_set()  # 初始化（必须）
```

| 图类型 | API | 替代工具 |
|---|---|---|
| UMAP/tSNE 散点 | `ov.pl.embedding(adata, basis='X_umap', color=...)` | scanpy.pl.umap |
| dotplot | `ov.pl.dotplot(adata)` / `markers_dotplot` | scanpy.pl.dotplot |
| violin/box/bar | `ov.pl.violin` / `boxplot` / `bardotplot` | scanpy.pl.violin |
| 火山图 | `ov.pl.volcano(df)` | 自写 matplotlib |
| 热图 | `ov.pl.complexheatmap(data)` （PyComplexHeatmap 封装） | seaborn/s ComplexHeatmap |
| marker 热图 | `ov.pl.marker_heatmap(adata)` | scanpy.pl.heatmap |
| feature 热图 | `ov.pl.feature_heatmap(adata)` | — |
| 细胞通讯图 | `ov.pl.ccc_heatmap` / `ccc_network_plot` / `CellChatViz` | CellChat 可视化 |
| 空间可视化 | `ov.pl.plot_spatial(adata)` + `add_pie2spatial` / `add_density_contour` | squidpy.pl.spatial_scatter |
| 细胞比例 | `ov.pl.cellproportion(adata)` / `plot_cellproportion` | — |
| circular UMAP | `ov.pl.plot1cell(adata)` | scCIRCULAR |
| 配色 | `ov.pl.palette` / `ForbiddenCity` 配色系统 | — |

## R→Python 已移植清单（RebuildR/R-bridges，无需 R 环境）

| R 包 | omicverse 入口 | 状态 |
|---|---|---|
| Monocle 2 | `ov.single.Monocle` | ✅ 30-100× 更快，相关性 ≥0.99 |
| DoubletFinder | `ov.pp.qc(doublets_method='doubletfinder')` | ✅ pip: pydoubletfinder |
| scDblFinder | `ov.pp.qc(doublets_method='scdblfinder')` | ✅ pip: pyscdblfinder |
| WGCNA | `ov.bulk.pyWGCNA`（封装 pyWGCNA） | ✅ |
| hdWGCNA | 独立 `py-hdWGCNA` 仓库 | ✅ 单细胞版 |
| inferCNV | 独立 `py-inferCNV` 仓库 | ✅ |
| CopyKAT | 独立 `py-CopyKAT` 仓库 | ✅ |
| scMetabolism | 独立 `py-scmetabolism` 仓库 | ✅ |
| NMF | 独立 `rust-NMF` 仓库 | ✅ Rust，76-218× 速度 |
| CellChat | `py-CellChat`（计划中）；现用 LIANA/CellPhoneDB v5 | 🟡 进行中 |

## AnnDataOOM 使用场景

| 场景 | 用法 |
|---|---|
| 百万级细胞（>100k） | `ov.read(path, backend='rust')`，内存节省 170× |
| 大空转数据 | 同上，支持 sparse |
| 标准 PCA 精度要求 | 用 AnnDataOOM 预处理后 `adata.to_adata()` 转标准 AnnData |
| **局限** | score_genes_cell_cycle / find_markers / 非 Harmony 批次校正会物化进内存；默认只读 |

## omicverse 未覆盖（保留独立 skill）

| 功能 | 保留的 skill / 工具 |
|---|---|
| cell2location 空间去卷积 | `spatial/deconvolution` |
| Perturb-seq | `single-cell/perturb-seq`（pertpy） |
| scVelo 深度调参 | `single-cell/rna-velocity`（提示 fallback） |
| 高分辨率空转（Stereo-seq/Visium HD） | `spatial/multiomics` |
| 空间蛋白组（CODEX/IMC/MIBI） | `spatial/proteomics`（scimap） |
| ATAC/表观下游 | （未集成，需 ArchR/Signac/SnapATAC2） |
| 甲基化 | （未覆盖） |
| 蛋白组学 | （未覆盖） |
| GWAS/eQTL | （未覆盖） |
