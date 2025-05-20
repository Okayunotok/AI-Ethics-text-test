# app.py
import streamlit as st
from openai import OpenAI
import os

# ✅ 設定 OpenAI API 金鑰
client = OpenAI(api_key="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
")

# 🖼️ 標題與說明
st.title("語氣分析模擬器")
st.write("請輸入你想在社群平台發表的話，我將使用模型分析")

# 📥 使用者輸入
user_input = st.text_input("輸入你的句子：")

# 🚀 GPT 語氣分析
if user_input:
    with st.spinner("AI 分析中，請稍候..."):
        prompt = f"""
請判斷以下句子的語氣是「正向」「負向」還是「中性」，並簡要說明理由。
句子：{user_input}
請用以下格式回覆：
語氣：＿＿＿
說明：＿＿＿
"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一位語氣分析助手"},
                    {"role": "user", "content": prompt}
                ]
            )
            result = response.choices[0].message.content
            st.success("分析結果：")
            st.write(result)

        except Exception as e:
            st.error(f"發生錯誤：{e}")
