---
name: omicverse-spatial-pipeline
description: 空间转录组全流程（IO→空间邻域→QC→空间域→SVG→通讯→可视化）基于 OmicVerse V2 统一 API，覆盖 Visium/Xenium/Nanostring/VisiumHD。一个 import omicverse as ov 完成 90% 常规空转分析。
---

## When NOT to use this skill
- 用户要 spot/细胞去卷积（cell2location/RCTD/Tangram 估细胞构成）→ 改用 `spatial/deconvolution`（omicverse 未注册 cell2location）
- 高分辨率平台（Stereo-seq / Slide-seq / Visium HD 亚细胞）+ cellpose 分割 → 改用 `spatial/multiomics`
- 空间蛋白组（CODEX/IMC/MIBI）→ 改用 `spatial/proteomics`（scimap，非空转）
- 常规单细胞（无空间坐标）→ 改用 `single-cell/omicverse-pipeline`

# OmicVerse 空间转录组全流程

**合并自原 skill**：`spatial/preprocessing`、`data-io`、`domains`、`neighbors`、`statistics`、`visualization`、`communication`、`image-analysis`。这些在 OmicVerse V2 中已有统一封装。**去卷积不在本 skill**——cell2location/RCTD 等仍需 `spatial/deconvolution`。高分辨率平台见 `spatial/multiomics`，空间蛋白组见 `spatial/proteomics`。

`pip install omicverse`（V2）。基于 scanpy/squidpy/anndata。

## 0. 初始化

```python
import omicverse as ov
ov.plot_set()
```

## 1. 数据 IO（按平台）

> **网络受限备选**：`sq.datasets.visium_hne_adata()` 等内置数据集源站可能 403。备选：① 用 `st` 环境的 `squidpy.read_visium('本地解压目录/')` 读本地下载的 spaceranger 输出；② 从 GEO 下载 `.h5ad` 后 `sc.read_h5ad()`。

```python
# Visium 标准
adata = ov.space.read_visium_10x('visium_sample/')

# 新一代平台
adata = ov.io.read_visium_hd('hd_sample/')     # 8μm/2μm bin
adata = ov.io.read_xenium('xenium_out/')       # 亚细胞分辨率
adata = ov.io.read_nanostring('cosmx/')        # GeoMx/CosMx
```

| 平台 | 函数 | 分辨率 |
|---|---|---|
| Visium | `ov.space.read_visium_10x` | 55μm spot |
| Visium HD | `ov.io.read_visium_hd` | 2-8μm bin |
| Xenium | `ov.io.read_xenium` | 亚细胞 |
| Nanostring | `ov.io.read_nanostring` | 单细胞级 |

## 2. QC + 预处理

```python
ov.pp.qc(adata, doublets_method='scrublet')   # 与单细胞同入口
ov.pp.preprocess(adata, mode='shiftlog', n_HVGs=3000)
ov.pp.scale(adata); ov.pp.pca(adata, n_pcs=50)
adata.layers['counts']  # 确保保留，去卷积需要
```

## 3. 空间邻域图（核心）

```python
ov.pp.spatial_neighbors(adata, n_neighbors=6, method='knn')
# 或坐标带 Delaunay：method='delaunay'（Visium 六边形网格默认 knn 即可）
# 结果 adata.obsp['spatial_connectivities'] / ['distances']
```

后续 SVG / 空间域 / 通讯都依赖此邻接图。

## 4. 空间域 / 组织区域

```python
# STAGATE（图自编码器，最常用，对噪声鲁棒）
ov.space.pySTAGATE(adata)
ov.pp.neighbors(adata, use_rep='X_STAGATE'); ov.pp.umap(adata)
ov.pp.leiden(adata, resolution='auto')

# 替代算法
ov.space.GraphST(adata)    # 图对比学习，更适大数据
ov.space.BANKSY(adata)     # 邻域感知，边界清晰
ov.space.BINARY(adata)     # 自监督，零样本
```

决策点：默认 STAGATE；样本量大（>1M spot）选 GraphST；需要锐利组织边界选 BANKSY。

## 5. 空间变异基因（SVG）

```python
ov.space.spatial_autocorr(adata, mode='moran')   # Moran's I；mode='geary' 为 Geary's C
# adata.var 新增: moranI, moranI_pval, spatial_high_variable
svg = adata.var.query('moranI > 0.3').index
```

## 6. 空间细胞通讯

```python
# 构建空间网络（ligand-receptor + 空间近邻）
ov.space.Cal_Spatial_Net(adata)
# 推断
ov.space.COMMOT(adata)   # 各向异性通讯，主流选择
# 或 CellChat 空间版（需 R），较少用
```

## 7. 可视化（详见 visualization/omicverse-plotting）

```python
ov.pl.plot_spatial(adata, color='leiden')           # 组织切片聚类
ov.pl.plot_spatial(adata, color='moranI_top_genes') # SVG 表达
ov.pl.embedding(adata, basis='X_umap', color='leiden')
```

H&E / IF 配准图像分析：ov V2 已集成基础配准；复杂配准（StarFusion/SpacesID）仍可借助 `squidpy.pl.spatial_scatter` + `ov.io.read_*` 返回的 `adata.uns['spatial']` 图像栈。

## 决策速查：何时离开本 skill

| 需求 | 去 |
|---|---|
| Spot/细胞去卷积（cell2location 等） | `spatial/deconvolution` |
| Stereo-seq / 高分辨率平台专门流程 | `spatial/multiomics` |
| 空间蛋白组（CODEX/IMC/MIBI） | `spatial/proteomics` |

## 关键坑

- `ov.pp.spatial_neighbors` 必须在空间域/SVG/通讯之前跑——所有空间方法都吃这张图。
- 平台不同默认 n_neighbors 不同：Visium 六边形取 6，Xenium/HD 用 4-8 试。
- SVG 用 Moran's I，阈值 0.3 起步；过严会漏掉弱空间模式基因。
- 去卷积前确认 `adata.layers['counts']` 未被归一化覆盖。
- Visium HD 用 `read_visium_hd`，不要降级用 `read_visium_10x`——会丢 bin 元信息。
