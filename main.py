from openai import OpenAI
import streamlit as st
from pinecone import Pinecone
import uuid

# 生成唯一id
def generate_unique_id():
    return str(uuid.uuid4())

# Pinecone数据库
pc = Pinecone(api_key=st.secrets["pinecone-api-key"])
index = pc.Index("lei")

st.title("Vector Database Assistant")

client = OpenAI(api_key=st.secrets["gpt-api-key"])

# embedding算法
def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# 保存内容到Pinecone数据库
def save_content(content):
    try:
        embedding = get_embedding(content)
        unique_id = generate_unique_id()
        index.upsert(vectors=[(unique_id, embedding)])
        return f"Save succeed，ID: {unique_id}"
    except Exception as e:
        return f"Save failed: {str(e)}"
    
# 查询相似内容
def get_content(content):
    try:
        query_embedding = get_embedding(content)
        results = index.query(vector=[query_embedding], top_k=5)
        return results
    except Exception as e:
        return f"Query failed: {str(e)}"

# 处理GPT响应的函数
def handle_gpt_response(response):
    # 解析GPT响应
    if response.startswith("1 = "):
        content = response.split("=", 1)[1].strip()
        return save_content(content)
    elif response.startswith("0 = "):
        content = response.split("=", 1)[1].strip()
        return get_content(content)

# Streamlit message
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "I am your Vector Database assistant bot. How can I assist you? If you need to store content, please input the command: save:[content you want to store]. If you need to perform a comparison, please input the command: get:[content you want to compare]."},
        {"role": "system", "content": "You are a Vector Database assistant bot. Your task is to assist users in database insertion and retrieval operations. Users may input their requests in natural language or using specific commands. For instance, a user might say ‘I want to save this content: [content you want to store]’ or ‘Can you retrieve information similar to [content you want to compare]?’. Based on the user's input, you will interpret the request and act accordingly. If the request is to save content, you will extract the content and return it in the format ‘1 = 'content you want to store'’. If the request is to retrieve content, you will search for similar content and return the closest matches in the format ‘0 = 'content you want to compare'’."}
        ]

for message in [m for m in st.session_state.messages if m["role"] != "system"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def format_results(results):
    # 初始化一个列表来存储格式化后的匹配项
    formatted_matches = []
    # 遍历查询结果中的匹配项
    for match in results['matches']:
        # 对每个匹配项，提取ID和得分（cosine相似度分数）
        match_id = match['id']
        score = match['score']
        # 将ID和得分格式化为字符串，然后添加到列表中
        formatted_matches.append(f"ID: {match_id}, cosine: {score}")
    # 如果没有找到匹配的项，返回一个提示信息
    if not formatted_matches:
        return "No match found."
    # 将所有格式化后的匹配项连接成一个字符串，每项之间用换行符分隔
    formatted_result = "The five most matching items and their corresponding cosine scores are:\n\n" + "\n\n".join(formatted_matches)
    return formatted_result

# 判断是否是特殊输入输出
def isQuery(response):
    if response.startswith("0 = "):
        return True
    else: 
        return False

def isPut(response):
    if response.startswith("1 = "):
        return True
    else:
        return False

# prompt是用户输入
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream = False
        )
        # print(stream.choices[0].message.content)
        #response = st.write_stream(stream)
        response = stream.choices[0].message.content
        if isQuery(response):
            result = handle_gpt_response(response)
            format_output = format_results(result)
            st.markdown(format_output)
            response = format_output
        elif isPut(response):
            print("现在我在存储")
            result = handle_gpt_response(response)
            st.markdown(result)
            response = result
        else:
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})