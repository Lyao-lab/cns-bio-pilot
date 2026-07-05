---
name: cns-bio-pilot
description: 空间转录组与单细胞生信分析全流程技能库（基于 OmicVerse V2 统一引擎）。每当用户提到：空间转录组、空转、spatial transcriptomics、Visium、Xenium、MERFISH、Stereo-seq、Slide-seq、空间去卷积、空间域、spatial domain、单细胞、single-cell、scRNA-seq、聚类、细胞注释、cell type annotation、doublet、批次校正、batch correction、scVI、Harmony、RNA velocity、拟时序、trajectory、细胞通讯、CellChat、Perturb-seq、scanpy、squidpy、cell2location、omicverse、差异表达、DEG、富集分析、GO、KEGG、GSEA、WGCNA、PPI、画图、绘图、火山图、热图、UMAP、多面板图、graphical abstract、机制图、写论文、写 Methods、写 Results、图注、figure legend、做 PPT、做幻灯片、lab meeting、汇报，或要求"帮我分析空转/单细胞数据""设计课题""画发表级图表""写文章""做演示"时，都应触发。核心纪律：OmicVerse优先（统一 ov.* API）；统计严谨（伪bulk DE、FDR校正、严格阈值）；保守措辞（关联≠因果）；Python优先；可复现。
---

# CNS Bio-Pilot v9.0

空间转录组 + 单细胞为主、兼顾其他生信与论文产出的技能库。**以 OmicVerse V2 为统一引擎**，核心分析全部走 `ov.*` API；仅在 omicverse 不覆盖时（cell2location 去卷积、Perturb-seq、深度调参）才 fallback 到独立工具。

## OmicVerse 优先原则（核心范式）

1. **先装 omicverse**：`pip install omicverse` （V2 含 AnnDataOOM Rust 后端 + RebuildR R→Python 移植）
2. **分析走 ov.* API**：QC→`ov.pp.qc`，归一化→`ov.pp.preprocess`，聚类→`ov.pp.leiden`，去卷积→`ov.space.Deconvolution`，DE→`ov.bulk.pyDEG`，绘图→`ov.pl.*`
3. **大数据用 AnnDataOOM**：`ov.read(path, backend='rust')` 处理百万级细胞，170× 节省内存
4. **R 包已被移植**：Monocle2→`ov.single.Monocle`，DoubletFinder→`ov.pp.qc(doublets_method='doubletfinder')`，WGCNA→`ov.bulk.pyWGCNA`，无需 R 环境
5. **统一绘图**：`ov.pl.*` 80+ 函数，`ov.plot_set()` 初始化样式

> 完整 API 映射见 `references/omicverse_guide.md`

## 核心原则（强制）

1. **真实数据优先**：真实实验数据，mock 仅用于测试
2. **统计严谨**：单细胞 DE 用 pseudobulk（不要 per-cell Wilcoxon）；FDR 校正（BH）；报告总检验数
3. **严格阈值**：DE: Padj<0.05 & |Log2FC|>1.0；相关: Padj<0.05 & |r|>0.5
4. **关联≠因果**：用 "associated with"，无证据不用 "regulates/causes"
5. **Python优先**：omicverse 已移植绝大多数 R 包，优先 `ov.*`；仅 omicverse 无对应时用 R
6. **批次校正纪律**：校正后 embedding 仅用于可视化/聚类，**绝不**用于 DE/富集
7. **保守措辞**：biomarker 类结论须验证队列；"potential candidate" 优先
8. **可复现**：保留 raw counts 到 `layers['counts']`；记录 ov 版本与种子
9. **空转特有**：去卷积报告质量评估；空间域需生物学验证

## 工作流路由表

根据需求读取对应子 skill。**所有分析优先尝试 omicverse API。**

### 🧬 OmicVerse 统一流水线（核心，5个 skill 覆盖原 30+ 功能）

