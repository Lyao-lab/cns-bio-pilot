# cns-bio-pilot 子skill 完整索引

19 个精选子skill，按类别组织。每个 skill 路径相对于本 skill 根目录。

> **架构说明**：双引擎——OmicVerse V2（Python，`ov.*` API）+ scop（R，`Run*` 动词，基于 Seurat）。核心分析优先 OmicVerse；R/Seurat 场景或 scop 独有工具（CytoTRACE/Milo/scCODA/SecAct/Giotto/SmoothClust/EcoTyper/scTenifold 等）用 scop。其余为不可替代的领域工具。

## 🧬 OmicVerse V2 统一流程（5个）

`pip install omicverse`（V2），一个 `import omicverse as ov` 覆盖 90% 常规分析。

| skill | 合并自 | 功能 | 关键 API |
|---|---|---|---|
| `single-cell/omicverse-pipeline` | preprocessing/doublet-detection/clustering/cell-annotation/batch-integration/cell-communication/trajectory-inference/scanpy/scvi-tools | 单细胞全流程（QC→doublet→聚类→注释→批次校正→通讯→轨迹） | `ov.pp.*`, `ov.single.*` |
| `spatial/omicverse-spatial` | preprocessing/data-io/domains/neighbors/statistics/visualization/communication/image-analysis | 空转全流程（IO→空间邻域→SVG→空间域→通讯→可视化） | `ov.io.read_*`, `ov.pp.spatial_neighbors`, `ov.space.*`, `ov.pl.plot_spatial` |
| `general-bio/omicverse-bulk` | differential-expression/gokegg/gsea/wgcna/ppi-network/batch-correction/batch-correction-de | bulk 全流程（DE→富集→WGCNA→PPI→批次校正）纯 Python 无 R | `ov.bulk.pyDEG/pyGSEA/pyWGCNA/pyPPI/batch_correction` |
| `visualization/omicverse-plotting` | heatmap/volcano-plot/specialized-omics-plots/interactive-visualization | 统一绘图（80+ 函数） | `ov.plot_set()`, `ov.pl.*` |
| `single-cell/rna-velocity` | scvelo（重命名重写） | RNA velocity | `ov.single.Velo(adata, mode='scvelo')` |

## 🔬 单细胞（single-cell/，5个）

| skill | 来源 | 功能 | 关键工具 |
|---|---|---|---|
| `single-cell/omicverse-pipeline` | OmicVerse V2 | 单细胞全流程统一 API（Python） | `ov.pp.*` + `ov.single.*` |
| `single-cell/scop` | [mengxu98/scop](https://github.com/mengxu98/scop) v0.8.9 | R/Seurat 单细胞+空转全流程（200+ Run* 动词，双引擎互补） | Seurat, reticulate, Signac |
| `single-cell/rna-velocity` | OmicVerse V2 | RNA velocity（封装 scvelo/dynamo） | `ov.single.Velo` |
| `single-cell/perturb-seq` | OpenClaw | Perturb-seq/CRISPR筛选 | pertpy, Cassiopeia |
| `single-cell/research-planner` | aipoch | 单细胞课题设计（方法论） | 零代码，9个references |

## 🧫 空间转录组（spatial/，4个）

| skill | 来源 | 功能 | 关键工具 |
|---|---|---|---|
| `spatial/omicverse-spatial` | OmicVerse V2 | 空转全流程统一 API | `ov.space.*` |
| `spatial/deconvolution` | OpenClaw | spot 细胞类型去卷积 | cell2location, Tangram, RCTD |
| `spatial/multiomics` | OpenClaw | 高分辨率平台（Stereo-seq/Visium HD） | squidpy, spatialdata |
| `spatial/proteomics` | OpenClaw | 空间蛋白组（CODEX/IMC/MIBI） | squidpy, scimap |

## 🧪 通用生信（general-bio/，1个）

| skill | 来源 | 功能 | 关键工具 |
|---|---|---|---|
| `general-bio/omicverse-bulk` | OmicVerse V2 | bulk 全流程纯 Python（DE/富集/WGCNA/PPI/批次校正） | `ov.bulk.*`（pyDESeq2/GSEApy/pyWGCNA） |

## 📊 绘图（visualization/，4个）

| skill | 来源 | 功能 | 关键工具 |
|---|---|---|---|
| `visualization/omicverse-plotting` | OmicVerse V2 | 统一绘图 API（80+ 函数） | `ov.pl.*`, `ov.plot_set()` |
| `visualization/multi-panel-figures` | aipoch | 6面板组合图（A-F） | patchwork, GridSpec |
| `visualization/scientific-schematics` | aipoch | 机制图/流程图/架构图 | scientific-schematics |
| `visualization/graphical-abstract` | aipoch | 图形摘要布局 | 布局推荐 |

## 📑 PPT/文稿（presentation/，5个）

| skill | 来源 | 功能 |
|---|---|---|
| `presentation/scientific-slides` | OpenClaw | 研究汇报PPT（beamer/pptx模板） |
| `presentation/lab-meeting-slides` | aipoch | 组会/lab meeting 幻灯片 |
| `presentation/methods-writer` | aipoch | 协议→Methods文字 |
| `presentation/results-writer` | aipoch | 结果→Results叙述 |
| `presentation/figure-legend-writer` | aipoch | 独立可读图注 |

## 重构去重记录

| 冲突 | 决策 |
|---|---|
| scanpy (aipoch 448行 vs K-Dense 511行+15脚本) | **全部并入** `single-cell/omicverse-pipeline`（OmicVerse V2 统一 API 取代） |
| preprocessing/doublet/clustering/annotation/integration/communication/trajectory | **合并为** `single-cell/omicverse-pipeline` |
| scvi-tools | **合并进** `single-cell/omicverse-pipeline`（`ov.single.batch_correction(method='scvi')`） |
| scvelo | **重命名重写为** `single-cell/rna-velocity`（`ov.single.Velo` 封装） |
| spatial preprocessing/io/domains/neighbors/stats/viz/comm/image | **合并为** `spatial/omicverse-spatial`（去卷积另立 `spatial/deconvolution`） |
| DE/gokegg/gsea/wgcna/ppi/batch-correction(-de) | **合并为** `general-bio/omicverse-bulk`（纯 Python，无 R） |
| heatmap/volcano/specialized/interactive | **合并为** `visualization/omicverse-plotting`（`ov.pl.*`） |
| 不可替代（保留） | deconvolution / multiomics / proteomics / perturb-seq / research-planner / multi-panel-figures / scientific-schematics / graphical-abstract / presentation×5 |
