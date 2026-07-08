# Lab Meeting Mode Workflow (merged from the original lab-meeting-slides skill)

> Slide **structure design** for group meetings / lab meetings / project reviews / PI updates / progress reports.
> **This mode produces only the slide structure / copy skeleton**; actual rendering goes through the scientific-slides main-flow `build_deck.py`.
> Core difference from the scientific-slides default mode (formal talk): **discussion-driven + data-honesty boundary + no inflating progress**.

---

## Key differences vs the formal talk

| dimension | formal talk (default mode) | Lab meeting (this mode) |
|---|---|---|
| Purpose | visual impact + complete story | **decision-useful + discussion-driven** |
| Story arc | complete narrative arc | **focused on unresolved problems / next steps** |
| Uncertain results | packaged as conclusions | **honestly marked "unresolved"** |
| Background | moderate (diverse audience) | **minimal** (the team knows the background) |
| Data | curated polished figure | **raw/intermediate results OK, seeking feedback** |
| Next steps | research outlook of completed work | **explicit next-step proposals, open for discussion** |

---

## 9-step workflow

### Step 1 — Clarify before structuring
If the user only says "make a group-meeting PPT", **do not immediately emit a full structure**. First ask:
- project topic, current stage, meeting goal, existing figures, unresolved problems, who the deck is for

### Step 2 — Identify the meeting goal
Judge what the deck is mainly for: progress reporting / seeking feedback / troubleshooting / decision (choosing the next experiment) / PI update / manuscript internal review

### Step 3 — Identify the project stage
background framing / early data / intermediate analysis / validation / interpretation / next-step decision

### Step 4 — Choose the slide proportions
Decide how much each of background / research question / methods / current data / interpretation / open problems / limitations / next steps gets

### Step 5 — Build the slide flow
Recommended order: project question → current status → key results → **unresolved issues** → interpretation/decision points → next-step proposal

### Step 6 — Frame unresolved problems honestly
Make explicit which uncertain / weak / inconclusive / blocked content **should be shown directly** rather than masked by generic background slides

### Step 7 — Structure the next-step section
Turn open problems into concrete, discussable next-step slides — but **do not pretend these steps are already finalized**

### Step 8 — Explain the structural logic
Why certain content leads, why certain background was cut, why certain open problems need their own slide

### Step 9 — Produce the structure (use the mandatory output structure below)

---

## Mandatory output structure (A-I)

| section | content |
|---|---|
| A. Input Match Check | is the input sufficient; what is missing |
| B. Meeting Context Understanding | project topic / stage / goal / progress / unresolved problems |
| C. Main Structuring Risks | what could weaken the deck (too much background / buried decision points / hidden open problems …) |
| D. Recommended Slide Deck Structure | recommended slide order |
| E. Slide Role Breakdown | what each slide should accomplish |
| F. Key Emphasis and Omissions | what to emphasize, what to cut |
| G. Next-Step Framing | how to present the next-step section |
| H. Structuring Logic Explanation | why this ordering |
| I. What Additional Information Would Improve Accuracy | what input is still missing |

---

## Hard Rules (do not violate)

1. **Never fabricate** progress / figures / results / next steps the user has not supplied
2. When the meeting goal + project status are unclear, **do not emit a full deck structure** — ask first
3. When input is insufficient, **ask follow-ups or recommend uploading materials** (project summary / figure list / progress notes / manuscript outline / current deck draft)
4. **Do not mask** uncertainty or blocked progress with decorative background slides
5. **Do not overload** the deck with raw data so that decision points blur
6. **Do not present** open next-step ideas as finalized commitments
7. Do not fabricate references / PMID / DOI / dataset status / validation status / experimental progress
8. **Must explain** why certain slide blocks were prioritized and others cut
9. Always keep the deck aligned with the **actual meeting function**
10. **Do not conflate** internal scientific communication with polished external storytelling

---

## Rule modules (load on demand)

| rule file | when to use |
|---|---|
| `rules/clarification-first-rule.md` | before any long structural output |
| `rules/meeting-goal-selection-rules.md` | when judging the deck type |
| `rules/slide-priority-rules.md` | when deciding content proportions |
| `rules/data-honesty-boundary-rules.md` | to prevent inflating incomplete results |
| `rules/next-step-structuring-rules.md` | open problem → discussable next step |
| `rules/logic-reporting-rule.md` | to explain slide-order reasoning |
| `rules/hard-rules.md` | applied throughout, overrides any polish pressure |

---

## After the structure is ready

Render the .pptx via the scientific-slides main-flow `build_deck.py`:
```bash
python scripts/build_deck.py outline_labmeeting.json -o labmeeting.pptx
python scripts/qa_deck.py labmeeting.pptx   # geometric QA
```

**Key difference**: the lab-meeting-mode outline.json should **reduce background slides, add more open-problem / next-step slides, and use "exploratory" wording for incomplete results** (see `data-honesty-boundary-rules.md`).
