## 该文件可以绘制对话质量评分的折线图（不适用于当前版本）
import re
import numpy as np

def extract_numbers(line):
    """从字符串中提取数字"""
    numbers = [int(num) for num in re.findall(r'\d+', line)]
    return numbers

def process_section(file, section_num=3, rows=3, cols=7):
    """处理数据部分"""
    section = np.zeros((rows, cols))
    for _ in range(section_num):
        for i in range(rows):
            line = file.readline().strip()
            numbers = extract_numbers(line)
            for k in range(min(cols, len(numbers))):
                section[i][k] += numbers[k]
    
    section = np.round(section / section_num, 2)
    return section

def main():
    try:
        with open("scores/a_score_summary.txt", "r", encoding="utf-8") as file:
            section1 = process_section(file)
            file.readline()  # 跳过空行
            section2 = process_section(file)
    except FileNotFoundError:
        print("无法打开文件 scores/a_score_summary.txt")
        return
    
    # 输出结果
    for row in section1:
        print(" ".join(map(str, row)))
    print()
    for row in section2:
        print(" ".join(map(str, row)))

if __name__ == "__main__":
    main()