# app.py
import streamlit as st
from openai import OpenAI


client = OpenAI(api_key="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")



st.title("社群模擬器（OpenAI v1+）")
st.write("請輸入一句話，我會分析")


user_input = st.text_input("輸入你的句子：")

if user_input:
    with st.spinner("分析中...請稍候"):
        try:
            prompt = f"""
請判斷以下句子的語氣是「正向」「負向」還是「中性」，並簡要說明理由。
句子：{user_input}
回覆格式：
語氣：＿＿＿
說明：＿＿＿
"""

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
