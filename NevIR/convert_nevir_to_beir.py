#!/usr/bin/env python3
"""Convert local NevIR JSONL files into BEIR-style files.

The ID scheme intentionally matches src.data_loader._load_nevir:
  doc1 -> nevir_doc_{pair_id}_1
  doc2 -> nevir_doc_{pair_id}_2
  q1   -> nevir_q_{pair_id}_1
  q2   -> nevir_q_{pair_id}_2
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


SPLIT_FILES = {
    "train": "train.jsonl",
    "dev": "validation.jsonl",
    "test": "test.jsonl",
}


def read_jsonl(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {path} at line {line_no}") from exc


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def convert_nevir(source_dir: Path, output_dir: Path) -> None:
    corpus: dict[str, dict[str, object]] = {}
    queries: dict[str, str] = {}
    qrels_by_split: dict[str, list[tuple[str, str, int]]] = {}
    pairs_by_split: dict[str, list[dict[str, str]]] = {}

    for split, filename in SPLIT_FILES.items():
        split_path = source_dir / filename
        if not split_path.exists():
            raise FileNotFoundError(f"Missing NevIR split file: {split_path}")

        qrels: list[tuple[str, str, int]] = []
        pairs: list[dict[str, str]] = []

        for row in read_jsonl(split_path):
            pair_id = str(row["id"])
            doc1_id = f"nevir_doc_{pair_id}_1"
            doc2_id = f"nevir_doc_{pair_id}_2"
            q1_id = f"nevir_q_{pair_id}_1"
            q2_id = f"nevir_q_{pair_id}_2"

            corpus[doc1_id] = {"_id": doc1_id, "title": "", "text": row["doc1"], "metadata": {}}
            corpus[doc2_id] = {"_id": doc2_id, "title": "", "text": row["doc2"], "metadata": {}}
            queries[q1_id] = row["q1"]
            queries[q2_id] = row["q2"]

            qrels.append((q1_id, doc1_id, 1))
            qrels.append((q2_id, doc2_id, 1))
            pairs.append(
                {
                    "pair_id": pair_id,
                    "q1_id": q1_id,
                    "q2_id": q2_id,
                    "doc1_id": doc1_id,
                    "doc2_id": doc2_id,
                }
            )

        qrels_by_split[split] = qrels
        pairs_by_split[split] = pairs

    output_dir.mkdir(parents=True, exist_ok=True)
    qrels_dir = output_dir / "qrels"
    pairs_dir = output_dir / "pairs"
    qrels_dir.mkdir(exist_ok=True)
    pairs_dir.mkdir(exist_ok=True)

    write_jsonl(output_dir / "corpus.jsonl", corpus.values())
    write_jsonl(
        output_dir / "queries.jsonl",
        ({"_id": query_id, "text": text, "metadata": {}} for query_id, text in queries.items()),
    )

    for split, qrels in qrels_by_split.items():
        with (qrels_dir / f"{split}.tsv").open("w", encoding="utf-8") as f:
            f.write("query-id\tcorpus-id\tscore\n")
            for query_id, doc_id, score in qrels:
                f.write(f"{query_id}\t{doc_id}\t{score}\n")

        with (pairs_dir / f"{split}.json").open("w", encoding="utf-8") as f:
            json.dump(pairs_by_split[split], f, ensure_ascii=False, indent=2)

    print(f"Wrote BEIR-style NevIR to {output_dir}")
    print(f"  corpus:  {len(corpus)} docs")
    print(f"  queries: {len(queries)} queries")
    for split in SPLIT_FILES:
        print(f"  {split}: {len(qrels_by_split[split])} qrels, {len(pairs_by_split[split])} pairs")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("/data/xingkun/NevIR"),
        help="Directory containing train.jsonl, validation.jsonl, and test.jsonl.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("beir/nevir"),
        help="Output directory for BEIR-style NevIR files.",
    )
    args = parser.parse_args()

    convert_nevir(args.source_dir, args.output_dir)


if __name__ == "__main__":
    main()
