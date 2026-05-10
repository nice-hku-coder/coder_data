{
  "hotel_url": "Hotel_Review-g187437-d290366-Reviews-Gran_Hotel_Elba_Estepona_Thalasso_Spa-Estepona_Costa_del_Sol_Province_of_Malaga_Andaluc.html",
  "author": "Khurmatulla",
  "date": "2015-11-01T00:00:00",
  "rating": 3.0,
  "title": "Angels and Dragons detected in sky",
  "text": "Please check photo and if you don't see any dragon and angel flying then you've never beed a dreamer. Now let's shift to review: 1. coast line covered with sand but you will be needed for swimming sleepers otherwice you can hurt your feet 2. hotel for 50+ people means no any of children facilities (only one small children swimpool with no water varning system) 3. kitchen is good but same all the time 4. IT IS NOT SPA HOTEL! Dear menagers please go to Thailand (for training) and study what is spa-hotel 5. very important: right next beach is nude beach and some times naked old gents and ladies are passed to our beach shocking our shildren. Yes we are on side of democracy but not so urgle meaning of that 6. hotel is not on walking distance from city. Be ready to spend at list 30-40 minutes to walk only one way 7. hotel is bit expensive and guess our first and last experience. No, we don't say that this hotel is bad... it is just not hotel what we needed for... 8. wifi signal is poor The rooms are really good and quality of cleaning services and other servicaes are really good.",
  "property_dict": {
    "service": 5.0,
    "sleep quality": 5.0,
    "value": 2.0
  },
  "_sentence_count": 16
},,

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