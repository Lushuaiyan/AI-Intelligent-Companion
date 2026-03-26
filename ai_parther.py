import streamlit as st
import os
from openai import OpenAI
import json
import datetime

# 生成会话ID的函数
def generate_conversation_id():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 保存会话信息的函数
def session_save():
    #保存的会话数据
    if st.session_state.conversation_id:
        session_data = {
                    "conversation_id": st.session_state.conversation_id,
                    "name": st.session_state.name,
                    "nature": st.session_state.nature,
                    "messages": st.session_state.messages
                }
        #创建保存会话记录的文件夹
        if not os.path.exists("./conversation_records"):
            os.makedirs("./conversation_records")
        #保存会话记录到本地JSON文件
        with open(f"./conversation_records/{st.session_state.conversation_id}.json", "w", encoding = "utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

# 加载所有的历史会话信息
def load_sessions():
    session_list = []
    if os.path.exists("./conversation_records"):
        file_list = os.listdir("./conversation_records")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    session_list.sort(reverse=True) #按时间倒序排序,最新的会话显示在最前面
    return session_list

# 加载指定的历史会话信息
def load_session(session):
    try:
        if os.path.exists(f"./conversation_records/{session}.json"):
            with open(f"./conversation_records/{session}.json", "r", encoding = "utf-8") as f:
                session_data = json.load(f)
                st.session_state.name = session_data["name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.conversation_id = session_data["conversation_id"]
                st.session_state.messages = session_data["messages"]               
    except Exception:
        st.error("加载会话失败")

# 删除指定的历史会话信息
def delete_session(session):
    try:
        if os.path.exists(f"./conversation_records/{session}.json"):             
            os.remove(f"./conversation_records/{session}.json")
            if session == st.session_state.conversation_id:
                st.session_state.messages = []
                st.session_state.conversation_id = generate_conversation_id()
                st.session_state.name = "小可爱"
                st.session_state.nature = "可爱、温柔、善解人意的四川姑娘"
    except Exception:
        st.error("删除会话失败")

#创建OpenAI客户端实例
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),base_url="https://api.deepseek.com")

#系统提示词
system_prompt = """
    你叫%s,现在是用户的真实伴侣,请完全带入你的角色
    规则:
    1.每次只能回复一句话,模仿人类的回复习惯,不要一次性回复过多内容
    2.禁止任何场景或状态描述性文字
    3.匹配用户的语言
    4.有需要的话可以使用表情包回复,但不要过于频繁
    5.用符合伴侣性格的语气回复,不要过于官方或机械
    6.回复内容要符合伴侣的性格设定,不要出现不符合设定的内容
    伴侣性格:
    - %s
    你必须严格遵守以上规则,完全带入角色,用心回复用户的每一个问题,让用户感受到你的陪伴和关爱
    """

## 页面配置
# 设置页面的配置项
st.set_page_config(
    #网页名
    page_title="AI 智能伴侣",
    #网页图标
    page_icon="🐶",
    layout="wide",
    #控制侧边栏
    initial_sidebar_state="expanded",
    menu_items={}
)

# 大标题
st.title("AI 智能伴侣")

# Logo
st.logo("./resource/AI伴侣.jpg", size = "large")

# 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = []

# 初始化昵称
if "name" not in st.session_state:
    st.session_state.name = "小可爱"

# 初始化性格设定
if "nature" not in st.session_state:
    st.session_state.nature = "可爱、温柔、善解人意的四川姑娘"

# 初始化会话ID
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = generate_conversation_id()

# 侧边栏
with st.sidebar:
    st.subheader("AI控制面板")
    if st.button("新建会话", icon = "✏️", use_container_width = True):
        #保存当前会话记录到本地文件
        session_save()
        #创建一个新的会话
        if st.session_state.messages:#不要在空会话新建会话
            st.session_state.messages = []
            st.session_state.name = "小可爱"
            st.session_state.nature = "可爱、温柔、善解人意的四川姑娘"
            st.session_state.conversation_id = generate_conversation_id()
            session_save()
            st.rerun()  #刷新页面,开始新的会话
    #会话历史栏
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        #在同一行分成两列
        col1, col2 = st.columns([4, 1])
        with col1:
            #历史会话信息
            if st.button(session, icon = "📜", use_container_width = True, type = "primary" if session == st.session_state.conversation_id else "secondary"):
                #加载指定的会话信息
                load_session(session)
                st.rerun()

        with col2:
            if st.button("", icon = "❌️", use_container_width = True, key = f"delete_{session}"):
                #删除指定的会话信息
                delete_session(session)
                st.rerun()

    #分割线
    st.divider()

    #伴侣信息设置
    st.subheader("伴侣信息")
    # 昵称输入框
    name = st.text_input("昵称", placeholder="请输入伴侣的昵称", value = st.session_state.name)
    st.session_state.name = name
    # 性格设定输入框
    nature = st.text_area("性格", placeholder="请输入伴侣的性格设定", value = st.session_state.nature)
    st.session_state.nature = nature

# 当前会话ID显示
if st.session_state.conversation_id:
    st.text(f"当前会话ID: {st.session_state.conversation_id}")

# 显示聊天记录
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(f"用户: {message['content']}")
    else:
        st.chat_message("assistant").write(f"AI智能伴侣: {message['content']}")

# 用户输入框
prompt = st.chat_input("请输入您的问题")
if prompt:
    # 显示用户输入
    st.chat_message("user").write(f"用户: {prompt}")
    print(f"--------------->用户输入: {prompt}")
    st.session_state.messages.append({"role": "user", "content": prompt})

    #调用AI大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.name, st.session_state.nature)},
            *st.session_state.messages  #解决会话记忆功能的缺失,滚雪球
        ],
        stream=True
    )

    # #显示AI回复(非流式输出的解析方式)
    # ai_reply = response.choices[0].message.content
    # st.chat_message("assistant").write(f"AI智能伴侣: {ai_reply}")
    # print(f"--------------->AI回复: {ai_reply}")
    # #保存大模型的回复结果
    # st.session_state.messages.append({"role": "assistant", "content": ai_reply})

    #显示AI回复(流式输出的解析方式)
    reply_messages = st.empty() #创建一个空容器,用来流式显示AI回复的内容
    full_reply = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            full_reply += chunk.choices[0].delta.content
            reply_messages.chat_message("assistant").write(f"AI智能伴侣: {full_reply}")
    #保存大模型的回复结果
    st.session_state.messages.append({"role": "assistant", "content": full_reply})    

    #保存会话信息
    session_save()


    
