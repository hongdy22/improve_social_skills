import re
import matplotlib.pyplot as plt

# 存储各个文件中 y_script 和 n_script 的总分
y_scores = []
n_scores = []

# 循环处理1.txt到10.txt
for i in range(1, 11):
    filename = f"{i}.txt"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"文件 {filename} 未找到。")
        continue

    # 分别收集以 y_script: 和 n_script: 开头的所有行
    y_lines = [line.strip() for line in lines if line.strip().startswith("y_script:")]
    n_lines = [line.strip() for line in lines if line.strip().startswith("n_script:")]

    # 判断是否存在至少两个这样的行
    if len(y_lines) < 2 or len(n_lines) < 2:
        print(f"文件 {filename} 格式不正确。")
        continue

    # 取第二个 y_script 和 n_script
    y_line = y_lines[1]
    n_line = n_lines[1]

    # 定义正则表达式，提取 'total score' 后面的数值
    pattern = r"'total score':\s*([0-9.]+)"
    
    y_match = re.search(pattern, y_line)
    n_match = re.search(pattern, n_line)

    if y_match and n_match:
        try:
            y_score = float(y_match.group(1)) * 100  # 转换为百分制
            n_score = float(n_match.group(1)) * 100
        except ValueError:
            print(f"文件 {filename} 中的得分格式错误。")
            continue

        y_scores.append(y_score)
        n_scores.append(n_score)
    else:
        print(f"文件 {filename} 中未找到 total score 信息。")
        continue

# 检查是否有数据
if not y_scores or not n_scores:
    print("未能提取到任何得分数据。")
    exit()
else:
    # 定义横坐标标签 section1 到 section10
    sections = [f"section{i}" for i in range(1, len(y_scores) + 1)]

    # 绘制条形图
    x = range(len(sections))
    width = 0.35  # 条形宽度

    fig, ax = plt.subplots(figsize=(10, 6))
    bars_y = ax.bar([p - width/2 for p in x], y_scores, width, label='y_script')
    bars_n = ax.bar([p + width/2 for p in x], n_scores, width, label='n_script')

    # 在条形上显示具体数值
    for bar in bars_y:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height, f'{height:.1f}', ha='center', va='bottom')

    for bar in bars_n:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height, f'{height:.1f}', ha='center', va='bottom')

    ax.set_xlabel('Sections')
    ax.set_ylabel('Total Score (Percentage)')
    ax.set_title('Score Comparison Across Sections')
    ax.set_xticks(x)
    ax.set_xticklabels(sections)
    ax.legend()

    plt.tight_layout()
    plt.show()
