# Figure Guide — 生信发表级图表视觉规格

> 本文件 = 视觉规格 + 原则 + 实战教训 + 数据→图型决策表（**不含代码**）。
> 代码模板查 `plotting_reference.md`；外部 omicverse-skills 参考查 `omicverse_skills_examples.md`；cns_style 包函数速查见 tool_registry.md（包内各模块 docstring 为准）。

---

## 0. 速查指引（画图前先看）

先定框架（哪种图、几张、怎么拼）再动笔——图型三层路由：**§0.2 数据形态→图型**（底座，按数据结构选最美形态）→ **§0.1 分析输出→图型**（分析语境）→ **图型域偏好**（域约束）；每张图 savefig 前必须过 `finalize_figure(fig)`。**整篇 fig 顺序（第几张 fig 讲什么）先查 `references/figure_templates.md` §0 自动路由表**（领域→领域卡，最强发现→研究型模板；506 篇 CNS 论文泛化）；本文件管**单张 panel 的图型选择**——下表 = 要画什么 → 代码模板 → 视觉规格章节。

| 要画什么 | 代码模板 | 关键规格（本文件章节）|
|---|---|---|
| UMAP/tSNE | plotting_reference §2.1/§3.4 | §5.1, 铁律3 |
| Volcano | §2.2 | §5.2 |
| Dotplot | §2.3 | §5.3 |
| Violin | §2.4 | §5.4 |
| Heatmap | §2.5 | §5.5 |
| Spatial | §2.6 | §5.6, §11.1 |
| Bar/比例 | §2.7 | §5.7 |
| 富集条形 | §2.8 | §5.8 |
| L-R Bubble | §2.9 | §5.9 |
| Feature 矩阵 | §2.10 | §5.10 |
| **PAGA** | §3.1 | §5.11 |
| **CCC（chord/network 统一入口）** | §3.2 | §5.12 |
| **Pseudotime** | §3.3 | §5.11 |
| **cellproportion** | §3.5 | §5.7 |
| **山脊/箱线/KDE/直方/抖动散点** | §3.16-§3.20 | §5.4 |
| **云雨图（半小提琴+箱线+雨点）** | §3.34 | §5.4 |
| **堆叠面积/柱+点组合** | §3.21-§3.22 | §5.7 |
| **堆叠火山/UpSet/Venn/森林/回归** | §3.23-§3.27 | §5.2/§5.8 |
| **通讯热图/PCA方差比/HVG散点** | §3.28-§3.30 | §5.5/§5.1 |
| **雷达图（多指标方法对比）** | §3.31 | §5.13 |
| **斜率图（组成 movers）** | §3.35 | §5.7 |
| **统计量 dotplot（多实体单统计量·首选）** | §3.46 | §5.3 |
| **发散棒棒糖（⚕默认降级→§3.46）** | §3.36 | §5.2 |
| **QC 条形卡片（样本×指标）** | §3.37 | §5.1 |
| **样本趋势小倍数（供体验证）** | §3.38 | §5.7 |
| **空间放大图（IF 风格 zoom+inset）** | §3.39 | §5.6 |
| **Sankey 状态转换/命运流** | §3.41 | — |
| **CNV 基因组热图（inferCNV 式）** | §3.42 | §5.5 |
| **轴向/距离梯度曲线（zonation/边界带）** | §3.43 | — |
| **克隆扩增追踪（TCR，composition/track）** | §3.44 | §5.7 |
| **工具层（stamp/断言/防撞标签/bar 坐标）** | §3.40 | — |

---

## 0.1 数据类型 → 图型决策表（选图前先查）

> §0 速查卡是"要画 UMAP → 代码在哪"（图型→代码）。本表是反方向：**我有 DE 结果/比例表/CCC/niche 数据，该用哪种图？**（数据→图型）。
> 基于 2025-2026 CNS 论文实践与 best-practices 文献（含 Neuro-Oncology Advances 2026 pitfalls 论文原话级建议）。
> **核心原则：UMAP 只是"地图"不是"证据"**——2026 年审稿趋势要求用 heatmap/定量图做证据，UMAP 降为索引图。

### 决策表（分析输出类型 → 首选图型 + 何时换图）

