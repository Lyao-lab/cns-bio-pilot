# 自主分析流程决策树（Analysis Flow Tree）

> **核心问题**：agent 拿到原始数据，怎么自主走完分析全流程？
> 不是线性 pipeline（QC→cluster→DE→CCC），而是**根据每步结果的特征决定下一步追哪条线**。
> 与 decision_guide.md（问题→方法）互补：那张表解决"做什么"，本表解决"做了之后看什么、然后追什么"。

## 全局流程框架

```
数据加载 → QC → 预处理+降维+聚类 → 细胞注释
                                         ↓
                                    ┌────┴────┐
                              有空间数据？   无空间
                                    ↓         ↓
                              空间分析线    单细胞分析线
                                    ↓         ↓
                              整合交叉验证 ←────┘
                                    ↓
                              故事构建 → 交付
```

## Phase 1: QC（数据质量评估 → 决定过滤策略）

| QC 结果特征 | 解读 | 下一步决策 |
|---|---|---|
| mt% 中位数 <10%，分布集中 | 线粒体质量好 | 正常过滤（mt<20%）→ 进预处理 |
| mt% 双峰（一群高一群低） | 可能混合了破损细胞/特定细胞类型（如心肌细胞天然高 mt） | 分层看高 mt 群是否为特定细胞；不要一刀切过滤 |
| doublet rate <10% | 正常 | 过滤 doublet → 进预处理 |
| doublet rate >20% | 可能技术问题 | 检查 scrublet 参数；降阈值重跑；标记为数据质量问题 |
| 某样本细胞数 <500 | 样本质量差/上机量不足 | 考虑剔除该样本；或标注 low-n 警告 |
| n_genes 双峰（一群高一群低） | 可能混合了不同测序深度/不同细胞类型 | 先聚类看是否自然分开，不要在 QC 阶段强行过滤 |

> **QC 的核心原则**：先诊断后过滤。画 QC 指标分布（violin per sample），确认过滤阈值不会偏向性剔除某个生物学群体。

## Phase 2: 聚类（cluster 数量 → 决定 resolution 和注释策略）

| 聚类结果 | 解读 | 下一步决策 |
|---|---|---|
| 3-8 个 cluster，marker 清晰 | 标准情况 | → 细胞注释（Phase 3）|
| >15 个 cluster，很多小 cluster | 可能过聚类 | 用 auto_resolution 或降 resolution；检查小 cluster 是否为 doublet/artifact |
| 2-3 个大 cluster，无细分 | 可能欠聚类 | 升 resolution；检查是否批次效应遮蔽了亚群 |
| marker 在多个 cluster 共表达 | 可能细胞连续状态而非离散类型 | → 考虑轨迹分析（非聚类细分）|
| 某个 cluster 只有 1-2 个样本贡献 | 可能是样本特异性 artifact | 检查 batch_key；考虑批次校正 |

## Phase 3: 细胞注释（注释结果 → 决定下游分析主线）

| 注释结果 | 解读 | 下一步决策 |
|---|---|---|
| 主 lineage 清晰（T/B/Myeloid/Stroma…） | 标准情况 | → **选主角细胞**（哪种类型最有趣？比例变化最大？疾病最相关？）→ 深入该类型 |
| 某个类型有多个亚群 | 亚群异质性 | → 亚群 DE + 富集 → 亚群间轨迹 → 该类型的 CCC |
| 恶性细胞 vs 正常细胞 | 肿瘤数据 | → CNV 推断确认恶性 → 恶性亚克隆 DE → 肿瘤-基质互作 |
| 注释不确定（很多 Unknown） | 数据参考不足 | → 用参考数据集迁移注释；或降级为 marker 描述不硬标类型 |
| **主角细胞**选定后 | | → Phase 4 根据"主角"展开分支 |

## Phase 4: 根据主角细胞展开分析（条件→选择分析分支）

### 分支 A: 比例变化明显（disease vs control 某类型比例变化 >10pp）

```
比例变化 → 差异丰度检验（DCT: sccoda/milopy）
  ├─ 显著（FDR<0.05）→ 该类型亚群细分 → 亚群间比例是否也变？
  │    ├─ 亚群也变 → 亚群 DE → 是什么驱动了亚群比例变化？
  │    └─ 亚群不变 → 是整体扩增/减少 → 追增殖（cell cycle score）或凋亡
  └─ 不显著 → 比例变化可能为抽样偏差 → 标注 exploratory
```

### 分支 B: DE 结果丰富（disease vs control 差异基因 >100）

