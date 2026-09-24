# 领域代表作案例索引（15 领域 × 2-3 篇）

> 精选自 2024-2026 年 15 领域 506 篇 CNS 调研（完整档案曾存 D:\workspace\lit_survey\，机器特定）。
> 用途：写论文/组稿时查"某领域代表作的主图序列实例"；图组模板（该学什么）查 figure_templates.md，本文件是"谁这么发过"。
> 选取标准：正刊优先 + Figure 结构完整 + 覆盖研究类型（图谱/机制/临床）+ 空转或 scRNA+空转联合优先。所有条目照抄调研文件记录，无编造。

## C1 实体肿瘤
### P1. Spatial Mapping of the Precancer-to-Cancer Transition in Breast and Prostate
- Cancer Discovery 2026 | 人（乳腺/前列腺） | lightsheet + 连续切片空间转录组 3D 重建 | 机制（癌前-癌转换）
- 主图序列：Fig1 队列与 3D 空间组学设计 → Fig2 lightsheet 3D 肿瘤结构 → Fig3 乳腺 DCIS→IDC 跨界面梯度 → Fig4 前列腺 normal→GP3 平行验证 → Fig5 TAM/CAF 界面邻近 → Fig6 两癌种共同/差异机制 → Fig7 shRNA+类器官功能验证
- 可借鉴点：边界带"跨界面表达梯度"panel 的排布方式；Fig7 体外/体内验证收尾
### P2. Spatially resolved single-cell analyses of human meningioma identify novel cell states...
- Nature Genetics 2026 | 人脑膜瘤多区域 | snRNA-seq + 空转 + DNA 甲基化 | 图谱+临床预测
- 主图序列：Fig1 微环境转录多样性与 metaprogram → Fig2 区域采样异质性+CNV 一致性 → Fig3 硬膜→肿瘤髓系空间梯度 → Fig4 髓系状态-肿瘤互作与空间依赖 → Fig5 预后模型（KM+超越分子分级） → Fig6 graphical overview（+6 ED）
- 可借鉴点：NatGenet 图谱-临床范式（异质性→空间→互作→预后→总览卡通）；dura→tumor 界面梯度 panel
### P3. Humoral IgG1 responses to tumor antigens underpin clinical outcomes in immune checkpoint blockade
- Nature Medicine 2026 | 人 HCC 新辅助抗 PD-1 | 血浆 IgG1 + scRNA/BCR + seromics + 空间 | 临床预测/机制
- 主图序列：Fig1 发现队列与 IgG1 同型 → Fig2 克隆性（BCR） → Fig3 免疫浸润空间分析（TLS/B 细胞聚集） → Fig4 验证队列 → Fig5 肿瘤抗原与血清标志物 → Fig6 生存+互作机制（+5 ED 全部 "Complementary xxx"）
- 可借鉴点：TLS 专图的 panel 组成；Nat Med 式"发现→克隆性→空间→验证→抗原→生存"临床链条

## C2 血液学
### P1. Mapping the cellular biogeography of human bone marrow niches...
- Cell 2024 | 人骨髓（含 AML） | 10x scRNA + CODEX 53 重免疫成像 | 空间生态位图谱
- 主图序列：Fig1 全细胞 scRNA 图谱 → Fig2 非造血基质亚群 → Fig3 细胞间通讯网络 → Fig4 CODEX 空间拓扑 → Fig5 邻域分析（GMP 生态位） → Fig6 HSPC 脂肪生态位 → Fig7 AML 映射与特异邻域
- 可借鉴点：CODEX 多重成像+空间邻域统计的组合；scRNA→空间成像逐层递进图序
### P2. Chromatin landscape and epigenetic heterogeneity of acute myeloid leukaemia
- Nature 2026 | 人 AML | ATAC + scATAC（+表达） | 表观分型/机制
- 主图序列：Fig1 ATAC 定义表观亚群 → Fig2 亚群表达与超级增强子 → Fig3 SE 驱动 GRN（TF 网络） → Fig4 单细胞分化状态与 TF 动态 → Fig5 预后与药敏（KM+C-index）
- 可借鉴点：正刊 5 主图紧凑制；超级增强子热图与 TF 调控网络图型
### P3. Single-cell multiomics analysis reveals dynamic clonal evolution... in acute myeloid leukemia with complex karyotype
- Nature Genetics 2024 | 人 CK-AML | 单细胞基因组+转录组 + FISH + PDX | 克隆演化/治疗
- 主图序列：Fig1 核型异质性（核型热图+Circos） → Fig2 克隆动态（克隆树+FISH） → Fig3 亚克隆转录结构 → Fig4 小鼠重建克隆演化（fish plot） → Fig5 LSC 药敏 → Fig6 复发遗传演化 → Fig7 耐药亚克隆机制
- 可借鉴点：克隆演化可视化组合拳（克隆树+fish plot+oncoprint+病程时间线），纵向配对采样论文标配

