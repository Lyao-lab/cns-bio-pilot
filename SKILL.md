---
name: cns-bio-pilot
description: 生信分析全流程技能库（空间转录组、单细胞、bulk 组学 + 发表级绘图 + 论文/PPT/网页报告产出）。当用户要做生信分析、处理单细胞/空转/空间组学数据、画发表级图表、写论文/PPT/汇报、构建生物学故事时触发；即使任务只涉及其中一个环节（只画一张图、只做一次差异分析、只写一段 Methods）也应使用本技能。
compatibility: Requires Python 3.11+ with omicverse/scanpy (conda env 'sc'), scvelo (env 'regvelo'), squidpy (env 'st'), R 4.5.3 with scop 0.8.9. See compat.yaml for version details.
license: GPL-3.0
metadata:
  version: "23.4"
  author: Lyao-lab
---

# CNS Bio-Pilot — Router

Read this file → pick ONE sub-skill → read that sub-skill's SKILL.md → execute (honoring Core Rule 8 batch checkpoints — do not auto-run a pipeline end-to-end). Never load multiple sub-skills at once.

## ⚠️ Dispatch Injection (read before delegating ANY sub-task)

When you delegate any analysis/plotting/API-calling work to a sub-agent (**any sub-agent — regardless of its name/type: worker, researcher, executor, explore, general-purpose, ...**), that sub-agent does NOT load this skill and cannot see this conversation. **Rules not written into the dispatch prompt do not exist for the sub-agent.** (If you execute the work yourself, you already have these rules in context — no injection needed, just follow them.)

**作用域注入（2026-10-10 架构减重）**：禁止 wholesale「遵守 A-E 全部」。规则按适用面分层——**核心九条（A1 诚实溯源 / A2 pseudobulk / A3 counts / A4 校正后禁 DE / A5 checkpoint / A6 step-gate / A7 组成禁卡方 / A8 措辞分级 / A10 台账）全任务适用**；其余按任务类型带：

- **(分析任务)** `读 <skill根目录>/references/dispatch_cheatsheet.md，执行【文首元规则 + §A + §C】（§B/§D/§E 与本任务无关，不适用）；涉注释加 A9、重算旧标签加 A11、ML 加 A12。特别注意：[2-3 条编号]。`
- **(绘图任务)** `读 ... dispatch_cheatsheet.md，执行【文首元规则 + §B + 核心九条中的 A1/A8/A10 + §C】。特别注意：[如 B1 统一入口 + B8 重叠断言]。`
- **(组合体：大 fig / deck / PPT)** `读 ... bigfig_deck_playbook.md 遵守 E1-E7（E4 缓存 + E5 像素门 + E7 数字门）；cheatsheet 只取 A10 + §B 的 B1-B3。`
- **(多 worker 并行)** `读 ... orchestration_playbook.md 遵守 O1-O5（O2 spec 契约 + O3 写者纪律）；cheatsheet 只取 A10 + E4。`
- **(narrow task ≤30min)** paste the 2-3 relevant rules directly (e.g. `[A2] pseudobulk DE; [A4] 批次校正后禁 DE`)——但 **[A10] 台账必含**
- **(needs decision table)** `读 <skill根目录>/references/figure_guide.md §0.1 数据→图型决策表`

> §D 系是主 agent 回路规则（Phase R 人门），**原则上不注入子 agent**（cheatsheet §D 头注有子 agent 替代动作）。

`dispatch_cheatsheet.md` condenses the hard rules (A1-A12 / B1-B9 / C1-C4 / D1-D7 / E1-E7) into ~125 lines — single source, 作用域由注入模板选择（不拆文件防计数漂移）；**计数以文件实际编号为准，机检（consistency_check C5）自动对账**。**Skipping injection = the sub-agent will violate rules it never saw.**

## Quick Route（关键词→子skill 索引，borrowed from Biomni prompt-retriever）

