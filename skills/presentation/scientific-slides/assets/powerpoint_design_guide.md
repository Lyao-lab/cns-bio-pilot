# PowerPoint Design Guide (PPT-specific only)

> Covers **only what is unique to PowerPoint**: slide masters, animation discipline, speaker notes, PPT-specific units/dimensions. Default implementation: **python-pptx** (`scripts/build_deck.py`); PptxGenJS (JS) is an alternative path. For general typography/color/layout, see `references/figure_guide.md`.

## Two creation paths via the pptx skill

**1. Programmatic (html2pptx / PptxGenJS)** — build from scratch with code. Best for custom data viz.
**2. Template-based** — start from an existing `.pptx`, rearrange + replace text via scripts.

Full docs: `document-skills/pptx/SKILL.md`, `pptx/html2pptx.md`, `pptx/ooxml.md`.

## PptxGenJS API essentials (JavaScript)

**Units**: PPT uses inches. 72 pt = 1 in. Position `(x,y)` and size `(w,h)` are in inches from top-left.
**16:9 canvas**: 10" × 5.625" (720pt × 405pt). **4:3**: 10" × 7.5".

```javascript
const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_16x9";
const slide = pptx.addSlide();

// Text — array of strings = bullets; object = single styled run
slide.addText("Slide Title", { x:0.5, y:0.5, w:9, h:0.5, fontSize:32, bold:true, color:"0A9396" });
slide.addText(["Bullet 1","Bullet 2"], { x:0.5, y:1.5, w:9, h:3, fontSize:24, bullet:true });

// Image (figure) — size the box, image scales to fit
slide.addImage({ path:"figure.png", x:0.5, y:1.5, w:9, h:4 });

// Table
slide.addTable([
  [{ text:"Method", options:{bold:true} }, { text:"Acc", options:{bold:true} }],
  ["A","0.92"], ["B","0.85"]
], { x:2, y:2, w:6, fontSize:20, fill:{color:"F5F5F5"} });

// Native chart (bar/line/pie/scatter) — PPT stays editable, unlike image charts
slide.addChart(pptx.ChartType.bar, [
  { name:"Control", labels:["m1","m2"], values:[45,67] },
  { name:"Treat", labels:["m1","m2"], values:[52,78] }
], { x:1, y:1.5, w:8, h:4, chartColors:["0A9396","EE6C4D"], showLegend:true });

// Background color block (title/closing slides)
slide.background = { color:"0A9396" };

pptx.writeFile({ fileName:"presentation.pptx" });
```

> **Equations**: PPT has no native LaTeX math. Render to PNG (matplotlib `$...$`, or LaTeX → image) then `addImage`.

## Slide master discipline

Define **4–5 master layouts** once, reuse everywhere: title, content (bullets), two-column, full-figure, closing. Set default fonts/colors/spacing + placeholders for logo/footer on the master so every slide inherits them. Avoid ad-hoc per-slide formatting — it breaks consistency. (Palette/contrast values live in `figure_guide.md`.)

## Animation rules (PPT-specific)

PPT has rich animation — Beamer doesn't. Use it sparingly.

| Use | Avoid |
|---|---|
| Progressive bullet reveal (`Appear`) | Decoration / entertainment |
| Building a complex figure panel-by-panel (`Fade`) | Every single slide |
| Emphasizing one key finding (`Wipe`) | Fly-in / bounce / spin / 3D |

- **Duration**: 0.2–0.3s (fast). **Trigger**: on click, not automatic.
- **Transitions**: consistent throughout — `None`, `Fade`, or `Push` only. Duration 0.3–0.5s.

## Speaker notes

```javascript
slide.addNotes("Speaker-only text: emphasize X; expect question on Y; credit collaborator Z.");
```
Notes don't show on the projected slide — use them to carry detail you won't put in bullets (citations, backup numbers, transition cues).

## Template-script workflow

本 skill 使用 `outline.json` → `build_deck.py` 的 source-first 工作流，不依赖模板脚本。
如需修改已有 .pptx，使用 python-pptx 直接操作（参考 `scripts/build_deck.py` 中的 API 用法）。

## Visual validation (mandatory before presenting)

Run `python scripts/qa_deck.py output.pptx` (geometry/overflow/font check) +
`python scripts/validate_presentation.py output.pptx` (content/placeholder check), then visually check each slide:
- [ ] Text not cut off / not too small
- [ ] No element overlap
- [ ] Figures clear and properly sized
- [ ] Alignment correct

**Common PPT-specific fixes**:
- Text overflow → enlarge text box or shorten text (don't shrink below readable size)
- Blurry figure → use higher-res image (300 DPI; prefer vector PDF/SVG → render to PNG at slide scale)
- Colors shift on projector → raise contrast, test on real hardware beforehand
- File too large → compress images

## When to choose PPT over Beamer
- Non-LaTeX collaborators
- Pixel-precise custom graphics / richer animation
- Rapid visual prototyping

See `document-skills/pptx/SKILL.md` for the full PptxGenJS reference and `pptx/html2pptx.md` for the HTML-to-PPTX workflow.
