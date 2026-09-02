#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nb_log — CLI 执行体的 ipynb 代码台账工具（Core Rule 9 / dispatch_cheatsheet A10）.

无 Jupyter 内核时，分析/绘图代码以临时脚本执行；每步成功后用本工具把
「实际执行的代码 + stdout 捕获 + 关键图」追加为任务 notebook 的 cell，
保证 .ipynb 始终是完整可复现代码台账——CLI 只是执行方式，不免除落账义务。

用法（notebook 不存在时自动创建）：
  # 代码 + stdout + 图，一步落账（最常用）
  python nb_log.py notebooks/01_qc.ipynb -t "§2 QC" -c step.py -o step.log -f panels/A_umap.png
  # 代码从 stdin
  cat step.py | python nb_log.py notebooks/01_qc.ipynb -t "§2 QC" -c -
  # 只追加一条 markdown 备注
  python nb_log.py notebooks/01_qc.ipynb --md -t "结论：过滤后剩 8,214 cells"
  # R 代码（scop 路由）——新建 R 内核 notebook
  python nb_log.py notebooks/02_deconv.ipynb --kernel r -t "RunRCTD" -c step.R -o step.log

零第三方依赖（纯标准库 JSON），写出 nbformat 4.5。
"""

import argparse
import base64
import json
import sys
import uuid
from pathlib import Path

MAX_TEXT_OUTPUT = 200_000  # 超长 stdout 截断保尾部

KERNELS = {
    "python3": {"display_name": "Python 3", "language": "python", "name": "python3", "lang_info": "python"},
    "r": {"display_name": "R", "language": "R", "name": "ir", "lang_info": "R"},
}


def new_notebook(kernel: str):
    ks = KERNELS[kernel]
    language_info = {"name": ks["lang_info"]}
    if kernel == "python3":
        language_info["version"] = sys.version.split()[0]
    return {
        "cells": [],
        "metadata": {
            "kernelspec": {"display_name": ks["display_name"], "language": ks["language"], "name": ks["name"]},
            "language_info": language_info,
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def load_notebook(path: Path, kernel: str):
    if not path.exists():
        print(f"[nb_log] notebook 不存在，已新建（kernel={kernel}）: {path}")
        return new_notebook(kernel)
    try:
        nb = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        sys.exit(f"[nb_log] ERROR 无法读取 {path}: {e}")
    if not isinstance(nb, dict) or not isinstance(nb.get("cells"), list):
        sys.exit(f"[nb_log] ERROR {path} 不是合法 .ipynb（缺 cells 列表）")
    return nb


def read_file(path_str: str, what: str) -> str:
    if path_str == "-":
        return sys.stdin.read()
    try:
        return Path(path_str).read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        sys.exit(f"[nb_log] ERROR 无法读取{what} {path_str}: {e}")


def as_lines(text: str):
    lines = text.splitlines(keepends=True)
    return lines if lines else [""]


def mk_cell(cell_type: str, source: str, outputs=None):
    cell = {
        "cell": cell_type,
        "id": uuid.uuid4().hex[:8],
        "metadata": {},
        "source": as_lines(source),
    }
    if cell_type == "code":
        cell["outputs"] = outputs or []
        cell["execution_count"] = None
    return cell


def text_output(text: str):
    if len(text) > MAX_TEXT_OUTPUT:
        text = f"... [stdout 超长，截断只保尾部 {MAX_TEXT_OUTPUT} 字符] ...\n" + text[-MAX_TEXT_OUTPUT:]
    return {"output_type": "stream", "name": "stdout", "text": as_lines(text)}


def image_output(png_path: str):
    try:
        data = Path(png_path).read_bytes()
    except OSError as e:
        sys.exit(f"[nb_log] ERROR 无法读取图 {png_path}: {e}")
    return {
        "output_type": "display_data",
        "data": {"image/png": base64.b64encode(data).decode("ascii")},
        "metadata": {},
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="把 CLI 执行的代码/输出/图追加进任务 ipynb（Core Rule 9 代码台账）")
    ap.add_argument("notebook", help="任务 notebook 路径（不存在则自动创建）")
    ap.add_argument("-t", "--title", help="先追加一个 markdown 标题 cell（原样写入，可含 markdown 格式）")
    ap.add_argument("-c", "--code", help="实际执行的脚本路径（'-' = stdin）")
    ap.add_argument("-o", "--output", help="stdout 捕获文件（如 step.log），附加为该 cell 的文本输出")
    ap.add_argument("-f", "--figure", action="append", default=[], metavar="PNG",
                    help="要嵌入 cell 输出的 PNG 路径，可重复（如 -f panels/A_umap.png）")
    ap.add_argument("--md", action="store_true",
                    help="把 --code 内容作为 markdown cell 追加（默认为 code cell；此时 -o/-f 被忽略）")
    ap.add_argument("--kernel", choices=sorted(KERNELS), default="python3",
                    help="新建 notebook 用的内核（仅 notebook 不存在时生效；R 代码用 r，已存在的 notebook 不受影响）")
    args = ap.parse_args(argv)

    if not (args.title or args.code):
        ap.error("至少提供 -t/--title 或 -c/--code 之一，否则没有内容可追加")

    nb_path = Path(args.notebook)
    nb = load_notebook(nb_path, args.kernel)

    if args.md and (args.output or args.figure):
        print("[nb_log] 提示: --md 模式下 -o/-f 被忽略")

    if args.title:
        nb["cells"].append(mk_cell("markdown", args.title.rstrip("\n") + "\n"))

    if args.code:
        source = read_file(args.code, "代码文件")
        if args.md:
            nb["cells"].append(mk_cell("markdown", source))
        else:
            outputs = []
            if args.output:
                outputs.append(text_output(read_file(args.output, "输出文件")))
            for fig in args.figure:
                outputs.append(image_output(fig))
            nb["cells"].append(mk_cell("code", source, outputs))

    nb_path.parent.mkdir(parents=True, exist_ok=True)
    nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[nb_log] OK {nb_path} 现有 {len(nb['cells'])} cells")


if __name__ == "__main__":
    main()
