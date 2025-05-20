# ✅ app.py — 支援 sk-proj 金鑰的語氣分析模擬器

import streamlit as st
from openai import OpenAI
import os

# 初始化 OpenAI 客戶端，使用環境變數讀取 sk-proj 金鑰
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID"),
    project=os.getenv("OPENAI_PROJECT_ID")
)

st.set_page_config(page_title="語氣分析模擬器（OpenAI v1+）")
st.title("語氣分析模擬器 （OpenAI v1+）")
st.write("請輸入一句話，我會分析其語氣（正向／負向／中性）並說明理由。")

user_input = st.text_input("輸入你的句子：", placeholder="例如：下雨天好討厭")

if user_input:
    with st.spinner("分析中...請稍候"):
        try:
            prompt = f"""
請判斷以下句子的語氣是「正向」、「負向」還是「中性」，並簡要說明理由：
句子：{user_input}
回覆格式：
語氣：<正向/負向/中性> 說明：<簡短說明>
"""
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            result = response.choices[0].message.content.strip()
            st.success("分析結果：")
            st.markdown(result)
        except Exception as e:
            st.error(f"發生錯誤：{e}")


