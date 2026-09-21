#!/usr/bin/env python3
"""cns-bio-pilot 路由/触发回归评测器。

三种用法：
  1) OpenAI 兼容后端直接跑（需要环境变量）：
       EVAL_BASE_URL=https://api.moonshot.cn/v1 EVAL_API_KEY=sk-... EVAL_MODEL=kimi-k2 \\
       python run_eval.py --suite route
  2) 只打印每条用例的完整 prompt（供 agent 驱动模式手工/批量执行）：
       python run_eval.py --suite route --backend print
  3) 对已收集的回答打分（agent 驱动模式回收结果）：
       python run_eval.py --suite route --from-json answers.json
       answers.json 格式: {"R01": "模型原始输出", ...}

退出码：全部通过 0，有失败 1（可挂 CI / pre-commit）。
结果落盘 results/<时间戳>_<suite>.json 与最新一份的 Markdown 摘要。
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
SUITES = {"route": "route_cases.yaml", "trigger": "trigger_cases.yaml"}


def load_suite(suite: str):
    cases = yaml.safe_load((HERE / SUITES[suite]).read_text(encoding="utf-8"))["cases"]
    prompt = (HERE / "prompts" / f"{suite}_prompt.md").read_text(encoding="utf-8")
    return prompt, cases


def build_prompt(template: str, utterance: str) -> str:
    return template.replace("{utterance}", utterance)


def score(case: dict, output: str, suite: str) -> bool:
    out = (output or "").strip()
    expected = case["expected"]
    if expected == "NONE":
        # route 套件没有干扰技能，NONE 必须字面输出；
        # trigger 套件有干扰技能在场，只要没选 cns-bio-pilot（选了别的正确技能也算对）即通过
        if suite == "trigger":
            return "cns-bio-pilot" not in out.lower()
        return "NONE" in out.upper()
    if expected.lower() not in out.lower():
        return False
    sib = case.get("not_contains")
    if sib and sib.lower() in out.lower():
        return False
    return True


def run_openai(template: str, cases: list) -> dict:
    import os
    from concurrent.futures import ThreadPoolExecutor

    from openai import OpenAI

    client = OpenAI(base_url=os.environ["EVAL_BASE_URL"], api_key=os.environ["EVAL_API_KEY"])
    model = os.environ["EVAL_MODEL"]

    def call(case):
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": build_prompt(template, case["utterance"])}],
            temperature=0,
            max_tokens=60,
        )
        return case["id"], resp.choices[0].message.content.strip()

    with ThreadPoolExecutor(max_workers=4) as ex:
        return dict(ex.map(call, cases))


def summarize(suite: str, cases: list, answers: dict) -> dict:
    rows, fails = [], []
    for c in cases:
        out = answers.get(c["id"], "<missing>")
        ok = score(c, out, suite)
        rows.append({**c, "output": out, "pass": ok})
        if not ok:
            fails.append(c["id"])
    passed = len(cases) - len(fails)
    result = {
        "suite": suite,
        "time": datetime.now().isoformat(timespec="seconds"),
        "total": len(cases),
        "passed": passed,
        "pass_rate": round(passed / len(cases), 4),
        "failed_ids": fails,
        "rows": rows,
    }
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_json = HERE / "results" / f"{ts}_{suite}.json"
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result, out_json


def print_report(result: dict, out_json: Path) -> None:
    print(f"\n== {result['suite']} 套件 ==")
    print(f"通过 {result['passed']}/{result['total']}  (pass rate {result['pass_rate']:.0%})")
    for r in result["rows"]:
        mark = "✅" if r["pass"] else "❌"
        line = f"{mark} {r['id']} [{r['category']}] 期望={r['expected']}  实际={r['output'][:60]!r}"
        print(line if r["pass"] else f"{line}   ← {r['utterance'][:30]}")
    print(f"明细已写入 {out_json}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", choices=SUITES, required=True)
    ap.add_argument("--backend", choices=["openai", "print"], default="openai")
    ap.add_argument("--from-json", help="跳过调用，直接对 answers.json 打分")
    args = ap.parse_args()

    template, cases = load_suite(args.suite)

    if args.from_json:
        answers = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
    elif args.backend == "print":
        for c in cases:
            print(f"===== {c['id']} =====")
            print(build_prompt(template, c["utterance"]))
        return 0
    else:
        t0 = time.time()
        answers = run_openai(template, cases)
        print(f"(调用完成，用时 {time.time() - t0:.1f}s)")

    result, out_json = summarize(args.suite, cases, answers)
    print_report(result, out_json)
    return 0 if not result["failed_ids"] else 1


if __name__ == "__main__":
    sys.exit(main())
