from openai import OpenAI
model_names = ["gpt-4o", "gpt-4-0613", "gpt-4-1106-preview", "gpt-3.5-turbo", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-1106", "gpt-4-vision-preview", "gpt-4o"]
client= OpenAI(base_url="http://115.182.62.174:18888/v1", api_key="zQTxB4T2yXBFeoBtE7418192Df3e476a84259d84D9015cC1")
model_names = ["gpt-4o", "gpt-4-0613", "gpt-4-1106-preview", "gpt-3.5-turbo", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-1106", "gpt-4-vision-preview", "gpt-4o"]

#预处理

#读入基本setting
content_setting=""
with open('setting.txt', 'r') as file:
    content_setting=file.read()
#读入生成指令
content_instruction_A=""
content_instruction_B=""
with open('instruction_A.txt', 'r') as file:
    content_instruction_A=file.read()
with open('instruction_B.txt', 'r') as file:
    content_instruction_B=file.read()
messages=[]
messages.append(
{
"role":"system",
"content":"You are a helpful assistant."
}
)


#先生成一轮对话

messages.append(
{
"role":"user",
"content": content_setting+"You should play as A and B and generate the first turn of the conversation.(only utterance, no action)"
}
)
response_script=client.chat.completions.create(
model=model_names[0],
messages=messages,
)
#不包含推理部分的script
script=response_script.choices[0].message.content
#包含推理部分的script
all_script=script
messages.pop()


#生成script

#截取utterance部分的函数
def extract_utterance(raw_content):
    last_character="?"
    now_character="?"
    tf=False
    mature_content=""
    for now_character in raw_content:
        if tf:
            mature_content=mature_content+now_character
        if now_character == "\n":
            tf=False
        if now_character == ":" and (last_character == "A" or last_character == "B"):
            mature_content=mature_content+last_character+now_character
            tf=True
        last_character=now_character
    return mature_content
#生成script
def generate_script(content_instruction):
    global content_setting
    global script
    global all_script
    global messages
    messages.append(
    {
    "role":"user",
    "content": content_setting+script+content_instruction
    }
    )
    response_script=client.chat.completions.create(
    model=model_names[0],
    messages=messages,
    )
    raw_content=response_script.choices[0].message.content
    #提取utterance
    mature_content=extract_utterance(raw_content=raw_content)
    #更新仅utterance的script
    script=script+"\n"+mature_content
    #更新含utterance的script
    all_script=all_script+"\n"+raw_content
    messages.pop()
#生成20轮
for i in range(20):
    #A生成
    generate_script(content_instruction_A)
    #B生成
    generate_script(content_instruction_B)


#输出

with open('script.txt','w') as file:
    file.write(script)
with open('all_script.txt','w') as file:
    file.write(all_script)