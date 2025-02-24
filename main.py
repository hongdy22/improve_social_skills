from openai import OpenAI

# 初始化 OpenAI 客户端
client = OpenAI(base_url="http://115.182.62.174:18888/v1", api_key="zQTxB4T2yXBFeoBtE7418192Df3e476a84259d84D9015cC1")
model_name = "gpt-4o"

# 清空script.txt和all_script.txt和info_test_result.txt
with open('script.txt', 'w', encoding='utf-8') as file:
    file.write("")
with open('all_script.txt', 'w', encoding='utf-8') as file:
    file.write("")
with open('info_test_result.txt', 'w', encoding='utf-8') as file:
    file.write("")

# 读入基本 setting
with open('setting.txt', 'r', encoding='utf-8') as file:
    content_setting = file.read().strip()

# 读入生成指令
with open('instruction_A.txt', 'r', encoding='utf-8') as file:
    content_instruction_A = file.read().strip()
with open('instruction_B.txt', 'r', encoding='utf-8') as file:
    content_instruction_B = file.read().strip()
with open('test_question.txt', 'r', encoding='utf-8') as file:
    test_question = file.read().strip()

def extract_utterance(raw_content):
    """提取对话中的 A 和 B 的发言部分"""
    lines = raw_content.split("\n")
    utterances = [line.strip() for line in lines if line.startswith("A:") or line.startswith("B:")]
    return "\n".join(utterances)

def generate_initial_script():
    """生成第一轮对话，不进行推理"""
    # A 先生成第一句
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "setting:" + content_setting + "\nA, based on the setting, generate your first utterance."}
    ]
    response_A = client.chat.completions.create(model=model_name, messages=messages)
    A_utterance = extract_utterance(response_A.choices[0].message.content)

    # B 根据 B 的 instruction 和 setting 进行推理回应
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "instruction:" + content_instruction_B + "\nsetting:" + content_setting + "\nA's first utterance: " + A_utterance + "\nB, based on the instruction and setting, generate your first utterance."}
    ]
    response_B = client.chat.completions.create(model=model_name, messages=messages)
    B_utterance = extract_utterance(response_B.choices[0].message.content)

    # 组合 A 和 B 的对话
    script = f"A: {A_utterance}\nB: {B_utterance}"
    return script

def generate_followup_script(prev_script):
    """基于上一轮对话生成下一轮对话，并进行心理推理"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Previous conversation:\n{prev_script}\n\n{content_instruction_A}\n\n{content_instruction_B}"}
    ]
    response = client.chat.completions.create(model=model_name, messages=messages)
    return response.choices[0].message.content.strip()

def ask_information_test_question(script):
    """向模型询问与对话相关的问题，以测试信息掌握情况"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Based on the following conversation, answer the question (in Chinese) :\n{script}\n\n{test_question}"}
    ]
    response = client.chat.completions.create(model=model_name, messages=messages)
    return response.choices[0].message.content.strip()

# 运行对话模拟
script = f"Round 0:\n{generate_initial_script()}"  # 生成第一轮对话
all_script = script  # 记录包含推理的完整对话

for i in range(5):  # 进行 5 轮对话
    new_script = generate_followup_script(all_script)  # 用 all_script 保持完整性
    utterance_only = extract_utterance(new_script)
    script += f"\n\nRound {i + 1}:\n" + utterance_only
    all_script += f"\n\nRound {i + 1}:\n" + new_script  # 包含推理部分
    
    # 进行信息测试
    info_test_result = ask_information_test_question(all_script)
    with open('info_test_result.txt', 'a', encoding='utf-8') as file:
        file.write(f"Round {i + 1}:\n" + info_test_result + "\n")

# 保存最终的对话脚本
with open('script.txt', 'w', encoding='utf-8') as file:
    file.write(script)
with open('all_script.txt', 'w', encoding='utf-8') as file:
    file.write(all_script)
