---
name: scientific-slides
description: Build slide decks and presentations for research talks. Use this for making PowerPoint slides, conference presentations, seminar talks, research presentations, thesis defense slides, or any scientific talk. Provides slide structure, design templates, timing guidance, and visual validation. Works with PowerPoint and LaTeX Beamer.
allowed-tools: Read Write Edit Bash
license: MIT license
metadata:
    skill-author: K-Dense Inc.
---

# Scientific Slides

> **路由层 SKILL.md**——本文件只放「该干啥 + 代码骨架 + 索引」。深度细节（8 大能力、6 阶段工作流、坑、脚本/提示词全集）下沉到 `references/`，按需加载。

## Overview

Scientific presentations are a critical medium for communicating research, sharing findings, and engaging with academic and professional audiences. This skill provides comprehensive guidance for creating effective scientific presentations, from structure and content development to visual design and delivery preparation.

**Key Focus**: Oral presentations for conferences, seminars, defenses, and professional talks.

**CRITICAL DESIGN PHILOSOPHY**: Scientific presentations should be VISUALLY ENGAGING and RESEARCH-BACKED. Avoid dry, text-heavy slides at all costs. Great scientific presentations combine:
- **Compelling visuals**: High-quality figures, images, diagrams (not just bullet points)
- **Research context**: Proper citations from research-lookup establishing credibility
- **Minimal text**: Bullet points as prompts, YOU provide the explanation verbally
- **Professional design**: Modern color schemes, strong visual hierarchy, generous white space
- **Story-driven**: Clear narrative arc, not just data dumps

**Remember**: Boring presentations = forgotten science. Make your slides visually memorable while maintaining scientific rigor through proper citations.

## When to Use This Skill

Use this skill when:
- Preparing conference presentations (5-20 minutes)
- Developing academic seminars (45-60 minutes)
- Creating thesis or dissertation defense presentations
- Designing grant pitch presentations
- Preparing journal club presentations
- Giving research talks at institutions or companies
- Teaching or tutorial presentations on scientific topics

**When NOT to use this skill**:
- Internal lab-meeting / progress updates → use `presentation/lab-meeting-slides` instead
- Writing paper Methods / Results / Figure legends → use `presentation/methods-writer`, `presentation/results-writer`, `presentation/figure-legend-writer`
- Making standalone publication figures (not slides) → use `visualization/multi-panel-figures`
- Drawing mechanism/flowchart schematics → use `visualization/scientific-schematics`

## Slide Generation with Nano Banana Pro

**This skill uses Nano Banana Pro AI to generate stunning presentation slides automatically.**

There are two workflows depending on output format. Both share the same planning step.

### Default Workflow: PDF Slides (Recommended)

Generate each slide as a complete image using Nano Banana Pro, then combine into a PDF. This produces the most visually stunning results.

**How it works:**
1. **Plan the deck**: Create a detailed plan for each slide (title, key points, visual elements)
2. **Generate slides**: Call Nano Banana Pro for each slide to create complete slide images
3. **Combine to PDF**: Assemble slide images into a single PDF presentation

**Step 1: Plan Each Slide**

Before generating, create a detailed plan for your presentation:

```markdown
# Presentation Plan: Introduction to Machine Learning

## Slide 1: Title Slide
- Title: "Machine Learning: From Theory to Practice"
- Subtitle: "AI Conference 2025"
- Speaker: Dr. Jane Smith, University of XYZ
- Visual: Modern abstract neural network background

## Slide 2: Introduction
- Title: "Why Machine Learning Matters"
- Key points: Industry adoption, breakthrough applications, future potential
- Visual: Icons showing different ML applications (healthcare, finance, robotics)

## Slide 3: Core Concepts
- Title: "The Three Types of Learning"
- Content: Supervised, Unsupervised, Reinforcement
- Visual: Three-part diagram showing each type with examples

... (continue for all slides)
```

**Step 2: Generate Each Slide**

Use the `generate_slide_image.py` script to create each slide.

**CRITICAL: Formatting Consistency Protocol**

To ensure unified formatting across all slides in a presentation:

