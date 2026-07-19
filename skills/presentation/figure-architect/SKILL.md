---
name: figure-architect
description: 单细胞/空转文章主图（main figure）深度设计——从一堆分析结果汇总→提炼文章逻辑脊柱→设计 panel 顺序与内容→构建前审查美观/逻辑/统计严谨度→产出 outline.json 交付物。当用户要设计主图、figure 1、article main figure、figure narrative、文章逻辑、panel 规划、汇总结果成图、深度思考主图时触发。不画单图（走 visualization/omicverse-plotting），不拼图（走 visualization/multi-panel-figures），只做"主图整体设计与审查"。
---

## When NOT to use this skill
- 单张图怎么画（UMAP/volcano/heatmap）→ `visualization/omicverse-plotting`
- 已有分图拼成 6-panel A-F → `visualization/multi-panel-figures`（拼图工具）
- 写 Results 文字叙述 → `presentation/results-writer`（本 skill 产出 outline.json 给 results-writer 用）
- 画机制图/流程图/示意图 → `visualization/scientific-schematics`
- 立项阶段的 figure 规划（分析前） → `single-cell/research-planner`（本 skill 是分析后）
- 组会/lab meeting PPT → `presentation/scientific-slides`

# Figure Architect — 主图深度设计

**核心原则**：主图不是"分析结果的罗列"，而是**一句话中心结论的可视化论证**。每个 panel 必须服务于中心结论；删掉任何一个 panel，论证链就断 = 它存在的理由；删掉任何一个 panel 论证链仍完整 = 它是冗余，应砍。

这个 skill 在分析全部完成后、拼图前运行。输入是一堆分析结果（h5ad/DE 表/SVG 表/通讯表/figure 草图），输出是一份 `outline.json`（panel 设计规范），交给 `visualization/multi-panel-figures` 拼图 + `presentation/results-writer` 写 Results 文字。

## 工作流：4 步深度思考（按顺序，不可跳）

### Step 1 — 汇总所有分析结果（inventory）

先把所有已有结果列出来，**不评判，只清点**：

```yaml
# outline.json 的 inventory 段（你产出，不交给下游）
inventory:
  data:
    - sc_annotated.h5ad          # QC+cluster+annotate 全流程结果
    - de_pseudobulk/             # 各 cell type × condition DE 表
    - svg_moranI.csv             # 空间变异基因
    - ccc_liana.csv              # 细胞通讯
    - spatial_deconv.h5ad        # 空转去卷积
    - trajectory_cellrank.h5ad   # 轨迹/命运
  figures_draft:                  # 已画的单图草稿
    - umap_celltype.png
    - dotplot_markers.png
    - volcano_fibroblast.png
    - spatial_celltype.png
    - proportion_bar.png
    - ccc_heatmap.png
  key_findings:                   # 你从数据里看到的关键发现（一句话一条）
    - "Fibroblast 比例 POP 56.9% vs Normal 44.2%（+12.8pp）"
    - "Quiescent_1 → Quiescent_2/3 内部重塑（padj<1e-40）"
    - "SMC 中间态两极化而非单向转换"
    - "M2 巨噬 +16.7pp（复现原文）"
    - "CXCL12-CXCR4 是成纤维-免疫通讯核心轴"
```

> **诚实清单**：key_findings 必须来自实际数据，不能编。每条要有数据出处（哪张图/哪个统计支撑）。元方法论原则 ①。

### Step 2 — 提炼文章逻辑脊柱（main message → narrative spine）

**这是最关键的一步——决定了整篇文章的命运。**

#### 2a. 写一句话 main message（≤30 词）

用一句话陈述"这篇文章证明了什么"。**写不出这句话 = 还没想清楚**——继续想，不要进 Step 3。

```
❌ 差的 main message（描述性，无论证）：
   "We performed single-cell analysis of POP and found changes in cell types."

✓ 好的 main message（论证性，含机制）：
   "POP is driven by fibroblast quiescent-subtype rewiring (not classic myofibroblast),
    with SMC intermediate-state bipolarization and M2 macrophage amplification forming
    a self-reinforcing fibrosis-inflammation loop."
```

**自检**：这句话是否——
- [ ] 包含**核心机制**（不是"发现 X 变了"，而是"X 通过 Y 机制导致 Z"）
- [ ] **可被证伪**（不是"我们表征了细胞异质性"这种无法证伪的话）
- [ ] **有数据支撑**（每关键词都能对应到一个 panel）

#### 2b. 从 main message 反推 narrative spine（论证链）

把 main message 拆成 3-6 个**必须论证的逻辑节点**，每个节点 = 一个 panel：

