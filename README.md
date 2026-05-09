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



# 生成 Negation Prompt
```
{
  "hotel_url": "Hotel_Review-g147278-d240969-Reviews-Papagayo_Beach_Resort-Willemstad_Curacao.html",
  "author": "lakeviewandsunsets",
  "date": "2015-01-01T00:00:00",
  "rating": 4.0,
  "title": "Great place to relax if you need down time",
  "text": "My friend and I stayed at the resort for one week with a sea view. We each had our own bedroom and bathroom which worked perfect for us. The veranda was large and comfortable with a nice breeze. Each bedroom had air conditioning. We went to the local grocery store which was within walking distance to pick up food for breakfast and lunch and wine. We enjoyed the food in the local restaurants and walked to one approximately 20 minutes away called Pop's and the food was also good. The spa was excellent. Orientation Suggestion: The resort needs to provide guests with an orientation upon arrival or first thing the next morning (general information on the grounds, suggested tour groups, where to eat, where is the grocery store, what is available at the beach, where to get the bus, taxi service available, where to rent a car, any special events taking place when they are visiting). Update the a website: Review what is listed as the information is misleading. For example there is no beach where you can walk along in the water, you need an adapter, etc. Visitors should know what to expect when they arrive. The local people we met in Curacao were friendly and helpful. We were told by a few of the locals not to be alone in town especially at night, be aware of your surroundings at all times, do not leave anything unattended, and do not stop if anyone asks you for money. Overall, it is a beautiful small island. If you are on a cruise, it is worth taking a day trip to see the island.",
  "property_dict": {},
  "_sentence_count": 15
},

将以上文档按照语义分为2-5个子文档，每个子文档可包含多条句子。从这些子文档中选择任意一个生成query，请尽量选择有不容易出现在其他review里的少见词或少见短语的，同时要求该query包含所选子文档的一个关键词；同时保持和其他文档的相关性。然后再生成一个子文档，要求该子文档：基础是前面所选中的那个文档；仅在该文档中的那个关键词前面加上no或not，关键词请选择形容词(少见词和关键词不一定是同一个，关键词可以不是形容词)，但需要注意修改后的加了否定的关键词不能和该子文档其他地方有语义矛盾。最后再补一条pair query，和前面生成的query的区别是关键词前面加上no或not。一对query还要保证标注的constraint_satisfying_doc_ids与constraint_violating_doc_ids以及graded_relevance分数相反，但topical_relevant_doc_ids一致。

以下是示例（不强制要求一个句子一个子文档）：
{"doc_id": "hotel-272455-369rd-1", "text": "El Mosaico del Sol was the best hotel experience the reviewer had ever had. Everyone on the staff was very friendly. The guests were provided a ride to and from the airport, which was very generous."}
{"doc_id": "hotel-272455-369rd-2", "text": "The cleaning staff was very friendly and did an excellent job at cleaning. Breakfast and Happy Hour were delicious."}
{"doc_id": "hotel-272455-369rd-3", "text": "The accommodations were wonderful and beautiful. Outside, the pool was serene, and upstairs there was a trendy and comfortable terrace."}
{"doc_id": "hotel-272455-369rd-4", "text": "The rooms were like apartments, with kitchenettes, a dining area, and a living room. There was a lot of space."}
{"doc_id": "hotel-272455-369rd-5", "text": "The location was prime, close to the town with great gelato and food, and shortly near some beautiful beaches. The owner Renato would bend over backwards to make sure guests enjoyed everything. The reviewer described the hotel, location, and staff as excellent quality and hoped to return soon."}
{"doc_id": "hotel-272455-369rd-6", "text": "The cleaning staff was very friendly and did an excellent job at cleaning. Breakfast and Happy Hour were not delicious."}

{"query_id": "q-hotel-272455-369rd-1", "query": "Breakfast and Happy Hour were delicious at El Mosaico del Sol.", "category": "negation", "topical_relevant_doc_ids": ["hotel-272455-369rd-1", "hotel-272455-369rd-2", "hotel-272455-369rd-3", "hotel-272455-369rd-4", "hotel-272455-369rd-5", "hotel-272455-369rd-6"], "constraint_satisfying_doc_ids": ["hotel-272455-369rd-2"], "constraint_violating_doc_ids": ["hotel-272455-369rd-6"], "graded_relevance": {"hotel-272455-369rd-1": 1.0, "hotel-272455-369rd-2": 2.0, "hotel-272455-369rd-3": 1.0, "hotel-272455-369rd-4": 1.0, "hotel-272455-369rd-5": 1.0, "hotel-272455-369rd-6": 0.0}}
{"query_id": "q-hotel-272455-369rd-2", "query": "Breakfast and Happy Hour were not delicious at El Mosaico del Sol.", "category": "negation", "topical_relevant_doc_ids": ["hotel-272455-369rd-1", "hotel-272455-369rd-2", "hotel-272455-369rd-3", "hotel-272455-369rd-4", "hotel-272455-369rd-5", "hotel-272455-369rd-6"], "constraint_satisfying_doc_ids": ["hotel-272455-369rd-6"], "constraint_violating_doc_ids": ["hotel-272455-369rd-2"], "graded_relevance": {"hotel-272455-369rd-1": 1.0, "hotel-272455-369rd-2": 0.0, "hotel-272455-369rd-3": 1.0, "hotel-272455-369rd-4": 1.0, "hotel-272455-369rd-5": 1.0, "hotel-272455-369rd-6": 2.0}}
```
- 当前数据来源是 `HotelRec_text_15to20_sentences_5000.json`
