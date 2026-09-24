# Figure Templates — 单细胞/空转主图组织顺序模板库（领域×故事类型自动路由）

> **证据基础**：2024-2026 年 15 个医学生物学领域 **506 篇** CNS 及大子刊单细胞/空转论文
> （其中 **203 篇**提取到完整 Fig1-FigN 原文结构，即 §3 各卡"Y 结构"之和；另约 12 篇
> 完整结构论文未单列成卡）。原始调研档案：`D:\workspace\lit_survey\01-15_*.md`（每篇含期刊/年份/PMID/平台/figure 标题，未获取处如实标注，无编造）。
> **谁读**：story_builder Step 4（因果链→Figure 映射）、figure-production Step 1（大框架 panel 列表）、research-planner（设计预读——故事需要几组数据、什么验证）。
> **怎么用**：§0 两步路由（领域→领域卡，故事类型→研究型模板）→ 叠加 §1 通用骨架 → §4 期刊格式裁剪。**模板是起点的默认值，不是铁律**——数据强度永远优先（story_builder 核心原则）。

---

## §0 自动路由表

**第一步：领域命中 → §3 领域卡**（拿到领域坐标轴、特色 panel、收尾惯例）

| 用户数据/组织关键词 | 领域卡 | 领域空间轴惯例 | 标志性特色 panel |
|---|---|---|---|
| 肿瘤/cancer/TME/癌/胶质瘤/转移 | C1 实体肿瘤 | 肿瘤边界带/界面梯度（core-edge、DCIS-IDC） | 边界带梯度、TLS 解剖、CNV 热图、克隆 Voronoi |
| 白血病/淋巴瘤/骨髓/造血/白血病 MRD | C2 血液 | 骨髓/淋巴结 microenvironment | 克隆树+fishplot+oncoprint 组合拳、MRD/ROC 收尾 |
| 免疫/自免/炎症/T 细胞/耗竭/狼疮/IBD 免疫 | C3 免疫 | 淋巴组织生态位/组织-外周配对 | TCR 克隆-表型-空间三连图、药物干预收尾 |
| 脑/神经/AD/帕金森/脊髓/皮层 | C4 神经 | 皮层层状/脑区解剖 | 病理-分子距离梯度、层状分布图、GWAS 收尾 |
| 心/心脏/心梗/心衰/动脉/瓣膜 | C5 心血管 | 梗死分区 BZ/IZ/RZ、心室壁分层 | BZ 基因评分空间图、鼠→人镜像、体内验证链 |
| 胚胎/发育/胎儿/类器官/器官发生 | C6 发育 | 时间轴×空间轴必占前两图 | 3D 重建、形态发生波前、时空对齐 |
| 肝/脂肪/胰岛/糖尿病/肥胖/MASLD | C7 代谢 | 肝 zonation（门脉-中央静脉）、depot 对比 | 分区梯度曲线、LAM 明星亚群专图 |
| 肺/肺纤维化/COPD/哮喘/气道 | C8 呼吸肺 | 近端-远端气道轴 | 成纤维灶邻域、示踪时间窗 schematic |
| 肠/胃/肝/胰/IBD/肝硬化 | C9 消化肝胆胰 | 隐窝-绒毛轴、肝小叶分区 | 谱系示踪+Voronoi 克隆、平台验证链 |
| 肾/AKI/CKD/纤维化肾/移植 | C10 肾脏 | 肾单位节段、皮质-髓质轴 | PT 状态转换专图、FME 预后评分 |
| 皮肤/伤口/银屑病/皮炎/毛囊 | C11 皮肤 | 表皮基底层-颗粒层分化轴 | DEJ/毛囊锚定结构、鼠-犬-人跨物种 |
| 骨/肌肉/关节/软骨/OA/肌腱 | C12 骨肌 | 承重区 vs 非承重区、损伤-再生时序 | 分区取样示意、力学负荷变量 |
| 衰老/aging/senescence/长寿 | C13 衰老 | 年龄梯度（非线性） | correlation-with-age、senolytic 干预收尾 |
| 感染/脓毒症/COVID/病原/宿主-微生物 | C14 感染 | 感染时间线、病原载量轴 | 宿主-病原共检测空间图、跨物种签名回映射 |
| 胎盘/内膜/卵巢/睾丸/着床/妊娠 | C15 生殖母胎 | 孕周/月经周期时序、母胎界面距离 | 界面距离分箱、SNP 母/胎拆分 |

