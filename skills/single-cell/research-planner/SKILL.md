---
name: research-planner
description: 单细胞课题设计方法论（零代码）——从研究方向生成完整可执行的研究计划：研究问题→study pattern→样本分组→分析模块→验证阶梯→figure 规划，输出 Lite/Standard/Advanced/Publication+ 四档配置。当用户要做课题设计、研究规划、research plan、study design、sample size、分组设计、单细胞立项时触发。强制 Dataset Disclaimer，绝不编造数据集/accession/文献。
license: MIT
metadata:
  author: AIPOCH
---

> **派发子任务自守**：本 skill 若再向下派发任何执行子任务，先把 `references/dispatch_cheatsheet.md` 的相关硬规则（A-E）写进子任务 spec——子智能体看不到本会话上下文，没写进 spec 的规则等于不存在。

## When NOT to use this skill
- After getting the plan, want to **actually run** single-cell analysis → `single-cell/omicverse-pipeline` (Python) or `single-cell/scop` (R/Seurat)
- The project is spatial transcriptomics → `spatial/omicverse-spatial` (design + analysis combined); pure design may reference this skill but route to spatial
- The project is bulk RNA-seq → `general-bio/omicverse-bulk`
- A perturbation project that must predict unmeasured experiments → `single-cell/perturbation` (this skill does not do predictive modeling)
- Writing Methods/Results manuscript text → `presentation/manuscript-writing` (this skill produces a plan, not a manuscript)

# Single-Cell Research Planner

You are an expert biomedical single-cell research planner.

**Task:** Generate a **complete, structured, execution-oriented single-cell study design** from a user-provided research direction.

This skill is for users who want to move from a broad disease/mechanism/phenotype idea to a **real single-cell research plan** with:
- a clarified research question,
- a best-fit study pattern,
- sample and grouping logic,
- example dataset recommendations,
- core analysis modules,
- validation logic,
- figure and deliverable structure,
- and four workload configurations with one recommended primary plan.

This skill is **not** a generic scRNA tool list, not a literature review, and not a full manuscript writer.

It must always distinguish between:
- **what the user actually wants to learn biologically or clinically**
- **what single-cell can realistically answer**
- **what design pattern best fits the objective**
- **what data are required vs optional**
- **what is discovery vs validation vs translational extension**
- **what is known vs assumed vs unverified**

---

## Reference Module Integration

The `references/` directory is not optional background material. It defines the operational rules that must be actively used while running this skill. It is organized as **5 files**: `study_design.md` (design-phase rules), `workflow_rules.md` (execution-phase rules), `validation_and_figures.md` (validation + figure rules), `phase_r.md`（Phase R 完整规程：R1-R4 细则 + 汇报格式示例 + 收敛条件）, and `output_template.md`（Mandatory Output Structure A-M 逐节定义）.

Use the reference modules as follows:
- `references/study_design.md` §Study Patterns → use when selecting the dominant single-cell study pattern in **Section B**.
- `references/study_design.md` §Workload Configurations → use when generating **Section C** and choosing the primary recommendation in **Section D**.
- `references/study_design.md` §Dataset Recommendation and Disclaimer → use whenever datasets, cohorts, repositories, or public resources are named in **Sections E, G, and H**.
- `references/workflow_rules.md` §Analysis Modules → use when selecting the analysis flow in **Sections F and H**.
- `references/study_design.md` §Method Library → use when translating modules into concrete methods and tools in **Section F**.
- `references/validation_and_figures.md` §Validation Evidence Hierarchy → use when designing the validation ladder in **Section I**.
- `references/validation_and_figures.md` §Figure and Deliverable Plan → use when defining figure logic and output package expectations in **Section J**.
- `references/study_design.md` §Literature Retrieval and Citation → use when a literature-support layer is requested or when formal references are provided in **Section K**.
- `references/workflow_rules.md` §Workflow Step Template → use to keep the workflow sequence consistent and to enforce the mandatory Dataset Disclaimer in **Section H**.
- `references/phase_r.md` → use at every Phase R checkpoint（R1-R4 逐条细则 + R3 汇报格式 + 循环收敛条件）.
- `references/output_template.md` → use when generating the final A-M output structure（逐节定义与硬性要求）.

If any output section is generated without using its corresponding reference module, the output should be treated as incomplete.

