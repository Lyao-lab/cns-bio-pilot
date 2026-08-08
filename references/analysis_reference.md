# 分析流程代码速查（Analysis Reference）

> 本文件是 cns-bio-pilot 所有分析流程的**索引**——worker 派发时引用对应子模块即可获得标准分析代码。
> 内容已模块化到 `references/analysis/` 目录，按分析阶段拆分。
> 依赖：omicverse 2.3.1（见 compat.yaml）。API 经 api_check.py 验证存在。
> 绘图代码见 `plotting_reference.md`。

## 模块索引

| 分析阶段 | 子模块 | 内容 |
|---|---|---|
| **生物学问题→方法决策表** | [`analysis/decision_guide.md`](analysis/decision_guide.md) | **⭐ 用户问生物学问题时先查这个——28 个问题→方法映射 + 反模式黑名单** |
| **自主分析流程决策树** | [`analysis/analysis_flow.md`](analysis/analysis_flow.md) | **⭐ agent 自主分析时查这个——每步结果解读→下一步追什么→交叉验证→逻辑闭环** |
| **高分文章分析范式** | [`analysis/paper_paradigms.md`](analysis/paper_paradigms.md) | **⭐ 像高分文章作者一样思考——3 种分析主干/主角细胞选择/空间验证模式/CCC 完整链/收敛点规律** |
| 速查卡 + 全局开头 | [`analysis/README.md`](analysis/README.md) | 分析任务→入口函数映射；全局 import 模板；数据 IO 速查 |
| 单细胞基础流程 | [`analysis/sc_basic.md`](analysis/sc_basic.md) | QC/doublet/ambient → preprocess → 降维 → 聚类 → 细胞周期 → 批次校正 |
| 注释 + DE + 富集 + 比例 | [`analysis/sc_annotation.md`](analysis/sc_annotation.md) | Marker/注释 → Pseudobulk DE → 富集 → 细胞比例/差异丰度 |
| 下游分析 | [`analysis/sc_downstream.md`](analysis/sc_downstream.md) | 细胞通讯(CCC) → 轨迹 → Velocity → AUCell |
| 空间转录组 | [`analysis/spatial.md`](analysis/spatial.md) | 数据IO → QC → 空间邻居 → domain → SVG → 去卷积 → 空间统计 → 空间通讯 |
| Bulk RNA-seq | [`analysis/bulk.md`](analysis/bulk.md) | DE → 富集/GSEA → WGCNA → 批次校正 |
| 分析纪律 | [`analysis/discipline.md`](analysis/discipline.md) | 红线规则（Pseudobulk DE / counts 保留 / 不做 per-cell 统计等） |

## 速查卡（分析任务 → 子模块）

| 分析任务 | 入口函数 | 子模块 | 关键注意 |
|---|---|---|---|
| 数据加载 + counts 保留 | `sc.read_*` + `layers['counts']=X.copy()` | README | counts 必须在 QC 前存 |
| QC + doublet | `ov.pp.qc` | sc_basic | 先诊断后过滤 |
| 预处理 | `ov.pp.preprocess` 或 scanpy 三步 | sc_basic | ⚠️ ov.preprocess 可能崩，有 scanpy 兜底 |
| 降维 + UMAP | `ov.pp.pca` + `sc.pp.neighbors` + `sc.tl.umap` | sc_basic | scanpy 1.11 用 sc.tl.umap 非 sc.pp.umap |
| 聚类 | `sc.tl.leiden(resolution=0.6)` | sc_basic | ⚠️ resolution='auto' 报错，用固定值 |
| 批次校正 | `ov.single.batch_correction` | sc_basic | `methods`(复数)；scVI 后重建邻居 |
| Marker + 注释 | `ov.single.find_markers` + `ov.single.pySCSA` | sc_annotation | 层级注释 |
| Pseudobulk DE | `sc.get.aggregate` + `ov.bulk.pyDEG` | sc_annotation | ⚠️ pyDEG 只接受 DataFrame |
| 富集 | `ov.bulk.geneset_enrichment` | sc_annotation | 需 pathways_dict + organism |
| 细胞通讯 | `ov.single.run_liana` | sc_downstream | 措辞用"associated with" |
| 轨迹 | `ov.single.cellrank_fate` | sc_downstream | 需 velocity 前置 |
| 空转 IO | `ov.space.read_visium_10x` | spatial | 按 platform 选 reader |
| 空间邻居图 | `ov.space.spatial_neighbors` | spatial | n_neighs（不是 n_neighbors）|
| 空间 domain | `ov.space.pySTAGATE` | spatial | 需 num_batch_x/num_batch_y |
| 空间去卷积 | cell2location/RCTD/Tangram | spatial | 需 scRNA 参考 |
| Bulk DE | `ov.bulk.pyDEG` | bulk | pyDESeq2 包装 |
| Bulk 富集 | `ov.bulk.pyGSEA` | bulk | ranked list |
