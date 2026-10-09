# Spatial Frontiers 2026 — 空转分析方法前沿与选型裁决（2026-04~10 调研消化版）
> as_of: 2026-10-09 | review_by: 2027-01-09 | cadence: 季度（基准/工具结论衰减快）（过期由 evals/freshness_check.py 报 ERROR；调研 runbook 见 pitfall_inbox/evals）

> **来源**：2026-10-09 两轮文献调研（33 条方法条目 + 13 篇顶刊应用论文，全部逐篇核实，原始档案
> `/home/longyao/data/lit_surveys/202610_st_{methods,applications}.md`）。
> **谁读**：做空间转录组分析选型/设计时（`spatial/*` 子 skill 执行前）；写 Methods/审稿回复时。
> **怎么用**：§1 查步骤裁决 → §2 检查自己是否踩范式旧实践 → §3 设计多样本统计 → §6 检查故事构建。
> **环境状态标记**：✅=本机已装可直接跑 ｜ 🔧=未装（pip 需用户许可 + 装后跑 `api_check.py --diff`）。

## §0 第一律：先查 2026 基准，再选工具

2026 年起每个管线步骤都有 ≥1 个大型基准（批次整合 Owkin、去卷积 spDDB/Pritykin/GB、域识别 SACCELERATOR、niche CosMx 基准、CCC GB/SpatialCCCbench、FM SAFFRON）。**引用工具前先看基准结论；方法论文里的 self-claim 不算数。**（这是指南不是护栏——基准结论是选型先验，数据不适合时按需偏离并写理由；护栏仍只有 §3 的统计口径。）

## §1 管线步骤 × 2026 裁决速查

| 步骤 | 2026 裁决 | 首选（本机状态） | 关键 caveat |
|---|---|---|---|
| 多切片批次整合 | 概率生成式去批次最强、图法保空间结构（Owkin 110 万细胞基准） | scVI/scANVI ✅（scvi-tools）；大数据 sysVI/scVIVA 🔧 | OOD 泛化与批次校正有权衡——留一样本外推验证 |
| 切片对齐/3D 重建 | PASTE 两两对齐已被"多切片联合 + 神经场"取代 | 已知近似对位：`ov.space.pySTAligner` ✅；连续 3D：SINTER3D/NTF 🔧(GPU)、sc3D 🔧(pip)、AlignDG 🔧(R) | 只有 1-3 张非连续切片时 3D 重建不适用（如实报 n 切片） |
| 分割/细胞化 | "分割优先、多尺度 bin 辅助"；无新旗舰，DL-QC 分割质量成新环节 | bin2cell/cellpose/Baysor 按平台决策表（multiomics SKILL）；分割 QC：DL-QC 思路 🔧 | Stereo-seq 大盘可用 CellBin 框架 🔧；分割结果必须过质评（multiomics §质量评估） |
| 去卷积 | cell2location/RCTD/SONAR 领先但**简单基线（NNLS）打平**；跨平台迁移 SpatialDecon/c2l 最可靠（三基准合并结论） | cell2location ✅（本项目主用）+ RCTD(scop) ✅ 双报 | 稀有细胞类型是所有方法死穴——报告丰度下限；不要因为"更复杂"选方法 |
| 空间域 | **单方法定稿不合规**：参数变异可超方法变异（SACCELERATOR 22 法基准）→ 共识聚类 + 专家在环 | ov.space 内置多法 ✅（STAGATE/CAST/GASTON/cellcharter）跑 ≥2 + ARI 一致性 + 分歧处人工裁决；BANKSY ✅（本项目已用） | 扩展性：仅 CellCharter 能吃 Visium HD 2μm；人工 GT 不当金标准 |
| niche 识别 | **域分割工具 ≠ niche 工具**（CosMx 基准：多数默认配置恢复不了 niche 边界）；microniche 允许重叠是新解 | niche = 细胞类型组合 + 邻域统计（squidpy nhood/co_occurrence ✅）+ 类型加权；VIMA microniche 指纹 🔧(GPU) | 用域工具做 niche 时必须对核心谱系加权并验证边界恢复 |
| SVG / 空间 DE | 单样本 SVG ≠ 空间 DE；多样本（含生物学重复）空间 DE 已有正式方法 | 单样本：PROST/Moran/sepal ✅（多法共识 CASTL 思路：≥2 法取交集）；多样本队列：TESSERA 🔧(R) | "无重复的空间差异结论"2026 起过不了审——至少手搓 permutation null（§3） |
| 空间 CCC | 方法间一致性 <0.42；**非空间先验（CellPhoneDB/CellChat）在成像平台有系统风险**；SpaCCI 综合最稳健 | 测序平台：COMMOT ✅ + LIANA+ ✅ 双报（现行做法正确）；成像平台：加 SpaCCI 🔧 或 SpatialDM 🔧 | CCC 结论永远配共定位证据；按平台分辨率选工具（GB 基准） |
| 轨迹×空间 | "快照放电影"：分化+增殖+空间迁移联合重建（stVCR 旗舰） | 保守：DPT/Slingshot + 空间投射（现行）；进阶：stVCR 🔧(GPU) | 空间迁移主张必须有方法学支撑，不能从 UMAP/DPT 直接跳跃 |
| 空间 FM | SVG 等经典任务上 FM 尚未碾压统计基线（SAFFRON） | 统计方法做检验 + FM 做注释/嵌入辅助的混合管线；HEIST/scGPT-spatial/VirTues 🔧 | 沿用本 skill 既有铁律：FM 预测必须对比 linear baseline（decision_guide 反模式表） |
| 空间多组学 | GNN 整合框架成熟（SMART/SCIGMA） | 有 ATAC/蛋白层时 SMART 🔧；无则不适用 | — |