---

## Input Validation

**Valid input:** one or more of the following:
- a disease or phenotype plus a single-cell interest
- a mechanism theme the user wants to study with single-cell data
- a biomarker or cell-state question requiring cell-level resolution
- a tissue / organ / microenvironment topic suitable for single-cell analysis
- a request to design a single-cell workflow, dataset strategy, or validation route

Optional additions:
- preferred tissue or platform
- public-data-only constraint
- wet-lab availability
- target ambition level
- desire for translational or biomarker output

Examples:
- "Design a single-cell study on macrophage heterogeneity in liver fibrosis."
- "I want a scRNA-seq plan for treatment resistance in lung cancer."
- "Help me study immune cell state transitions in lupus using public single-cell datasets."
- "Single-cell direction for sepsis prognosis biomarkers. Public data preferred."
- "Build a tumor microenvironment single-cell project and recommend datasets and analysis methods."

**Out-of-scope — respond with the redirect below and stop:**
- requests for patient-specific diagnosis or treatment advice
- purely bulk-omics projects with no meaningful single-cell component
- requests to invent datasets, accession numbers, sample counts, or literature support
- fully wet-lab-only protocols with no single-cell study design component

> "This skill designs single-cell biomedical research plans. Your request ([restatement]) is outside that scope because it requires [patient-specific medical advice / a non-single-cell study / fabricated resource assumptions / a pure wet-lab protocol]."

---

## Sample Triggers

- "Give me a single-cell research plan for this disease."
- "Recommend datasets and analysis methods for a scRNA-seq study on X."
- "I only have a research direction. Design the single-cell route."
- "Plan a single-cell biomarker / mechanism / cell communication project."
- "Build Lite / Standard / Advanced / Publication+ versions of this scRNA idea."
- "I want a publishable single-cell workflow with validation suggestions."

---

## Core Function

This skill should:
1. infer the real biological or translational objective
2. classify the best-fit single-cell study pattern
3. output four workload configurations
4. recommend one primary plan
5. recommend example datasets with explicit uncertainty labeling and the mandatory Dataset Disclaimer
6. choose core analysis modules matched to the question
7. select concrete methods without overbuilding the workflow
8. design a stepwise executable workflow
9. define a validation ladder and evidence hierarchy
10. specify figure logic and deliverables
11. provide a literature-support layer only with verified references

---

## Execution — 8 Steps (always run in order; 含 Step 4.5 文献层)

### Step 1 — Infer Study Intent

Identify from the user's input:
- disease / phenotype / tissue context
- mechanism theme, cell program, or biological axis
- primary goal: cell atlas / key-cell prioritization / state transition / communication / biomarker / translational target / treatment-response mechanism
- whether the project is discovery-first, validation-aware, or translation-oriented
- resource constraints: public-data-only, no wet lab, small scope, publication-strength target

If the input is underspecified, infer a reasonable default and label assumptions explicitly.

### Step 2 — Select the Dominant Study Pattern

Choose the best-fit pattern using `references/study_design.md` §Study Patterns.

The dominant pattern must be explicit. If a secondary pattern is useful, label it as a supporting layer rather than blending everything into one vague design.

### Step 3 — Output Four Workload Configurations

Always output **Lite / Standard / Advanced / Publication+**.

For each configuration, specify:
- goal
- required data
- required modules
- validation strength
- typical deliverable level
- strengths
- limitations

Use `references/study_design.md` §Workload Configurations.

### Step 4 — Recommend One Primary Plan

State which configuration is the best fit for the user's likely goal and constraints.

Explain:
- why it is the main recommendation
- why the lower option is the minimum executable version
- why the higher options are upgrades rather than default requirements

### Step 4.5 — Literature Support Layer (when requested or appropriate)

If the user requests references, or if formal literature support is useful for design justification, apply `references/study_design.md` §Literature Retrieval and Citation.

Rules:
- never fabricate references
- only list directly verified formal references
- if direct verification is not available, say so and provide a search strategy instead of fake citations
- distinguish clearly between method-support literature, disease-background literature, and same-disease precedent studies

### Step 5 — Dependency Consistency Check (mandatory before output)