| 分析输出 | 首选图型 | 何时换备选 | 备选 | 代码模板 |
|---|---|---|---|---|
| **细胞类型注释总览** | UMAP 按类型着色 | 仅作"地图"；注释**证据**用 dotplot/heatmap | dotplot（marker 紧凑展示）；heatmap（严谨证据） | §2.1/§2.3/§2.5 |
| **marker 注释证据** | dotplot（点=%表达，色=均值） | 基因>20 或需展示表达分布 | violin（每基因分布）；heatmap（genes×cells 带 metadata 条） | §2.3/§2.4/§2.5 |
| **严谨注释证据**（审稿级） | genes×cells heatmap（带类型/样本/condition 注释条） | 细胞太多→按类均值 heatmap | ridge plot | §2.5 |
| **比例变化（有重复）** | 分组柱/点图（每点=一样本）+ 统计检验 | 条件>3→heatmap（celltype×condition） | 云雨图；箱线图；Milo beeswarm（无预定义 cluster） | §2.7/§3.34 |
| **比例变化（无重复）** | 堆叠柱（100%归一化） | **只能放 supplement**，正文不可做条件比较 | — | §3.5 |
| **局部丰度变化（无预定义cluster）** | Milo beeswarm（logFC 映射 KNN 图节点） | 需配类型/空间注释才可读 | DA neighborhood heatmap | §3.8 |
| **DE 单一对比** | volcano（pseudobulk 前提！） | per-cell Wilcoxon 做的 DE **禁止**画 volcano | MA plot | §2.2 |
| **DE 多时点/多条件** | 分组散点（x=组别，y=logFC，每点=一基因） | volcano 无法容纳>1 个对比维度 | logFC×time heatmap | §3.6 |
| **DE 基因模块/模式** | heatmap（行=基因，列=样本/伪群，带注释条） | — | — | §2.5 |
| **候选基因验证** | violin/ridge（按类型+condition 分面） | 把 DE 结论落回单细胞层面 | feature plot | §2.4 |
| **轨迹总览** | UMAP 按 pseudotime 着色 | **禁止用 UMAP 形状论证轨迹方向** | 按 branch 着色 | §2.1 |
| **轨迹拓扑/分支证据** | PAGA/图抽象 或 branch 树状图 | 拓扑断言用图模型而非 embedding 形状 | fate probability 矩阵 | §3.1 |
| **轨迹基因动态证据** | gene-along-pseudotime 曲线（带 CI/平滑） | 轨迹论文的"证据图"永远是这个，不是 UMAP | 分 bin heatmap | §3.3 |
| **CCC 强度+显著性** | bubble/dot plot（LR对×细胞类型对） | 信息密度最高的标准形式 | LR heatmap | §2.9 |
| **组成变化 top movers（3-4 时点×类型）** | 斜率图（端点直接标签带 Δ） | 类型>8 或时点>4 时换 heatmap（celltype×time） | 堆叠面积（全量背景）；heatmap | §3.35 |
| **模块/TF-性状相关（多实体单统计量）** | **统计量 dotplot**（色=ρ、径=\|ρ\|或 -log10p、行按值排序；§3.46） | 实体×分组二维（如 module×TF）→ 2D 点矩阵形态（同入口 group_col）；实体>25 → heatmap；双统计量+置换零带必须同面板时才用棒棒糖 | 发散棒棒糖（仅点名/零带场景）；forest ⚕临床 meta 专用 | §3.46 |
| **样本 QC 总览（n≤25 供体）** | QC 条形卡片（行=样本、列=指标+GA 色块） | 样本>25 换分位数概览表 | barh 每指标一张 | §3.37 |
| **供体级程序/基因得分验证** | 趋势小倍数（点径∝n、标题内嵌 ρ） | 实体>16 时换 module×donor heatmap | regplot 单面板 | §3.38 |
| **空间局部信号/区域放大** | IF 风格放大图（自动取框+inset 定位） | 多类型×多时点网格时循环调用共享 vmax | plot_spatial 全片 | §3.39 |
| **CCC 方向性叙事** | chord（≤8 类型） | chord 丢 LR 细节，只适合"谁给谁收信号" | network（>8 类型/复杂拓扑） | §3.2 |
| **CCC 信号角色模式** | outgoing-incoming pattern heatmap | 展示 sender/receiver/mediator 角色 | — | §3.9 |
| **空间单基因表达** | feature plot（spot/细胞着色） | 成像平台用单分子点渲染 | 阈值二值图（低表达基因） | §2.6 |
| **空间+形态学** | H&E/IF 底图 overlay | 形态学结论必须 overlay 或并排 | 相邻并排面板 | §2.6 |
| **空间多基因共表达** | RGB 合成图（≤3-4 基因） | 基因>4 换面板网格 | 共表达散点+空间 mask | — |
| **空间 niche/domain** | 组织 categorical 着色（边界清晰） | **必须配定量面板**："在哪里"+"差多少"成对出现 | domain 边界描线 | §2.6 |
| **空间 niche 定量** | 每 niche 细胞密度/组成/签名 score（箱线+点） | 着色图负责"在哪里"，此图负责"差多少" | domain×celltype 富集 heatmap | §2.7 |
| **空间去卷积** | 每关键类型一张比例空间散点图 | 类型>6 时 per-spot pie 不可读 | per-spot 堆叠（≤5-6 类型） | §2.6 |
| **空间 CCC** | 空间箭头/向量场 + 配受体相邻面板 | 空转 CCC 最低证据=共定位；chord 在空转退潮 | 通讯分-距离曲线 | §3.7 |
| **scRNA+空转联合** | 三件套：scRNA UMAP + 同色系空间投影 + mapping score 图 | 只展示投影结果不做验证=审稿拒点 | 基因级验证散点 | §2.1+§2.6 |
| **TF/regulon 活性** | TF×cluster 活性 heatmap | 定位→UMAP 着色；定量比较→violin | 二值化 regulon heatmap | §2.5 |
| 多指标方法/整合基准对比（异量纲） | 雷达图（每辐条独立量程） | 指标>6 或系列>4 | 分面小柱图 | §3.31 |
| 消融/组件贡献对比 | 同色相 alpha 渐变 bar（完整=实） | 需指认每个基线时 | focus_ramp 焦点+渐褪柱 | §3.32 |
| **状态转移矩阵/命运概率流**（PAGA/CellRank/OT） | sankey 两阶段 alluvial（≥3 阶段拆面板） | 因果链叙事时换 PAGA 图 | plot_sankey | §3.41 |
| **CNV 推断结果**（区分恶性/非恶性、克隆） | inferCNV 式基因组热图（染色体分隔+分组色条） | — | — | §3.42 |
| **信号沿连续组织轴/距离**（zonation/病理共定位/边界带） | 梯度曲线+分位带（norm='each' 多基因比形状） | 单基因空间分布图换 feature plot | plot_axis_gradient | §3.43 |
| **克隆构成/扩增变化**（TCR/演化） | composition 堆叠柱（大小分类）；跨时点演化用 track 折线 | — | slope（组成 movers） | §3.44 |
| **RNA velocity 流向** | velocity embedding 箭头（scvelo 原生；n<3 万 cell-level，更大用 grid/stream 平均流） | 只看谱系方向 → PAGA+velocity 叠加 | streamplot | scvelo/pl.velocity_embedding |
| **Ripley/空间点过程**（K/L/F 函数） | K/L/F 曲线 + **理论 CSR 参考带（envelope）**——绝对值无意义，偏离带才有 | 多组比较 → 曲线分面；单统计量（如 L at r=50µm）→ 带 CI 横条 | 组内 randomization envelope | squidpy gr.ripley 直绘 |
| **in silico 扰动预测**（Arc State/CPA 输出） | 预测 vs 对照 **Δ 发散 heatmap（RdBu_r）+ 预测 DE volcano（caption 标 predicted）** | 多扰动并排 → 扰动×基因 diverging 矩阵；**必配 linear baseline 对比**（FM 铁律） | 与实测扰动散点（有 validation 时） | plot_heatmap/plot_volcano |
| **细胞周期评分/相位** | S vs G2M 散点按 phase 着色（象限图，标各象限 %） | 沿轨迹的相位动态 → phase 占比堆叠面积；per-cluster → 箱线 | — | plot_regplot(no-fit)/plot_stackarea |