用户说短句时按关键词快速命中，无需扫全表。**三条裁决规则（关键词多行命中时按此定归属）**：① **意图优先**——分析诉求（找 DE/找亚群）优先于顺带提到的绘图词；已产出的图要"美化/拼图"时归 `figure-production`；② **专属分析词优先于泛绘图词**——"画 KM 曲线"归 `omicverse-bulk`（KM 是专属行），"画 figure"归 `figure-production`；③ **平台优先级**见表尾注（高分空转平台命中一律 multiomics）。
**行类型约定**：输出子 skill 的行是执行型；输出带 `ref:` 前缀指向 references/ 下文件的行是**知识查询型**（只读参考、无执行体）——出现第二个知识查询行时沿用此前缀。**本表到 50 行时按 single-cell / spatial / 可视化 / 产出四组重排，不再平铺追加。**

| 关键词 | 子skill |
|---|---|
| umap / tsne / 聚类 / 分群 / annotate / 注释 | `single-cell/omicverse-pipeline` §2-4（UMAP 仅作拼图素材时归 `figure-production`）|
| 拟时序 / pseudotime / trajectory / monocle | `omicverse-pipeline`（§7 轨迹；fate/velocity 推断归 `rna-velocity`）|
| 差异基因 / DE / volcano / marker / 筛选 | `omicverse-pipeline` §8.5（DE 已算好、只求发表级美化时归 `figure-production`）|
| 细胞比例 / 组成 / Milo / 丰度 / proportion | `omicverse-pipeline` §9c |
| 通讯 / CCC / CellChat / LR / ligand | `omicverse-pipeline` §9 |
| 空间 / Visium / 空转 / Xenium / spot / spatial | `spatial/omicverse-spatial` |
| 空间 domain / niche / 区域 / STAGATE / CAST | `spatial/omicverse-spatial` §domain |
| 共定位 / colocalization / 空间邻近 / 邻域富集 / nhood | `spatial/omicverse-spatial`（模板 `analysis/templates/spatial.md` 统计段：nhood_enrichment/co_occurrence）|
| 空间变异基因 / SVG / spatial variable / Moran | `spatial/omicverse-spatial`（同上 spatial.md 统计段：svg/spatial_autocorr/sepal）|
| 空间统计 / Ripley / centrality / 空间分布 | `spatial/omicverse-spatial`（同上 spatial.md 统计段：ripley/centrality_scores）|
| 去卷积 / cell2location / deconv / Tangram | `spatial/deconvolution`（Python 五法 + scop R 系 SPOTlight/CARD）|
| 高分空转 / Visium HD / Stereo-seq / MERFISH | `spatial/multiomics` |
| 蛋白组 / CODEX / IMC / MIBI | `spatial/proteomics` |
| 速度 / velocity / RNA velocity / fate | `single-cell/rna-velocity` |
| 扰动 / Perturb-seq / perturbation / State / 虚拟细胞 / virtual cell / 药物响应预测 | `single-cell/perturbation`（in silico 预测是诉求主体时本行优先，被扰动的靶点如 TF 只是对象）|
| R / Seurat / scop | `single-cell/scop` |
| bulk / 路径 / 通路 / enrichment / 富集 | `general-bio/omicverse-bulk` |
| CNV / inferCNV / copykat | `omicverse-pipeline` |
| 转录因子 / TF / regulon / SCENIC / GRN | `omicverse-pipeline`（模板 `analysis/templates/sc_annotation.md` SCENIC 段）|
| 生存分析 / survival / KM / Kaplan | `general-bio/omicverse-bulk`（ov.pl.kaplan_meier/survival）|
| 画图 / 绘图 / figure / panel / 拼图 | `visualization/figure-production` |
| 绘图特型（Sankey/CNV 热图/轴梯度 zonation/克隆扩增 TCR/雷达/统计量 dotplot） | `visualization/figure-production`（完整图型→入口速查：plotting_reference §0 + figure_guide §0.1）|
| **知识查询型全族**（主图顺序/护栏边界/并行编排/空转选型与 2026 基准/3D 重建/多样本空间统计/microniche/稳健性加固/深审查数字门/统计口径/踩坑 inbox/外部数据库） | `ref:references/route_index.md`（**grep 关键词即查**，命中行右端为目标文档；本行是唯一入口，不逐条展开）|
| 机制图 / 流程图 / schematic / 图形摘要 | `visualization/scientific-schematics` |
| PPT / 汇报 / 幻灯片 / slides / 答辩 | `presentation/scientific-slides` |
| 网页报告 / HTML / report / 在线分享 / web report | `presentation/web-report` |
| 论文 / manuscript / methods / 写作 | `presentation/manuscript-writing` |
| 研究设计 / 规划 / study design | `single-cell/research-planner` |

