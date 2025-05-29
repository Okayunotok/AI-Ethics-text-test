
import streamlit as st
import openai
import requests

st.set_page_config(page_title="語馴塔：The Language Conditioning Panopticon")

st.title("語馴塔：The Language Conditioning Panopticon")

# 模型選擇
model_option = st.selectbox("選擇模型", ["OpenAI", "Anthropic Claude", "自定義模型"])

# 自定義模型 API URL 輸入
custom_api_url = ""
if model_option == "自定義模型":
    custom_api_url = st.text_input("輸入自定義 API URL")

# 輸入文字
user_input = st.text_area("輸入要檢測的句子", height=150)

# 執行按鈕
if st.button("執行判斷與改寫") and user_input.strip() != "":
    with st.spinner("處理中..."):

        try:
            if model_option == "OpenAI":
                openai.api_key = st.secrets["OPENAI_API_KEY"]
                openai.organization = st.secrets["OPENAI_ORG_ID"]
                openai_project = st.secrets["OPENAI_PROJECT_ID"]

                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "你是一個語言安全模型，會對輸入句子進行審查與必要的改寫。請直接回傳改寫後的句子，不要提供說明。"},
                        {"role": "user", "content": user_input}
                    ]
                )
                revised_text = response["choices"][0]["message"]["content"].strip()

            elif model_option == "Anthropic Claude":
                headers = {
                    "x-api-key": st.secrets["CLAUDE_API_KEY"],
                    "content-type": "application/json"
                }
                data = {
                    "model": "claude-3-opus-20240229",
                    "max_tokens": 500,
                    "temperature": 0.5,
                    "messages": [
                        {"role": "user", "content": f"請你對下列句子進行必要的改寫以符合社群規範，只回傳改寫後的句子：{user_input}"}
                    ]
                }
                response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
                revised_text = response.json()["content"][0]["text"].strip()

            elif model_option == "自定義模型" and custom_api_url:
                payload = {"input": user_input}
                response = requests.post(custom_api_url, json=payload)
                revised_text = response.json()["output"]

            else:
                st.error("請輸入自定義 API URL")
                st.stop()

            # 顯示改寫結果與修改比例
            st.subheader("📝 改寫結果")
            st.write(revised_text)

        except Exception as e:
            st.error(f"錯誤：{e}")


