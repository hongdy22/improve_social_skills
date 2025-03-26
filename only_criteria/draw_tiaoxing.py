import os
import numpy as np
import matplotlib.pyplot as plt

def extract_scores(file_path):
    y_scores, n_scores = [], []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content.startswith("{") and content.endswith("}"):
                # JSON 格式
                data = json.loads(content)
                if "y_script" in data:
                    y_scores = list(map(int, data["y_script"].split(", ")))
                if "n_script" in data:
                    n_scores = list(map(int, data["n_script"].split(", ")))
            else:
                # 纯文本格式
                print("file_path:", file_path)
                for line in content.split("\n"):
                    if line.startswith("y_script:"):
                        y_scores = list(map(int, line.split(":")[1].strip().rstrip(",").split(", ")))
                    elif line.startswith("n_script:"):
                        n_scores = list(map(int, line.split(":")[1].strip().rstrip(",").split(", ")))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return y_scores, n_scores

def main():
    y_all, n_all = [], []
    
    for i in range(1, 11):  # 处理1.txt到10.txt
        file_name = f"{i}.txt"
        if os.path.exists(file_name):
            y_scores, n_scores = extract_scores(file_name)
            y_all.append(y_scores)
            n_all.append(n_scores)
    
    # 确保所有列表长度一致
    max_length = max(len(y_all[0]), len(n_all[0])) if y_all and n_all else 0
    y_all = [arr + [0] * (max_length - len(arr)) for arr in y_all]
    n_all = [arr + [0] * (max_length - len(arr)) for arr in n_all]
    
    # 转换为NumPy数组并计算平均值
    y_array = np.array(y_all)
    n_array = np.array(n_all)
    
    y_avg = np.mean(y_array, axis=0)  # 计算每列的平均值
    n_avg = np.mean(n_array, axis=0)
    
    # 存储结果
    final_scores_part1 = {7: y_avg.tolist()}
    final_scores_part3 = {7: n_avg.tolist()}
    
    print("final_scores_part1[7]:", final_scores_part1[7])
    print("final_scores_part3[7]:", final_scores_part3[7])
    
    # 绘制条形图
    x_labels = [f"Item {i+1}" for i in range(len(y_avg))]
    x = np.arange(len(y_avg))
    width = 0.35  # 柱状图宽度
    
    fig, ax = plt.subplots()
    bars1 = ax.bar(x - width/2, y_avg, width, label='y_script')
    bars2 = ax.bar(x + width/2, n_avg, width, label='n_script')
    
    # 在条形图上方标注数字
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height, f'{height:.2f}', ha='center', va='bottom')
    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height, f'{height:.2f}', ha='center', va='bottom')
    
    ax.set_xlabel('Index')
    ax.set_ylabel('Average Score')
    ax.set_title('Average Scores from 10 sections')
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45)
    ax.legend()
    
    # 设置纵坐标范围
    ax.set_ylim(5, max(max(y_avg), max(n_avg)) + 1)
    
    plt.show()

if __name__ == "__main__":
    main()