> **优先级**：平台关键词（高分空转 / Visium HD / Stereo-seq / MERFISH / Slide-seq）命中时一律走 `spatial/multiomics`，其流程内已覆盖 binning 后的聚类/domain 等分析；上表中的 domain / 共定位 / SVG / Ripley 等分析关键词仅对常规分辨率平台（Visium / Xenium）指向 `spatial/omicverse-spatial`。
> **无命中兜底（越界任务）**：Quick Route 与 Routing Table 均不命中（如 ATAC-seq/ChIP/flow cytometry/宏基因组等本库未覆盖的组学）→ **不加载任何子 skill**，仅以 Core Rules（0-10）+ 用户指令直接执行，并在台账注明「无子 skill 覆盖」；不硬选近似子 skill。复合任务（一句话含分析+绘图+交付）走串行链：分析 skill → Core Rule 8 人门 → `figure-production` → Core Rule 10 交付 skill，逐段交接而非一次全派。

## Routing Table

| Task | Sub-skill | Engine |
|---|---|---|
| scRNA-seq full pipeline (QC→cluster→annotate→DE→CCC→trajectory) | `single-cell/omicverse-pipeline` | omicverse (Python) |
| R/Seurat pipeline or scop-wrapped tools (133 Run\* verbs) | `single-cell/scop` | scop (R) |
| RNA velocity / fate inference | `single-cell/rna-velocity` | omicverse + scvelo |
| Perturbation (measured Perturb-seq OR in silico prediction) | `single-cell/perturbation` | pertpy / CellOracle / scop / Arc State (arc-state CLI) |
| Study design / research planning (pre-analysis) | `single-cell/research-planner` | zero-code methodology |
| Spatial transcriptomics (Visium/Xenium/Stereo-seq; domains/SVG/CCC) | `spatial/omicverse-spatial` | omicverse ov.space |
| Spatial deconvolution (cell2location/RCTD/Tangram/SPOTlight/CARD) | `spatial/deconvolution` | omicverse / scop |
| High-res spatial (Visium HD/Slide-seq/MERFISH; segmentation/binning) | `spatial/multiomics` | squidpy + spatialdata |
| Spatial proteomics (CODEX/IMC/MIBI) | `spatial/proteomics` | scimap |
| Bulk RNA-seq / pathway / enrichment | `general-bio/omicverse-bulk` | omicverse ov.bulk |
| Cell-type proportion / differential abundance (Milo/scCODA/propeller) | `single-cell/omicverse-pipeline` §9c (or scop RunMilo/RunscCODA) | omicverse / scop |
| CNV inference / inferCNV / copykat | `single-cell/omicverse-pipeline` (or scop RunCNV) | omicverse / scop |
| **Figures** (iterative: design A → look → adjust B → ... → assemble) | `visualization/figure-production` | cns_style 包 + ov.pl |
| Schematics / mechanism diagrams / graphical abstract | `visualization/scientific-schematics` | matplotlib + networkx (纯代码模板) |
| **Manuscript writing** (Methods / Results / Figure Legends) | `presentation/manuscript-writing` | LLM |
| Slides (lab meeting / conference / defense) | `presentation/scientific-slides` | python-pptx / Beamer |
| **Web report** / HTML report / 在线分享结果 | `presentation/web-report` | Python 标准库（自包含 HTML）|

