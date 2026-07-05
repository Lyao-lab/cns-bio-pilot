# cns-bio-pilot 子skill 完整索引

42 个精选子skill，按类别组织。每个 skill 路径相对于本 skill 根目录。

## 🧬 空间转录组（spatial/，11个）

| skill | 来源 | 功能 | 关键工具 |
|---|---|---|---|
| `spatial/preprocessing` | OpenClaw | QC/归一化/特征选择 | scanpy, squidpy |
| `spatial/data-io` | OpenClaw | 加载 Visium/Xenium/MERFISH/Slide-seq | squidpy, spatialdata |
| `spatial/deconvolution` | OpenClaw | spot 细胞类型去卷积 | cell2location, Tangram, RCTD |
| `spatial/domains` | OpenClaw | 空间域/组织区域识别 | squidpy, BayesSpace, STAGATE |
| `spatial/communication` | OpenClaw | 空间细胞通讯分析 | CellChat, NicheNet 空间版 |
| `spatial/statistics` | OpenClaw | 空间统计（Moran's I, Geary's C） | squidpy |
| `spatial/neighbors` | OpenClaw | 空间邻域图构建 | squidpy |
| `spatial/visualization` | OpenClaw | 组织切片可视化 | squidpy, scanpy |
| `spatial/image-analysis` | OpenClaw | 组织图像分析（H&E配准） | squidpy, scikit-image |
| `spatial/multiomics` | OpenClaw | 高分辨率平台（Stereo-seq/Visium HD） | squidpy, spatialdata |
| `spatial/proteomics` | OpenClaw | 空间蛋白组（CODEX/IMC/MIBI） | squidpy, scimap |

## 🔬 单细胞（single-cell/，12个）

| skill | 来源 | 功能 | 关键工具 |
|---|---|---|---|
| `single-cell/preprocessing` | OpenClaw | QC/过滤/归一化 | scanpy, Seurat |
| `single-cell/doublet-detection` | OpenClaw | doublet 检测与去除 | scDblFinder, DoubletFinder |
| `single-cell/clustering` | OpenClaw | 降维聚类（PCA/UMAP/Leiden） | scanpy, Seurat |
| `single-cell/cell-annotation` | OpenClaw | 自动细胞类型注释 | CellTypist, SingleR, Azimuth, scPred |
| `single-cell/cell-communication` | OpenClaw | 细胞通讯网络推断 | CellChat, NicheNet, LIANA |
| `single-cell/trajectory-inference` | OpenClaw | 发育轨迹/拟时序 | Monocle, PAGA, Slingshot |
| `single-cell/batch-integration` | OpenClaw | 多批次整合 | Harmony, scVI, Seurat anchors |
| `single-cell/perturb-seq` | OpenClaw | Perturb-seq/CRISPR筛选 | pertpy, Cassiopeia |
| `single-cell/scvelo` | K-Dense | RNA velocity | scVelo |
| `single-cell/scvi-tools` | K-Dense | 深度生成模型（整合/去噪/多模态） | scVI, scANVI, totalVI |
| `single-cell/scanpy` | K-Dense | scanpy完整流水线（含15个CLI脚本） | scanpy + scripts工具箱 |
| `single-cell/research-planner` | aipoch | 单细胞课题设计（方法论） | 零代码，9个references |

## 📊 绘图（visualization/，7个）

| skill | 来源 | 功能 | 关键工具 |
|---|---|---|---|
| `visualization/multi-panel-figures` | aipoch | 6面板组合图（A-F） | patchwork, GridSpec |
| `visualization/volcano-plot` | aipoch | 火山图生成 | ggplot2, matplotlib |
| `visualization/heatmap` | aipoch | 热图美化（聚类+注释） | seaborn, ComplexHeatmap |
| `visualization/specialized-omics-plots` | OpenClaw | 组学专用图（dot/violin/track） | ggplot2, matplotlib |
| `visualization/interactive-visualization` | OpenClaw | 交互式探索图 | plotly, bokeh |
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

## 🧪 通用生信（general-bio/，7个）

| skill | 来源 | 功能 | 关键工具 |
|---|---|---|---|
| `general-bio/differential-expression` | aipoch | bulk差异表达 | DESeq2, edgeR, limma |
| `general-bio/batch-correction-de` | OpenClaw | DE批次校正 | ComBat, ComBat-Seq, limma |
| `general-bio/batch-correction` | aipoch | 表达矩阵批次校正 | limma, ComBat |
| `general-bio/gokegg` | aipoch | GO/KEGG富集 | clusterProfiler |
| `general-bio/gsea` | aipoch | GSEA富集 | fgsea, clusterProfiler |
| `general-bio/wgcna` | aipoch | 共表达网络 | WGCNA |
| `general-bio/ppi-network` | aipoch | 蛋白互作网络 | STRING |

## 去重记录

| 冲突 | 决策 |
|---|---|
| scanpy (aipoch 448行 vs K-Dense 511行+15脚本) | **保留 K-Dense**（更新，含CLI工具箱，修正统计） |
| OpenClaw bio-* vs bioSkills/ 嵌套副本 | 只取扁平 bio-* |
| single-* 旧版 vs bio-single-cell-* 新版 | 保留新版 |
| 多面板图 aipoch vs OpenClaw | 保留 aipoch（6面板固定布局） |
