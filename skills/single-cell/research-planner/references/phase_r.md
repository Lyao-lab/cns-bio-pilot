# Phase R — Review & Re-plan（结果回顾与再规划完整规程）

> 自 SKILL.md 拆出（2026-09-24，内容原样迁移）。进入时机/收敛条件亦在此文件；SKILL.md Step 8 产出的假设台账是本循环的消费对象。
> 本文件与 discovery_miner（扫描）、story_builder（收敛判据）、meta_methodology §7-8（step-gate/台账）联动。

---

> **This is the most important phase.** Steps 1-7 produce an *initial* plan — but biology is evidence-driven, not spec-driven. The real research happens in the loop: run a batch → look at results → discuss with the researcher → revise → run the next batch. This is NOT optional (Core Rule 8). Do not treat the initial plan as a fixed spec to execute linearly.

### When to enter Phase R

After completing each analysis batch (e.g., after QC+clustering+annotation; after first DE round; after CCC; after spatial mapping). The pipeline skills (`omicverse-pipeline`, `omicverse-spatial`, etc.) hand control back here after each batch — this skill is the **hub** the researcher returns to between batches.

### Phase R has four sub-steps — run them every time

#### R1. Result Interpretation (what does the data say?)

Read top-level `references/discovery_miner.md` and scan the batch's outputs:
- For each hypothesis in the ledger (meta §8a): is it now `supported` / `refuted` / `inconclusive`? Update its status.
- What **unexpected** signals appeared? (a cell state not in the plan, a pathway that shouldn't be there, a spatial pattern) — log these as candidate discoveries per discovery_miner §1.
- Run the false-positive checklist (discovery_miner §3) on any new finding before believing it.

#### R2. Extract Decision Points (what needs human judgment?)

Identify decisions that **cannot** be made from data alone and require the researcher's biological knowledge / project goals. Typical decision points:

| Decision type | Example | Why human must decide |
|---|---|---|
| **Cell-type naming** | "Cluster 3 expresses CD3D+IL7R- — is this an unconventional T subset, or a doublet?" | Naming anchors all downstream narrative; wrong name = wrong story |
| **Direction selection** | "DE shows both fibrosis AND immune signals — which is the main thread?" | Resource-limited; can't chase both. Depends on the researcher's question |
| **Signal pursuit** | "An unexpected neuronal marker appeared in gut data — artifact or real?" | Pursuing serendipity costs time; only the researcher knows if it's worth it |
| **Threshold calibration** | "The knee in mt% is ambiguous between 12% and 18%" | Tissue biology determines this, not the algorithm |
| **Negative result handling** | "The hypothesized cell state doesn't separate — is the hypothesis wrong, or is the data underpowered?" | Determines whether to pivot, reprocess, or report negative |

#### R3. Discussion Checkpoint (PAUSE — wait for researcher)

> **This is a hard gate.** Do NOT proceed to R4 or the next analysis batch until the researcher responds.

Present to the researcher, concisely:
1. **What the results show** (key findings, with figures/tables already generated)
2. **Updated hypothesis ledger** (which hypotheses moved to supported/refuted/inconclusive)
3. **Decision points needing their input** (from R2) — each as a clear question with your recommended option + rationale, but their call
4. **What you would do next for each plausible direction** (so they can choose informed)

Format example:
```
## Batch 1 Review (QC + clustering + annotation)

### Results
- 12 clusters recovered; major lineages (T/B/Mye/Fibro/EC) annotated with marker confidence
- Unexpected: cluster 7 co-expresses CD3D and CD79A (low) — flagged as potential doublet or rare transitional
- Hypothesis ledger: H1 (VIC transition) → inconclusive (need DE); H2 (immune shift) → supported (M2 expanded +16pp)

### Decision points — need your input
1. Cluster 7 (CD3D+/CD79A+): remove as doublet, or keep and investigate?
   → Recommend: check doublet score first; if borderline, keep + run Step 2b sanity (meta §7)
2. Main thread: H1 (fibrosis) or H2 (immune)? Both have signal.
   → Recommend: pursue H1 as main (stronger tissue-specificity), keep H2 as supporting

### If you choose...
- Chase H1 → next batch: subcluster Fibro, DE, trajectory
- Chase H2 → next batch: subcluster Mye, CCC (CellChat Fibro→Mac), spatial co-localization
- Investigate cluster 7 → next batch: doublet re-score, if real → SCRATCH / CITable

Your call?
```

#### R4. Re-plan (revise based on discussion)

After the researcher responds:
1. Update the hypothesis ledger with their decisions
2. Revise the analysis plan — which modules to run next, in what order
3. If the direction changed significantly, re-select the study pattern (Step 2) or workload (Step 3)
4. Record what changed and why in `analysis_log.md` (meta §8b)
5. Hand off to the next analysis batch (pipeline skill)

### When does the loop end?

The iteration continues until:
- ✅ The hypothesis ledger has at least one `supported` hypothesis with a coherent causal chain (story_builder §2)
- ✅ That chain passes the gap scan (story_builder Step 2b)
- ✅ The researcher agrees the story is complete enough to produce figures / slides / manuscript

Then proceed to `story_builder` → `figure-production` → `scientific-slides`. **Do not jump to outputs prematurely** — a story built on unresolved hypotheses is fabrication.