## Environments

| Env | Contents | Activate |
|---|---|---|
| `sc` | omicverse (see `compat.yaml`) + scanpy + scvi + spatialdata + pertpy + squidpy 1.8.2 + tangram-sc 1.0.4 | `conda activate sc` |
| `st` | squidpy 1.8.2 + decoupler 2.2.0 | `conda activate st` |
| `regvelo` | scvelo 0.3.4（原生 scvelo/RegVelo 引擎；sc env 无 scvelo——2026-09-21 实测） | `conda activate regvelo` |
| `scop_env` (conda) | R 4.5.3 + scop 0.8.9 + Seurat | `~/miniforge3/envs/scop_env/bin/Rscript` |
| `state` (uv tool) | Arc State 扰动预测 CLI（PyTorch；独立环境，GPU；版本见 compat.yaml `arc-state`） | `uv tool install arc-state` |

Package versions: **`compat.yaml`** (single source of truth). After any upgrade: `python scripts/api_check.py --diff`.

## Core Rules (stated once — sub-skills do not repeat these)

0. **判断优先于流程（Rule 0）**——本 skill 的规则是**护栏不是剧本**：守不变量、给出理由，方案随数据而变。
   - **护栏（非协商，违反=出错）**：全集见 `references/guards_vs_guides.md` §2 的 **G1-G10**（诚实溯源 / pseudobulk DE / counts 先行 / 校正后禁 DE / 组成禁卡方 / 口径声明+版本切换 / notebook 台账 / 机检门 / 数字门 / ML 泄漏隔离）。
   - **自适应（数据/证据驱动，按需偏离但说明理由）**：选哪个方法、跑几个批次、面板怎么排、故事怎么组织——`analysis_flow.md` / `figure_guide` / `paper_paradigms` / `spatial_frontiers_2026` 是**决策参考不是模板**。
   - **偏离纪律**：护栏不可绕；自适应项可偏离但必须在分析日志注明「偏了哪条、为什么（数据证据）」。
   - **遇到冲突/新情况**：护栏之间冲突或规则未覆盖时，优先级 = 用户指令 > 数据证据 > 护栏；把冲突写进台账，不静默二选一。
1. **Fact-based; ask when unsure; never fabricate.** Every number/dataset/accession/API must have a source. Missing info → `[AUTHOR TO SPECIFY]`.
2. **Pseudobulk for single-cell DE.** Per-cell Wilcoxon inflates false positives. Aggregate by sample×celltype → DESeq2/edgeR.
3. **Search before implementing — 先查已执行产物（RULE ZERO），再查轮子，最后才自写。** ①执行任何分析前，先扫项目内已有产物：`analysis/` 下 h5ad/csv/`*_executed.ipynb`、`INDEX.md`、checkpoints——命中则**直接引用不复算**（重跑会产生与已归档答案不同的数字，且慢 5-10 倍；口径以归档表为准，E7）；②新分析按 omicverse/scop wrapper → standalone package → R/Bioconductor → adapt → from-scratch 顺序找现成实现；GEO → GEOparse；③**加载任何主数据前先跑 `scripts/data_sanity.py <path>`**（分析前坏数据/诱饵门：常数矩阵/错物种/FASTQ N% 超标/metadata 错配——FAIL 必须停下修数据，禁"绕过去"）。
4. **Postcheck is mandatory** *(automated, per-analysis)*. After any quantitative analysis (DE/deconvolution/CCC/composition), run `python scripts/postcheck.py`. FAIL must be resolved before proceeding. **Acceptance gate**: when the main agent accepts a bioinformatics deliverable from **any executor** (a sub-agent of any name, or a result it produced itself), it must confirm the matching machine-check has run and PASSED — `postcheck.py` after DE/deconv/CCC/composition; `qa_deck.py` + `validate_presentation.py` after PPT; `api_check.py --diff` after package upgrades. If the executor did not attach machine-check output, the main agent re-runs it before accepting. For the full rule set that executors must follow, see `references/dispatch_cheatsheet.md` (condensed hard rules A1-A11 / B1-B9 / C1-C4 / D1-D6 / E1-E7) — inject it into dispatch prompts per the ⚠️ Dispatch Injection section at the top of this file.
5. **Save checkpoints.** After each major step (QC/cluster/annotation/DE), save `adata.write_h5ad('checkpoints/XX_step.h5ad')`. Upstream changes → re-run from last valid checkpoint.
6. **Runtime API self-adaptation.** Do NOT trust hardcoded version numbers or assume API signatures. Before calling any ov.*/pt.*/sc.* function for the first time, verify with `inspect.signature(func)`. Run `python scripts/api_check.py --diff` after any package upgrade.
7. **Step-gate + hypothesis ledger** *(agent self-check, per-step)*. Every analysis follows meta_methodology §7 (step-gate sanity checks after each step) and §8 (hypothesis ledger + provenance + conclusion grading).
   > *Rationale*: The planner-verifier dual loop is the proven-optimal pattern for bioinformatics agents (K-Dense Analyst outperforms single-model by 6 points on BixBench via per-step verification).
