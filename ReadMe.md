# Relevance Theory Script 2.0使用方法
## 1. setting.json
用于填入标准格式的场景
## 2. instruction_A.txt & instruction_B.txt
分别用于填入A和B生成对话的prompting
## 3. script.txt
存储仅包含对话的生成结果
## 4. script_all.txt
存储包含对话和推理链的生成结果
## 5. test_question.txt
测试的问题
## 6. test_question_ans.txt
测试问题得到的答案
## 7. score_criteria_mutual.txt
互评标准
## 8. score_criteria_self.txt
自评标准
## 9. score_criteria.txt
评价标准
## 10. score_details.txt
评分细节
## 11. score_summary.txt
仅提取得分
## Notice
因为instruction中包含“分析上一句话”，导致第一轮对话没有上一句话时LLM会产生有上一句话的幻觉，所以我让LLM先不带推理地生成了第一轮A的发言