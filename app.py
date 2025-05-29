import streamlit as st
import difflib
import requests
import openai
import os

# 載入 API 金鑰與設定
openai.api_key = st.secrets["OPENAI_API_KEY"]
openai.organization = st.secrets["OPENAI_ORG_ID"]
openai_project_id = st.secrets["OPENAI_PROJECT_ID"]

# Claude API 金鑰
claude_api_key = st.secrets["CLAUDE_API_KEY"]

# 模型選單
st.title("語馴塔：The Language Conditioning Panopticon")
model_choice = st.selectbox("選擇模型", ["OpenAI", "Anthropic Claude", "自定義"])

# 輸入欄位
user_input = st.text_area("輸入要檢測的句子")

# 若選擇自定義模型，顯示自定義 URL 欄位
custom_url = ""
if model_choice == "自定義":
    custom_url = st.text_input("請輸入自定義 API URL")

# 按鈕觸發
if st.button("執行判斷與改寫") and user_input.strip():

    def rewrite_with_openai(text):
        prompt = f"請改寫以下句子，使其更符合社群平台規範：\n{text}"
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()

    def rewrite_with_claude(text):
        headers = {
            "x-api-key": claude_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1024,
            "temperature": 0,
            "messages": [
                {"role": "user", "content": f"請改寫以下句子，使其更符合社群平台規範：\n{text}"}
            ]
        }
        res = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
        return res.json()["content"][0]["text"].strip()

    def rewrite_with_custom(url, text):
        payload = {"text": text}
        res = requests.post(url, json=payload)
        return res.json()["rewrite"]

    # 選擇模型執行改寫
    try:
        if model_choice == "OpenAI":
            rewritten = rewrite_with_openai(user_input)
        elif model_choice == "Anthropic Claude":
            rewritten = rewrite_with_claude(user_input)
        elif model_choice == "自定義" and custom_url:
            rewritten = rewrite_with_custom(custom_url, user_input)
        else:
            st.warning("請輸入自定義模型的 API URL")
            st.stop()

        # 顯示改寫結果
        st.subheader("✏️ 改寫結果")
        st.success(rewritten)

        # 比對差異與修改率
        seq = difflib.SequenceMatcher(None, user_input, rewritten)
        diff = []
        for opcode, a0, a1, b0, b1 in seq.get_opcodes():
            if opcode == "equal":
                diff.append(user_input[a0:a1])
            elif opcode in ("replace", "insert", "delete"):
                diff.append(f"🟡{rewritten[b0:b1]}")

        diff_text = "".join(diff)
        percent = round((1 - seq.ratio()) * 100, 2)

        st.subheader("🔍 修改百分比")
        st.markdown(f"修改百分比：**{percent}%**")

    except Exception as e:
        st.error(f"錯誤：{e}")



