# Story Builder — 从分析结果到生物学叙事

> 分析跑完了（QC/聚类/注释/DE/通讯/轨迹/空间），但怎么把这些表格和数字变成一个**有逻辑的生物学故事**？本文件是"结果→故事"的转化方法论。
>
> **谁读这个**：分析完成后、开始画图/写论文前。research-planner 设计时预读（知道故事该怎么讲影响实验设计）；figure-production 出图时读（决定每张 panel 论证什么）。

---

## 1. 故事的三个层次

一篇 CNS 单细胞论文的生物学故事有三层，从上到下：

```
Layer 3 (宏观): 疾病/现象的因果假说
  "POP 的纤维化是由成纤维细胞静息态重塑驱动的，而非经典肌成纤维细胞活化"

Layer 2 (中观): 细胞层面的现象 + 分子层面的机制
  "Quiescent_1 亚群向 Quiescent_2/3 转换，CXCL12 上调，招募 M2 巨噬"

Layer 1 (微观): 数据层面的证据
  "Fibro 比例 44%→57% (padj<1e-40); Quiescent_1→2 DE 基因富集 TGFβ 通路;
   CXCL12-CXCR4 通讯 score 在 Fibro-Mac 对中最高"
```

**故事构建 = 从 Layer 1（数据）往 Layer 3（假说）走，每一步都要有证据支撑。**
LLM 最常犯的错误：直接从 Layer 1 跳到 Layer 3（"CXCL12 上调 → CXCL12 驱动疾病"），跳过了 Layer 2 的中间论证。

---

## 2. 从结果到故事的五步法

### Step 1: 清点发现（What did I find?）

把所有分析结果列成"发现清单"，**不加解读，只陈述数据**：

```
发现 1: Fibroblast 占比 Normal 44% vs POP 57% (+13pp, padj<1e-40)
发现 2: Fibroblast 内部 Quiescent_1 减少, Quiescent_2/3 增加
发现 3: Quiescent_2/3 DE 基因: COL1A1↑, CXCL12↑, PDGFRB↑ (padj<0.001)
发现 4: SMC 出现中间态群体 (表达 ACTA2+MYH11 混合标记)
发现 5: CXCL12-CXCR4 是 Fibro→Mac 通讯最强轴 (score=0.85)
发现 6: 空间上 CXCL12+ Fibro 与 M2 Mac 在纤维化区域共定位
发现 7: M2 巨噬比例 POP +16.7pp (复现原文)
```

> **纪律**：每条发现必须有数据出处（哪张图/哪个统计）。没有出处的发现是假说不是发现。

### Step 2: 找因果链（How do findings connect?）

把发现按因果顺序排列，找出 **"因为 A → 所以 B → 导致 C"** 的链条：

```
链条 1 (纤维化主线):
  发现2 (亚群重塑) → 发现3 (分子变化: CXCL12↑) → 发现5 (通讯: CXCL12→Mac)
  → 发现6 (空间验证: 共定位) → 发现1 (比例变化: Fibro 扩增)

链条 2 (免疫轴):
  发现3 (CXCL12↑) → 发现5 (CXCL12-CXCR4 通讯) → 发现7 (M2 扩增)

链条 3 (SMC 副线):
  发现4 (SMC 中间态) → 独立于主链，可能是次要发现
```

> **纪律**：因果链里每一步都必须有**独立证据**。不能"因为 A → 所以 B"而没有 B 的数据。只有 A 的数据 → "A is associated with B"（关联），不是 "A causes B"（因果）。

### Step 3: 提炼主结论（What is the one sentence?）

从因果链中提炼出**一句话主结论**（Layer 3）：

```
❌ 差的主结论（描述性）: "我们发现了 POP 组织的细胞异质性"
✓ 好的主结论（论证性）: "POP 的纤维化由成纤维细胞静息态重塑驱动
   (非肌成纤维细胞活化)，CXCL12-CXCR4 轴连接纤维化-免疫正反馈"
```

**自检**：
- 主结论是**可被证伪的**吗？（"发现异质性"不可证伪；"静息态重塑驱动"可）
- 主结论的**每个关键词都有 panel 支撑**吗？
- 主结论是否**区别于已知**？（如果与已发表结果完全一样，那你的贡献是什么？）

### Step 4: 组织 Figure 叙事（Which panel tells what?）