### 0.2 数据形态 → 图型（底座层：§0.1 未命中或要在备选间挑时，按数据本身的结构选）

> §0.1 按"分析输出"路由；本表按**数据形态**（几个定性维 × 几个连续维 × 有无序/空间/配对结构）路由——同一数据往往有多条合法路径，本表给**最美观**的那条（美学依据 = 感知精度排序，见表后元规则 1）。全部条目映射到 cns_style 现有入口。

| 数据形态 | 最美观首选 | 何时换 | 入口 |
|---|---|---|---|
| 1 定性（2-5 组）× 1 连续 | violin+内箱线+供体点（分布形状与统计量同屏） | 大 n 拥挤→box+抖动点 | `plot_violin` / `plot_boxplot`+`plot_stripplot` |
| 1 定性（6-15 组）× 1 连续 | 紧凑 violin 矩阵 | 组间需精确比中位→box+点 | `plot_violin` |
| 1 定性（>15 组）× 1 连续 | 按值排序 Cleveland 点图（长条不如点阵可辨） | 需展示全分布→ridge | `plot_bardotplot` |
| **配对**（同供体两条件）× 连续 | paired slope（配对结构最能显差） | 对多→bump/ heatmap | `plot_slope` |
| 定性 × 连续 + 重复 | bar+供体点（**纯 bar 无点不合规**——重复是证据） | — | `plot_bar`/`plot_bardotplot` |
| 连续 × 连续（n<2000） | 散点+拟合+CI 带 | — | `plot_regplot` |
| 连续 × 连续（n 大，点海） | 密度（KDE/hex）——重叠散点不美观也不可读 | 需看离群点→对数轴+抽稀 | `plot_kde` |
| 连续 × 连续 + 分组（≤6） | 色分组散点（同屏比分面强） | >6 组→分面小倍数 | `plot_regplot`(hue) |
| 连续 × 连续 + 连续（第三维） | 散点+径编码（**径可辨 ≤3 档**，更多换分面） | 第三维是时间→动画/小倍数 | scatter(手写)/`plot_lr_bubble` |
| 矩阵（行×列，值可 z-score） | heatmap（行 z、白-色映射、按需聚类+dendro） | 列=基因行=类型看 marker→dotplot | `plot_heatmap` |
| 矩阵（类型 × 基因 marker） | dotplot（色=均值 径=%——两通道比热图单通道信息多） | 基因>40→top-N 分块 | `plot_dotplot` |
| 矩阵（值跨零，相关/Δ） | 发散色 heatmap 或 2D 统计量 dotplot | — | `plot_stats_dotplot`(group_col) |
| 构成 × 单时点（≤5 类） | 100% 堆叠柱 | 🚫 饼图>5 类（CNS 弃用） | `plot_cellproportion` |
| 构成 × 时间/阶段（连续） | 堆叠面积（流动感最强） | 离散时点→堆叠柱 | `plot_stackarea` |
| 构成 movers（首 vs 末） | slope（端点直标 Δ） | 类型>8→heatmap | `plot_slope` |
| 1 连续分布 × 单组 | KDE+rug（比直方平滑无 bin 争议） | 需计数→直方 | `plot_kde` / `plot_histplot` |
| 1 连续分布 × 多组（≤8） | ridge 山脊（并排密度最美） | >8→violin 矩阵 | `plot_ridge` / `plot_violin` |
| 多实体 × 1-2 统计量（排名/相关） | 统计量 dotplot（色=值 径=幅值；行按值排序） | 见 §0.1 行 72 | `plot_stats_dotplot` |
| 富集结果（通路 × 基因数/ratio） | 横条+gene-ratio 点（GO/KEGG 专属形态） | — | `plot_enrichment` |
| 有向关系 ≤8 类型 | chord（谁给谁收一图可读） | >8→network | `plot_chord` / `plot_ccc_network` |
| LR 对 × 细胞对/通路 | bubble（径=-log10p 色=强度） | — | `plot_lr_bubble` |
| 状态转移 ≥3 阶段 | sankey alluvial | 因果叙事→PAGA | `plot_sankey` / `plot_paga` |
| 空间坐标 × 定性 | categorical spatial（低饱和 20 色、白底） | — | `plot_spatial` |
| 空间坐标 × 连续 | spatial+colorbar（per-type 色标 p98） | 局部结构→zoom | `plot_spatial` / `plot_spatial_zoom` |
| 沿组织轴/距离 × 信号 | 梯度曲线+分位带（多基因各归一比形状） | 单基因→feature plot | `plot_axis_gradient` |
| 有序（伪时间/GA）× 连续 | 曲线+CI 带；多实体→小倍数 | 多时点多条件→heatmap | `plot_pseudotime` / `plot_trend_grid` |
| 集合交集 2-4 组 | Venn | >4 组→UpSet（Venn 不可读） | `plot_venn` / `plot_upset` |

**美观五元规则**（本表的"为什么"）：
1. **感知精度排序**（Cleveland & McGill）：共同尺度上的位置 > 长度 > 角度 > 面积 > 颜色——同一信息永远用更高精度通道：dot>bar>pie、slope>双柱、点径编码≤3 档。
2. **定性色 ≤26 类**（MORLANDI_EXTENDED 上限）；再多必须分面——图例超过一列就是失败的图例。
3. **小倍数优于图例过载**：>6 组同屏不如按组拆面（`plot_trend_grid` 范式）。
4. **数据墨水比**：删网格（或极浅灰）、删无信息刻度、图例无框、轴不加粗——留白是信息。
5. **一图一主张**：一张图讲一件事；第二个主张开新面板，不往同一 axes 里塞第二套编码。

### 图型域偏好（2026-10 空转顶刊频率校准——跨表通用约束）