## C3 免疫学
### P1. Spatial proteomics identifies JAKi as treatment for a lethal skin disease
- Nature 2024 | 人 TEN + 小鼠 | 深度视觉蛋白组 DVP（AI 分割+激光显微切割+mDIA） | 空间蛋白组→药物重定位
- 主图序列：Fig1 DVP 工作流+角质细胞蛋白组 → Fig2 病灶免疫细胞蛋白组 → Fig3 免疫亚型空间蛋白图谱 → Fig4 JAK/STAT 通路激活发现 → Fig5 体内外药效 → Fig6 患者治疗获益
- 可借鉴点："发现→验证→患者"三段式收官；空间蛋白组工作流首图
### P2. High-definition spatial transcriptomic profiling of immune cell populations in colorectal cancer
- Nature Genetics 2025 | 人 CRC FFPE | Visium HD(2/8µm) + Xenium（含 TCR 探针）+ Flex scRNA | 高分辨空转图谱
- 主图序列：Fig1 HD 数据总览 → Fig2 平台性能基准（vs Visium/Xenium） → Fig3 高分辨转录映射 → Fig4 肿瘤外周细胞组成 → Fig5 巨噬细胞亚群空间定位 → Fig6 T 细胞空间定位 → Fig7 Xenium+TCR 探针原位验证克隆扩增
- 可借鉴点：原位 TCR 克隆扩增验证（Xenium 定制探针）是 2025-2026 新趋势
### P3. Immune-epithelial-stromal networks define the cellular ecosystem of the small intestine in celiac disease
- Nature Immunology 2025 | 人乳糜泻多队列 | scRNA + 靶向测序 + Visium + TCR | 自免图谱
- 主图序列：Fig1 队列设计 → Fig2 上皮 → Fig3 CD4 T（含 TCR） → Fig4/5 CD8 T 状态与克隆 → Fig6 空转免疫分布 → Fig7 TFH-B 淋巴聚集体生态位 → Fig8 空间分辨黏膜免疫模型
- 可借鉴点：按免疫谱系逐图展开+空转充当"第二幕转折"；终图"机制模型+空转背景"