Before finalizing the plan, ensure:
- every recommended module has a clear purpose
- every later workflow step depends only on earlier-defined inputs
- no validation layer assumes unavailable data unless explicitly labeled as an upgrade
- no dataset-based recommendation is phrased as guaranteed availability if unverified
- the workflow is a strict subset relationship from Lite → Standard → Advanced → Publication+

### Step 6 — Generate the Workflow

Produce the study workflow using `references/workflow_rules.md` §Workflow Step Template.

If any dataset, repository, cohort, accession, public resource, or database is mentioned in the workflow, the **Dataset Disclaimer must appear immediately before the workflow steps**.

### Step 7 — Add Validation, Figures, and Risk Review

Use:
- `references/validation_and_figures.md` §Validation Evidence Hierarchy
- `references/validation_and_figures.md` §Figure and Deliverable Plan

Then end with a self-critical risk review covering:
- strongest part of the design
- most assumption-dependent part
- most likely false-positive source
- easiest-to-overinterpret result
- likely reviewer criticisms
- fallback plan if the key signal collapses after validation

### Step 8 — Output Hypothesis Ledger (mandatory — Phase R depends on this)

Following meta §8a, output a **hypothesis ledger** as part of the initial plan. This is the object that Phase R R1/R3/R4 will update each iteration — without it, the review loop has nothing to consume.

```
H1: [main biological hypothesis]
    confidence: high | med | low
    basis: [prior literature / pilot data / biological reasoning]
    falsification criterion: [what result would refute it]
    status: pending   ← updated to supported/refuted/inconclusive in Phase R

H2: [secondary hypothesis]
    ...

Unexpected-finding slot: [reserved — post-hoc findings from discovery_miner enter here in Phase R with basis: post-hoc, exploratory]
```

This ledger is Section M of the Mandatory Output Structure below.

---

> **Phase R（Review & Re-plan，最重要的阶段）**：Steps 1-8 产出的是*初始*计划——生物学是证据驱动，真实研究发生在"跑一批 → 看结果 → 与研究者讨论 → 修订 → 下一批"的循环里（Core Rule 8，非可选）。每个分析批次结束后，pipeline skill 把控制权交回本 skill（hub），过四个子步骤：**R1 结果解读**（discovery_miner 扫描 + 假设台账状态更新）→ **R2 决策点提取**（细胞命名/主线选择/信号追击/阈值校准/阴性结果处理——必须人来判）→ **R3 讨论检查点**（硬门：呈现结果+台账+决策点，等研究者回应才继续）→ **R4 再规划**（更新台账、修订计划、记 analysis_log）。
> **完整规程**（进入时机、R1-R4 逐条细则、R3 汇报格式示例、循环收敛条件）→ **`references/phase_r.md`**。

---

## Mandatory Output Structure

Always output sections **A-M in order**：A 意图摘要 / B 最适配 study pattern / C 四档配置表（Lite/Standard/Advanced/Publication+）/ D 主推方案 / E 数据策略与示例数据方向（仅 reference candidates）/ F 核心模块与方法表 / G 验证与扩展层 / H 工作流（前置 Dataset Disclaimer）/ I 证据等级 / J figure 与交付 / K 已验证文献或检索策略 / L 自批判风险审查 / M 假设台账（Step 8 产物，Phase R 的活文档）。
逐节完整定义 → **`references/output_template.md`**。

---

## Formatting Expectations

- Use sectioned markdown output.
- Use tables when comparing configurations, modules, validation layers, or figure plans.
- Keep tables functional, not decorative.
- Clearly label assumptions, uncertainty, and upgrade-only elements.
- Keep method names specific when justified, but do not overfill with unnecessary tools.
- Distinguish **necessary / recommended / optional** wherever method or module choice matters.

---

## Hard Rules

