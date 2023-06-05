import streamlit as st
import openai
from pathlib import Path
from tempfile import NamedTemporaryFile
import os

openai.api_key = st.secrets['api_key']

if "qa" not in st.session_state:
    st.session_state.qa = {"pdf": "", "history": []}

def store_del_msg():
    st.session_state.qa["history"].append({"role": "Q", "msg": st.session_state.user_input}) # store
    st.session_state.user_input = ""  # del

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "あなたは優秀なアシスタントAIです。"}
        ]

# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]

    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )  

    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)

    st.session_state["user_input"] = ""  # 入力欄を消去

# View (User Interface)
## Sidebar
st.sidebar.title("タイトル未定")
user_input = st.sidebar.text_input("ご質問をどうぞ", key="user_input", on_change=store_del_msg)
## Main Content
if st.session_state.qa["history"]:
    for message in st.session_state.qa["history"]:
        if message["role"] == "Q": # Q: Question (User)
            st.info(message["msg"])
        elif message["role"] == "A": # A: Answer (AI Assistant)
            st.success(message["msg"])
        elif message["role"] == "E": # E: Error
            st.error(message["msg"])
chat_box = st.empty() # Streaming message

# Model (Business Logic)

if st.session_state.qa["history"]:
    query = st.session_state.qa["history"][-1]["msg"]
    try:
        response = engine.query(query) # Query to ChatGPT
        text = ""
        for next in response.response_gen:
            text += next
            chat_box.success(text)
            st.session_state.qa["history"].append({"role": "A", "msg": text})
    except Exception as error_msg:
#             error_msg = "エラーが発生しました！　もう一度、質問して下さい。"
        st.error(error_msg)
        st.session_state.qa["history"].append({"role": "E", "msg": error_msg})