## C4 神经科学
### P1. Single-cell and spatial atlases of spinal cord injury in the Tabulae Paralytica
- Nature 2024 | 小鼠 SCI 多时点 | snRNA + 多组学 + Visium + 4D 时空 + 基因治疗 | 旗舰图谱
- 主图序列：Fig1 总设计概览 → Fig2 细胞类型/亚型全景 → Fig3 损伤响应生物学原则 → Fig4 年老-年轻屏障重建对比 → Fig5 多组学模块 → Fig6 空转模块（损伤空间梯度） → Fig7 4D 时空图谱 → Fig8 基因治疗恢复行走
- 可借鉴点：模块化总览图开场；"4D 时空图谱+视频"与治疗行为学收尾的旗舰级排布
### P2. Human microglial transitions at the Aβ-tau inflection point...
- Nature Medicine 2026 | 人 80+/百岁老人脑 | Visium + Xenium + IF | AD 病理空间组学
- 主图序列：Fig1 病理 spot 界定（Aβ/pTau） → Fig2 组织域（Tissue Domain）分类 → Fig3 斑块诱导基因程序早/晚期 → Fig4 Xenium+IF 双重验证 → Fig5 独立队列验证
- 可借鉴点：病理注释 spot 图+斑块距离-表达梯度 panel；"发现→原位双验证→队列验证"三段式
### P3. An emergent disease-associated motor neuron state precedes cell death in ALS
- Cell 2026 | 小鼠 SOD1 + 人脊髓 | snRNA + snATAC + 空间 + 人核转录组 | 机制
- 主图序列：Fig1 时间点取材+脊髓图谱 → Fig2 疾病关联运动神经元（DM）状态 → Fig3 snATAC 染色质可及性 → Fig4 DM 状态 TF 调控 → Fig5 人运动神经元诱导验证 → Fig6 空间+组成随病程 → Fig7 人样本+ALS 遗传关联
- 可借鉴点：疾病时间 course 谱系动态贯穿图序；人鼠跨物种验证排布

## C5 心血管
### P1. Spatially clustered type I interferon responses at injury borderzones
- Nature 2024 | 小鼠 MI + 人心验证 | Visium + RNA/DNA-MERFISH + sc/snRNA + Irf3 敲除 | 机制
- 主图序列：Fig1 BZ 基因评分/ISG 评分空间图 → Fig2 人梗死心跨物种验证 → Fig3 细胞类型特异 Irf3-KO 定源 → Fig4 DNA-MERFISH 核破裂成像 → Fig5 破裂位点共定位+生存 meta（+10 ED）
- 可借鉴点：梗死 border zone 基因评分空间图是 MI 空转标准 panel；"小鼠发现→人心验证"镜像结构
### P2. Targeting immune-fibroblast cell communication in heart failure
- Nature 2024 | 人 MI+HF 心 | CITE-seq + Multiome + 空转 | 机制+治疗靶点
- 主图序列：Fig1 多组学队列总览 → Fig2 成纤维细胞状态细分 → Fig3 体内/体外模型映射比较 → Fig4 CCR2 巨噬-成纤维空间共定位+IL-1β → Fig5 体内干预验证（+10 ED）
- 可借鉴点：体内-体外模型映射图；"治疗后细胞状态轨迹"作为 ED 收尾
### P3. Dynamic cellular programs of human cardiac allograft rejection revealed by spatial transcriptomics
- Nature Cardiovascular Research 2026 | 人移植心活检 | Xenium 高分辨空转 | 临床空转
- 主图序列：Fig1 治疗全流程 alluvial+细胞全景 → Fig2 细胞邻近 log-OR 热图 → Fig3 病理分级-分子异质性 → Fig4 ACR vs AMR 细胞特异签名 → Fig5 治疗后与 CAV 关联
- 可借鉴点：治疗时间线 alluvial 与细胞邻近 log odds-ratio 热图；病理分级与空间程序并排展示

