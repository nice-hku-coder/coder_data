# SciFact

`beir` 文件夹包含 BEIR 格式的多种数据集。

`scifact_antonym` 文件夹包含粗粒度和细粒度的反义词数据。`corpus_length_stats.csv` 和 `corpus_length_summary.txt` 存放sicfact语料库文档长度的统计信息。
* 对于粗粒度数据集制作：我挑选了句数 9–25 句，词数约 180–600 词的文档到 `corpus_candidate.jsonl`，然后根据以下原则形成了 `queries_antonym.jsonl` 和 `corpus_antonym.jsonl`：
    1. 把一个文档切成几部分（2-5部分），每个部分几句话
    2. 抽取其中某个部分，针对其中的某关键词（容易找到反义词的）人工生成 paired-queries，一个是含该词的query，另一个是含该词的反义词的query。然后抽出来的这一部分直接成为constraint_satisfying_doc
    3. 将constraint_satisfying_doc中的刚刚选中的那个词改为反义词然后形成constraint_violating_doc
    4. constraint_satisfying_doc、constraint_violating_doc再加上其余没抽中的部分作为topical_relevant_doc。因为它们原本是在一个文档里的，可以算是话题相关
* 对于细粒度数据则使用了句数小于等于5的文档，每一句话作为一个部分，然后按照上面类似的原则进行处理。最终形成了 `queries_antonym_coarse_grained.jsonl`、`corpus_antonym_coarse_grained.jsonl`、`queries_antonym_fine_grained.jsonl` 和 `corpus_antonym_fine_grained.jsonl` 四个文件。

`NegConstraint_labeled` 文件夹包含了人工标注的 NS-IR 数据集。