# 分析流程代码速查（Analysis Reference）

> 本文件是 cns-bio-pilot 所有分析流程的代码模板速查——worker 派发时引用本文件即可获得标准分析代码。
> **所有代码从 omicverse-pipeline / omicverse-spatial / omicverse-bulk / deconvolution 各 SKILL.md 抽取**，非新写。
> 依赖：omicverse 2.3.1（见 compat.yaml）。API 经 api_check.py 验证存在。
> 绘图代码不在本文件——见 `plotting_reference.md`。

## 0. 速查卡（分析任务 → 入口函数 → 所在章节）

| 分析任务 | 入口函数 | 本文件章节 | 关键注意 |
|---|---|---|---|
| 数据加载 + counts 保留 | `sc.read_*` + `layers['counts']=X.copy()` | §1 | counts 必须在 QC 前存 |
| QC + doublet | `ov.pp.qc` | §2 | 先诊断后过滤；`tresh` 不是 `mt_thresh` |
| Ambient RNA 去除 | `ov.pp.ambient.remove_ambient` | §2.1 | 在 QC 前跑 |
| 预处理 | `ov.pp.preprocess` + `ov.pp.scale` | §3 | shiftlog vs pearson |
| 降维 + UMAP | `ov.pp.pca` + `ov.pp.neighbors` + `ov.pp.umap` | §4 | neighbors 依赖 pca |
| 聚类 | `ov.pp.leiden(resolution='auto')` | §5 | 依赖 neighbors |
| 细胞周期 | `ov.pp.score_genes_cell_cycle` | §6 | species 参数 |
| 批次校正 | `ov.single.batch_correction` | §7 | `methods`(复数)！scVI 后重建邻居 |
| Marker + 注释 | `ov.single.find_markers` + `ov.single.pySCSA` | §8 | 层级注释（先 lineage 后 subtype） |
| Pseudobulk DE | `sc.get.aggregate` + `ov.bulk.pyDEG` | §9 | **Core Rule 2**：禁 per-cell Wilcoxon |
| 富集 | `ov.bulk.geneset_enrichment` + `ov.bulk.pyGSEA` | §9.1 | GO/KEGG/Reactome |
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
ov.pp.preprocess(adata, mode='shiftlog', n_HVGs=2000)  # shiftlog=classic log1p | pearson=残差
ov.pp.scale(adata)   # 结果存 adata.layers['scaled']
```

### 2.5 降维 + UMAP
```python
# 来源：omicverse-pipeline §4
ov.pp.pca(adata, layer='scaled', n_pcs=50)
ov.pp.neighbors(adata, n_neighbors=15, use_rep='X_pca', n_pcs=30)
ov.pp.umap(adata)
# tSNE 可选：ov.pp.tsne(adata)
```

### 2.6 聚类
```python
# 来源：omicverse-pipeline §5
ov.pp.leiden(adata, resolution='auto')   # auto 调用 ov.single.auto_resolution
# 结果在 adata.obs['leiden']
# ⚠️ 依赖 neighbors 图（§2.5 必须先完成）
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
# 轻量：Harmony（PCA 空间，秒级）
ov.single.batch_correction(adata, methods='harmony', batch_key='sample')
# ⚠️ 参数名是 methods（复数）！method= 被静默吞掉

# 深度：scVI（生成模型）
ov.single.batch_correction(adata, methods='scVI', batch_key='sample')
# scVI 后必须重建邻居：ov.pp.neighbors(adata, use_rep='X_scVI'); ov.pp.umap(adata)
```

## 3. 注释 + 差异分析 + 富集 + 比例

### 3.1 Marker + 注释
```python
# 来源：omicverse-pipeline §8
ov.single.find_markers(adata, groupby='leiden', method='wilcoxon')
# groupby 必需！默认 method='cosg'（稀有群体更稳但慢）