1. **Define a Formatting Goal** at the start of your presentation and include it in EVERY prompt:
   - Color scheme (e.g., "dark blue background, white text, gold accents")
   - Typography style (e.g., "bold sans-serif titles, clean body text")
   - Visual style (e.g., "minimal, professional, corporate aesthetic")
   - Layout approach (e.g., "generous white space, left-aligned content")

2. **Always attach the previous slide** when generating subsequent slides using `--attach`:
   - This allows Nano Banana Pro to see and match the existing style
   - Creates visual continuity throughout the deck
   - Ensures consistent colors, fonts, and design language

3. **Default author is "K-Dense"** unless another name is specified

4. **Include citations directly in the prompt** for slides that reference research:
   - Add citations in the prompt text so they appear on the generated slide
   - Use format: "Include citation: (Author et al., Year)" or "Show reference: Author et al., Year"
   - For multiple citations, list them all in the prompt
   - Citations should appear in small text at the bottom of the slide or near relevant content

5. **Attach existing figures/data for results slides** (CRITICAL for data-driven presentations):
   - When creating slides about results, ALWAYS check for existing figures in:
     - The working directory (e.g., `figures/`, `results/`, `plots/`, `images/`)
     - User-provided input files or directories
     - Any data visualizations, charts, or graphs relevant to the presentation
   - Use `--attach` to include these figures so Nano Banana Pro can incorporate them:
     - Attach the actual data figure/chart for results slides
     - Attach relevant diagrams for methodology slides
     - Attach logos or institutional images for title slides
   - When attaching data figures, describe what you want in the prompt:
     - "Create a slide presenting the attached results chart with key findings highlighted"
     - "Build a slide around this attached figure, add title and bullet points explaining the data"
     - "Incorporate the attached graph into a results slide with interpretation"
   - **Before generating results slides**: List files in the working directory to find relevant figures
   - Multiple figures can be attached: `--attach fig1.png --attach fig2.png`

**Example with formatting consistency, citations, and figure attachments:**

```bash
# Title slide (first slide - establishes the style)
python scripts/generate_slide_image.py "Title slide for presentation: 'Machine Learning: From Theory to Practice'. Subtitle: 'AI Conference 2025'. Speaker: K-Dense. FORMATTING GOAL: Dark blue background (#1a237e), white text, gold accents (#ffc107), minimal design, sans-serif fonts, generous margins, no decorative elements." -o slides/01_title.png

# Content slide with citations (attach previous slide for consistency)
python scripts/generate_slide_image.py "Presentation slide titled 'Why Machine Learning Matters'. Three key points with simple icons: 1) Industry adoption, 2) Breakthrough applications, 3) Future potential. CITATIONS: Include at bottom in small text: (LeCun et al., 2015; Goodfellow et al., 2016). FORMATTING GOAL: Match attached slide style - dark blue background, white text, gold accents, minimal professional design, no visual clutter." -o slides/02_intro.png --attach slides/01_title.png

# Background slide with multiple citations
python scripts/generate_slide_image.py "Presentation slide titled 'Deep Learning Revolution'. Key milestones: ImageNet breakthrough (2012), transformer architecture (2017), GPT models (2018-present). CITATIONS: Show references at bottom: (Krizhevsky et al., 2012; Vaswani et al., 2017; Brown et al., 2020). FORMATTING GOAL: Match attached slide style exactly - same colors, fonts, minimal design." -o slides/03_background.png --attach slides/02_intro.png

# RESULTS SLIDE - Attach actual data figure from working directory
# First, check what figures exist: ls figures/ or ls results/
python scripts/generate_slide_image.py "Presentation slide titled 'Model Performance Results'. Create a slide presenting the attached accuracy chart. Key findings to highlight: 1) 95% accuracy achieved, 2) Outperforms baseline by 12%, 3) Consistent across test sets. CITATIONS: Include at bottom: (Our results, 2025). FORMATTING GOAL: Match attached slide style exactly." -o slides/04_results.png --attach slides/03_background.png --attach figures/accuracy_chart.png

# RESULTS SLIDE - Multiple figures comparison
python scripts/generate_slide_image.py "Presentation slide titled 'Before vs After Comparison'. Build a side-by-side comparison slide using the two attached figures. Left: baseline results, Right: our improved results. Add brief labels explaining the improvement. FORMATTING GOAL: Match attached slide style exactly." -o slides/05_comparison.png --attach slides/04_results.png --attach figures/baseline.png --attach figures/improved.png

# METHODOLOGY SLIDE - Attach existing diagram
python scripts/generate_slide_image.py "Presentation slide titled 'System Architecture'. Present the attached architecture diagram with brief explanatory bullet points: 1) Input processing, 2) Model inference, 3) Output generation. FORMATTING GOAL: Match attached slide style exactly." -o slides/06_architecture.png --attach slides/05_comparison.png --attach diagrams/system_architecture.png
```

