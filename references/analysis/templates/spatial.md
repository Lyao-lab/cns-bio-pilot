# 空间转录组分析

> **本文件 = 可执行代码模板层**（怎么调 API，照抄并按数据改造）。方法选型与"为什么"见知识层：[`../decision_guide.md`](../decision_guide.md)（生物学问题→方法）、[`../analysis_flow.md`](../analysis_flow.md)（结果→下一步）。执行警告（参数名/顺序/obsm key）就在代码注释里，随片段一起拷贝。

## 空转分析

### 数据 IO
```python
# ⚠️ 读取函数在 ov.io（不是 ov.space）；Visium 标准用 scanpy 的 sc.read_visium
# Visium 标准（scanpy）
adata = sc.read_visium('visium_sample/')

# Visium HD / Xenium / Nanostring（ov.io，8μm/2μm bin / 亚细胞分辨率 / GeoMx-CosMx）
adata = ov.io.read_visium_hd('hd_sample/')
adata = ov.io.read_xenium('xenium_out/')
adata = ov.io.read_nanostring('cosmx/')
```

### 空转 QC + 预处理
> 同单细胞流程，完整代码见 [`sc_basic.md`](sc_basic.md) 的 QC/预处理节。空转特有注意：
> - n_HVGs 可比单细胞多（3000 vs 2000）
> - `layers['counts']` 必须保留（去卷积需要）
> - ⚠️ PCA 在 obsm['scaled|original|X_pca']（非默认 'X_pca'）

### 空间邻居图（所有空间分析前置）
```python
# ⚠️ 参数名是 n_neighs（不是 n_neighbors）；method→coord_type
ov.space.spatial_neighbors(adata, spatial_key='spatial', n_neighs=6, coord_type='generic')
# delaunay=True 用于三角剖分；Visium hex grid 用默认 generic
# 输出 adata.obsp['spatial_connectivities']
# ⚠️ 是 ov.space 不是 ov.pp（ov.pp.spatial_neighbors 不存在）
```

### 空间 domain
```python
# ⚠️ pySTAGATE 必填 num_batch_x/num_batch_y（切片网格划分，单切片填 1,1）
ov.space.pySTAGATE(adata, num_batch_x=1, num_batch_y=1, spatial_key=[0,1])
# spatial_key 指向 obsm 列索引（如 obsm['spatial'] 的第0/1列）
ov.pp.neighbors(adata, use_rep='X_STAGATE'); ov.pp.umap(adata)
ov.pp.leiden(adata, resolution=0.6)

# ov.space.pySTAligner(adata_list)   # 多切片对齐
# ov.space.pySpaceFlow(adata)         # spatial flow embedding
# 非 ov 包装（standalone）：BANKSY / BINARY / GraphST / MENDER / SpatialGlue
```

```python
# CAST（GPU 加速空间聚类，需现建 norm_1e4 layer）
# ⚠️ CAST 依赖分层归一化后的表达量，必须先手动建 layer='norm_1e4'
adata.layers['norm_1e4'] = sc.pp.normalize_total(adata, target_sum=1e4, inplace=False)['X']
# ⚠️ 默认 device='cuda:0'，无 GPU 时显式传 device='cpu'
ov.space.CAST(adata, layer='norm_1e4', device='cuda:0')

# GASTON（空间等深线 IsoDepth，识别空间梯度/边界结构）
gaston = ov.space.GASTON(adata)
gaston.get_gaston_input(get_rgb=False, spot_umi_threshold=50)
gaston.train(isodepth_arch=[20,20], expression_fn_arch=[20,20],
             num_epochs=10000, num_restarts=30, out_dir='result/gaston')
gaston.cal_iso_depth(num_domains=10)            # derive discrete domains
gaston.plot_isodepth(show_streamlines=True)     # continuous isodepth map
gaston.plot_clusters(domain_colors=...)         # discrete domain labels
# Full API: bin_data / filter_genes / get_restricted_adata /
#   get_top_pearson_residuals / load_rescale / pw_linear_fit / restrict_spot /
#   plot_clusters_restrict / plot_gene_gastonrex / plot_gene_pwlinear / plot_gene_raw

# STT（单细胞空间轨迹推断，需 obsm['xy_loc'] + obs['Region'] 列）
ov.space.STT(adata, spatial_loc='xy_loc', region='Region')

# CellCharter（多尺度空间聚类）
# ⚠️ n_clusters 必填；use_rep 指定低维表示来源，n_layers 控制多尺度层数
ov.space.cellcharter(adata, n_clusters=8, use_rep='X_pca', n_layers=3)

# merge_cluster（pymclustR 过聚类结果合并，STAGATE 标配收尾步骤）
#   对 mclust 等过聚类结果按表达相似度合并，threshold 控制合并阈值
ov.space.merge_cluster(adata, groupby='mclust', use_rep='STAGATE', threshold=0.05)
```

### 空间变异基因（SVG）
```python
# spatial_autocorr：Moran's I / Geary's C 空间自相关
ov.space.spatial_autocorr(adata, mode='moran')   # mode='geary' for Geary's C
svg = adata.var.query('moranI > 0.3').index
```

```python
# svg（PROST 法，ov 主推的 SVG 鉴定方法）
#   platform 按平台指定（'visium'/'stereo-seq' 等），n_svgs 控制输出数量
ov.space.svg(adata, mode='prost', n_svgs=3000, platform='visium')

# sepal（图扩散法 SVG）
# ⚠️ 需先跑 spatial_neighbors 建图；max_neighs 必填
#   n_iter/dt 控制扩散迭代与步长，收敛慢时调大 n_iter
ov.space.sepal(adata, max_neighs=6, n_iter=30000, dt=0.001)
```