## C6 发育生物学
### P1. Whole-embryo spatial transcriptomics at subcellular resolution from gastrulation to organogenesis
- Science 2026 | 斑马鱼 | weMERFISH(495 基) + snRNA + ATAC 推断 | 全胚胎时空图谱（图题取自 bioRxiv 预印本）
- 主图序列：Fig1 全胚胎成像流程与基因面板 → Fig2 多阶段表达/可及性空间模式 → Fig3 跨阶段空间聚类 → Fig4 伪时序轨迹映射回物理空间+RNA velocity → Fig5 组织特异基因/peak → Fig6 染色质调控逻辑 → Fig7 组织边界表达锐度+smFISH 验证
- 可借鉴点：轨迹-物理空间联合映射；组织边界"锐度"定量 panel
### P2. Spatiotemporal transcriptome atlas of human embryos after gastrulation
- Nature 2026 | 人 CS12-23 | snRNA-seq + 空转 | 全胚胎时空图谱
- 主图序列：Fig1 时空图谱总览（时间轴+UMAP+空间） → Fig2 器官亚结构谱系与 GRN 全景 → Fig3 心脏亚结构 GRN → Fig4 神经系统区域化（人鼠比较） → Fig5 病毒受体器官富集与疾病易感
- 可借鉴点：亚结构级 GRN 空间模块；"时间轴+空间轴必占 Fig1-2"的发育领域惯例
### P3. A three-dimensional spatial transcriptome atlas reconstructs early organogenesis in primate CS9/10 embryos
- Nature Cell Biology 2026 | 食蟹猴 | Stereo-seq + 3D 重建 | 3D 时空图谱
- 主图序列：Fig1 空转表征与 3D 重建总览 → Fig2 A-P 轴分子程序与信号 → Fig3 心管 → Fig4 肠管 → Fig5 神经胚 → Fig6 体节/轴 → Fig7 脊索 → Fig8 跨物种（人/猴/鼠）比较
- 可借鉴点：3D 胚胎重建开场+按器官逐图推进（每图"鉴定→空间→动态"）；跨物种收尾

## C7 代谢/内分泌
### P1. Spatially resolved multi-omics of human MASLD
- Nature Genetics 2025 | 人肝 | Visium + snRNA/scRNA + 空间代谢组 MSI + 蛋白组 | 疾病图谱+机制
- 主图序列：Fig1 空间+单细胞图谱总览 → Fig2 分期细胞状态变化（Milo+TCR） → Fig3 LAM 特异 TF MITF → Fig4 MITF-PGC1α-PPARγ-FAO 轴（Seahorse+共聚焦） → Fig5 HGF-MET 肝保护 → Fig6 STAMP 纤维化空间主题 → Fig7 Hotspot 代谢模块+MSI 配准
- 可借鉴点：空间主题模型（STAMP/Hotspot）与 MSI-空转配准（STalign）图型
### P2. A spatial atlas of the healthy human liver from live donors
- Nature 2026 | 人活体供肝+跨物种 | Visium/Visium HD + snRNA + MERFISH + PhenoCycler | 健康参考图谱
- 主图序列：Fig1 空间表达图谱总览 → Fig2 肝细胞分区（zonation）梯度 → Fig3 跨物种分区保守性 → Fig4 NPC 分区 → Fig5 脂变肝细胞动态（+10 ED 多平台互验）
- 可借鉴点：肝小叶分区（zonal heatmap/zone index 空间图/沿轴折线）三连 panel；"健康参考→疾病分区丢失"叙事
### P3. Selective remodelling of the adipose niche in obesity and weight loss
- Nature 2025 | 人脂肪 | scRNA + 空转 | 肥胖-减重纵向图谱
- 主图序列：Fig1 瘦/胖/减重三态图谱 → Fig2 免疫区室 → Fig3 脂肪细胞区室动态 → Fig4 应激细胞空间 niche → Fig5 减重逆转衰老
- 可借鉴点：三态（lean/obese/WL）对比设计；"干预前后配对+末图通讯重塑"惯例

