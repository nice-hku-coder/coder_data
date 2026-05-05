# SciFact

`scifact` 文件夹包含当前实验使用的 SciFact 数据子集。`corpus.jsonl` 存放语料库文档内容，`claim_contradict_topic_relevant.jsonl` 存放每条 claim（均带有 `CONTRADICT` 证据）对应的主题相关文档 ID 列表（用于检索与评估）。

`scifact_antonym` 文件夹包含 SciFact-Antonym 数据子集。`corpus_length_stats.csv` 和 `corpus_length_summary.txt` 存放sicfact语料库文档长度的统计信息，我根据它挑选了句数 9–25 句，词数约 180–600 词的文档到 `corpus_candidate.jsonl`，然后根据以下原则形成了 `queries_antonym.jsonl` 和 `corpus_antonym.jsonl`：
1. 把一个文档切成几部分（2-5部分），每个部分几句话
2. 抽取其中某个部分，针对其中的某关键词（容易找到反义词的）人工生成 paired-queries，一个是含该词的query，另一个是含该词的反义词的query。然后抽出来的这一部分直接成为constraint_satisfying_doc
3. 将constraint_satisfying_doc中的刚刚选中的那个词改为反义词然后形成constraint_violating_doc
4. constraint_satisfying_doc、constraint_violating_doc再加上其余没抽中的部分作为topical_relevant_doc。因为它们原本是在一个文档里的，可以算是话题相关

> **潜在的问题**：constraint_violating_doc可能在语义上与constraint_satisfying_doc非常相似，甚至可能在某些情况下仍然满足约束条件（例如反义词在特定上下文中可能不完全违背原意），因为本质上它们只有一对正反义词的差距。

> 一个trival的想法是将文档切的更细粒度，比如一句话一个文档，这样改变其中某个关键词就足以改变这一个文档的语义。