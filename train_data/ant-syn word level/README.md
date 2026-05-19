`ant_pairs.jsonl` 和 `syn_pairs.jsonl` w1 和 w2 互为 近义/反义 词

`build_stage1_lexical_triplets.py` 
```
python build_stage1_lexical_triplets.py \
  --syn_file syn_pairs.jsonl \
  --ant_file ant_pairs.jsonl \
  --out_dir antsyn_triplets \
  --seed 42 \
  --val_ratio 0.1 \
  --max_pos_per_anchor 10 \
  --max_neg_per_anchor 10 \
  --max_triplets_per_anchor 20
```
- 创造用来训练的 triplet

`build_stage2_phrase_triplets.py`
```
python build_stage2_phrase_triplets.py \
  --syn_file syn_pairs.jsonl \
  --ant_file ant_pairs.jsonl \
  --out_dir not_triplets \
  --seed 42 \
  --val_ratio 0.1

python build_stage2_phrase_triplets.py \
  --syn_file syn_pairs.jsonl \
  --ant_file ant_pairs.jsonl \
  --out_dir exclusion_triplets \
  --templates "not {x}" "without {x}" "excluding {x}" "no {x}" \
  --seed 42 \
  --val_ratio 0.1
```
- 创造用来训练的 triplet