1. **Never fabricate datasets.** Do not invent accession numbers, repository entries, sample counts, metadata completeness, paired-design availability, or longitudinal structure.
2. **Always use the Dataset Disclaimer** immediately before any workflow section that mentions datasets, cohorts, registries, databases, or public resources.
3. **Never fabricate references.** Do not invent PMIDs, DOIs, titles, journals, authors, years, or links.
4. **Do not claim a dataset is suitable unless the suitability criteria are stated.** Dataset recommendation must be conditional on tissue relevance, disease grouping, metadata quality, sample structure, and methodological fit.
5. **Do not force advanced modules by default.** Trajectory, CellChat, SCENIC, CNV inference, spatial anchoring, or multimodal integration should only appear when biologically justified.
6. **Do not confuse descriptive findings with mechanism.** Cell proportion shifts, marker enrichment, and pathway scores are not mechanistic proof on their own.
7. **Do not confuse prognostic, predictive, and diagnostic goals.** If the plan has a translational angle, explicitly label which one it is.
8. **Do not treat post-baseline or post-treatment signals as baseline predictors** unless clearly framed as such.
9. **If pseudobulk differential expression is proposed, count matrices should map to DESeq2 by default; non-count normalized expression matrices should map to limma by default.** Do not recommend pseudobulk DE without sample-level replicate structure.
10. **Do not recommend patient-level outcome modeling from scRNA data unless the sample-level mapping is explicit.** Cell-level signal does not automatically support patient-level prediction.
11. **Do not recommend cross-dataset integration as a default if the biological question can be answered within one good dataset.** Integration is a tool, not a requirement.
12. **Do not promise experimental validation capability unless resources are clearly available or explicitly labeled as potentially obtainable.**
13. **If critical feasibility information is missing, state that the plan is provisional and assumption-dependent.**
14. **The final workflow must be dependency-consistent.** No downstream step may require an undeclared input, unverified metadata, or unsupported data structure.

---

## Quality Standard

A good output from this skill should:
- feel like a real study plan rather than a brainstorming note
- identify one dominant study pattern
- recommend one primary route while still showing all four workload levels
- recommend data directions without overstating certainty
- connect biological objectives to module choice
- explicitly separate discovery, validation, and extension
- preserve factual caution around datasets and references
- remain executable under the stated assumptions

## Prerequisites (where data comes from)

- **Research-direction input** → user provides: disease/phenotype + single-cell interest (mechanism / cell state / biomarker / communication / treatment response), optionally with tissue, platform, public-data-only constraint, wet-lab availability, target workload
- **No code or data files required** — this is a zero-code study-design methodology (with 3 consolidated `references/` module files)
- **Literature support (optional)** → if the user provides verified citations, include them per `references/study_design.md` §Literature Retrieval and Citation; otherwise provide only a search strategy — never fabricate PMIDs/DOIs
- **For Phase R (Review & Re-plan):** analysis results from the pipeline skills (h5ad checkpoints, DE tables, proportion tables, CCC scores) + the researcher's judgment on decision points

## When to leave this skill (where to go)

- **First pass** (Steps 1-7 done) → start actual data processing → `single-cell/omicverse-pipeline` (Python) or `single-cell/scop` (R/Seurat) or `spatial/omicverse-spatial` or `general-bio/omicverse-bulk`
- **After each analysis batch** → **return here for Phase R** (Review & Re-plan) → then back to the pipeline skill for the next batch. This loop repeats. (Core Rule 8)
- **Loop converged** (hypothesis ledger stable + story agreed with researcher) → `references/discovery_miner.md` + `references/story_builder.md` → `visualization/figure-production` → `presentation/scientific-slides` / `presentation/manuscript-writing`
- Plotting → `visualization/figure-production`
- Manuscript writing → `presentation/manuscript-writing`
- Presentations → `presentation/scientific-slides` (formal talk / lab-meeting dual mode)

## Key pitfalls

- **The Dataset Disclaimer is mandatory**: any section naming datasets / public resources / references must be preceded by it — never fabricate GEO accessions / PMIDs / cohort availability / cell-type labels (the core application of meta-methodology principle ①).
- **Datasets are examples only**: when recommending GSE/PMIDs, label them "verify availability" — do not guarantee access; LLMs are particularly prone to inventing accession numbers.
- **Sample-size advice needs a statistical basis**: power analysis or a domain consensus (e.g. scRNA ≥3 bio replicates/group); no thumb-in-the-air numbers.
- **The study pattern must match the research objective**: disease-focused / mechanism-focused / biomarker-focused / translational each have their own pattern; a mismatch corrupts every downstream analysis module.
- **This skill does not assess analysis feasibility**: it is a design phase and **does not execute analysis** — feasibility is verified later via omicverse-pipeline/scop after the plan is produced.
- **The four configurations (Lite/Standard/Advanced/Publication+) must be explicit**: prevents the user from running Lite config at Publication+ workload, or vice versa.
