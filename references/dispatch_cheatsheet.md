# 执行速查表（任何执行体施工必守硬规则）

> **适用对象 = "执行者"**：写/跑分析或绘图代码的任何一方——主智能体自己、任意名称的子智能体（worker/researcher/executor/Explore/…）、或根本没有子智能体时的直接执行。
> **用途**：执行者凡未读过 skill 主文档（任何子智能体天然如此——不论叫什么名字），注入一句"开工前读本文件并遵守全部硬规则"即可传递 skill 核心纪律，避免其因看不到主会话上下文而违规。主智能体自己执行时同样适用本表（尤其 A2/A4/B1-B3）。
> **来源**：浓缩自 SKILL.md Core Rules + meta_methodology + figure_guide + plotting_reference。
> **每条格式**：`[编号] 规则 | 违规后果 | 机检：脚本名/自觉`
> 只读本文件即可覆盖施工时 95% 的硬约束；需要完整决策表时再读对应 reference。（6 系 35 条：A 分析 10 / B 绘图 9 / C API 4 / D 迭代 6 / E 组合体 6——E 系每条较详，细节查 `references/bigfig_deck_playbook.md`）

---

## 0. 分析代码模板位置（开工前必查）

分析代码已分层：**知识层**（决策/为什么，无代码）在 `references/analysis/`，**代码模板层**（可执行，唯一拷贝源）在 `references/analysis/templates/`——写分析代码前**必须查对应模板**，不要凭记忆写（API 可能已更新）：
- **不知道该做什么分析？** 先查 `references/analysis/decision_guide.md`（生物学问题→分析方法决策表，34 个问题映射）
- **自主分析不知下一步追什么？** 查 `references/analysis/analysis_flow.md`（每步结果→下一步决策树）
- **想像高分文章一样设计分析路线？** 查 `references/analysis/paper_paradigms.md`（3 种分析主干 + 主角细胞选择 + 空间验证模式）

| 分析任务 | 查这个文件 |
|---|---|
| QC / preprocess / 降维 / 聚类 / 批次校正 | `references/analysis/templates/sc_basic.md` |
| 注释 / DE / 富集 / 差异丰度 / SCENIC / CNV | `references/analysis/templates/sc_annotation.md` |
| 细胞通讯 / 轨迹 / Velocity / AUCell | `references/analysis/templates/sc_downstream.md` |
| 扰动 / Perturb-seq / in silico 状态预测 | `references/analysis/templates/sc_perturbation_state.md` |
| 空转（domain/SVG/去卷积/统计/Visium HD） | `references/analysis/templates/spatial.md` |
| Bulk（DE/GSEA/WGCNA/PPI） | `references/analysis/templates/bulk.md` |
| 分析纪律红线 | `references/analysis/discipline.md` |
| 数据 IO + 全局 import | `references/analysis/templates/setup.md` |
| 代码落 ipynb 台账（无内核 CLI 执行时） | `scripts/nb_log.py`（规则 A10） |

## A. 分析严谨性（违反 = 科学错误）

- **[A1] 基于事实不虚构**：每个数字/数据集/accession/API 必须有来源；缺失标 `[AUTHOR TO SPECIFY]`，绝不编造 | 虚构 = 论文造假 | 机检：postcheck F1（占位符/编造 accession）
- **[A2] 单细胞 DE 必须 pseudobulk**（显著性三层口径见 `references/analysis/stats_convention.md`：名义/BH校正/CI；跨产物数字只许引唯一计算源表）：禁止 per-cell Wilcoxon（假阳性膨胀）；sample×celltype 聚合 → DESeq2/edgeR；≥3 生物学重复，否则标 exploratory；用 `layers['counts']` 非 normalized | per-cell DE = 结论不可信 | 机检：postcheck D3/D4
- **[A3] counts layer 先存**：`adata.layers['counts'] = adata.X.copy()` 必须在 QC 前完成 | 缺 counts = DE/velocity 无法做 | 机检：postcheck A1
- **[A4] 批次校正后禁止 DE**：corrected embedding 不得当 raw counts 做 DE（疾病信号被抹除）；用 raw counts + pseudobulk | 批次校正数据做 DE = FAIL | 机检：postcheck D3
- **[A5] 每步存 checkpoint**：每个 major step 存 `checkpoints/XX_step.h5ad`；上游变化 → 从该步全部重算，禁复用旧 h5ad/DE/图 | 无 checkpoint = 无法回溯重算 | 机检：自觉
- **[A6] step-gate 每步自查**：QC 后查 mt%/doublet/每样本细胞数；聚类后查 marker 分布；DEG 后查 housekeeping 不得 top；富集后查非"整基因列表"；CCC 后查 L-R 方向 | 跳过自查 = 错误传到下游 | 机检：自觉（部分 postcheck D3/D4/C1 覆盖）
- **[A7] 组成数据禁 chi-square/Fisher**：比例和为 1 的 compositional 约束 → 必须 Milo/scCODA/propeller | 卡方检验比例 = 统计错误 | 机检：postcheck C1
- **[A8] 措辞纪律**：CCC 只能"associated with / enriched for"，禁"regulates/activates/drives"（无功能证据）；pseudotime 是排序不是时间；结论必须分级（已验证/数据支持/推测）| 过度因果措辞 = 审稿拒点 | 机检：postcheck L1/L2
- **[A9] 注释是假说非 ground truth**：层级注释（先 lineage 后 subtype）；auto-annotation 后必须 marker 人工验证；无 marker 的 cluster 标 Unknown 不硬凑 | 硬凑注释 = 错误结论 | 机检：自觉
- **[A10] 代码必须落 ipynb 台账**：每任务一个 `notebooks/NN_task.ipynb` 开工即建；有 Jupyter 内核 → 直接在 notebook 分 cell 执行；无内核（CLI 执行，子智能体默认）→ 每步执行成功后立刻 `python scripts/nb_log.py <nb> -t "步骤名" -c step.py -o step.log` 把实际执行代码 + stdout 追加进 notebook（关键图加 `-f panels/X.png` 嵌入 cell 输出）| 代码不落账 = 分析不可复现（等同没跑），验收不通过 | 机检：验收时查 notebook 存在且含各步 code cell

