import streamlit as st
import openai
import requests
import json
from difflib import SequenceMatcher

st.set_page_config(page_title="語馴塔：The Language Conditioning Panopticon")
st.title("語馴塔：The Language Conditioning Panopticon")

model_option = st.selectbox("選擇模型", ["OpenAI", "Anthropic Claude", "自定義模型"])
user_input = st.text_area("輸入要檢測的句子")
custom_api_url = ""

if model_option == "自定義模型":
    custom_api_url = st.text_input("輸入自定義 API 的 URL")

if st.button("執行判斷與改寫"):
    if not user_input:
        st.error("請輸入句子")
    else:
        try:
            revised_text = ""

            if model_option == "OpenAI":
                openai.api_key = st.secrets["OPENAI_API_KEY"]
                openai.organization = st.secrets["OPENAI_ORG_ID"]
                openai.project = st.secrets["OPENAI_PROJECT_ID"]
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": f"請判斷下列句子是否需要改寫，若需要請提供改寫版本，否則請重複原句即可：{user_input}"}
                    ]
                )
                revised_text = response.choices[0].message.content.strip()

            elif model_option == "Anthropic Claude":
                headers = {
                    "x-api-key": st.secrets["CLAUDE_API_KEY"],
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
                data = {
                    "model": "claude-3-opus-20240229",
                    "max_tokens": 1000,
                    "messages": [
                        {"role": "user", "content": f"請判斷下列句子是否需要改寫，若需要請提供改寫版本，否則請重複原句即可：{user_input}"}
                    ]
                }
                response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, data=json.dumps(data))
                revised_text = response.json()["content"][0]["text"].strip()

            elif model_option == "自定義模型":
                if not custom_api_url:
                    st.error("請輸入自定義 API 的 URL")
                    st.stop()
                response = requests.post(custom_api_url, json={"text": user_input})
                revised_text = response.json()["revised"]

            st.subheader(" 改寫結果")
            st.write(revised_text)

            def highlight_diff(original, revised):
                matcher = SequenceMatcher(None, original, revised)
                highlighted = ""
                for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
                    if opcode == "equal":
                        highlighted += original[a0:a1]
                    elif opcode in ("replace", "delete"):
                        highlighted += f'<span style="background-color:#ffd6d6">{original[a0:a1]}</span>'
                    elif opcode == "insert":
                        highlighted += f'<span style="background-color:#d6ffd6">{revised[b0:b1]}</span>'
                return highlighted

            st.markdown("###  改寫差異高亮比對")
            diff_html = highlight_diff(user_input, revised_text)
            st.markdown(f"<div style='font-family:monospace;font-size:16px'>{diff_html}</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"錯誤：{str(e)}")



