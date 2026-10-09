# Orchestration Playbook — 多 worker 并行编排（orchestrator 视角，2026-10）

> **来源**：fetal_heart 大 fig 重建/深审查/加固战役实战模式提炼（4 分析 worker 并行 + 主会话验收）。
> **谁读**：主 agent 计划 fan-out 多个子任务时（per-panel 出图 / 深审查多通道 / 多方法平行试 / 多平台分析）。
> 子 agent 不读本文件——它们只收 O2 的 spec 契约。与 `dispatch_cheatsheet.md`（executor 规则）分层：**本文件管编排，cheatsheet 管施工**。

## O1 什么该并行、什么必须串行

| 可 fan-out（worker 间无依赖） | 必须串行（单写者/有依赖） |
|---|---|
| per-panel 绘图（输入冻结后各面板独立） | compose → build → render 后处理链（E1 顺序） |
| 深审查五通道（溯源/统计审计/文献红队/跨产物 grep 各自只读） | 深审查的裁决汇总（主 agent） |
| 稳健性配方 R1-R6（bootstrap/置换/LOO/扫描） | Phase R 人门（永远主 agent + 用户） |
| 多方法平行试（2-3 个域方法对比） | 方向判断/下一 batch 决策 |
| 不同供体/时点/腔室的独立分析 | 同一 checkpoint 的写回（O3） |

**判断口诀**：读同一份冻结输入、写不同产物 = 可并行；写同一文件/决定下一步 = 串行。

## O2 子任务 spec 五要素契约（每个 worker 必须收到）

> **fork 型子 agent 返回值契约（2026 共识）**：结果摘要 + 产物路径清单 + 机检输出——**丢弃中间过程**
> （主 agent 只消费结论与产物，不读过程流水；中间态留在 worker 自己的 notebook/目录里可追溯）。与 E4 内容寻址缓存配套：主 agent 凭产物 hash 引用，不凭过程叙述。

```
[目标] 一句话结果定义（不是任务过程）
[冻结输入] 数据文件路径+版本（h5ad/表/掩膜；写明"以此为准，不重算上游"）
[产物清单] 每个输出文件的路径与格式（面板 png+pdf / 表 csv / 汇报格式）
[验收门] 本任务对应机检（postcheck/B 系断言/数字抽检点）+ FAIL 处置
[禁止动作] 不改共享文件（analysis_log/INDEX/上游 h5ad）；数字仅作指引、表与指引冲突以表为准（E7）
＋ [规则] 注入（cheatsheet 或 playbook，见 SKILL.md Dispatch Injection）
＋ [上下文]（可选）autopilot 授权态 / 已知坑 / 命名空间（O3）
```

## O3 并行写者纪律（默认单写者假设的破除）

- **notebook 台账**：并行 worker 各用独立编号（`NN_task_workerX.ipynb` 或各自任务名 notebook），主 agent 收编时不动 worker notebook，只在汇总台账登记索引——**禁止两个 worker 写同一 .ipynb**。
- **analysis_log.md**：worker 不直接 append 共享 log（并发写冲突）；各自把日志段落放进交付报告，主 agent 串行合并。
- **checkpoints/面板目录**：每个 worker 独占一个输出子目录（`analysis/figures/<task>_<date>/`）；同名文件覆盖只发生在同一 worker 内部。
- **上游数据**：一律只读（h5py 部分读/backed），需要派生副本时复制到自己的目录。

## O4 fan-in 收敛（主 agent 合并规则）

1. 每份 worker 交付先过其自报机检（没附输出的重跑，Core Rule 4）。
2. **数字抽检**：每 worker ≥2 个关键数字对依据表（deep_review §5——不能只看汇报）。
3. 冲突结果（两个 worker 对同一量给不同值）→ 以依据表裁决，禁止平均值/和稀泥；分歧根因写 pitfall_inbox（D7）。
4. 合并后的叙事/图序由主 agent 统一（E6 组合叙事一致），worker 不改全局结构。

## O5 主 agent 验收表（验收即跑，缺一不放行）

| 产物 | 门 | 工具 |
|---|---|---|
| 分析结果 | postcheck + 数字抽检 | `scripts/postcheck.py` + 对表 |
| 面板 | B 系断言（finalize/重叠/边缘） | cns_style finalize + Read PNG 自检 |
| deck | 像素门 + 机检门 + 数字门 | `scripts/edge_sweep.py` + qa_deck/validate + deep_review §1 |
| 大 fig | E4 嵌入 md5 链 | 派生链逐页比对 |
| 台账 | notebook 存在且含各步 code cell（A10） | 逐 worker 查 |

## 反模式（实战教训）

- **spec 只给规则不给契约**：worker 自由发挥输出路径 → fan-in 时找不到产物（O2 五要素缺一不可）。
- **让 worker 决策方向**：分析 worker 在报告里"顺手"决定下一步 → 违反 D1 受众分层；spec 里写明"决策点列入报告，不自行执行"。
- **并行写共享 log**：两 worker 同写 analysis_log → 互相覆盖（O3）。
- **验收只看汇报**：worker 汇报数字与表不符是实战最高频 P0（O4-2 数字抽检为此而设）。