ov.single.pySCSA(adata)             # 无参考，marker→自动注释
ov.single.AnnotationRef(adata, adata_ref=ref_adata, celltype_key='celltype')
# ref_adata 必须是 AnnData 对象（不是字符串）
```

### 3.2 Pseudobulk DE（Core Rule 2 必须）
```python
# 来源：omicverse-pipeline §8.5
# Step 1: 聚合到 pseudobulk（sample × celltype）
pb = sc.get.aggregate(adata, by=['sample', 'celltype'], func='sum', layer='counts')
# ⚠️ 必须用 raw counts layer（不是 normalized .X）

# Step 2: DE（omicverse 包装的 pyDESeq2）
de = ov.bulk.pyDEG(pb, groupby='condition', vs='ctrl',
                   celltype_key='celltype', method='DESeq2')

# Step 3: 过滤
sig = de[(de['padj'] < 0.05) & (de['log2FC'].abs() > 1.0)]
# ⚠️ 禁止 per-cell Wilcoxon 当 DE 报告（Core Rule 2）
# 必须有 ≥3 biological replicates per condition
```

### 3.3 富集分析
```python
# 来源：omicverse-bulk §4
ov.bulk.geneset_enrichment(gene_list=up_genes, org='human')   # GO/KEGG/Reactome
ov.bulk.pyGSEA(rank_series=rank, org='human')
# rank_series: pd.Series(index=gene, values=-log10(p)*sign(FC))
ov.bulk.geneset_plot(adata)
```

### 3.4 细胞比例/差异丰度（standalone，非 ov）
```python
# 来源：omicverse-pipeline §9c
# ⚠️ 禁止 chi-square/Fisher 检验比例（违反 compositional 约束）

# Milo（neighborhood 级 DA，R）
# install.packages("miloR")  →  milo <- Milo(adata); testNhoods(milo)

# scCODA（Bayesian compositional，Python）
# pip install scCODA  →  参考官方教程

# 可视化（ov 有）：
# ov.pl.cellproportion(adata, celltype_clusters='celltype', groupby='condition', legend=True)
```

## 4. 下游：通讯 + 轨迹 + 多组学

### 4.1 细胞通讯（CCC）
```python
# 来源：omicverse-pipeline §9
ov.single.run_liana(adata, groupby='celltype')   # LIANA+ consensus（推荐）
ov.single.run_cellphonedb_v5(adata)               # CellPhoneDB v5（备选）
ov.pl.ccc_heatmap(adata)
# ⚠️ CCC 措辞用"associated with/enriched for"，禁"regulates/activates"
```

### 4.2 轨迹
```python
# 来源：omicverse-pipeline §9
# CellRank 2（Nat Methods 2024，推荐）
ov.single.cellrank_fate(adata, cluster_key='celltype')   # 需 velocity 前置
# 经典 pseudotime：
ov.single.Fate(adata, pseudotime='dpt_pseudotime')
ov.single.Monocle(adata)
# ⚠️ pseudotime 是排序不是时间，禁止"速率/时长"表述
```

### 4.3 多组学整合
```python
# 来源：omicverse-pipeline §9b + multiomics_integration.md
# 按 modal 组合选方法（完整决策表见 omicverse-pipeline §9b）：
ov.single.GLUE_pair(adata)      # scRNA + scATAC
ov.single.pyMOFA(adata)         # ≥3 modalities
ov.single.Metabolism(adata)     # scRNA + 代谢
# 完整 API 见 references/multiomics_integration.md（per-modality 代码）
```

## 5. 空转分析

### 5.1 数据 IO
```python
# 来源：omicverse-spatial §1
adata = ov.space.read_visium_10x('visium_sample/')
adata = ov.io.read_visium_hd('hd_sample/')     # 8μm/2μm bin
adata = ov.io.read_xenium('xenium_out/')       # 亚细胞分辨率
adata = ov.io.read_nanostring('cosmx/')        # GeoMx/CosMx
```

### 5.2 空转 QC + 预处理
```python
# 来源：omicverse-spatial §2
ov.pp.qc(adata, doublets_method='scrublet')   # 同单细胞入口
ov.pp.preprocess(adata, mode='shiftlog', n_HVGs=3000)
ov.pp.scale(adata); ov.pp.pca(adata, n_pcs=50)
# layers['counts'] 必须保留（去卷积需要）
```

### 5.3 空间邻居图（所有空间分析前置）
```python
# 来源：omicverse-spatial §3
ov.space.spatial_neighbors(adata, n_neighbors=6, method='knn')
# method='delaunay' 用于坐标（Visium hex grid 用 knn）
# 输出 adata.obsp['spatial_connectivities']
# ⚠️ 是 ov.space 不是 ov.pp（ov.pp.spatial_neighbors 不存在）
```

### 5.4 空间 domain
```python
# 来源：omicverse-spatial §4
ov.space.pySTAGATE(adata)   # 最常用（graph autoencoder）
ov.pp.neighbors(adata, use_rep='X_STAGATE'); ov.pp.umap(adata)
ov.pp.leiden(adata, resolution='auto')

