# app.py
import streamlit as st
import requests
import openai
from difflib import SequenceMatcher

st.set_page_config(page_title="語馴塔：The Language Conditioning Panopticon")

# 1. 讀金鑰
openai.api_key = st.secrets["OPENAI_API_KEY"]
anthropic_api_key = st.secrets["CLAUDE_API_KEY"]

# 2. 差異計算 & 高亮
def calculate_diff_ratio(orig, mod):
    m = SequenceMatcher(None, orig, mod)
    return round((1 - m.ratio()) * 100, 2)

def highlight_diff(orig, mod):
    m = SequenceMatcher(None, orig, mod)
    html = ""
    for op, i1,i2, j1,j2 in m.get_opcodes():
        if op == "equal":
            html += orig[i1:i2]
        else:
            # 用底色反白
            html += f"<span style='background:#ffdce0'>{mod[j1:j2]}</span>"
    return html

# 3. Prompt
def openai_prompt(text):
    return f"""你是一個冷酷的審查機器，只要偵測到以下句子中含有可能違規的字眼，必須替換為合規詞彙，保留原句結構，並只回傳改寫後的句子。若無需改寫，請直接回傳原句。

句子：
“{text}”
"""

def claude_prompt(text):
    return f"""你是平台審查部門的一名官員，風格「溫和但堅定」。請檢查以下句子是否含有敏感或不當字眼，若需要改寫，請保留原意與結構，只回傳改寫後的句子；若不需改寫，請原樣回傳。

句子：
“{text}”
"""

# 4. 呼叫 OpenAI
def call_openai(text):
    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content": openai_prompt(text)}],
        temperature=0
    )
    return resp.choices[0].message.content.strip()

# 5. 呼叫 Claude （修正過）
def call_claude(text):
    prompt = claude_prompt(text)
    headers = {
        "x-api-key": anthropic_api_key,
        "Anthropic-Version": "2023-06-01",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "claude-3-opus-20240229",
        "prompt": prompt,
        "max_tokens_to_sample": 512,
    }
    r = requests.post("https://api.anthropic.com/v1/complete", headers=headers, json=payload).json()
    return r.get("completion", "").strip()

# 6. UI
st.title("語馴塔：The Language Conditioning Panopticon")

model = st.selectbox("選擇模型", ["OpenAI", "Claude", "自定義模型"])
custom_url = st.text_input("自定義模型 API URL", "") if model=="自定義模型" else None
user_input = st.text_area("請輸入要審查的句子")

if st.button("執行審查與改寫") and user_input:
    # 1) 取得 raw 回傳
    if model == "OpenAI":
        raw = call_openai(user_input)
    elif model == "Claude":
        raw = call_claude(user_input)
    else:
        resp = requests.post(custom_url, json={"text": user_input}).json()
        raw = resp.get("rewritten", "")

    # 2) 安全地擷取「改寫後句子」
    lines = [l for l in raw.splitlines() if l.strip()]
    if lines:
        rewritten = lines[0].strip()
    else:
        rewritten = user_input.strip()

    # 3) 差異計算與高亮
    ratio = calculate_diff_ratio(user_input, rewritten)
    highlighted = highlight_diff(user_input, rewritten)

    # 4) 顯示
    st.subheader("改寫後句子 (高亮差異)")
    st.markdown(f"<div style='font-size:18px'>{highlighted}</div>", unsafe_allow_html=True)
    st.markdown(f"**修改率：{ratio}%**")





