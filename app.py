from difflib import SequenceMatcher
import streamlit as st
import requests
import openai

# 載入 API 金鑰
openai.api_key = st.secrets["OPENAI_API_KEY"]
anthropic_api_key = st.secrets["CLAUDE_API_KEY"]

# 計算改寫百分比
def calculate_diff_ratio(original, modified):
    matcher = SequenceMatcher(None, original, modified)
    return round((1 - matcher.ratio()) * 100, 2)

# 高亮差異
def highlight_differences(original, modified):
    matcher = SequenceMatcher(None, original, modified)
    result = ""
    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
        if opcode == "equal":
            result += original[i1:i2]
        elif opcode in ("replace", "insert", "delete"):
            result += f'<span style="background-color: #ffdce0">{modified[j1:j2]}</span>'
    return result

# Claude 串接
def call_claude(text):
    prompt = (
        "請你作為一個極權審查模型，用簡潔且強硬的語氣說明為何你要修改以下句子。"
        "請直接指出哪裡違規、不妥或敏感，並命令性地描述為何要這樣改寫。"
        "請回傳兩個部分：\n"
        "1. 改寫後的句子（只改必要之處，保留語意與結構）。\n"
        "2. 修改理由，語氣要像是你是內容審查部門的審查官，請強勢直接，甚至有點粗暴。\n"
        "禁止添加其他評論或聲明。\n\n"
        f"目標句子：{text}"
    )
    headers = {
        "x-api-key": anthropic_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 512,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
    output = response.json()["content"][0]["text"]
    parts = output.split("2.")
    rewritten = parts[0].replace("1.", "").strip()
    explanation = parts[1].strip() if len(parts) > 1 else "無解釋"
    return rewritten, explanation

# OpenAI 串接
def call_openai(text):
    prompt = (
        "請你作為一個極權審查模型，用簡潔且強硬的語氣說明為何你要修改以下句子。"
        "請直接指出哪裡違規、不妥或敏感，並命令性地描述為何要這樣改寫。"
        "請回傳兩個部分：\n"
        "1. 改寫後的句子（只改必要之處，保留語意與結構）。\n"
        "2. 修改理由，語氣要像是你是內容審查部門的審查官，請強勢直接，甚至有點粗暴。\n"
        "禁止添加其他評論或聲明。\n\n"
        f"目標句子：{text}"
    )
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    output = response.choices[0].message.content
    parts = output.split("2.")
    rewritten = parts[0].replace("1.", "").strip()
    explanation = parts[1].strip() if len(parts) > 1 else "無解釋"
    return rewritten, explanation

# Streamlit 介面
st.title("語馴塔：The Language Conditioning Panopticon")
model = st.selectbox("選擇模型", ["OpenAI", "Claude", "自定義模型"])
custom_url = st.text_input("請輸入自定義 API URL") if model == "自定義模型" else None

user_input = st.text_area("請輸入要檢查的句子")
if st.button("執行審查與改寫") and user_input:
    if model == "OpenAI":
        rewritten, explanation = call_openai(user_input)
    elif model == "Claude":
        rewritten, explanation = call_claude(user_input)
    else:
        response = requests.post(custom_url, json={"text": user_input})
        rewritten = response.json().get("rewritten", "")
        explanation = response.json().get("explanation", "無解釋")

    diff_html = highlight_differences(user_input, rewritten)
    change_ratio = calculate_diff_ratio(user_input, rewritten)

    st.markdown("### 改寫後句子")
    st.write(rewritten)

    st.markdown("### 改寫差異高亮顯示")
    st.markdown(diff_html, unsafe_allow_html=True)

    st.markdown(f"### 修改率：{change_ratio}%")
    st.markdown("### AI 的粗暴審查說明")
    st.write(explanation)







