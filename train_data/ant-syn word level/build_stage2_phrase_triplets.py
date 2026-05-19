import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, List, Tuple


def normalize_word(x: str, lowercase: bool = True) -> str:
    x = str(x).strip().replace("_", " ")
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
    Read JSONL pairs in this format:
        {"w1": "clean", "w2": "dirty"}

    Return:
        pair_map[w1] = {w2, ...}
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
                print(f"[WARN] Invalid JSON at {path}:{line_idx + 1}")
                continue

            if "w1" not in obj or "w2" not in obj:
                print(f"[WARN] Missing w1/w2 at {path}:{line_idx + 1}")
                continue

            w1 = normalize_word(obj["w1"], lowercase=lowercase)
            w2 = normalize_word(obj["w2"], lowercase=lowercase)

            if not w1 or not w2 or w1 == w2:
                continue

            if not keep_multiword and (" " in w1 or " " in w2):
                continue

            pair_map[w1].add(w2)

            if bidirectional:
                pair_map[w2].add(w1)

    return pair_map


def sample_items(items: Set[str], max_items: int, rng: random.Random) -> List[str]:
    items = sorted(items)

    if max_items is None or max_items <= 0:
        return items

    if len(items) <= max_items:
        return items

    return sorted(rng.sample(items, max_items))


def split_anchors(
    anchors: List[str],
    val_ratio: float,
    seed: int,
) -> Tuple[Set[str], Set[str]]:
    """
    Split by anchor word to avoid leakage.

    Example:
        If "dirty" is in train, then all triplets with query "not dirty"
        stay in train.
    """
    rng = random.Random(seed)
    anchors = sorted(anchors)
    rng.shuffle(anchors)

    n_val = int(len(anchors) * val_ratio)
    val_anchors = set(anchors[:n_val])
    train_anchors = set(anchors[n_val:])

    return train_anchors, val_anchors


def build_stage2_triplets_for_anchor(
    anchor: str,
    syn_map: Dict[str, Set[str]],
    ant_map: Dict[str, Set[str]],
    query_templates: List[str],
    rng: random.Random,
    max_antonyms_per_anchor: int = 5,
    max_pos_per_antonym: int = 5,
    max_neg_per_anchor: int = 5,
    max_triplets_per_anchor: int = 30,
    with_metadata: bool = False,
) -> List[dict]:
    """
    For anchor X, build phrase-level triplets:

        query = "not X"
        positive = antonym(X) or synonym(antonym(X))
        hard_negative = X or synonym(X)

    Example:
        anchor = dirty
        antonym = clean
        query = not dirty
        positive = clean / hygienic
        hard_negative = dirty / filthy
    """
    rows = []

    antonyms = set(ant_map.get(anchor, set()))
    if not antonyms:
        return rows

    antonyms = sample_items(antonyms, max_antonyms_per_anchor, rng)

    # Hard negatives are the forbidden concept itself and its synonyms.
    negative_candidates = set([anchor]) | set(syn_map.get(anchor, set()))

    for ant in antonyms:
        # Positives are the opposite concept and its synonyms.
        positive_candidates = set([ant]) | set(syn_map.get(ant, set()))

        # Remove ambiguous overlaps.
        overlap = positive_candidates & negative_candidates
        positive_candidates -= overlap
        negative_clean = negative_candidates - overlap

        if not positive_candidates or not negative_clean:
            continue

        positives = sample_items(positive_candidates, max_pos_per_antonym, rng)
        negatives = sample_items(negative_clean, max_neg_per_anchor, rng)

        for template in query_templates:
            query = template.format(x=anchor)

            for pos in positives:
                for neg in negatives:
                    if pos == neg:
                        continue

                    if with_metadata:
                        row = {
                            "query": query,
                            "positive": pos,
                            "hard_negative": neg,
                            "source": "lexical_stage2_phrase",
                            "anchor": anchor,
                            "antonym_seed": ant,
                            "query_template": template,
                            "positive_rule": "antonym_or_synonym_of_antonym",
                            "hard_negative_rule": "anchor_or_synonym_of_anchor",
                        }
                    else:
                        row = {
                            "query": query,
                            "positive": pos,
                            "hard_negative": neg,
                        }

                    rows.append(row)

    # Deduplicate.
    dedup = {}
    for row in rows:
        key = (row["query"], row["positive"], row["hard_negative"])
        dedup[key] = row
    rows = list(dedup.values())

    if max_triplets_per_anchor is not None and max_triplets_per_anchor > 0:
        if len(rows) > max_triplets_per_anchor:
            rows = rng.sample(rows, max_triplets_per_anchor)

    return rows


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

    parser.add_argument("--max_antonyms_per_anchor", type=int, default=5)
    parser.add_argument("--max_pos_per_antonym", type=int, default=5)
    parser.add_argument("--max_neg_per_anchor", type=int, default=5)
    parser.add_argument("--max_triplets_per_anchor", type=int, default=30)

    parser.add_argument("--no_bidirectional", action="store_true")
    parser.add_argument("--no_lowercase", action="store_true")
    parser.add_argument("--single_word_only", action="store_true")

    parser.add_argument(
        "--templates",
        nargs="+",
        default=["not {x}"],
        help=(
            "Query templates. Use {x} as the anchor word. "
            "Example: --templates 'not {x}' 'without {x}' 'excluding {x}'"
        ),
    )

    parser.add_argument(
        "--with_metadata",
        action="store_true",
        help="Output extra metadata fields. Default output only has query/positive/hard_negative.",
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

    anchors = sorted(set(ant_map.keys()))

    train_anchors, val_anchors = split_anchors(
        anchors=anchors,
        val_ratio=args.val_ratio,
        seed=args.seed,
    )

    train_rows = []
    val_rows = []

    for anchor in anchors:
        rows = build_stage2_triplets_for_anchor(
            anchor=anchor,
            syn_map=syn_map,
            ant_map=ant_map,
            query_templates=args.templates,
            rng=rng,
            max_antonyms_per_anchor=args.max_antonyms_per_anchor,
            max_pos_per_antonym=args.max_pos_per_antonym,
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
    train_path = out_dir / "stage2_phrase_train_triplets.jsonl"
    val_path = out_dir / "stage2_phrase_val_triplets.jsonl"

    write_jsonl(str(train_path), train_rows)
    write_jsonl(str(val_path), val_rows)

    print("Done.")
    print(f"syn anchors: {len(syn_map)}")
    print(f"ant anchors: {len(ant_map)}")
    print(f"usable anchors: {len(anchors)}")
    print(f"train anchors: {len(train_anchors)}")
    print(f"val anchors: {len(val_anchors)}")
    print(f"train triplets: {len(train_rows)}")
    print(f"val triplets: {len(val_rows)}")
    print(f"train output: {train_path}")
    print(f"val output: {val_path}")


if __name__ == "__main__":
    main()