## B. 绘图规范（违反 = 图不达标）

- **[B1] 必须 plot_xxx 统一入口**：用 cns_style 的 51 个 `plot_xxx` 函数（plot_umap/plot_volcano/plot_sankey/plot_cnv_heatmap/...，完整清单见 plotting_reference §0 速查卡 / tool_registry.md），内部自动 ov.pl 优先 + mpl 兜底；不手写 ov.pl.xxx / plt.savefig | 绕过 = 失去统一风格 + 降级保护 | 机检：自觉
- **[B2] save_panel 强制收尾**：保存走 `save_panel(fig, name, fmt='pdf')`，它强制 finalize_figure + 建 panels/ + tight bbox；不用 plt.savefig 替代 | 不用 = 图未过 finalize 检查 | 机检：自觉
- **[B3] finalize_figure 强制**：每张图 savefig 前过 `finalize_figure(fig)`：自动右移图例 + 检测文字重叠 + 栅格化警告 | 跳过 = 图例遮数据/文字重叠 | 机检：finalize_figure 内置
- **[B4] 全局开头 3 行**：每个绘图脚本顶部 `import cns_style` + `set_cns_style_journal('nature')`（自动 Morlandi 配色/Arial/字号/DPI） | 缺 = 默认丑样式 | 机检：自觉
- **[B5] 绘图前 assert**：`assert_anndata_keys(adata, obs_cols=[...], obsm_keys=[...])` 校验 key 存在 | 缺 = 运行到一半 KeyError | 机检：assert_anndata_keys 内置
- **[B6] 数据→图型查决策表**：不确定选什么图时查 figure_guide.md §0.1；反模式：per-cell Wilcoxon 的 DE 禁画 volcano、无重复堆叠柱禁做条件比较、UMAP 不全场多次 | 乱选图 = 审稿拒点 | 机检：自觉
- **[B7] 配色锁 manifest**：默认 Morlandi + CONDITION_COLORS，全论文同 cell type 同色；禁 tab20/jet | 配色乱 = 跨图不可比 | 机检：自觉
- **[B8] 画布级文字重叠断言**：finalize_figure 只查 ax.texts；`ax.title`、刻度标签、图例必须在脚本里另做 pairwise bbox 断言（`assert_no_text_overlap`）；字号最后设定——`ax.tick_params(labelsize=...)` 会静默覆盖 `set_yticklabels(fontsize=...)` | 漏 = 渲染放大后逐层返工 | 机检：assert_no_text_overlap（raise 版验收门）
- **[B9] 版面字面量防截断**：加构/裁剪/缩放后必须断言"全部文本 artist 在画布内"（tight bbox 会把越界文本包进 PNG，反而把图撑宽失真）；窄轴放不下 N 个刻度名时用数字刻度+键并入脚注 | 漏 = 图在组合体里被裁/变形 | 机检：edge_sweep.py（组合体）+ 自觉（单图）

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

## E. 组合体与交付（大 fig / 多面板 deck；违反 = 渲染放大后才暴露的系统性返工）

