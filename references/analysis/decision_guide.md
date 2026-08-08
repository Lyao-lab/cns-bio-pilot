# 生物学问题 → 分析方法决策表

> 本表是"用户描述一个生物学假设/问题 → 该用哪个分析方法"的决策指南。
> 与 figure_guide §0.1（数据→图型）互补：那张表解决"画什么图"，本表解决"做什么分析"。
> **使用方式**：agent 面对用户的生物学问题时，先查本表找到方法，再去对应子模块查代码模板。

## 1. 细胞身份与注释

| 生物学问题 | 分析方法 | ov API | 代码模板 | 陷阱 |
|---|---|---|---|---|
| 我的细胞有哪些类型？ | Marker 检测 → 自动注释 → 人工验证 | `find_markers` → `Annotation` → dotplot/violin | sc_annotation.md | auto-annotation 后必须 marker 人工验证 [A9] |
| 这个 cluster 是什么细胞？ | Marker 查注释 | `find_markers` → `pySCSA/CellTypist/Annotation` | sc_annotation.md | 无 marker 的 cluster 标 Unknown 不硬凑 |
| 恶性 vs 正常细胞怎么区分？ | CNV 推断 | `ov.single.CNV(method='infercnv', genome='hg38')` | sc_annotation.md | 需要正常细胞（如免疫/内皮）作参照基线 |
| 两个数据集的注释能对齐？ | 注释迁移 | `AnnotationRef` / `scanpy ingest` / `CellVote` | sc_annotation.md | 迁移后检查 transfer quality（mapping score）|

## 2. 细胞状态与动态

| 生物学问题 | 分析方法 | ov API | 代码模板 | 陷阱 |
|---|---|---|---|---|
| 细胞的发育轨迹是什么？ | 轨迹推断 | `TrajInfer(method='palantir')` → `PseudotimeFate.fit()` | sc_downstream.md | ⚠️ 禁止用 UMAP 形状论证轨迹方向（Chari & Pachter 2023）|
| 哪个转录因子驱动命运转变？ | GRN + 轨迹 | `SCENIC` → `AUCell` → `PseudotimeFate.fit_lineage_trends` | sc_annotation + downstream | TF-target 数据库要匹配物种 |
| RNA 速度支持轨迹方向吗？ | Velocity | `ov.single.velocity` → velocity embedding → 与 PAGA 对比 | sc_downstream.md | velocity 需要 spliced/unspliced counts |
| 哪个 branch 的基因动态变化最大？ | 轨迹基因动态 | `PseudotimeFate.fit_lineage_trends` → `dynamic_trends/heatmap` | sc_downstream.md | 轨迹论文的"证据图"永远是这个 |

## 3. 细胞间相互作用

| 生物学问题 | 分析方法 | ov API | 代码模板 | 陷阱 |
|---|---|---|---|---|
| 哪些细胞类型在互相通讯？ | CCC 强度排序 | `run_liana(rank_aggregate)` → `ccc_heatmap` / `ccc_network_plot` | sc_downstream.md | 措辞用"associated with"不用"regulates" [A8] |
| 哪个通路驱动通讯？ | CCC 通路层面 | `ccc_stat_plot(plot_type='pathway')` → pathway 贡献 | sc_downstream.md | pathway 级别是聚合推断，不如 LR 对精确 |
| 配受体对的方向是什么？ | LR 方向性 | `ccc_network_plot(plot_type='chord')` → sender/receiver | sc_downstream.md | chord ≤8 类型，>8 用 network |
| 空间里的 CCC 和单细胞一致吗？ | 空间 CCC | `Cal_Spatial_Net` → `COMMOT` → 与 LIANA 对比 | spatial.md | 空转 CCC 需共定位证据，纯数据库打分退潮 |

## 4. 条件间差异

| 生物学问题 | 分析方法 | ov API | 代码模板 | 陷阱 |
|---|---|---|---|---|
| 疾病 vs 正常哪些基因差异表达？ | Pseudobulk DE | `sc.get.aggregate(sample×celltype)` → `pyDEG` → volcano | sc_annotation.md | ⚠️ 必须 pseudobulk！per-cell DE 假阳性膨胀 [A2] |
| 哪些细胞类型在疾病中比例变化？ | 差异丰度 | `DCT(method='sccoda/milopy')` → beeswarm/stacked | sc_annotation.md | 比例数据禁 chi-square/Fisher [A7]；需 ≥3 重复 |
| 多个时间点的 DE 模式是什么？ | 多条件 DE | `DEG per condition` → `stacking_vol` / `de_scatter` | sc_annotation + plots_stats | volcano 无法容纳 >1 对比维度 |
| 批次效应影响我的结论吗？ | 批次校正 | `batch_correction(harmony/scVI)` → 校正前后对比 | sc_basic.md | ⚠️ 校正后数据禁 DE（信号被抹）[A4]；DE 用 raw counts |
| 每个细胞类型内 DE 还是组成变化？ | DE vs DA 解耦 | pseudobulk DE（基因层面）+ DCT（比例层面）分开做 | sc_annotation.md | 比例变化 ≠ 表达变化，两个问题两个分析 |

