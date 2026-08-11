# 单细胞基础流程

> **本文件 = 可执行代码模板层**（怎么调 API，照抄并按数据改造）。方法选型与"为什么"见知识层：[`../decision_guide.md`](../decision_guide.md)（生物学问题→方法）、[`../analysis_flow.md`](../analysis_flow.md)（结果→下一步）。执行警告（参数名/顺序/obsm key）就在代码注释里，随片段一起拷贝。

### 数据加载
```python
adata = sc.read_10x_mtx('filtered_feature_bc_matrix/')   # or ov.read('data.h5ad')
adata.layers['counts'] = adata.X.copy()   # MUST store raw counts BEFORE QC
# 百万细胞级：adata = ov.read('data.h5ad', backend='rust')  # AnnDataOOM, ~170× 省内存
```

### QC + doublet（先诊断后过滤）
```python
adata.var['mt'] = adata.var_names.str.startswith('MT-')   # human；mouse 用 'mt-'
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
sc.pl.violin(adata, ['n_genes_by_counts','total_counts','pct_counts_mt'],
             groupby='sample', jitter=0.4, multi_panel=True)
sc.pl.scatter(adata, x='total_counts', y='pct_counts_mt')
sc.pl.scatter(adata, x='total_counts', y='n_genes_by_counts')
```

```python
ov.pp.qc(adata, mode='seurat', doublets_method='scdblfinder',
         batch_key='sample', filter_doublets=True,
         tresh={'mito_perc': 0.15, 'nUMIs': 500, 'detected_genes': 250})
# ⚠️ 参数名是 tresh（不是 mt_thresh）；mt_thresh 被 **kwargs 静默吞掉
# 或自动阈值：mode='mads', nmads=5
```

### Ambient RNA removal（QC 前跑）
```python
ov.pp.ambient.remove_ambient(adata, method='soupx', raw=raw_adata)
# method: 'soupx'/'fastcar'/'decontx'/'sccdc'/'cellbender'/'scar'
# ⚠️ 必须在 QC 前跑；去除后重新存 layers['counts'] = adata.X.copy()
```

### 元数据 EDA（设计可分性检查）
```python
# batch×condition 混淆=设计问题，任何算法救不了；先于整合/DE 检查
import pandas as pd
# batch × condition cross-tab — is the design separable?
print(pd.crosstab(adata.obs['batch'], adata.obs['condition']))
# If batch1 = all control, batch2 = all treated → CONFOUNDED. No algorithm rescues this.
# If balanced (each batch has both conditions) → separable, proceed.

# Sample-level overview — spot outliers before they become artifacts
sample_stats = adata.obs.groupby('sample').agg(
    n_cells=('n_genes_by_counts', 'count'),
    median_genes=('n_genes_by_counts', 'median'),
    median_mt=('pct_counts_mt', 'median')
)
print(sample_stats)
# Any sample with <1/3 median cell count or >2× median mt% → flag, investigate before pooling
```

### 预处理
```python
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

### 降维 + UMAP
```python
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

### 聚类
```python
# 手动 resolution（默认）：0.4-1.0 常用范围；0.6 适合 2k-50k 细胞
ov.pp.leiden(adata, resolution=0.6)
# 结果在 adata.obs['leiden']
# 候选对比：跑 res=[0.3,0.6,1.0]，选目标群体最稳定的（ARI>0.7）
# ⚠️ 依赖 neighbors 图（「降维 + UMAP」节必须先完成）

# ⭐ 自动选 resolution（推荐）：bootstrap-ARI，返回 (adata, best_res, score_df)
adata, best_res, scores = ov.single.auto_resolution(
    adata, resolutions=[0.2,0.4,0.6,0.8,1.0,1.2,1.5],
    n_subsamples=5, n_null_subsamples=3, random_state=0)
# 结果在 adata.obs['leiden']（key_added='leiden' 默认）
```

### 细胞周期
```python
ov.pp.score_genes_cell_cycle(adata, species='human')  # 'human'|'mouse'
# adata.obs: S_score, G2M_score, phase
```

### 批次校正
```python
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

```python
# 整合诊断：iLISI/cLISI/ASW_batch/ASW_celltype，校正后必查
from scib_metrics.benchmark import Benchmarker
# compute iLISI/cLISI/ASW_batch/ASW_celltype on X_pca vs X_scVI vs X_harmony
```

### 其他 ov.pp 工具
```python
# recover_counts：从归一化数据恢复 counts（preprocess 后想找回原始量级）
adata.layers['recover_counts'] = ov.pp.recover_counts(adata.X, mult_value=50*1e4, max_range=50*1e5)

# normalize_pearson_residuals：单独跑 pearson 残差归一化（不用 preprocess 联合模式时）
ov.pp.normalize_pearson_residuals(adata)

# scrublet：单独跑 doublet 检测（不用 ov.pp.qc 的 doublets_method 时）
ov.pp.scrublet(adata)

# qc_metrics：只算 QC 指标不过滤（诊断阶段）
ov.pp.qc_metrics(adata, mt_startswith='MT-')

# regress：回归校正（去 batch effect / 细胞周期等协变量）
ov.pp.regress(adata, keys=['n_counts', 'percent_mito'])

# louvain：Louvain 聚类（leiden 的替代）
ov.pp.louvain(adata, resolution=0.6)
```

