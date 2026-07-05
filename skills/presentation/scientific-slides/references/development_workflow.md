# Workflow for Presentation Development

> 下沉自原 SKILL.md 的「Workflow for Presentation Development」6 阶段 + 「Integration with Other Skills」+ 「Quick Start Guide」。

## Stage 1: Planning (Before Creating Slides)

**Define Context**:
1. What type of talk? (Conference, seminar, defense, etc.)
2. How long? (Duration in minutes)
3. Who is the audience? (Specialists, general, mixed)
4. What's the venue? (Room size, A/V setup, virtual/in-person)
5. What happens after? (Q&A, discussion, networking)

**Research and Literature Review** (Use research-lookup skill):
1. **Search for background literature**: Find 5-10 key papers establishing context
2. **Identify knowledge gaps**: Use research-lookup to find what's unknown
3. **Locate comparison studies**: Find papers with similar methods or results
4. **Gather supporting citations**: Collect papers supporting your interpretations
5. **Build reference list**: Create .bib file or citation list for slides
6. **Note key findings to cite**: Document specific results to reference

**Develop Content Outline**:
1. Identify 1-3 core messages
2. Select key findings to present
3. Choose essential figures (typically 3-6 for 15-min talk)
4. Plan narrative arc with proper citations
5. Allocate time by section

**Example Outline for 15-Minute Talk**:
```
1. Title (30 sec)
2. Hook: Compelling problem (60 sec) [Cite 1-2 papers via research-lookup]
3. Background (90 sec) [Cite 3-4 key papers establishing context]
4. Research question (45 sec) [Cite papers showing gap]
5. Methods overview (2 min)
6-8. Main result 1 (3 min, 3 slides)
9-10. Main result 2 (2 min, 2 slides)
11-12. Result 3 or validation (2 min, 2 slides)
13-14. Discussion and implications (2 min) [Compare to 2-3 prior studies]
15. Conclusions (45 sec)
16. Acknowledgments (15 sec)

NOTE: Use research-lookup to find papers for background (slides 2-4)
and discussion (slides 13-14) BEFORE creating slides.
```

## Stage 2: Design and Creation

**Choose Implementation Method**:

**Option A: PowerPoint (via PPTX skill)**
1. Read `assets/powerpoint_design_guide.md`
2. Read `document-skills/pptx/SKILL.md`
3. Choose approach (programmatic or template-based)
4. Create master slides with consistent design
5. Build presentation following outline

**Option B: LaTeX Beamer**
1. Read `references/beamer_guide.md`
2. Select appropriate template from `assets/`
3. Customize theme and colors
4. Write content in LaTeX
5. Compile to PDF

**Design Considerations** (Make It Visually Appealing):
- **Select MODERN color palette**: Match your topic (biotech=vibrant, physics=sleek, health=warm)
  - Use pptx skill's color palette examples (Teal & Coral, Bold Red, Deep Purple & Emerald, etc.)
  - NOT just default blue/gray themes
  - 3-5 colors with high contrast
- **Choose clean fonts**: Sans-serif, large sizes (24pt+ body)
- **Plan visual elements**: What images, diagrams, icons for each slide?
- **Create varied layouts**: Mix full-figure, two-column, text-overlay (not all bullets)
- **Design section dividers**: Visual breaks with striking graphics
- **Plan animations/builds**: Control information flow for complex slides
- **Add visual interest**: Background images, color blocks, shapes, icons

## Stage 3: Content Development

**Populate Slides** (Visual-First Strategy):
1. **Start with visuals**: Plan which figures, images, diagrams for each key point
2. **Use research-lookup extensively**: Find 8-15 papers for proper citations
3. **Create visual backbone first**: Add all figures, charts, images, diagrams
4. **Add minimal text as support**: Bullet points complement visuals, don't replace them
5. **Design section dividers**: Visual breaks with images or graphics (not just text)
6. **Polish title/closing**: Make visually striking, include contact info
7. **Add transitions/builds**: Control information flow

**VISUAL CONTENT REQUIREMENTS** (Make Slides Engaging):
- **Images**: Use high-quality photos, illustrations, conceptual graphics
- **Icons**: Visual representations of concepts (not decoration)
- **Diagrams**: Flowcharts, schematics, process diagrams
- **Figures**: Simplified research figures with LARGE labels (18-24pt)
- **Charts**: Clean data visualizations with clear messages
- **Graphics**: Visual metaphors, conceptual illustrations
- **Color blocks**: Use colored shapes to organize content visually
- Target: MINIMUM 1-2 strong visual elements per slide

**Scientific Content** (Research-Backed):
- **Citations**: Use research-lookup EXTENSIVELY to find relevant papers
  - Introduction: Cite 3-5 papers establishing context and gap
  - Background: Show key prior work visually (not just cite)
  - Discussion: Cite 3-5 papers for comparison with your results
  - Use author-year format (Smith et al., 2023) for readability
  - Citations establish credibility and scientific rigor
- **Figures**: Simplified from papers, LARGE labels (18-24pt minimum)
- **Equations**: Large, clear, explain each term (use sparingly)
- **Tables**: Minimal, highlight key comparisons (not data dumps)
- **Code/Algorithms**: Use syntax highlighting, keep brief

**Text Guidelines** (Less is More):
- Bullet points, NEVER paragraphs
- 3-4 bullets per slide (max 6 only if essential)
- 4-6 words per bullet (shorter than 6×6 rule)
- Key terms in bold
- Text is SUPPORTING ROLE, visuals are stars
- Use builds to control pacing

## Stage 4: Visual Validation