**第二步：故事类型（最强发现是什么）→ §2 研究型模板**

| 最强发现 | 模板 | 
|---|---|
| 前所未有的图谱/资源 | T1 图谱资源型 |
| 清晰因果链（X 驱动 Y） | T2 机制驱动型 |
| 克隆/谱系/演化 | T3 谱系演化型 |
| 能预测临床结局 | T4 临床预测型 |
| 新算法/新平台 | T5 方法型 |
| 时空动态过程 | T6 时序过程型 |

---

## §1 通用主图骨架（跨 15 领域 ≈100% 论文遵守的排序定律）

**五段式叙事**（来自 203 篇完整结构论文的频数统计）：

| 段位 | 位置 | 内容 | 出现率 | 高频图型（cns_style 入口） |
|---|---|---|---|---|
| **① 定场** | Fig1（100%） | 研究设计 schematic + 队列/时间线 + 图谱总览 UMAP/空间全景 + 组成图；**领域坐标轴在此亮相**（年龄分布/感染时间线/分区取样/时序轴） | 15/15 领域 | `plot_umap` / `plot_bar` / `plot_cellproportion` / `plot_qc_cards`（QC 下沉 supplement） |
| **② 展开** | Fig2-N（中段） | 分谱系/compartment **逐图推进**（T/NK→B→髓系→内皮；CM/EC/FB/MP；PT/TAL/CD……每图一个谱系）；或聚焦明星亚群 | 15/15 | `plot_dotplot` / `plot_heatmap` / `plot_violin` / `plot_ridge` |
| **③ 空间转折** | Fig3-6 | 空转固定做"第二幕转折"：scRNA 发现 → 空间定位/共定位/梯度验证。**通信图惯例放 Fig5-7 而非开头** | 13/15 | `plot_spatial` / `plot_spatial_zoom` / `plot_nhood_enrichment` / `plot_colocalization` / `plot_distance_distribution` / `plot_ccc` / `plot_lr_bubble` / `plot_axis_gradient`（新增） |
| **④ 机制** | 中后段 | 轨迹/调控（SCENIC/velocity）、状态转换、扰动 | ~80% | `plot_paga` / `plot_pseudotime` / `plot_sankey`（新增）/ `plot_de_scatter` / `plot_volcano` |
| **⑤ 收尾** | 末 1-2 图（三选一或组合） | **a)** 临床转化（KM/ROC/预后评分）→ `plot_forest` / ov.pl.kaplan_meier；**b)** 机制模型 schematic/graphical abstract → `scientific-schematics`；**c)** 湿实验功能验证（KO/药物/拯救/类器官）→ 实验图，无 cns_style 入口 | 15/15 | 领域偏好见 §3 各卡"收尾惯例" |

**三条排序铁律**（203 篇中违反者罕见）：
1. **先"谁在哪"再"谁跟谁说话"**：空间定位图在通信图之前。
2. **每张主图只讲一个机制/谱系**（story_builder §3b.3 同款规则，本次数据再确认）。
3. **湿实验/独立队列验证永远在最后**，不插中间打断叙事。

---

## §2 六种研究类型模板（按最强发现选择）