- **[E1] deck-as-code 流水线**：draw(每面板脚本+save_panel) → compose(几何/排布) → build(shrink→fit_captions→place_panels) → render 预览 → 像素门。完整模板与顺序见 `references/bigfig_deck_playbook.md` §1 | 跳步 = 缓存/几何类缺陷静默进交付 | 机检：自觉
- **[E2] 行宽公式扣间隙**：多面板行高 = (W − 间隙×(n−1))/Σar；漏扣 → 行块宽于画布、居中把边缘面板推出界（"左缘截断"真因不是缺边距）。组合体外加 ~0.15in 白边 | 边缘面板出画布 | 机检：边缘像素扫描
- **[E3] 渲染保真**：自写 preview renderer 必须真实字号、按**文本框宽**换行（PIL 量宽，Bold/Oblique 族）、段落级字号回退；字号物理放大（fs×100/72）或按画布宽换行 → 全 deck caption"截断"是幻影，验收结论全错 | 机检：抽一页用真实渲染核对
- **[E4] 内容寻址缓存**：派生文件名含 内容hash+max_px（`{stem}_{px}_{md5[:12]}.png`）；按输出路径直接复用的缓存（裁剪/合成图）必须校验源 mtime/hash | 旧版本静默进交付物 | 机检：嵌入 md5 == 派生链末文件 md5（逐页）
- **[E5] 像素级验收门**：每页底/右/顶缘深色像素占比扫描（>1% = 文字出界；caption 截断类字级检查测不出）+ 视觉门只读渲染后 PNG、每页一行 JSON、必须给可定位证据（幻觉不接） | 缺 = 截断/重叠进最终交付 | 机检：自觉（playbook §4 清单）
- **[E6] 组合叙事一致**：大 fig 先行、deck 按分区拆页、caption 与大 fig 分区标题一致 | 两处叙事漂移 = 答辩翻车点 | 机检：自觉

---

## 注入模板（给看不到 skill 主文档的执行者；主智能体自用则跳过注入、直接照表执行）

**通用生信/绘图任务**：
```
[规则] 开工前读 <skill根目录>/references/dispatch_cheatsheet.md 并遵守 A-E 全部硬规则。
特别注意：[列出本任务最相关的 2-3 条编号，如 A2 pseudobulk + A5 checkpoint + B1 plot_xxx]。
```

**大 fig / 多面板 deck / PPT 组合体任务**：
```
[规则] 开工前读 <skill根目录>/references/bigfig_deck_playbook.md 并遵守 E1-E6 全部硬规则。
特别注意：[E2 行宽扣间隙 + E4 内容寻址缓存 + E5 像素级验收门]。
```
组合体任务下限：注入清单必须含 [A10]（ipynb 台账）+ [E4]（缓存纪律）。

**窄任务（只需 2-3 条）**：
```
[规则] 本任务必须遵守：[A2] pseudobulk DE（禁 per-cell Wilcoxon）；[A4] 批次校正后禁 DE。
[验收] 完成后跑 python scripts/postcheck.py <产物> --type de，FAIL 必须修。
```
窄任务下限：凡任务会执行分析/绘图代码，[A10] ipynb 台账必须列入注入清单（与具体分析类型无关，总适用；R 代码 `--kernel r`）。

**需要完整决策表**：
```
[规则] 开工前读 <skill根目录>/references/figure_guide.md §0.1 数据→图型决策表，按表选图型。
```

## 机检脚本速查（验收时跑）
| 产物类型 | 脚本 | 覆盖规则 |
|---|---|---|
| DE/deconv/CCC/composition | `scripts/postcheck.py <产物> --type <类型>` | A1-A8（D3/D4/L1/L2/C1/F1） |
| ipynb 代码台账 | 验收时查 `notebooks/*.ipynb` 存在且含各步 code cell | A10 |
| PPT | `qa_deck.py` + `validate_presentation.py` | A1（占位符）+ 字号/几何 |
| 包升级/环境变更 | `scripts/api_check.py --diff` | C2/C3 |
| 绘图 | （finalize_figure 内置） | B3 |
| 组合体像素门 | `scripts/edge_sweep.py <render_dir>`（逐页底/右/顶缘扫描，exit≠0 = 截断） | E5 |
| 组合体几何/嵌入链/备注 | `scripts/deck_gate.py deck.pptx --expected '{...}' [--embed-map '{...}'] [--notes-block 方法,意义]`（exit≠0 = 截断/越界/旧图/缺备注段） | E4/E5 |
| 大 fig 拼版 | `scripts/compose_bigfig.py sections.json out.png`（行宽扣间隙/分区标题带/边距） | E1/E2 |
| 渲染预览（保真） | `scripts/render_slides.py deck.pptx /tmp/dir`（真实字号+按框宽换行） | E3 |
