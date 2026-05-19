# NegConstraint_labeled

这个目录提供一个**带 query 类别标注**的 NegConstraint 数据集版本。

## 数据来源

- 原始 BEIR 风格数据来自 [`NS-IR-main/NegConstraint`](../../NS-IR-main/NegConstraint)
- 两套 query 类别标签来自 [`coder_data/NS-IR`](../NS-IR)

## 目录结构

- [`corpus.jsonl`](./corpus.jsonl): 原始语料文件
- [`queries.jsonl`](./queries.jsonl): 原始查询文件
- [`qrels/test.tsv`](./qrels/test.tsv): 原始 qrels 文件，已调整为 BEIR 常见目录结构
- [`labels_textual_semantic.jsonl`](./labels_textual_semantic.jsonl): 按 query 文本语义人工标注的类别映射
- [`labels_textual_semantic.csv`](./labels_textual_semantic.csv): 同上，CSV 版本
- [`labels_paper_count_aligned_best_fit.jsonl`](./labels_paper_count_aligned_best_fit.jsonl): 对齐论文计数口径的类别映射
- [`labels_paper_count_aligned_best_fit.csv`](./labels_paper_count_aligned_best_fit.csv): 同上，CSV 版本
- [`query_labels_combined.jsonl`](./query_labels_combined.jsonl): 将两套标签合并到同一条记录，便于 join / 检查
- [`query_labels_combined.csv`](./query_labels_combined.csv): 合并标签的 CSV 版本
- [`label_summary.md`](./label_summary.md): 标签说明文档副本

## 标签字段

标签映射文件统一使用以下字段：

- `query_id`: 对应 [`queries.jsonl`](./queries.jsonl) 中的 `_id`
- `formulation`: query 所属类别
- `method`: 标签方案名称

合并文件使用以下字段：

- `query_id`
- `textual_semantic_formulation`
- `paper_count_aligned_best_fit_formulation`

## 类别集合

共有三类 NegConstraint query：

- `A - a`
- `(A - a) ∪ B`
- `(A - a) ∪ (B - b)`

## 规模与完整性

- query 总数：366
- 两套标签都已经按 `query_id` 与全部 query 对齐
- 原始 BEIR 三件套保持不变，仅新增标签映射与说明文件

## 使用建议

- 若希望按 query 文本本身进行类别分析，优先使用 [`labels_textual_semantic.jsonl`](./labels_textual_semantic.jsonl)
- 若希望复现论文表中的类别计数口径，可使用 [`labels_paper_count_aligned_best_fit.jsonl`](./labels_paper_count_aligned_best_fit.jsonl)
- 在评测脚本中，可将标签文件按 `query_id` join 到 [`queries.jsonl`](./queries.jsonl) 或评测结果的 per-query 输出上，以支持分组统计