## C8 呼吸/肺
### P1. Spatial transcriptomics identifies molecular niche dysregulation... in pulmonary fibrosis
- Nature Genetics 2025 | 人 PF vs 未受累肺 | Visium + scRNA 参考 | 疾病空转图谱
- 主图序列：Fig1 空转分析 pipeline → Fig2 标记基因+空间信息推断组成 → Fig3 多方法互补 niche 注释 → Fig4 KRT5−/KRT17+ 上皮在活动纤维化位点 → Fig5 FABP4+/SPP1+ 巨噬空隙聚集 → Fig6 气腔分辨率肺泡重塑
- 可借鉴点：罕见的"方法学首图"惯例；KRT5−/KRT17+ 与 SPP1+ 巨噬空间邻域 panel
### P2. Histological signatures map anti-fibrotic factors in mouse and human lungs
- Nature 2025 | 小鼠博来霉素时序 + 人 IPF | snRNA/scRNA + ATAC + 空间蛋白 | 纤维化-消退机制
- 主图序列：Fig1 组织学轨迹定义纤维化/纤化后状态 → Fig2 成纤维亚型时序富集 → Fig3 表观（ATAC）转变 → Fig4 空间组织演化+通讯 → Fig5 邻域富集因子离体功能验证 → Fig6 人 IPF 空间蛋白表型
- 可借鉴点：组织学轨迹图+时间梯度设计；"空间邻域→外植体功能验证"闭环
### P3. An aberrant immune–epithelial progenitor niche drives viral lung sequelae
- Nature 2024 | 人 PASC-PF + 小鼠模型 | 空转 + scRNA + 干预 | 感染后遗机制
- 主图序列：Fig1 异常免疫-上皮祖细胞 niche 标志 → Fig2 持续 CD8 T 损害肺泡再生 → Fig3 空转三细胞 niche（CD8-巨噬-祖细胞） → Fig4 IFNγ/TNF→IL-1β 因果轴 → Fig5 细胞因子中和促再生
- 可借鉴点：三细胞空间 niche 专图；Nature 5 主图短链路+治疗转化终图

## C9 消化/肝胆胰
### P1. Single-cell integration reveals metaplasia in inflammatory gut diseases
- Nature 2024 | 人全 GI + IBD/乳糜泻 | scRNA 整合 + smFISH/蛋白验证 | 参考-疾病映射图谱
- 主图序列：Fig1 泛胃肠整合总览（scAutoQC） → Fig2 IBD 化生谱系（口腔黏膜成纤维/Paneth） → Fig3 INFLARE 鉴定（smFISH） → Fig4 干细胞起源拟时序 → Fig5 免疫招募互作（+10 ED）
- 可借鉴点：泛器官参考映射+smFISH 原位验证贯穿；化生状态拟时序 panel
### P2. A longitudinal single-cell atlas of anti-TNF treatment in IBD（TAURUS）
- Nature Immunology 2024 | 人 CD/UC 治疗前后配对 | scRNA(98.8 万) + GeoMx + RNAscope | 纵向治疗图谱
- 主图序列：Fig1 TAURUS 设计+109 状态 UMAP → Fig2 上皮/淋巴细胞化学计量（RNAscope 验证） → Fig3 GEP 空间 niche 枢纽 → Fig4 缓解 vs 无缓解治疗前差异 → Fig5 adalimumab 后变化 → Fig6 IBD-RA 跨疾病 meta-atlas
- 可借鉴点：治疗前后配对热图与"虚拟 H&E+GEP 网络枢纽"图型；跨疾病转移图谱收尾
### P3. An immunobiliary single-cell atlas resolves cDC2–γδ T cell crosstalk in cholangitis
- Nature Communications 2026 | 人 + 小鼠 DDC | scRNA + 成像型空转 + CITE-seq + Multiome | 机制
- 主图序列：Fig1 免疫胆道微环境（空间 niche+IHC） → Fig2 DDC 导管反应（NiCo 空间互作） → Fig3 疾病分期特异 cDC2 转变 → Fig4 γδT17 纤维化（共培养） → Fig5 空间去卷积 cDC2B-γδT domain → Fig6 cDC2B 耗竭实验 → Fig7 引流淋巴结 CITE-seq+图形摘要
- 可借鉴点：NiCo 空间互作网络；SCENIC+motif 与 Multiome 混编；图形摘要收尾

