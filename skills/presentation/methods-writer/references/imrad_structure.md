# Methods Section Structure (IMRAD)

## Purpose

Provide sufficient detail for another expert to **replicate the study exactly** and assess its validity. Core principle: replication-first.

## Standard Subsections

### Research Design
- State the design type (RCT, cohort, case-control, cross-sectional, diagnostic accuracy, prediction model)
- Justify the choice if non-obvious
- Specify controls, randomization, blinding as applicable

### Participants / Subjects / Samples
- Define population + inclusion/exclusion criteria (use recognized standards: ICD-10, DSM-5)
- Sample size: state method (power analysis — effect size, α, power, one/two-tailed) and account for attrition
- Recruitment: sources, timeframe, setting, consent process
- Animals: species, strain, age, sex, housing conditions

### Materials and Equipment
- List all reagents/materials/equipment with **manufacturer name + location** in parentheses
- Catalog numbers for special items; lot numbers for chemical reagents
- Software names + versions
- Antibodies: clone, catalog number, dilution

### Procedures
- Chronological order; subheadings for complex protocols
- Specify parameters: temperature, time, concentration, pH, centrifugation force
- Sufficient detail for replication (e.g., "5 mL venous blood from antecubital vein into EDTA tubes via 21-gauge needle; centrifuged 1,500 × g, 10 min, within 30 min")

### Measurements and Outcomes
- Pre-specify **primary** and **secondary** outcomes
- Define measurement tools, scoring, validity (e.g., Cronbach's α)
- State units

### Statistical Analysis
General stats live in `figure_design.md` §3. Methods-specific requirements:
- Name every test with justification + assumptions
- Software + version (e.g., R 4.2.1)
- Missing-data mechanism + handling (complete-case, multiple imputation) + sensitivity analysis
- Multiple-comparison adjustment method (Bonferroni, BH-FDR) with adjusted threshold
- Analysis population (ITT vs. per-protocol)

### Ethical Considerations
- Human: IRB approval **number**, Declaration of Helsinki adherence, informed consent
- Animal: IACUC approval **number**, ARRIVE 2.0 adherence, anesthesia/euthanasia method

## Verb Tense in Methods

| Content | Tense |
|---|---|
| Actions you performed | Past ("We measured...", "Participants completed...") |
| Established procedures / instrument description | Present ("PCR amplifies DNA", "The scale consists of 17 items") |

## Format Rules
- Write in **full paragraphs / flowing prose** — never bulleted lists in the final manuscript
- Typical length 2–4 pages, proportional to study complexity

## STAR Methods Format (Cell Press / Current Biology)

Structured one-line-per-item layout when the journal requires STAR Methods. Fixed headings:
- **Lead Contact** — single point of contact for reagents/resource sharing
- **Materials Availability** — statement on reagent availability
- **Data and Code Availability** — accession numbers, repository links, DOI
- **Experimental Model and Subject Details** — cell lines, organisms, human subjects
- **Method Details** — full protocols, chronologically organized
- **Quantification and Statistical Analysis** — tests, software, n, error bars, significance definition
- **Additional Resources** — websites, databases used

## Placeholder Convention `[AUTHOR TO SPECIFY]`

When generating Methods drafts, insert `[AUTHOR TO SPECIFY]` for any field the source material does not supply — never fabricate values. Typical uses:
- Ethics/IACUC approval numbers
- Reagent catalog numbers, antibody dilutions, clone IDs
- Software versions, equipment model numbers
- Exact dates, recruitment site names
- Randomization seed / sequence generator

The author replaces every `[AUTHOR TO SPECIFY]` before submission; an unfilled placeholder signals missing source data, not finished prose.

## Adaptation by Study Type

### Clinical Trials
Add: trial registration number + platform, blinding detail, adverse-event reporting, DSMB (if any).

### Systematic Reviews / Meta-Analyses
Methods focuses on: search strategy (databases, dates, full query for ≥1 database), eligibility criteria, data extraction, risk-of-bias tool (Cochrane ROB 2 / ROBINS-I / QUADAS-2), synthesis method, certainty assessment (GRADE).

### Case Reports
Methods section is usually titled **"Case Description"**: demographics, history, findings, diagnostic workup, intervention, timeline.

### Observational Studies
Emphasize: identification of confounders, control methods (stratification, multivariable adjustment), causal-inference limitations.

## Common Methods-Specific Errors

1. **Insufficient detail** for replication (vague "samples collected on ice")
2. **Results leaking into Methods** ("the intervention significantly reduced symptoms, p=0.002") — Methods describes *how measured/analyzed only*
3. **Missing randomization / blinding mechanics** — state generation method, allocation concealment, who was blinded
4. **Missing sample-size justification** ("we recruited 100 participants" → must show power calc)
5. Undefined abbreviations; missing ethical approval numbers

## Methods Checklist (Pre-Submission)

- [ ] Design type + rationale stated
- [ ] Timeframe, location, setting
- [ ] Inclusion/exclusion criteria explicit
- [ ] Recruitment + consent process
- [ ] Sample-size calculation with parameters
- [ ] Randomization generation + allocation concealment + blinding (if applicable)
- [ ] All reagents/equipment: manufacturer + location + catalog #
- [ ] Software + versions
- [ ] Procedures chronologically ordered with key parameters
- [ ] Primary + secondary outcomes defined
- [ ] Statistical tests named + justified; software + version
- [ ] Missing-data handling; multiple-comparison adjustment
- [ ] Ethics approval numbers; Helsinki / ARRIVE adherence statement
- [ ] No `[AUTHOR TO SPECIFY]` placeholders left unfilled
