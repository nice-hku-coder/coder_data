# 从 med-01 中移除的 query 和 corpus
```
{
    "query_id":"drug_q003", 
    "query":"I need depression medicine that improves energy, not hunger, fogginess, or daytime sluggishness.", 
    "target_drug":"bupropion", 
    "category":"negation", 
    "constraint_satisfying_doc_ids":["drugdoc_03_gold"], 
    "constraint_violating_doc_ids":["drugdoc_03_wrong"], 
    "expected_wrong_doc_ids":["drugdoc_03_wrong"], 
    "topical_relevant_doc_ids":["drugdoc_03_gold", "drugdoc_03_wrong"], 
    "desired_attributes":["brighter", "energized", "no fogginess"], 
    "forbidden_attributes":["hunger", "fogginess", "sluggishness"], 
    "answer_gold":"bupropion"
}
{
    "query_id":"drug_q006", 
    "query":"I need allergy medicine for class that is not drowsy, foggy, or slow.", 
    "target_drug":"loratadine", 
    "category":"negation", 
    "constraint_satisfying_doc_ids":["drugdoc_06_gold"], 
    "constraint_violating_doc_ids":["drugdoc_06_wrong"], 
    "expected_wrong_doc_ids":["drugdoc_06_wrong"], 
    "topical_relevant_doc_ids":["drugdoc_06_gold", "drugdoc_06_wrong"], 
    "desired_attributes":["alert", "quick", "allergy eased"], 
    "forbidden_attributes":["drowsy", "foggy", "slow"], 
    "answer_gold":"loratadine"
}
{
    "query_id":"drug_q015", 
    "query":"I need bladder medicine that keeps thoughts clear and mouth moist rather than dry and foggy.", 
    "target_drug":"mirabegron", 
    "category":"antonym", 
    "constraint_satisfying_doc_ids":["drugdoc_15_gold"], 
    "constraint_violating_doc_ids":["drugdoc_15_wrong"], 
    "expected_wrong_doc_ids":["drugdoc_15_wrong"], 
    "topical_relevant_doc_ids":["drugdoc_15_gold", "drugdoc_15_wrong"], 
    "desired_attributes":["fewer urgency episodes", "clear-headed", "moist mouth"], 
    "forbidden_attributes":["dry", "foggy", "mentally slow"], 
    "answer_gold":"mirabegron"
}
```
```
{"doc_id": "drugdoc_03_gold", "drug": "bupropion", "text": "One bupropion user felt brighter and energized through the day without fogginess or extra hunger.", "role": "satisfying", "source": "synthetic_drug_end2end_v1"}
{"doc_id": "drugdoc_03_wrong", "drug": "mirtazapine", "text": "One mirtazapine user sought depression help but reported hunger, fogginess, and daytime sluggishness.", "role": "violating", "source": "synthetic_drug_end2end_v1"}
{"doc_id": "drugdoc_06_gold", "drug": "loratadine", "text": "One loratadine user had allergy symptoms ease while staying alert and quick in class.", "role": "satisfying", "source": "synthetic_drug_end2end_v1"}
{"doc_id": "drugdoc_06_wrong", "drug": "diphenhydramine", "text": "One diphenhydramine user treated allergies but became drowsy, foggy, and slow in class.", "role": "violating", "source": "synthetic_drug_end2end_v1"}
{"doc_id": "drugdoc_15_gold", "drug": "mirabegron", "text": "One mirabegron user had fewer urgency episodes while staying clear-headed with a moist mouth.", "role": "satisfying", "source": "synthetic_drug_end2end_v1"}
{"doc_id": "drugdoc_15_wrong", "drug": "oxybutynin", "text": "One oxybutynin user had bladder help but became dry-mouthed, foggy, and mentally slow.", "role": "violating", "source": "synthetic_drug_end2end_v1"}
```

# 从 med-02 中移动过来
