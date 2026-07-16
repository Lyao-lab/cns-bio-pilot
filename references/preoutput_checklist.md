# Pre-Output Checklist (shared across all skills)

> The 5 universal checks every figure / writing / slide output must pass before delivery.
> Each skill's `Pre-Output Checklist` section should reference this file rather than duplicating these items.
> Skill-specific items (e.g. omicverse-plotting adds "colorblind palette"; scientific-slides adds "readability contract") stay in the skill's own checklist appended below this core 5.

## Core 5 (universal — apply to every output)

- [ ] **Numeric integrity**: every quantitative figure/table keeps N / statistical test / error bars — no numbers without provenance
- [ ] **Citation support**: state exactly which figure / statistic / dataset backs the main conclusion
- [ ] **No speculation**: when there is no significant difference, write "No significant effect" — don't fabricate a trend
- [ ] **Association ≠ causation**: use "associated with"; "regulates/causes" requires experimental evidence
- [ ] **No fabrication**: never invent datasets / accession numbers / PMIDs / API signatures / sample sizes — missing info uses placeholder `[AUTHOR TO SPECIFY: ...]`

## Skill-specific extensions

| Skill | Extra items beyond core 5 |
|---|---|
| visualization/omicverse-plotting | colorblind palette; `ov.plot_set()` + `pdf.fonttype=42`; title/legend non-overlap (see figure_aesthetics.md) |
| visualization/multi-panel-figures | panel labels A-F; shared legend; DPI consistent across sub-panels |
| visualization/scientific-schematics | no fake data in schematics; OPENROUTER_API_KEY set |
| presentation/scientific-slides | readability contract (title≥24pt/body≥12pt/caption≥7.5pt); no accent line under title; qa_deck.py PASS |
| presentation/methods-writer | reporting guideline matched (CONSORT/STROBE/PRISMA/TRIPOD/ARRIVE/STARD); version numbers verified |
| presentation/results-writer | Results ≠ Discussion; citation-needed placeholders; no Discussion-style interpretation |
| presentation/figure-legend-writer | legend self-contained (readable without body text); figure type stated correctly |

## How skills should reference this

In each skill's `## Pre-Output Checklist` section, write:
```markdown
## Pre-Output Checklist (core 5 in references/preoutput_checklist.md + skill-specific below)
- [ ] Core 5 passed (see references/preoutput_checklist.md)
- [ ] <skill-specific item 1>
- [ ] <skill-specific item 2>
```

This avoids duplicating the same 5 bullets across 6+ skill files.
