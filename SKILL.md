---
name: cns-bio-pilot
description: 单细胞与空间转录组（兼 bulk/其他组学）生信分析全流程技能库。每当用户提到：空间转录组、空转、spatial transcriptomics、Visium、Xenium、MERFISH、Stereo-seq、Slide-seq、空间去卷积、空间域、spatial domain、单细胞、single-cell、scRNA-seq、聚类、细胞注释、cell type annotation、doublet、批次校正、batch correction、scVI、Harmony、RNA velocity、拟时序、trajectory、细胞通讯、CellChat、Perturb-seq、扰动预测、perturbation prediction、scanpy、squidpy、cell2location、omicverse、scop、Seurat、scGPT、GEARS、CPA、差异表达、DEG、富集分析、GO、KEGG、GSEA、WGCNA、PPI、画图、绘图、火山图、热图、UMAP、多面板图、graphical abstract、机制图、写论文、写 Methods、写 Results、图注、figure legend、做 PPT、做幻灯片、lab meeting、汇报，或要求"帮我分析空转/单细胞数据""设计课题""画发表级图表""写文章""做演示"时，都应触发。
---

# CNS Bio-Pilot

单细胞 + 空间转录组（兼 bulk/其他组学）生信分析技能库。三引擎：**OmicVerse**（Python，默认）+ **scop**（R/Seurat）+ **scGPT/扰动模型**（深度学习）。本文件是**路由器**——读它确定走哪个子 skill，不要在此执行分析。

## Loading Protocol（强制）

1. **永远只读**：本 SKILL.md + 命中的 **1 个**子 skill + 该子 skill 声明的 references
2. **禁止**一次读多个子 skill（上下文爆炸）
3. 子 skill 路径见 `skill-index.json`（紧凑索引）或下方路由表
4. 子 skill 内的 references/scripts **按需读取**，不前置加载

## Quick Route — 先读这个（6 步）

```
① 判断数据类型  → 见「路由：数据类型轴」
② 判断分析任务  → 见「路由：任务轴」
③ ①×② 交叉命中 → 锁定子 skill 路径
④ Pre-Routing Checks → 确认环境/数据前提（见下）
⑤ 读命中的子 skill SKILL.md → 执行
⑥ Postcheck → 跑 scripts/postcheck.py 验证科学严谨性
```

## Pre-Routing Checks（路由前必跑）

匹配路由**之前**先排雷——这些是绝大多数生信错误的根因：

| 检查项 | 怎么查 | 不满足怎么办 |
|---|---|---|
| **raw counts 保留？** | `'counts' in adata.layers` | 🚨 DE/velocity 的生死线——先备份 `adata.layers['counts']=adata.X.copy()` |
| **多批次？** | `adata.obs['batch'].nunique()>1` | 决定是否走 batch_correction；且**校正后 embedding 禁用于 DE** |
| **数据规模** | `adata.n_obs` | >100k → 考虑 AnnDataOOM（`ov.read(backend='rust')`） |
| **环境就绪** | `python -c "import omicverse"` | 缺包 → 见子 skill 的安装段 |
| **GPU**（深度学习任务） | `torch.cuda.is_available()` | scGPT/GEARS finetune 必须 GPU；无则降级 CPU 推理或换方法 |
| **spliced/unspliced**（velocity） | `'spliced' in adata.layers` | scvelo 必须；缺 → 先跑 velocyto/kb_python |

## 路由：数据类型轴（先判断这个）

```
数据有空间坐标 / 组织切片？
├─ YES → 空间转录组（spatial/）
│   └─ 需去卷积？→ spatial/deconvolution（🚨 cell2location 无 ov 封装，强制此 skill）
│   其余 → spatial/omicverse-spatial
├─ NO，但是细胞×基因矩阵（scRNA-seq）
│   └─ 单细胞（single-cell/）
└─ NO，样本级表达矩阵（bulk/microarray）
    └─ bulk（general-bio/omicverse-bulk）
```

## 路由：任务轴（再判断这个）

