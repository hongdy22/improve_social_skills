import json
import matplotlib.pyplot as plt

### 处理带推理的数据
data_summary = {}
for i in range(0, 20):
    file_path = f'Y_consensus/{i+1}_consensus_progress.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # 存储每个 round 的 (B_discovered + A_discovered) 数组大小
        consensus_progress = []
        for entry in data:
            b_size = len(entry["progress"].get("B_discovered", []))
            a_size = len(entry["progress"].get("A_discovered", []))
            consensus_progress.append(b_size + a_size)
        
        # 存储结果
        data_summary[f"{i+1}_consensus_progress"] = consensus_progress
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# 输出结果
for key, value in data_summary.items():
    print(f"{key} = {value}")
    
# 将前3组每部分的数据第一项相加，然后除以3，得到平均值，然后第二项相加，以此类推
average_data_1 = []
for i in range(9):
    average_data_1.append(sum([data_summary[f"{j}_consensus_progress"][i] for j in range(1, 11)]) / 10)
print(f"average_data = {average_data_1}")

# 将后3组每部分的数据第一项相加，然后除以3，得到平均值，然后第二项相加，以此类推
average_data_2 = []
for i in range(9):
    average_data_2.append(sum([data_summary[f"{j}_consensus_progress"][i] for j in range(11, 21)]) / 10)
print(f"average_data = {average_data_2}")

### 处理不带推理的数据
data_summary = {}
for i in range(0, 20):
    file_path = f'N_consensus/{i+1}_consensus_progress.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # 存储每个 round 的 (B_discovered + A_discovered) 数组大小
        consensus_progress = []
        for entry in data:
            b_size = len(entry["progress"].get("B_discovered", []))
            a_size = len(entry["progress"].get("A_discovered", []))
            consensus_progress.append(b_size + a_size)
        
        # 存储结果
        data_summary[f"{i+1}_consensus_progress"] = consensus_progress
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# 输出结果
for key, value in data_summary.items():
    print(f"{key} = {value}")
    
# 将前3组每部分的数据第一项相加，然后除以3，得到平均值，然后第二项相加，以此类推
average_data_3 = []
for i in range(9):
    average_data_3.append(sum([data_summary[f"{j}_consensus_progress"][i] for j in range(1, 11)]) / 10)
print(f"average_data = {average_data_3}")

# 将后3组每部分的数据第一项相加，然后除以3，得到平均值，然后第二项相加，以此类推
average_data_4 = []
for i in range(9):
    average_data_4.append(sum([data_summary[f"{j}_consensus_progress"][i] for j in range(11, 21)]) / 10)
print(f"average_data = {average_data_4}")

# 绘制折线图
plt.figure(figsize=(10, 5))
x = range(1, 10)
plt.plot(x, average_data_1, marker='o', linestyle='-', label='with_reasoning', color='salmon')
plt.plot(x, average_data_3, marker='s', linestyle='--', label='without_reasoning', color='skyblue')
plt.xlabel("Round")
plt.ylabel("Consensus Progress")
plt.title("Difficult Section Consensus Progress Summary")
plt.legend()
plt.grid(True)
plt.show()

plt.figure(figsize=(10, 5))
x = range(1, 10)
plt.plot(x, average_data_2, marker='o', linestyle='-', label='with_reasoning', color='salmon')
plt.plot(x, average_data_4, marker='s', linestyle='--', label='without_reasoning', color='skyblue')
plt.xlabel("Round")
plt.ylabel("Consensus Progress")
plt.title("Easy Section Consensus Progress Summary")
plt.legend()
plt.grid(True)
plt.show()
