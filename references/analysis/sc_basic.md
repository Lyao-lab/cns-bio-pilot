# 单细胞基础流程

## 2. 单细胞基础流程

### 2.1 数据加载
```python
# 来源：omicverse-pipeline §1
adata = sc.read_10x_mtx('filtered_feature_bc_matrix/')   # or ov.read('data.h5ad')
adata.layers['counts'] = adata.X.copy()   # MUST store raw counts BEFORE QC
# 百万细胞级：adata = ov.read('data.h5ad', backend='rust')  # AnnDataOOM, ~170× 省内存
```

### 2.2 QC + doublet（先诊断后过滤）
```python
# 来源：omicverse-pipeline §2a Step 2a — 诊断（必须先于过滤）
adata.var['mt'] = adata.var_names.str.startswith('MT-')   # human；mouse 用 'mt-'
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
sc.pl.violin(adata, ['n_genes_by_counts','total_counts','pct_counts_mt'],
             groupby='sample', jitter=0.4, multi_panel=True)
sc.pl.scatter(adata, x='total_counts', y='pct_counts_mt')
sc.pl.scatter(adata, x='total_counts', y='n_genes_by_counts')
```

```python
# 来源：omicverse-pipeline §2b Step 2b — 用诊断出的阈值过滤
ov.pp.qc(adata, mode='seurat', doublets_method='scdblfinder',
         batch_key='sample', filter_doublets=True,
         tresh={'mito_perc': 0.15, 'nUMIs': 500, 'detected_genes': 250})
# ⚠️ 参数名是 tresh（不是 mt_thresh）；mt_thresh 被 **kwargs 静默吞掉
# 或自动阈值：mode='mads', nmads=5
```

### 2.3 Ambient RNA removal（QC 前跑）
```python
# 来源：omicverse-pipeline §1.5
ov.pp.ambient.remove_ambient(adata, method='soupx', raw=raw_adata)
# method: 'soupx'/'fastcar'/'decontx'/'sccdc'/'cellbender'/'scar'
# ⚠️ 必须在 QC 前跑；去除后重新存 layers['counts'] = adata.X.copy()
```

### 2.4 预处理
```python
# 来源：omicverse-pipeline §3
# ⭐ 首选：ov 一步式（normalize+HVG+scale 一条龙，ov 2.3.1 已验证可用）
ov.pp.preprocess(adata, mode='shiftlog|pearson', n_HVGs=2000,
                 target_sum=50*1e4, identify_robust=True)
# mode='shiftlog|pearson'=经典 log1p + pearson 残差（默认）；target_sum=50*1e4 是默认
ov.pp.scale(adata)
ov.pp.pca(adata, layer='scaled', n_pcs=50)
# ⚠️ preprocess 后 obsm key 是 'scaled|original|X_pca'，下游 use_rep 必须匹配
# 如需统一为 'X_pca'：
adata.obsm['X_pca'] = adata.obsm['scaled|original|X_pca']

# 兜底：scanpy 标准三步（ov 预处理在个别数据上仍可能崩，如 IndexError）
# sc.pp.normalize_total(adata, target_sum=1e4)
# sc.pp.log1p(adata)
# sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor='seurat_v3', layer='counts')
# ⚠️ HVG 列名：ov 预处理产出 'highly_variable_features'，scanpy 产出 'highly_variable'——按实际路径取列
# adata.raw = adata                    # ⚠️ 在 HVG 子集化前存 raw（LIANA/注释需要）
# hvg_col = 'highly_variable_features' if 'highly_variable_features' in adata.var else 'highly_variable'
# adata = adata[:, adata.var[hvg_col]].copy()
# sc.pp.scale(adata, max_value=10)
# adata.layers['scaled'] = adata.X.copy()  # 给 ov.pp.pca 的 layer= 参数用
```

### 2.5 降维 + UMAP
```python
# 来源：omicverse-pipeline §4
ov.pp.pca(adata, layer='scaled', n_pcs=50)
ov.pp.neighbors(adata, n_neighbors=15, use_rep='X_pca', n_pcs=30)
# UMAP（默认）
ov.pp.umap(adata)
# MDE（UMAP+GPU 加速，大 cohort 推荐）
ov.pp.mde(adata, embedding_dim=2, n_neighbors=15, basis='X_mde', n_pcs=50)
# SUDE 嵌入（自监督降维）
ov.pp.sude(adata)
# tSNE 可选：ov.pp.tsne(adata)
```

### 2.6 聚类
```python
# 来源：omicverse-pipeline §5
# 手动 resolution（默认）：0.4-1.0 常用范围；0.6 适合 2k-50k 细胞
ov.pp.leiden(adata, resolution=0.6)
# 结果在 adata.obs['leiden']
# 候选对比：跑 res=[0.3,0.6,1.0]，选目标群体最稳定的（ARI>0.7）
# ⚠️ 依赖 neighbors 图（§2.5 必须先完成）

# ⭐ 自动选 resolution（推荐）：bootstrap-ARI，返回 (adata, best_res, score_df)
adata, best_res, scores = ov.single.auto_resolution(
    adata, resolutions=[0.2,0.4,0.6,0.8,1.0,1.2,1.5],
    n_subsamples=5, n_null_subsamples=3, random_state=0)
# 结果在 adata.obs['leiden']（key_added='leiden' 默认）
```

### 2.7 细胞周期
```python
# 来源：omicverse-pipeline §6
ov.pp.score_genes_cell_cycle(adata, species='human')  # 'human'|'mouse'
# adata.obs: S_score, G2M_score, phase
```

### 2.8 批次校正
```python
# 来源：omicverse-pipeline §7
# ⭐ Harmony（默认推荐，PCA 空间，秒级）
ov.single.batch_correction(adata, batch_key='batch', methods='harmony', n_pcs=50)
# ⚠️ 参数名是 methods（复数）！method= 被静默吞掉
# ⚠️ 校正后 obsm key 是 'X_pca_harmony'，下游 use_rep 要匹配
ov.pp.neighbors(adata, n_neighbors=15, n_pcs=50, use_rep='X_pca_harmony')

# scVI（深度学习，生成模型）
model = ov.single.batch_correction(adata, batch_key='batch', methods='scVI',
                                   n_layers=2, n_latent=30, gene_likelihood="nb")
# ⚠️ scVI 后必须重建邻居：ov.pp.neighbors(adata, use_rep='X_scVI'); ov.pp.umap(adata)

# 其他方法：combat / scanorama / scANVI / totalVI / scPoli / CellANOVA / Concord / cca
# 例：ov.single.batch_correction(adata, batch_key='batch', methods='scanorama')
```