**IMPORTANT: Before creating results slides, always:**
1. List files in working directory: `ls -la figures/` or `ls -la results/`
2. Check user-provided directories for relevant figures
3. Attach ALL relevant figures that should appear on the slide
4. Describe how Nano Banana Pro should incorporate the attached figures

**Prompt Template:**

Include these elements in every prompt (customize as needed):
```
[Slide content description]
CITATIONS: Include at bottom: (Author1 et al., Year; Author2 et al., Year)
FORMATTING GOAL: [Background color], [text color], [accent color], minimal professional design, no decorative elements, consistent with attached slide style.
```

**Step 3: Combine to PDF**

```bash
# Combine all slides into a PDF presentation
python scripts/slides_to_pdf.py slides/*.png -o presentation.pdf
```

### PPT Workflow: PowerPoint with Generated Visuals

When creating PowerPoint presentations, use Nano Banana Pro to generate images and figures for each slide, then add text separately using the PPTX skill.

**How it works:**
1. **Plan the deck**: Create content plan for each slide
2. **Generate visuals**: Use Nano Banana Pro with `--visual-only` flag to create images for slides
3. **Build PPTX**: Use the PPTX skill (html2pptx or template-based) to create slides with generated visuals and separate text

**Step 1: Generate Visuals for Each Slide**

```bash
# Generate a figure for the introduction slide
python scripts/generate_slide_image.py "Professional illustration showing machine learning applications: healthcare diagnosis, financial analysis, autonomous vehicles, and robotics. Modern flat design, colorful icons on white background." -o figures/ml_applications.png --visual-only

# Generate a diagram for the methods slide
python scripts/generate_slide_image.py "Neural network architecture diagram showing input layer, three hidden layers, and output layer. Clean, technical style with node connections. Blue and gray color scheme." -o figures/neural_network.png --visual-only

# Generate a conceptual graphic for results
python scripts/generate_slide_image.py "Before and after comparison showing improvement: left side shows cluttered data, right side shows organized insights. Arrow connecting them. Professional business style." -o figures/results_visual.png --visual-only
```

**Step 2: Build PowerPoint with PPTX Skill**

Use the PPTX skill's html2pptx workflow to create slides that include:
- Generated images from step 1
- Title and body text added separately
- Professional layout and formatting

See `document-skills/pptx/SKILL.md` for complete PPTX creation documentation.

## Visual Enhancement with Scientific Schematics

For complex technical diagrams (circuit diagrams, chemical structures, publication-quality schematics requiring scientific accuracy review), use the **scientific-schematics** skill instead of Nano Banana Pro:

```bash
python scripts/generate_schematic.py "your diagram description" -o figures/output.png
```

## References 索引（按需加载，不要一次全读）

> 以下文件存于 `references/`。本 SKILL.md 已覆盖路由与代码骨架；只在需要深度细节时读对应文件。