8. **Result-driven iteration** *(human gate, per-batch)*. Biology is evidence-driven, NOT linear like software. After each analysis batch: review results → **discuss direction with researcher** → revise plan → next batch. Pause for researcher input on decisions that need human judgment (cell-type naming, which signal to chase, threshold calibration). Full procedure: `research-planner` Phase R. **Autopilot exception**: if the user explicitly authorizes "just run it through, don't stop at every step", agent may merge batches into a continuous run, but MUST do one full Phase R review (R1 ledger update + R2 decision-point retro) before final delivery, and record the authorization in `analysis_log.md`.
   > *Rationale*: A pipeline that auto-runs QC→cluster→DE→CCC→figures without pausing to interpret results produces data dredging, not science. But a rule that ignores real usage ("跑完别停") gets silently bypassed — the autopilot exception keeps the ledger alive while respecting user autonomy.
9. **Notebook is the code ledger** *(one .ipynb per task — mandatory in BOTH execution modes)*. Analysis and plotting code lives in Jupyter notebooks (.ipynb), one task per notebook (`notebooks/NN_task.ipynb`, created at task start — before writing any code). Structure: Cell 1 = shared setup (imports + `set_cns_style` + load data, run once); subsequent cells = one logical step each (one QC step, one panel, one DE round). Two execution modes, same persistence duty:
   - **Kernel mode** (Jupyter kernel available): run cells in the notebook; re-run only the cell you change — data stays in memory across cells. `save_panel` auto-displays figures in notebook output (`show=None` detects Jupyter → figure shows in cell + PDF saved to disk).
   - **CLI mode** (no Jupyter kernel — the default for sub-agents): execute each step as a temp script, then immediately append the exact executed code + stdout + key figures into the task notebook: `python scripts/nb_log.py <nb> -t "step" -c step.py -o step.log -f panels/X.png` (auto-creates the notebook; embeds figures as cell outputs). CLI changes the execution path, NOT the persistence duty — **code that never lands in the .ipynb counts as not run** (irreproducible). Figures in CLI mode save double format via `save_panel(fig, name, fmt='png+pdf')` — PNG for self-inspection (Read it before the next panel) + PDF for vector delivery.
   Checkpoints (Rule 5) and `analysis_log` (meta §8b) are the data/provenance layer; the notebook is the code/workflow layer — both layers are mandatory.
   > *Rationale*: Agents without a Jupyter kernel used to treat "CLI fallback" as license to leave code in ephemeral scripts — analysis ran, figures existed, but nothing reproducible remained. Making the notebook a code ledger (append-after-execute, 1 command per step) closes the loophole.

   > **判断优先（Rule 0 的具体化）**：台账的形式可随任务规模缩放——探索性试跑/一次性小图的代码也建议随手 `nb_log.py` 一行登记（成本一行命令）；正式任务 notebook 必须逐步落账。Kernel mode 下若已在 notebook 内直接执行且 save_panel 自动显示输出，`nb_log.py` 不必重复登记同一段（同一段落账两次无收益）。
