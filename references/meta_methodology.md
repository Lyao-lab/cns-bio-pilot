# Meta-methodology: How to Find and Solve Problems

> Cross-project, cross-tool, cross-LLM principles for "how to think".
> Not a list of specific pitfalls — every project meets new ones, but every pitfall violates at least one principle below.
> Distilled from: (a) POP project fieldwork (b) recurring failure modes on GitHub/Biostars/r/bioinformatics (c) failures specific to LLM-assisted bioinformatics.
> Foundational literature: Luecken & Theis 2019, Heumos et al. 2023 (sc-best-practices), Squair et al. 2021, Lähnemann et al. 2020, LIANA benchmark (Dimitrov 2022).

---

## 1. Verify Preconditions, Don't Assume Them

**Root cause**: Every method, API, and LLM output carries implicit assumptions / preconditions. Failure means **using it without checking its preconditions** — code that runs is the most dangerous, because it lowers vigilance.

**Version self-adaptation**: Package versions change constantly. Do NOT hardcode version assumptions in your code or trust API signatures from memory/training data. Instead:
- Before calling any `ov.*` / `pt.*` / `sc.*` function for the first time: `inspect.signature(func)` — verify parameter names exist
- After any `pip install --upgrade`: run `python scripts/api_check.py --diff` to detect breaking changes
- If a parameter doesn't match: adapt the call (read the actual signature), don't fail silently
- See `compat.yaml` for the currently verified environment (but treat it as a snapshot, not a constraint)

| What you assume | What you must verify |
|---|---|
| "this function exists" | `inspect.signature()` / official docs — LLM package-hallucination rate ~9–20% |
| "this parameter name is correct" | `inspect.signature(func)` — params get renamed across versions (e.g. `tresh` not `thresh`, `methods` not `method`) |
| "this GEO/PMID/gene name is real" | batch-check NCBI/HGNC — ~20% of LLM citations are fabricated |
| "DESeq2 assumes replicates" | check `design`, is donor in the model? n≤3 = exploratory only |
| "CellChat p<0.001 = real signaling" | it assumes mRNA ≈ protein activity; multi-method consensus = evidence |
| "deconvolution proportions are true" | the reference is a strong prior; have you validated on simulated ground truth? |
| "code runs = result correct" | is the geometric / statistical / biological semantics right? No error ≠ correct |

**Discipline**: Before using any method / API / LLM conclusion, write down "it assumes X, I verified X with Y". If unverifiable, downgrade to exploratory and say so.

---

## 2. State Semantic Boundaries Explicitly

**Root cause**: The same data / artifact has **different semantics in different uses** and cannot be swapped. Numbers may compute, but the semantics are already wrong.

| Confusion | Consequence |
|---|---|
| Corrected embedding used as raw counts for DE | disease signal erased, DE all non-significant or false negative |
| normalized / log layer fed to a tool needing raw counts | NB model assumptions break, p-values meaningless |
| per-sample z-score then compared across samples | "difference" is a scaling artifact, not biology |
| module score with binary cutoff | fabricates a false pos/neg boundary |
| exploratory results in confirmatory language | "we proved X causes Y" → overclaim |
| LLM code that "looks right" | wrong statistical assumptions (NB treated as Gaussian, negatives as counts) |
| inference (annotation / CCC / deconvolution output) treated as measurement | treating "prediction from an imperfect reference" as fact |

**Discipline**: Every time you change data use (use adata.X for something new, run LLM code on a new analysis), ask "do the semantics of this artifact support what I'm about to do?". LLMs have no "data semantic awareness" — whether `adata.X` is raw or normalized, you must declare it explicitly.

---

## 3. Who Is N — Always State the Replicate Unit

**Root cause**: cell ≠ donor; spot ≠ tissue; technical replicate ≠ biological replicate. This single root error underlies pseudoreplication, CCC, and composition analyses.