ov.space.pySTAligner(adata_list)   # 多切片对齐
ov.space.pySpaceFlow(adata)         # spatial flow embedding

# 非 ov 包装（standalone）：BANKSY / BINARY / GraphST / MENDER / SpatialGlue
```

### 5.5 空间变异基因（SVG）
```python
# 来源：omicverse-spatial §5
ov.space.spatial_autocorr(adata, mode='moran')   # Moran's I；mode='geary' for Geary's C
svg = adata.var.query('moranI > 0.3').index
```

### 5.6 空间去卷积
```python
# 来源：deconvolution SKILL.md（cell2location 为主）
# cell2location：需 scRNA 参考 + 空转数据
# 参考：skills/spatial/deconvolution/examples/deconvolve_spatial.py
# ov 包装：ov.space.Deconvolution（cell2location/RCTD/Tangram/SPOTlight/CARD）
# 详见 skills/spatial/deconvolution/SKILL.md
```

### 5.7 空间通讯
```python
# 来源：omicverse-spatial §6
ov.space.Cal_Spatial_Net(adata)                    # 构建 LR 网络（helper 可用）
ov.space.create_communication_anndata(adata)        # 格式化通讯数据
# COMMOT 需 standalone：pip install commot → ct.tl.commot(...)
# 或 LIANA+ spatial mode：ov.single.run_liana(adata, ...) with spatial coords
# ⚠️ ov.space.COMMOT 无公开方法（只有 _commot 私有 + helper）
```

## 6. Bulk 分析

### 6.1 Batch correction + DE
```python
# 来源：omicverse-bulk §2-3
ov.bulk.batch_correction(adata, batch_key='batch')
de = ov.bulk.pyDEG(adata, groupby='condition', method='DESeq2')
```

### 6.2 富集 + GSEA
```python
# 来源：omicverse-bulk §4
ov.bulk.geneset_enrichment(gene_list=up_genes, org='human')
ov.bulk.pyGSEA(rank_series=rank, org='human')
ov.bulk.geneset_plot(adata)
```

### 6.3 共表达网络
```python
# 来源：omicverse-bulk §5
ov.bulk.pyWGCNA(adata, method='signed')   # 'signed'|'unsigned'
```

## 7. 关键纪律速查（分析时的红线）

| 纪律 | 违规后果 | 详见 |
|---|---|---|
| `layers['counts']` 在 QC 前存 | DE/velocity 无法做 | dispatch_cheatsheet A3 |
| 单细胞 DE 必须 pseudobulk | 假阳性膨胀 | dispatch_cheatsheet A2 |
| 批次校正后禁做 DE | 疾病信号被抹除 | dispatch_cheatsheet A4 |
| 比例数据禁 chi-square | 违反 compositional 约束 | dispatch_cheatsheet A7 |
| `tresh` 不是 `mt_thresh` | 参数被静默吞掉 | omicverse-pipeline §2 |
| `methods`(复数) 不是 `method` | 参数被静默吞掉 | omicverse-pipeline §7 |
| scVI 后重建 neighbors(use_rep='X_scVI') | 聚类用错空间 | omicverse-pipeline §7 |
| 空间分析前置 spatial_neighbors | 所有空间方法崩溃 | omicverse-spatial §3 |
| 每步后跑 postcheck | 错误传到下游 | Core Rule 4 |
| 每步存 checkpoint | 无法回溯重算 | Core Rule 5 |
