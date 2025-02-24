import json
from openai import OpenAI

# 初始化 OpenAI 客户端
client = OpenAI(base_url="http://115.182.62.174:18888/v1", api_key="zQTxB4T2yXBFeoBtE7418192Df3e476a84259d84D9015cC1")
model_name = "gpt-4o"

# 读取 JSON 配置
with open('setting.json', 'r', encoding='utf-8') as file:
    settings = json.load(file)

# 选取第一个对话主题
selected_theme = settings[0]  # 选择 JSON 数组的第一项

# 提取 `role_A` 和 `role_B`
content_role_A = f"Role A:\nCharacter: {selected_theme['role_A']['character']}\nBehavior: {selected_theme['role_A']['behavior']}\nGoal: {selected_theme['role_A']['goal']}"
content_role_B = f"Role B:\nCharacter: {selected_theme['role_B']['character']}\nBehavior: {selected_theme['role_B']['behavior']}\nGoal: {selected_theme['role_B']['goal']}"

# 读取 `setting`
content_setting = selected_theme["background"]

# 读取 `instruction_A` 和 `instruction_B`
with open('instruction_A.txt', 'r', encoding='utf-8') as file:
    content_instruction_A = file.read().strip()
with open('instruction_B.txt', 'r', encoding='utf-8') as file:
    content_instruction_B = file.read().strip()
    
# 读取 `test_question`
with open('test_question.txt', 'r', encoding='utf-8') as file:
    test_question = file.read().strip()

# 清空 script.txt 和 script_all.txt 和 info_test_result.txt
for file_name in ['script.txt', 'script_all.txt', 'test_question_ans.txt']:
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write("")

def extract_utterance(raw_content):
    """提取对话中的 A 和 B 的发言部分"""
    lines = raw_content.split("\n")
    utterances = [line.strip() for line in lines if line.startswith("A:") or line.startswith("B:")]
    return "\n".join(utterances)

def generate_initial_script():
    """生成第一轮对话"""

    # `A` 先生成第一句
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Setting: {content_setting}\n{content_role_A}\n\nA, based on your role and the background, generate your first utterance.\n(Additional requirements: Only one line in the answer starts with 'A:'.)"}
    ]
    response_A = client.chat.completions.create(model=model_name, messages=messages)
    A_utterance = response_A.choices[0].message.content

    # `B` 分析 `A` 的第一句并生成回应
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Setting: {content_setting}\n{content_role_B}\n{content_instruction_B}\nA's first utterance: {A_utterance}\nB, based on your role and the background, and strictly following the steps and format of instruction_B, generate your response.\n(Additional requirements: Only one line in the answer starts with 'B:',Do not make any bold modifications either.)"}
    ]
    response_B = client.chat.completions.create(model=model_name, messages=messages)
    B_utterance = response_B.choices[0].message.content

    # 组合 A 和 B 的对话
    script = f"all scripts A: \n{A_utterance}\n\nall scripts B: \n{B_utterance}"
    return script

def generate_followup_script(prev_script):
    """基于上一轮对话生成下一轮对话，并进行心理推理"""
    messages_A = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Setting: {content_setting}\n{content_role_A}\n{content_instruction_A}\nPrevious conversation:\n{prev_script}\nA, based on your role and the background and previous conversation, and strictly following the steps and format of instruction_A, generate your response.\n(Additional requirements: Only one line in the answer starts with 'A:',Do not make any bold modifications either.)"}
    ]
    response_A = client.chat.completions.create(model=model_name, messages=messages_A)
    A_utterance = response_A.choices[0].message.content.strip()

    messages_B = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Setting: {content_setting}\n{content_role_B}\n{content_instruction_B}\nPrevious conversation:\n{prev_script}\nB, based on your role and the background and previous conversation, and strictly following the steps and format of instruction_B, generate your response.\n(Additional requirements: Only one line in the answer starts with 'B:',Do not make any bold modifications either.)"}
    ]
    response_B = client.chat.completions.create(model=model_name, messages=messages_B)
    B_utterance = response_B.choices[0].message.content.strip()

    new_script = f"all scripts of A: \n{A_utterance}\n\nall scripts of B: \n{B_utterance}"
    return new_script

# def ask_information_test_question(script):
#     """向模型询问与对话相关的问题，以测试信息掌握情况"""
#     messages = [
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": f"Based on the following conversation, answer the question (in Chinese):\n{script}\n\n{test_question}"}
#     ]
#     response = client.chat.completions.create(model=model_name, messages=messages)
#     return response.choices[0].message.content.strip()

# 运行对话模拟
script_all = f"Round 0:\n{generate_initial_script()}"  # 生成第一轮对话
script = f"Round 0:\n" + extract_utterance(script_all)

for i in range(2):  # 进行 10 轮对话
    # 提示进度
    print(f"Round {i + 1} is running...")
    
    new_utterance = generate_followup_script(script)  # 交替生成
    script += f"\n\nRound {i + 1}:\n" + extract_utterance(new_utterance)  # 追加对话
    script_all += f"\n\nRound {i + 1}:\n" + new_utterance  # 追加完整对话
    
    # 进行信息测试(感觉应该加在B发言之后)
    # test_question_ans = ask_information_test_question(script_all)
    # with open('test_question_ans.txt', 'a', encoding='utf-8') as file:
    #     file.write(f"Round {i + 1}:\n" + test_question_ans + "\n")

# 保存最终的对话脚本
with open('script.txt', 'w', encoding='utf-8') as file:
    file.write(script)
with open('script_all.txt', 'w', encoding='utf-8') as file:
    file.write(script_all)
    
# 对对话进行评价
def load_criteria():
    """加载评分标准"""
    with open('score_criteria.txt', 'r', encoding='utf-8') as file:
        criteria = file.read().strip()
    return criteria

def evaluate_script(script):
    """评价对话脚本"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"background: {content_setting}\n{content_role_A}\n{content_role_B}\nConversation:\n{script}\n\n{load_criteria()}"}
    ]
    response = client.chat.completions.create(model=model_name, messages=messages)
    return response.choices[0].message.content.strip()

# 将评价结果写入文件 score_details.txt
print(f"Evaluating the script...")
evaluation = evaluate_script(script)
with open('score_details.txt', 'w', encoding='utf-8') as file:
    file.write(evaluation)

# 将最终得分写入文件 score_summary.txt (提取“final_scores:”开头的行)
with open('score_details.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
    final_scores = [line for line in lines if line.startswith("final_scores:")]
with open('score_summary.txt', 'w', encoding='utf-8') as file:
    for line in final_scores:
        file.write(line)
