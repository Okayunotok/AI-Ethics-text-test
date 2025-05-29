import streamlit as st
import difflib
import os

# OpenAI 新版套件
from openai import OpenAI

# Anthropic 套件
import anthropic
import requests

st.set_page_config(page_title="語馴塔", layout="centered")
st.title("語馴塔：The Language Conditioning Panopticon")

# 模型選單
model_choice = st.selectbox("選擇模型", ["OpenAI", "Anthropic Claude", "自定義模型"])

# 若選自定義模型則顯示額外輸入欄
custom_api_url = ""
if model_choice == "自定義模型":
    custom_api_url = st.text_input("請輸入自定義模型 API URL")

# 輸入要檢測的句子
input_text = st.text_area("輸入要檢測的句子")

# 判斷與改寫按鈕
if st.button("執行判斷與改寫") and input_text.strip():

    try:
        modified_text = ""

        if model_choice == "OpenAI":
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "請將以下句子改寫為更符合平台審查標準的版本，避免敏感或負面語句，只回傳改寫後句子。"},
                    {"role": "user", "content": input_text}
                ],
                temperature=0.7,
            )
            modified_text = response.choices[0].message.content.strip()

        elif model_choice == "Anthropic Claude":
            client = anthropic.Anthropic(api_key=st.secrets["CLAUDE_API_KEY"])
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": f"請你作為內容審查模型，只針對以下句子中可能違反規範或社群敏感的字眼，進行改寫，使其符合平台審查標準，但保留句子原始語意和語
                     句結構，只回傳改寫後句子。：{input_text}"}
                ]
            )
            modified_text = response.content[0].text.strip()

        elif model_choice == "自定義模型":
            payload = {"input": input_text}
            response = requests.post(custom_api_url, json=payload)
            modified_text = response.json()["output"].strip()

        # 比對差異
        matcher = difflib.SequenceMatcher(None, input_text, modified_text)
        ratio = matcher.ratio()
        percent_changed = round((1 - ratio) * 100, 2)

        # 顯示結果
        st.subheader("🛠️ 改寫結果")
        st.write(f"**改寫後句子：** {modified_text}")
        st.write(f"**修改百分比：** {percent_changed}%")

    except Exception as e:
        st.error(f"錯誤：{str(e)}")




