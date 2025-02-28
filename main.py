# TODO: 评价维度是否可以更全面
# TODO: background有点问题，会透露信息
# TODO: 自评和互评的评价标准还没改
# TODO: 信息提问是否要加
import json
from openai import OpenAI

# 初始化 OpenAI 客户端
client = OpenAI(base_url="http://115.182.62.174:18888/v1", api_key="zQTxB4T2yXBFeoBtE7418192Df3e476a84259d84D9015cC1")
model_name = "gpt-4o"

def extract_asymmetric_points(role_a, role_b, background):
    """提取10个关键不对称信息点（每方5个）"""
    prompt = f"""基于以下角色设定和背景，找出10个关键信息点（每方5个），这些信息点满足：
1. 信息点一定是真实的，而不是虚构的，只能在角色设定和背景中提取内容
2. 对对话进展有一定影响
3. 可能可以通过对话逐步揭示
4. 是某一方独有的信息（对方不知道）
5. 每个信息点不必太冗长，可以是性格、行为、目标等方面

【背景设定】
{background}

【角色A】
{role_a}

【角色B】
{role_b}

请按以下JSON格式返回：
{{
    "A_exclusive": ["信息点1", "信息点2", "信息点3", "信息点4", "信息点5"],
    "B_exclusive": ["信息点1", "信息点2", "信息点3", "信息点4", "信息点5"]
}}"""
    
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def check_consensus_progress(script, key_points):
    """检查对话中的共识进展"""
    prompt = f"""请分析对话内容，判断哪些关键信息点已被对方知晓：
【关键信息点】
A方独有：{key_points['A_exclusive']}
B方独有：{key_points['B_exclusive']}

【对话记录】
{script}

请返回JSON格式：
{{
    "A_discovered": [已发现的A方信息点索引列表],
    "B_discovered": [已发现的B方信息点索引列表]
}}
示例：如果B在第3轮发现A的第0个信息点，返回："B_discovered": [0]"""
    
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# 读取 JSON 配置
with open('setting.json', 'r', encoding='utf-8') as file:
    settings = json.load(file)

