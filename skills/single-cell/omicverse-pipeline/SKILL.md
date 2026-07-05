---
name: omicverse-single-cell-pipeline
description: 单细胞全流程（QC→doublet→降维聚类→注释→批次校正→通讯→轨迹）基于 OmicVerse V2 统一 API，无需在 scanpy/Seurat/scVI/CellTypist 间切换。一个 import omicverse as ov 覆盖 90% 常规分析。
---

# OmicVerse 单细胞全流程

**合并自原 skill**：`single-cell/preprocessing`、`doublet-detection`、`clustering`、`cell-annotation`、`batch-integration`、`cell-communication`、`trajectory-inference`、`scanpy`、`scvi-tools`。这些功能在 OmicVerse V2 中已有统一封装，本 skill 是它们的官方推荐入口。RNA velocity 见 `single-cell/rna-velocity`，perturb-seq 见 `single-cell/perturb-seq`。

`pip install omicverse` （V2 已发布）。代码示例基于实际 ov API，标注关键参数与坑。

## 0. 初始化

```python
import omicverse as ov
ov.plot_set()  # 统一全局绘图样式（字体/配色/dpi）
import scanpy as sc   # ov 基于 scanpy/anndata，少量操作仍需 sc
```

## 1. 加载数据（保留 layers['counts']）

```python
adata = sc.read_10x_mtx('filtered_feature_bc_matrix/')   # 或 ov.read('data.h5ad')
adata.layers['counts'] = adata.X.copy()   # 重要：QC 前存原始计数，DE/velo 全靠它
```

> 百万细胞级数据：`adata = ov.read('data.h5ad', backend='rust')` 用 AnnDataOOM，内存省 ~170×。

## 2. QC + doublet（一步）

`ov.pp.qc` 内联 mt/ribo 比例计算、细胞/基因过滤与 doublet 检测。

```python
ov.pp.qc(
    adata,
    doublets_method='scrublet',     # 'scrublet'|'scdblfinder'|'doubletfinder'
    batch_key='sample',             # 多样本必须按批次检测 doublet
    filter_doublets=True,
    mt_thresh=20,                   # mt% 阈值，组织相关；脑/肝 5-10，培养细胞可 20
)
# adata.obs 新增: n_genes_by_counts, total_counts, pct_counts_mt, predicted_doublet
```

决策点：scrublet 默认（快、Python 原生）；doubletfinder（R 引擎，需 R 环境）结果常与 Seurat 一致。

## 3. 预处理（归一化 + HVG + scale）

```python
ov.pp.preprocess(adata, mode='shiftlog', n_HVGs=2000)
# mode='shiftlog'  → 经典 log1p（默认）
# mode='pearson'   → Pearson残差（免去显式 HVG/scale，更鲁棒）
ov.pp.scale(adata)   # 结果存 adata.layers['scaled']
```

决策点：常规图用 shiftlog；残差模式 pearson 对线粒体/细胞周期污染更稳，但 DE 解释性略差。

## 4. 降维 + 邻域 + UMAP/TSNE

```python
ov.pp.pca(adata, layer='scaled', n_pcs=50)
ov.pp.neighbors(adata, n_neighbors=15, use_rep='X_pca', n_pcs=30)
ov.pp.umap(adata)
ov.pp.tsne(adata)   # 可选，按需
```

## 5. 聚类（自动分辨率）

```python
ov.pp.leiden(adata, resolution='auto')   # auto 模式调用 ov.single.auto_resolution
# 等价手动：
# ov.single.auto_resolution(adata); ov.pp.leiden(adata, resolution=res)
# 结果 adata.obs['leiden']
```

## 6. 细胞周期评分

```python
ov.pp.score_genes_cell_cycle(adata, species='human')  # 'human'|'mouse'
# adata.obs: S_score, G2M_score, phase
```

## 7. 批次校正 / 整合

```python
# 轻量：Harmony（在 PCA 空间，秒级）
ov.single.batch_correction(adata, method='harmony', batch_key='sample')

# 深度：scVI（生成模型，捕捉非线性批次效应）
ov.single.batch_correction(adata, method='scvi', batch_key='sample')
# 注意：scVI 后用 adata.obsm['X_scVI'] 作为 use_rep 重算 neighbors/umap
ov.pp.neighbors(adata, use_rep='X_scVI'); ov.pp.umap(adata)
```

决策点：浅批次/快迭代用 Harmony；批次复杂、发 CNS 主图用 scVI（原 scvi-tools 已被合并进来，参数透传）。

## 8. marker + 注释

```python
# marker
ov.single.find_markers(adata, method='wilcoxon')   # 'wilcoxon'|'t-test'|'cosg'
# COSG 对稀有细胞群更稳但慢

# 注释（三选一/组合）
ov.single.pySCSA(adata)             # 无参考，marker→自动注释
ov.single.AnnotationRef(adata, ref='...')  # 有参考（CellTypist/SingleR 引擎）
ov.single.gptcelltype(adata)        # LLM 辅助，需 API key
```

## 9. 下游：通讯 / 轨迹

```python
# 细胞通讯
ov.single.run_cellphonedb_v5(adata)  # 或 ov.single.run_liana(adata)
ov.pl.ccc_heatmap(adata)

# 拟时序（py-monocle2，已从 R 移植为 Python）
ov.single.Monocle(adata)
```

## 10. 可视化（详见 visualization/omicverse-plotting）

```python
ov.pl.embedding(adata, basis='X_umap', color='celltype')
ov.pl.dotplot(adata, var_names=markers, groupby='celltype')
ov.pl.violin(adata, keys=['CD3D'], groupby='celltype')
```

## 决策速查：何时离开本 skill

| 需求 | 去 |
|---|---|
| RNA velocity | `single-cell/rna-velocity` |
| Perturb-seq / CRISPR | `single-cell/perturb-seq` |
| 课题方法学设计 | `single-cell/research-planner` |
| 多面板拼图 / 图形摘要 | `visualization/*` |

## 关键坑

- `layers['counts']` 必须在 `ov.pp.qc` **之前**保存，否则 DE/velo 无原始计数。
- scVI 整合后所有 neighbors/umap/leiden 都要在 `use_rep='X_scVI'` 上重算。
- `ov.pp.leiden(resolution='auto')` 依赖已有 neighbors 图，确保第 4 步完成。
- 多样本 doublet 检测务必传 `batch_key`，否则跨样本假 doublet 泛滥。
