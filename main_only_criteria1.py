## 本文件用于对比评价带/不带推理生成的对话质量forA
## 版本1：直接根据整段对话，给出获取了多少信息不对称的点
import json
from openai import OpenAI

# 修改这里可以设置需要运行的 setting 数量
setting_num = 10

# 初始化 OpenAI 客户端
client = OpenAI(base_url="http://115.182.62.174:18888/v1", api_key="sk-AP87QFGmx6FLSXmw326a6b7aBf254f468011Ef9c293c21Fc")
model_name = "gpt-4o"

response = client.chat.completions.create(
    model=model_name,
    messages=[{"role": "user", "content": "Hello!"}]
)
input_tokens = response.usage.prompt_tokens
output_tokens = response.usage.completion_tokens

# 将输入和输出的 tokens 保存到文件中
with open("tokens.json", "a") as f:
    json.dump({"input_tokens": input_tokens, "output_tokens": output_tokens}, f)
    f.write("\n")
    
for i in range(0, setting_num):
    print(f"正在处理第 {i+1} 个对话主题...")
    # 读取文件Y_scripts/{i+1}_script.txt中的文本
    with open(f"Y_scripts/{i+1}_script.txt", "r") as f:
        y_script = f.read()
        
    # 读取文件X_scripts/{i+1}_script.txt中的文本
    with open(f"N_scripts/{i+1}_script.txt", "r") as f:
        n_script = f.read()
        
    # 读取 JSON 配置
    with open('setting.json', 'r', encoding='utf-8') as file:
        settings = json.load(file)
        
    # 选取第一个对话主题
    selected_theme = settings[i]  # 选择 JSON 数组的第一项

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
    
    # 读取评价维度
    with open('score_criteria_forA.txt', 'r', encoding='utf-8') as file:
        criteria = file.read().strip()
        
    # 调用api，让AI根据评价维度（有七个评价维度），基于背景信息和双方角色设定，给出y_script和n_script各个维度的评分，以json格式返回
    prompt = (
        f"请根据以下背景信息、角色设定和评价维度，对两个对话中role A的表现进行评分，评分范围均为 0 到 10 分，"
        f"要求分别对 y_script 和 n_script 中A的表现，从各个维度进行评分，并以 JSON 格式返回结果。\n\n"
        f"背景信息:\n{content_setting}\n\n"
        f"{content_role_A}\n\n{content_role_B}\n\n"
        f"评价维度:\n{criteria}\n\n"
        f"对话1 (y_script):\n{y_script}\n\n"
        f"对话2 (n_script):\n{n_script}\n\n"
        f"请严格用两行返回结果：\n"
        f"y_script: *points, *points, *points, *points, *points, *points, *points\n"
        f"n_script: *points, *points, *points, *points, *points, *points, *points\n"
        f"where '' is replaced with the actual scores."
    )
    
    evaluation_response = client.chat.completions.create(
         model=model_name,
         messages=[{"role": "user", "content": prompt}]
    )
    
    # 获取 AI 返回的评分结果
    evaluation_result = evaluation_response.choices[0].message.content
    with open(f"only_criteria/{i+1}.txt", "w") as f:
        f.write(evaluation_result)
    
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
    
    #  For any aspects that are not clearly indicated, please err on the side of caution (treat as not acquired).
    def check_consensus_progress(y_script, n_script, key_points):
        """检查对话中的共识进展：判断双方是否在对话中get到了对方在character, behavior, goal, information四个方面的信息"""
        prompt = f"""Please analyze the following two conversation transcripts and determine whether each party has acquired the other's information in the following four aspects: character, behavior, goal, and information.
        
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

    [Conversation Transcript 1]
    {y_script}

    [Conversation Transcript 2]
    {n_script}

    Please return the result in JSON format as follows:
    {{
        "y_script": {{
            "B_discovered": [list the field names of Party A's information that Party B has acquired, e.g., "character", "goal"],
            "A_discovered": [list the field names of Party B's information that Party A has acquired]
        }},
        "n_script": {{
            "B_discovered": [list the field names of Party A's information that Party B has acquired, e.g., "character", "goal"],
            "A_discovered": [list the field names of Party B's information that Party A has acquired]
        }}
    }}

    Note: Base your judgment solely on the hints and expressions in the conversation; do not add any extra information."""
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    
    # 检查 y_script 和 n_script 的共识进展
    progress = check_consensus_progress(y_script, n_script, key_points)
    
    # 将结果保存到文件中
    with open(f"consensus_progress/{i+1}.txt", "w") as f:
        f.write(f"y_script: {progress['y_script']}\n")
        f.write(f"n_script: {progress['n_script']}\n")
        
    # info_prompt = (
    #     f"八个关键信息点：\n"
    #     f"1. Role A - Character: {selected_theme['role_A']['character']}\n"
    #     f"2. Role A - Behavior: {selected_theme['role_A']['behavior']}\n"
    #     f"3. Role A - Goal: {selected_theme['role_A']['goal']}\n"
    #     f"4. Role A - Information: {selected_theme['role_A']['information']}\n"
    #     f"5. Role B - Character: {selected_theme['role_B']['character']}\n"
    #     f"6. Role B - Behavior: {selected_theme['role_B']['behavior']}\n"
    #     f"7. Role B - Goal: {selected_theme['role_B']['goal']}\n"
    #     f"8. Role B - Information: {selected_theme['role_B']['information']}\n\n"
    #     f"下面有两个对话，每个对话有10个回合，请分别分析每个对话中每回合关键信息点的传递情况：\n"
    #     f"例如通过第一轮对话之后，B得到了Role A - Behavior信息，那么总分+1分，若A得到了Role B - Character和Role B - Goal，那么总分+2分\n"
    #     f"那么第一轮的总分就是3分，以此类推，分析10个回合的，理论上得到的信息数（总分）应该是非降的\n"
    #     f"请你最后一行以这样的形式总结出结果'y_script: *points,*points,*points,*points,*points,*points,*points,*points,*points,*points;n_script: *points,*points,*points,*points,*points,*points,*points,*points,*points,*points,'\n"
    #     f"10个points分别对应10轮每一轮的得分，请严格按照获取到的关键信息点的数量给分\n"
    # )

    # info_response = client.chat.completions.create(
    #      model=model_name,
    #      messages=[{"role": "user", "content": info_prompt}]
    # )
    
    # # 获取 AI 返回的关键信息分析结果，并保存到文件中
    # info_result = info_response.choices[0].message.content
    # with open(f"information_asymmetry/{i+1}.txt", "w", encoding="utf-8") as f:
    #      f.write(info_result)
    