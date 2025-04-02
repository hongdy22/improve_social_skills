import os
import numpy as np
import matplotlib.pyplot as plt
import re

def extract_scores(file_path):
    y_scores, n_scores = [], []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 读取每一行，读取到"y_script"和"n_script"的行
            for line in f:
                if "y_script" in line:
                    # 提取行中的所有数字
                    nums = re.findall(r'\d+', line)
                    if len(nums) == 7:
                        # 只取前7个数字并转换为整数后加入列表
                        y_scores.append(list(map(int, nums[:7])))
                    else:
                        print(f"Warning: Expected 7 numbers in y_script, found {len(nums)} in line: {line.strip()}")
                elif "n_script" in line:
                    # 与上面类似，提取行中的所有数字
                    nums = re.findall(r'\d+', line)
                    if len(nums) == 7:
                        # 只取前7个数字并转换为整数后加入列表
                        n_scores.append(list(map(int, nums[:7])))
                    else:
                        print(f"Warning: Expected 7 numbers in n_script, found {len(nums)} in line: {line.strip()}")
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
    
    # 确保所有文件的数据行数一致，如果某文件数据不足，则补全为 [0,0,...,0] (7个0)
    if y_all and n_all:
        max_length = max(len(y_all[0]), len(n_all[0]))
        y_all = [arr + [[0]*7 for _ in range(max_length - len(arr))] for arr in y_all]
        n_all = [arr + [[0]*7 for _ in range(max_length - len(arr))] for arr in n_all]
    else:
        max_length = 0

    # 转换为 NumPy 数组，并将形状调整为 (文件数, 行数, 7)
    y_array = np.array(y_all)  # 形状: (num_files, max_length, 7)
    n_array = np.array(n_all)
    
    # 对所有文件在第一维求平均，得到 shape (max_length, 7)
    y_avg = np.mean(y_array, axis=0).squeeze()  # squeeze 去除多余的维度
    n_avg = np.mean(n_array, axis=0).squeeze()
    
    # 若只有一行数据，则 y_avg, n_avg 可能为 1D 数组；若多行则可根据需求选择哪一行或对多行数据做进一步处理
    # 这里假设只处理第一行的平均数据（如果有多行，可根据实际需求修改）
    if y_avg.ndim == 2:
        y_avg = y_avg[0]
    if n_avg.ndim == 2:
        n_avg = n_avg[0]
    
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