## C10 肾脏
### P1. Spatial atlas of diabetic kidney disease reveals a B cell-rich subgroup
- Nature 2026 | 人 DKD 活检 | 空转 + Xenium + IMC + snRNA 参考 | 疾病空间分型
- 主图序列：Fig1 细胞分辨率空间图谱总览 → Fig2 niche 解码组织架构（GFR 相关） → Fig3 促纤维化微环境 → Fig4 免疫景观空间制图 → Fig5 B 细胞微环境定义亚型（KM+标志物）
- 可借鉴点：niche 聚类→免疫空间→分子分型→患者分层收官；Xenium+IMC 多模态验证 panel
### P2. Single-cell multi-omic and spatial profiling of human kidneys implicates the fibrotic microenvironment...
- Nature Genetics 2024 | 人 KPMP 队列 | sc/snRNA+ATAC + Visium + CosMx | 图谱+预后
- 主图序列：Fig1 多模态整合图谱 → Fig2 空间分辨人肾 → Fig3 基质细胞图谱 → Fig4 纤维化微环境（FME） → Fig5 受伤近曲小管 iPT → Fig6 FME-GS 大队列预后验证
- 可借鉴点：FME（纤维化微环境）专图+基因评分→临床预后（KM/ROC）转化
### P3. Single-cell spatial mapping of human kidney development implicates the microenvironment in guiding cell fate decisions
- Nature Genetics 2026 | 人胚胎/胎儿肾 | scRNA + 空转 + RNA velocity/CellRank + IF | 发育+命运机制
- 主图序列：Fig1 发育人肾 scRNA 图谱 → Fig2 分化轨迹（velocity+CellRank） → Fig3 胎儿特异肾小体内 PT 空间模式 → Fig4 空间分子表征（空间伪时间） → Fig5 组织学邻域（环形邻域频率图） → Fig6 IGF2-NPC 干性（类器官验证） → Fig7 无偏空间邻域 microenvironment
- 可借鉴点：空间伪时间与环形邻域频率图；配体活性空间评分+类器官验证

## C11 皮肤
### P1. A prenatal skin atlas reveals immune regulation of human skin morphogenesis
- Nature 2024 | 人胎龄 5-17 周皮肤 | scRNA + 空转 + 类器官 | 发育图谱
- 主图序列：Fig1 单细胞图谱总览（时间轴） → Fig2 毛囊发育（轨迹+原位） → Fig3 成纤维-巨噬与无瘢痕愈合 → Fig4 巨噬细胞支持血管生成
- 可借鉴点：4 主图+大量 ED 的 Nature 图谱制；"无瘢痕愈合 vs 瘢痕"对照逻辑
### P2. Single-cell spatial transcriptomic analysis of human skin anatomy
- Nature Genetics 2026 | 成人多解剖部位 | MERFISH + scRNA 反卷积 | 空间解剖图谱
- 主图序列：Fig1 MERFISH panel 与采样设计 → Fig2 跨部位细胞密度/丰度刻板模式 → Fig3 多细胞空间邻域定义 → Fig4 部位×老化邻域重塑 → Fig5 邻域内/跨邻域 L-R 通信 → Fig6 疾病微解剖重塑（+10 ED）
- 可借鉴点：邻域（neighborhood）为分析单元贯穿全篇；部位-老化双因素丰度热图
### P3. Cross-species comparative spatial transcriptomics of hair follicle–T cell interactions...（cutaneous lupus）
- Nature Communications 2026 | 小鼠+犬+人 | Visium 空转 | 跨物种疾病机制
- 主图序列：Fig1 CLE 小鼠模型 → Fig2 自反应 CD8 T 攻击毛囊 → Fig3 小鼠空转保守/差异 → Fig4 犬自发性 DLE 空转验证 → Fig5 人 DLE 受累毛囊验证 → Fig6 CXCR3 轴保守+缺陷减轻 → Fig7 B 细胞清除疗效
- 可借鉴点："鼠→犬→人"三物种空转并列比较的组织方式；毛囊-免疫互作专图

