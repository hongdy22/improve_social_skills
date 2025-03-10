# TODO: 评价维度是否可以更全面
# TODO: background有点问题，会透露信息
# TODO: 信息提问是否要加
# TODO: 背景信息较少，提取不到10个信息点
# TODO: 输出放到json中会更加稳定
# NOTE: 并不是所有时候都需要保守自己的信息，所以测试的时候先仅统计获取的信息
# TODO: 信息不对称的点还是自己给，避免因为ai提取的信息点不合适而评分标准不一致
# TODO: 带推理的得分和不带推理的储存在两个文件中，然后提取，然后可以先取消自评和互评，然后画easy和difficlut两个图
# TODO: U235聊天记录里需要注意的
# TODO: 目前没有增加自评和互评
import json
from openai import OpenAI

# 初始化 OpenAI 客户端
client = OpenAI(base_url="http://115.182.62.174:18888/v1", api_key="zQTxB4T2yXBFeoBtE7418192Df3e476a84259d84D9015cC1")
model_name = "gpt-4o"

def check_consensus_progress(script, key_points):
    """检查对话中的共识进展：判断双方是否在对话中get到了对方在character, behavior, goal, information四个方面的信息"""
    prompt = f"""Please analyze the following conversation transcript and determine whether each party has acquired the other's information in the following four aspects: character, behavior, goal, and information.
    
[Requirements]
Please strictly base your judgment on the existing conversation. For any aspects that are not clearly indicated, please err on the side of caution (treat as not acquired).

[Information Points for Both Parties]
Party A's information:
- character: {key_points['A_exclusive'][0]['point']}
- behavior: {key_points['A_exclusive'][1]['point']}
- goal: {key_points['A_exclusive'][2]['point']}
- information: {key_points['A_exclusive'][3]['point']}

Party B's information:
- character: {key_points['B_exclusive'][0]['point']}
- behavior: {key_points['B_exclusive'][1]['point']}
- goal: {key_points['B_exclusive'][2]['point']}
- information: {key_points['B_exclusive'][3]['point']}

[Conversation Transcript]
{script}

Please return the result in JSON format as follows:
{{
    "B_discovered": [list the field names of Party A's information that Party B has acquired, e.g., "character", "goal"],
    "A_discovered": [list the field names of Party B's information that Party A has acquired]
}}

Note: Base your judgment solely on the hints and expressions in the conversation; do not add any extra information."""
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# 读取 JSON 配置
with open('setting.json', 'r', encoding='utf-8') as file:
    settings = json.load(file)

for j in range(15, len(settings)):  # 遍历 JSON 数组
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

    # 直接构造双方的关键信息点（各自4个信息点）
    key_points = {
        "A_exclusive": [
            {"field": "character", "point": selected_theme['role_A']['character']},
            {"field": "behavior", "point": selected_theme['role_A']['behavior']},
            {"field": "goal", "point": selected_theme['role_A']['goal']},
            {"field": "information", "point": selected_theme['role_A']['information']}
        ],
        "B_exclusive": [
            {"field": "character", "point": selected_theme['role_B']['character']},
            {"field": "behavior", "point": selected_theme['role_B']['behavior']},
            {"field": "goal", "point": selected_theme['role_B']['goal']},
            {"field": "information", "point": selected_theme['role_B']['information']}
        ]
    }
    
    # 保存关键信息点
    with open(f'Y_consensus/{j+1}_setting_key_points.json', 'w') as f:
        json.dump(key_points, f, ensure_ascii=False, indent=2)
    
    # 初始化共识跟踪（对每个信息点增加 discovered 标记）
    consensus = {
        "A_exclusive": [
            {"field": p["field"], "point": p["point"], "discovered": False, "round": -1} 
            for p in key_points["A_exclusive"]
        ],
        "B_exclusive": [
            {"field": p["field"], "point": p["point"], "discovered": False, "round": -1} 
            for p in key_points["B_exclusive"]
        ]
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
    for file_name in [f'Y_scripts/{j+1}_script.txt', f'Y_scripts/{j+1}_script_all.txt', 'test_question_ans.txt']:
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
    with open(f'Y_consensus/{j+1}_consensus_progress.json', 'w') as f:
        f.write("[]")

    for i in range(9):  # 进行 10 轮对话
        # 提示进度
        print(f"Round {i + 1} is running...")
        
        new_utterance = generate_followup_script(script)  # 交替生成
        script += f"\n\nRound {i + 1}:\n" + extract_utterance(new_utterance)  # 追加对话
        script_all += f"\n\nRound {i + 1}:\n" + new_utterance  # 追加完整对话
        
        # 检查共识进展
        progress = check_consensus_progress(script, key_points)
        
        # 更新共识进度：B_discovered 表示B获取了A的某个信息点；A_discovered 表示A获取了B的某个信息点
        for field in progress.get('B_discovered', []):
            for item in consensus["A_exclusive"]:
                if item["field"] == field and not item["discovered"]:
                    item["discovered"] = True
                    item["round"] = i + 1
        for field in progress.get('A_discovered', []):
            for item in consensus["B_exclusive"]:
                if item["field"] == field and not item["discovered"]:
                    item["discovered"] = True
                    item["round"] = i + 1
        
        # 保存当前进展到文件
        with open(f'Y_consensus/{j+1}_consensus_progress.json', 'r+', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
            data.append({
                "setting": j + 1,
                "round": i + 1,
                "progress": {
                    "B_discovered": [p["field"] for p in consensus["A_exclusive"] if p["discovered"]],
                    "A_discovered": [p["field"] for p in consensus["B_exclusive"] if p["discovered"]]
                }
            })
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
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
    
    with open(f'Y_consensus/{j+1}_setting_final_consensus.json', 'w') as f:
        json.dump({
            "total_points": total_points,
            "matched_points": matched_points
        }, f, ensure_ascii=False, indent=2)

    # 保存最终的对话脚本
    with open(f'Y_scripts/{j+1}_script.txt', 'w', encoding='utf-8') as file:
        file.write(script)
    with open(f'Y_scripts/{j+1}_script_all.txt', 'w', encoding='utf-8') as file:
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
    with open(f'Y_scores/{j+1}_score_details.txt', 'w', encoding='utf-8') as file:
        file.write(evaluation)

    # 将最终得分写入文件 score_summary.txt (提取“final_scores:”开头的行)
    with open(f'Y_scores/{j+1}_score_details.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        final_scores = [line for line in lines if line.lower().startswith("final_scores") or line.lower().startswith("final scores") or line.lower().startswith("**final scores") or line.lower().startswith("**final_scores")]
    with open(f'Y_scores/a_score_summary.txt', 'a', encoding='utf-8') as file:
        for line in final_scores:
            file.write(line + "\n")
        file.write("\n")   
         
    print(f"Setting {j + 1} is finished.\n")
print("All settings are finished.")