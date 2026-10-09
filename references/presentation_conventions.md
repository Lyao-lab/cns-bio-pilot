# Presentation Conventions — CNS 2025-26 结果展示规范（单一权威页）

> **来源**：2026-10-10 调研，7 篇逐句核实（Nature 胎心 T21 / 肝图谱 / PsychAD 脑、Nat Methods VIMA、
> Nat Genet 皮肤 MERFISH、Commun Biol 小鼠心〔对照档〕、Cell PDAC〔摘要级〕；原始报告
> `/home/longyao/data/lit_surveys/20261010_presentation_conventions.md`）。
> **谁读**：写 figure caption / 组 panel / 标统计 / 画误差棒 / 展示空间证据时（figure-production、
> manuscript-writing、deck 组装）。措辞词汇表在 `analysis/stats_convention.md`（本页管**格式与呈现**，
> 那页管**措辞与口径**——互补不重叠）。

## 1. 统计量报告格式（进 caption，不只进方法段）

- 检验三元组句式：**检验名 + two-sided/two-tailed + 精确值**，直接写 figure caption。例：*(two-sided Mantel test with Spearman's correlation and 999 permutations, r = 0.76, P = 0.01)*
- **P 斜体大写**；小数写满（P = 0.00375）；<10⁻³ 转科学计数（P = 2.05 × 10⁻⁸）；置换检验按次数报分辨率上限（999 次 → 只能写 P < 0.001）。⚠️ 篇内 main/ED 图 P 大小写会漂移——投稿前统一。
- 效应量必配区间：`OR = 1.94, 95% CI 1.47–2.54`（en-dash）或 `95% CI 0.51 to 0.95`——篇内统一一种。
- 相关系数：Spearman 优先写 **ρ**（或篇内统一 r/R），符号与检验名同句首现；**FDR/q 与 P 分开**，星号可绑 FDR（*FDR < 0.05）。
- n 三要素：**数值 + 单位词（donors/samples/sections/spots）+（能给则给）供体 ID**；样本与供体两个 n 都报（"n = 109 samples from n = 19 donors"）。

## 2. 重复与误差

- 每个含箱线/误差的 panel 在 caption **逐 panel 写全**：中线/箱/whisker 规则（1.5×IQR 或 min–max）/outlier 判定。⚠️ 同一篇内定义可不同——全局默认不安全。
- 误差棒主流：**供体级 bootstrap 的 s.d.**（组间比较）+ **s.e.m. 阴影带**（空间连续曲线/拟合）；mean±SD+t 检验是低档口径。嵌套数据两级点：小点=技术单元、大点=生物学重复、横线=总均值；检验在生物学层。
- 点身份句式：*"Each dot represents one biologically independent donor (n = …)"*。
- 方法段固定诚实三句：样本量未预设 / 是否随机化 / 是否盲法。

## 3. 空间证据的成对呈现（铁律）

- 每张空间着色图**同 figure 内必配定量伴随面板**：分组箱线 / 分 bin 均值±s.e.m. 曲线 / 散点+拟合+95%CI 带——只有空间图无定量面板在旗舰档零先例。
- **n=1 三件套**：*"One section from one donor is shown"* + 逐 section n + 跨供体一致性句（含供体 ID）。
- 空间交互显著性：置换检验（报次数+阈值），图上用**描边/圈出**编码显著（"outlined circles denote significant interactions, empirical permutation P < 0.1; 1,000 permutations"）。
- 跨时点逐 stage 报 n（"5w4d, n = 163; 7w4d, n = 1,210"），时间轴符号记供体数。
- "representative" 必须跟 n 与供体 ID——裸 representative 不合格。

## 4. 多 panel 组织

- 单张 main fig **5-9 panel**、全文 4-7 张；总结 schematic 压轴（图尾 panel）。
- Fig.1 固定结构：设计 schematic（一次列全所有 n）→ 队列 → atlas 总览 → QC（QC 可下沉）。
- 降级线：QC/扩展 marker/单供体验证/平台对比 → Extended Data；缩写字典与样本元数据 → Supplementary Table（caption 显式指路）。

## 5. Caption 写法

- 长度 **150-400 词**，每 panel 1-3 句；统计方法句进 caption；缩写首现即定义或末尾集中 key。
- 色标语义逐 panel 用 *"The hue indicates…"* 句式；schematic 注明制作工具署名；Nature 每 panel 留 Source data 位。
- **统计数值避免直印图面**（"p=0.0015" 印在 panel 上是 Prism 低档口径）——进 caption；仅全局检验单值可 overlay 图上。

## 6. 模型图与推导量

- 机制总结用**专业插画**（BioRender 级，逐图署名），非简笔；方法学流程图可用几何简图。
- 色标裁剪/截断必须声明：*"clipped between −10 and 10" / "−log₁₀[FDR] (clipped at 5)"*；阈值类分析把全部阈值写进 caption。

## 7. 增强项自识（超出 CNS 现行惯例——用时可保留但知道是增强）

- **null band 画进图**：未核实到 main fig 先例（null 以置换次数+经验 P 数字呈现）——我们的 lollipop null_band / 建议中的 null band 图属增强，慎用、用则 caption 说明。
- **"DERIVED/assumed" 大写标签**：未见 CNS 惯例——我们 fig3 S15 的 DERIVED 标签是自明增强，可保留但勿误当 CNS 标配。
- 我们的 fig1 deck 结构（设计→队列→atlas→QC→空间）与规范 4 的 Fig.1 模式吻合；S07/S08 空间+定量成对与规范 3 吻合——现行做法已被本轮调研反向验证。
