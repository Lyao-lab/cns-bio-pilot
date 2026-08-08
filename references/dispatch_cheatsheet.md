# 派发速查表（子智能体施工必守硬规则）

> **用途**：主智能体派发 worker/researcher 时，用一句"开工前读本文件并遵守全部硬规则"即可传递 skill 核心纪律，避免子智能体因看不到主会话上下文而违规。
> **来源**：浓缩自 SKILL.md Core Rules + meta_methodology + figure_guide + plotting_reference。
> **每条格式**：`[编号] 规则 | 违规后果 | 机检：脚本名/自觉`
> 子智能体只读本文件即可覆盖施工时 95% 的硬约束；需要完整决策表时再读对应 reference。

---

## 0. 分析代码模板位置（开工前必查）

分析代码模板已模块化到 `references/analysis/`，按分析阶段拆分——写分析代码前**必须查对应子模块**，不要凭记忆写（API 可能已更新）：
- **不知道该做什么分析？** 先查 `references/analysis/decision_guide.md`（生物学问题→分析方法决策表，28 个问题映射）
- **自主分析不知下一步追什么？** 查 `references/analysis/analysis_flow.md`（每步结果→下一步决策树）

| 分析任务 | 查这个文件 |
|---|---|
| QC / preprocess / 降维 / 聚类 / 批次校正 | `references/analysis/sc_basic.md` |
| 注释 / DE / 富集 / 差异丰度 / SCENIC / CNV | `references/analysis/sc_annotation.md` |
| 细胞通讯 / 轨迹 / Velocity / AUCell | `references/analysis/sc_downstream.md` |
| 空转（domain/SVG/去卷积/统计/Visium HD） | `references/analysis/spatial.md` |
| Bulk（DE/GSEA/WGCNA/PPI） | `references/analysis/bulk.md` |
| 分析纪律红线 | `references/analysis/discipline.md` |
| 数据 IO 速查 | `references/analysis/README.md` |

## A. 分析严谨性（违反 = 科学错误）

- **[A1] 基于事实不虚构**：每个数字/数据集/accession/API 必须有来源；缺失标 `[AUTHOR TO SPECIFY]`，绝不编造 | 虚构 = 论文造假 | 机检：postcheck F1（占位符/编造 accession）
- **[A2] 单细胞 DE 必须 pseudobulk**：禁止 per-cell Wilcoxon（假阳性膨胀）；sample×celltype 聚合 → DESeq2/edgeR；≥3 生物学重复，否则标 exploratory；用 `layers['counts']` 非 normalized | per-cell DE = 结论不可信 | 机检：postcheck D3/D4
- **[A3] counts layer 先存**：`adata.layers['counts'] = adata.X.copy()` 必须在 QC 前完成 | 缺 counts = DE/velocity 无法做 | 机检：postcheck A1
- **[A4] 批次校正后禁止 DE**：corrected embedding 不得当 raw counts 做 DE（疾病信号被抹除）；用 raw counts + pseudobulk | 批次校正数据做 DE = FAIL | 机检：postcheck D3
- **[A5] 每步存 checkpoint**：每个 major step 存 `checkpoints/XX_step.h5ad`；上游变化 → 从该步全部重算，禁复用旧 h5ad/DE/图 | 无 checkpoint = 无法回溯重算 | 机检：自觉
- **[A6] step-gate 每步自查**：QC 后查 mt%/doublet/每样本细胞数；聚类后查 marker 分布；DEG 后查 housekeeping 不得 top；富集后查非"整基因列表"；CCC 后查 L-R 方向 | 跳过自查 = 错误传到下游 | 机检：自觉（部分 postcheck D3/D4/C1 覆盖）
- **[A7] 组成数据禁 chi-square/Fisher**：比例和为 1 的 compositional 约束 → 必须 Milo/scCODA/propeller | 卡方检验比例 = 统计错误 | 机检：postcheck C1
- **[A8] 措辞纪律**：CCC 只能"associated with / enriched for"，禁"regulates/activates/drives"（无功能证据）；pseudotime 是排序不是时间；结论必须分级（已验证/数据支持/推测）| 过度因果措辞 = 审稿拒点 | 机检：postcheck L1/L2
- **[A9] 注释是假说非 ground truth**：层级注释（先 lineage 后 subtype）；auto-annotation 后必须 marker 人工验证；无 marker 的 cluster 标 Unknown 不硬凑 | 硬凑注释 = 错误结论 | 机检：自觉

## B. 绘图规范（违反 = 图不达标）

