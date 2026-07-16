# LaTeX Beamer Guide (Beamer-specific only)

> Beamer = LaTeX document class for presentations. This file covers **only what is unique to Beamer**: theme/color selection, Chinese support (xelatex + ctex), compile commands, common errors, and template variables. For general design/color/layout/aesthetics, see `references/figure_design.md` + `figure_aesthetics.md` + `figure_layout.md`. Assumes you know basic LaTeX.

## When to use Beamer
- Heavy math/equations, code listings, algorithm pseudocode
- Plain-text source → version-control friendly, reproducible
- Need publication-quality typography (PDF vector output)

## Theme & color selection

| Theme | Style | Use for |
|---|---|---|
| `default`, `Copenhagen` | Clean / minimal | Most conference talks |
| `Madrid`, `Boadilla` | Professional, footer | General academic |
| `Berlin`, `CambridgeUS` | Section nav in header | Multi-section seminars |
| `Singapore`, `Rochester` | Ultra-minimal | Lightning talks |
| `Pittsburgh` | Traditional academic | Defenses |

```latex
\usetheme{Madrid}
\usecolortheme{default}   % blue | beaver(red) | seagull(gray) | crane(orange) | albatross(dark)
\usefonttheme{professionalfonts}
```

**Clean minimal setup (recommended baseline)**:
```latex
\usetheme{default}
\setbeamertemplate{navigation symbols}{}   % kill default nav arrows
\setbeamertemplate{footline}[frame number] % page number only
\setbeamertemplate{itemize items}[circle]
\setbeamertemplate{blocks}[rounded][shadow=false]
% bind structure color to your palette (see figure_aesthetics.md for hex choices)
\definecolor{accent}{RGB}{0,115,178}
\setbeamercolor{structure}{fg=accent}
\setbeamercolor{frametitle}{fg=accent,bg=white}
```

## Chinese support (xelatex + ctex) — REQUIRED for any Chinese text

`pdflatex` cannot render Chinese reliably. Use **xelatex** with the `ctex` package:

```latex
\documentclass[UTF8]{ctexart}       % or \documentclass{beamer} + \usepackage[UTF8]{ctex}
\usepackage{ctex}                    % after \documentclass{beamer}
% ctex auto-picks a system CJK font; for finer control:
\setCJKmainfont{SimSun}              % Windows: SimSun / SimHei / Microsoft YaHei
\setCJKsansfont{Microsoft YaHei}     % macOS: PingFang SC; Linux: Noto Sans CJK SC
```

**Compile with xelatex** (not pdflatex):
```bash
xelatex presentation.tex
# bibliography still needs biber:
xelatex presentation.tex && biber presentation && xelatex presentation.tex && xelatex presentation.tex
```

> Mixed CN/EN: keep English in `\texttt` / `\mathrm` for math; CJK fonts have no math glyphs.

## Compile commands

| Task | Command |
|---|---|
| Standard | `pdflatex presentation.tex` |
| + bibliography | `pdflatex → biber → pdflatex → pdflatex` |
| Automated (recommended) | `latexmk -pdf presentation.tex` |
| Continuous preview | `latexmk -pdf -pvc presentation.tex` |
| Chinese / system fonts | `xelatex presentation.tex` |
| Better Unicode | `lualatex presentation.tex` |
| Output dir | `pdflatex -output-directory=build presentation.tex` |
| Draft (fast, boxes) | `\documentclass[draft]{beamer}` or `pdflatex -draftmode` |

## Template variables (for conference/defense/seminar templates)

The templates in `assets/beamer_template_{conference,seminar,defense}.tex` expose these variables in the preamble:

| Variable | Purpose |
|---|---|
| `\title{}` / `\subtitle{}` | Title slide |
| `\author{}` / `\institute{}` | Author + affiliation |
| `\date{}` | Date or `\today` |
| `\usetheme{}` / `\usecolortheme{}` | Overall look |
| `\definecolor{accent}{RGB}{}` | Single accent color (bind to `structure`) |
| `\graphicspath{{./figures/}}` | Figure search path |

## Common errors (quick fixes)

| Symptom | Fix |
|---|---|
| `Verbatim environment in frame` | Add `[fragile]` to the frame (required for `lstlisting`, `verbatim`, `minted`) |
| `Option clash for package X` | Load the package once in the preamble, with options |
| `File 'figure.pdf' not found` | Check `\graphicspath`, use PDF (vector) not raster when possible |
| Chinese shows as tofu boxes | Switch engine to `xelatex` + `\usepackage{ctex}` |
| Overlay `<n->` not working | Confirm syntax: `<2->` = "from slide 2 on"; `<2-4>` = slides 2–4 |
| Compilation stalls / loops | Run `latexmk -c` to clear aux, recompile |

## Beamer-specific overlays (the only animation that matters)

Beamer's overlay system is its unique strength — use sparingly for build-ups, not decoration:
```latex
\begin{itemize}[<+->]   % each item appears one-by-one
  \item First
  \item Second
\end{itemize}
% or inline:
\only<2>{shown only on slide 2}
\uncover<3->{appears slide 3+, reserves space}
\pause                     % simple sequential reveal
```

## Backup slides & appendix (don't count in numbering)
```latex
\appendix                  % after \begin{document}, after main content
\begin{frame}{Extra Data}  % slides after \appendix are "backup"
  ...
\end{frame}
```

## Handouts & speaker notes
```latex
\documentclass[handout]{beamer}          % flattens overlays → one frame per slide
\usepackage{pgfpages}
\setbeameroption{show notes on second screen=right}  % presenter-view notes
\note{ Speaker-only text inside any \begin{frame}... }
\pgfpagesuselayout{2 on 1}[a4paper,border shrink=5mm] % 2-up handout
```

## When NOT to use Beamer
- Collaborators are non-LaTeX → use PowerPoint
- Need pixel-precise custom graphics / heavy animation → PowerPoint
- Rapid visual prototyping → PowerPoint

See `assets/beamer_template_conference.tex` for a complete working template, and `texdoc beamer` for the full manual.
