# BENCHMARK — 评测结果固化（measured contribution，NVIDIA trust-pipeline 对齐）

> 每次 skill 大版本更新后回填一行；数据源 = `evals/results/` 时间戳 JSON 的聚合。

| 日期 | 版本 | 套件 | 结果 | 备注 |
|---|---|---|---|---|
| 2026-09-21 | 22.x | route 33 例 | 33/33 | 首轮基线（结果目录首份） |
| 2026-09-24 | 22.x | route 33 / trigger | 33/33 / pass | lint/desc_overlap 上线 |
| 2026-10-09 | 23.0 | route 38 例 | 38/38 | +R34-R38（新路由/域校准/深审查 near-miss）；sync_prompts 修复 prompt 快照漂移 |
| 2026-10-10 | 23.2 | route 38 例 | 38/38 | router 瘦身（25.7→19.5KB）+ route_index.md 外置，评测 prompt 并入索引表——瘦身零回归 |
| 2026-10-10 | 23.4 | chart 18 例 | 18/18 | 图型选择回归套件上线（C01 历史踩坑=棒棒糖→stats_dotplot 锁定）；三层路由链验证 |
| 2026-10-10 | 23.2 | 机检套件 | consistency 0E/0W · lint 0E/0W · freshness 0E/0W · plot_* 52=52 | C1-C8 全绿；postcheck 新增 A11/DOM/E7 三启发式（正反用例冒烟过） |

## 待建（staged，见 pitfall_inbox）

- **causal lift 成对评估**（E3）：with-skill vs without-skill 同题双臂 + 置换检验——挑 3-5 个"无 skill 会犯 A4/A10 错"的场景。
- **端到端任务基准**（B8）：固定 3-5 条（PBMC3k 注释 / 模拟空转 domain / 已知阳性 pseudobulk DE）+ ground truth 打分。
- **prompt-bloat 用例组**（B3）：+800-1900 词噪声指令下的路由稳定性（BioAgent Bench：膨胀使完成率 -28%）。
