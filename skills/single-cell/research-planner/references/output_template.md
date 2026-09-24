# Mandatory Output Structure（A-M 逐节定义）

> 自 SKILL.md 拆出（2026-09-24，内容原样迁移）。输出时 A-M 按序全部出现；SKILL.md 保留一句话索引。
> 与 references 模块的对应关系见 SKILL.md「Reference Module Integration」节。

Always use the following sections in order.

### A. Study Intent Summary
A concise restatement of:
- disease / phenotype / tissue
- biological question
- single-cell value-add
- scope assumptions

### B. Best-Fit Study Pattern
Name the dominant pattern and, if needed, one secondary supporting pattern.

### C. Four Workload Configurations
Output **Lite / Standard / Advanced / Publication+** in a comparison table.

### D. Recommended Primary Plan
Pick one primary route and explain why it is the best fit.

### E. Data Strategy and Example Dataset Directions
Specify:
- required data type(s)
- preferred sample grouping logic
- key metadata requirements
- example dataset directions / repositories / dataset types
- dataset risks and access assumptions

This section may name **example datasets or repositories**, but they must be presented as **reference candidates only**, not as guaranteed usable resources.

### F. Core Analysis Modules and Method Choices
Use a table to specify:
- analysis module
- purpose
- when it is necessary / recommended / optional
- preferred methods or tools
- important method constraints

### G. Validation and Extension Layers
Specify what counts as:
- within-dataset validation
- cross-dataset validation
- orthogonal validation
- translational extension
- experimental follow-up

### H. Step-by-Step Workflow
Provide the ordered workflow.

**If datasets or public resources are mentioned, place the Dataset Disclaimer immediately before the workflow.**

### I. Validation Evidence Hierarchy
State what evidence level the proposed plan can actually support.

### J. Figure and Deliverable Plan
State the likely figure set and output package.

### K. Verified Reference Layer or Search Strategy
If verified references are available, list them.
If not, provide a structured literature search strategy and clearly state that formal references are not yet verified.

### L. Self-Critical Risk Review
Include:
- strongest part
- most assumption-dependent part
- most likely false-positive source
- easiest-to-overinterpret result
- likely reviewer criticisms
- fallback plan

### M. Hypothesis Ledger
The pre-registered hypothesis list from Step 8 (each H with confidence/basis/falsification criterion/status=pending). This is the living document that Phase R updates each iteration.
