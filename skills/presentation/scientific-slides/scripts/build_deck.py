#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_deck.py — outline.json → .pptx 渲染器（python-pptx，无 AI API 依赖）

用法：
    python build_deck.py outline.json -o presentation.pptx
    python build_deck.py outline.json -o out.pptx --preset cns-bio-light

吸收 siril9/presentation-skill 的 source-first 范式 + davila7 的 DESIGN 常量。
"""
import argparse, json, sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# ---- Preset（生信专用 cns-bio-light）----
PRESETS = {
    "cns-bio-light": {
        "bg": RGBColor(0xFF,0xFF,0xFF),
        "title": RGBColor(0x1F,0x3A,0x5F),    # Navy
        "accent": RGBColor(0x3D,0x7A,0xAB),    # Blue
        "body": RGBColor(0x33,0x33,0x33),       # Dark grey
        "caption": RGBColor(0x66,0x66,0x66),    # Light grey
        "pass": RGBColor(0x2E,0x8B,0x57),       # Green
        "fail": RGBColor(0xE2,0x5D,0x5D),       # Red
        "warn": RGBColor(0xE8,0xA8,0x38),       # Orange
    }
}

def build(outline_path, output_path, preset_name="cns-bio-light"):
    outline = json.loads(Path(outline_path).read_text(encoding="utf-8"))
    preset = PRESETS.get(preset_name, PRESETS["cns-bio-light"])
    prs = Presentation()
    prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    for sdef in outline.get("slides", []):
        variant = sdef.get("variant","bullets")
        title = sdef.get("title","")
        s = prs.slides.add_slide(blank)
        # 背景填充
        bg = s.background.fill; bg.solid(); bg.fore_color.rgb = preset["bg"]
        # 标题（除 title variant 外都顶部）
        if variant == "title":
            _title_slide(s, sdef, preset)
        elif variant == "section":
            _section_slide(s, title, preset)
        elif variant == "scientific-figure":
            _figure_slide(s, sdef, preset, max_panels=4)
        elif variant == "image-sidebar":
            _image_sidebar(s, sdef, preset)
        elif variant == "results-table":
            _table_slide(s, sdef, preset)
        elif variant == "methods-flow":
            _flow_slide(s, sdef, preset)
        else:  # bullets
            _bullets_slide(s, sdef, preset)

    prs.save(str(output_path))
    print(f"SAVED {output_path} ({len(prs.slides)} slides)")

def _add_text(s, left, top, width, height, text, size, color, bold=False, italic=False, align=PP_ALIGN.LEFT):
    tb = s.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = text
    p.font.size = Pt(size); p.font.color.rgb = color
    p.font.bold = bold; p.font.italic = italic; p.alignment = align
    return tb

def _add_bullets(s, left, top, width, height, bullets, size, color):
    tb = s.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame; tf.word_wrap = True
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.text = "• " + str(b); p.font.size = Pt(size); p.font.color.rgb = color
        p.space_after = Pt(8)

def _title_slide(s, d, preset):
    _add_text(s, Inches(1), Inches(2.5), Inches(11), Inches(1.5),
              d.get("title",""), 40, preset["title"], bold=True, align=PP_ALIGN.CENTER)
    if d.get("subtitle"):
        _add_text(s, Inches(1), Inches(4), Inches(11), Inches(1),
                  d["subtitle"], 20, preset["caption"], align=PP_ALIGN.CENTER)

def _section_slide(s, title, preset):
    _add_text(s, Inches(1), Inches(3), Inches(11), Inches(1.5),
              title, 36, preset["title"], bold=True, align=PP_ALIGN.CENTER)

def _figure_slide(s, d, preset, max_panels=4):
    _add_text(s, Inches(0.5), Inches(0.3), Inches(12), Inches(0.7),
              d.get("title",""), 28, preset["title"], bold=True)
    img = d.get("image")
    if img and Path(img).exists():
        # 限制图片高度不超出可用区域（标题0.3-1.0in + 图 + 图注6.7-7.2in）
        pic = s.shapes.add_picture(img, Inches(0.8), Inches(1.2), width=Inches(7.5))
        max_h = Inches(5.3)  # 1.2 + 5.3 = 6.5，留 0.2 给图注
        if pic.height > max_h:
            ratio = max_h / pic.height
            pic.height = max_h
            pic.width = int(pic.width * ratio)
        if d.get("caption"):
            _add_text(s, Inches(0.8), Inches(6.7), Inches(7.5), Inches(0.5),
                      d["caption"], 10, preset["caption"], italic=True)
    if d.get("bullets"):
        _add_bullets(s, Inches(8.5), Inches(1.2), Inches(4.5), Inches(5.5),
                     d["bullets"], 14, preset["body"])

def _image_sidebar(s, d, preset):
    _add_text(s, Inches(0.5), Inches(0.3), Inches(12), Inches(0.7),
              d.get("title",""), 28, preset["title"], bold=True)
    img = d.get("image")
    if img and Path(img).exists():
        pic = s.shapes.add_picture(img, Inches(0.5), Inches(1.2), width=Inches(7.8))
        max_h = Inches(5.3)
        if pic.height > max_h:
            ratio = max_h / pic.height
            pic.height = max_h; pic.width = int(pic.width * ratio)
        if d.get("caption"):
            _add_text(s, Inches(0.5), Inches(6.7), Inches(7.8), Inches(0.5),
                      d["caption"], 10, preset["caption"], italic=True)
    if d.get("bullets"):
        _add_bullets(s, Inches(8.5), Inches(1.2), Inches(4.5), Inches(5.5),
                     d["bullets"], 14, preset["body"])

def _table_slide(s, d, preset):
    _add_text(s, Inches(0.5), Inches(0.3), Inches(12), Inches(0.7),
              d.get("title",""), 28, preset["title"], bold=True)
    tdef = d.get("table", {})
    headers = tdef.get("headers", []); rows = tdef.get("rows", [])
    if not headers: return
    nrows = len(rows)+1; ncols = len(headers)
    tbl_shape = s.shapes.add_table(nrows, ncols, Inches(1), Inches(1.3), Inches(11), Inches(0.4*nrows))
    tbl = tbl_shape.table
    for j,h in enumerate(headers):
        cell = tbl.cell(0,j); cell.text = str(h)
        cell.text_frame.paragraphs[0].font.size = Pt(12); cell.text_frame.paragraphs[0].font.bold = True
        cell.text_frame.paragraphs[0].font.color.rgb = preset["title"]
    for i,row in enumerate(rows):
        for j,val in enumerate(row):
            cell = tbl.cell(i+1,j); cell.text = str(val)
            cell.text_frame.paragraphs[0].font.size = Pt(11)
            cell.text_frame.paragraphs[0].font.color.rgb = preset["body"]

def _flow_slide(s, d, preset):
    _add_text(s, Inches(0.5), Inches(0.3), Inches(12), Inches(0.7),
              d.get("title",""), 28, preset["title"], bold=True)
    steps = d.get("steps",[])
    if not steps: return
    n = len(steps); step_w = 11.0/n; arrow = " → "
    tb = s.shapes.add_textbox(Inches(1), Inches(3.2), Inches(11), Inches(1))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = arrow.join(steps); p.font.size = Pt(20); p.font.color.rgb = preset["accent"]
    p.alignment = PP_ALIGN.CENTER; p.font.bold = True

def _bullets_slide(s, d, preset):
    _add_text(s, Inches(0.5), Inches(0.3), Inches(12), Inches(0.7),
              d.get("title",""), 28, preset["title"], bold=True)
    _add_bullets(s, Inches(0.8), Inches(1.5), Inches(11.5), Inches(5.5),
                 d.get("bullets",[]), 18, preset["body"])

def main():
    ap = argparse.ArgumentParser(description="outline.json → .pptx (python-pptx, no AI API)")
    ap.add_argument("outline", help="outline.json path")
    ap.add_argument("-o","--output", default="presentation.pptx", help="output .pptx")
    ap.add_argument("--preset", default="cns-bio-light", choices=list(PRESETS))
    a = ap.parse_args()
    build(a.outline, a.output, a.preset)

if __name__ == "__main__":
    main()
