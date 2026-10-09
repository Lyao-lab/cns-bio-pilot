# Pitfall Inbox — 坑捕捉收件箱（skill 自我进化的最小可行回流环）

> **用途**：任务中踩到新坑 / 发现新方法 / 发现 skill 某处漂移时，**一行 append 进本表**（成本限定一行，
> 当时只记录症状+根因，不写完整修复）。**不在这里写修复方案**——方案留到季度 triage 时批量蒸馏进正式
> reference，避免任务中直接改护栏（一次判断失误污染合规线）。
> **使用**：任务执行中（含子 agent），任何"这个坑下次别再踩" → 立刻一行（见下方格式）。skill 里对应规则
> `[D7]`（dispatch_cheatsheet）。
> **归档**：季度 triage（人工策展）时，把本条目的经验蒸到正式 reference（见归属映射），然后清空已蒸馏行。

## 归属映射（经验类型 → 目标 reference）

| 经验类型 | 目标文件 |
|---|---|
| API 漂移/参数改名 | `compat.yaml` + `references/analysis/templates/spatial.md`（或对应模板） |
| 方法选型教训（哪种数据用哪个方法） | `references/analysis/decision_guide.md` 或 `references/spatial_frontiers_2026.md` |
| 绘图坑（图型域、布局、截断） | `references/figure_guide.md` 或 `references/bigfig_deck_playbook.md` |
| 路由错误（派错子 skill） | `evals/route_cases.yaml`（新增 near_miss 用例，沿用现有 README 规则） |
| 统计口径/显著性表述 | `references/analysis/stats_convention.md` 或 `references/analysis/robustness_recipes.md` |
| 深审查/数字门新发现 | `references/deep_review_protocol.md` |
| 派发/编排坑（子 agent 行为） | `references/dispatch_cheatsheet.md` 或 `references/bigfig_deck_playbook.md` |
| 新鲜度/文件漂移 | `evals/consistency_check.py`（补检查项）或对应 reference 本身 |

## 坑记录表（一行一条，最新在上）

| 日期 | 症状（一句话） | 根因 | 建议归属 | 状态 |
|---|---|---|---|---|
| （示例）2026-10-09 | route_prompt.md 快照与 SKILL.md 漂移，评测会用旧规则判新用例 | sync_prompts.py 是手动触发，改 SKILL.md 后没人记得跑 | `evals/` 工作流（改路由后先 sync_prompts 再评测） | ✅已修（本轮） |
| 2026-10-09 | postcheck.py 没有 A11（口径声明）/E7（数字门）/图型域 的机检函数 | 新规则加了没配机检 | `scripts/postcheck.py` 补启发式函数 | ✅已修（正反用例冒烟过） |
| 2026-10-09 | Core Rules 4 与 Rule 0 都引用规则全集，措辞有重叠 | 新规则加了没做去重 | `SKILL.md` Core Rules 4 只留汇总句 | ✅已修（Rule 0 改 G 系指针） |

| 2026-10-09 | 注入模板 E1-E6 漏 E7 数字门；通用模板引用子 agent 看不到的 G 编号；G10/A12 ML 隔离无载体 | 后加规则没跟上模板（Reviewer B F3/F5/F11） | cheatsheet/SKILL.md 模板统一 + 新增 A12 | ✅已修 |
| 2026-10-09 | 规则计数散文两次漂移（38→39），手维护计数必然再漂 | 加规则不改计数（Reviewer A F2） | 计数改机检自动对账（consistency_check C5） | ✅已修 |
| 2026-10-09 | 结论分级三处三套（3 级 vs 4 级 vs 3 标签） | 各文件独立演化（Reviewer A F4） | 统一 meta §8c 四级 + A8 指针化 | ✅已修 |
| 2026-10-09 | D 系回路规则发给 fire-and-forget 子 agent（R3 人门子 agent 无法执行）；§0 Init/gap scan 悬空引用 | 注入模板无受众分层（Reviewer B F1/F2/F7） | D 系受众分层 + 悬空引用补路径 | ✅已修 |
| 2026-10-09 | 无多智能体编排指导；并行写者冲突（notebook 编号/analysis_log/checkpoint 单写者假设） | skill 只有 executor 视角（Reviewer B G-a~G-e） | 新建 orchestration_playbook.md（O1-O5） | ✅已修 |
| 2026-10-09 | 时效敏感文件无新鲜度元数据，陈旧不可机检 | 只有人工复盘才更新（Reviewer C 1-A） | as_of/review_by 标记 + freshness_check.py | ✅已修 |
| 2026-10-09 | 越界组学（ATAC/flow）无路由兜底；figure-production/manuscript-writing 无 When NOT | 子 skill 边界只靠 router 裁决（Reviewer C 2-A/2-B） | SKILL.md NONE 兜底 + 两 skill 补 When NOT | ✅已修 |
| 2026-10-09 | pseudobulk 规则四处复述无权威指向；深审查五步两处复述 | 设计性冗余无单一出处（Reviewer A F5/F7） | 季度 triage：定「以 meta_methodology/stats_convention 为权威，他处改指针」 | ⏳待 triage |
| 2026-10-09 | C4 已知坑位表与 pitfall_inbox 职能重叠 | 两个静态/动态清单并存（Reviewer A 改5） | 季度 triage：C4 静态坑并入 inbox 或标注分工 | ⏳待 triage |

| 2026-10-10 | 中期项：skill 自生长（skill_miner 从 analysis_log+notebook 蒸馏新 SOP） | references 全靠人工沉淀，新跑通路线无回流 | SpatialAgent skill-generation-from-memory | ⏳待 triage |
| 2026-10-10 | 中期项：视觉模型 panel 语义解读回路（读 PNG+代码上下文→结构化判读回填决策） | E5 像素门只验机械质量不解读内容 | SpatialAgent auto figure interpretation | ⏳待 triage |
| 2026-10-10 | 中期项：claim 级半自动验证（claim 抽取→逐条链源→Supported/Cannot-verify 报告） | deep_review 是提示词驱动无脚本 | SpatialAgent verification subagent | ⏳待 triage |
| 2026-10-10 | 中期项：外部 DB 检索接入（K-Dense cellxgene-census/gget 或 knowledgebase-mcp） | 全库无 GEO/CellxGene/Ensembl 查询入口 | route_index 已留指针；装包需用户许可 | ⏳待 triage（需许可） |
| 2026-10-10 | 中期项：端到端任务基准（3-5 条固定任务+ground truth） | evals 只有路由/结构，无分析质量基准 | BixBench 模式 | ⏳待 triage |
| 2026-10-10 | 中期项：causal lift 成对评估（with/without skill 双臂+置换检验） | 现有 eval 不测 skill 的边际贡献 | adewale harness / NVIDIA Tier3 | ⏳待 triage |
| 2026-10-10 | 中期项：>100 行 reference 补 TOC + 引用一层深检查 | agentskills.io 规范 | consistency_check 可加二层引用检测 | ⏳待 triage |
| 2026-10-10 | 子 skill description 含流程链（4 个 SDO 疑似违规）但承担触发词功能——改需与 trigger eval 联动复测（无 LLM backend 时不可盲改） | superpowers SDO 铁律 vs 触发精度权衡 | 季度 triage 时配 trigger eval 改 | ⏳待 triage |

> **清空规则**：状态=✅已修 或已蒸馏到归属文件的行，季度 triage 后可删；⏳待修 行保留到修复。
