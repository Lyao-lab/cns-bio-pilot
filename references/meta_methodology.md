# Meta-methodology: How to Find and Solve Problems

> Cross-project, cross-tool, cross-LLM principles for "how to think".
> Not a list of specific pitfalls — every project meets new ones, but every pitfall violates at least one principle below.
> Distilled from: (a) POP project fieldwork (b) recurring failure modes on GitHub/Biostars/r/bioinformatics (c) failures specific to LLM-assisted bioinformatics.
> Foundational literature: Luecken & Theis 2019, Heumos et al. 2023 (sc-best-practices), Squair et al. 2021, Lähnemann et al. 2020, LIANA benchmark (Dimitrov 2022).

---

## 1. Verify Preconditions, Don't Assume Them

**Root cause**: Every method, API, and LLM output carries implicit assumptions / preconditions. Failure means **using it without checking its preconditions** — code that runs is the most dangerous, because it lowers vigilance.

| What you assume | What you must verify |
|---|---|
| "this function exists" | `inspect.signature()` / official docs — LLM package-hallucination rate ~9–20% |
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

**Discipline**: Always make **"who is my N"** explicit — into the design matrix, into the legend, into the methods. Default single-cell DE to pseudobulk (aggregate by sample × cell type → DESeq2/edgeR). When n≤3/group, label it exploratory.

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

## How to Use the Six Principles

After each analysis step, run the **Six Self-Check Questions**:

1. Did I **verify a precondition**? (API / method assumption / LLM output — at least one)
2. When I changed data use, did I **ask about semantics**?
3. **Who is my N**, and is it in the model?
4. Am I reporting the **destination or the path**? Did I do sensitivity analysis?
5. After an upstream change, did I **recompute downstream**? Is this my **third** retry? If yes → stop for root cause.
6. Did I do the **design / environment prechecks**?

If any answer is "no" or a circuit-breaker triggers, **do not proceed**.

---

## Negative Reference: Real Failures Matching These Six (not part of the skill — for recognition only)

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

> When recognizing a failure, **map it to one of the six first** — it tells you "where the thinking went wrong", which beats "how to fix this bug".