## C12 骨骼/肌肉/关节
### P1. Multimodal cell atlas of the ageing human skeletal muscle
- Nature 2024 | 人 15-99 岁 | snRNA + snATAC 多模态 | 器官衰老图谱
- 主图序列：Fig1 多模态图谱总览 → Fig2 衰老新肌核亚群 → Fig3 肌核衰老轨迹与 GRN → Fig4 常驻单核细胞群 → Fig5 互作组 → Fig6 肌少症遗传变异注释（+7 ED）
- 可借鉴点：肌核与单核常住细胞分开聚类再整合；GWAS 变异功能注释收尾
### P2. Transcriptomic analysis of skeletal muscle regeneration across mouse lifespan...
- Nature Aging 2024 | 小鼠损伤后时序 | scRNA 时序 + 空转验证 | 再生+衰老图谱
- 主图序列：Fig1 跨生命周期再生图谱组装 → Fig2 年龄差异细胞动态 → Fig3 信息学衰老打分 → Fig4 打分方法评估 → Fig5 年龄特异成肌轨迹 → Fig6 过渡态衰老样聚集 → Fig7 空转损伤区定位衰老样 MuSC
- 可借鉴点：时序构成曲线（stacked area）招牌图型；衰老打分及其方法学评估独立成图
### P3. Cell type mapping of inflammatory muscle diseases... in inclusion body myositis
- Nature Aging 2024 | 人 IBM | snRNA + 空转 | 疾病图谱
- 主图序列：Fig1 组织学+snRNA+ST 总览 → Fig2 肌核/免疫/内皮/基质亚群精聚类 → Fig3 差异丰度分析 → Fig4 IBM 特异炎性组织 niche → Fig5 GADD45A 相关肌纤维 T 细胞浸润 → Fig6 ACHE/NORAD 轴
- 可借鉴点：snRNA+ST 联用图序（总览→精聚类→丰度→空间 niche→浸润定位）

## C13 衰老
### P1. Single-cell transcriptomic and genomic changes in the ageing human brain
- Nature 2025 | 人 PFC 全生命周期 | snRNA + scWGS + MERFISH | 衰老图谱+突变偶联
- 主图序列：Fig1 三技术并行设计+图谱 → Fig2 全生命周期转录状态（MERFISH 验证） → Fig3 跨细胞类型共性下调 → Fig4 scWGS 突变签名与表达关联 → Fig5 基因属性-突变负荷-下调整合模型（+10 ED）
- 可借鉴点：年龄趋势散点+CI 与混合效应模型图；scWGS-表达偶联的特色 panel
### P2. Single-cell spatial atlas of the aging human breast
- Nature Aging 2026 | 人 527 例 | 成像质体流式 IMC（40 蛋白） | 空间衰老图谱
- 主图序列：Fig1 队列与成像设计 → Fig2 腔上皮异质性 → Fig3 表型组成与年龄 → Fig4 增殖/形态衰老变化 → Fig5 微环境空间结构（Ripley's K） → Fig6 多细胞邻域聚类 → Fig7 上皮结构组织级重塑 → Fig8 非线性衰老模式
- 可借鉴点：Ripley's K 空间统计与滑动窗口非线性衰老曲线；空间蛋白组建图谱全篇
### P3. Spatiotemporal transcriptomic changes of human ovarian aging and the regulatory role of FOXP1
- Nature Aging 2024 | 人卵巢 + 小鼠 | scRNA + 空转 + 条件 KO + senolytic | 时空图谱+机制干预
- 主图序列：Fig1 卵巢单细胞+空间定位 → Fig2 细胞类型时空程序 → Fig3 卵母细胞时序与通讯 → Fig4 颗粒细胞亚群 → Fig5 卵泡膜/间质亚群 → Fig6 FOXP1 调控（ChIP/荧光素酶） → Fig7 条件 KO 加速衰老 → Fig8 槲皮素保护储备
- 可借鉴点：衰老领域"图谱→机制 KO→senolytic 干预"完整收尾链条；时空 spot 联排

