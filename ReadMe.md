# Relevance Theory Script 2.0使用方法
## 1. setting.txt
用于填入Scenario
## 2. instruction_A.txt & instruction_B.txt
分别用于填入A和B生成对话的prompting
## 3. script.txt
存储仅包含对话的生成结果
## 4. all_script.txt
存储包含对话和推理链的生成结果
## Notice
因为instruction中包含“分析上一句话”，导致第一轮对话没有上一句话时LLM会产生有上一句话的幻觉，所以我让LLM先不带推理地生成了第一轮对话