### 空间去卷积
```python
# cell2location：需 scRNA 参考 + 空转数据
# 参考：skills/spatial/deconvolution/examples/deconvolve_spatial.py
# ov 包装：ov.space.Deconvolution（cell2location/RCTD/Tangram/SPOTlight/CARD）
# 详见 skills/spatial/deconvolution/SKILL.md
```

```python
# CellLoc / CellMap（轻量去卷积/细胞映射，无需 MCMC 训练）
ov.space.CellLoc(adata_sc, adata_sp, use_rep_sc='X_pca', use_rep_sp='X_pca')
ov.space.CellMap(adata_sc, adata_sp, use_rep_sc='X_pca', use_rep_sp='X_pca')

# Visium HD 去卷积后处理链
# salvage_secondary_labels：用次级标签（如表达标签）回填/修正主标签
ov.space.salvage_secondary_labels(adata, primary_label='labels_he',
                                  secondary_label='labels_gex', labels_key='labels_joint')
# split_purify：按去卷积权重拆分并纯化混合斑点
ov.space.split_purify(adata, deconvolution_weights, reference, layer='counts')
```

### 空间统计
```python
# 前置：全部需要先跑 ov.space.spatial_neighbors 建图 + obs 中有 cluster_key 列
ov.space.spatial_neighbors(adata, spatial_key='spatial', n_neighs=6, coord_type='generic')

# 邻域富集（哪些 celltype 在空间上显著共邻？）
#   n_perms 为置换检验次数，越大越稳（p 值可重复）
ov.space.nhood_enrichment(adata, cluster_key='celltype', n_perms=1000)

# 共现概率（两种 celltype 在给定距离内出现的概率）
#   interval：距离窗口（单位同 spatial_key 坐标）
ov.space.co_occurrence(adata, cluster_key='celltype', spatial_key='spatial', interval=50)

# Ripley's（点空间分布是随机/聚集/均匀？）
#   mode='F' 为 F 函数（空最近邻），还有 'K'/'G' 等
ov.space.ripley(adata, cluster_key='celltype', mode='F')

# 中心性（celltype 在空间邻居网络中的中心程度）
ov.space.centrality_scores(adata, cluster_key='celltype')

# 距离相关方差（基因表达随与特定区域距离的变化）
#   groups 指定目标区域/分组，cluster_key 指定分组来源列
ov.space.var_by_distance(adata, groups='celltype', cluster_key='celltype')
```

### Visium HD bin→cell
```python
# bin2cell：Visium HD bin 级表达 → 单细胞级表达
# ⚠️ 依赖 cellpose 核分割产出的 adata.obs['labels_joint']（labelled 结果）
#   spatial_keys：bin 坐标所在 obsm key；diameter_scale_factor 缩放核直径
#   add_geometry=True 时把细胞几何写入 anndata（下游可做形态学分析）
ov.space.bin2cell(adata, labels_key='labels_joint', spatial_keys=['spatial'],
                  diameter_scale_factor=None, add_geometry=True)
```

### SPATA2 工具层
```python
# SPATA2 集成工具（辅助层，非独立分析：坐标/样本信息/组织轮廓等）
# spata2_get_coords：取坐标并附带 obs 变量（include_obs 指定附带列）
ov.space.spata2_get_coords(adata, include_obs=['total_counts'])
# spata2_join_variables：把基因列表并入样本信息表
ov.space.spata2_join_variables(adata, gene_list)
# spata2_tissue_outline：提取组织轮廓
ov.space.spata2_tissue_outline(adata)
# spata2_identify_outliers：识别离群点（method='dbscan' 基于密度）
ov.space.spata2_identify_outliers(adata, method='dbscan')
# spata2_remove_outliers：剔除离群点
ov.space.spata2_remove_outliers(adata)
```

### 空间通讯
```python
ov.space.Cal_Spatial_Net(adata)                    # 构建 LR 网络（helper 可用）
# ⚠️ create_communication_anndata 的 clustering_column 参数必填（指定细胞分群列）
ov.space.create_communication_anndata(adata, clustering_column='celltype')
# COMMOT 有两条路：
# ① ov 包装（fetal_heart VIC 项目实测可用，omicverse 2.3.1）：
db = ov.external.commot.pp.ligand_receptor_database(
    species='human', signaling_type='Secreted Signaling', database='CellChat')
db.columns = ['ligand', 'receptor', 'pathway', 'type']
db_filt = ov.external.commot.pp.filter_lr_database(db, adata, heteromeric=True, min_cell_pct=0.01)
ov.external.commot.tl.spatial_communication(
    adata, database_name='CellChat', df_ligrec=db_filt,
    dis_thr=500., heteromeric=True, pathway_sum=True)
# 结果：adata.obsm['commot-CellChat-sum-sender'/'-receiver']（每 LR 一列）
# ② standalone：pip install commot → ct.tl.commot(...)
# 或 LIANA+ spatial mode：ov.single.run_liana(adata, ...) with spatial coords
# ⚠️ ov.space.COMMOT 顶层无公开方法（只有 _commot 私有 + helper）
```

### 其他空间分析工具
```python
# clusters：通用空间聚类（支持多种方法）
ov.space.clusters(adata, methods='kmeans', spatial_key='spatial')

# interaction_matrix：细胞类型互作矩阵（哪些类型相邻）
ov.space.interaction_matrix(adata, cluster_key='celltype')

# nmf_tissue_zones：NMF 组织区域分解
ov.space.nmf_tissue_zones(adata, obsm_key='X_pca', n_factors=10)

# sliding_window：滑动窗口分析（局部特征提取）
ov.space.sliding_window(adata, window_size=100, overlap=20)
```