# 工作流路由决策指南

详细的路由决策逻辑，帮助判断用户需求该走哪个子 skill。

## 判断数据类型（第一步）

```
数据有空间坐标/组织切片图像？
├─ YES → 空间转录组路线（spatial/）
│   判断平台：
│   ├─ Visium (10x) → spatial/data-io 支持
│   ├─ Xenium (10x) → spatial/data-io 支持
│   ├─ MERFISH → spatial/data-io 支持
│   ├─ Slide-seq / Stereo-seq → spatial/multiomics（高分辨率）
│   ├─ CODEX/IMC/MIBI（蛋白） → spatial/proteomics
│   └─ 其他 → spatial/data-io 通用
│
└─ NO → 判断是否有细胞×基因矩阵
    ├─ YES（单细胞级别） → 单细胞路线（single-cell/）
    └─ NO（bulk/矩阵是样本级） → 通用生信路线（general-bio/）
```

## 空间转录组完整路线

```
1. 加载数据        → spatial/data-io
   ├─ 检查：adata.obsm['spatial'] 存在？
   └─ 输出：spatially-aware AnnData

2. 质控预处理      → spatial/preprocessing
   ├─ 过滤低质量 spot
   ├─ 归一化（注意：保留 raw counts 到 layers['counts']）
   └─ HVG 选择

3. 空间邻域图      → spatial/neighbors
   └─ 计算 k-NN / 空间权重图（squidpy.gr.spatial_neighbors）

4. 分支（按目标）：
   ├─ 想知道每个 spot 的细胞构成
   │   → spatial/deconvolution（cell2location/Tanggram/RCTD）
   │   ⚠️ 必须报告去卷积质量评估
   │
   ├─ 想划分组织区域
   │   → spatial/domains（squidpy/BayesSpace/STAGATE）
   │   ⚠️ 空间域需生物学验证，不能纯算法
   │
   ├─ 想看细胞间信号
   │   → spatial/communication（空间CellChat/NicheNet）
   │
   ├─ 想算空间变异基因
   │   → spatial/statistics（Moran's I, Geary's C）
   │
   └─ 想分析配对的组织图像
       → spatial/image-analysis（H&E配准/形态学特征）

5. 可视化          → spatial/visualization
   └─ 组织切片叠加表达/注释
```

## 单细胞完整路线

```
1. 质控            → single-cell/preprocessing
   └─ 紧接着 → single-cell/doublet-detection（去 doublet）

2. 降维聚类        → single-cell/clustering
   ├─ PCA → 邻居图 → Leiden/Louvain → UMAP/tSNE
   └─ 多批次？ → 先 single-cell/batch-integration
       ├─ 快速/CPU → Harmony
       ├─ 大规模/GPU → scVI (single-cell/scvi-tools)
       └─ 参考图谱 → scANVI

3. 细胞命名        → single-cell/cell-annotation
   ├─ 有参考 → CellTypist/SingleR/Azimuth
   └─ 无参考 → marker 基因手动注释

4. 下游分析（按目标）：
   ├─ 发育/时间序列
   │   ├─ 拟时序 → single-cell/trajectory-inference (Monocle/PAGA)
   │   └─ RNA velocity → single-cell/scvelo（剪接动力学）
   │
   ├─ 细胞间信号
   │   → single-cell/cell-communication (CellChat/NicheNet/LIANA)
   │
   ├─ CRISPR 扰动实验
   │   → single-cell/perturb-seq (pertpy/Cassiopeia)
   │
   └─ 多模态（CITE-seq/多组学）
       → single-cell/scvi-tools (totalVI)

5. DE 分析（重要纪律）
   ├─ ⚠️ 不要 per-cell Wilcoxon
   ├️ 用 pseudobulk（按样本+细胞类型聚合后 DESeq2/edgeR）
   └️ 或 mixed model（muscat/NEBULA）

6. scanpy 用户      → single-cell/scanpy（15个CLI脚本工具箱）
```

## 通用生信路线（bulk/其他）

```
有表达矩阵 + 分组？
├─ 差异表达 → general-bio/differential-expression
│   ├─ 有批次 → 先 general-bio/batch-correction-de
│   └─ DESeq2/edgeR/limma
│
├─ 拿到基因列表后：
│   ├─ GO/KEGG → general-bio/gokegg
│   ├─ GSEA（需排序列表） → general-bio/gsea
│   ├─ 共表达模块 → general-bio/wgcna
│   └─ 蛋白互作 → general-bio/ppi-network
│
└─ 多数据集合并 → general-bio/batch-correction
```

## 绘图路线

```
要画什么？
├─ 多张图组合成发表级 figure → visualization/multi-panel-figures
├─ 差异结果 → visualization/volcano-plot
├─ 表达模式 → visualization/heatmap
├─ 单细胞/组学专用（dot/violin/track） → visualization/specialized-omics-plots
├─ 网页/交互探索 → visualization/interactive-visualization
├─ 机制/流程示意图 → visualization/scientific-schematics
└─ 论文 Graphical Abstract → visualization/graphical-abstract
```

## 论文产出路线

```
分析做完后要产出什么？
├─ 正式汇报 PPT → presentation/scientific-slides（beamer/pptx）
├─ 组会幻灯片 → presentation/lab-meeting-slides
├─ Methods 文字 → presentation/methods-writer
├─ Results 叙述 → presentation/results-writer
├─ 图注 → presentation/figure-legend-writer
└─ 课题设计（分析前） → single-cell/research-planner
```

## 常见陷阱与强制规则

1. **批次校正后数据禁用于 DE**：Harmony/scVI 校正后的 embedding 只用于聚类/可视化，DE 必须用 raw counts（pseudobulk）
2. **空转去卷积要验证**：报告 cell2location 的 reconstruction quality、对照已知 marker
3. **空间域不是聚类**：必须用空间感知方法（squidpy spatial neighbors + 图聚类），不能用普通 Leiden
4. **RNA velocity 需剪接信息**：spliced/unspliced layers 必须存在（velocyto/KB 输出），没有则不能用 scvelo
5. **细胞注释保守**：reference-based（CellTypist/SingleR）优于 marker 手动；低置信度标 "Unknown"
6. **所有图保留原始数据**：N、统计检验、Padj 必须在图注或图内可见