| 模板 | 适用 | 标准 fig 序列 | 领域代表 |
|---|---|---|---|
| **T1 图谱资源型** | 大规模多供体/多组织 atlas | Fig1 设计+全景 → Fig2 图谱注释/QC 亮点 → Fig3-5 逐 compartment 深挖 → Fig6-7 跨状态/疾病比较 + 资源门户/工具 | 心脏/肺/脑图谱、跨癌 CAF |
| **T2 机制驱动型** | 清晰因果链 | Fig1 设计+图谱 → Fig2 现象（差异亚群） → Fig3-4 机制（轨迹/调控/通讯） → Fig5 空间验证 → Fig6 功能验证/模型 | 心衰 IL-1β、IFNIC |
| **T3 谱系演化型** | 克隆/演化/转移 | Fig1 平台/模型 → Fig2 克隆或空间社区检测 → Fig3 克隆-微环境耦合 → Fig4 选择压力/状态转换 → Fig5 转移级联/验证 | AML 演化、肠癌空间演化 |
| **T4 临床预测型** | 配对治疗/预后队列 | Fig1 试验设计+发现队列 → Fig2 基线特征/分子分型 → Fig3 应答 vs 无应答 → Fig4 空间预测因子 → Fig5 独立验证+模型 | TNBC IMC、免疫治疗 TLS |
| **T5 方法型** | 新算法/新平台 | Fig1 workflow+QC → Fig2 benchmark → Fig3 跨平台泛化 → Fig4-6 真实疾病应用 | STARS、scXpand |
| **T6 时序过程型** | 发育/再生/疾病进展多时点 | Fig1 时间轴设计+全景 → Fig2-3 时序动态/轨迹 → Fig4 命运决定 → Fig5 信号中心/波前 → Fig6 形态建成/终态 | 原肠胚、肺再生、瓣膜发育 |

> 与 story_builder §Step4 旧表（5 模式）的对应：机制驱动型=T2、资源图谱型=T1、临床预测型=T4、发育过程型=T6、方法创新型=T5；**新增 T3 谱系演化型**（本次调研在肿瘤/血液/消化领域高频确认）。

---

## §3 领域模板卡（15 张）

> 每卡 = 该领域标准序列 + 领域专属惯例。序列是默认起点，用 §1 骨架理解其结构。

### C1 实体肿瘤（22 篇/12 结构）
- **序列**：Fig1 队列+多模态设计 → Fig2 空间细胞图谱/注释 → Fig3 关键空间结构（邻域/界面/TLS）→ Fig4 细胞状态与通讯 → Fig5 临床关联（生存/疗效）→ Fig6 验证（小鼠/独立队列）或 graphical overview
- **惯例**：TME 型按细胞大类逐类一图（T/NK→B→髓系→内皮）；CNV 推断热图区分恶性/非恶性；免疫表型分层（desert/excluded/inflamed）；病毒状态（HPV/EBV）配对对比
- **特色**：肿瘤边界带/界面梯度（最有辨识度的 panel）、TLS 解剖（独立 sub-field）、克隆 Voronoi 空间图、3D lightsheet、同片蛋白+染色体成像
- **收尾**：功能验证（Cancer Discov 系）或卡通总览（Nat Genet 系）

### C2 血液（40 篇/17 结构）
- **序列**：Fig1 设计+队列/图谱 → 中段亚群/克隆/空间结构+扰动机制（移植/编辑/药物/活体成像）→ 末图 MRD/生存/ROC/靶点
- **惯例**：克隆演化组合拳=克隆树+fishplot+oncoprint+单细胞 CNV 热图+病程时间线（纵向配对采样标配）；NMF 微环境原型（LymphoMAPs）；造血层级景观
- **特色**：CODEX/mIF 空间邻域、FICTURE 像素级图、活体双光子、TIMING 时移杀伤
- **收尾**：MRD 检出+生存/ROC（最强临床闭环惯例之一）

