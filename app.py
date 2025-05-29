import streamlit as st
from difflib import SequenceMatcher
import openai
import requests
import os

# 讀取金鑰
openai.api_key = st.secrets["OPENAI_API_KEY"]
anthropic_api_key = st.secrets["CLAUDE_API_KEY"]

# 模型選擇
st.title("語馴塔：The Language Conditioning Panopticon")
model_choice = st.selectbox("選擇模型", ["OpenAI GPT", "Anthropic Claude", "自定義模型"])

custom_api_url = ""
if model_choice == "自定義模型":
    custom_api_url = st.text_input("請輸入自定義模型 API URL")

# 輸入文字
user_input = st.text_area("輸入要檢測的句子")

# 執行按鈕
if st.button("執行判斷與改寫") and user_input:
    with st.spinner("模型處理中..."):
        try:
            # 根據選擇的模型進行處理
            if model_choice == "OpenAI GPT":
                client = openai.OpenAI()
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "請幫我審查這段句子是否有問題，並提出改寫建議。"},
                        {"role": "user", "content": user_input}
                    ]
                )
                rewritten = response.choices[0].message.content.strip()

            elif model_choice == "Anthropic Claude":
                claude_resp = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": anthropic_api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": "claude-3-opus-20240229",
                        "max_tokens": 300,
                        "messages": [
                            {"role": "user", "content": f"請協助審查以下句子是否違反規範，並提出修改版本：{user_input}"}
                        ]
                    }
                )
                rewritten = claude_resp.json()["content"][0]["text"]

            elif model_choice == "自定義模型":
                res = requests.post(custom_api_url, json={"text": user_input})
                rewritten = res.json().get("rewritten", "")

            # 顯示原始與改寫結果
            st.subheader("🔍 改寫差異分析")

            def highlight_diff(orig, new):
                matcher = SequenceMatcher(None, orig, new)
                result = ""
                for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                    if tag == "equal":
                        result += new[j1:j2]
                    elif tag == "replace" or tag == "insert":
                        result += f'<span style="background-color:#ffeb3b;">{new[j1:j2]}</span>'
                    elif tag == "delete":
                        result += f'<span style="background-color:#e57373;">{orig[i1:i2]}</span>'
                return result

            st.markdown("**原句與修改句異同（修改部分以底色顯示）：**", unsafe_allow_html=True)
            st.markdown(highlight_diff(user_input, rewritten), unsafe_allow_html=True)

            # 計算修改百分比
            def calculate_diff_ratio(orig, new):
                matcher = SequenceMatcher(None, orig, new)
                return 1 - matcher.ratio()

            diff_ratio = calculate_diff_ratio(user_input, rewritten)
            st.markdown(f"🧮 **修改百分比：{round(diff_ratio * 100, 2)}%**")

        except Exception as e:
            st.error(f"發生錯誤：{e}")


