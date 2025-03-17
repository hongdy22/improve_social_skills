## 该文件可以绘制对话质量评分的条形图（适用于当前版本）
import re
import json
import matplotlib.pyplot as plt
import numpy as np

# 场景数量
setting_num = 5
difficult_num = 5
easy_num = 0

def parse_score_line(line):
    """
    给定一行文本（以 "final_scores:"、"final scores:" 或 "**final_scores"、"**final scores" 开头），
    去除前缀后提取7个数值评分。评分可能包含额外的文字（例如 "5 points" 或 "7"）。
    """
    # 移除前缀（直到冒号为止的所有内容）
    _, _, remainder = line.partition(':')
    # 按逗号分割并去除每个部分的空白字符
    parts = [part.strip() for part in remainder.split(',')]
    # 使用正则表达式提取每个部分中的数字
    scores = []
    for part in parts:
        match = re.search(r"(\d+(?:\.\d+)?)", part)
        if match:
            scores.append(float(match.group(1)))
    return scores

def process_file(filename):
    """
    打开指定文件，忽略空白行，然后将有效行分为两部分：
    前3行和后3行。对每一部分计算每一项的列平均分（每行包含7项评分）。
    返回两个列表：final_scores_part1 和 final_scores_part2（各长度为7）。
    """
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 去除空白行并去除每行两侧空白字符
    valid_lines = [line.strip() for line in lines if line.strip()]
    
    # 前3行和后3行
    part1_lines = valid_lines[:difficult_num]
    part2_lines = valid_lines[-easy_num:]
    
    # 将每一行解析为7个数字
    part1_scores = [parse_score_line(line) for line in part1_lines]
    part2_scores = [parse_score_line(line) for line in part2_lines]
    
    # 检查每一行是否有7个评分
    for idx, scores in enumerate(part1_scores + part2_scores):
        if len(scores) != 7:
            raise ValueError(f"Line {idx+1} in {filename} does not contain 7 scores: {scores}")
    
    # 分别计算前3行和后3行的每一项的平均分
    final_scores_part1 = [sum(scores[i] for scores in part1_scores) / difficult_num for i in range(7)]
    final_scores_part2 = [sum(scores[i] for scores in part2_scores) / easy_num for i in range(7)]
    
    return final_scores_part1, final_scores_part2

# 处理"./Y_scores/a_score_summary"文件
final_scores1, final_scores2 = process_file("./Y_scores/a_score_summary.txt")

# 处理"./N_scores/a_score_summary"文件
final_scores3, final_scores4 = process_file("./N_scores/a_score_summary.txt")

def plot_grouped_bars(scores_a, scores_b, title):
    """
    绘制分组条形图，用于比较 scores_a 和 scores_b。
    横坐标为7个项目，对于每个项目绘制两个条形：一个代表 scores_a，一个代表 scores_b。
    """
    n = 7  # 项目数
    x = np.arange(n)
    width = 0.35  # 每个条形的宽度

    fig, ax = plt.subplots()
    # 绘制两组条形
    bars1 = ax.bar(x - width/2, scores_a, width, label='with_reasoning', color='salmon')
    bars2 = ax.bar(x + width/2, scores_b, width, label='without_reasoning', color='skyblue')

    # 设置x轴和y轴标签及标题
    ax.set_xlabel('Score Index')
    ax.set_ylabel('Average Score')
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels([f'Item {i+1}' for i in range(n)])
    ax.legend()

    # 为每个条形添加数值标签
    def autolabel(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 竖直偏移3个点
                        textcoords="offset points",
                        ha='center', va='bottom')
    
    autolabel(bars1)
    autolabel(bars2)
    
    plt.tight_layout()
    plt.show()

# 绘制第一组分组条形图：final_scores1 和 final_scores3（分别来自Y_scores和N_scores的前3行）
plot_grouped_bars(final_scores1, final_scores3, "Difficult Section: with_reasoning vs without_reasoning")

# 绘制第二组分组条形图：final_scores2 和 final_scores4（分别来自Y_scores和N_scores的后3行）
plot_grouped_bars(final_scores2, final_scores4, "Easy Section: with_reasoning vs without_reasoning")
