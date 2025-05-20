# app.py
import streamlit as st
import os
from openai import OpenAI

# 初始化 OpenAI client（支援 sk-proj + org + project）
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID"),
    project=os.getenv("OPENAI_PROJECT_ID")
)

# 網頁標題與說明
st.title("語氣分析模擬器（OpenAI v1+）")
st.write("請輸入一句話，我會分析其語氣（正向／負向／中性）並說明理由。")

# 使用者輸入
user_input = st.text_input("請輸入你的句子：")

if user_input:
    with st.spinner("分析中...請稍候"):
        try:
            # 給 GPT 的 prompt
            prompt = f"""
請判斷以下句子的語氣是「正向」「負向」還是「中性」，並簡要說明理由：
句子：{user_input}
回覆格式：
語氣：___
說明：___
"""

            # 呼叫 OpenAI Chat API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            # 顯示結果
            answer = response.choices[0].message.content
            st.success("分析結果：")
            st.write(answer)

        except Exception as e:
            st.error(f"發生錯誤：{e}")

