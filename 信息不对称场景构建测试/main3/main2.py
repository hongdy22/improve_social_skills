from openai import OpenAI
import time
import json

# 设置 OpenAI API Key
client = OpenAI(base_url="http://115.182.62.174:18888/v1", api_key="zQTxB4T2yXBFeoBtE7418192Df3e476a84259d84D9015cC1")
# models = client.models.list()
# print([model.id for model in models.data])
# model_names = ["gpt-4o", "gpt-4-0613", "gpt-4-1106-preview", "gpt-3.5-turbo", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-1106", "gpt-4-vision-preview"]

# 定义角色类
class Role:
    def __init__(self, name, personality, secrets):
        self.name = name
        self.personality = personality
        self.secrets = secrets  # 多条秘密信息
        self.history = []       # 记录该角色的发言

# 场景描述和规则
scenario_description = """
三位投资人齐聚一场私密的房地产投资会议，目标是竞标一块市中心的核心地段。然而，每个人都掌握着不同的市场情报，同时也有自己的投资策略和隐藏意图。他们需要在谈判中获取对方的信息，以便做出更优的投资决策，同时隐藏自己的核心机密，避免被对方利用。
"""

rules = """
【对话规则】:
1. 会议进行7轮，每位高管轮流发言，顺序：张总，王总，李总。
2. 每次发言控制在70字以内，以符合商业谈判的风格，尽量符合自己的性格特点。
3. 所有人只能看到公开会议记录和自己的机密信息。
4. 他们需要谨慎表达立场，避免暴露太多，同时设法获取更多对方的信息。
"""

# 初始化角色
roles = [
    Role("张总", "房地产开发商，谨慎务实，擅长操控市场风向。", [
        "政府规划文件显示，该地块未来五年内将建设高铁站，地价暴涨。",
        "公司资金链吃紧，需要找合作伙伴，但不能让人知道自己缺钱。",
        "已经和市长接触，可能会有政策倾斜，但不确定能否最终落地。"
    ]),
    Role("王总", "私募基金经理，冷静精明，擅长资本运作和杠杆收购。", [
        "基金已经收购了周边多个地块，若能拿下该地块，可垄断整个片区。",
        "资金充裕，但想压低价格，因此必须让其他人觉得风险很大。",
        "掌握了一条未公开的政策信息：政府可能会调整容积率，导致未来开发限制增加。"
    ]),
    Role("李总", "国际投资机构代表，外向果敢，擅长宏观市场布局。", [
        "海外投资团队对该地块非常感兴趣，但对政策透明度有所疑虑。",
        "与某大型商业集团有合作关系，若拿下地块，商业综合体可立刻入驻。",
        "团队内部未达成共识，若价格过高，可能不得不放弃竞标。"
    ])
]

# 公共对话记录
conversation_history = []

def generate_prompt(role, conversation_history):
    """ 生成当前角色的 prompt """
    public_history = "\n".join(conversation_history) if conversation_history else "(无)"
    prompt = f"""【场景描述】
{scenario_description}

【对话规则】
{rules}

【你的身份】：{role.name}
【你的性格】：{role.personality}
【你的秘密情报】：
"""
    for idx, secret in enumerate(role.secrets, 1):
        prompt += f"   {idx}. {secret}\n"
    prompt += f"""

【当前公共对话记录】:
{public_history}

请生成你的发言，注意不要直接暴露秘密，同时符合并利用你的性格特点，尽可能获取到对方的信息。"""
    return prompt

def call_gpt_for_role(role, gpt_name):
    """ 调用大模型 API 生成当前角色的回复 """
    prompt = generate_prompt(role, conversation_history)
    messages = [
        {"role": "system", "content": "你是一个商务谈判模拟系统，请严格按照要求生成对话回复。"},
        {"role": "user", "content": prompt}
    ]
    try:
        response = client.chat.completions.create(
            model=gpt_name,
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        text = response.choices[0].message.content.strip()
    except Exception as e:
        # print(f"调用API出错: {e}, 正在重试...")
        return call_gpt_for_role(role, gpt_name)
    return text

def simulate_conversation(rounds=15, log_filename="main2_conversation_log.txt"):
    """ 逐轮模拟谈判 """
    global conversation_history
    with open(log_filename, "w", encoding="utf-8") as log_file:
        for rnd in range(1, rounds+1):
            round_header = f"=== 第 {rnd} 轮对话 ==="
            print(round_header)
            log_file.write(round_header + "\n")
            conversation_history.append(round_header)
            for role in roles:
                if role.name == "张总":
                    gpt_name = "gpt-4o"
                elif role.name == "王总":
                    gpt_name = "gpt-3.5-turbo-1106"
                elif role.name == "李总":
                    gpt_name = "gpt-3.5-turbo-1106"
                else:
                    print("未知角色........................................")
                    gpt_name = "gpt-4o"
                response_text = call_gpt_for_role(role, gpt_name)
                message = f"{role.name}: {response_text}"
                conversation_history.append(message)
                role.history.append(response_text)
                print(message)
                log_file.write(message + "\n")
                time.sleep(1)
            print("\n")
            log_file.write("\n")
    return conversation_history

def analyze_conversation():
    """ 调用大模型 API 分析谈判结果 """
    analysis_prompt = f"""请分析以下会议记录，
判断各高管在会议中获取了多少对方的机密信息（请严格从下面机密清单中提取），以及泄露了多少自己的机密信息。

【机密清单】
张总: {roles[0].secrets}
王总: {roles[1].secrets}
李总: {roles[2].secrets}

【对话记录】：
{"\n".join(conversation_history)}
"""
    messages = [
        {"role": "system", "content": "你是商务谈判分析师，请判断信息交换情况。"},
        {"role": "user", "content": analysis_prompt}
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.0,
            max_tokens=500
        )
        analysis_result = response.choices[0].message.content.strip()
    except Exception as e:
        analysis_result = f"调用分析API出错: {e}"
    return analysis_result

def save_analysis_result(result, filename="main2_analysis_results.txt"):
    """ 以文本格式保存分析结果 """
    try:
        result_json = json.loads(result)
        with open(filename, "w", encoding="utf-8") as f:
            for agent, data in result_json.items():
                f.write(f"{agent} - 泄露情报: {data['leaked']} | 获取情报: {data['obtained']}\n")
            f.write("\n")
    except json.JSONDecodeError:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("分析结果解析失败:\n" + result)
    print(f"分析结果已保存到 {filename}")

if __name__ == "__main__":
    print("开始模拟情报对话...\n")
    simulate_conversation(rounds=7)
    
    print("【对话结束】\n开始分析情报对话...\n")
    analysis_result = analyze_conversation()
    print("分析结果:")
    print(analysis_result)
    
    save_analysis_result(analysis_result)