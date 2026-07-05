---
name: cns-bio-pilot
description: 空间转录组与单细胞生信分析全流程技能库（路由器架构）。每当用户提到：空间转录组、空转、spatial transcriptomics、Visium、Xenium、MERFISH、Stereo-seq、Slide-seq、空间去卷积、空间域、spatial domain、单细胞、single-cell、scRNA-seq、聚类、细胞注释、cell type annotation、doublet、批次校正、batch correction、scVI、Harmony、RNA velocity、拟时序、trajectory、细胞通讯、CellChat、Perturb-seq、scanpy、squidpy、squidy、cell2location、差异表达、DEG、富集分析、GO、KEGG、GSEA、WGCNA、PPI、画图、绘图、火山图、热图、UMAP、多面板图、graphical abstract、机制图、写论文、写 Methods、写 Results、图注、figure legend、做 PPT、做幻灯片、lab meeting、汇报，或要求"帮我分析空转/单细胞数据""设计课题""画发表级图表""写文章""做演示"时，都应触发。核心纪律：先理解需求再路由到对应子skill；统计严谨（伪bulk DE、FDR校正、严格阈值）；保守措辞（关联≠因果）；Python优先；可复现。
---

# CNS Bio-Pilot

空间转录组 + 单细胞为主、兼顾其他生信与论文产出的**路由器技能**。本文件是入口与导航；具体方法在 `skills/<category>/<name>/SKILL.md` 中按需加载。

## 核心原则（强制，贯穿所有子skill）

1. **真实数据优先**：真实实验数据，mock 数据仅用于测试
2. **统计严谨**：单细胞 DE 用 pseudobulk（不要 per-cell Wilcoxon）；FDR 校正（BH）；报告总检验数
3. **严格阈值**：DE: Padj<0.05 & |Log2FC|>1.0；相关: Padj<0.05 & |r|>0.5
4. **关联≠因果**：用 "associated with"，无证据不用 "regulates/causes"
5. **Python优先**：scanpy/squidpy/scvi 优先于 Seurat；pydeseq2 优先于 DESeq2；仅 Python 无对应工具时用 R
6. **批次校正纪律**：校正后 embedding 仅用于可视化/聚类，**绝不**用于 DE/富集
7. **保守措辞**：biomarker 类结论须验证队列；"potential candidate" 优先
8. **可复现**：保留 raw counts 到 `layers['counts']`；记录软件版本与随机种子
9. **空转特有**：去卷积结果要报告质量评估；空间域要生物学验证而非纯算法

## 工作流路由表（核心）

根据用户需求，读取对应的子 skill。**先读路由表，再加载具体 skill。**

### 🧬 空间转录组（11 skills，路径 `skills/spatial/`）

| 用户需求 | 读取 | 关键工具 |
|---|---|---|
| 空转数据 QC/归一化/筛选 | `spatial/preprocessing/SKILL.md` | scanpy, squidpy |
| 加载 Visium/Xenium/MERFISH 等 | `spatial/data-io/SKILL.md` | squidpy, spatialdata |
| spot 细胞类型去卷积 | `spatial/deconvolution/SKILL.md` | cell2location, Tangram, RCTD |
| 空间域/组织区域识别 | `spatial/domains/SKILL.md` | squidpy, BayesSpace, STAGATE |
| 空间细胞通讯 | `spatial/communication/SKILL.md` | CellChat, NicheNet 空间版 |
| 空间统计（Moran's I 等） | `spatial/statistics/SKILL.md` | squidpy |
| 空间邻域图 | `spatial/neighbors/SKILL.md` | squidpy |
| 空间可视化（组织切片图） | `spatial/visualization/SKILL.md` | squidpy, scanpy |
| 组织图像分析（H&E配准） | `spatial/image-analysis/SKILL.md` | squidpy, scikit-image |
| 高分辨率平台（Stereo-seq/Visium HD） | `spatial/multiomics/SKILL.md` | squidpy, spatialdata |
| 空间蛋白组（CODEX/IMC/MIBI） | `spatial/proteomics/SKILL.md` | squidpy, scimap |