## 5. 空间组织架构

| 生物学问题 | 分析方法 | ov API | 代码模板 | 陷阱 |
|---|---|---|---|---|
| 组织里有哪些空间 niche/domain？ | 空间 domain | `pySTAGATE/CAST/cellcharter` → leiden → 空间着色 | spatial.md | **必须配定量面板**："在哪里"+"差多少"成对出现 |
| 两种细胞在空间上邻近吗？ | 空间共定位 | `nhood_enrichment` / `co_occurrence` / `distance_distribution` | spatial.md | 需先跑 `spatial_neighbors` + 有 cluster_key 列 |
| 哪些基因有空间特异性？ | SVG 检测 | `svg(mode='prost')` / `spatial_autocorr(mode='moran')` / `sepal` | spatial.md | sepal 的 max_neighs 必填 |
| spot 里的细胞组成是什么？ | 空间去卷积 | `Deconvolution(cell2location)` / `Tangram` / `CellLoc` | spatial.md | 需 scRNA 参考；cell2location 需 GPU |
| 哪个区域的基因表达梯度变化？ | 空间梯度 | `GASTON(IsoDepth)` / `var_by_distance` | spatial.md | GASTON 需 obsm['xy_loc'] + obs['Region'] |
| 细胞在组织中的分布是随机的吗？ | 空间点统计 | `ripley(mode='F/L/K')` → 聚集/均匀/随机判定 | spatial.md | 需先 spatial_neighbors + cluster_key |
| Visium HD 的 bin→单细胞？ | bin2cell | `bin2cell(labels_key='labels_joint')` | spatial.md | 需先 cellpose 分割 + salvage_secondary_labels |

## 6. 调控网络与机制

| 生物学问题 | 分析方法 | ov API | 代码模板 | 陷阱 |
|---|---|---|---|---|
| 哪些转录因子的调控网络活跃？ | SCENIC GRN | `SCENIC` → regulon → `AUCell` → regulon activity heatmap | sc_annotation.md | TF-target 数据库匹配物种；需 8GB+ 内存 |
| 不同 celltype 的转录组相似度？ | 细胞相关性 | `cell_cor_heatmap(group_by='celltype')` → 层级聚类 | sc_annotation.md | — |
| 有没有新的基因模块/共表达？ | 基因模块 | `pyWGCNA` / `MetaCell` → 模块鉴定 | sc_annotation + bulk | MetaCell 降噪后做 DE 更稳健 |

## 7. 临床关联

| 生物学问题 | 分析方法 | ov API | 代码模板 | 陷阱 |
|---|---|---|---|---|
| 某个基因/特征和生存率有关吗？ | 生存分析 | `ov.pl.kaplan_meier` / `survival` / `logrank_test` → forest plot | bulk.md | 需临床随访数据（time + event）|
| 哪个细胞类型对治疗响应最关键？ | Augur 优先级 | `Augur(label_col='response')` → cell type priority | sc_annotation.md | 需 treatment vs control 分组 |
| 药物处理后细胞状态怎么变？ | 药物响应 | `ov.single.Drug_Response` → 状态轨迹 | sc_annotation.md | 需 dose-response 或 time-course 设计 |

---

## 反模式黑名单（以下分析组合是错的）

| ❌ 错误做法 | 为什么错 | 正确做法 |
|---|---|---|
| per-cell Wilcoxon 做 DE | 假阳性膨胀（没有 sample 级别聚合） | Pseudobulk → DESeq2/edgeR [A2] |
| 批次校正后的 embedding 做 DE | 疾病信号被批次校正抹除 | 用 raw counts + pseudobulk [A4] |
| 卡方检验做比例比较 | 组成数据有 compositional 约束 | Milo/scCODA/DCT [A7] |
| UMAP 形状论证轨迹 | UMAP 距离不可解释 | PAGA / TrajInfer / gene-pseudotime [A6] |
| 空转 CCC 无共定位证据 | 纯数据库打分正在退潮 | 配 spatial CCC 或配受体相邻面板 |
| domain 只有着色图没有定量 | "在哪里"没有"差多少"支撑 | domain 着色 + 组成/密度定量面板成对出现 |
| 只有 UMAP 没有 dotplot/heatmap | UMAP 是"地图"不是注释证据 | dotplot/heatmap 做注释证据 [A9] |
