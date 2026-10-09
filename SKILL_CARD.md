# SKILL CARD — cns-bio-pilot（机读+人读双份能力/风险声明，NVIDIA trust-pipeline 对齐）

| 字段 | 值 |
|---|---|
| name | cns-bio-pilot |
| version | 见 SKILL.md frontmatter（metadata.version，唯一源） |
| owner | Lyao-lab（fetal_heart / fetal_gland 项目组） |
| license | GPL-3.0 |
| use case | 单细胞/空转全流程分析（QC→注释→DE/CCC/轨迹→空间统计）→ 发表级图表 → deck/HTML/PPT 交付；深度审查与稳健性加固 |
| 输出形态 | h5ad checkpoints / csv 表 / png+pdf 面板 / ipynb 台账 / pptx·html 交付物 |
| 环境依赖 | compat.yaml（单一版本源）；conda envs sc/st/regvelo/scop_env；GPU 可选 |
| 安装位置 | `~/.agents/skills/cns-bio-pilot`（agentskills.io 标准路径，40+ 客户端可发现） |

## 风险面与权限红线（与服务器 AGENTS.md 三层边界对应）

| 风险面 | 声明 |
|---|---|
| 大内存操作 | h5ad/loom 加载、稠密化、pairwise——AGENTS.md §3 资源排查铁律（估算峰值→free -g→放行条件 available ≥ max(50G, 峰值×1.5)；>100G systemd-run MemoryMax） |
| 只读红线 | rawdata/cellranger outs/GEF/INDEX.md/integrity_*.json——只读可复制，禁原地改 |
| 安装类 | pip/conda install、外部 skill/MCP 接入（K-Dense cellxgene-census/gget、knowledgebase-mcp 等）——需用户许可，装后跑 api_check --diff |
| 网络类 | 外网下载 >1G、数据上传外发——需用户许可 |
| 破坏类 | 删除/覆盖已有产物（>100M 尤甚）、git push——需用户许可 |
| AI 生成风险 | 数字虚构（G1）、FM 预测无 baseline、CCC 因果措辞（A8）——由 postcheck/deep_review 机检兜底 |

## 成熟度分级（B9，ClawBio 五级简化为三级；全库默认 L1，逐项标注升级）

| 级 | 定义 | 当前达标项 |
|---|---|---|
| **L2 tested** | 有 evals 用例 + 机检脚本覆盖 | 路由（38 例 + sync/lint/consistency）、绘图（cns_style 52 plot_* + 冒烟）、postcheck 12 检查项、data_sanity 6 检查项、freshness/consistency 机检 |
| **L3 battle-tested** | 真实项目全流程跑通并交付 | fig1-3 大 fig 体系（v4f 重算/深审查/47 页视觉门，2026-10 fetal_heart）、VIC niche 全链（2026-08）、CM 转化专题（2026-09）、空转 niche 工具链（BANKSY/c2l/模块投射） |
| L1 spec-only | 仅有规范未实测 | 其余（外部 DB 检索、FM 微调类、3D 重建——见 spatial_frontiers §7 未装清单） |

> 使用者判断：L3 流程可直接信任按 SOP 跑；L2 有回归保护可放心改；L1 项执行时按护栏走并预期踩坑（坑记 pitfall_inbox）。