10. **Deliverable gate** *(mandatory, post-convergence)*. When the analysis story converges (Phase R loop done + researcher agrees, Rule 8), the agent MUST produce at least one deliverable package — not just leave figures on disk. Default outputs: PPT (`scientific-slides`, for meeting/defense) or HTML report (`web-report`, for online sharing — no PowerPoint needed to view). Choose based on audience: lab meeting → PPT; remote collaborator → HTML; both if the user wants. The deliverable embeds real figures + key findings (with source labels per meta_methodology §8c: `[实测+文献]/[实测]/[推断]/[文献]`) + hypothesis ledger + method/reproducibility info. **Skipping this = analysis done but nothing delivered.**

## Key Files（四层按需取用；入口导航=grep `references/route_index.md`）

**派发时（主 agent 给子 agent 配规则/契约）**
| File | When |
|---|---|
| `references/dispatch_cheatsheet.md` | 每次派发——按 Dispatch Injection 作用域选节 |
| `references/bigfig_deck_playbook.md` | 组合体任务（E 系执行体+踩坑清单） |
| `references/orchestration_playbook.md` | 多 worker 并行（O1-O5） |

**分析/绘图执行时**
| File | When |
|---|---|
| `references/analysis/templates/` | 分析代码唯一拷贝源（setup/sc_basic/sc_annotation/sc_downstream/spatial/bulk） |
| `references/analysis/decision_guide.md` | 生物学问题→方法决策表 + 反模式黑名单 |
| `references/analysis/analysis_flow.md` | 每步结果怎么解读→下一步走哪 |
| `references/plotting_reference.md` / `references/figure_guide.md` | 绘图代码模板 / 视觉规格+图型决策表（§0.1） |
| `scripts/cns_style/` | plot_* 统一入口（52+，from cns_style import *） |
| `references/analysis/stats_convention.md` | 显著性三层口径与词汇表（唯一出处） |
| `references/meta_methodology.md` | 每步自查 8 原则 + 假设台账 |
| `references/omicverse_guide.md` / `compat.yaml` | ov.* API 速查 / 版本唯一源 |
| `scripts/postcheck.py` / `scripts/data_sanity.py` | 分析后机检 / 分析前数据门 |
| `scripts/nb_log.py` | CLI 台账 + `--obs` 结构化观测 jsonl |
| `scripts/api_check.py` / `scripts/scop_api_check.R` | 装包/升级后 |

**交稿时（定稿/外发/投稿前）**
| File | When |
|---|---|
| `references/deep_review_protocol.md` | 定稿与外发前必跑（数字门五步审查） |
| `references/analysis/robustness_recipes.md` | 审稿加固（R1-R6 配方） |
| `references/figure_templates.md` + `references/analysis/paper_paradigms.md` | 主图组织顺序 / 高分范式（时效文件，见 freshness） |

**维护 skill 本身时（季度/改文件后）**
| File | When |
|---|---|
| `evals/check_all.py` | 改任何文件后一键跑全部门检（lint+consistency+freshness+desc） |
| `evals/`（route/trigger 用例 + `sync_prompts.py`） | 改路由/触发后：先 sync 再评测 |
| `references/pitfall_inbox.md` | 踩坑一行回流 + 季度 triage（D7） |
| `references/guards_vs_guides.md` | 护栏 vs 指南裁决细则（操作性内容已内嵌 Rule 0；**冲突/破例时再读全文**） |
| `SKILL_CARD.md` / `BENCHMARK.md` | 能力/风险声明与成熟度 / 评测记录 |