### 🔬 单细胞（12 skills，路径 `skills/single-cell/`）

| 用户需求 | 读取 | 关键工具 |
|---|---|---|
| scRNA QC/归一化 | `single-cell/preprocessing/SKILL.md` | scanpy, Seurat |
| doublet 检测 | `single-cell/doublet-detection/SKILL.md` | scDblFinder, DoubletFinder |
| 降维聚类（PCA/UMAP/Leiden） | `single-cell/clustering/SKILL.md` | scanpy, Seurat |
| 细胞类型注释 | `single-cell/cell-annotation/SKILL.md` | CellTypist, SingleR, Azimuth |
| 细胞通讯 | `single-cell/cell-communication/SKILL.md` | CellChat, NicheNet, LIANA |
| 拟时序/轨迹推断 | `single-cell/trajectory-inference/SKILL.md` | Monocle, PAGA, Slingshot |
| 多批次整合 | `single-cell/batch-integration/SKILL.md` | Harmony, scVI, Seurat anchors |
| Perturb-seq/CRISPR 筛选 | `single-cell/perturb-seq/SKILL.md` | pertpy, Cassiopeia |
| RNA velocity（剪接动力学） | `single-cell/scvelo/SKILL.md` | scVelo |
| 深度学习整合/去噪/多模态 | `single-cell/scvi-tools/SKILL.md` | scVI, scANVI, totalVI |
| scanpy 完整流水线（含15个CLI脚本） | `single-cell/scanpy/SKILL.md` | scanpy + scripts 工具箱 |
| 单细胞课题设计/研究规划 | `single-cell/research-planner/SKILL.md` | 方法论（零代码） |

### 📊 绘图（7 skills，路径 `skills/visualization/`）

| 用户需求 | 读取 | 关键工具 |
|---|---|---|
| 6面板组合图（A-F 发表级） | `visualization/multi-panel-figures/SKILL.md` | patchwork, GridSpec |
| 火山图 | `visualization/volcano-plot/SKILL.md` | ggplot2, matplotlib |
| 热图美化（聚类+注释） | `visualization/heatmap/SKILL.md` | seaborn, ComplexHeatmap |
| 组学专用图（dot/violin/track） | `visualization/specialized-omics-plots/SKILL.md` | ggplot2, matplotlib |
| 交互式探索图 | `visualization/interactive-visualization/SKILL.md` | plotly, bokeh |
| 机制图/流程图/架构图 | `visualization/scientific-schematics/SKILL.md` | scientific-schematics |
| 图形摘要（Graphical Abstract） | `visualization/graphical-abstract/SKILL.md` | 布局推荐 |

### 📑 PPT/文稿（5 skills，路径 `skills/presentation/`）

| 用户需求 | 读取 | 说明 |
|---|---|---|
| 研究汇报 PPT（正式） | `presentation/scientific-slides/SKILL.md` | 含beamer/pptx模板 |
| 组会/lab meeting 幻灯片 | `presentation/lab-meeting-slides/SKILL.md` | 进度汇报结构 |
| 写 Methods 章节 | `presentation/methods-writer/SKILL.md` | 协议→发表文字 |
| 写 Results 章节 | `presentation/results-writer/SKILL.md` | 结果→叙述 |
| 写图注（Figure Legend） | `presentation/figure-legend-writer/SKILL.md` | 独立可读图注 |

### 🧪 通用生信（7 skills，路径 `skills/general-bio/`）

| 用户需求 | 读取 | 关键工具 |
|---|---|---|
| bulk RNA-seq 差异表达 | `general-bio/differential-expression/SKILL.md` | DESeq2, edgeR, limma |
| DE 批次校正（ComBat 类） | `general-bio/batch-correction-de/SKILL.md` | ComBat, ComBat-Seq |
| 合并表达矩阵批次校正 | `general-bio/batch-correction/SKILL.md` | limma, ComBat |
| GO/KEGG 富集 | `general-bio/gokegg/SKILL.md` | clusterProfiler |
| GSEA（预排序基因集富集） | `general-bio/gsea/SKILL.md` | fgsea, clusterProfiler |
| WGCNA 共表达网络 | `general-bio/wgcna/SKILL.md` | WGCNA |
| PPI 蛋白互作网络 | `general-bio/ppi-network/SKILL.md` | STRING |