```
DE → 富集分析（GO/KEGG/GSEA）
  ├─ 免疫相关通路 top → 追 CCC（免疫-基质/免疫-恶性 通讯）
  ├─ 代谢通路 top → 迹代谢重编程（基因模块/SCENIC TF）
  ├─ 细胞周期通路 top → 追增殖差异（cell cycle score per condition）
  ├─ ECM/纤维化通路 top → 追 EMT/EndMT 轨迹
  └─ 通路无显著 → 检查 DE 质量（housekeeping 基因在 top？pseudobulk 做了没？）
```

### 分支 C: 轨迹/分化信号（pseudotime 有意义）

```
轨迹推断 → gene-along-pseudotime 动态
  ├─ 某基因沿轨迹单调变化 → 候选 fate marker → 空间验证（如果有空转）
  ├─ 分支点基因差异大 → 转录因子驱动？（SCENIC → branch-specific regulon）
  ├─ velocity 方向与 pseudotime 一致 → 轨迹有支持
  └─ velocity 方向与 pseudotime 矛盾 → 检查 root cell 选择 → 降级轨迹结论
```

### 分支 D: CCC 信号强（LIANA/CellPhoneDB 发现显著 LR 对）

```
CCC → 通路层面聚合
  ├─ 某通路在 disease 特异性活跃 → 追该通路的 LR 对细节
  │    → 配体在哪种细胞？受体在哪种细胞？→ 空间是否共定位？（需空转）
  ├─ sender-receiver 方向变化 → disease 特异性通讯重塑
  ├─ 某细胞类型同时是 sender 和 receiver → hub 细胞 → 追其内部状态（DE/SCENIC）
  └─ 只有一个方法的信号 → 降级（discovery_miner §3：单方法信号要交叉验证）
```

### 分支 E: 空间分析线（有空转数据时并行展开）

```
空间 domain detection → domain 间差异
  ├─ domain×celltype 组成不同 → 空间 niche 定义 → 追 niche 特异性基因（SVG）
  ├─ 某细胞在特定 domain 富集 → 空间共定位（nhood_enrichment）→ 为什么？（趋化因子？）
  ├─ 基因表达有空间梯度 → GASTON/IsoDepth → 梯度与 domain 边界一致？
  └─ 空间 CCC（COMMOT）→ 与单细胞 CCC 一致？不一致则空间 CCC 更可信（有共定位证据）
```

## Phase 5: 交叉验证与逻辑闭环

| 你发现了什么 | 怎么验证 | 验证通过 | 验证不通过 |
|---|---|---|---|
| "细胞 A 比例变化" | 是否伴随 A 的 DE 变化？ | 比例+分子双重支持 → 强证据 | 只有比例变没有分子变 → 可能是抽样偏差 |
| "细胞 A 和 B 通讯" | A 和 B 在空间上共定位吗？ | 共定位 → CCC 有空间支持 | 不共定位 → 降级为"推断性通讯" |
| "基因 X 沿轨迹变化" | X 在空间上有梯度吗？velocity 支持吗？ | 多维度一致 → 强证据 | 单维度 → 标注为"假说" |
| "通路 Y 在 disease 活跃" | Y 的多个基因一致变？独立队列也变？ | 通路级一致 → 可靠 | 单基因驱动 → 检查是否 artifact |

## 逻辑闭环检查（分析收尾前必查）

在交付前，agent 必须能回答以下问题——答不上来的说明分析链有断口：

1. **生物学结论的证据等级**：每个结论是"地图证据"（UMAP 着色）还是"定量证据"（DE/统计检验）？定量证据 ≥ 1 张？
2. **主角细胞的故事完整性**：选了主角 → 亚群 → 分子机制 → 互作/空间 → so-what，链路完整吗？
3. **反假说排除了吗**：比例变化不是抽样偏差？DE 不是 normalization artifact？CCC 不是单方法偶然？
4. **降级路径走了吗**：当证据不够时，是否标注为"假说/exploratory"而不是硬下结论？

## 自主分析的节奏（Core Rule 8 落地）

```
Batch 1: QC → preprocess → cluster → annotation（确立全景）
  → 暂停：与研究者讨论 celltype 命名、主角选择
Batch 2: DE + 富集 + 比例/丰度（主角的分子和组成变化）
  → 暂停：讨论哪个信号最强、值得追
Batch 3: CCC / 轨迹 / SCENIC（机制层面，基于 Batch 2 的方向）
  → 暂停：讨论机制假说
Batch 4: 空间验证（如果有空转）/ 交叉验证
  → 暂停：讨论最终故事框架
Batch 5: 交付（PPT/HTML report + 图 + 图注）
```

> **关键**：每个 batch 之间暂停一次，不是跑完所有分析再回头。生物学是 evidence-driven，不是 pipeline-driven。
