# Relevance Theory Script使用方法
## 1. setting_easy.json & setting_difficult.json
简单和困难场景的设定
## 2. instruction_A_without_reasoning.txt & instruction_B_without_reasoning.txt
分别用于填入 `A` 和 `B` 生成对话的 `prompting`（不带推理）
## 3. instruction_A.txt & instruction_B.txt
分别用于填入 `A` 和 `B` 生成对话的 `prompting`（带推理）
## 4. token_count.txt
记录消耗的 `tokens` 数量
## 5. token_count.py
通过 `token_count.txt` 计算消耗的 `tokens` 总数
## 6. score_criteria_forA.txt
对 `A` 的评价标准（因为 `B` 是 `npc` ，所以仅评价 `A`）
## 7. {Y/N}_{D/E}_scripts
{带/不带}推理_{困难/简单}场景_对话记录
## 8. script.txt
仅储存每一轮的对话（从 `script.txt` 中提取）
## 9. script_all.txt
储存对话和推理链过程
## 10. consensus_{D/E}_progress
{困难/简单}场景_共识分析（分析 `A` 在对话过程中获取不对称信息的能力）
## 11. criteria_{D/E}
{困难/简单}场景_评价结果（七个维度，根据整个对话进行评价）
## 12. draw.py
根据数据进行绘图
## 13. main_{with/without}_reasoning.py
根据 `setting.json`，{带/不带}推理地生成对话并储存到相应文件夹
## 14. main_criteria.py
对生成的对话进行评价（对话生成完之后进行调用）

## Notice
因为 `instruction` 中包含“分析上一句话”，所以在第一轮中 `LLM` 会先不带推理地生成第一轮 `A` 的发言