### C3 免疫（43 篇/12 结构）
- **序列**：Fig1 设计/图谱 → 中段按谱系逐图（CD4→CD8→B/GC→浆→髓系）或"发现亚群→状态转换→空间定位" → 空间验证（Fig3-6）→ 末图药物干预/临床分层
- **惯例**：TCR/BCR 克隆追踪贯穿图序（"克隆-表型-空间"三连图）；原位 TCR 探针（2025-26 新趋势）；GWAS 位点映射收尾；免疫组织生态（GC/TLS/聚集体）独立成图
- **特色**：纵向克隆河流图、Drug2Cell 空间药物-靶点映射、DVP 蛋白组工作流
- **收尾**：**药物干预收尾是本领域显著惯例**（IFNAR 阻断/JAKi/imatinib），区别于肿瘤

### C4 神经（38 篇/14 结构）
- **序列**：Fig1 脑区解剖示意+取样+QC/UMAP 全景 → Fig2-3 核心发现 → 中段多组学/TF 调控/通讯 → 后段空间原位验证（MERFISH/Visium/Xenium）→ 末图 GWAS 富集或治疗转化
- **惯例**：脑区解剖对照 Fig1 必备；皮层层状分布图（laminar/depth 定量）；病理-分子共定位距离梯度（Aβ/pTau/TDP-43）；跨物种（人-猴-鼠）对齐列图
- **特色**：4D 时序图谱、scWGS 突变-表达、3D 基因组 contact、Perturb-FISH
- **收尾**：遗传学落点（GWAS→细胞类型）比例最高

### C5 心血管（36 篇/16 结构）
- **序列（机制型）**：Fig1 设计+数据总览 → Fig2-3 细胞状态 → 中段空间共定位+niche 交互 → 末段遗传操纵/药物体内验证
- **惯例**：梗死分区词汇学（border/ischemic/remote zone 基因评分空间图，短轴视角）；"小鼠发现→人心脏镜像验证"跨物种图序；图谱型按解剖结构定义空间 cluster（LA/RA/LV/RV/IVS）；遗传整合型 snRNA 遗传力富集固定在 Fig5
- **特色**：Moran's I、NiCo niche 网络、邻近 log-OR 热图、全 mount 谱系追踪、PIP-seq 体内 CRISPR
- **收尾**：体内验证链（Cre KO/OE/中和抗体/senolytics）；移植排斥 Xenium+病理分级并排是 2026 新势力

### C6 发育（41 篇/13 结构）
- **序列**：Fig1 设计+全胚胎/大视场总览（**时间轴+空间轴必占前两图**）→ Fig2 全景注释或主轴分子程序 → 中段按器官/谱系逐图（鉴定→空间映射→轨迹→GRN/通讯四段式）→ 末图跨物种/疾病关联
- **惯例**：类器官走"参考图谱-投影"范式（图谱→保真度评估→来源对比→疾病建模）；轨迹映射回物理空间联合展示
- **特色**：3D 全胚胎重建、4D 分子 mapping、边界表达锐度/形态发生波前、MADM 克隆树
- **收尾**：跨物种比较或总结模型

### C7 代谢（41 篇/12 结构）
- **序列（"总-分-聚-证"）**：Fig1 图谱总览 → Fig2-N 区室逐图（免疫→血管/基质→实质）→ 中后段明星亚群（LAM/GPNMB+ 巨噬/nonclassical adipocyte）→ 末图转化/遗传（PRS-GWAS/药物）
- **惯例**：肝必做 zonation 且常以"健康参考→疾病分区丢失"叙事；脂肪 depot 对比（SAT vs VAT）+胖/减重三态；胰岛以细胞身份/可塑性为核心（velocity 必配）；减重研究"干预前后配对"纵向布局
- **特色**：分区梯度曲线、3D 基因组 loop、Hotspot/STAMP 空间模块、Perturb-seq 扰动矩阵（KO→机制→挽救→药物闭环）
- **收尾**：遗传整合（PRS/GWAS 分区富集）或药物干预