| Wrong unit | Artifact |
|---|---|
| 10,000 cells treated as 10,000 replicates | per-cell Wilcoxon explosively inflates significance |
| spots treated as independent samples | spatial autocorrelation inflates n |
| "cell cluster expresses an LR pair" treated as "cells are signaling" | mRNA co-expression ≠ pathway activation |
| cell-type proportions (which sum to 1) treated as independent counts | compositional constraint → chi-square / Fisher produce spurious significance + wrong direction |

**Discipline**: Always make **"who is my N"** explicit — into the design matrix, into the legend, into the methods. Default single-cell DE to pseudobulk (aggregate by sample × cell type → DESeq2/edgeR). When n≤3/group, label it exploratory. For **cell-type proportion / differential abundance** comparisons: proportions sum to 1, so one cell type going up forces others down — this compositional constraint violates chi-square/Fisher/t-test independence assumptions and inflates false positives. Use **compositional-aware methods**: `miloR` (R, neighborhood-level DA — bypasses annotation-label dependence), `scCODA` (Bayesian compositional, Python/R), or `propeller` (R, cell-type proportion with sample-level replicate). Plain `chi2_contingency` / `fisher_exact` / `chisq.test` on proportion tables is a methodological error at the same level as per-cell DE.

---

## 4. Report the Path, Not Just the Destination

**Root cause**: "Garden of forking paths" — an analysis has countless branches (resolution, reference, filter thresholds, annotation method, batch method, pseudobulk vs per-cell, Harmony vs scVI…); reporting only **the one that worked** = hidden p-hacking. LLMs worsen this: they emit "shortest-path-to-result" code and skip sensitivity analysis.

**Discipline**:
- Run **sensitivity analysis** on every key parameter (± 1 step, does the conclusion change?); reversal = selective-reporting risk
- **Method choice must rest on objective criteria independent of the conclusion** (stability, scSHC significance, bootstrap, simulated ground truth), never "it gave me the cluster I wanted"
- Report **total attempts**, not just the one that worked
- Distinguish exploratory vs confirmatory; single-cell is mostly exploratory — ban "prove / cause" language
- **LLM output is a draft, not an answer** — audit before use, never trust directly

---

## 5. Chain Failure & Circuit-Breaking

**Root cause**: Bioinformatics is a chain — one upstream change invalidates everything downstream; complex dependency stacks have interlocked versions; LLM training data is a time snapshot, so versions / IDs / APIs drift.

**Discipline**:
- **Recompute on chain failure**: any upstream change (re-integration / re-annotation / re-QC / re-filtering) → recompute everything from that step onward, **never reuse old h5ad / old DE tables / old figures**
- **Debug circuit-breaker**: if the same step fails ≥3 retries, stop and do root-cause analysis (read full traceback, minimal repro, check dependency chain); don't gamble on more retries
- **Lock method versions**: for complex dependency stacks (R / toolchain / scvi↔anndata↔omicverse interlocks), get it working once at project start, then pin `pip freeze` + `conda env export` + R `sessionInfo()` — no drift
- **Predefine downgrade paths**: every core method gets a plan B (GPU→CPU / method A→B / toolchain break→alt implementation); don't improvise on the spot
- **Verify external dependencies live**: never trust LLM memory for versions, accessions, APIs — check PyPI / NCBI / official docs in real time

---

## 6. Design Upfront — Analysis Cannot Rescue a Design Flaw

**Root cause**: When batch is confounded with condition, no algorithm separates signal from noise; when the reference is mismatched, annotation / deconvolution are necessarily biased; with no replicates, DESeq2 dispersion is unestimable. This is mistaking a statistics problem for an algorithm problem.

**Discipline**: Confirm once, before touching the data:

| Precheck | If unmet |
|---|---|
| Are batch and condition **separable**? (don't do batch1=all control, batch2=all treated) | Not separable → **no cross-condition comparison**; this is a design problem |
| Is the reference **same tissue / same state / same resolution**? | Mismatched → annotate only to broad lineage, subtypes untrusted |
| **≥3 biological replicates per condition**? | <3 → label exploratory, no conclusions |
| Does the dependency matrix (Python/R/toolchain/GPU) **import successfully**? | Any failure → halt business logic, fix environment first |
| Does every core method **run on minimal data**? | Fails → switch method now, don't defer to results time |

> Core lesson of Luecken & Theis 2019 and Lähnemann et al. 2020: **a design problem cannot be rescued at the analysis stage**.

---

## 7. Step-Gate Sanity Checks (borrowed from planner-verifier loop)

**Root cause**: A long pipeline (QC → cluster → DE → enrichment → CCC → trajectory) silently accumulates errors. By the time results look wrong at the end, the failing step is buried upstream. LLM-driven analysis is especially prone: it emits "shortest-path-to-result" code and never looks back.

**Discipline**: After each key step, pass an automatic sanity check **before** proceeding to the next. A failed check → stop and debug that step; do not carry garbage downstream. This is the bioinformatics concretization of the planner-verifier dual loop (K-Dense Analyst outperforms single-model by 6 points on BixBench precisely because of per-step verification).

| Step | Sanity check | Red flag (stop) |
|---|---|---|
| **After QC** | mt% distribution per sample; doublet rate; cell count per sample | Any sample loses >50% cells vs others; doublet rate >30% |
| **After clustering** | Known marker expression per cluster (e.g., CD3D in T cell cluster only, not spread); are expected cell-type markers split across clusters or collapsed into one? | Marker expressed everywhere or nowhere; one cluster = mixed lineages (e.g., CD3D+ and CD79a+ in same cluster) |
| **After DEG** | Housekeeping genes (ACTB/GAPDH/HPRT1) not in top DEG; logFC magnitude reasonable; up/down gene counts roughly balanced | Housekeeping gene is "significantly DE"; all genes up-regulated (normalization artifact); abs(logFC) > 10 for many genes |
| **After enrichment** | Gene-set overlap is not "the entire gene list"; no anti-biological pathways top-ranked (e.g., apoptosis pathway top in a proliferation analysis) | Same 200 genes appear in every pathway; ribosomal/mitochondrial terms dominate |
| **After CCC** | Known ligand-receptor direction correct (ligand in sender, receptor in receiver); not single-method-only (see discovery_miner §3) | Ligand and receptor both expressed in the same side; CCC score driven by one rare cell pair |
| **After trajectory / pseudotime** | Root cell expresses known root marker; trajectory direction matches known biology or independent velocity | Root cell has no biological justification; pseudotime contradicts known developmental order |
| **After each analysis batch** (before next batch) | **Discussion checkpoint passed**: results interpreted, hypothesis ledger updated, decision points surfaced to researcher, researcher responded | Proceeding to next batch without reviewing results or getting researcher input on direction (Core Rule 8 — biology is iterative, not linear) |

> This check is **per-step**, not just at the end. meta_methodology §1-§6 are principles; §7 is the **operational gate** that enforces them mid-pipeline. The last row (discussion checkpoint) is the **batch-level gate** — it prevents the pipeline from auto-running end-to-end without the result-driven iteration loop that real biological research requires.

---

## 8. Hypothesis Ledger + Provenance Contract (borrowed from hypothesis-driven science agents)

**Root cause**: Running a pipeline without explicit hypotheses produces "data dredging" — every significant result is post-hoc framed as if intended. Without provenance records, results are irreproducible and reviewers cannot audit the path.

**Discipline**:

### 8a. Hypothesis Ledger

Before analysis begins, output a **hypothesis ledger** — an ordered list of falsifiable hypotheses, each with a calibrated confidence:

```
H1: [main biological hypothesis, e.g., "VIC-to-myofibroblast transition drives valve fibrosis"]
    confidence: high | med | low
    basis: [prior literature / pilot data / biological reasoning]
    falsification criterion: [what result would refute it]
    status: [pending | supported | refuted | inconclusive]  ← filled in after analysis

H2: [secondary hypothesis]
    confidence: ...
    ...
```

- `confidence` is calibrated against the strength of the basis, not the desirability of the hypothesis
- After analysis, **fill in `status`** for each: `supported` (data + significance + biology coherent) / `refuted` (data contradicts) / `inconclusive` (insufficient evidence)
- Conclusions not in the ledger = post-hoc / exploratory; label them as such (see 8c)

### 8b. Provenance Contract

Every analysis run must record, in an `analysis_log.md` (or `step.params.json` per checkpoint):

| Record | Example |
|---|---|
| **Random seed** | `np.random.seed(42); torch.manual_seed(42)` set in §0 Init; scVI `seed=42` |
| **Key parameters per step** | `§2: mt_threshold=0.15 (from diagnostic knee); §5: resolution=0.6 (chosen from candidate comparison, see Step 5b); §7: integration=harmony (batch separable, lightweight sufficient)` |
| **Data hash** | `md5sum` of input h5ad/matrix at project start |
| **Versions** | from `compat.yaml` + `pip freeze` + `sessionInfo()` (meta §5) |
| **Total attempts** | `§5 clustering: tried res=0.3/0.6/1.0 → chose 0.6 (ARI stability 0.82)` — not just the one that worked |

The checkpoint h5ad (Core Rule 5) stores **data state**; the provenance log stores **decision state**. Both are needed for reproducibility.

### 8c. Conclusion Confidence Grading

Every conclusion in the final report gets a grade:

| Grade | Criterion | Wording allowed |
|---|---|---|
| **Verified** | Data support + literature grounding (PubMed/DOI cited) + passes §7 sanity gate | "we show / demonstrates" |
| **Data-supported, literature gap** | Data support + passes §7, but no prior literature to contextualize | "we observe / suggests, consistent with our data" |
| **Speculative** | Plausible biology but data insufficient or no orthogonal validation | "may / hypothesized / warrants further study" |

Conclusions without any grade = not reportable. This three-tier system (borrowed from PaperQA2's evidence grading and Co-Scientist's calibrated confidence) prevents overclaiming.

---

## How to Use the Eight Principles

After each analysis step, run the **Eight Self-Check Questions**:

1. Did I **verify a precondition**? (API / method assumption / LLM output — at least one)
2. When I changed data use, did I **ask about semantics**?
3. **Who is my N**, and is it in the model?
4. Am I reporting the **destination or the path**? Did I do sensitivity analysis?
5. After an upstream change, did I **recompute downstream**? Is this my **third** retry? If yes → stop for root cause.
6. Did I do the **design / environment prechecks**?
7. Did I pass the **step-gate sanity check** (§7) for the step I just completed? Is the next step built on a verified step?
8. Is this conclusion in my **hypothesis ledger** (§8a)? What grade does it earn (§8c)?

If any answer is "no" or a circuit-breaker triggers, **do not proceed**.

---

## Negative Reference: Real Failures Matching These Eight (not part of the skill — for recognition only)

> Typical counter-examples distilled from GitHub / Biostars / POP projects. **Not written into the skill body** — they exist only to help you recognize "which principle was violated".

- **Spatial coordinates mirrored — 11 steps to fix** (POP) → violates 1 (no ground-truth check) + 5 (retry without root cause)
- **Same code, same data, Tangram drifts across runs** (POP) → violates 5 (no seed / version lock)
- **Annotation switch flips cell proportion 60.6% → 66.0%** (POP) → violates 1 (reference assumption) + 4 (sensitivity)
- **Milo / rpy2 toolchain break** (POP) → violates 6 (dependency precheck)
- **Per-cell Wilcoxon reports thousands of DEG** (fieldwide high-frequency) → violates 3 (pseudoreplication)
- **DE on corrected embedding** (fieldwide high-frequency) → violates 2 (semantic confusion)
- **LLM fabricates Ensembl ID / GEO accession** (Ming Tang et al. public records) → violates 1 (verify preconditions)
- **LLM-written NB-DESeq2 fed normalized input** (long-standing Biostars consensus) → violates 2 (semantics)
- **CellChat single-tool conclusion taken as truth** (LIANA: 16 resources × 7 methods, very low consensus) → violates 1 (confidence ≠ evidence)

> When recognizing a failure, **map it to one of the eight first** — it tells you "where the thinking went wrong", which beats "how to fix this bug".
