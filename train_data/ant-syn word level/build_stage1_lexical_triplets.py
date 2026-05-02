import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, List, Tuple


def normalize_word(x: str, lowercase: bool = True) -> str:
    """
    Basic normalization for lexical pairs.
    """
    x = x.strip().replace("_", " ")
    x = " ".join(x.split())
    if lowercase:
        x = x.lower()
    return x


def read_pair_jsonl(
    path: str,
    bidirectional: bool = True,
    lowercase: bool = True,
    keep_multiword: bool = True,
) -> Dict[str, Set[str]]:
    """
    Read jsonl file with {"w1": ..., "w2": ...} format.

    If bidirectional=True:
        w1 -> w2 and w2 -> w1 are both added.
    """
    pair_map = defaultdict(set)

    with open(path, "r", encoding="utf-8") as f:
        for line_idx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                print(f"[WARN] Skip invalid JSON at line {line_idx + 1} in {path}")
                continue

            if "w1" not in obj or "w2" not in obj:
                print(f"[WARN] Skip line without w1/w2 at line {line_idx + 1} in {path}")
                continue

            w1 = normalize_word(obj["w1"], lowercase=lowercase)
            w2 = normalize_word(obj["w2"], lowercase=lowercase)

            if not w1 or not w2 or w1 == w2:
                continue

            if not keep_multiword:
                if " " in w1 or " " in w2:
                    continue

            pair_map[w1].add(w2)

            if bidirectional:
                pair_map[w2].add(w1)

    return pair_map


def sample_list(items: List[str], max_items: int, rng: random.Random) -> List[str]:
    """
    Deterministically sample up to max_items.
    If max_items <= 0, keep all.
    """
    items = sorted(items)

    if max_items is None or max_items <= 0 or len(items) <= max_items:
        return items

    return sorted(rng.sample(items, max_items))


def build_triplets_for_anchor(
    anchor: str,
    synonyms: Set[str],
    antonyms: Set[str],
    rng: random.Random,
    max_pos_per_anchor: int = 10,
    max_neg_per_anchor: int = 10,
    max_triplets_per_anchor: int = 20,
    with_metadata: bool = False,
) -> List[dict]:
    """
    Build triplets:
        query = anchor
        positive = synonym(anchor)
        hard_negative = antonym(anchor)
    """
    positives = set(synonyms) - {anchor}
    negatives = set(antonyms) - {anchor}

    # Avoid contradictory labels if a word appears in both synonym and antonym sets.
    positives = positives - negatives
    negatives = negatives - positives

    positives = sample_list(list(positives), max_pos_per_anchor, rng)
    negatives = sample_list(list(negatives), max_neg_per_anchor, rng)

    triplets: List[dict] = []

    for pos in positives:
        for neg in negatives:
            if pos == neg:
                continue

            if with_metadata:
                ex = {
                    "query": anchor,
                    "positive": pos,
                    "hard_negative": neg,
                    "source": "lexical_stage1",
                    "anchor": anchor,
                    "positive_relation": "synonym",
                    "hard_negative_relation": "antonym",
                }
            else:
                # This is the exact minimal format used by your current encoder training.
                ex = {
                    "query": anchor,
                    "positive": pos,
                    "hard_negative": neg,
                }

            triplets.append(ex)

    if max_triplets_per_anchor is not None and max_triplets_per_anchor > 0:
        if len(triplets) > max_triplets_per_anchor:
            triplets = rng.sample(triplets, max_triplets_per_anchor)

    return triplets


def split_anchors(
    anchors: List[str],
    val_ratio: float,
    seed: int,
) -> Tuple[Set[str], Set[str]]:
    """
    Split by anchor word, not by triplet.

    This prevents leakage where the same anchor word appears in both train and val.
    """
    rng = random.Random(seed)
    anchors = sorted(anchors)
    rng.shuffle(anchors)

    n_val = int(len(anchors) * val_ratio)
    val_anchors = set(anchors[:n_val])
    train_anchors = set(anchors[n_val:])

    return train_anchors, val_anchors


def write_jsonl(path: str, rows: List[dict]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--syn_file", type=str, required=True)
    parser.add_argument("--ant_file", type=str, required=True)
    parser.add_argument("--out_dir", type=str, default="data/processed")

    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--val_ratio", type=float, default=0.1)

    parser.add_argument("--max_pos_per_anchor", type=int, default=10)
    parser.add_argument("--max_neg_per_anchor", type=int, default=10)
    parser.add_argument("--max_triplets_per_anchor", type=int, default=20)

    parser.add_argument("--no_bidirectional", action="store_true")
    parser.add_argument("--no_lowercase", action="store_true")
    parser.add_argument("--single_word_only", action="store_true")

    parser.add_argument(
        "--with_metadata",
        action="store_true",
        help="If set, output extra metadata fields. Default output has only query/positive/hard_negative.",
    )

    args = parser.parse_args()

    rng = random.Random(args.seed)

    bidirectional = not args.no_bidirectional
    lowercase = not args.no_lowercase
    keep_multiword = not args.single_word_only

    syn_map = read_pair_jsonl(
        args.syn_file,
        bidirectional=bidirectional,
        lowercase=lowercase,
        keep_multiword=keep_multiword,
    )

    ant_map = read_pair_jsonl(
        args.ant_file,
        bidirectional=bidirectional,
        lowercase=lowercase,
        keep_multiword=keep_multiword,
    )

    anchors = sorted(set(syn_map.keys()) & set(ant_map.keys()))

    train_anchors, val_anchors = split_anchors(
        anchors=anchors,
        val_ratio=args.val_ratio,
        seed=args.seed,
    )

    train_rows: List[dict] = []
    val_rows: List[dict] = []

    for anchor in anchors:
        rows = build_triplets_for_anchor(
            anchor=anchor,
            synonyms=syn_map[anchor],
            antonyms=ant_map[anchor],
            rng=rng,
            max_pos_per_anchor=args.max_pos_per_anchor,
            max_neg_per_anchor=args.max_neg_per_anchor,
            max_triplets_per_anchor=args.max_triplets_per_anchor,
            with_metadata=args.with_metadata,
        )

        if anchor in train_anchors:
            train_rows.extend(rows)
        elif anchor in val_anchors:
            val_rows.extend(rows)

    rng.shuffle(train_rows)
    rng.shuffle(val_rows)

    out_dir = Path(args.out_dir)
    train_path = out_dir / "stage1_lexical_train_triplets.jsonl"
    val_path = out_dir / "stage1_lexical_val_triplets.jsonl"

    write_jsonl(str(train_path), train_rows)
    write_jsonl(str(val_path), val_rows)

    print("Done.")
    print(f"syn anchors: {len(syn_map)}")
    print(f"ant anchors: {len(ant_map)}")
    print(f"usable anchors with both synonym and antonym: {len(anchors)}")
    print(f"train anchors: {len(train_anchors)}")
    print(f"val anchors: {len(val_anchors)}")
    print(f"train triplets: {len(train_rows)}")
    print(f"val triplets: {len(val_rows)}")
    print(f"train output: {train_path}")
    print(f"val output: {val_path}")


if __name__ == "__main__":
    main()