| 用户需求 | 读取 | omicverse API |
|---|---|---|
| 单细胞全流程（QC→聚类→注释→整合→通讯→轨迹） | `single-cell/omicverse-pipeline/SKILL.md` | `ov.pp.*` + `ov.single.*` |
| 空转全流程（除去卷积） | `spatial/omicverse-spatial/SKILL.md` | `ov.space.*` + `ov.io.read_*` |
| 空转去卷积（cell2location 等独立工具） | `spatial/deconvolution/SKILL.md` | cell2location（omicverse 未注册） |
| bulk 全流程（DE→富集→WGCNA→PPI） | `general-bio/omicverse-bulk/SKILL.md` | `ov.bulk.pyDEG/pyGSEA/pyWGCNA/pyPPI` |
| 统一绘图（80+ 函数） | `visualization/omicverse-plotting/SKILL.md` | `ov.pl.*` + `ov.plot_set()` |

### 🔬 需独立工具的场景（omicverse 未完全覆盖，保留专用 skill）

| 用户需求 | 读取 | 说明 |
|---|---|---|
| Perturb-seq / CRISPR 筛选 | `single-cell/perturb-seq/SKILL.md` | pertpy（omicverse 未覆盖） |
| RNA velocity 深度调参 | `single-cell/scvelo/SKILL.md` | `ov.single.Velo` 封装 scvelo，深度调参用原生 |
| 高分辨率空转（Stereo-seq/Visium HD） | `spatial/multiomics/SKILL.md` | 含 cellpose 等 |
| 空间蛋白组（CODEX/IMC/MIBI） | `spatial/proteomics/SKILL.md` | scimap |
| 单细胞课题设计 | `single-cell/research-planner/SKILL.md` | 方法论（无代码） |

### 📊 通用绘图/示意（omicverse 之外）

| 用户需求 | 读取 | 说明 |
|---|---|---|
| 多面板组合图（A-F 发表级） | `visualization/multi-panel-figures/SKILL.md` | PIL 拼图 |
| 机制图/流程图 | `visualization/scientific-schematics/SKILL.md` | LLM 生成 |
| 图形摘要 | `visualization/graphical-abstract/SKILL.md` | 布局推荐 |

### 📑 PPT/文稿（与 omicverse 无关，全保留）

| 用户需求 | 读取 |
|---|---|
| 研究汇报 PPT | `presentation/scientific-slides/SKILL.md` |
| 组会幻灯片 | `presentation/lab-meeting-slides/SKILL.md` |
| 写 Methods | `presentation/methods-writer/SKILL.md` |
| 写 Results | `presentation/results-writer/SKILL.md` |
| 图注 | `presentation/figure-legend-writer/SKILL.md` |

## 典型工作流（omicverse 统一）

**单细胞完整流程**（一个 skill 一站式）：
```python
import omicverse as ov
ov.plot_set()
adata = ov.read('data.h5ad', backend='rust')  # 大数据用 AnnDataOOM
ov.pp.qc(adata, doublets_method='scrublet')    # QC + doublet 一步
ov.pp.preprocess(adata, mode='shiftlog', n_HVGs=2000)
ov.pp.scale(adata); ov.pp.pca(adata, layer='scaled')
ov.pp.neighbors(adata); ov.pp.umap(adata)
ov.pp.leiden(adata, resolution='auto')         # auto_resolution
ov.single.batch_correction(adata, method='harmony')  # 多批次
# 注释/通讯/轨迹见 omicverse-pipeline/SKILL.md
ov.pl.embedding(adata, basis='X_umap', color='leiden')
```

**空转完整流程**：`spatial/omicverse-spatial` 一站式（含空间域、SVG、可视化），去卷积单独用 `spatial/deconvolution`

**bulk 完整流程**：`ov.bulk.pyDEG` → `ov.bulk.pyGSEA` → `ov.bulk.pyWGCNA` → `ov.pl.volcano/geneset_plot`

## 版本与架构

- **版本**：9.0.0（OmicVerse 统一引擎重构）
- **架构演进**：v8.0（42个独立子skill）→ v9.0（omicverse 统一，精简至 ~18 个）
- **引擎**：[OmicVerse V2](https://github.com/Starlitnightly/omicverse)（14模块/694方法/AnnDataOOM/RebuildR）
- **不可替代**：cell2location、pertpy、scvelo深度调参、空间蛋白组、PPT/写作类
- 完整 API 速查见 `references/omicverse_guide.md`，路由决策见 `references/workflow_routing.md`
