# 分析流程索引（Analysis Reference Index）

## 0. 速查卡（分析任务 → 入口函数 → 所在章节）

| 分析任务 | 入口函数 | 本文件章节 | 关键注意 |
|---|---|---|---|
| 数据加载 + counts 保留 | `sc.read_*` + `layers['counts']=X.copy()` | §1 | counts 必须在 QC 前存 |
| QC + doublet | `ov.pp.qc` | §2 | 先诊断后过滤；`tresh` 不是 `mt_thresh` |
| Ambient RNA 去除 | `ov.pp.ambient.remove_ambient` | §2.1 | 在 QC 前跑 |
| 预处理 | `ov.pp.preprocess` 或 scanpy 三步 | §3 | ⚠️ ov.preprocess 可能崩，有 scanpy 兜底 |
| 降维 + UMAP | `ov.pp.pca` + `ov.pp.neighbors` + `ov.pp.umap` | §4 | neighbors 依赖 pca |
| 聚类 | `ov.pp.leiden(resolution=0.6)` | §5 | ⚠️ 'auto' 报错，用固定值；依赖 neighbors |
| 细胞周期 | `ov.pp.score_genes_cell_cycle` | §6 | species 参数 |
| 批次校正 | `ov.single.batch_correction` | §7 | `methods`(复数)！scVI 后重建邻居 |
| Marker + 注释 | `ov.single.find_markers` + `ov.single.pySCSA` | §8 | 层级注释（先 lineage 后 subtype） |
| Pseudobulk DE | `sc.get.aggregate` + `ov.bulk.pyDEG(count_df)` | §9 | ⚠️ pyDEG 只接受 DataFrame（行=基因列=样本） |
| 富集 | `ov.bulk.geneset_enrichment` + pathways_dict | §9.1 | ⚠️ 需 pathways_dict + organism（不是 org） |
| 细胞比例/丰度 | Milo/scCODA/propeller（standalone） | §9.2 | 禁 chi-square/Fisher |
| 细胞通讯 | `ov.single.run_liana` | §10 | 措辞用"associated with" |
| 轨迹 | `ov.single.cellrank_fate` / `ov.single.Monocle` | §10.1 | 需 velocity 前置 |
| 空转数据 IO | `ov.space.read_visium_10x` | §11 | 按 platform 选 reader |
| 空转 QC | `ov.pp.qc` + `ov.pp.preprocess` | §11.1 | 同单细胞入口 |
| 空间邻居图 | `ov.space.spatial_neighbors` | §12 | 所有空间分析前置 |
| 空间 domain | `ov.space.pySTAGATE` | §13 | BANKSY/GraphST 需 standalone |
| 空间变异基因 | `ov.space.spatial_autocorr` | §14 | Moran's I / Geary's C |
| 空间去卷积 | cell2location/RCTD/Tangram | §15 | 需 scRNA 参考 |
| 空间通讯 | COMMOT standalone + `ov.space.Cal_Spatial_Net` | §16 | ov 无 COMMOT 公开方法 |
| Bulk DE | `ov.bulk.pyDEG` | §17 | pyDESeq2 包装 |
| Bulk 富集 | `ov.bulk.pyGSEA` | §17.1 | ranked list |
| Bulk WGCNA | `ov.bulk.pyWGCNA` | §17.2 | 共表达网络 |


## 1. 全局开头（每个分析脚本第一行）

```python
import omicverse as ov
import scanpy as sc
ov.ov_plot_set()  # 或 from cns_style import set_cns_style_journal; set_cns_style_journal('nature')

# Core Rule 2: 保留 raw counts（DE/velocity 生死线）
adata.layers['counts'] = adata.X.copy()
```

## 数据 IO 速查 ⭐ 新增

```python
# 单细胞
adata = ov.io.read_10x_h5('filtered_feature_bc_matrix.h5')
adata = ov.io.read_10x_mtx('matrix/')
adata = ov.io.read_h5ad('data.h5ad')
adata = ov.io.read_csv('data.csv')
# 空间
adata = sc.read_visium('visium_sample/')
adata = ov.io.read_visium_hd('hd_sample/')
adata = ov.io.read_visium_hd_bin('hd/', binsize=8)       # bin 级
adata = ov.io.read_visium_hd_seg('hd/')                   # 分割级
adata = ov.io.read_xenium('xenium_out/')
adata = ov.io.read_nanostring('cosmx/')
# 其他
adata = ov.io.read_fcs('sample.fcs')                      # FACS
```