## 典型工作流（端到端示例）

**空转完整流程**：`spatial/data-io` → `spatial/preprocessing` → `spatial/neighbors` → `spatial/domains` → `spatial/deconvolution` → `spatial/communication` → `spatial/visualization` → `presentation/scientific-slides`

**单细胞完整流程**：`single-cell/preprocessing` → `doublet-detection` → `clustering` → `cell-annotation` → `batch-integration`（多批次时）→ `cell-communication`/`trajectory-inference` → `visualization/multi-panel-figures` → `presentation/methods-writer`

**bulk+空转联合**：`general-bio/differential-expression` → 把 DE 基因映射到空转 → `spatial/visualization`

## 路由决策树

```
用户需求是什么类型？
│
├─ 空间转录组（有空间坐标/组织切片）
│   ├─ 加载数据 → spatial/data-io
│   ├─ 质控预处理 → spatial/preprocessing
│   ├─ 细胞类型构成 → spatial/deconvolution
│   ├─ 区域划分 → spatial/domains
│   ├─ 细胞间信号 → spatial/communication
│   └─ 画图 → spatial/visualization
│
├─ 单细胞（有细胞×基因矩阵，无空间）
│   ├─ 质控 → single-cell/preprocessing + doublet-detection
│   ├─ 分群 → single-cell/clustering
│   ├─ 命名细胞 → single-cell/cell-annotation
│   ├─ 多样本 → single-cell/batch-integration
│   ├─ 时间/发育 → single-cell/trajectory-inference 或 scvelo
│   ├─ 细胞通讯 → single-cell/cell-communication
│   ├─ 扰动实验 → single-cell/perturb-seq
│   └─ 深度学习 → single-cell/scvi-tools
│
├─ bulk/其他组学
│   ├─ 差异表达 → general-bio/differential-expression
│   ├─ 富集 → general-bio/gokegg 或 gsea
│   ├─ 网络 → general-bio/wgcna 或 ppi-network
│   └─ 批次 → general-bio/batch-correction
│
├─ 画图
│   ├─ 组合多面板 → visualization/multi-panel-figures
│   ├─ 单类图 → volcano-plot / heatmap / specialized-omics-plots
│   ├─ 示意图 → scientific-schematics / graphical-abstract
│   └─ 交互 → interactive-visualization
│
└─ 论文产出
    ├─ PPT → presentation/scientific-slides 或 lab-meeting-slides
    ├─ 写作 → presentation/methods-writer / results-writer / figure-legend-writer
    └─ 课题设计 → single-cell/research-planner
```

## 版本与来源

- **版本**：8.0.0（路由器架构）
- **子skill 来源**（去重整合，保留上游原版）：
  - [FreedomIntelligence/OpenClaw-Medical-Skills](https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills) — 空转11 + 单细胞8 + 可视化2 + slides + DE批次
  - [aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills) — 可视化5 + PPT/写作4 + 通用生信6 + 课题设计
  - [K-Dense-AI/scientific-agent-skills](https://github.com/k-dense-ai/scientific-agent-skills) — scanpy(含CLI工具箱) + scvelo + scvi-tools
- **去重规则**：scanpy 取 K-Dense 版（更新，含15个CLI脚本）；OpenClaw 只取扁平 bio-* 不取嵌套副本

## 子skill 索引统计

| 类别 | 数量 |
|---|---|
| spatial（空转） | 11 |
| single-cell（单细胞） | 12 |
| visualization（绘图） | 7 |
| presentation（PPT/文稿） | 5 |
| general-bio（通用生信） | 7 |
| **合计** | **42** |

完整索引见 `references/README.md`，详细路由决策见 `references/workflow_routing.md`。
