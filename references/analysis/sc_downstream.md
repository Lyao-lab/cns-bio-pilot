# 下游分析：通讯 + 轨迹 + 多组学

## 4. 下游：通讯 + 轨迹 + 多组学

### 4.1 细胞通讯（CCC）
```python
# 来源：omicverse-pipeline §9
# ⚠️ LIANA 需要 adata.raw（含所有基因的归一化表达），HVG 子集化前必须设 adata.raw=adata
ov.single.run_liana(adata, groupby='celltype')   # LIANA+ consensus（推荐）
ov.single.run_cellphonedb_v5(adata)               # CellPhoneDB v5（备选）
ov.pl.ccc_heatmap(adata)
# ⚠️ CCC 措辞用"associated with/enriched for"，禁"regulates/activates"
```

### 4.2 轨迹
```python
# 来源：omicverse-pipeline §9
# ⭐ 新 API：TrajInfer（Palantir-based 轨迹推断）
Traj = ov.single.TrajInfer(adata, basis="X_umap", groupby="clusters",
    use_rep="scaled|original|X_pca", n_comps=50)
Traj.set_origin_cells("Progenitor")
Traj.set_terminal_cells(["TypeA", "TypeB"])
Traj.inference(method="palantir", num_waypoints=500)
# 伪时序结果在 adata.obs 的 'palantir_pseudotime' 等列

# ⭐ PseudotimeFate（fate probability + macrostate 分析）
fate = ov.single.PseudotimeFate(adata, pseudotime_key='palantir_pseudotime',
    groupby='clusters', n_macrostates=10)
res = fate.fit()
vk = fate.compute_pseudotime_velocity(basis='X_umap')

# 旧 API（仍可用）：
ov.single.cellrank_fate(adata, cluster_key='celltype')   # 需 velocity 前置
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

### 4.4 其他下游工具 ⭐ 新增
```python
# 来源：omicverse-pipeline + omicverse-analysis（API 签名以 ov 2.3.1 实测为准）
# StaVIA：VIA 轨迹分析（替代 cellrank_fate）
via = ov.single.StaVIA(adata, use_rep='scaled|original|X_pca', n_comps=50, basis='X_umap')

# MetaTiME：肿瘤微环境 cell state 注释
ov.single.MetaTiME(adata, mode='table')

# CrossSpecies：跨物种分析（human/mouse 对齐）
cs = ov.single.CrossSpecies(adatas=[adata_human, adata_mouse], species=['human','mouse'],
                            method='sym', ref_species='human')
```

### 4.5 CellPhoneDB v5（CCC 替代方法）
```python
# ⭐ CellPhoneDB v5（除 LIANA+ 外的另一个主流 CCC 方法）
ov.single.run_cellphonedb_v5(adata, cpdb_file_path='cellphonedb/',
    celltype_key='celltype', min_cell_fraction=0.1, min_genes=10, min_cells=10)
# 需先下载数据库：ov.single.download_cellphonedb_database()
# 结果可视化：ov.pl.cpdb_heatmap / cpdb_network / cpdb_plot_interaction
```

### 4.6 RNA Velocity（轨迹前置）
```python
# ⭐ scVelo velocity（需先安装 scvelo）
vdata = ov.single.velocity(adata)
# 速度嵌入到 UMAP：scv.pl.velocity_embedding / velocity_stream
# 注意：velocity 需要 spliced/unspliced counts（需 velocytelo 或 kb-python 产出）
```

### 4.7 AUCell（SCENIC 配套富集）
```python
# ⭐ AUCell：基于 regulon 活性评分的富集
# 通常在 SCENIC 后跑，对每个 regulon 算 AUC 评分
import pandas as pd
auc_mtx = ov.single.aucell(exp_mtx=pd.DataFrame(adata.X.toarray(), index=adata.obs_names, columns=adata.var_names),
                           signatures=regulon_dict, auc_threshold=0.05)
# 结果存入 adata.obs 或 adata.obsm 供下游可视化
```