**Generate Images**:
```bash
# Convert PDF to images
python scripts/pdf_to_images.py presentation.pdf review/slides

# Or create thumbnail grid
python ../document-skills/pptx/scripts/thumbnail.py presentation.pptx review/grid
```

**Systematic Review**:
1. View each slide image
2. Check against issue checklist
3. Document problems with slide numbers
4. Test readability from distance (view at 50% size)

**Common Issues to Fix**:
- Text extending beyond boundaries
- Figures overlapping with text
- Font sizes too small
- Poor contrast
- Misalignment

**Iteration**:
1. Fix identified issues in source
2. Regenerate PDF/presentation
3. Convert to images again
4. Re-inspect
5. Repeat until clean

## Stage 5: Practice and Refinement

**Practice Schedule**:
- Run 1: Rough draft (will run long)
- Run 2: Smooth transitions
- Run 3: Exact timing
- Run 4: Final polish
- Run 5+: Maintenance (day before, morning of)

**What to Practice**:
- Full talk with timer
- Difficult explanations
- Transitions between sections
- Opening and closing (until flawless)
- Anticipated questions

**Refinement Based on Practice**:
- Cut slides if running over
- Expand explanations if unclear
- Adjust wording for clarity
- Mark timing checkpoints
- Prepare backup slides

## Stage 6: Final Preparation

**Technical Checks**:
- [ ] Multiple copies saved (laptop, cloud, USB)
- [ ] Works on presentation computer
- [ ] Adapters/cables available
- [ ] Backup PDF version
- [ ] Tested with projector (if possible)

**Content Final**:
- [ ] No typos or errors
- [ ] All figures high quality
- [ ] Slide numbers correct
- [ ] Contact info on final slide
- [ ] Backup slides ready

**Delivery Prep**:
- [ ] Notes prepared (if using)
- [ ] Timer/phone ready
- [ ] Water available
- [ ] Business cards/handouts
- [ ] Comfortable with material (3+ practices)

## Integration with Other Skills

**Research Lookup** (Critical for Scientific Presentations):
- **Background development**: Search literature to build introduction context
- **Citation gathering**: Find key papers to cite in your talk
- **Gap identification**: Identify what's unknown to motivate research
- **Prior work comparison**: Find papers to compare your results against
- **Supporting evidence**: Locate literature supporting your interpretations
- **Question preparation**: Find papers that might inform Q&A responses
- **Always use research-lookup** when developing any scientific presentation to ensure proper context and citations

**Scientific Writing**:
- Convert paper content to presentation format
- Extract key findings and simplify
- Use same figures (but redesigned for slides)
- Maintain consistent terminology

**PPTX Skill**:
- Use for PowerPoint creation and editing
- Leverage scripts for template workflows
- Use thumbnail generation for validation
- Reference html2pptx for programmatic creation

**Data Visualization**:
- Create presentation-appropriate figures
- Simplify complex visualizations
- Ensure readability from distance
- Use progressive disclosure

## Quick Start Guide

### For a 15-Minute Conference Talk (PDF Workflow - Recommended)

1. **Research & Plan** (45 minutes):
   - **Use research-lookup** to find 8-12 relevant papers for citations
   - Build reference list (background, comparison studies)
   - Outline content (intro → methods → 2-3 key results → conclusion)
   - **Create detailed plan for each slide** (title, key points, visual elements)
   - Target 15-18 slides

2. **Generate Slides with Nano Banana Pro** (1-2 hours):

   **Important: Use consistent formatting, attach previous slides, and include citations!**

   ```bash
   # Title slide (establishes style - default author: K-Dense)
   python scripts/generate_slide_image.py "Title slide: 'Your Research Title'. Conference name, K-Dense. FORMATTING GOAL: [your color scheme], minimal professional design, no decorative elements, clean and corporate." -o slides/01_title.png

   # Introduction slide with citations (attach previous for consistency)
   python scripts/generate_slide_image.py "Slide titled 'Why This Matters'. Three key points with simple icons. CITATIONS: Include at bottom: (Smith et al., 2023; Jones et al., 2024). FORMATTING GOAL: Match attached slide style exactly." -o slides/02_intro.png --attach slides/01_title.png

   # Continue for each slide (always attach previous, include citations where relevant)
   python scripts/generate_slide_image.py "Slide titled 'Methods'. Key methodology points. CITATIONS: (Based on Chen et al., 2022). FORMATTING GOAL: Match attached slide style exactly." -o slides/03_methods.png --attach slides/02_intro.png

   # Combine to PDF
   python scripts/slides_to_pdf.py slides/*.png -o presentation.pdf
   ```

3. **Review & Iterate** (30 minutes):
   - Open the PDF and review each slide
   - Regenerate any slides that need improvement
   - Re-combine to PDF

4. **Practice** (2-3 hours):
   - Practice 3-5 times with timer
   - Aim for 13-14 minutes (leave buffer)
   - Record yourself, watch playback
   - **Prepare for questions** (use research-lookup to anticipate)

5. **Finalize** (30 minutes):
   - Generate backup/appendix slides if needed
   - Save multiple copies
   - Test on presentation computer

Total time: ~5-6 hours for quality AI-generated presentation

### Alternative: PowerPoint Workflow

If you need editable slides (e.g., for company templates):

1. **Plan slides** as above
2. **Generate visuals** with `--visual-only` flag:
   ```bash
   python scripts/generate_slide_image.py "diagram description" -o figures/fig1.png --visual-only
   ```
3. **Build PPTX** using the PPTX skill with generated images
4. **Add text** separately using PPTX workflow

See `document-skills/pptx/SKILL.md` for complete PowerPoint workflow.
