# 计算消耗的token数

with open('token_count.txt', 'r') as f:
    lines = f.readlines()
    input_tokens = []
    output_tokens = []
    total_tokens = []
    for line in lines:
        # 提取Input tokens, Output tokens, Total tokens
        input_token = int(line.split('Input tokens: ')[1].split(',')[0])
        output_token = int(line.split('Output tokens: ')[1].split(',')[0])
        total_token = int(line.split('Total tokens: ')[1].strip())
        
        input_tokens.append(input_token)
        output_tokens.append(output_token)
        total_tokens.append(total_token)
    # 计算总和
    input_tokens_sum = sum(input_tokens)
    output_tokens_sum = sum(output_tokens)
    total_tokens_sum = sum(total_tokens)
    # 输出结果
    print(f"Input tokens sum: {input_tokens_sum}")
    print(f"Output tokens sum: {output_tokens_sum}")
    print(f"Total tokens sum: {total_tokens_sum}")
# 计算平均值
input_tokens_avg = input_tokens_sum / len(input_tokens)
output_tokens_avg = output_tokens_sum / len(output_tokens)
total_tokens_avg = total_tokens_sum / len(total_tokens)
# 输出结果
print(f"Input tokens avg: {input_tokens_avg}")
print(f"Output tokens avg: {output_tokens_avg}")
print(f"Total tokens avg: {total_tokens_avg}")