### C8 呼吸肺（20 篇/13 结构）
- **序列（图谱型）**：Fig1 队列/平台总览或核心组成变化 → 逐细胞大类差异+临床关联 → 空间 niche 验证 → 分子层整合（蛋白组/eQTL-GWAS）
- **惯例**：IPF 空转图谱以"方法学首图"开场（pipeline 惯例）；示踪时间窗 schematic（tamoxifen 黑箭头+取样彩箭头）是肺再生标志图式；近端-远端气道轴；KRT5−/KRT17+ 上皮与 SPP1+ 巨噬空间邻域
- **特色**：aberrant community 社区检测、气腔级高分辨、ECM-血浆配对蛋白组、人鼠平行映射
- **收尾**：organoid 药理/抗体中和/人肺 RNAscope（PASC 三段式：人现象→鼠复制→干预逆转）

### C9 消化肝胆胰（39 篇/13 结构）
- **序列（TME 型）**：Fig1 队列/工作流+UMAP → Fig2 空间分布/解卷积 → 逐细胞大类一图 → 临床转化收尾（KM/ROC）
- **惯例**：肝 zonation 独立成图（分区热图、zone index、沿小叶轴折线、跨物种并排）；多平台验证链（Visium→MERFISH→Visium HD→PhenoCycler）；肠领域隐窝谱系示踪（Confetti/Voronoi 克隆分割/mtDNA 条码）；平台 benchmarking 服务临床试验设计
- **特色**：STAMP/Hotspot 空间主题、FlowSig 细胞间流、dN/dS 选择+克隆树、MSI 空间代谢组配准
- **收尾**：原位验证→功能实验→临床端（KM/ROC/UK Biobank PheWAS）

### C10 肾脏（28 篇/12 结构）
- **序列**：Fig1 设计+图谱（UMAP+marker dot+全肾空间图，常配 PAS 损伤评分/BUN/Scr）→ Fig2-3 状态转换（伪时间/Sankey）→ 中段 niche 解卷积+通讯 → 末图 KM/预后评分（FME-GS 类）或 IF/RNAscope 验证
- **惯例**：**肾单位节段是核心 axis**（PT/TAL/DCT/CD 各自成图；AKI 必有 PT 状态转换专图）；皮质-髓质-乳头轴向梯度；纤维化微环境（FME）已固化为独立分析单元+预后评分
- **特色**：距离依赖 L-R 曲线、邻域山脊图、跨物种 label transfer、患者个体化功能报告
- **收尾**：预后基因评分或治疗性干预（KO/OE）

### C11 皮肤（32 篇/12 结构）
- **序列（Nat Commun 7 图制）**：Fig1 图谱总览（workflow+UMAP+分组组成条）→ Fig2-3 亚群深挖（KC 分化轨迹/免疫亚型）→ Fig4-5 通路功能（pseudobulk 回映射+体外）→ Fig6 空间/通信双验证 → Fig7 机制 schema/治疗验证（Fig8 graphical abstract 收尾）
- **惯例**：**表皮分层（基底-棘层-颗粒）是默认空间轴**；真皮-表皮界面+毛囊单位是两大锚定结构；EIME（KC-成纤维-免疫三元）叙事；皮损/非皮损/健康三组配色
- **特色**：鼠-犬-人并列空转跨物种验证、MERFISH 邻域聚类、4D 发育动力学
- **收尾**：双模型（IMQ+IL-23A）+KO/药理双干预插槽；终图图形摘要

### C12 骨肌（32 篇/19 结构）
- **序列（图谱型）**：Fig1 分区采样设计+图谱 → Fig2-3 谱系精细聚类+空间定位 → Fig4-5 差异/衰老对比 → Fig6 机制轴 → 末图 GWAS/变异注释或模型
- **惯例**：**分区采样是 Fig1 标配**（软骨承重/非承重、肌腱解剖微区、骨皮质/内膜）；肌核与单核常住细胞分开聚类再整合；损伤-再生多时点+力学负荷（BTX/跑轮）为特有实验变量
- **特色**：scWGS 体细胞突变签名、3D 透明化淋巴管、生物力学曲线、Manhattan 样细胞特异 DE
- **收尾**：AAV/抗体/小分子药物拯救（Maraviroc/hPTH/抗 BSG）+人活检保守性验证