```
main message: POP = 成纤维亚群重塑 + SMC 两极化 + M2 极化的纤维化-炎症正反馈

narrative spine（论证链，每个 = 一个 panel）：
  节点1（背景）:  阴道壁细胞图谱（"有哪些细胞"）           → panel A: UMAP + 比例
  节点2（现象1）: 成纤维扩增 + 内部重塑（"哪群变了"）       → panel B: 亚群 UMAP + 比例
  节点3（机制1）: Quiescent_1→2/3 转向 + 非 myofibroblast → panel C: 状态评分 + DE 火山
  节点4（现象2）: SMC 中间态两极化（"深化原文"）            → panel D: 表型评分 + 散点
  节点5（机制2）: M2 极化（复现原文 + 空间验证）            → panel E: 极化比例 + 空间
  节点6（整合）:  CXCL12-CXCR4 通讯轴连接成纤维-免疫       → panel F: 通讯热图 + LR 图
```

> **冗余判定**：如果某个节点删掉，main message 仍能成立 → 它不属于主图（移到 supplementary）。CNS 主图 ≤6 panel，超过 = 论证不够精炼。

#### 2c. 检查逻辑链完整性

- [ ] **背景 → 现象 → 机制 → 整合** 的推进顺序是否成立？
- [ ] 每个节点是否**只依赖前面已建立的节点**（不能引用后面才讲的）？
- [ ] 有没有**循环论证**（节点5 依赖节点6，节点6 又依赖节点5）？
- [ ] 有没有**未论证的跳跃**（从节点2 直接到节点5，中间机制缺失）？

### Step 3 — 设计每个 panel（spec → outline.json）

为每个 panel 写规范，**包含审查维度**（在 Step 4 用）：

```json
{
  "panels": [
    {
      "id": "A",
      "narrative_role": "背景：建立阴道壁细胞图谱",
      "chart_type": "UMAP embedding + 比例堆叠柱",
      "data_source": "sc_annotated.h5ad, obs['celltype']",
      "take_home": "10 类细胞，Fibro + SMC 主导",
      "completeness_check": "N 标注 / 统计检验 / 配色一致性",
      "must_show": ["N=91725", "10 cell types", "Fibro 44→57%"]
    },
    {
      "id": "B",
      "narrative_role": "现象1：成纤维扩增 + 内部重塑",
      "chart_type": "亚群 UMAP + per-sample 比例柱",
      "data_source": "fibroblast_subclustered.h5ad",
      "take_home": "Quiescent_1→2/3 重塑，非 myofibroblast 扩增",
      "completeness_check": "padj 标注 / per-sample 散点 / 卡方检验声明",
      "must_show": ["8 fibro subtypes", "Quiescent 内部重塑 padj<1e-40", "Myofibroblast 未扩增"]
    }
    // ... C/D/E/F
  ],
  "panel_order_rationale": "A 背景 → B-C 成纤维机制 → D SMC 机制 → E 免疫 → F 通讯整合（成纤维到免疫的因果闭环）",
  "main_message": "POP = 成纤维亚群重塑 + SMC 两极化 + M2 极化的纤维化-炎症正反馈"
}
```

#### panel chart_type 选择（参考 `references/figure_design.md` §1）

| narrative role | 推荐 chart type | 来自哪个 skill 画 |
|---|---|---|
| 图谱/分群总览 | UMAP embedding + 比例堆叠柱 | omicverse-plotting |
| marker 验证 | dotplot（≤6 type × ≤20 marker）或 heatmap（>20 marker） | omicverse-plotting |
| 组成变化 | per-sample 散点 + 比例柱（不用 pie） | omicverse-plotting |
| DE 结果 | volcano + top genes（padj + lfcShrink） | omicverse-plotting |
| 轨迹/命运 | PAGA + UMAP pseudotime（绝不强画线性曲线） | omicverse-plotting / rna-velocity |
| 空间验证 | H&E + expression overlay（统一 color scale） | omicverse-spatial |
| 通讯 | circle/chord（≤8 type）或 heatmap | omicverse-plotting |
| 机制示意 | schematic（最后一张，整合用） | scientific-schematics |

### Step 4 — 构建前深度审查（mandatory gate）

**拼图前必跑的 5 类审查**。任何一类 FAIL → 不许进 multi-panel-figures，先修。

#### 4a. 逻辑审查（logic）
- [ ] **Main message 一句话成立**（Step 2a 自检通过）
- [ ] **每个 panel 都服务 main message**（删任一论证链断）
- [ ] **panel 顺序 = 阅读顺序**（陌生人按 A→B→C 能跟上，不跳跃）
- [ ] **无循环论证 / 无未论证跳跃**
- [ ] **背景 → 现象 → 机制 → 整合** 的层级递进成立

