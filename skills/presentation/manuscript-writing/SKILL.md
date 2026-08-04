---
name: manuscript-writing
description: 论文写作（Methods / Results / Figure Legends 三种模式）。当用户要写 Methods、写 Results、写图注、写论文段落、manuscript writing、STAR Methods、figure legend 时触发。一个 skill 按 section 参数切换。
---

# Manuscript Writing (Methods / Results / Figure Legends)

**触发词**: 写 Methods / 写 Results / 写图注 / figure legend / manuscript / 论文写作 / STAR Methods

**模式**（用户指定或从上下文推断）：
- `section=methods` → 写 Methods
- `section=results` → 写 Results
- `section=legend` → 写 Figure Legends

---

## 通用规则（三种模式共享，不重复）

1. **不编造**：数据集/accession/PMID/样本量/API 参数——缺信息用 `[AUTHOR TO SPECIFY: ...]`
2. **引用支撑**：每个结论标注来源（哪张图/哪个统计/哪篇文献）
3. **关联 ≠ 因果**："associated with"，"regulates/causes" 需实验证据
4. **精确数字**：N、fold change、padj 写具体值，不写"显著增加"
5. **版本可追溯**：工具 + 版本号必须出现。**版本号必须来自实际来源**（`compat.yaml` / `pip freeze` / `sessionInfo()` 输出），禁止凭记忆填写。拿不到 → `[AUTHOR TO SPECIFY: version]`

---

## section=methods

**结构**（STAR Methods 风格）：

```
## STAR Methods

### Resource Availability
- Lead contact / Materials availability / Data and code availability

### Method Details
（按实验→分析顺序，每段一个方法）

### Quantification and Statistical Analysis
（统计检验、阈值、软件版本、重复数）
```

**规则**：
- 匹配报告指南：CONSORT（RCT）/ STROBE（观察）/ PRISMA（meta）/ ARRIVE（动物）/ TRIPOD（预测模型）
- 每个工具写：`Tool Name (version X.Y.Z; reference)`
- 参数写具体值（`mt_max=20, nFeature_min=300`），不写"standard parameters"
- 统计段必含：检验方法 + 校正方法 + 阈值 + n（biological vs technical）
- 代码可用性：GitHub repo / Zenodo DOI

---

## section=results

> **先读 `references/story_builder.md`** —— Results 段落顺序 = 故事叙事弧（story_builder §2 Step 5）。

**结构**（每个 Figure 一段）：

```
Figure N 的标题（一句话 main finding，不是 "Figure N. Analysis of..."）

[数据描述] To investigate..., we performed... (n=X samples, Y cells).
[观察] We identified... (Fig. NA, padj=Z, log2FC=W).
[对比/验证] Consistent with..., / In contrast to...,
[过渡] These results suggest... (用 "suggest"，不用 "prove/demonstrate")
```

**规则**：
- **Results ≠ Discussion**：只写"观察到什么"，不写"为什么"或"意味着什么"
- 每段对应一个 Figure（按 A→B→C 顺序描述 panel）
- 引用格式：`(Fig. 1A)`、`(Fig. 2B-C)`、`(Supplementary Fig. S3)`
- 数字带来源：`"Fibroblast fraction increased from 44.2% to 56.9% (+12.7pp; Fig. 1B, padj=3.2e-41)"`
- 无显著差异时写 "No significant difference was observed (padj=0.34)"——**不编趋势**
- 不确定处用占位：`[CITE: relevant literature]`、`[AUTHOR TO VERIFY: exact n]`

---

## section=legend

**结构**（CNS 6 段式）：

```
**Figure N | 标题句**（一句话 main finding，无引用）

**(a)** Panel A 描述：什么图 + 轴含义 + 颜色/大小编码。
**(b)** Panel B 描述：...
...

统计声明：Error bars represent [SD/95% CI]; n = X biological replicates;
P values from [test name] with [correction]; *P<0.05, **P<0.01, ***P<0.001.

缩写/符号定义：FC, fold change; ns, not significant; ...
```

**规则**：
- **自洽**：不读正文，只看 Figure + Legend 能完全理解
- 标题句是 finding（"Fibroblast quiescent rewiring drives POP"），不是描述（"UMAP of cell types"）
- 每个 panel 用 **(a)(b)(c)** 小写加粗（Nature）或 **A/B/C**（Cell）——跟目标期刊走
- 统计块必含：error bar 类型 + n + 检验方法 + 校正 + 星号定义
- 不写方法细节（那是 Methods 的事）——"as described in Methods"

---

## 输出格式

```markdown
## [Section 标题]

[正文内容]

---
Metadata:
- section: methods | results | legend
- target_journal: Nature | Cell | Science | other
- figures_referenced: [Fig.1, Fig.2, ...]
- unresolved: [AUTHOR TO SPECIFY 列表]
```