- **[B1] 必须 plot_xxx 统一入口**：用 cns_style 的 18 个 `plot_xxx` 函数（plot_umap/plot_volcano/...），内部自动 ov.pl 优先 + mpl 兜底；不手写 ov.pl.xxx / plt.savefig | 绕过 = 失去统一风格 + 降级保护 | 机检：自觉
- **[B2] save_panel 强制收尾**：保存走 `save_panel(fig, name, fmt='pdf')`，它强制 finalize_figure + 建 panels/ + tight bbox；不用 plt.savefig 替代 | 不用 = 图未过 finalize 检查 | 机检：自觉
- **[B3] finalize_figure 强制**：每张图 savefig 前过 `finalize_figure(fig)`：自动右移图例 + 检测文字重叠 + 栅格化警告 | 跳过 = 图例遮数据/文字重叠 | 机检：finalize_figure 内置
- **[B4] 全局开头 3 行**：每个绘图脚本顶部 `import cns_style` + `set_cns_style_journal('nature')`（自动 Morlandi 配色/Arial/字号/DPI） | 缺 = 默认丑样式 | 机检：自觉
- **[B5] 绘图前 assert**：`assert_anndata_keys(adata, obs_cols=[...], obsm_keys=[...])` 校验 key 存在 | 缺 = 运行到一半 KeyError | 机检：assert_anndata_keys 内置
- **[B6] 数据→图型查决策表**：不确定选什么图时查 figure_guide.md §0.1；反模式：per-cell Wilcoxon 的 DE 禁画 volcano、无重复堆叠柱禁做条件比较、UMAP 不全场多次 | 乱选图 = 审稿拒点 | 机检：自觉
- **[B7] 配色锁 manifest**：默认 Morlandi + CONDITION_COLORS，全论文同 cell type 同色；禁 tab20/jet | 配色乱 = 跨图不可比 | 机检：自觉

## C. API 自适应（违反 = 运行时崩溃）

- **[C1] inspect.signature 验证**：调用任何 ov.*/pt.*/sc.* 函数前 `inspect.signature(func)` 验证参数名；不匹配则读实际签名适配，不硬编码假设 | 硬编码 = 参数改名即崩 | 机检：自觉（LLM 包幻觉率 9-20%）
- **[C2] api_check --diff**：pip upgrade / 环境变更后跑 `python scripts/api_check.py --diff` | 不跑 = 文档 API 可能已失效 | 机检：api_check.py
- **[C3] compat.yaml 唯一版本源**：版本以 compat.yaml 为准，文档不硬编码版本号 | 硬编码 = 版本漂移 | 机检：api_check.py --diff 检测旧版本引用
- **[C4] 已知坑位避让**：`ov.pp.qc` 无 mt_thresh（用 `tresh={'mito_perc':...}`）；`ov.single.batch_correction` 参数是 methods(复数)；scVI 后邻居用 `use_rep='X_scVI'` | 踩坑 = 静默错误 | 机检：自觉（omicverse-pipeline/SKILL.md 有完整坑位表）

## D. 结果驱动迭代（违反 = 故事断裂）

- **[D1] Phase R 触发节点**：每个分析 batch 结束（QC+cluster+annotation / 第一轮 DE / CCC / spatial mapping）后、下一个 batch 前，必须回 research-planner Phase R，禁端到端自动跑 | 跳过 = 带着漏洞往下走 | 机检：自觉（R3 是人工硬门）
- **[D2] Phase R 四步全跑**：R1 结果解读（更新台账 supported/refuted/inconclusive + unexpected 排雷）→ R2 提取决策点 → R3 讨论 checkpoint（硬门，暂停等 researcher）→ R4 重规划 | 漏步 = 决策无依据 | 机检：自觉
- **[D3] 假设台账创建时机**：research-planner 进入 → Step 8 建台账；data-first 直进管线 → §0 Init 立即建迷你台账（至少 H1 + status:pending + unexpected slot） | 无台账 = Phase R 无物可消费 | 机检：自觉
- **[D4] 台账更新规则**：结论不在台账中 = post-hoc/exploratory 必须标注；unexpected findings 以 `basis: post-hoc` 入台账；循环终止 = ≥1 supported 假设 + 因果链过 gap scan + researcher 同意 | 不更新 = post-hoc 当预设结论 | 机检：自觉
- **[D5] provenance 强制**：§0 Init 建 `analysis_log.md`，每 major step 追加参数/阈值/方法/seed/数据 md5/版本 | 缺 = 不可复现 | 机检：自觉
- **[D6] autopilot 例外**：仅当用户明确授权"跑完别停"时连续跑，但交付前必须做一次完整 Phase R（R1+R2），授权记录进 analysis_log | 未授权却自动跑 = 跳过人工门 | 机检：自觉

---

## 派发模板（主智能体复制使用）

**通用生信/绘图任务**：
```
[规则] 开工前读 <skill根目录>/references/dispatch_cheatsheet.md 并遵守 A-D 全部硬规则。
特别注意：[列出本任务最相关的 2-3 条编号，如 A2 pseudobulk + A5 checkpoint + B1 plot_xxx]。
```

**窄任务（只需 2-3 条）**：
```
[规则] 本任务必须遵守：[A2] pseudobulk DE（禁 per-cell Wilcoxon）；[A4] 批次校正后禁 DE。
[验收] 完成后跑 python scripts/postcheck.py <产物> --type de，FAIL 必须修。
```

**需要完整决策表**：
```
[规则] 开工前读 <skill根目录>/references/figure_guide.md §0.1 数据→图型决策表，按表选图型。
```

## 机检脚本速查（验收时跑）
| 产物类型 | 脚本 | 覆盖规则 |
|---|---|---|
| DE/deconv/CCC/composition | `scripts/postcheck.py <产物> --type <类型>` | A1-A8（D3/D4/L1/L2/C1/F1） |
| PPT | `qa_deck.py` + `validate_presentation.py` | A1（占位符）+ 字号/几何 |
| 包升级/环境变更 | `scripts/api_check.py --diff` | C2/C3 |
| 绘图 | （finalize_figure 内置） | B3 |
