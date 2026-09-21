#!/usr/bin/env python3
"""子 skill description 语义重叠检测（本地化 NVIDIA SkillEvaluator Tier2 思路）。

对全部子 skill 的 description 做 char n-gram TF-IDF 余弦相似度矩阵，
标出高重叠对——这些对最容易在路由时互相抢触发，需要拉开描述边界。

用法:  python desc_overlap.py [--threshold 0.45]
零网络依赖；中英混合文本用 char 2~4-gram 比分词器更稳。
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_descriptions() -> dict:
    descs = {}
    for f in sorted(ROOT.glob("skills/*/*/SKILL.md")):
        text = f.read_text(encoding="utf-8")
        m = re.search(r"^---\n(.*?)\n---\n", text, re.S | re.M)
        if not m:
            continue
        d = re.search(r"^description:\s*(.+)$", m.group(1), re.M)
        if d:
            key = str(f.relative_to(ROOT)).replace("/SKILL.md", "").replace("skills/", "")
            descs[key] = d.group(1).strip()
    # 路由器的 description 也纳入（它与子 skill 描述也不应过度重叠）
    rt = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^description:\s*(.+)$", rt, re.M)
    if m:
        descs["<router>"] = m.group(1).strip()
    return descs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=0.45)
    args = ap.parse_args()

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    descs = load_descriptions()
    keys = list(descs)
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), min_df=1)
    X = vec.fit_transform([descs[k] for k in keys])
    sim = cosine_similarity(X)

    pairs = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            pairs.append((sim[i, j], keys[i], keys[j]))
    pairs.sort(reverse=True)

    print(f"共 {len(keys)} 个 description，阈值 {args.threshold}\n")
    print("== 全部配对 Top 15 ==")
    for s, a, b in pairs[:15]:
        flag = " ⚠️" if s >= args.threshold else ""
        print(f"{s:.3f}  {a}  ×  {b}{flag}")

    flagged = [p for p in pairs if p[0] >= args.threshold]
    print(f"\n== 超过阈值的高重叠对: {len(flagged)} ==")
    for s, a, b in flagged:
        print(f"⚠️  {s:.3f}  {a} × {b}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
