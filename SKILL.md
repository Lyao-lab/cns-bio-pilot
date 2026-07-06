---
name: cns-bio-pilot
description: 生信分析全流程技能库（空间转录组、单细胞、bulk 组学 + 绘图 + 论文/PPT 产出）。当用户要做生信分析、处理单细胞或空转数据、画发表级图表、写论文/PPT 时触发。核心原则：基于事实不懂就问不虚构；不重复造轮子（先检索 PubMed/GitHub/PyPI/R 库是否已有实现，实在没有才改造相似算法，GEO 下载用 GEOparse）。本 skill 是路由器——触发后读取它来确定走哪个子 skill，具体分析在子 skill 中进行。
---

# CNS Bio-Pilot

单细胞 + 空间转录组（兼 bulk/其他组学）生信分析技能库。三引擎：**OmicVerse**（Python，默认）+ **scop**（R/Seurat）+ **scGPT/扰动模型**（深度学习）。本文件是**路由器**——读它确定走哪个子 skill，不要在此执行分析。

## Loading Protocol（原因贯穿下文）

1. **永远只读**：本 SKILL.md + 命中的 **1 个**子 skill + 该子 skill 声明的 references
2. **不要一次读多个子 skill**——上下文窗口会被占满，路由判断与代码生成质量都会下降（一次只加载命中的那一个即可覆盖分析需求）
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

### 环境前提（conda 环境映射）

不同任务在不同 conda 环境，跑错环境会 `ModuleNotFoundError`：

| 任务类型 | conda 环境 | 关键包 | 激活 |
|---|---|---|---|
| 单细胞（omicverse 主力） | `sc` | omicverse 2.2.3 + scanpy + scvelo | `conda activate sc` |
| 空转（squidpy） | `st` | squidpy 1.2.2 + scanpy | `conda activate st` |
| R/scop | `scop_env` | scanpy + R/scop | `conda activate scop_env` |
| cell2location 去卷积 | 需新建 | cell2location（三个环境都缺） | `conda create -n c2l python=3.10` |

> postcheck.py 也要用**装了 anndata 的环境**跑（如 `sc`），否则报"anndata 未安装"。

### 数据/代码前提

匹配路由**之前**先排雷——这些是绝大多数生信错误的根因：

| 检查项 | 怎么查 | 不满足怎么办 |
|---|---|---|
| **raw counts 保留？** | `'counts' in adata.layers` | **DE/velocity 的生死线**——先备份 `adata.layers['counts']=adata.X.copy()`；一旦归一化覆盖 `.X`，DESeq2/负二项模型和速度推断都会失真 |
| **多批次？** | `adata.obs['batch'].nunique()>1` | 决定是否走 batch_correction；且**校正后 embedding 不用于 DE**——它移除了真实生物学差异，用于 DE 会同时抹掉疾病信号 |
| **数据规模** | `adata.n_obs` | >100k → 考虑 AnnDataOOM（`ov.read(backend='rust')`） |
| **环境就绪** | `python -c "import omicverse"` | 缺包 → 见子 skill 的安装段 |
| **GPU**（深度学习任务） | `torch.cuda.is_available()` | scGPT/GEARS finetune 必须 GPU；无则降级 CPU 推理或换方法 |
| **spliced/unspliced**（velocity） | `'spliced' in adata.layers` | scvelo 必须；缺 → 先跑 velocyto/kb_python |

### 方法实现前提（强制：实现前先检索，原则 2）

**写任何自定义分析代码前，必须先确认无现成实现**——按此顺序检索，命中即用，不自己写：

