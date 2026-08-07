#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_report.py — report.json → 自包含 report.html 渲染器（纯 Python 标准库，无外部依赖）

用法：
    python build_report.py report.json -o report.html
    python build_report.py report.json            # 默认输出 report.html

输出是单文件 HTML：图片 base64 内联、CSS 内联、无 JS —— 双击打开即看，可邮件/微信分享。
图片支持 PDF（自动转 300dpi PNG 嵌入，需 pymupdf）和 PNG/JPG（直接 base64）。
与 build_deck.py 的 _ensure_png 模式一致；PDF 转换失败时该图渲染为占位提示，不崩。

report.json 支持的 section type：
    summary  段落文本（content，\n 分段）
    findings 无序列表（items，自动识别 [实测]/[文献]/[推断] 标签并着色）
    figure   图片（image 路径 PDF→PNG 后 base64 内联）+ caption 图注
    table    表格（headers + rows，zebra striping）
    ledger   假设台账（Hypothesis | Status | Confidence | Basis，status 着色）
    methods  方法学段落（content，等宽字体灰底框）
"""
import argparse, base64, html, json, sys
from datetime import datetime
from pathlib import Path

# ---- 内联 CSS（学术风，与 PPT preset cns-bio-light 同一套色板）----
CSS = """
  body { font-family: -apple-system, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
         max-width: 900px; margin: 40px auto; padding: 0 20px; color: #333; line-height: 1.7; }
  h1 { color: #1F3A5F; border-bottom: 2px solid #1F3A5F; padding-bottom: 10px; }
  h2 { color: #1F3A5F; margin-top: 2em; }
  .subtitle { color: #666; font-size: 1.1em; margin-top: -0.5em; }
  img { max-width: 100%; height: auto; display: block; margin: 10px auto;
        border: 1px solid #eee; border-radius: 4px; }
  .caption { font-size: 0.9em; color: #666; font-style: italic; text-align: center; }
  table { border-collapse: collapse; width: 100%; margin: 1em 0; }
  th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
  th { background: #1F3A5F; color: white; }
  tr:nth-child(even) { background: #f8f8f8; }
  .finding-item { margin: 0.5em 0; }
  .tag-exp { color: #2E8B57; font-size: 0.8em; font-weight: bold; }
  .tag-lit { color: #3D7AAB; font-size: 0.8em; font-weight: bold; }
  .tag-inf { color: #999; font-size: 0.8em; font-weight: bold; }
  .status-supported { color: #2E8B57; font-weight: bold; }
  .status-refuted { color: #E25D5D; font-weight: bold; }
  .status-inconclusive { color: #E8A838; font-weight: bold; }
  .status-pending { color: #999; }
  .methods-box { background: #f5f5f5; padding: 15px; border-radius: 5px;
                 font-family: "Consolas", monospace; font-size: 0.9em; }
  .img-placeholder { background: #fafafa; border: 1px dashed #ccc; border-radius: 4px;
                     color: #999; text-align: center; padding: 40px 10px; margin: 10px auto; }
  .footer { margin-top: 3em; padding-top: 1em; border-top: 1px solid #eee;
            font-size: 0.8em; color: #999; }
"""


def _image_to_base64(path):
    """图片→base64 data URI。PDF 先转 PNG（pymupdf），PNG/JPG 直接读。

    转换/读取失败返回 None，由调用方渲染占位提示（不崩）。
    """
    p = str(path)
    if p.lower().endswith('.pdf'):
        try:
            import fitz
            doc = fitz.open(p)
            pix = doc[0].get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
            png_path = p.rsplit('.',1)[0] + '_report.png'
            pix.save(png_path); doc.close()
            p = png_path
        except Exception:
            return None  # pymupdf 没装或转换失败，跳过该图
    try:
        with open(p, 'rb') as f:
            data = base64.b64encode(f.read()).decode()
    except OSError:
        return None  # 文件不存在
    ext = p.lower().rsplit('.',1)[-1] if '.' in p else 'png'
    mime = {'png':'image/png','jpg':'image/jpeg','jpeg':'image/jpeg'}.get(ext,'image/png')
    return f'data:{mime};base64,{data}'


def _esc(text):
    """HTML 转义（所有用户文本入口统一走这里，防注入/乱码）。"""
    return html.escape(str(text))


# ---- 6 种 section 渲染器 ----
def _section_summary(s):
    """段落文本，\n 分段。"""
    paras = [p.strip() for p in str(s.get('content','')).split('\n') if p.strip()]
    return ''.join(f'<p>{_esc(p)}</p>' for p in paras) or '<p></p>'


_FINDING_TAGS = [('实测','tag-exp'), ('文献','tag-lit'), ('推断','tag-inf')]

def _section_findings(s):
    """无序列表，每项前加 ▸；识别 [实测]/[文献]/[推断] 标签并着色。"""
    out = []
    for item in s.get('items', []):
        text = str(item)
        tag_html = ''
        for tag, cls in _FINDING_TAGS:
            marker = f'[{tag}]'
            if marker in text:
                text = text.replace(marker, '', 1).strip()
                tag_html = f' <span class="{cls}">{_esc(marker)}</span>'
                break
        out.append(f'<div class="finding-item">▸ {_esc(text)}{tag_html}</div>')
    return ''.join(out)


def _section_figure(s):
    """图片（PDF→PNG 后 base64 内联）+ 斜体灰图注。"""
    img_path = s.get('image', '')
    if not img_path or not Path(img_path).exists():
        body = '<div class="img-placeholder">Image not found: %s</div>' % _esc(img_path)
    else:
        uri = _image_to_base64(img_path)
        if uri is None:
            body = '<div class="img-placeholder">PDF image needs pymupdf (pip install pymupdf) — skipped: %s</div>' % _esc(img_path)
        else:
            body = f'<img src="{uri}" alt="{_esc(s.get("title",""))}">'
    caption = f'<p class="caption">{_esc(s.get("caption",""))}</p>' if s.get('caption') else ''
    return f'<div>{body}{caption}</div>'


def _section_table(s):
    """HTML table（headers + rows），zebra striping 由 CSS nth-child(even) 处理。"""
    headers = s.get('headers', [])
    rows = s.get('rows', [])
    if not headers:
        return '<p></p>'
    thead = ''.join(f'<th>{_esc(h)}</th>' for h in headers)
    tbody = ''.join(
        '<tr>' + ''.join(f'<td>{_esc(c)}</td>' for c in row) + '</tr>'
        for row in rows
    )
    return f'<table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>'


_STATUS_CLASS = {
    'supported': 'status-supported',
    'refuted': 'status-refuted',
    'inconclusive': 'status-inconclusive',
    'pending': 'status-pending',
}

def _section_ledger(s):
    """假设台账：Hypothesis | Status | Confidence | Basis，status 着色。"""
    ledger = s.get('ledger', [])
    if not ledger:
        return '<p></p>'
    head = '<tr><th>Hypothesis</th><th>Status</th><th>Confidence</th><th>Basis</th></tr>'
    body = []
    for entry in ledger:
        status = str(entry.get('status','')).lower()
        cls = _STATUS_CLASS.get(status, 'status-pending')
        body.append(
            '<tr>'
            f'<td>{_esc(entry.get("hypothesis",""))}</td>'
            f'<td class="{cls}">{_esc(entry.get("status",""))}</td>'
            f'<td>{_esc(entry.get("confidence",""))}</td>'
            f'<td>{_esc(entry.get("basis",""))}</td>'
            '</tr>'
        )
    return f'<table><thead>{head}</thead><tbody>{"".join(body)}</tbody></table>'


def _section_methods(s):
    """方法学段落：等宽字体灰底框。"""
    content = str(s.get('content',''))
    text = _esc(content).replace('\n', '<br>')
    return f'<div class="methods-box">{text}</div>'


_RENDERERS = {
    'summary': _section_summary,
    'findings': _section_findings,
    'figure': _section_figure,
    'table': _section_table,
    'ledger': _section_ledger,
    'methods': _section_methods,
}


def build(report_path, output_path):
    report = json.loads(Path(report_path).read_text(encoding='utf-8'))
    title = report.get('title', 'Analysis Report')
    subtitle = report.get('subtitle', '')

    sections_html = []
    for sec in report.get('sections', []):
        stype = sec.get('type', 'summary')
        render = _RENDERERS.get(stype, _section_summary)  # 未知 type 回退 summary
        sec_html = render(sec)
        sec_title = sec.get('title', '')
        head = f'<h2>{_esc(sec_title)}</h2>' if sec_title else ''
        sections_html.append(f'<section>{head}{sec_html}</section>')

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    page = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_esc(title)}</title>
<style>
{CSS}</style>
</head>
<body>
<h1>{_esc(title)}</h1>
<p class="subtitle">{_esc(subtitle)}</p>
{"".join(sections_html)}
<div class="footer">Generated by cns-bio-pilot web-report · {timestamp}</div>
</body>
</html>
"""
    Path(output_path).write_text(page, encoding='utf-8')
    size_kb = Path(output_path).stat().st_size / 1024
    print(f'SAVED {output_path} ({size_kb:.1f} KB, {len(report.get("sections",[]))} sections)')


def main():
    ap = argparse.ArgumentParser(description='report.json → 自包含 report.html（纯 Python 标准库）')
    ap.add_argument('report', help='report.json path')
    ap.add_argument('-o', '--output', default='report.html', help='output .html (default: report.html)')
    a = ap.parse_args()
    build(a.report, a.output)


if __name__ == '__main__':
    main()