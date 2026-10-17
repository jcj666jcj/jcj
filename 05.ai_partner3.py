import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json


system_prompt = """
            你叫%s，现在是用户的真实伴侣，请完全带入伴侣角度，用温柔可爱的语气回答用户的问题。
             规则
             1.每次只会发一条信息
             2禁止人任何场景和状态描述性文字
             3匹配用户的语言
             4回复简短，像微信聊天一样
             5有需要的话可以使用emoji表情
             6用符合伴侣性格的方式对话
             7回复的内容要充分体现伴侣性格
            伴侣性格：%s  
            """


client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com")


st.set_page_config(
     page_title="ai智能伴侣",
     page_icon="🫶",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={},

)


#标题
st.title("ai智能伴侣")
#logo
st.logo("第三章/logo.webp")

#加载指定的对话信息
def load_session(session_name):
    if os.path.exists(f"sessions/{session_name}.json"):
        with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
            session_data = json.load(f)
        st.session_state.name = session_data["name"]
        st.session_state.nature = session_data["nature"]
        st.session_state.messages = session_data["messages"]
        st.session_state.current_session =session_name
        st.rerun()
    else:
        st.error("会话不存在")


def delete_session(session_name):
    if os.path.exists(f"sessions/{session_name}.json"):
        os.remove(f"sessions/{session_name}.json")
        #如果删除的是当前会话，则需要更新消息列表
        if session_name == st.session_state.current_session:
            st.session_state.messages = []
            st.session_state.name = '小甜甜'
            st.session_state.nature = '活泼开朗'
            st.session_state.current_session = generate_session_name()
    else:
        st.error("会话不存在")



#加载所有的会话列表信息
def load_sessions():
    sessions_list = []
    # 加载所有会话列表信息
    if os.path.exists("sessions"):
        file_list=os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                sessions_list.append(filename[:-5])  # 去掉.json后缀
    sessions_list.sort(reverse=True)  # 按时间倒序排列
    return sessions_list

# 生成会话标识的函数（当前时间）
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 保存会话函数
def save_session():
    # 保存当前会话
    if st.session_state.current_session:
        # 构建新的会话对象
        session_date = {"name": st.session_state.name,
                        "nature": st.session_state.nature,
                        "messages": st.session_state.messages,
                        "session_session": st.session_state.current_session}
        # 如果sessions不存在，则创建一个
        if not os.path.exists("sessions"):
            os.makedirs("sessions")

        # 保存会话数据
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_date, f, ensure_ascii=False, indent=2)


#初始化聊天信息
if 'messages' not in st.session_state:
    st.session_state.messages = []#初始化聊天信息

 #昵称
if 'name' not in st.session_state:
        st.session_state.name = '小甜甜' # 初始化聊天信息
 #性格
if 'nature' not in st.session_state:
        st.session_state.nature = '活泼开朗' # 初始化聊天信息
#会话标识
if 'current_session' not in st.session_state:
    st.session_state.current_session = generate_session_name() # 初始化会话标识


#左侧侧边栏
st.sidebar.subheader("ai控制面板")
#新建会话
if st.sidebar.button("新建会话",width="stretch",icon="💾"):
    # 保存当前会话逻辑信息
    save_session()
#创建新的会话
    if st.session_state.messages:  # 如果有聊天信息
        st.session_state.messages = []#初始化聊天信息
        st.session_state.name = '小甜甜' # 初始化聊天信息
        st.session_state.nature = '活泼开朗' # 初始化聊天信息
        st.session_state.current_session = generate_session_name()
        save_session()
        st.rerun()
st.sidebar.text("会话历史")#会话历史
sessions_list = load_sessions()
for session in sessions_list:
    col1,col2=st.sidebar.columns([4,1])
    with col1:#加载会话信息#三元运算符；如果条件为真，则返回第一个表达式的值，否则，则返回第二个表达式的值，语法：值1 if 条件 else 值2
       if col1.button(session,width="stretch", icon="📁",key=f"load_{session}",type="primary" if session==st.session_state.current_session else "secondary"):#加载会话信息
           load_session(session)
           st.rerun()
    with col2:
       if col2.button("",width="stretch", icon="🚫",key=f"delete_{session}"):#删除会话信息
           delete_session(session)
           st.rerun()


with st.sidebar:
    st.subheader("伴侣信息")
    name = st.text_input("昵称", placeholder="请输入昵称", value=st.session_state.name)
    if name:
        st.session_state.name = name  # 初始化聊天信息
    nature = st.text_input("性格", placeholder="请输入性格", value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature  # 初始化聊天信息






#展示历史聊天信息
st.text(f"会话名称：{st.session_state.current_session}")
for message in st.session_state.messages:
    if message['role']=="user":
        st.chat_message("user").write(message['content'])
    elif message['role']=="assistant":
        st.chat_message("assistant").write(message['content'])



#消息输入框
prompt=st.chat_input("请输入您要问的问题")#输入框
if prompt:#字符串自动转化为布尔值，非空为Ture，空为false
     st.chat_message("user").write(prompt)#展示输入内容
     st.session_state.messages.append({"role": "user", "content": prompt})#将用户输入内容添加到聊天信息中



     #调用ai大模型
     response = client.chat.completions.create(
         model="deepseek-chat",
         messages=[
             {"role": "system", "content": system_prompt % (st.session_state.name, st.session_state.nature)},
             *st.session_state.messages
         ],
         temperature=0.7,#控制ai大模型回答的随机性，值越小越确定性越高
         stream=True,#启动流式输出
     )
     #非流式输出的解析方式
     # st.chat_message("assistant").write(response.choices[0].message.content)#展示ai大模型回答内容

     #流式输出的解析方式
     response_message=st.empty()
     full_response = ""
     for chunk in response:
         if chunk.choices[0].delta.content:
             full_response += chunk.choices[0].delta.content
             response_message.chat_message ("assistant").write(full_response)

     st.session_state.messages.append({"role": "assistant", "content": full_response})  #将ai大模响应内容存汝
     save_session()