#### 4b. 美观审查（aesthetics，参考 `references/figure_aesthetics.md` + `figure_layout.md`）
- [ ] **全图配色一致**（同一 cell type 在所有 panel 同色——建 cell_type → color 映射复用）
- [ ] **字号层级统一**（参考 figure_layout.md 字号缩放表）
- [ ] **无 chartjunk**（Tufte：去冗余边框/网格/3D）
- [ ] **panel label A/B/C** 加上（omicverse 无 API，inline `ax.text`）
- [ ] **共享 legend/colorbar 合并**（同 scale 不重复）

#### 4c. 统计严谨审查（rigor，参考 `references/figure_design.md` §3 + `references/preoutput_checklist.md`）
- [ ] **每个定量 panel 标 N**（bio replicate vs cell 数，区分）
- [ ] **error bar 类型声明**（SD / 95% CI，不用 SEM 单独）
- [ ] **padj 而非裸 p**（DE / 富集）
- [ ] **关联 ≠ 因果**用词（"associated with"，"regulates"需实验证据）
- [ ] **个体数据点显示**（n<30/group 时）

#### 4d. 冗余审查（redundancy）
- [ ] **无两个 panel 讲同一件事**（如同时有 violin + dotplot 显示同一 marker → 砍一个）
- [ ] **无 supplementary 该有的内容塞进主图**（细节/qc/敏感性分析→ supp）
- [ ] **panel 数 ≤6**（CNS 主图惯例；>6 = 论证不够精炼或塞太多）

#### 4e. 可读性审查（readability，目标读者视角）
- [ ] **3 秒抓到 take-home**（每个 panel 有明确视觉焦点）
- [ ] **图注自洽**（不读正文能懂——figure_design.md §5 结构）
- [ ] **缩放后字仍可读**（最终印刷尺寸下 ≥6pt）
- [ ] **跨 panel 比较 facilitat**（如比较 condition，所有 panel 用同一 condition 配色 + 同一顺序）

#### 审查报告模板

```
=== Figure Architect 审查报告 ===
Main message: <一句话>
Panel 数: 6 (A-F)
[logic]    ✅ PASS / ❌ FAIL: <详情>
[aesthetics] ✅ / ❌: <详情>
[rigor]    ✅ / ❌: <详情>
[redundancy] ✅ / ❌: <详情>
[readability] ✅ / ❌: <详情>
判定: <全部 PASS → 可交付 multi-panel-figures；任一 FAIL → 列出修复项>
```

## 交付物

审查全 PASS 后，产出 `outline.json`（如 Step 3 格式），交给：
- **`visualization/multi-panel-figures`**：按 outline 拼 6-panel A-F（panel_order + chart_type + data_source）
- **`presentation/results-writer`**：按 narrative_spine 写 Results 文字（每段对应一个 panel）
- **`presentation/figure-legend-writer`**：按 panel spec 写自洽图注

> **不要自己拼图**——本 skill 只设计，拼图走 multi-panel-figures（它有几何 QA）。

## Prerequisites (where it comes from)

- **全部分析已完成**：QC → cluster → annotate → DE → 通讯 → 轨迹 → 空转去卷积（各 skill 产出）
- **已有单图草稿**（UMAP/火山/dotplot 等，来自 `visualization/omicverse-plotting`）
- **关键发现清单**（你从数据里看到的关键现象，一句话一条 + 数据出处）
- **必读**：`references/figure_design.md`（图型选择 + 信息层级 + 统计可视化）+ `references/figure_aesthetics.md`（技术规范）+ `references/figure_layout.md`（组合布局）

## When to leave this skill (where to go)

- 拼主图 → `visualization/multi-panel-figures`（带 outline.json）
- 写 Results 文字 → `presentation/results-writer`（带 narrative_spine）
- 写图注 → `presentation/figure-legend-writer`（带 panel spec）
- 画机制示意图（panel F 整合用） → `visualization/scientific-schematics`
- 做 talk PPT 嵌入主图 → `presentation/scientific-slides`

## Key pitfalls

- **不写 main message 就开始设计 panel** = 没想清楚就动手，必然做出"分析结果罗列"而非"论证"。Step 2a 是 gate，写不出就停。
- **panel 数 >6** = 论证不够精炼，或塞了 supplementary 该有的内容。砍到 ≤6。
- **循环论证 / 未论证跳跃** = 逻辑链断了，审稿人会抓。Step 2c 专门查这个。
- **同一 cell type 跨 panel 不同色** = 读者无法跨 panel 比较。建 cell_type → color 映射，全局复用。
- **跳过 Step 4 审查直接拼图** = 把"分析结果罗列"当主图交差。审查 gate 不可跳。
- **把本 skill 当拼图工具** = 拼图走 multi-panel-figures，本 skill 只设计 + 审查。
- **main message 描述性而非论证性** = "我们发现了 X 变化"是描述；"X 通过 Y 机制导致 Z"是论证。CNS 要论证。
- **编造关键发现** = key_findings 必须来自实际数据，每条有出处。元方法论原则 ①。