### C13 衰老（28 篇/12 结构）
- **序列**：Fig1 设计+年龄分布+图谱+空间注释 → 中段按 lineage 分章（**章内固定序列：UMAP→年龄组比例箱线→火山/点图→衰老评分→伪时间**）→ 空间章（通讯点图+邻域统计）→ 末图验证+干预
- **惯例**：correlation-with-age 热图+LOESS/滑动窗口呈现非线性；senotype（衰老亚型）术语化+空间定位-清除闭环（mapping→targeting）
- **特色**：空间衰老时钟（预测 vs 实际年龄+扰动建模）、SASP Circos、最优传输转变矩阵、dMRI-空转联合
- **收尾**：senolytic/senomorphic 药物（槲皮素/维奈托克/Maraviroc）+敲除小鼠+总结模型

### C14 感染（32 篇/13 结构）
- **序列（近模板化）**：Fig1 设计+队列+**感染时间线**（挑战时间轴/采样点/病原载量，重症/轻症/后遗症分层贯穿配色）→ Fig2-3 受感染细胞身份定位+时序状态 → 中段 TCR/代谢深挖+空间验证（IMC/Xenium/RNAscope）→ 末图机制干预+跨队列跨物种签名回映射
- **惯例**："外周 vs 组织能否互代"常独立成图；宿主-微生物研究把**病原空间定位与载量作主线图**；PASC 三段式（人现象→鼠复制→干预逆转）
- **特色**：宿主-病原共检测空间图、物种-面积曲线、病原端单细胞时杀曲线+ROC、病毒基因组覆盖图
- **收尾**：中和/清除/药物拯救（IFNβ）+模型示意

### C15 生殖母胎（34 篇/13 结构）
- **序列**：Fig1 景观图（设计+UMAP+marker+组成+空间总览）→ Fig2-N 分谱系（滋养层/上皮→基质/蜕膜→免疫/内皮）→ 轨迹与调控 → 倒数第二图疾病/干预对比 → 终图机制模型
- **惯例**：**孕周/月经周期（LH 日/WOI）时序是独有坐标轴**；母胎界面双向性——SNP/基因型拆分母体 vs 胎儿来源是 Nature/NG 标配；绒毛-蜕膜界面互作（EVT 侵袭/螺旋动脉重塑/uNK）必有专属主图；滋养层分层话语（VCT→SCT/EVT）
- **特色**：界面距离分箱统计、CODEX 状态级联（caEC→R0→R2）、CellTrek 映射、StemVAE 时间偏移
- **收尾**：疾病"逆转热图"（二甲双胍）+拯救实验（sitagliptin/Il1r2-KO）；体外模型桥接（类器官相似性对比）

---

## §4 期刊格式规则（裁剪主图数量的硬约束）

| 期刊系 | 主图数 | 补充结构 | 惯例 |
|---|---|---|---|
| **Nature 系**（Nature/NM/NG/NN/NI/Nature Aging） | **4-6 张**（衰老/图谱 5-7） | Extended Data 6-18 张 | QC/基准/replicate/阴性对照/人体验证**全部下沉 ED**；ED 图题模板化（"Complementary xxx analysis"）；正文图必须讲完整故事链 |
| **Cell 系**（Cell/Cancer Cell/Immunity/Cell Stem Cell/Cell Metab） | **6-8 张**（Cell 正刊偶 4 张） | 无 ED，补充材料另编 | caption 逐 panel（A,B,C…）长描述；单图信息密度更高；机制发现编入主图 |
| **Nat Commun** | **7-8 张** | Supp Figures 数十张 | 机制验证做满（KO/拯救各占 1-2 图）；终图 graphical abstract 惯例 |
| **领域顶刊**（Blood/CircRes/ARD/Gut 等） | 3-8 张 | 按刊别 | Blood caption 内嵌 panel 级 n；CircRes 6-8 主图一线排开无 ED，Fig1 必为实验时序设计 |

