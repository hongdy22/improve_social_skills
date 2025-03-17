## 本文件用于对比评价带/不带推理生成的对话质量
import json
from openai import OpenAI

# 修改这里可以设置需要运行的 setting 数量
setting_num = 2

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
    with open('score_criteria.txt', 'r', encoding='utf-8') as file:
        criteria = file.read().strip()
        
    # 调用api，让AI根据评价维度（有七个评价维度），基于背景信息和双方角色设定，给出y_script和n_script各个维度的评分，以json格式返回
    prompt = (
        f"请根据以下背景信息、角色设定和评价维度，对两个对话进行评分，评分范围均为 0 到 10 分，"
        f"要求分别对 y_script 和 n_script 各个维度进行评分，并以 JSON 格式返回结果。\n\n"
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
    