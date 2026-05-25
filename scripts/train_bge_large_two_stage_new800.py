from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path

import numpy as np
import torch
from sentence_transformers import InputExample, SentenceTransformer, losses
from torch.utils.data import DataLoader


STAGE1_TRAIN_FILE = Path(
    "/data/xingkun/coder_data/train_data/ant-syn word level/triplets/combined_triplets.jsonl"
)
STAGE2_TRAIN_FILE = Path(
    "/data/xingkun/coder_data/train_data/excluir_nevir_new800_prefixed_query_triplets.jsonl"
)
DEFAULT_BASE_MODEL = Path("/data/xingkun/local_model/bge-large-en-v1.5")
DEFAULT_OUTPUT_ROOT = Path(
    "/data/xingkun/encoder-b-checkpoints/bge-large-ant_then_prefixed_excluir_nevir_new800_triplets"
)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def triplet_rows_to_examples(rows: list[dict]) -> list[InputExample]:
    examples: list[InputExample] = []
    for row in rows:
        query = row.get("query", "").strip()
        positive = row.get("positive", "").strip()
        hard_negative = row.get("hard_negative", "").strip()
        if not query or not positive or not hard_negative:
            continue
        examples.append(InputExample(texts=[query, positive, hard_negative]))
    return examples


def train_stage(
    *,
    base_model: str,
    train_examples: list[InputExample],
    output_dir: Path,
    epochs: int,
    batch_size: int,
    max_seq_length: int,
    warmup_ratio: float,
    seed: int,
) -> None:
    if not train_examples:
        raise RuntimeError(f"No training examples for {output_dir}")

    set_seed(seed)
    output_dir.mkdir(parents=True, exist_ok=True)

    model = SentenceTransformer(base_model)
    model.max_seq_length = max_seq_length
    loader = DataLoader(train_examples, shuffle=True, batch_size=batch_size)
    train_loss = losses.MultipleNegativesRankingLoss(model=model)
    warmup_steps = max(1, int(len(loader) * epochs * warmup_ratio))

    print(f"Training {output_dir}")
    print(f"  base_model: {base_model}")
    print(f"  examples: {len(train_examples)}")
    print(f"  epochs: {epochs}")
    print(f"  batch_size: {batch_size}")
    print(f"  max_seq_length: {max_seq_length}")
    print(f"  steps_per_epoch: {len(loader)}")
    print(f"  warmup_steps: {warmup_steps}")

    model.fit(
        train_objectives=[(loader, train_loss)],
        epochs=epochs,
        warmup_steps=warmup_steps,
        output_path=str(output_dir),
        show_progress_bar=True,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Two-stage fine-tune bge-large-en-v1.5 on ant-syn then "
            "prefixed excluir+nevir new800 triplets."
        )
    )
    parser.add_argument("--base-model", type=str, default=str(DEFAULT_BASE_MODEL))
    parser.add_argument("--output-root", type=str, default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--stage1-epochs", type=int, default=1)
    parser.add_argument("--stage2-epochs", type=int, default=1)
    parser.add_argument("--stage1-batch-size", type=int, default=16)
    parser.add_argument("--stage2-batch-size", type=int, default=16)
    parser.add_argument("--stage1-max-seq-length", type=int, default=128)
    parser.add_argument("--stage2-max-seq-length", type=int, default=512)
    parser.add_argument("--warmup-ratio", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--stage",
        choices=("both", "1", "2"),
        default="both",
        help="Train stage 1 only, stage 2 only, or both sequentially.",
    )
    parser.add_argument(
        "--stage1-checkpoint",
        type=str,
        default="",
        help="Optional stage-1 checkpoint path when running --stage 2 only.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if "CUDA_VISIBLE_DEVICES" not in os.environ:
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    output_root = Path(args.output_root)
    stage1_output = Path(f"{output_root}-stage1")
    final_output = output_root

    if args.stage in {"both", "1"}:
        stage1_rows = read_jsonl(STAGE1_TRAIN_FILE)
        stage1_examples = triplet_rows_to_examples(stage1_rows)
        train_stage(
            base_model=args.base_model,
            train_examples=stage1_examples,
            output_dir=stage1_output,
            epochs=args.stage1_epochs,
            batch_size=args.stage1_batch_size,
            max_seq_length=args.stage1_max_seq_length,
            warmup_ratio=args.warmup_ratio,
            seed=args.seed,
        )
        stage1_model_path = str(stage1_output)
    else:
        stage1_model_path = args.stage1_checkpoint or str(stage1_output)
        if not Path(stage1_model_path).exists():
            raise FileNotFoundError(f"Stage 1 checkpoint not found: {stage1_model_path}")

    if args.stage in {"both", "2"}:
        stage2_rows = read_jsonl(STAGE2_TRAIN_FILE)
        stage2_examples = triplet_rows_to_examples(stage2_rows)
        train_stage(
            base_model=stage1_model_path,
            train_examples=stage2_examples,
            output_dir=final_output,
            epochs=args.stage2_epochs,
            batch_size=args.stage2_batch_size,
            max_seq_length=args.stage2_max_seq_length,
            warmup_ratio=args.warmup_ratio,
            seed=args.seed,
        )

    print("Training complete.")
    if args.stage in {"both", "1"}:
        print(f"Stage 1 checkpoint: {stage1_output}")
    if args.stage in {"both", "2"}:
        print(f"Final checkpoint: {final_output}")


if __name__ == "__main__":
    main()
