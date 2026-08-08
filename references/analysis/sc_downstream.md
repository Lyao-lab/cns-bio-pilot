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

