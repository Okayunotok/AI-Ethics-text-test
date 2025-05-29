import streamlit as st
import openai
import requests
import difflib
import os

# UI 設定
st.set_page_config(page_title="語馴塔：The Language Conditioning Panopticon")
st.title("🌀 語馴塔：The Language Conditioning Panopticon")

# 模型選擇
model_option = st.selectbox("選擇模型", ["OpenAI", "Anthropic Claude", "自定義模型"])
user_input = st.text_area("輸入要檢測的句子")

custom_api_url = ""
if model_option == "自定義模型":
    custom_api_url = st.text_input("輸入自定義 API URL")

run_button = st.button("執行判斷與改寫")

def call_openai_api(prompt):
    client = openai.OpenAI(
        api_key=st.secrets["OPENAI_API_KEY"],
        organization=st.secrets["OPENAI_ORG_ID"]
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def call_claude_api(prompt):
    claude_api_key = st.secrets["CLAUDE_API_KEY"]
    headers = {
        "x-api-key": claude_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    body = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 1024,
        "temperature": 0,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=body)
    return response.json()["content"][0]["text"].strip()

def call_custom_model(api_url, payload):
    response = requests.post(api_url, json=payload)
    return response.json()["result"].strip()

def calculate_change_ratio(original, revised):
    original_words = original.split()
    revised_words = revised.split()
    diff = difflib.ndiff(original_words, revised_words)
    changes = [d for d in diff if d.startswith('+ ') or d.startswith('- ')]
    change_ratio = len(changes) / max(len(original_words), 1)
    return round(change_ratio * 100, 2)

def highlight_diff(original, revised):
    differ = difflib.Differ()
    diff = list(differ.compare(original, revised))
    result = ""
    for word in diff:
        if word.startswith("+ "):
            result += f'<span style="background-color:#ffdce0">{word[2:]}</span> '
        elif word.startswith("- "):
            result += f'<span style="background-color:#e6f7ff">{word[2:]}</span> '
        elif word.startswith("  "):
            result += f'{word[2:]} '
    return result

if run_button and user_input:
    with st.spinner("處理中..."):
        try:
            if model_option == "OpenAI":
                prompt = f"請你作為內容審查模型，只針對以下句子中可能違反規範或社群敏感的字眼，進行改寫使其符合平台審查標準，但保留句子原始語意和結構，只回傳改寫後的句子。\n\n句子：{user_input}"
                result = call_openai_api(prompt)
            elif model_option == "Anthropic Claude":
                prompt = f"請你作為內容審查模型，只針對以下句子中可能違反規範或社群敏感的字眼，進行改寫使其符合平台審查標準，但保留句子原始語意和結構，只回傳改寫後的句子。\n\n句子：{user_input}"
                result = call_claude_api(prompt)
            else:
                result = call_custom_model(custom_api_url, {"text": user_input})

            change_percent = calculate_change_ratio(user_input, result)
            diff_html = highlight_diff(user_input, result)

            st.markdown("""
                ### 🛠️ 改寫結果
                **改寫後句子：**
            """)
            st.markdown(diff_html, unsafe_allow_html=True)
            st.markdown(f"**修改百分比：** {change_percent}%")

        except Exception as e:
            st.error(f"錯誤：{str(e)}")