for j in range(0, len(settings)):  # 遍历 JSON 数组
    print(f"Setting {j + 1} is running...")

    # 选取第一个对话主题
    selected_theme = settings[j]  # 选择 JSON 数组的第一项

    # 提取 `role_A` 和 `role_B`
    content_role_A = f"Role A:\nCharacter: {selected_theme['role_A']['character']}\nBehavior: {selected_theme['role_A']['behavior']}\nGoal: {selected_theme['role_A']['goal']}"
    content_role_B = f"Role B:\nCharacter: {selected_theme['role_B']['character']}\nBehavior: {selected_theme['role_B']['behavior']}\nGoal: {selected_theme['role_B']['goal']}"

    # 读取 `setting`
    content_setting = selected_theme["background"]

    # 生成关键信息点
    key_points = extract_asymmetric_points(content_role_A, content_role_B, content_setting)
    
    # 保存关键信息点
    with open(f'consensus/{j+1}_setting_key_points.json', 'w') as f:
        json.dump(key_points, f, ensure_ascii=False, indent=2)
    
    # 初始化共识跟踪
    consensus = {
        "A_exclusive": [{"point": p, "discovered": False, "round": -1} for p in key_points['A_exclusive']],
        "B_exclusive": [{"point": p, "discovered": False, "round": -1} for p in key_points['B_exclusive']]
    }

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
    
    # 初始化共识跟踪文件
    with open(f'consensus/{j+1}_consensus_progress.json', 'w') as f:
        f.write("[]")

    for i in range(9):  # 进行 10 轮对话
        # 提示进度
        print(f"Round {i + 1} is running...")
        
        new_utterance = generate_followup_script(script)  # 交替生成
        script += f"\n\nRound {i + 1}:\n" + extract_utterance(new_utterance)  # 追加对话
        script_all += f"\n\nRound {i + 1}:\n" + new_utterance  # 追加完整对话
        
        # 检查共识进展
        progress = check_consensus_progress(script, key_points)
        
        # 在每轮对话后分析共识进展
        for idx in progress.get('A_discovered', []):
            if 0 <= idx < len(consensus["A_exclusive"]) and not consensus["A_exclusive"][idx]["discovered"]:
                consensus["A_exclusive"][idx].update({
                    "discovered": True,
                    "round": i+1
                })
        
        for idx in progress.get('B_discovered', []):
            if 0 <= idx < len(consensus["B_exclusive"]) and not consensus["B_exclusive"][idx]["discovered"]:
                consensus["B_exclusive"][idx].update({
                    "discovered": True,
                    "round": i+1
                })
        
        # 保存当前进展
        with open(f'consensus/{j+1}_consensus_progress.json', 'r+') as f:
            data = json.load(f)
            data.append({
            "setting": j+1,
            "round": i+1,
            "progress": {
                "A_discovered": [p["point"] for p in consensus["A_exclusive"] if p["discovered"]],
                "B_discovered": [p["point"] for p in consensus["B_exclusive"] if p["discovered"]]
            }
            })
            f.seek(0)
            # 设置 indent 参数为 4，使输出的 JSON 数据格式化，每个元素换行显示
            json.dump(data, f, ensure_ascii=False,indent=4)
            f.truncate()
        
        # 进行信息测试(感觉应该加在B发言之后)
        # test_question_ans = ask_information_test_question(script_all)
        # with open('test_question_ans.txt', 'a', encoding='utf-8') as file:
        #     file.write(f"Round {i + 1}:\n" + test_question_ans + "\n")
    
    # 保存最终共识结果
    matched_points = [
        {**p, "side": "A"} for p in consensus["A_exclusive"] if p["discovered"]
    ] + [
        {**p, "side": "B"} for p in consensus["B_exclusive"] if p["discovered"]
    ]
    total_points = len(matched_points)
    
    with open(f'consensus/{j+1}_setting_final_consensus.json', 'w') as f:
        json.dump({
            "total_points": total_points,
            "matched_points": matched_points
        }, f, ensure_ascii=False, indent=2)

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
    
    # 加载自评标准
    def load_self_evaluation():
        with open('score_criteria_self.txt', 'r', encoding='utf-8') as file:
            self_evaluation = file.read().strip()
        return self_evaluation
    
    # 加载互评标准
    def load_mutual_evaluation():
        with open('score_criteria_mutual.txt', 'r', encoding='utf-8') as file:
            mutual_evaluation = file.read().strip()
        return mutual_evaluation

    # 客观评价
    def evaluate_script(script):
        """评价对话脚本"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"background: {content_setting}\n{content_role_A}\n{content_role_B}\nConversation:\n{script}\n\n{load_criteria()}"}
        ]
        response = client.chat.completions.create(model=model_name, messages=messages)
        return response.choices[0].message.content.strip()
    
    ## TODO: 目前自评和互评只有B的评价，需要添加A的评价
    # 自评
    def self_evaluation(script):
        """自评"""
        messages = [
            {"role": "system", "content": "You are B, please provide a self-assessment based on the following information."},
            {"role": "user", "content": f"background: {content_setting}\n{content_role_B}\nConversation:\n{script}\n\n{load_self_evaluation()}"}
        ]
        response = client.chat.completions.create(model=model_name, messages=messages)
        return response.choices[0].message.content.strip()
    
    # 互评
    def mutual_evaluation(script):
        """互评"""
        messages = [
            {"role": "system", "content": "You are A, please provide a mutual-assessment based on the following information."},
            {"role": "user", "content": f"background: {content_setting}\n{content_role_A}\nConversation:\n{script}\n\n{load_mutual_evaluation()}"}
        ]
        response = client.chat.completions.create(model=model_name, messages=messages)
        return response.choices[0].message.content.strip()

    # 进行客观评价
    print(f"Evaluating the script...")
    evaluation = "Evaluating:\n" + evaluate_script(script)
    
    # # 进行自评
    # print(f"Self-evaluating the script...")
    # evaluation += "\n\nSelf-evaluating:\n" + self_evaluation(script)
    
    # # 进行互评
    # print(f"Mutual-evaluating the script...")
    # evaluation += "\n\nMutual-evaluating:\n" + mutual_evaluation(script)
    
    # 将评价结果写入文件 score_details.txt
    with open('score_details.txt', 'w', encoding='utf-8') as file:
        file.write(evaluation)

    # 将最终得分写入文件 score_summary.txt (提取“final_scores:”开头的行)
    with open('score_details.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        final_scores = [line for line in lines if line.lower().startswith("final_scores") or line.lower().startswith("final scores")]
    with open('score_summary.txt', 'a', encoding='utf-8') as file:
        for line in final_scores:
            file.write(line + "\n")
        file.write("\n")   
         
    print(f"Setting {j + 1} is finished.")
    print("")
print("All settings are finished.")