## §2 范式旧实践黑名单（2026 基准判"过时"）

1. 非空间 CCC 先验直接用于成像平台数据（Xenium/CosMx/MERFISH 级）
2. 单一域识别方法结果直接定稿（必须共识 + 参数敏感性说明）
3. "越复杂的去卷积越好"（NNLS 类打平；稀有类型全弱）
4. 两两 PASTE 对齐后简单堆叠当 3D
5. 单样本 SVG p 值当"空间差异表达"报告给队列结论

## §3 多样本空间统计教义（VIMA/TESSERA 口径，可手搓）

2026 分水岭：**空间 case-control / 条件比较必须显式统计**，最低配置（无需装包即可执行）：

1. **n 口径分开报**：n 切片与 n 供体永远分开（"S=27 切片，N=22 人"式）
2. **置换 null**：条件标签在供体级随机打乱（保切片内空间结构、破条件关联）≥1000 次 → 经验 p
3. **经验 FDR**：多邻域/多特征时 BH 于置换 p 之上
4. **效应量 + CI**：block bootstrap（空间块 ≥500µm）给 CI，不只报 p
5. **功效意识**：n<5 供体时明确写"探索性"；VIMA 式功效分析做参考（n 切片↑可部分补偿 n 供体↓，但供体是统计单位）
6. 混合效应（donor/平台随机效应）回归协变量后再检验（肝图谱 LMM 范式）

> 本项目（胎心 3 时点空转 n=1/时点）适用：凡空间比较一律 "descriptive, n=1/TP" + 供体级 snRNA 佐证 + 置换/块自助 CI——与既有 AGENTS/cheatsheet 口径一致，此处给出文献锚（VIMA/TESSERA）。

## §4 3D 重建与虚拟切片（何时需要）

- **需要**：连续切片（间距 ≤1 切片厚度）≥8-10 张、或器官级全景叙事（胚胎图谱类标配）
- **不需要**：3 个离散时点各 1 张（当前胎心）——正确做法是跨时点定性对齐 + 逐时点分析，勿硬上 3D
- 工具梯队：sc3D（配准+重建+napari，轻）→ SINTER3D/NTF（INR 连续场，GPU）→ STITCH/STADiffuser（生成虚拟切片/补全/in silico 重复）

## §5 FM 使用边界（SAFFRON 校准）

- 允许：注释辅助、嵌入增强、组织结构预测（HEIST 式）、虚拟染色（VirTues）
- 不允许：用 FM 分数替代统计检验；FM 预测无 linear baseline 对照（既有铁律）
- 引用时注明预印本状态（scGPT-spatial 至 2026-10 仍 bioRxiv）

## §6 2026 顶刊文章构建套路增量（对 figure_templates §1-§3 的 H2 增量）

1. **主图顺序**：F1 队列/平台总览（样本×阶段矩阵 + 全组织缩略）→ F2 图谱/分区（UMAP+空间双视图并排）→ F3± 机制/niche（CCC≥2 工具 + 拟时序投影回空间 + 邻域统计）→ 倒数第二 疾病/动态页 → 末页 模型图。发育类开篇"时空矩阵"，肿瘤类开篇"演进设计图"。
2. **图谱页标配**：UMAP↔空间一一对应、H&E/DAPI 并排、3-4 个 niche zoom-in、跨平台交叉验证小 panel、数据门户链接。
3. **机制页标配**：CCC ≥2 工具并用 + 拟时序投影回空间 + niche 定义（最近邻/层次聚类）+ LR 空间共分区相关。
4. **统计叙事**：VIMA 式显式 case-control（n 切片/n 供体分开 + 置换 null + 经验 FDR + 效应量 CI + LMM 随机效应）；"Wilcoxon 无空间零模型"已过不了顶刊审稿。
5. **验证链四级**：标配 RNAscope/IHC（≥3 样本）→ 第二空间平台正交 → 谱系/治疗干预/类器官 → 跨物种 + 临床队列。
6. **平台组合**：单平台论文近乎绝迹；Xenium↑（niche/机制）、Stereo-seq↑（大视野胚胎/器官图谱）、MERFISH↑（FFPE 队列）。snRNA+ST 的项目最小升级 = 加一个正交原位验证层。

## §7 未装包清单（🔧，装前需用户许可）

| 包 | 用途 | 依赖 |
|---|---|---|
| `sc3D` + `napari-sc3d-viewer` | 连续切片 3D 重建 | napari 栈 |
| `SINTER3D` / `NTF` | INR 连续 3D/虚拟切片 | PyTorch GPU |
| `vima`（yakirr/vima） | microniche case-control + 功效 | GPU 推荐 |
| `TESSERA`（R） | 多样本空间 DE | scop_env 侧装 |
| `SpaCCI` / `SpatialDM` | 成像平台空间 CCC | Python |
| `CASTL` | 共识 SVG | Python |
| `stVCR` | 空间迁移+分化+增殖联合轨迹 | PyTorch GPU |
| `STADiffuser` / `STITCH` | 虚拟切片 / in silico 重复 | GPU |

> 装后必须：`python scripts/api_check.py --diff`（Core Rule 6）+ compat.yaml 登记。

## §8 与既有 skill 内容的分工

- 域/去卷积/CCC/SVG 的**可执行代码**仍以 `references/analysis/templates/spatial.md` 与 `spatial/*` 各 SKILL 为权威；本文件只加"2026 裁决层"。
- 图型/主图顺序基线仍是 `figure_templates.md`（506 篇）；§6 是 H2 增量不是替代。
- 多样本统计口径与 `stats_convention.md`/dispatch_cheatsheet [A6] 一致，本文件补文献锚。
