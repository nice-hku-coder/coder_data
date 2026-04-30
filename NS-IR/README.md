阅读理解一下这篇文章 https://arxiv.org/pdf/2505.22299 ，它说它提出了一个新的 dataset NegConstraint。从第一个截图里你能看到它把query 分成了3类。 这些query可以在 https://github.com/troyyxk/NS-IR-main/blob/main/NegConstraint/queries.jsonl 里面找到，总数量对得上，不过没有对应的是三类中的哪一个的标签。请阅读每一个query，把他们归类到对应的类下面。

---

我已经把 366 条 query 全部归类好了。论文里第 5 节说明：`A/a/B/b` 表示实体集合，小写是大写集合的子集；`-` 是 negative constraint，`∪` 是 union，并给出三类数量分别为 136、123、107。仓库的 `NegConstraint` 目录里确实有 `queries.jsonl`、`corpus.jsonl`、`test.tsv`。([arXiv][1]) ([GitHub][2])

分类过程中有个重要问题：**按 query 文本逐条语义阅读，三类数量并不严格等于论文表里的 136/123/107**。例如 `_id=4` 的 query 文本没有显式 negative constraint；而 `_id=271` 明确写了 `(A)/(a)/(B)/(b)` 风格，语义上明显属于 `(A - a) ∪ (B - b)`。([GitHub][3])
所以我给了两套结果：

1. **textual_semantic**：按每条 query 的实际文本语义归类，推荐作为“读 query 文本本身”的标签。
   计数：`A - a = 132`，`(A - a) ∪ B = 90`，`(A - a) ∪ (B - b) = 144`。

2. **paper_count_aligned_best_fit**：强制对齐论文表格的 136/123/107，用于需要复现论文统计口径的情况。
   计数：`A - a = 136`，`(A - a) ∪ B = 123`，`(A - a) ∪ (B - b) = 107`。但这套会把一些文本上明显像第三类的 late IDs 放到第二类，所以我不建议把它当作纯语义真值。

文件如下：

* [合并版 CSV：每个 `_id` 同时给出两套标签](sandbox:/mnt/data/negconstraint_labels_combined.csv)
* [合并版 JSONL](sandbox:/mnt/data/negconstraint_labels_combined.jsonl)
* [推荐的文本语义版 CSV](sandbox:/mnt/data/negconstraint_labels_textual_semantic.csv)
* [推荐的文本语义版 JSONL](sandbox:/mnt/data/negconstraint_labels_textual_semantic.jsonl)
* [论文计数对齐版 CSV](sandbox:/mnt/data/negconstraint_labels_paper_count_aligned_best_fit.csv)
* [论文计数对齐版 JSONL](sandbox:/mnt/data/negconstraint_labels_paper_count_aligned_best_fit.jsonl)
* [分组与说明 Markdown](sandbox:/mnt/data/negconstraint_label_summary.md)

这些文件都用原始 `queries.jsonl` 的 `_id` 做 key，可以直接和原 query 文件 join。

[1]: https://arxiv.org/pdf/2505.22299 "Logical Consistency is Vital: Neural-Symbolic Information Retrieval for Negative-Constraint Queries"
[2]: https://github.com/troyyxk/NS-IR-main/tree/main/NegConstraint "NS-IR-main/NegConstraint at main · troyyxk/NS-IR-main · GitHub"
[3]: https://github.com/troyyxk/NS-IR-main/blob/main/NegConstraint/queries.jsonl "NS-IR-main/NegConstraint/queries.jsonl at main · troyyxk/NS-IR-main · GitHub"
