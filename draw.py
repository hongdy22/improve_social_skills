#### 信息不对称获取能力对比绘图
import matplotlib.pyplot as plt
import numpy as np

# 删除使用 seaborn 风格的代码
# plt.style.use('seaborn-darkgrid')

# 数据准备
sections = ["With Reasoning", "Without Reasoning"]
y_scores = [73.125, 61.417]
n_scores = [84.291, 68.291]

# 创建画布和坐标轴
fig, ax = plt.subplots(figsize=(12, 7))
bar_width = 0.3
indices = np.arange(len(sections))

# 定义专业配色：柔和蓝色和橙色
colors = ['#4C72B0', '#DD8452']

# 绘制条形图
bars_y = ax.bar(indices - bar_width/2, y_scores, bar_width,
                label='Difficult Section', color=colors[0],
                edgecolor='black', alpha=0.9)
bars_n = ax.bar(indices + bar_width/2, n_scores, bar_width,
                label='Easy Section', color=colors[1],
                edgecolor='black', alpha=0.9)

# 添加数值标签
def add_labels(bars):
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                f'{height:.1f}', ha='center', va='bottom', fontsize=10)

add_labels(bars_y)
add_labels(bars_n)

# 坐标轴和标题设置
ax.set_ylim(60, 90)
ax.set_ylabel('Average Score', fontsize=12, labelpad=10)
ax.set_xlabel('Prompt Strategy', fontsize=12, labelpad=10)
ax.set_title('Performance Comparison by Strategy and Section Difficulty',
             fontsize=14, pad=20, fontweight='bold')

# 设置 x 轴刻度及标签
ax.set_xticks(indices)
ax.set_xticklabels([s.upper() for s in sections], fontsize=11)

# 添加横向网格并去掉上右边框
ax.grid(True, linestyle='--', alpha=0.6, axis='y')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 调整图例位置和样式
legend = ax.legend(loc='upper right', frameon=True, shadow=True, framealpha=0.9)
legend.get_frame().set_edgecolor('#FFFFFF')

# 调整整体布局，并添加脚注
plt.tight_layout(pad=3)
plt.figtext(0.5, 0.01, 'Data Source: Experimental Results',
            ha='center', fontsize=9, color='#666666')

plt.show()
