## 本文件用于对比评价带/不带推理生成的对话质量forA
## 版本2：A每次发言之前，都说一下根据之前的对话，自己知道了什么信息（Character, Behavior, Goal, Information四个维度）
## 然后根据9次这样的信息（10轮对话），来对应设定好的信息不对称的点来判断匹配程度
## update：改为deepseek api，计算余弦相似度
import json
from openai import OpenAI

# 修改这里可以设置需要运行的 setting 数量
setting_num = 10

# 初始化 OpenAI 客户端
# deepseek：sk-247d2d6df8224009a12e2b11f2c080b1
client = OpenAI(api_key="sk-247d2d6df8224009a12e2b11f2c080b1", base_url="https://api.deepseek.com")
# client = OpenAI(base_url="http://115.182.62.174:18888/v1", api_key="zQTxB4T2yXBFeoBtE7418192Df3e476a84259d84D9015cC1")
# client = OpenAI(base_url="http://115.182.62.174:18888/v1", api_key="sk-AP87QFGmx6FLSXmw326a6b7aBf254f468011Ef9c293c21Fc")
# model_name = "gpt-4o"
model_name = "deepseek-chat"

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
    # 读取文件Y_scripts/{i+1}_script.txt中的文本，截取到"Round 6:"这一行之前
    with open(f"Y_scripts/{i+1}_script.txt", "r") as f:
        y_script = ""
        for line in f:
            if "Round 11:" in line:
                break
            y_script += line
        
    # 读取文件X_scripts/{i+1}_script.txt中的文本，截取到"Round 6:"这一行之前
    with open(f"N_scripts/{i+1}_script.txt", "r") as f:
        n_script = ""
        for line in f:
            if "Round 11:" in line:
                break
            n_script += line
        
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
    
    # # 读取评价维度
    # with open('score_criteria_forA.txt', 'r', encoding='utf-8') as file:
    #     criteria = file.read().strip()
        
    # # 调用api，让AI根据评价维度（有七个评价维度），基于背景信息和双方角色设定，给出y_script和n_script各个维度的评分，以json格式返回
    # prompt = (
    #     f"Please evaluate Role A's performance in the two dialogues based on the following background information, role settings, and evaluation criteria. "
    #     f"The scoring range is from 0 to 10 points. Provide scores for Role A's performance in y_script and n_script separately, "
    #     f"across each evaluation dimension, and return the results in JSON format.\n\n"
    #     f"Background Information:\n{content_setting}\n\n"
    #     f"{content_role_A}\n\n{content_role_B}\n\n"
    #     f"Evaluation Criteria:\n{criteria}\n\n"
    #     f"Dialogue 1 (y_script):\n{y_script}\n\n"
    #     f"Dialogue 2 (n_script):\n{n_script}\n\n"
    #     f"Please strictly return the results in two lines:\n"
    #     f"y_script: *points, *points, *points, *points, *points, *points, *points\n"
    #     f"n_script: *points, *points, *points, *points, *points, *points, *points\n"
    #     f"where '' is replaced with the actual scores."
    # )
    
    # evaluation_response = client.chat.completions.create(
    #      model=model_name,
    #      messages=[{"role": "user", "content": prompt}]
    # )
    
    # # 获取 AI 返回的评分结果
    # evaluation_result = evaluation_response.choices[0].message.content
    # with open(f"only_criteria/{i+1}.txt", "w") as f:
    #     f.write(evaluation_result)
    
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
    
    # 根据前面的对话，让role A输出自己已经获取到的信息，包括Character, Behavior, Goal, Information四个维度
    # 每个对话有10轮，从第二轮开始，每轮开始前，role A都会输出自己已经获取到的信息
    # 因此，需要给A提供A的初始设定，以及前n轮对话的内容，让A根据前n轮对话，输出自己已经获取到的信息
    def check_role_A_info(y_script, n_script):
        prompt = f"""You are Role A. Based on the previous dialogue content (there are two dialogues: Dialogue Record 1 and Dialogue Record 2, which are completely independent and need to be judged separately), from your perspective, output the information you have obtained, including four dimensions: Character, Behavior, Goal, and Information.
        
        [Requirements]
        Strictly base your judgment on the existing dialogue content. For any information that cannot be clearly inferred, handle it cautiously.
        
        [background information]
        {content_setting}

        [Role A's character settings]
        Role A's character settings: {content_role_A}

        [Dialogue Record 1(marked as y_script)]
        {y_script}

        [Dialogue Record 2(marked as n_script)]
        {n_script}

        Please return the result in JSON format as follows (y_script represents Dialogue Record 1, n_script represents Dialogue Record 2):
        {{
            "y_script": {{
            "B's Character": "Summarize the Character information of Role B inferred from the dialogue in one sentence.",
            "B's Behavior": "Summarize the Behavior information of Role B inferred from the dialogue in one sentence.",
            "B's Goal": "Summarize the Goal information of Role B inferred from the dialogue in one sentence.",
            "B's Information": "Summarize the Information of Role B inferred from the dialogue in one sentence."
            }},
            "n_script": {{
            "B's Character": "Summarize the Character information of Role B inferred from the dialogue in one sentence.",
            "B's Behavior": "Summarize the Behavior information of Role B inferred from the dialogue in one sentence.",
            "B's Goal": "Summarize the Goal information of Role B inferred from the dialogue in one sentence.",
            "B's Information": "Summarize the Information of Role B inferred from the dialogue in one sentence."
            }}
        }}

        Note: Strictly base your judgment on the hints and expressions in the dialogue. Do not add any extra information."""
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    
    # 保存 role A 的信息获取情况
    role_A_info = check_role_A_info(y_script, n_script)
    with open(f"consensus_progress/{i+1}.txt", "w") as f:
        f.write(f"y_script: {role_A_info['y_script']}\n")
        f.write(f"n_script: {role_A_info['n_script']}\n")
    
    
    #  根据A的信息获取情况，和B真实的角色设定，来判断匹配程度，从而进行打分
    # def check_consensus_progress(role_A_info, selected_theme):
    #     prompt = f"""Please evaluate the degree of information matching between the information inferred by Role A about Role B and the actual information of Role B.
    
    # [Requirements]
    # Strictly follow the scoring criteria for evaluation. Do not add any extra information.
    # Note that Role A has two separate inferences, which need to be evaluated independently.
    
    # [background information]
    # {content_setting}

    # [Scoring Criteria]
    # - character matching degree:
    #     0 points: Completely unmatched, A's inference is entirely unrelated to B's actual character setting.
    #     1 point: Partially matched, A's inference has some relevant information about B's actual character setting, but most are inaccurate.
    #     2 points: Mostly matched, A's inference is generally consistent with B's actual character setting, with minor deviations.
    #     3 points: Fully matched, A's inference is entirely consistent with B's actual character setting.

    # - behavior matching degree:
    #     0 points: Completely unmatched, A's inference is entirely unrelated to B's actual behavior setting.
    #     1 point: Partially matched, A's inference has some relevant information about B's actual behavior setting, but most are inaccurate.
    #     2 points: Mostly matched, A's inference is generally consistent with B's actual behavior setting, with minor deviations.
    #     3 points: Fully matched, A's inference is entirely consistent with B's actual behavior setting.

    # - goal matching degree:
    #     0 points: Completely unmatched, A's inference is entirely unrelated to B's actual goal setting.
    #     1 point: Partially matched, A's inference has some relevant information about B's actual goal setting, but most are inaccurate.
    #     2 points: Mostly matched, A's inference is generally consistent with B's actual goal setting, with minor deviations.
    #     3 points: Fully matched, A's inference is entirely consistent with B's actual goal setting.

    # - information matching degree:
    #     0 points: Completely unmatched, A's inference is entirely unrelated to B's actual information.
    #     1 point: Partially matched, A's inference has some relevant information about B's actual information, but most are inaccurate.
    #     2 points: Mostly matched, A's inference is generally consistent with B's actual information, with minor deviations.
    #     3 points: Fully matched, A's inference is entirely consistent with B's actual information.
    
    # [A's inferred information about B (First inference, referred to as A1)]
    # A1's inferred Character information about B: {role_A_info['y_script']['B\'s Character']}
    # A1's inferred Behavior information about B: {role_A_info['y_script']['B\'s Behavior']}
    # A1's inferred Goal information about B: {role_A_info['y_script']['B\'s Goal']}
    # A1's inferred Information about B: {role_A_info['y_script']['B\'s Information']}
    
    # [A's inferred information about B (Second inference, referred to as A2)]
    # A2's inferred Character information about B: {role_A_info['n_script']['B\'s Character']}
    # A2's inferred Behavior information about B: {role_A_info['n_script']['B\'s Behavior']}
    # A2's inferred Goal information about B: {role_A_info['n_script']['B\'s Goal']}
    # A2's inferred Information about B: {role_A_info['n_script']['B\'s Information']}    
    
    # [B's actual information (i.e., B's actual role settings)]
    # B's information:
    # - character: {selected_theme['role_B']['character']}
    # - behavior: {selected_theme['role_B']['behavior']}
    # - goal: {selected_theme['role_B']['goal']}
    # - information: {selected_theme['role_B']['information']}

    # Please return the result in JSON format as follows:
    # {{
    #     "A1": {{
    #         "character matching degree": [0-3 points],
    #         "behavior matching degree": [0-3 points],
    #         "goal matching degree": [0-3 points],
    #         "information matching degree": [0-3 points]
    #     }},
    #     "A2": {{
    #         "character matching degree": [0-3 points],
    #         "behavior matching degree": [0-3 points],
    #         "goal matching degree": [0-3 points],
    #         "information matching degree": [0-3 points]
    #     }}
    # }}

    # Note: Base your judgment solely on the existing information; do not add any extra information."""
    #     response = client.chat.completions.create(
    #         model=model_name,
    #         messages=[{"role": "user", "content": prompt}],
    #         response_format={"type": "json_object"}
    #     )
    #     return json.loads(response.choices[0].message.content)
    
    def check_consensus_progress(role_A_info, selected_theme):
        prompt = f"""请基于以下信息，对两段独立对话中 Role A 对 Role B 信息不对称点的捕捉能力进行对比评价。

    [要求]
    1. 两个对话分别独立评估：
    - 对 Dialogue Record 1（y_script），请基于 A 提取的信息，对 Role B 在 Character、Behavior、Goal、Information 四个维度的关键信息进行模糊匹配，返回 0 到 1 的分数，其中：
        - 0 表示完全没有捕捉到信息不对称点，
        - 1 表示完全捕捉到了。
    - 对 Dialogue Record 2（n_script），同样给出上述各维度的模糊匹配分数（0～1）。
    2. 请分别汇总每段对话中四个维度的得分（计算平均值作为总得分）。

    [背景信息]
    {content_setting}

    [Role B 实际设定]
    - Character: {selected_theme['role_B']['character']}
    - Behavior: {selected_theme['role_B']['behavior']}
    - Goal: {selected_theme['role_B']['goal']}
    - Information: {selected_theme['role_B']['information']}

    [A 对 B 的推理信息]
    【Dialogue Record 1 (y_script)】
    - A 对 B 的 Character 推理：{role_A_info['y_script']["B's Character"]}
    - A 对 B 的 Behavior 推理：{role_A_info['y_script']["B's Behavior"]}
    - A 对 B 的 Goal 推理：{role_A_info['y_script']["B's Goal"]}
    - A 对 B 的 Information 推理：{role_A_info['y_script']["B's Information"]}

    【Dialogue Record 2 (n_script)】
    - A 对 B 的 Character 推理：{role_A_info['n_script']["B's Character"]}
    - A 对 B 的 Behavior 推理：{role_A_info['n_script']["B's Behavior"]}
    - A 对 B 的 Goal 推理：{role_A_info['n_script']["B's Goal"]}
    - A 对 B 的 Information 推理：{role_A_info['n_script']["B's Information"]}

    [评分要求]
    请对每个对话分别给出：
    - 对于每个维度（Character、Behavior、Goal、Information）的模糊匹配分数（范围 0~1）。
    - 计算该对话的总得分（四个维度分数的平均值）。

    请严格按照如下 JSON 格式返回结果，不要包含其他额外信息：
    {{
        "y_script": {{
            "character score": <0~1 的数值>,
            "behavior score": <0~1 的数值>,
            "goal score": <0~1 的数值>,
            "information score": <0~1 的数值>,
            "total score": <0~1 的数值>
        }},
        "n_script": {{
            "character score": <0~1 的数值>,
            "behavior score": <0~1 的数值>,
            "goal score": <0~1 的数值>,
            "information score": <0~1 的数值>,
            "total score": <0~1 的数值>
        }}
    }}

    请严格根据以上要求和提供的信息返回结果，不要添加额外解释。"""
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    
    # 检查 y_script 和 n_script 的共识进展
    progress = check_consensus_progress(role_A_info, selected_theme)
    
    # 将结果保存到文件中
    with open(f"consensus_progress/{i+1}.txt", "a") as f:
        f.write(f"\n\n\n")
        f.write(f"y_script: {progress['y_script']}\n")
        f.write(f"n_script: {progress['n_script']}\n")
        f.write("\n")

    