# 空间转录组分析

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
# ⚠️ 参数名是 n_neighs（不是 n_neighbors）；method→coord_type
ov.space.spatial_neighbors(adata, spatial_key='spatial', n_neighs=6, coord_type='generic')
# delaunay=True 用于三角剖分；Visium hex grid 用默认 generic
# 输出 adata.obsp['spatial_connectivities']
# ⚠️ 是 ov.space 不是 ov.pp（ov.pp.spatial_neighbors 不存在）
```

### 5.4 空间 domain
```python
# 来源：omicverse-spatial §4
# ⚠️ pySTAGATE 必填 num_batch_x/num_batch_y（切片网格划分，单切片填 1,1）
ov.space.pySTAGATE(adata, num_batch_x=1, num_batch_y=1, spatial_key=[0,1])
# spatial_key 指向 obsm 列索引（如 obsm['spatial'] 的第0/1列）
ov.pp.neighbors(adata, use_rep='X_STAGATE'); ov.pp.umap(adata)
ov.pp.leiden(adata, resolution=0.6)

# ov.space.pySTAligner(adata_list)   # 多切片对齐
# ov.space.pySpaceFlow(adata)         # spatial flow embedding
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