| 任务 | 单细胞 | 空转 | bulk |
|---|---|---|---|
| QC/预处理/聚类 | `single-cell/omicverse-pipeline` | `spatial/omicverse-spatial` | `general-bio/omicverse-bulk` |
| 细胞注释 | `omicverse-pipeline`（CellTypist/SingleR） | — | — |
| 批次整合 | `omicverse-pipeline`（Harmony/scVI） | `omicverse-spatial` | `omicverse-bulk` |
| 差异表达 DE | `omicverse-pipeline`（🚨 pseudobulk） | `omicverse-spatial` | `omicverse-bulk`（pyDEG） |
| 去卷积 | — | 🚨 `spatial/deconvolution` | `omicverse-bulk` |
| 拟时序/轨迹 | `omicverse-pipeline` 或 `rna-velocity` | — | — |
| 细胞通讯 | `omicverse-pipeline` | `omicverse-spatial` | — |
| 富集(GO/GSEA) | `omicverse-bulk` | `omicverse-bulk` | `omicverse-bulk` |
| 扰动预测 | 🚨 `perturbation-prediction`（独立专题） | — | — |
| 高分辨率平台 | — | `spatial/multiomics` | — |
| 空间蛋白组 | — | `spatial/proteomics` | — |
| Perturb-seq 分析 | `perturb-seq` | — | — |
| 绘图 | `visualization/omicverse-plotting`（ov.pl） | 同左 | 同左 |
| 多面板组合图 | `visualization/multi-panel-figures` | 同左 | 同左 |
| 机制图/示意图 | `visualization/scientific-schematics` | 同左 | 同左 |
| 图形摘要 | `visualization/graphical-abstract` | 同左 | 同左 |
| PPT | `presentation/scientific-slides` 或 `lab-meeting-slides` | 同左 | 同左 |
| 写作 | `presentation/methods-writer`/`results-writer`/`figure-legend-writer` | 同左 | 同左 |
| 课题设计 | `single-cell/research-planner` | 同左 | 同左 |

### 🚨 Special Routing Rules（覆盖规则，优先级高于上表）

- **任何 DE** → 先确认 `layers['counts']` 存在；单细胞 DE 强制 pseudobulk（`ov.single` 或 `RunDEtest(cells.group.by=...)`），**禁** per-cell Wilcoxon
- **cell2location 去卷积** → omicverse 未注册，**强制** `spatial/deconvolution`
- **批次校正后** → embedding（X_scVI/X_harmony）**仅**可视化/聚类，**禁** DE/富集
- **RNA velocity** → 必须 spliced/unspliced layers；缺则先 velocyto
- **scGPT finetune** → GPU 必须；轻量 zero-shot 用 `ov.fm.scgpt`

## When to Use / When NOT to Use（引擎选择）

| 情况 | 用 | 不用 |
|---|---|---|
| 默认 Python scRNA/空转分析 | **OmicVerse**（`ov.*`） | — |
| R/Seurat 环境，或 scop 独有工具（CytoTRACE/Milo/scCODA/SecAct/Giotto/SmoothClust/EcoTyper） | **scop**（`single-cell/scop`） | omicverse（无对应） |
| 跨数据集注释 / 扰动预测 / GRN attention | **scGPT/扰动模型** | 常规注释（CellTypist 够） |
| 常规批次校正 | Harmony/scVI（omicverse 内） | scGPT（杀鸡用牛刀） |
| 常规轨迹 | Monocle/Slingshot（omicverse 内） | scGPT |
| 百万细胞 | **AnnDataOOM**（`ov.read(backend='rust')`） | 标准 AnnData（OOM） |

## 核心原则（强制，postcheck.py 可机检项标 ✅）

1. **真实数据优先**：mock 仅测试
2. **统计严谨**：单细胞 DE 用 pseudobulk ✅；FDR 校正（BH）✅；报告总检验数
3. **严格阈值**：DE Padj<0.05 & |Log2FC|>1.0 ✅；相关 Padj<0.05 & |r|>0.5
4. **关联≠因果**：用 "associated with" ✅，无证据不用 "regulates/causes"
5. **Python优先**：omicverse（已移植 Monocle/WGCNA/DoubletFinder）；仅无对应时用 R
6. **批次校正纪律**：校正 embedding 禁 DE/富集 ✅
7. **保守措辞**：biomarker 须验证队列；"potential candidate" 优先
8. **可复现**：保留 `layers['counts']` ✅；记录版本与种子 ✅
9. **空转特有**：去卷积报质量评估 ✅；空间域需生物学验证

> ✅ = `scripts/postcheck.py` 自动检查；其余靠人工。**分析完成后必须跑 postcheck**。

## 版本与架构

- **版本**：10.0.0（结构工程重构：双轴路由 + postcheck 闭环 + loading protocol）
- **引擎**：[OmicVerse V2](https://github.com/Starlitnightly/omicverse) + [scop](https://github.com/mengxu98/scop) + scGPT/扰动模型
- **子 skill**：20 个（见 `skill-index.json` 紧凑索引，或 `references/README.md` 全集目录）
- **架构演进**：v8（42独立）→ v9（omicverse 统一 + scop + 扰动专题）→ **v10（结构工程：路由/闭环/协议）**

## 索引文件职责

| 文件 | 角色 | 何时读 |
|---|---|---|
| `SKILL.md`（本文件） | **路由权威** | 总是先读 |
| `skill-index.json` | 紧凑索引（name/triggers/engine/path） | 需要快速定位子 skill 时 |
| `references/workflow_routing.md` | 决策树详情 | 路由表命中模糊、需细化时 |
| `references/omicverse_guide.md` | OmicVerse API 速查 | 用 ov.* 时 |
| `references/README.md` | 子 skill 全集目录 | 浏览全部能力时 |
| `scripts/postcheck.py` | 科学严谨性自动校验 | **分析完成后必跑** |
