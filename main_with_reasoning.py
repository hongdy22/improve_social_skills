### 简洁版（带推理），仅生成对话
import json
from openai import OpenAI

# 修改这里可以设置需要运行的 setting 数量
setting_num = 30
setting_json_file = 'setting_easy.json'
save_file_prefix = 'Y_E_scripts/'

# 初始化 OpenAI 客户端
client = OpenAI(base_url="http://115.182.62.174:18888/v1", api_key="zQTxB4T2yXBFeoBtE7418192Df3e476a84259d84D9015cC1")
model_name = "gpt-4o"

def save_used_token_count(response):
    """"保存输入和输出的 token 数量"""
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens

    with open('token_count.txt', 'a', encoding='utf-8') as file:
        file.write(f"Input tokens: {input_tokens}, Output tokens: {output_tokens}, Total tokens: {total_tokens}\n")

# 读取 JSON 配置
with open(f"{setting_json_file}", 'r', encoding='utf-8') as file:
    settings = json.load(file)

for j in range(23, setting_num):  # 遍历 JSON 数组
    print(f"Setting {j + 1} is running...")

    # 选取第一个对话主题
    selected_theme = settings[j]  # 选择 JSON 数组的第一项

    # 提取 role_A 和 role_B（修正 role_B 的信息读取）
    content_role_A = (
        f"Role A:\n"
        f"Character: {selected_theme['role_A']['character']}\n"
        f"Behavior: {selected_theme['role_A']['behavior']}\n"
        f"Goal: {selected_theme['role_A']['goal']}\n"
        f"Information: {selected_theme['role_A']['information']}"
    )
    content_role_B = (
        f"Role B:\n"
        f"Character: {selected_theme['role_B']['character']}\n"
        f"Behavior: {selected_theme['role_B']['behavior']}\n"
        f"Goal: {selected_theme['role_B']['goal']}\n"
        f"Information: {selected_theme['role_B']['information']}"
    )
    
    # 读取 `setting`
    content_setting = selected_theme["background"]

    # 读取 `instruction_A` 和 `instruction_B`
    with open('instruction_A.txt', 'r', encoding='utf-8') as file:
        content_instruction_A = file.read().strip()
    with open('instruction_B_without_reasoning.txt', 'r', encoding='utf-8') as file:
        content_instruction_B = file.read().strip()
        
    # 清空 script.txt 和 script_all.txt 和 info_test_result.txt
    for file_name in [f'{save_file_prefix}{j+1}_script.txt', f'{save_file_prefix}{j+1}_script_all.txt']:
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
        save_used_token_count(response_A)

        # `B` 分析 `A` 的第一句并生成回应
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Setting: {content_setting}\n{content_role_B}\n{content_instruction_B}\nA's first utterance: {A_utterance}\nB, based on your role and the background, and strictly following the steps and format of instruction_B, generate your response.\n(Additional requirements: Only one line in the answer starts with 'B:',Do not make any bold modifications either.)"}
        ]
        response_B = client.chat.completions.create(model=model_name, messages=messages)
        B_utterance = response_B.choices[0].message.content
        save_used_token_count(response_B)

        # 组合 A 和 B 的对话
        script = f"all scripts A: \n{A_utterance}\n\nall scripts B: \n{B_utterance}"
        return script

    def generate_followup_script(prev_script, round_num):
        """基于上一轮对话生成下一轮对话，并进行心理推理"""
        messages_A = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Setting: {content_setting}\n{content_role_A}\n{content_instruction_A}\nPrevious conversation:\n{prev_script}\nA, based on your role and the background and previous conversation, and strictly following the steps and format of instruction_A, generate your response.\n(Additional requirements: Only one line in the answer starts with 'A:',Do not make any bold modifications either.)"}
        ]
        response_A = client.chat.completions.create(model=model_name, messages=messages_A)
        A_utterance = response_A.choices[0].message.content.strip()
        save_used_token_count(response_A)
        
        prev_script += f"\n\nRound {round_num}:\n" + extract_utterance(A_utterance)  # 追加对话
        messages_B = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Setting: {content_setting}\n{content_role_B}\n{content_instruction_B}\nPrevious conversation:\n{prev_script}\nB, based on your role and the background and previous conversation, and strictly following the steps and format of instruction_B, generate your response.\n(Additional requirements: Only one line in the answer starts with 'B:',Do not make any bold modifications either.)"}
        ]
        response_B = client.chat.completions.create(model=model_name, messages=messages_B)
        B_utterance = response_B.choices[0].message.content.strip()
        save_used_token_count(response_B)
        
        new_script = f"all scripts of A: \n{A_utterance}\n\nall scripts of B: \n{B_utterance}"
        return new_script

    # 运行对话模拟
    script_all = f"Round 0:\n{generate_initial_script()}"  # 生成第一轮对话
    script = f"Round 0:\n" + extract_utterance(script_all)

    for i in range(9):  # 进行 10 轮对话
        # 提示进度
        print(f"Round {i + 1} is running...")
        
        new_utterance = generate_followup_script(script, i+1)  # 交替生成
        script += f"\n\nRound {i + 1}:\n" + extract_utterance(new_utterance)  # 追加对话
        script_all += f"\n\nRound {i + 1}:\n" + new_utterance  # 追加完整对话

    # 保存最终的对话脚本
    with open(f'{save_file_prefix}{j+1}_script.txt', 'w', encoding='utf-8') as file:
        file.write(script)
    with open(f'{save_file_prefix}{j+1}_script_all.txt', 'w', encoding='utf-8') as file:
        file.write(script_all)
         
    print(f"Setting {j + 1} is finished.\n")
print("All settings are finished.")