- 主图数量中位数（203 篇）：**6 张**；最紧凑 3-4（Nature 正刊方法/机制），最多 8（Nat Commun 机制做满）。
- **迁移规则**：同一故事投 Nature 系 → 中段每谱系合并、验证下沉 ED；投 Cell/Nat Commun → 展开逐谱系+验证上图。

---

## §5 图型频率表 → 绘图优先度（低频模板降级）

**超高频（≥80% 论文；cns_style 已全覆盖）**：
UMAP/聚类（plot_umap）、组成比例（plot_bar/plot_cellproportion）、marker dotplot（plot_dotplot）、DE 火山/热图（plot_volcano/plot_heatmap）、空间着色+H&E（plot_spatial）、轨迹/伪时间（plot_paga/plot_pseudotime）、L-R 通信（plot_ccc/plot_lr_bubble/plot_ccc_heatmap）、实验设计 schematic（scientific-schematics）、湿实验验证图（IF/IHC/RNAscope——拍照无代码模板）

**高频（30-60%；已覆盖）**：
Milo beeswarm（plot_milo）、邻域/共定位（plot_nhood_enrichment/plot_colocalization/plot_distance_distribution）、去卷积空间图（plot_deconv_pie/plot_spatial）、富集（plot_enrichment/plot_enrichment_scatter）、KM/生存（ov.pl.kaplan_meier）、RNA velocity（rna-velocity skill）、pseudobulk 回映射、跨物种 label transfer（散点/umap）

**中频（10-30%；本次新增 4 个模板）**：
| 图型 | 频率证据 | 入口 | 代码 |
|---|---|---|---|
| Sankey/状态转换 | 肾 PT 转换、心 alluvial、衰老 OT 矩阵、发育命运流 | `plot_sankey` | plotting_reference §3.41 |
| CNV 基因组热图 | 肿瘤 ~40%、血液演化标配 | `plot_cnv_heatmap` | §3.42 |
| 轴向/距离梯度曲线 | 肝 zonation、肾轴、神经病理共定位、肿瘤边界、母胎界面——**跨领域最通用的新增图型** | `plot_axis_gradient` | §3.43 |
| 克隆扩增追踪 | 免疫 TCR 三连图、血液/感染克隆演化 | `plot_clone_expansion` | §3.44 |

**低频特色（<10%；不建代码模板，降优先度——需要时按此指引外部工具）**：
fishplot/克隆树（R fishplot/cloneevolve、 grapetree）、oncoprint（R ComplexHeatmap `oncoPrint`）、克隆 Voronoi 空间图（scipy `Voronoi` + patch）、3D 重建（napari/BioIO/3D viewer）、4D mapping/最优传输（moscot）、空间时钟（自研+GNN）、scWGS 突变签名（Signatures）、宿主-病原共检测（原厂 pipeline）、FICTURE 像素图（ficture CLI）、dMRI 配准（ANTs）、数学模型/生物力学（MATLAB/自定义）。
**路由纪律**：这些图型仅当领域卡明确列为"特色"且用户点名时才启动；默认用中高频图型替代（如克隆树→`plot_sankey` 两阶段替代；oncoprint→`plot_heatmap`+注释条替代）。

---

## §6 与既有文档的关系（防重复漂移）

- **story_builder.md Step 4**：五步法的 Figure 映射步骤改为"先查本文件路由 → 回 story_builder 检查逻辑链完整"
- **figure_guide.md §0.1**：数据→图型决策（单 panel 层）；本文件=**图组层**（整篇 fig 顺序）。两层互补：先本文件定序列，再 §0.1 定每张图型
- **plotting_reference.md §3.41-3.45**：新增 4 图型代码 + 低频图型指引
- **paper_paradigms.md / paper_directions.md**：分析路径层（链 A-E）；本文件=呈现层。分析链决定"有什么可画"，本文件决定"按什么顺序画"
- 原始调研档案 `D:\workspace\lit_survey\01-15_*.md`（506 篇逐篇条目；换机器后可重新生成）
