# 分析流程代码速查（Analysis Reference）

> 本文件是 cns-bio-pilot 所有分析流程的**索引**——执行者（主智能体自身或任意子智能体）写分析代码时引用对应子模块即可获得标准分析代码。
> 内容已分层：知识层（决策/为什么，无代码）在 `references/analysis/`，代码模板层（可执行，唯一拷贝源）在 `references/analysis/templates/`。
> 依赖版本以 compat.yaml 为准。API 经 api_check.py 验证存在。
> 绘图代码见 `plotting_reference.md`。

## 知识层（决策/为什么，无代码）

| 文件 | 内容 |
|---|---|
| [analysis/decision_guide.md](analysis/decision_guide.md) | **⭐ 生物学问题→方法决策表：28 个问题→方法映射 + 反模式黑名单** |
| [analysis/analysis_flow.md](analysis/analysis_flow.md) | **⭐ 自主分析决策树：每步结果解读→下一步追什么→交叉验证→逻辑闭环** |
| [analysis/paper_paradigms.md](analysis/paper_paradigms.md) | **⭐ 分析主干：链 A-E / 主角细胞选择 / 空间验证模式 / CCC 完整链 / 收敛点规律** |
| [analysis/paper_directions.md](analysis/paper_directions.md) | **⭐ 方向指南：7 方向独有要素 + 新主干 D-E + 验证模式 D + 方向专属工具** |
| [analysis/discipline.md](analysis/discipline.md) | 红线：Pseudobulk DE / counts 保留 / 不做 per-cell 统计等 |

## 模板层（可执行代码，唯一拷贝源）

| 模板 | 内容 |
|---|---|
| [analysis/templates/setup.md](analysis/templates/setup.md) | 全局 import + 数据 IO（Visium / HD / Xenium / …） |
| [analysis/templates/sc_basic.md](analysis/templates/sc_basic.md) | QC / preprocess / 降维 / 聚类 / 批次校正 |
| [analysis/templates/sc_annotation.md](analysis/templates/sc_annotation.md) | 注释 / DE / 富集 / 丰度 / SCENIC / CNV |
| [analysis/templates/sc_downstream.md](analysis/templates/sc_downstream.md) | CCC / 轨迹 / 多组学 |
| [analysis/templates/spatial.md](analysis/templates/spatial.md) | 空转全流程 |
| [analysis/templates/bulk.md](analysis/templates/bulk.md) | Bulk DE / GSEA / WGCNA / PPI |

## 速查卡（分析任务 → 模板模块 → 入口函数）

| 分析任务 | 入口函数 | 模板模块 | 关键注意 |
|---|---|---|---|
| 全局 import + counts 保留 | `ov.plot_set()` + `layers['counts']=X.copy()` | templates/setup.md | counts 必须在 QC 前存 |
| 数据 IO（Visium/HD/Xenium/…） | `sc.read_visium` / `ov.io.read_*` | templates/setup.md | reader 在 ov.io；标准 Visium 用 sc.read_visium |
| QC + doublet | `ov.pp.qc` | templates/sc_basic.md | 先诊断后过滤；`tresh` 不是 `mt_thresh` |
| Ambient RNA 去除 | `ov.pp.ambient.remove_ambient` | templates/sc_basic.md | 在 QC 前跑 |
| 元数据 EDA（设计可分性） | `pd.crosstab(batch, condition)` | templates/sc_basic.md | 混淆=设计问题，算法救不了 |
| 预处理 | `ov.pp.preprocess(mode='shiftlog\|pearson')` | templates/sc_basic.md | obsm key 'scaled\|original\|X_pca' |
| 降维 + UMAP | `ov.pp.pca`+`neighbors`+`umap`/`mde` | templates/sc_basic.md | neighbors 依赖 pca |
| 聚类 | `ov.pp.leiden(0.6)` / `auto_resolution` | templates/sc_basic.md | 'auto' 报错，用固定值 |
| 细胞周期 | `ov.pp.score_genes_cell_cycle` | templates/sc_basic.md | species 参数 |
| 批次校正 | `ov.single.batch_correction(methods=…)` | templates/sc_basic.md | methods 复数；scVI 重建邻居；查 iLISI/cLISI |
| Marker + 注释 | `ov.single.find_markers` + `ov.single.Annotation` | templates/sc_annotation.md | 统一 Annotation 类；层级注释 |
| Pseudobulk DE | `sc.get.aggregate` + `ov.bulk.pyDEG(count_df)` | templates/sc_annotation.md | pyDEG 只收 DataFrame |
| 富集 | `ov.bulk.geneset_enrichment(organism=…)` | templates/sc_annotation.md | 需 pathways_dict + organism（非 org） |
| 细胞比例/差异丰度 | `ov.single.DCT`（sccoda/milo） | templates/sc_annotation.md | 禁 chi-square/Fisher |
| SCENIC / CNV / Augur | `ov.single.SCENIC/CNV/Augur` | templates/sc_annotation.md | |
| 细胞通讯 | `ov.single.run_liana` | templates/sc_downstream.md | 措辞 "associated with" |
| 轨迹 | `ov.single.TrajInfer` + `PseudotimeFate` | templates/sc_downstream.md | 新 API；cellrank_fate 旧 |
| 多组学整合 | `ov.single.GLUE_pair/pyMOFA` | templates/sc_downstream.md | 按 modal 组合选 |
| 空间邻居图 | `ov.space.spatial_neighbors(n_neighs=…)` | templates/spatial.md | n_neighs 非 n_neighbors |
| 空间 domain | `ov.space.pySTAGATE/CAST/GASTON` | templates/spatial.md | GASTON 有完整工作流 |
| SVG | `ov.space.svg/spatial_autocorr/sepal` | templates/spatial.md | |
| 空间去卷积 | `ov.space.Deconvolution/CellLoc/CellMap` | templates/spatial.md | 需 scRNA 参考 |
| 空间统计 | `ov.space.nhood_enrichment/ripley/…` | templates/spatial.md | 先 spatial_neighbors |
| 空间通讯 | `ov.space.Cal_Spatial_Net` + `ov.external.commot`（或 standalone） | templates/spatial.md | ov.space 顶层无 COMMOT；wrapper 在 ov.external.commot |
| Bulk DE | `ov.bulk.pyDEG(count_df)` | templates/bulk.md | pyDESeq2 包装 |
| Bulk 富集/GSEA | `ov.bulk.geneset_enrichment/pyGSEA(gene_rnk=…)` | templates/bulk.md | gene_rnk 非 rank_series |
| Bulk WGCNA | `ov.bulk.pyWGCNA(anndata=…)` | templates/bulk.md | anndata=/networkType |
| Bulk PPI | `ov.bulk.pyPPI(species=9606)` | templates/bulk.md | species=NCBI id |
| 分析纪律红线 | — | analysis/discipline.md | Pseudobulk/counts/措辞 |

数据 IO 完整说明见 templates/setup.md 与 templates/spatial.md。