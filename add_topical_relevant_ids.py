#!/usr/bin/env python3
"""
为 nevir_beir 和 excluir_beir 的 queries.jsonl 添加 topical_relevant_doc_ids 字段。

topical_relevant_doc_ids = constraint_satisfying_doc_ids ∪ constraint_violating_doc_ids
（即所有与 query 话题相关的文档，不论是否满足约束）

用法：
    python add_topical_relevant_ids.py
"""

import json
import os
import shutil

TARGETS = [
    "nevir_beir/queries.jsonl",
    "excluir_beir/queries.jsonl",
]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def process_file(rel_path: str):
    path = os.path.join(SCRIPT_DIR, rel_path)
    backup = path + ".bak"

    if not os.path.exists(path):
        print(f"[SKIP] Not found: {path}")
        return

    # 备份原文件
    shutil.copy2(path, backup)
    print(f"[Backup] {path} -> {backup}")

    updated = 0
    already = 0
    lines_out = []

    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                lines_out.append("")
                continue
            row = json.loads(line)

            if "topical_relevant_doc_ids" in row:
                already += 1
                lines_out.append(json.dumps(row, ensure_ascii=False))
                continue

            satisfying = row.get("constraint_satisfying_doc_ids") or []
            violating = row.get("constraint_violating_doc_ids") or []

            # 合并去重，保持顺序（satisfying 在前）
            seen = set()
            topical = []
            for doc_id in list(satisfying) + list(violating):
                if doc_id not in seen:
                    seen.add(doc_id)
                    topical.append(doc_id)

            row["topical_relevant_doc_ids"] = topical
            lines_out.append(json.dumps(row, ensure_ascii=False))
            updated += 1

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines_out))
        if lines_out:
            f.write("\n")

    print(f"[Done] {rel_path}: {updated} rows updated, {already} rows already had the field.")


if __name__ == "__main__":
    for target in TARGETS:
        process_file(target)
    print("\nAll done. Original files backed up as *.bak")
