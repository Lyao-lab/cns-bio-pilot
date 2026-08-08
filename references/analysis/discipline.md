# 分析纪律速查（红线规则）

## 7. 关键纪律速查（分析时的红线）

| 纪律 | 违规后果 | 详见 |
|---|---|---|
| `layers['counts']` 在 QC 前存 | DE/velocity 无法做 | dispatch_cheatsheet A3 |
| 单细胞 DE 必须 pseudobulk | 假阳性膨胀 | dispatch_cheatsheet A2 |
| 批次校正后禁做 DE | 疾病信号被抹除 | dispatch_cheatsheet A4 |
| 比例数据禁 chi-square | 违反 compositional 约束 | dispatch_cheatsheet A7 |
| `tresh` 不是 `mt_thresh` | 参数被静默吞掉 | omicverse-pipeline §2 |
| `methods`(复数) 不是 `method` | 参数被静默吞掉 | omicverse-pipeline §7 |
| `resolution='auto'` 报错 | ov 2.3.1 不支持 auto | 用固定值 0.4-1.0 |
| `ov.pp.preprocess` 可能崩 | IndexError（ov 2.3.1 已知） | scanpy 三步兜底 |
| preprocess 后 obsm key 是 `scaled|original|X_pca` | 下游 use_rep 找不到键 | use_rep 必须匹配，或 adata.obsm['X_pca']=adata.obsm['scaled|original|X_pca'] |
| HVG 列名：ov 用 `highly_variable_features` | scanpy 用 `highly_variable`，取错列报 KeyError | 按实际路径取列（见 sc_basic §2.4） |
| `ov.single.DEG` 是 per-cell DE（探索） | 直接当发表结果 → 假阳性 | pseudobulk pyDEG 是金标准（发表） |
| LIANA 需要 `adata.raw` | ".raw is not initialized" | HVG 子集化前设 raw |
| `pyDEG` 只接受 DataFrame | "unexpected keyword argument 'groupby'" | 转成 行=基因列=样本 的 count_df |
| `geneset_enrichment` 需 pathways_dict + organism | "unexpected keyword argument 'org'" | 先 geneset_prepare，organism 不是 org |
| `spatial_neighbors` 参数是 n_neighs | "unexpected keyword argument 'n_neighbors'" | n_neighs 不是 n_neighbors |
| `pySTAGATE` 必填 num_batch_x/num_batch_y | "missing required positional arguments" | 单切片传 1,1 |
| scVI 后重建 neighbors(use_rep='X_scVI') | 聚类用错空间 | omicverse-pipeline §7 |
| 空间分析前置 spatial_neighbors | 所有空间方法崩溃 | omicverse-spatial §3 |
| 每步后跑 postcheck | 错误传到下游 | Core Rule 4 |
| 每步存 checkpoint | 无法回溯重算 | Core Rule 5 |

