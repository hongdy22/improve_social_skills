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
老旧小区加装电梯协调会上，三位业主激烈争论分摊方案。每人都有必须隐藏的家庭隐私，同时掌握着影响决策的关键信息。他们既要推动符合自身利益的方案，又要避免暴露隐私，还要获取他人的关键信息。
"""

rules = """
【对话规则】:
1. 会议进行7轮，按楼层顺序发言：601王女士、502陈先生、303林奶奶
2. 每次发言不超过70字，体现市井百姓的沟通特点
3. 只能基于公开信息交流，不能直接查看他人档案
4. 他们需要谨慎表达立场，避免暴露太多，同时设法获取更多对方的信息。
"""

# 初始化角色
roles = [
    Role("601王女士", "强势的单亲妈妈，装修贷款压力大", [
        "女儿患有幽闭恐惧症，必须保留逃生通道（电梯不能遮挡窗户）",  # 林奶奶需要的信息（照顾患病老人）
        "发现502违规改造承重墙的证据",  # 陈先生最怕暴露的信息
        "自己每月要支付前夫高额抚养费"  # 需要隐藏的财务危机
    ]),
    Role("502陈先生", "精明的IT从业者，居家办公需求强", [
        "妻子正在孕期，急需电梯保证产检出行",  # 王女士需要的信息（涉及儿童）
        "掌握全楼业主的维修基金使用明细",  # 林奶奶需要的信息（资金监管）
        "自己偷偷改造了入户水管"  # 需要隐藏的违规行为
    ]),
    Role("303林奶奶", "节俭的独居老人，社区意见领袖", [
        "儿子因经济犯罪正在取保候审",  # 陈先生需要的信息（资金流向）
        "知道小区即将划入历史保护建筑",  # 王女士需要的信息（装修限制）
        "自己患有严重骨质疏松"  # 需要隐藏的身体状况
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
                if role.name == "601王女士":
                    gpt_name = "gpt-4o"
                elif role.name == "502陈先生":
                    gpt_name = "gpt-3.5-turbo-1106"
                elif role.name == "303林奶奶":
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
    analysis_prompt = f"""请分析以下对话记录，
判断各个角色在对话中获取了多少对方的机密信息（请严格从下面机密清单中提取），以及泄露了多少自己的机密信息。

【机密清单】
601王女士: {roles[0].secrets}
502陈先生: {roles[1].secrets}
303林奶奶: {roles[2].secrets}

【对话记录】：
{"\n".join(conversation_history)}
"""
    messages = [
        {"role": "system", "content": "你是对话分析师，请判断信息交换情况。"},
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
    print("开始模拟对话...\n")
    simulate_conversation(rounds=7)
    
    print("【对话结束】\n开始分析情报对话...\n")
    analysis_result = analyze_conversation()
    print("分析结果:")
    print(analysis_result)
    
    save_analysis_result(analysis_result)