| 顺序 | 检索源 | 怎么查 | 命中则 |
|---|---|---|---|
| 1 | omicverse / scop 封装 | `dir(ov.pp)` / `dir(ov.single)` / `dir(ov.bulk)` / scop `Run*` | 直接调，最省 |
| 2 | 成熟独立包 | PyPI / [libraries.io](https://libraries.io) / GitHub awesome-single-cell | `pip install` 后用 |
| 3 | R/Bioconductor | [bioconductor.org](https://bioconductor.org/packages) 搜索 | R 脚本调 |
| 4 | 改造相似算法 | PubMed 方法学文献 + GitHub | 改造时注明"基于 X 改造" |

> **从头实现是最后手段**——必须先确认前 4 步都无果，并向用户说明"为什么所有现有方法都不适用"。GEO 数据下载用 GEOparse，不自写下载器；DEG 用 pydeseq2/edgeR，不手写统计。

## 路由：数据类型轴（先判断这个）

```
数据有空间坐标 / 组织切片？
├─ YES → 空间转录组（spatial/）
│   └─ 需去卷积？→ spatial/deconvolution（cell2location 无 ov 封装，omicverse 未注册该方法，直接调会 fallback 到 Tangram，精度不同，故走此 skill）
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
| 差异表达 DE | `omicverse-pipeline`（**pseudobulk**） | `omicverse-spatial` | `omicverse-bulk`（pyDEG） |
| 去卷积 | — | `spatial/deconvolution`（omicverse 未注册 cell2location） | `omicverse-bulk` |
| 空间域识别/SVG | — | `spatial/omicverse-spatial`（STAGATE/BayesSpace/Moran's I） | — |
| 拟时序/轨迹 | `omicverse-pipeline` 或 `rna-velocity` | — | — |
| 细胞通讯 | `omicverse-pipeline` | `omicverse-spatial` | — |
| 富集(GO/GSEA) | `omicverse-bulk` | `omicverse-bulk` | `omicverse-bulk` |
| 扰动预测 | `perturbation-prediction`（独立专题，与常规流程评估口径不同） | — | — |
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

### Special Routing Rules（覆盖规则，优先级高于上表，原因见下）

- **任何 DE** → 先确认 `layers['counts']` 存在；单细胞 DE 用 pseudobulk 而非 per-cell Wilcoxon——per-cell 假独立会膨胀自由度，p 值系统性偏小（误报率↑）
- **cell2location 去卷积** → 走 `spatial/deconvolution`——omicverse 未注册该方法，直接调 `ov.space.Deconvolution` 会 fallback 到 Tangram（精度不同）
- **批次校正后** → embedding（X_scVI/X_harmony）仅用于可视化/聚类——它移除了真实生物学差异，用于 DE/富集会同时抹掉疾病信号
- **RNA velocity** → 必须 spliced/unspliced layers；缺则先 velocyto——剪接动力学是速度推断的唯一输入，没有就只能改走拟时序
- **scGPT finetune** → GPU 必须（参数量大，CPU 上 finetune 不现实）；轻量 zero-shot 用 `ov.fm.scgpt`

## When to Use / When NOT to Use（引擎选择）

| 情况 | 用 | 不用 |
|---|---|---|
| 默认 Python scRNA/空转分析 | **OmicVerse**（`ov.*`） | — |
| R/Seurat 环境，或 scop 独有工具（CytoTRACE/Milo/scCODA/SecAct/Giotto/SmoothClust/EcoTyper） | **scop**（`single-cell/scop`） | omicverse（无对应） |
| 跨数据集注释 / 扰动预测 / GRN attention | **scGPT/扰动模型** | 常规注释（CellTypist 够） |
| 常规批次校正 | Harmony/scVI（omicverse 内） | scGPT（杀鸡用牛刀） |
| 常规轨迹 | Monocle/Slingshot（omicverse 内） | scGPT |
| 百万细胞 | **AnnDataOOM**（`ov.read(backend='rust')`） | 标准 AnnData（OOM） |

## 核心原则（原因贯穿下文；postcheck.py 可机检项标 ✅）

1. **基于事实，不懂就问，不猜测不虚构**：所有数据集名/accession/样本量/细胞类型标签/工具参数/生物学结论必须有出处——来自数据本身、官方文档、或文献。**任何不确定时，先问用户，不要猜**。绝不编造数据集元信息、accession 号、样本可用性、文献引用、API 签名、或分析结果。不确定的 API 参数用 `inspect.signature(func)` 或 `help()` 核实，不凭印象调用 ✅
2. **不重复造轮子，先检索后实现**：实现任何方法前，**必须先检索**是否已有现成实现——查 PubMed（方法学文献）、GitHub（`awesome-single-cell` / 主题 awesome 列表）、PyPI（`pip search` 替代：[libraries.io](https://libraries.io) / Bioconda）、CRAN/Bioconductor、omicverse/scop 是否已封装。检索顺序：**omicverse/scop 封装 > 成熟独立包 > R/Bioconductor > 改造相似算法 > 从头实现**。只有确认无现成方法时，才借鉴最相似的已有算法改造；改造时必须在报告里注明"基于 X 方法改造"及差异。**从头实现是最后手段，需向用户说明为什么所有现有方法都不适用**。GEO 数据下载用 GEOparse，不自写下载器
3. **真实数据优先**：mock 仅测试
4. **统计严谨**：单细胞 DE 用 pseudobulk ✅；FDR 校正（BH）✅；报告总检验数
5. **严格阈值**：DE Padj<0.05 & |Log2FC|>1.0 ✅；相关 Padj<0.05 & |r|>0.5
6. **关联≠因果**：用 "associated with" ✅，无证据不用 "regulates/causes"
7. **Python优先**：omicverse（已移植 Monocle/WGCNA/DoubletFinder）；仅无对应时用 R——与原则 2 联动：先查 omicverse/scop 有无封装
8. **批次校正纪律**：校正 embedding 不用于 DE/富集——校正旨在去批次，会一并移除真实生物学差异，用回 DE 会把疾病/处理信号也抹掉 ✅
9. **保守措辞**：biomarker 须验证队列；"potential candidate" 优先
10. **可复现**：保留 `layers['counts']` ✅；记录版本与种子 ✅
11. **空转特有**：去卷积报质量评估 ✅；空间域需生物学验证
12. **发表级绘图审美**：遵循 CNS figure guidelines——300 DPI+、Arial/Helvetica、双轨配色（离散分类=莫兰迪 Nord 柔和；连续表达=蓝白红共识，高=红；发散 log2FC=蓝白红）、矢量 PDF 首选、多图配色一致。详见 `references/figure_aesthetics.md`。`ov.plot_set()` 后需手动补 DPI=300 + 双轨配色 + font.type=42 ✅

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
| `references/figure_aesthetics.md` | CNS 发表级绘图审美规范（DPI/字体/配色/色盲） | **任何绘图前必读** |
| `references/README.md` | 子 skill 全集目录 | 浏览全部能力时 |
| `scripts/postcheck.py` | 科学严谨性自动校验 | **分析完成后必跑** |
