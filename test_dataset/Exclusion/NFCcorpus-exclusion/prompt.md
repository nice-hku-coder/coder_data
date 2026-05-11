  {
    "_id": "MED-3492",
    "title": "Effects of a natural extract of (-)-hydroxycitric acid (HCA-SX) and a combination of HCA-SX plus niacin-bound chromium and Gymnema sylvestre extrac...",
    "text": "AIM: The efficacy of optimal doses of highly bioavailable (-)-hydroxycitric acid (HCA-SX) alone and in combination with niacin-bound chromium (NBC) and a standardized Gymnema sylvestre extract (GSE) on weight loss in moderately obese subjects was evaluated by monitoring changes in body weight, body mass index (BMI), appetite, lipid profiles, serum leptin and excretion of urinary fat metabolites. HCA-SX has been shown to reduce appetite, inhibit fat synthesis and decrease body weight without stimulating the central nervous system. NBC has demonstrated its ability to maintain healthy insulin levels, while GSE has been shown to regulate weight loss and blood sugar levels. METHODS: A randomized, double-blind, placebo-controlled human study was conducted in Elluru, India for 8 weeks in 60 moderately obese subjects (ages 21-50, BMI >26 kg/m(2)). Subjects were randomly divided into three groups. Group A was administered HCA-SX 4667 mg, group B was administered a combination of HCA-SX 4667 mg, NBC 4 mg and GSE 400 mg, while group C was given placebo daily in three equally divided doses 30-60 min before meals. All subjects received a 2000 kcal diet/day and participated in supervised walking. RESULTS: At the end of 8 weeks, body weight and BMI decreased by 5-6% in both groups A and B. Food intake, total cholesterol, low-density lipoproteins, triglycerides and serum leptin levels were significantly reduced in both groups, while high-density lipoprotein levels and excretion of urinary fat metabolites increased in both groups. A marginal or non-significant effect was observed in all parameters in group C. CONCLUSION: The present study shows that optimal doses of HCA-SX and, to a greater degree, the combination of HCA-SX, NBC and GSE can serve as an effective and safe weight-loss formula that can facilitate a reduction in excess body weight and BMI, while promoting healthy blood lipid levels.",
    "text_length": 11,
    "matched_queries": [
      "high",
      "decrease",
      "safe",
      "end",
      "healthy",
      "reduce",
      "present",
      "day",
      "blind",
      "fat",
      "all",
      "loss",
      "equally",
      "low",
      "divided",
      "double",
      "regulate",
      "significant",
      "effective",
      "human",
      "decreased",
      "on",
      "central",
      "stimulating",
      "significantly",
      "synthesis",
      "efficacy",
      "moderately",
      "bound",
      "ability"
    ],
    "matched_query_count": 30
  },

将以上文档按照语义分为2-5个子文档，每个子文档可包含多条句子。从这些子文档中选择任意一个生成query，请尽量选择有不容易出现在其他文档里的少见词或少见短语的，同时要求该query包含从matched_queries里面选的一个关键词；同时保持和其他文档的相关性。然后再生成一个子文档，要求该子文档：基础是前面所选中的那个文档；仅将该文档中某个明确存在的研究对象、干预措施、药物、暴露因素、风险因素、疾病/症状、病原体、实验条件、检测指标、结局变量、人群特征或生物医学实体改为 exclusion 表达，优先使用 without 或 excluding。注意不要机械地在关键词前直接加 without 导致语法不自然，可以做最小局部改写，例如将 “with X” 改为 “without X”，或将 “including X” 改为 “excluding X”。修改后的子文档必须显式表达“不包含/排除该对象”，且不能和该子文档其他地方有语义矛盾。最后再补一条 pair query，和前面生成的 query 的区别是把 inclusion 表达改成 exclusion 表达，例如 with/without 或 including/excluding。一对 query 还要保证标注的 constraint_satisfying_doc_ids 与 constraint_violating_doc_ids 以及 graded_relevance 分数相反，但 topical_relevant_doc_ids 一致。

以下是 exclusion 类型的示例（不强制要求一个句子一个子文档）：
{"doc_id": "MED-3538-1", "text": "The study investigated the consequences of chronically reduced human sleep by comparing chronic sleep restriction with total sleep deprivation."}
{"doc_id": "MED-3538-2", "text": "The chronic sleep restriction experiment involved randomization to one of three sleep doses: 4 h, 6 h, or 8 h time in bed per night for 14 consecutive days. The study protocol also included total sleep deprivation, involving 3 nights with 0 h time in bed."}
{"doc_id": "MED-3538-3", "text": "Both experiments were conducted under standardized laboratory conditions with continuous behavioral, physiological, and medical monitoring. The participants were 48 healthy adults aged 21 to 38."}
{"doc_id": "MED-3538-4", "text": "Chronic restriction of sleep to 4 h or 6 h per night produced significant cumulative, dose-dependent deficits in cognitive performance. Subjective sleepiness ratings showed an acute response but did not significantly differentiate the 6 h and 4 h conditions."}
{"doc_id": "MED-3538-5", "text": "Lapses in behavioral alertness were near-linearly related to the cumulative duration of wakefulness in excess of 15.84 h, suggesting that sleep debt has a neurobiological cost that accumulates over time."}
{"doc_id": "MED-3538-6", "text": "The chronic sleep restriction experiment involved randomization to one of three sleep doses: 4 h, 6 h, or 8 h time in bed per night for 14 consecutive days. The study protocol excluding total sleep deprivation and focused only on the chronic sleep restriction conditions."}

{"query_id": "q-MED-3538-1", "query": "The study protocol included total sleep deprivation alongside chronic sleep restriction in healthy adults.", "category": "exclusion", "topical_relevant_doc_ids": ["MED-3538-1", "MED-3538-2", "MED-3538-3", "MED-3538-4", "MED-3538-5", "MED-3538-6"], "constraint_satisfying_doc_ids": ["MED-3538-2"], "constraint_violating_doc_ids": ["MED-3538-6"], "graded_relevance": {"MED-3538-1": 1.0, "MED-3538-2": 2.0, "MED-3538-3": 1.0, "MED-3538-4": 1.0, "MED-3538-5": 1.0, "MED-3538-6": 0.0}}
{"query_id": "q-MED-3538-2", "query": "The study protocol excluding total sleep deprivation and focused on chronic sleep restriction in healthy adults.", "category": "exclusion", "topical_relevant_doc_ids": ["MED-3538-1", "MED-3538-2", "MED-3538-3", "MED-3538-4", "MED-3538-5", "MED-3538-6"], "constraint_satisfying_doc_ids": ["MED-3538-6"], "constraint_violating_doc_ids": ["MED-3538-2"], "graded_relevance": {"MED-3538-1": 1.0, "MED-3538-2": 0.0, "MED-3538-3": 1.0, "MED-3538-4": 1.0, "MED-3538-5": 1.0, "MED-3538-6": 2.0}}