> 依据：2026-04~10 顶刊 ST 13 篇逐篇 panel 盘点（原始档案 `/home/longyao/data/lit_surveys/202610_st_applications.md`）+ 506 篇库频率列。**决策表命中图型后，再过本层域检查**——域错配的图型再"好看"也换。

| 域 | 高频（首选池） | 禁/限用（域专属，不进空转机制页） |
|---|---|---|
| 空转/发育/机制叙事 | 空间散点图（类型/基因/模块/丰度）·UMAP↔空间双视图 ·H&E 并排+zoom inset ·dotplot（marker/LR/通路/**统计量 dotplot §3.46**）·heatmap（模块×条件/组成/regulon）·轴/距离梯度曲线+分位带 ·箱线/小提琴+供体点（case-control+CI）·邻域/共定位矩阵 ·LR bubble ·拟时序投影回空间 ·时空矩阵（样本×阶段）·schematic 模型图 | **棒棒糖**（0/13，仅用户点名/双统计量+零带场景）·**森林图**（0/13，临床 meta 专用）·雷达图（方法对比专用）·云雨图（可读性差于箱线+抖动点，降级） |
| 临床/转化叙事（C1/C2 域、临床队列收尾） | KM/ROC/森林图（效应量+CI）·oncoprint ·fishplot | —（本域内 forest 合法且标准） |
| 方法学/基准叙事 | 雷达 ·消融渐变 bar ·基准散点+null 带 | — |

**路由铁律**：`figure-production` 出图时若命中"多实体单统计量"→ 一律 `plot_stats_dotplot`（§3.46）；棒棒糖/森林图需要**显式理由**（域匹配或用户点名）才可画，否则视为路由错误。
（域铁律属护栏——图型域错配（临床形态进空转机制页）是审稿级错误；在此之外，决策表是指南非剧本：命中即采、不中就推理，偏离写理由即可——见 `guards_vs_guides.md` §3。）

### 证据等级（每个生物学结论至少配一张定量图）

| 等级 | 图型 | 角色 | 2026 趋势 |
|---|---|---|---|
| **地图图** | UMAP/tSNE/空间着色 | 索引/定位——"在哪里" | ↓ 降权：不作注释证据，不论证轨迹 |
| **模式图** | heatmap/streamplot/PAGA/dotplot | 结构/模式——"有什么" | ↑ 升权：heatmap（带注释条）成为注释证据首选 |
| **定量图** | 曲线/散点+统计/violin/箱线 | 证据——"差多少" | 硬性要求：有重复时必须带样本级点+检验 |

> **纪律**：一个结论如果只有地图图（如"UMAP 上某群分开了"）没有定量图支撑，审稿会被质疑。至少补一张定量图。

### 反模式黑名单（以下组合会被审稿质疑）

| ❌ 反模式 | 为什么错 | 正确做法 |
|---|---|---|
| UMAP 形状论证轨迹方向 | UMAP 距离/形状不可解释（Chari & Pachter 2023） | PAGA/gene-along-pseudotime 曲线 |
| 无重复的堆叠柱做条件比较 | 无统计效力，无法排除抽样偏差 | 带样本级点的分组图+检验 |
| per-cell Wilcoxon 的 DE 画 volcano | 假阳性膨胀 | pseudobulk DE → volcano |
| >6 细胞类型的 per-spot pie | 视觉不可读 | 每类型一张比例空间散点图 |
| 空转 CCC 无共定位证据 | 纯数据库打分正在退潮 | 配空间箭头或配受体相邻面板 |
| 只有投影结果无 mapping score | 无法评估 label transfer 质量 | 三件套（UMAP+投影+mapping score） |
| dotplot 做唯一注释证据 | dotplot 夸大特异性偏倚 | 关键结论配 heatmap 交叉验证 |

---

## 0.5 两条调用路径（重要）

cns_style 包同时支持两层，所有图型默认 ov.pl 优先：

1. **omicverse 层（默认）**：`ov.pl.*` 一行调用（embedding/volcano/dotplot/violin/plot_spatial/trajectory_overlay/CellChatViz）。自动 omicverse 风格，接受 ax 可与 cns_style 组合。
2. **Universal 兜底层**：纯 matplotlib/seaborn/scapy。ov 不支持该图型、或需精细控制时用。cns_style 的 polish_axes/clean_umap_axes/finalize_figure 对两层都适用。

**配色两层并存**：
- 默认 Morlandi Nord（MORLANDI / MORLANDI_EXTENDED）+ CONDITION_COLORS，跨论文锁 manifest.yaml。
- 可选 ForbiddenCity 命名色板（`ForbiddenCityBridge` / `palette_from_names`），用于高颜值/人文风格场景（图形摘要、综述图）。omicverse 装了走精确色，没装走 fallback 近似色。

---

## 1. 全局设定（每个绘图脚本第一行）

每个脚本开头 3 行固定模板（import cns_style + `set_cns_style_journal('nature')`）见 `plotting_reference.md §1`。

作用：自动设好 Morlandi 配色 / Arial 字体 / modular scale 字号(7/8/10/12/14) / L-frame axes / outward ticks / 300-600 DPI / PDF 输出。

---

## 2. 配色（含 2026-10 CNS 原图实测 colormap 约定）

**Colormap 约定**（常量在 `cns_style._constants`，实测来源=2026 年 11 张 Nature/Cell 主图）：
- Sequential 表达量/伪时间：首选 `viridis`（`SEQ_PRIMARY`）；dotplot 表达量用深红渐变（`DOT_SEQ`）；绿系（dark-green→yellow）为备选
- Diverging（相关/logFC/GSEA）：`RdBu_r` 对称 `vcenter=0`；🚫 jet/rainbow 零出现
- 定性色：中低饱和策展色；**簇数>12 自动降饱和**（MORLANDI→MORLANDI_EXTENDED）；单 panel ≤26 类
- **灰 = 语义色**（`GREY_NS`）：unassigned/纤维化/非显著——MA/volcano 非显著点一律压浅灰、显著点彩色（灰+高亮二分是 CNS 标配）

**Morlandi Nord**（离散/categorical）：8 色（冰蓝 #88C0D0 起，含珊瑚红/草绿/陶土/紫/金黄/北欧蓝/灰蓝），见 cns_style 包（_constants.py）的 `MORLANDI` / `MORLANDI_EXTENDED`。
**连续表达**（heatmap/feature）：`EXPR_CMAP`（蓝→麦→暗红）；**Diverging**（log2FC）：`DIVERGING_CMAP`（蓝→白→红，0=白）

**好 vs 坏配色**：

| ❌ 坏 | ✅ 好 |
|---|---|
| `tab20`（高饱和霓虹，学生作业感） | Morlandi + 色温叙事：焦点=原色（Fibroblast 珊瑚红、Macrophage 北欧蓝），配角=原色（T_cell 草绿、B_cell 紫），非焦点=灰（Endothelial/Epithelial 同灰） |
| `jet`（感知不均匀，Nature 明确反对） | EXPR_CMAP / DIVERGING_CMAP |

**可选 ForbiddenCity 命名色板**：`ForbiddenCityBridge` + `palette_from_names(celltypes, color_names)` 按名字取色（如 'cinnabar'/'porcelain'），不依赖具体 hex；用于图形摘要/综述等人文风格场景，omicverse 已装走精确色，未装走 fallback 近似色。示范见 `plotting_reference.md §2.4/§3.5`。

---

## 3. 排版

| 元素 | 字号 | 颜色 | 备注 |
|---|---|---|---|
| Tick labels | 7-8pt | #2E3440 | |
| Axis labels | 10pt | #2E3440 | labelpad=10 |
| Title | 12pt | #2E3440 | pad=8 |
| Panel label (A/B/C) | 12pt bold | #2E3440 | offset (-0.12, 1.08) |
| In-figure annotation | 7pt | #4C566A | gene names italic |
| Legend | 7-8pt | #2E3440 | frameon=False |

- 字号只用 7/8/10/12/14；期刊 preset（6/7/8）覆盖此规则
- 多行 title: linespacing=1.4；文字颜色 #2E3440（不用纯黑 #000000）

---

## 4. 轴与留白

三个函数（签名见 cns_style 包 _axes.py docstring）：`polish_axes(ax)` — L-frame + outward ticks + alpha=0.15 参考线（非 UMAP）；`clean_umap_axes(ax)` — 去所有轴/ticks，只留 "UMAP1/2"（UMAP/tSNE 专用）；`optical_margin(ax, 0.12)` — 圆形数据多留 12% 呼吸空间。

- 锚点 panel 占总面积 40-50%（`width_ratios=[1.8, 1, 1]`）；逻辑相关 panel 间距 < 逻辑分组间距
- savefig: `bbox_inches='tight', pad_inches=0.1`
- **大 cohort 数据用 `cohort_params(n_cells)` 联动调 size/alpha/figsize，不要只调 size**（会糊成色块）

---

## 5. 图型视觉规格（每种图的关键参数，不放完整代码）

### 5.1 UMAP/tSNE — omicverse 风格
- **优先用 `ov.pl.embedding()`**（自动应用 omicverse 5 签名：`frameon='small'` / grid off / `legend_fontweight='bold'` / mini colorbar / cluster names on plot）
- omicverse 默认：`legend_loc='right margin'`, `na_color='lightgray'`, `edges=False`
- 手动 sc.pl.umap 时 size 分档：<10k→8, 10-50k→3, 50-200k→1, >200k→0.3（或用 `cohort_params(n_cells)`）；`alpha=0.7, edgecolor='none'`
- On-plot labels: `add_cluster_labels()`（白色光晕，median 定位）或 scanpy `legend_loc='on data'`
- 轴风格二选一：`frameon='small'`（L 型小轴）或 `clean_umap_axes()`（Nature 无轴）；`optical_margin(ax, 0.12)`
- → 代码模板见 plotting_reference.md §2.1/§3.4

### 5.2 Volcano — omicverse 风格
- **优先用 `ov.pl.volcano()`**（自动配色 + top-10 标注 + legend 下方）；手动时对齐默认色：Up=`#e25d5d`, Down=`#7388c1`, NS=`#d7d7d7`
- figsize: **(4, 3.5)**（与 `recipe_figsize('volcano')` 一致）；阈值线 `ls='--', lw=0.5, alpha=0.3`
- Gene labels: **top 10**（不是 5），fontsize=10，italic；Legend **图下方**（`bbox_to_anchor=(0.8, -0.2), ncol=2, fontsize=12`）
- Title: weight='normal'（不 bold），size=14；`polish_axes(ax)`
- → 代码模板见 plotting_reference.md §2.2

### 5.3 Dotplot — omicverse 风格
- **优先用 `ov.pl.dotplot()`**（自动标准：colorbar_title='Mean expression in group', size_title='Fraction of cells in group (%)'）
- `num_categories=7`（>7 类自动分组）；`standard_scale='var'`（行标准化）
- cmap=EXPR_CMAP 或 'Reds'；`edge_color='#2E3440', edge_lw=0.3`；`dendrogram=False`（列按生物学排序）；统一 vmin/vmax across genes
- → 代码模板见 plotting_reference.md §2.3

### 5.4 Violin/Box (gene expression per cluster) — omicverse 风格
- **交替背景色带**（omicverse 标志性特征）：white + group_color 淡化 80%（`_lighten_color(color, 0.8)`）；Violin fill **α=0.8**，edge 同色 lw=1
- Spine 颜色: **#b4aea9**（暖灰，不是纯黑）；**水平 grid lines: True**（`alpha=0.3, lw=0.5`）
- Box overlay: **默认不加**（`show_boxplot=False`）；需要时 widths=0.15；Individual points: **s=1**, α=0.4, jitter
- 统计检验: 内置（`statistical_tests='wilcox'`）或手动 `add_significance_bracket()`；Y 轴 log-normalized expression
- X 轴: cluster names（≤12 rotation=0；>12 rotation=45）；多基因每基因一行 subplot（共享 x 轴），figsize=(n_clusters×0.6+1, n_genes×2.8)
- → 代码模板见 plotting_reference.md §2.4

### 5.5 Heatmap — omicverse/scanpy 风格
- omicverse 无独立 heatmap 函数——用 `sc.pl.heatmap()` 或 `seaborn.clustermap()`
- Z-score per row, `vmin=-2, vmax=2`；cmap=EXPR_CMAP 或 'RdBu_r'
- row-clustered, **column-fixed by biology**（列按生物学排序，不画列 dendrogram——2024 顶刊趋势）
- 白线分隔 groups: `linewidths=0.5, linecolor='white'`；Gene names italic；`add_elegant_colorbar(label='Scaled expression')`
- 列注释条（condition/celltype/batch）：高 0.1 inch/条，色来自 manifest；注释条与热图间留 0.5pt 白缝
- → 代码模板见 plotting_reference.md §2.5

### 5.6 Spatial — omicverse 风格（2026-10 CNS 原图校准）
- **优先用 `ov.pl.plot_spatial()`**（自动处理 tissue + spots + colorbar）；手动时 Tissue `alpha_img=1.0`（不透明！不是 0.4），spots `alpha=0.85`（CNS 实测近不透明、单图层可 1.0），**点径=图幅短边 0.8-1.2%**（Visium SD）/ 0.3-0.5%（HD）/ bin 级呈连续 painted 面；**`edgecolors='none'`（实测零描边）**
- **Scale bar 必须有**（缺它审稿人立刻扣分）；长度取 100/200/500µm 中最接近图宽 1/5 者；`add_scale_bar(color=None)` **默认按背景自适应**（白底图=黑条黑字〔胎心 Fig2 实测〕，组织/H&E 深底=白条〔胚胎 Fig1〕）；横条+外侧数值文字，右下/左下角
- **背景白底**（2026 实测全部 Nature 空间主图白底；黑底仅限真实 IF/H&E 影像）；无坐标轴、无 A/P 罗盘（解剖方位用 6pt 小字贴组织旁）
- Colorbar 横置于图下方（`orientation='horizontal', fraction=0.046, pad=0.08`）；一基因一 panel；shared vmin/vmax (99th percentile clip)
- omicverse spatial 默认：`frameon='small'`, `colorbar_loc='right'`
- → 代码模板见 plotting_reference.md §2.6

### 5.7 Bar (proportions) / cellproportion
- 95% CI error bars (capsize=3, lw=1)；Per-sample dots overlay (s=15, α=0.7)；Y-axis starts at 0
- cellproportion 图（堆叠比例）同样 y 从 0 起、按组别分组、色锁 manifest
- → 代码模板见 plotting_reference.md §2.7/§3.5

### 5.8 Enrichment Bar (GO/KEGG)
- **水平条形**，按 -log10(FDR) 降序排列（top 在最上）；条色 = -log10(FDR) 映射（单暖色 `#BF616A` 或 EXPR_CMAP）
- x 轴: "-log₁₀(FDR)"；条右端标 gene count（`fontsize=6, color=GREY`）；Top 10-15 条；通路名 ≤40 字符截断（`textwrap.shorten`）
- figsize: (4.5, 0.35×n_terms + 1)；`polish_axes(ax)`；无 grid
- → 代码模板见 plotting_reference.md §2.8

### 5.9 L-R Bubble Plot (pathway × cell-type pair)
- x = cell-type pair (sender→receiver)；y = pathway；size = -log10(p-value) → `s ∈ [20, 200]`；color = mean expression（EXPR_CMAP）
- ≤10 pairs × ≤15 pathways；pair 标签 `rotation=45, ha='right', fontsize=6`
- `add_elegant_colorbar(label='Mean expression')` + `polish_axes(ax, subtle_grid=False)`
- → 代码模板见 plotting_reference.md §2.9

### 5.10 Feature Plot Matrix (多基因 UMAP)
- `ncols=3`（`ncols=min(3, n_genes)`）；每 panel (3, 3)
- 所有 panel 共享 `vmin=0, vmax=99th_percentile`（跨基因可比）；基因名斜体作 title（`fontstyle='italic', fontsize=10, pad=4`）
- 矩阵级单 colorbar（仅当基因同量纲）或 per-panel mini colorbar；`clean_umap_axes(ax)` on all panels
- → 代码模板见 plotting_reference.md §2.10

### 5.11 PAGA 与 Pseudotime（轨迹分析）
- **PAGA**：`sc.tl.paga()` 前置计算 + `sc.pl.paga(colors=...)`（注意 **colors 是复数参数**，传 celltype 列表）；边阈值 `threshold=0.05` 滤噪声；可与 UMAP 叠加（paga 图投影到 UMAP 布局）
- **Pseudotime**：Gene-along-pseudotime 用 LOESS 平滑线 `lw=1.2` + 95% CI 带 `alpha=0.15`；**分支拓扑 → 绝不用单线性曲线**（多分支用分面或树状叠加）
- 图尺寸：PAGA (3.5×3) + pseudotime UMAP (4.5×4)
- → 代码模板见 plotting_reference.md §3.1/§3.3

### 5.12 Chord/CCC（细胞通讯）
- **≤8 cell types**（再多和弦图不可读）；lw ∝ interaction strength；source-colored α=0.5
- figsize=(5,5) square；omicverse 走 `CellChatViz` → `netVisual_chord_cell`（自动配色 + 布局）
- → 代码模板见 plotting_reference.md §3.2

### 5.13 Radar（多尺度方法对比）
- **≤3 系列最佳**，>4 会糊（fill α=0.06 叠加后难以分辨）
- 异量纲指标 **axis_ranges 必须显式传**（如 GraphConn 0-100 与 0-1 混排；缺省按各轴数据 min/max 归一 → 压扁大范围轴）
- 顶点 scatter 标出真实数据点（s=6）；每辐条外侧只标该轴 max 数值（原始单位，沿辐条旋转）
- 外环 NEAR_BLACK lw=0.6 / 辐条 GREY lw=0.4（grid off 后手绘补回）；spoke 标签按 |sin| 加 offset 防挤
- figsize 默认 (3.2, 3.2)；legend 右外置（铁律 1）
- → 代码模板见 plotting_reference.md §3.31（plot_radar）

---

## 6. 拼图规则

- 输入 = 已独立渲染+验证的 PDF/PNG（不是 live axes）
- Panel labels: 12pt bold, top-left；wspace=0.35, hspace=0.45
- 共享 colorbar 合并（同 scale 不重复）
- 某张比例不对 → 回去重画那张，不在拼图时缩放

---

## 7. 报告级

- 整篇顺序：查 `references/figure_templates.md`（五段式骨架：定场→展开→空间转折→机制→收尾 + 期刊格式裁剪）；Fig1 = atlas (2-3 panels) → 中间 = mechanism (4-6) → 最后 = validation (2-3)
- 全论文锁 `manifest.yaml`（cell_type_colors / condition_colors / cmap）
- 同一 cell type 全论文同色；同一 gene 全论文同 colorbar range

---

## 8. Ugly → Beautiful 速记

| ❌ 丑 | ✅ 美 |
|---|---|
| 默认 matplotlib 调色板 | Morlandi Nord |
| s=15 for 100k cells (blob) | s=1 (texture) |
| 4 个 spine + ticks + grey bg | L-frame / 去轴 (UMAP) |
| 外部 legend 15 entries | On-plot labels |
| 所有 cluster 同等饱和 | 焦点饱和 + 其余 grey |
| 纯黑 #000 | #2E3440 |
| 默认 fat colorbar with border | slim, no border, 3 ticks |
| 字号随意 (9pt, 11pt) | Modular scale 7/8/10/12/14 |
| 一边画一边拼 | 逐张独立出图验证后再拼 |

---

## 9. 统计标注规则（p-value bracket / star）

**规则**：
- Star 定义写在 legend：`*P<0.05, **P<0.01, ***P<0.001, ****P<0.0001`；优先报 exact P（`P=3.2×10⁻⁵`），star 是辅助
- bracket 线 `lw=0.8, color='#2E3440'`（不用纯黑）；多组比较时 bracket 高度错开（每层 +0.1），避免交叉
- `ns` 也标出来（不显著也是信息）
- 调用 `add_significance_bracket(ax, x1, x2, pval, y=None, height_frac=0.03)`：y 不传时自动定位（数据最大值上方 2%），多组自动错开高度
- 代码见 plotting_reference.md §4

---

## 10. Layout 三铁律（legend / 文字 / 比例）

### 铁律 1: Legend 永远在右侧外置

唯一正确放置：`frameon=False, fontsize=7, bbox_to_anchor=(1.02, 0.5), loc='center left', borderaxespad=0`（右侧外置，垂直居中）。太长（>8 entries）用 ncol=2 或缩小到 6pt；右侧被截 → figsize 宽度 +1 inch 或 wspace 加大。

**反例**（legend 会盖在数据上）：❌ `loc='best'`（matplotlib 的 'best' 经常盖数据）；❌ 图内 legend + 边框（视觉噪音）。

**例外**：UMAP 用 on-plot labels 代替 legend（见 §5.1）。savefig 前用 `finalize_figure(fig)` 自动检查并右移 legend。

### 铁律 2: 文字不重叠

每张图 savefig 前统一走 `finalize_figure(fig)`：自动检测 title/label/annotation 的 bbox 两两交叉；>50k 点未 rasterize 警告；legend 覆盖数据自动移到右侧。

**如果仍有重叠**（finalize_figure 会 warn）：加大 `figsize` 高度（不是缩小字号）；缩短 title 文字（不是让它挤在一起）；减少 panel 数（不是硬塞）。

### 铁律 3: 比例不畸形

| 图型 | 宽高比 | 取值 |
|---|---|---|
| UMAP/tSNE | 正方形（1:1） | `recipe_figsize('umap')` → (4.5, 4.5) |
| Spatial tissue | 匹配组织形状 | figsize 按 H&E 的 W/H 比例设 |
| Heatmap | cell 接近正方形 | figsize 配合 `ax.set_aspect('auto')` |
| Volcano | 4:3.5 | `recipe_figsize('volcano')` |
| Bar/Violin | 宽度随组数增长 | `recipe_figsize('bar', n_x=N)` |

反例：UMAP 被拉成椭圆（如 figsize=(6,3) 太扁）→ 用 `recipe_figsize('umap')` 保证正方形。

---

## 11. 实战教训（从真实 PPT 迭代中提炼）

> 以下教训来自一次 16-slide 瓣膜发育 PPT 的完整迭代过程（11 张脚本、15 张图、多轮返工）。每条都是真实踩过的坑。

### 11.1 空间散点图（spatial scatter）的 7 个陷阱

| # | 陷阱 | 表现 | 解决 |
|---|---|---|---|
| 1 | **niche bins 太少被背景淹没** | 13w 仅 687/41923 bins，niche 散点几乎不可见 | niche 点 s≥12 + 背景减到 ≤30000 subsample + alpha 0.15 |
| 2 | **细长 niche 的 bbox 计算错误** | niche 19850×9150px，buffer=max(W,H)*0.25=4962 → bbox 太大 | buffer=`min(W,H)*0.15`（用短边，更紧凑） |
| 3 | **全切片散点 s 太大糊成色块** | 483646 bins × s=1 → 点重叠 | s=0.3-0.5（>20 万 bins）；niche 放大图 s=8-15 |
| 4 | **convex hull 轮廓遮挡数据** | 在散点上画黑色多边形 → 用户反感 | 不要主动画 hull；如需标 niche 用文字注释或 inset |
| 5 | **多 panel 统一 colorscale** | 三时点各自 vmax → 不可比 | `vmax = max(三时点 p95)`，共享 |
| 6 | **scale bar 缺失** | 审稿人一眼扣分 | `add_scale_bar()` 必须有；坐标→μm 换算需平台元数据 |
| 7 | **24w niche 细长导致 panel "空"** | niche 占 panel 面积 <5% | 放大到 niche bbox（不是全切片）；或改为梯度曲线 |

### 11.2 dotplot 的 4 个陷阱

| # | 陷阱 | 解决 |
|---|---|---|
| 1 | **点太大**（s=420 for frac=100%）→ 重叠 | `s = 8 + frac/100 * 100`（max s=108，不是 420） |
| 2 | **26 类×26 基因糊成一团** | 行/列分组（按 lineage 排序）+ 分隔线 |
| 3 | **legend 挤压数据区** | finalize_figure 自动移 legend → 预先放好（底部/右侧外置） |
| 4 | **行名/列名消失** | set_yticklabels 后检查渲染（finalize_figure 可能移位） |

### 11.3 火山图 → 分组散点图的替代决策

**教训**：火山图在 niche DE / 多时点 / 多组间比较场景经常**丑且不可读**——基因标注重叠、灰点密集、关键基因挤在 FDR 地板；多组比较时火山图无法并列展示。

**替代方案**：**分组散点图**（y=logFC，x=各时点/组别，每点=一个基因）：

> 代码模板：plotting_reference.md §3.6（统一入口 plot_de_scatter）；需精细控制时见该文件 Example 2 手动实现。

**优势**：多时点/多组直接可比；无标注重叠；显著 vs ns 用颜色+大小区分；每个组别的 DE 分布一目了然。

### 11.4 UMAP 双层次注释的陷阱

| 陷阱 | 解决 |
|---|---|
| 26 亚型 on-plot labels 互相遮挡 | 只标 n>2000 的主要亚型 + VIC 焦点；其余靠颜色 |
| labels 被散点挡住 | `zorder=12` + `path_effects=[withStroke(linewidth=3, foreground='white')]` |
| 同色系深浅区分度差 | 用**不同色相**而非微调深浅（CM 蓝 vs EC 青是完全不同色相） |
| 外置图例 26 行太挤 | 按大类分组（5 个 header + 子条目），fontsize=5.5 |

### 11.5 颜色编码的纪律

- **不要在散点上画圈/轮廓**——用户普遍反感（除非主动要求）
- **VIC/焦点色用最饱和**（#E64B35 亮珊瑚），非焦点用同系浅色或灰
- **三时点对比用 alpha 渐变**（0.5→0.75→1.0），不用完全不同颜色
- **显著=彩色，ns=灰**（不要给 ns 也上色）

### 11.6 finalize_figure 的自动干预

`finalize_figure(fig)` 会自动移动重叠的 legend——但有时把 legend 移到意外位置导致 panel 被挤压。

**对策**：
- 画图前预先规划 legend 位置（`bbox_to_anchor` 底部或右外置）
- 跑完后检查 finalize 的 warning（"Legend moved to outside-right"）
- 如果 Panel B 因为 legend 移位变空 → 去掉 Panel B（信息冗余时）或把 legend 放 Panel A 内

### 11.7 figures4papers 移植技巧（Nature MI/ICML/NeurIPS 图库提炼）

> 从 figures4papers 图库（Nature MI 社群的 ICML/NeurIPS 论文图脚本）移植配色/标注技巧到 cns_style 的实践沉淀；对应实现见 plotting_reference §3.32/§3.33 与 cns_style 的 `alpha_ramp`/`focus_ramp`/`mark_events`/`is_dark`。

- **大画布 vs 实物尺寸**：源库用 24-52 英寸大画布 + 24-54pt 字号、再在 LaTeX 里缩小——**我们不用**，cns_style 坚持实物尺寸（2.5-3.5 英寸）+ 7-8pt 直接出图；只移植技巧，不移植画布哲学
- **alpha 编码信息**：消融完整度用同一色相透明度表达（`alpha_ramp`），比多色更聚焦——读者一眼看"完整性梯度"，不用猜色块归属
- **焦点+渐褪 ramp**：比"其余全灰"好在基线仍可在图例中指认（`focus_ramp`）
- **数值标签位置**：压色块上 → `is_dark()` 选字色（白/黑字）；色块外 → 一律 NEAR_BLACK（白字白底不可见的真实踩坑）
- **事件标注防撞梯**：label 中 `'*'` 计数抬高文字（`mark_events`），多事件叠标不用手工逐条调 y
- **hatch+白描边**：黑白打印/色盲友好的双序列区分（fill_between hatch 后叠同形状白描边擦边框）
- **图例可独占一个 subplot**：多指标小倍数图共享颜色时 `ax.legend(handles, ...)` + `ax.set_axis_off()`，图例自占一格不挤数据区

---

## 12. 指针（收尾）

- 代码模板 → `plotting_reference.md`（本文件所有 §5.X / §9 的代码实现都在那里）
- 外部 omicverse-skills 参考 → `omicverse_skills_examples.md`
- cns_style 包函数 → 见 tool_registry.md 与包内各模块 docstring（plot_* 统一入口导出见 scripts/cns_style/__init__.py；含 save_panel / assert_anndata_keys / cohort_params / plot_umap / plot_volcano / ...）
- 流程（先定框架再迭代） → `skills/visualization/figure-production/SKILL.md`

### 12.1 组合体增补（B8-B9，已并入 dispatch_cheatsheet B 系；权威细节在 `references/bigfig_deck_playbook.md`）

单图质量由 B1-B7 + finalize_figure 兜底；**组合体（大 fig / 多面板 deck）的系统性
失败在 B 系之外**。B8/B9 的完整条目见 `references/dispatch_cheatsheet.md`（编号以
cheatsheet 为唯一源），绘图时额外硬约束（B8/B9）：

- **[B8] 画布级文字重叠断言**：finalize_figure 只查 ax.texts；`ax.title`、刻度标签、
  图例必须在脚本里另做 pairwise bbox 断言；字号最后设定——`ax.tick_params(labelsize=...)`
  会静默覆盖 `set_yticklabels(fontsize=...)` | 漏 = 渲染放大后逐层返工
- **[B9] 版面字面量防截断**：加构/裁剪/缩放后必须断言"全部文本 artist 在画布内"
  （tight bbox 会把越界文本包进 PNG，反而把图撑宽失真）；窄轴放不下 N 个刻度名时，
  用数字刻度+键并入脚注 | 漏 = 图在组合体里被裁/变形
- 组合体总管线/缓存/渲染/像素门 → `bigfig_deck_playbook.md`（E1-E6）；显著性口径 →
  `references/analysis/stats_convention.md`