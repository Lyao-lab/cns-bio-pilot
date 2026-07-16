# Scientific Writing Principles (Methods-Focused)

Generic writing guidance (clarity, conciseness, grammar, paragraph structure) is not repeated here. This file covers **scientific-writing-specific** conventions: tense by section, hedging calibrated to evidence, terminology consistency, statistical language, and venue adaptation.

## Verb Tense by Manuscript Section

Tense errors are among the most common scientific-writing mistakes. Match tense to content, not to personal preference.

| Section / content | Tense | Example |
|---|---|---|
| Introduction — established facts | Present | "DNA is composed of nucleotides." |
| Introduction — prior research | Present perfect | "Several methods have been proposed..." |
| Introduction — gap | Present | "However, little is known..." |
| **Methods — your actions** | **Past** | "We collected samples...", "Participants completed..." |
| **Methods — established procedure / instrument** | **Present** | "PCR amplifies DNA", "The scale consists of 17 items." |
| Results — your findings | Past | "The mean age was 45 years." |
| Discussion — your findings | Past | "We found that..." |
| Discussion — interpretation | Present | "These findings suggest..." |
| Discussion — prior work | Past or Present | "Smith et al. found..." / "Prior work shows..." |
| References to figures/tables | Present | "Figure 1 shows..." |

## Hedging: Matching Claim Strength to Evidence

Over-hedging reads as uncertain; under-hedging overstates. Calibrate to study design.

| Study design | Allowed causal language |
|---|---|
| RCT | "caused", "reduced", "increased" (randomization supports causality) |
| Observational / cohort | "associated with", "linked to" — NOT "causes" |
| Cross-sectional | "associated with" — cannot infer direction |
| In-vitro / mechanism | "suggests", "may", "could" |

Hedging vocabulary:
- **suggest / indicate / imply** — for correlational data (avoid "prove", "demonstrate")
- **may / might / could** — possibility
- **seem / appear** — observation needing confirmation
- **likely / probably / possibly** — degree of certainty

## Statistical Language Precision

- "Significant" reserved for **statistical** significance (p < threshold); never for magnitude ("a significant increase of 30%").
- Avoid "very significant" / "highly significant" unless p < 0.001.
- Match precision to measurement capability (age "45.2 years", not "45.237 years").
- Distinguish **observation** ("BP decreased 145→132 mmHg, p=0.003") from **interpretation** ("this suggests the intervention lowered BP").

## Terminology Consistency

- Use **one term** for one concept throughout; do not vary for elegance (no synonyms for variety).
- Define abbreviations at first use (define separately in Abstract and main text); use only if term appears ≥3 times.
- Do not abbreviate in the title.
- Standard nomenclature: gene symbols italic (*TP53*), protein roman (TP53); follow field convention.

## Anthropomorphism (Scientific-Specific)

Avoid attributing intent to non-human subjects:

| Anthropomorphic | Scientific |
|---|---|
| "The study wanted to examine..." | "We aimed to examine..." |
| "The data suggest they want to..." | "The data suggest..." |
| "This paper will prove..." | "This paper demonstrates..." |
| "Table 1 tells us..." | "Table 1 shows..." |

## Venue-Specific Writing Styles

Calibrate style to target venue.

| Aspect | Nature/Science/PNAS | NEJM/Lancet/JAMA | Field journals | ML (NeurIPS/ICML/ICLR) |
|---|---|---|---|---|
| Audience | Broad; non-specialist accessible | Clinicians | Specialists | ML community |
| Sentence length | 15–20 words | 12–18 words | 18–25 words | 12–20 words |
| Vocabulary | Minimal jargon | Clinical terms | Field-specific | Technical + math |
| Tone | Engaging, "we show here" | Conservative, "we conducted" | Formal | Direct, contribution-focused |
| Equations | Minimized | Rare | Moderate | Essential |
| Contributions | Implicit | Implicit | Implicit | **Numbered list** in Intro |
| Hedging | Moderate | Conservative | Detailed | Minimal (claim gains) |

**ML-conference specifics**: numbered contributions in Intro ("Our contributions are: (1)... (2)... (3)..."); pseudocode and equations expected; quantified claims ("15% speedup", "2.3% accuracy gain"); reproducibility checklist (seeds, compute, hyperparameters).

## Quick Style Adaptation

- **Journal → ML conference**: add numbered contributions; include equations/pseudocode; emphasize quantified gains; compress prose.
- **ML conference → Journal**: remove contribution numbering; expand motivation; separate results/discussion; reduce in-text equations.
- **Basic science → Clinical**: add patient/clinical context; clinical language; emphasize outcomes; cite clinical evidence.

## Numbers and Units (Scientific Conventions)

- Numerals for: ≥10, values with units (5 mg), statistics (p=0.03), ages, percentages.
- Words for: numbers <10 without units ("five participants"); spell out at sentence start.
- Space between number and unit (5 mg, not 5mg); no period after unit.
- SI units unless field convention differs.
- En-dash for ranges with unit only after second number: "15–20 mg".
- Commas for thousands in text: "12,500".

## Pre-Submission Style Checklist

- [ ] Verb tense matches section/content throughout
- [ ] Causal language matches design strength (no "causes" from observational data)
- [ ] "Significant" used only for statistical significance
- [ ] One term per concept; abbreviations defined + used ≥3 times
- [ ] Style matches 3–5 recent papers from target venue
- [ ] All numbers verified: text ↔ tables ↔ figures; n-values sum correctly
- [ ] No anthropomorphism; no overstated claims
