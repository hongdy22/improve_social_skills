from openai import OpenAI
import time
import json

# 设置 OpenAI API Key
client = OpenAI(base_url="http://115.182.62.174:18888/v1", api_key="zQTxB4T2yXBFeoBtE7418192Df3e476a84259d84D9015cC1")

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
这是一次紧急召开的情报会议，地点位于一处秘密安全屋内。
三名特工分别代表不同的情报部门，他们在过去的任务中相互交错，
有时合作，有时对抗。每个人掌握着关键情报，但也各怀心思，
既要套取对方的信息，又要保护自己的秘密。

最近，一项涉及国家安全的重要任务出现了变故——
原定的目标突然失踪，而恐怖分子可能已获取绝密情报。
三名特工被命令在最短时间内，拼凑出当前局势的完整拼图，
但他们的上级并未透露全部信息，甚至可能故意隐瞒部分情报……

在这场博弈中，谁能真正掌控局势？谁又会成为情报战的牺牲品？
"""

rules = """
【对话规则】:
1. 对话共10轮，顺序：Agent A、Agent B、Agent C。
2. 每位特工只能看到公共对话记录和自己的秘密。
3. 必须谨慎发言，避免泄露自身情报，同时探查对方秘密。
4. 每次发言尽量不超过200字（一小段话），尽量符合自己的性格特点。
"""

# 初始化角色
roles = [
    Role("Agent A", "谨慎且理性，前军情六处高级分析员，因叛徒事件失去信任感", [
        "情报1：旧仓库内发现可疑炸药残留，但未发现目标。",
        "情报2：‘红玫瑰’是某高级官员的代号，而非简单的口令。",
        "情报3：目标的最后通话记录指向‘东区’，但信号可能被伪造。"
    ]),
    Role("Agent B", "冷静、计算精准，前黑客，专注于解密情报，但过度自信", [
        "情报1：暗号‘Eagle’用于某地下组织，但实际身份未知。",
        "情报2：北区的监控录像显示可疑身影，但无法确认是否为目标。",
        "情报3：编号12的情报员曾泄露机密，可能在误导我们。"
    ]),
    Role("Agent C", "冲动且富有冒险精神，初入情报界，渴望证明自己", [
        "情报1：监听中发现‘计划改变’，但具体内容被加密。",
        "情报2：备用武器已调动，但目标并未出现，可能是陷阱。",
        "情报3：一名‘内部联络人’提供的指令不符合标准协议，可能受胁迫。"
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
        {"role": "system", "content": "你是一个模拟多角色情报对话的系统，请严格按照要求生成对话回复。"},
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
        text = f"调用API出错: {e}"
    return text

def simulate_conversation(rounds=15, log_filename="main2_conversation_log.txt"):
    """ 逐轮模拟对话 """
    global conversation_history
    with open(log_filename, "w", encoding="utf-8") as log_file:
        for rnd in range(1, rounds+1):
            round_header = f"=== 第 {rnd} 轮对话 ==="
            print(round_header)
            log_file.write(round_header + "\n")
            conversation_history.append(round_header)
            for role in roles:
                if role.name == "Agent A":
                    gpt_name = "gpt-4o"
                elif role.name == "Agent B":
                    gpt_name = "gpt-4o"
                elif role.name == "Agent C":
                    gpt_name = "gpt-4o-mini"
                else:
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
    """ 调用大模型 API 分析情报获取与泄露情况 """
    analysis_prompt = f"""请分析下面的情报对话记录，
判断每个特工在对话中获取了多少其他特工的秘密情报（请严格按照从下面秘密清单中提取），以及泄露了多少自己的秘密。

【秘密情报清单】
Agent A: {roles[0].secrets}
Agent B: {roles[1].secrets}
Agent C: {roles[2].secrets}

【对话记录】：
{"\n".join(conversation_history)}
"""
    messages = [
        {"role": "system", "content": "你是情报分析专家，请根据提供的信息判断情报获取与泄露情况。"},
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
            f.write("\n总结: 本次模拟显示，各特工在信息交换中的表现各有不同，展现出不同的策略倾向。")
    except json.JSONDecodeError:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("分析结果解析失败:\n" + result)
    print(f"分析结果已保存到 {filename}")

if __name__ == "__main__":
    print("开始模拟情报对话...\n")
    simulate_conversation(rounds=10)
    
    print("【对话结束】\n开始分析情报对话...\n")
    analysis_result = analyze_conversation()
    print("分析结果:")
    print(analysis_result)
    
    save_analysis_result(analysis_result)