把因果链映射到 Figure/Panel：

```
Figure 1 (atlas):
  A: UMAP 全景 → "有哪些细胞" (发现 1 的基础)
  B: 比例柱 → "谁变了" (发现 1)
  C: marker dotplot → "身份可信" (支撑)

Figure 2 (机制: 纤维化主线):
  A: Fibro 亚群 UMAP → "内部重塑" (发现 2)
  B: 比例变化 → "定量" (发现 2)
  C: volcano → "分子机制" (发现 3)
  D: trajectory → "方向性" (发现 2 补充)

Figure 3 (机制: 通讯+空间):
  A: CCC heatmap → "谁跟谁说话" (发现 5)
  B: CXCL12-CXCR4 bubble → "具体哪条轴" (发现 5)
  C: 空间 overlay → "物理邻近" (发现 6)
  D: M2 比例 → "免疫后果" (发现 7)
```

**每张 Figure 只讲一个机制**。两个机制塞一张 = 聚焦不够。

### Step 5: 写出叙事弧（What is the story arc?）

论文的叙事弧 = 因果链的时间/逻辑顺序：

```
开头 (背景): 这个组织/疾病的细胞组成是什么？→ Figure 1
发展 (现象): 哪个细胞群发生了变化？变化多大？→ Figure 2A-B
深入 (机制): 变化的分子基础是什么？→ Figure 2C-D
转折 (整合): 这个变化如何影响其他细胞？→ Figure 3A-B
验证 (空间): 这些相互作用在组织里真的发生吗？→ Figure 3C
收束 (结论): 所以这个疾病的驱动机制是什么？→ Figure 3D + 模型图
```

---

## 3. 单细胞结果的常见误读（LLM 高发）

| 数据结果 | ❌ 误读（过度推断） | ✓ 正确解读 |
|---|---|---|
| Cluster A 的 marker gene X 高表达 | "X 是 A 的标记基因" | X 在 A 中富集（不代表 X 只在 A 表达或 X 定义 A） |
| Condition 组 Cluster A 比例增加 | "Condition 导致 A 扩增" | A 的比例在 Condition 组更高（关联，非因果；可能是采样偏差） |
| Ligand L 在 CellType1 高表达，Receptor R 在 CellType2 高表达 | "L-R 信号介导 1→2 通讯" | L-R 共表达提示潜在通讯（需蛋白/空间/功能验证） |
| Pseudotime: A → B → C | "A 分化为 B 再分化为 C" | 沿 pseudotime 的排序：A→B→C 是计算排序（需实验验证是否为真实分化） |
| SCENIC+ 发现 Regulon R 在 Cluster A 活跃 | "R 驱动 A 的细胞命运" | R 的活性在 A 中富集（关联，非因果；需 KO/OE 验证） |
| DE 分析发现 Pathway P 富集 | "P 通路被激活" | P 的基因集在差异基因中过表达（可能是少数基因驱动） |

---

## 4. 从"一堆结果"到"一个故事"的检查清单

- [ ] **每条发现都有数据出处**（图/统计/数字）
- [ ] **因果链每一步都有独立证据**（不能跳过中间环节）
- [ ] **主结论可被证伪**（不是"我们表征了异质性"）
- [ ] **每张 Figure 只讲一个机制**（两个机制 = 两张 Figure）
- [ ] **Panel 顺序 = 阅读顺序**（陌生人按 A→B→C 能跟上）
- [ ] **措辞区分关联与因果**（"associated with" vs "regulates"）
- [ ] **知道自己的局限**：scRNA 只测 mRNA → 蛋白层面需验证；pseudotime 不是时间；CCC 是假设不是机制
- [ ] **故事有"新"的东西**：复现原文 + 新发现 = 有价值的论文；只复现 = 不够

---

## 5. 与 skill 其他部分的关系

```
research-planner: 设计时预读本文 → 知道"这个故事需要几组数据、什么验证"
                  （分析前：决定做什么实验能支撑想要的故事）

omicverse-pipeline: 跑完后读本文 → 把 §2-§9 的结果组织成因果链
                    （分析后：结果解读）

figure-production: 出图时读本文 → Step 1 大框架的 panel 列表来自 Step 4
                   （画图：每个 panel 论证什么）

manuscript-writing: 写作时读本文 → Results 段落顺序 = Step 5 叙事弧
                    （写作：文字组织）
```
