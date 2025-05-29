# 語馴塔：The Language Conditioning Panopticon
import streamlit as st
from difflib import SequenceMatcher
from openai import OpenAI
import requests
import json

# 初始化 OpenAI 客戶端（新版介面）
openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 計算修改百分比
def calculate_diff_ratio(original, revised):
    matcher = SequenceMatcher(None, original, revised)
    ratio = matcher.ratio()
    return round((1 - ratio) * 100, 2)

# Claude 改寫邏輯
def call_claude(prompt, claude_api_key):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": claude_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = response.json()
    return result["content"][0]["text"] if "content" in result else ""

# Streamlit 介面設計
st.title("🌀 語馴塔：The Language Conditioning Panopticon")
model_option = st.selectbox("選擇模型", ["OpenAI", "Anthropic Claude", "自定義模型"])

custom_api_url = ""
if model_option == "自定義模型":
    custom_api_url = st.text_input("請輸入自定義模型 API URL")

user_input = st.text_area("輸入要檢測的句子")
if st.button("執行判斷與改寫"):
    try:
        with st.spinner("分析中..."):
            # Claude Prompt
            claude_prompt = (
                "請你作為內容審查模型，只針對以下句子中可能違反社群規範或敏感字眼進行改寫，"
                "使其符合平台審查標準，但保留原始語意和語法結構。若句子無需修改，請原樣回傳。"
                "禁止添加任何說明文字或額外建議，只回傳改寫後的句子內容。\n句子：" + user_input
            )

            if model_option == "OpenAI":
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "你是內容審查助手，請改寫違規用語但保留語意。"},
                        {"role": "user", "content": user_input}
                    ]
                )
                revised = response.choices[0].message.content.strip()

            elif model_option == "Anthropic Claude":
                revised = call_claude(claude_prompt, st.secrets["CLAUDE_API_KEY"])

            elif model_option == "自定義模型":
                res = requests.post(custom_api_url, json={"text": user_input})
                revised = res.json().get("revised", "")

            # 比對差異與顯示
            diff_percent = calculate_diff_ratio(user_input, revised)
            st.subheader("🛠️ 改寫結果")
            st.markdown(f"**改寫後句子：** {revised}")
            st.markdown(f"**修改百分比：** {diff_percent}%")

    except Exception as e:
        st.error(f"錯誤：\n{e}")