## C14 感染/微生物组
### P1. Human SARS-CoV-2 challenge uncovers local and systemic response dynamics
- Nature 2024 | 人挑战队列 | 纵向 scRNA + TCR + 流式/显微 | 感染时间序列
- 主图序列：Fig1 接毒后细胞状态时间动态 → Fig2 状态特异抗病毒应答与感染细胞 → Fig3 第 10 天适应性免疫（TCR） → Fig4 与自然感染整合的公共 TCR motif（+10 ED）
- 可借鉴点：人体攻毒纵向设计+感染时间线折线；Nature 4 主图+ED 分层极简制
### P2. Spatially resolved single-cell atlas unveils a distinct cellular signature of fatal lung COVID-19 in a Malawian population
- Nature Medicine 2024 | 人马拉维尸检肺 | IMC + scRNA + HLCA 整合 | 空间+单细胞图谱
- 主图序列：Fig1 队列与病变类型跨人群对比 → Fig2 IMC 免疫病理景观（巨噬细胞驱动） → Fig3 肺单细胞图谱 IFN-γ 应答 → Fig4 HLCA 整合 T-巨噬 IFN-γ 轴 → Fig5 鼻/血 vs 肺一致性 → Fig6 空间互作预测+原位 L-R 染色
- 可借鉴点：跨人群/跨队列整合验证；"外周能否代表组织"独立成图
### P3. Spatial transcriptomics maps host-gut microbiome biogeography at high resolution
- Nature Microbiology 2026 | 小鼠 GI 四区 | Visium + Stereo-seq 总 RNA（原位 polyA 捕获微生物） | 宿主-微生物空间图谱
- 主图序列：Fig1 原位 polyadenylation 原理与流程 → Fig2 Visium 四肠区细菌 RNA+宿主空间图 → Fig3 Stereo-seq 宿主+细菌属高分辨映射（物种-面积曲线） → Fig4 肿瘤-微生物界面
- 可借鉴点：宿主-病原共检测空间图、物种-面积曲线、肿瘤-微生物界面图——微生物空间生物学专属图型

## C15 生殖/母胎
### P1. Single-cell spatiotemporal dissection of the human maternal-fetal interface
- Nature 2026 | 人多孕周妊娠组织 | snRNA + snATAC + 亚微米 Stereo-seq + CODEX | 多组学时空图谱
- 主图序列：Fig1 跨孕周多组学总览（母/胎基因型拆分+EVT GRN） → Fig2 亚微米空转全景（niche 社群+距离分箱+内皮状态 pseudotime） → Fig3 CODEX 验证螺旋动脉内皮级联 → Fig4 滋养层发育双分支轨迹+空间定位 → Fig5 蜕膜基质亚型+侵袭实验
- 可借鉴点：距离分箱空间统计与 CODEX 状态级联验证；母/胎基因型拆分是 MFI 标配
### P2. An integrated single-cell reference atlas of the human endometrium
- Nature Genetics 2024 | 人 63 供体 | sc/snRNA + Visium + smFISH | 参考图谱
- 主图序列：Fig1 月经周期协调细胞图谱 → Fig2 上皮时空（Visium+多重 smFISH） → Fig3 基质异质性与周期 crosstalk（cell2location） → Fig4 修复/再生 L-R 与巨噬细胞 → Fig5 内异症 niche（fGWAS 遗传归因）（+14 ED）
- 可借鉴点：月经周期时序 beeswarm 与 Visium+cell2location 去卷积；fGWAS 细胞类型遗传力归因收尾
### P3. Single-cell profiling of the human endometrium in polycystic ovary syndrome
- Nature Medicine 2025 | 人 PCOS ± 干预 | snRNA + Stereo-seq | 疾病+干预
- 主图序列：Fig1 PCOS 单核+空间 profiling → Fig2 上皮时空与治疗逆转 → Fig3 基质逆转 → Fig4 免疫/内皮逆转 → Fig5 CellChat crosstalk 与空间共表达 → Fig6 GWAS 关联+代谢指标相关
- 可借鉴点：疾病→干预"逆转热图"配对设计；GWAS 细胞关联+临床代谢指标散点收官
