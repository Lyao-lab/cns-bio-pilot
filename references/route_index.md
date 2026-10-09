# Route Index — 知识查询型路由完整索引（router Quick Route 的外置全表）

> **用途**：router SKILL.md 的 Quick Route 只保留执行型（子 skill）行；本文件承载全部**知识查询型**
> （`ref:` → references/ 下方法论文档）行的完整关键词索引。**怎么查**：`grep -i "<关键词>" 本文件`，
> 命中行右端即目标文档。
> **维护**：新增知识查询型路由时，router 只加一行汇总指针不动，本表加行；sync_prompts 会把本表并入评测 prompt。

| 关键词（grep 命中词） | 目标文档 |
|---|---|
| 主图顺序 / fig 组织 / 第几张图 / 故事组织成图 / 图谱论文怎么排图 / figure templates | `references/figure_templates.md`（§0 路由：领域 C1-C15 × 故事 T1-T6；506 篇泛化）|
| 判断 vs 规则 / 要不要破例 / 规则太死 / 过度合规 / 自由度 / 护栏 | `references/guards_vs_guides.md`（护栏 G1-G10 vs 指南两层分界 + 冲突优先级 + 反模式）|
| 并行 / 多 worker / fan-out / 子任务派发 / spec 契约 / 主 agent 验收 / 编排 | `references/orchestration_playbook.md`（O1-O5：并行口诀 + 五要素契约 + 写者纪律 + 验收表）|
| 空转选型 / 2026 基准 / SACCELERATOR / 空间基础模型 / spatial FM / 去卷积基准 | `references/spatial_frontiers_2026.md`（§0 第一律 + §1 全管线裁决 + §5 FM 边界）|
| 3D 重建 / 多切片对齐 / 虚拟切片 / 连续切片 | 同上 §4（适用边界：连续切片 ≥8 张才考虑 3D）|
| 空间 case-control / 多样本空间 DE / 空间重复 / 空间功效 | 同上 §3（VIMA/TESSERA 统计教义，含零包手搓方案）|
| microniche / 微生态位 / niche 分类器 / niche 定量 | 同上 §1 niche 行（域工具 ≠ niche 工具）|
| 稳健性 / 敏感性 / 置换检验 / block bootstrap / split-reliability / LOO / 审稿加固 | `references/analysis/robustness_recipes.md`（R1-R6 实战配方带代码骨架）|
| 审查 / 红队 / 数字核验 / deck 复核 / 深审查 / 投稿前检查 / 版本切换 / 口径声明 | `references/deep_review_protocol.md`（五步审查 + caption-from-table + 版本切换纪律）|
| 什么数据画什么图 / 数据形态选图 / 图型选择 / 最美观图型 | `references/figure_guide.md` §0.2（数据形态→图型矩阵 + 美观五元规则）＋ §0.1 分析输出路由 |
| caption 怎么写 / 统计量格式 / 误差棒语义 / n 怎么标 / 空间图配什么 / panel 怎么组织 / 展示规范 | `references/presentation_conventions.md`（CNS 2025-26 实测 24 条：ρ/P/CI/n 格式、箱线逐 panel 定义、空间定量成对、5-9 panel、caption 150-400 词）|
| 坑 / 踩坑 / 新方法发现 / skill 漂移 | `references/pitfall_inbox.md`（一行回流 inbox + 归属映射）|
| 统计口径 / 显著性措辞 / 名义显著 / 多重校正怎么写 | `references/analysis/stats_convention.md`（三层口径 + 词汇表，唯一出处）|
| 大 fig / 拼版 / deck 流水线 / 像素门 / 渲染 | `references/bigfig_deck_playbook.md`（E 系执行体 + §7 数字门 + §8 画布规则）|
| 数据库 / GEO / SRA / CellxGene / Ensembl / 参照图谱查询（外部检索） | 待装外部 skill：K-Dense `cellxgene-census`/`gget` 或 knowledgebase-mcp（装前需用户许可；见 `spatial_frontiers_2026.md` §7 未装清单惯例）|