| 需要什么 | 读哪个文件 |
|---|---|
| 8 大能力详解（Structure / Design Principles / Data Viz / Talk-Specific / Implementation / Visual Review / Timing / QA） | `references/core_capabilities.md` |
| 6 阶段开发工作流 + 跨 skill 集成 + 15 分钟会议 talk Quick Start | `references/development_workflow.md` |
| Content / Design / Timing 三类常见坑 + 10 条核心原则总结 | `references/pitfalls.md` |
| `generate_slide_image.py` / `slides_to_pdf.py` 脚本完整参数 + 提示词写作全集 + 工具清单 + Reference/Assets 索引 | `references/nano_banana_pro_reference.md` |
| 详细结构（所有 talk 类型、开场/结尾、过渡） | `references/presentation_structure.md` |
| 排版 / 配色 / 布局 / 无障碍 / 视觉层级 | `references/slide_design_principles.md` |
| 把期刊 figure 改成 slide-friendly | `references/data_visualization_slides.md` |
| 各 talk 类型（会议/研讨会/答辩/基金/Journal Club）专项指导 | `references/talk_types_guide.md` |
| LaTeX Beamer 完整文档、主题、定制、编译 | `references/beamer_guide.md` |
| PDF→图片、系统化审查、问题记录、迭代改进 | `references/visual_review_workflow.md` |

## Assets（模板与指南）

### Templates
- **`assets/beamer_template_conference.tex`**: 15-minute conference talk template
- **`assets/beamer_template_seminar.tex`**: 45-minute academic seminar template
- **`assets/beamer_template_defense.tex`**: Dissertation defense template

### Guides
- **`assets/powerpoint_design_guide.md`**: Complete PowerPoint design and implementation guide
- **`assets/timing_guidelines.md`**: Comprehensive timing, pacing, and practice strategies

## 核心原则速记（详见 `references/pitfalls.md`）

1. **Visual-First Design**: Every slide needs strong visual element - avoid text-only slides
2. **Research-Backed**: Use research-lookup to find 8-15 papers, cite 3-5 in intro, 3-5 in discussion
3. **Modern Aesthetics**: Choose contemporary color palette matching topic, not default themes
4. **Minimal Text**: 3-4 bullets, 4-6 words each (24-28pt font), let visuals tell story
5. **Structure**: Follow story arc, spend 40-50% on results
6. **High Contrast**: 7:1 preferred for professional appearance
7. **Varied Layouts**: Mix full-figure, two-column, visual overlays (not all bullets)
8. **Timing**: Practice 3-5 times, ~1 slide per minute, never skip conclusions
9. **Validation**: Visual review workflow to catch overflow and overlap
10. **White Space**: 40-50% of slide empty for visual breathing room

**Remember**:
- **Boring = Forgotten**: Dry, text-heavy slides fail to communicate your science
- **Visual + Research = Impact**: Combine compelling visuals with research-backed context
- **You are the presentation, slides are visual support**: They should enhance, not replace your talk

## 前置依赖（从哪来）

- **研究数据 / 结果图** → 已发表的 figure（`visualization/multi-panel-figures` 产出的 PNG/PDF）或工作目录 `figures/`、`results/` 下的图表，结果类 slide 用 `--attach` 嵌入
- **文献与引用** → 用 research-lookup skill 找 8-15 篇背景/对比文献（intro 引 3-5，discussion 引 3-5）
- **论文初稿**（可选）→ `presentation/results-writer` / `presentation/methods-writer` 写好的文字，可改写成 slide 文案
- **技术示意图**（可选）→ `visualization/scientific-schematics` 生成的机制图/流程图，可 `--attach` 进 slide
- **环境**：`OPENROUTER_API_KEY` 环境变量（Nano Banana Pro），见 `references/nano_banana_pro_reference.md`

## 何时离开本 skill（去哪）

- 需要可编辑 PPTX（公司模板 / 后期改字）→ `document-skills/pptx`（html2pptx 工作流）
- 内部组会 / 进度汇报（非正式）→ `presentation/lab-meeting-slides`
- 把 talk 内容写成论文 Methods / Results / 图注 → `presentation/methods-writer` / `presentation/results-writer` / `presentation/figure-legend-writer`
- 单独制作发表级 figure（不是 slide）→ `visualization/multi-panel-figures`
- 复杂技术示意图（电路、化学结构、需科学准确性审查）→ `visualization/scientific-schematics`
- 论文图形摘要 → `visualization/graphical-abstract`
- 完成后建议跑 `python scripts/validate_presentation.py presentation.pdf --duration <N>` 校验页数/字体/编译
