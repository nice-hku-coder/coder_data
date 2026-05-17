#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Convert ExcluIR to BEIR format.

Output:
  beir/excluir/
    train_set/
      corpus.jsonl
      queries.jsonl
      qrels/
        train.tsv
      excluir_meta.jsonl
    test_set/
      corpus.jsonl
      queries.jsonl
      qrels/
        test.tsv
      excluir_meta.jsonl

Run:
  python convert_excluir_to_beir.py

Optional:
  python convert_excluir_to_beir.py --raw_dir data/excluir_raw --out_dir beir/excluir
  python convert_excluir_to_beir.py --no_download --raw_dir path/to/downloaded/ExcluIR_data
"""

import argparse
import json
import random
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


GDRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1O7IHuEHgjAHL6FCb8z5-zTI3YCqcA5J1?usp=sharing"


def ensure_gdown():
    try:
        import gdown  # noqa: F401
        return
    except ImportError:
        print("[INFO] gdown not found. Installing gdown ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "gdown"])


def download_excluir(raw_dir: Path, force: bool = False):
    """
    Download the official ExcluIR dataset folder from Google Drive.
    """
    raw_dir.mkdir(parents=True, exist_ok=True)

    existing_corpus = list(raw_dir.rglob("corpus.json"))
    existing_test = list(raw_dir.rglob("test_manual_final.json"))

    if existing_corpus and existing_test and not force:
        print(f"[INFO] Found existing dataset under {raw_dir}. Skip download.")
        return

    ensure_gdown()
    import gdown

    print(f"[INFO] Downloading ExcluIR dataset to {raw_dir} ...")
    print(f"[INFO] Source: {GDRIVE_FOLDER_URL}")

    try:
        gdown.download_folder(
            url=GDRIVE_FOLDER_URL,
            output=str(raw_dir),
            quiet=False,
            use_cookies=False,
            remaining_ok=True,
        )
    except TypeError:
        # For older gdown versions that do not support remaining_ok.
        gdown.download_folder(
            url=GDRIVE_FOLDER_URL,
            output=str(raw_dir),
            quiet=False,
            use_cookies=False,
        )

    print("[INFO] Download finished.")


def find_file(root: Path, filename: str) -> Path:
    matches = list(root.rglob(filename))
    if not matches:
        raise FileNotFoundError(
            f"Could not find {filename} under {root}. "
            f"Please check whether the Google Drive download succeeded."
        )

    # Prefer the shortest path in case there are duplicates.
    matches = sorted(matches, key=lambda p: (len(str(p)), str(p)))
    return matches[0]


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_jsonl(path: Path, rows: List[Dict[str, Any]]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def normalize_doc(doc: Any, idx: int) -> Tuple[str, str]:
    """
    ExcluIR official corpus is usually List[str].
    This function also handles dict-like docs for robustness.
    """
    if isinstance(doc, str):
        return "", doc

    if isinstance(doc, dict):
        title = str(doc.get("title", ""))
        text = (
            doc.get("text")
            or doc.get("contents")
            or doc.get("content")
            or doc.get("body")
            or doc.get("document")
        )
        if text is None:
            text = json.dumps(doc, ensure_ascii=False)
        return title, str(text)

    return "", str(doc)


def get_first_existing(sample: Dict[str, Any], keys: List[str], sample_id: int) -> Any:
    for key in keys:
        if key in sample:
            return sample[key]
    raise KeyError(
        f"Sample {sample_id} does not contain any of keys: {keys}. "
        f"Actual keys: {list(sample.keys())}"
    )


def extract_query_and_indices(sample: Dict[str, Any], sample_id: int) -> Tuple[str, List[int], Dict[str, Any]]:
    """
    Official data README says:
      query key: RQ_rewrite
      index key: corpus_sub_index

    Official bi_eval.py uses:
      query key: ExcluQ
      index key: index

    We support both.
    """
    query = get_first_existing(
        sample,
        keys=["RQ_rewrite", "ExcluQ", "exclusive_query", "query", "question"],
        sample_id=sample_id,
    )

    indices = get_first_existing(
        sample,
        keys=["corpus_sub_index", "index", "indices", "doc_indices"],
        sample_id=sample_id,
    )

    if not isinstance(indices, list) or len(indices) < 2:
        raise ValueError(
            f"Sample {sample_id} has invalid indices: {indices}. "
            f"Expected a list like [negative_doc_index, positive_doc_index]."
        )

    try:
        indices = [int(x) for x in indices]
    except Exception as e:
        raise ValueError(f"Sample {sample_id} has non-integer indices: {indices}") from e

    extra = {}
    for key in ["question0", "RQ_rewrite", "ExcluQ"]:
        if key in sample:
            extra[key] = sample[key]

    return str(query), indices, extra


def make_train_test_split(num_samples: int, train_ratio: float, seed: int) -> Dict[int, str]:
    if not 0.0 < train_ratio < 1.0:
        raise ValueError(f"train_ratio must be between 0 and 1, got {train_ratio}")

    indices = list(range(num_samples))
    rng = random.Random(seed)
    rng.shuffle(indices)

    train_size = int(num_samples * train_ratio)
    train_indices = set(indices[:train_size])
    return {
        idx: "train" if idx in train_indices else "test"
        for idx in range(num_samples)
    }


def convert_to_beir(raw_dir: Path, out_dir: Path, train_ratio: float = 0.2, seed: int = 42):
    corpus_path = find_file(raw_dir, "corpus.json")
    test_path = find_file(raw_dir, "test_manual_final.json")

    print(f"[INFO] corpus path: {corpus_path}")
    print(f"[INFO] test path:   {test_path}")

    corpus_raw = read_json(corpus_path)
    samples = read_json(test_path)

    if not isinstance(corpus_raw, list):
        raise ValueError(f"Expected corpus.json to be a list, got {type(corpus_raw)}")

    if not isinstance(samples, list):
        raise ValueError(f"Expected test_manual_final.json to be a list, got {type(samples)}")

    split_dirs = {
        "train": out_dir / "train_set",
        "test": out_dir / "test_set",
    }
    for split_dir in split_dirs.values():
        split_dir.mkdir(parents=True, exist_ok=True)
        (split_dir / "qrels").mkdir(parents=True, exist_ok=True)

    # 1. corpus.jsonl
    corpus_rows = []
    for i, doc in enumerate(corpus_raw):
        title, text = normalize_doc(doc, i)
        corpus_rows.append(
            {
                "_id": f"excluir_doc_{i}",
                "title": title,
                "text": text,
            }
        )

    for split_dir in split_dirs.values():
        write_jsonl(split_dir / "corpus.jsonl", corpus_rows)

    # 2. queries.jsonl, qrels/{train,test}.tsv, excluir_meta.jsonl
    query_rows = {"train": [], "test": []}
    meta_rows = {"train": [], "test": []}
    sample_splits = make_train_test_split(len(samples), train_ratio=train_ratio, seed=seed)

    qrels_paths = {
        split: split_dir / "qrels" / f"{split}.tsv"
        for split, split_dir in split_dirs.items()
    }
    qrels_files = {
        split: path.open("w", encoding="utf-8")
        for split, path in qrels_paths.items()
    }

    try:
        for qf in qrels_files.values():
            qf.write("query-id\tcorpus-id\tscore\n")

        for qi, sample in enumerate(samples):
            if not isinstance(sample, dict):
                raise ValueError(f"Sample {qi} is not a dict: {sample}")

            query_text, indices, extra = extract_query_and_indices(sample, qi)

            neg_indices = indices[:1]
            pos_indices = indices[1:]

            for idx in indices:
                if idx < 0 or idx >= len(corpus_raw):
                    raise IndexError(
                        f"Sample {qi} references corpus index {idx}, "
                        f"but corpus size is {len(corpus_raw)}"
                    )

            query_id = f"excluir_q_{qi}"
            sample_split = sample_splits[qi]

            positive_doc_ids = [f"excluir_doc_{idx}" for idx in pos_indices]
            violating_doc_ids = [f"excluir_doc_{idx}" for idx in neg_indices]

            query_rows[sample_split].append(
                {
                    "_id": query_id,
                    "text": query_text,
                    "constraint_satisfying_doc_ids": positive_doc_ids,
                    "constraint_violating_doc_ids": violating_doc_ids,
                    "graded_relevance": {
                        **{doc_id: 2.0 for doc_id in positive_doc_ids},
                        **{doc_id: 0.0 for doc_id in violating_doc_ids},
                    },
                    "topical_relevant_doc_ids": positive_doc_ids + violating_doc_ids,
                }
            )

            for doc_id in positive_doc_ids:
                qrels_files[sample_split].write(f"{query_id}\t{doc_id}\t1\n")

            meta_rows[sample_split].append(
                {
                    "query_id": query_id,
                    "query_text": query_text,
                    "split": sample_split,
                    "positive_doc_ids": positive_doc_ids,
                    "violating_doc_ids": violating_doc_ids,
                    "positive_indices": pos_indices,
                    "violating_indices": neg_indices,
                    "original_indices": indices,
                    "source_extra": extra,
                }
            )
    finally:
        for qf in qrels_files.values():
            qf.close()

    for split, split_dir in split_dirs.items():
        write_jsonl(split_dir / "queries.jsonl", query_rows[split])
        write_jsonl(split_dir / "excluir_meta.jsonl", meta_rows[split])

    print("\n[DONE] Saved BEIR-format ExcluIR:")
    for split, split_dir in split_dirs.items():
        print(f"  {split_dir / 'corpus.jsonl'}")
        print(f"  {split_dir / 'queries.jsonl'}")
        print(f"  {qrels_paths[split]}")
        print(f"  {split_dir / 'excluir_meta.jsonl'}")
    print()
    print(f"[STATS] corpus docs: {len(corpus_rows)}")
    print(f"[STATS] train queries: {len(query_rows['train'])}")
    print(f"[STATS] test queries:  {len(query_rows['test'])}")
    print(f"[STATS] train qrels:   {sum(len(r['positive_doc_ids']) for r in meta_rows['train'])}")
    print(f"[STATS] test qrels:    {sum(len(r['positive_doc_ids']) for r in meta_rows['test'])}")
    print(f"[STATS] violating:     {sum(len(r['violating_doc_ids']) for rows in meta_rows.values() for r in rows)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw_dir",
        type=str,
        default="data/excluir_raw",
        help="Directory for raw downloaded ExcluIR files.",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default="beir/excluir",
        help="Output directory for BEIR-format ExcluIR.",
    )
    parser.add_argument(
        "--train_ratio",
        type=float,
        default=0.2,
        help="Fraction of queries assigned to train. Default: 0.2 for a 2:8 train/test split.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible train/test splitting.",
    )
    parser.add_argument(
        "--no_download",
        action="store_true",
        help="Skip download and use files already in --raw_dir.",
    )
    parser.add_argument(
        "--force_download",
        action="store_true",
        help="Force re-download even if files already exist.",
    )

    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    out_dir = Path(args.out_dir)

    if not args.no_download:
        download_excluir(raw_dir, force=args.force_download)

    convert_to_beir(raw_dir, out_dir, train_ratio=args.train_ratio, seed=args.seed)


if __name__ == "__main__":
    main()