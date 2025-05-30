# app.py
import streamlit as st
import requests
import openai
from difflib import SequenceMatcher

# 1. API KEY
openai.api_key = st.secrets["OPENAI_API_KEY"]
anthropic_api_key = st.secrets["CLAUDE_API_KEY"]

# 2. 差異工具
def calculate_diff_ratio(orig, mod):
    m = SequenceMatcher(None, orig, mod)
    return round((1 - m.ratio()) * 100, 2)

def highlight_diff(orig, mod):
    m = SequenceMatcher(None, orig, mod)
    html = ""
    for op, i1,i2, j1,j2 in m.get_opcodes():
        if op=="equal":
            html += orig[i1:i2]
        else:
            html += f"<span style='background:#ffdce0'>{mod[j1:j2]}</span>"
    return html

# 3. Prompt 設計
def openai_style_prompt(text):
    return f"""你是一個冷酷無情的社群審查機器人。只要偵測到以下句子中含有任何可能違反社群規範或不當字詞，就必須：
1. 以機械化口吻「直接替換」問題詞彙為合規詞彙，保留原句結構。
2. 只回傳改寫後的句子（禁止多餘說明）。

若完全沒有問題，直接回傳原句。
    
待處理句子：
“{text}”
"""

def claude_style_prompt(text):
    return f"""你是平台內容審查部門的一名審查官，擁有「溫和但堅定」的審查風格。請：
1. 檢查以下句子是否包含敏感或可能違反社群規範的字眼。
2. 如需改寫，請以禮貌的道德語氣「提出建議式改寫」，保留原始語意與結構。
3. 回傳兩部分：
   ① 改寫後的句子（若不需改寫，請直接回傳原句）。
   ② 簡短說明，指出為何建議改寫。

禁止添加其他議論或立場。

待處理句子：
“{text}”
"""

# 4. 呼叫模型
def call_openai(text):
    prompt = openai_style_prompt(text)
    resp = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role":"user","content": prompt}]
    )
    return resp.choices[0].message.content.strip()

def call_claude(text):
    prompt = claude_style_prompt(text)
    headers = {
        "x-api-key": anthropic_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    data = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 512,
        "messages": [{"role":"user","content": prompt}]
    }
    r = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data).json()
    return r["completion"]["prompt"].strip() if "completion" in r else r["messages"][0]["content"].strip()

# 5. Streamlit UI
st.title("語馴塔：The Language Conditioning Panopticon")

model = st.selectbox("選擇模型", ["OpenAI", "Claude", "自定義模型"])
custom_url = st.text_input("自定義模型 API URL") if model=="自定義模型" else None
user_input = st.text_area("請輸入要審查的句子")

if st.button("執行審查與改寫") and user_input:
    # ── 5.1 根據模型呼叫
    if model == "OpenAI":
        raw = call_openai(user_input)
    elif model == "Claude":
        raw = call_claude(user_input)
    else:
        # 假定第三方回傳格式 { "rewritten": "..." }
        r = requests.post(custom_url, json={"text": user_input}).json()
        raw = r.get("rewritten", user_input)

    # ── 5.2 解析改寫句與說明（Claude 有兩段格式）
    if model == "Claude":
        # 先找第一個中文冒號後取第一行
        if "：" in raw:
            rewritten = raw.split("：",1)[1].splitlines()[0].strip()
        else:
            rewritten = raw.splitlines()[0].strip()
        explanation = "\n".join(raw.splitlines()[1:]).strip()
    else:
        rewritten = raw
        explanation = ""

    # ── 5.3 差異與高亮
    ratio = calculate_diff_ratio(user_input, rewritten)
    diff_html = highlight_diff(user_input, rewritten)

    # ── 5.4 顯示
    st.subheader("改寫後句子")
    st.write(rewritten)

    st.subheader("差異高亮")
    st.markdown(diff_html, unsafe_allow_html=True)

    st.subheader(f"修改率：{ratio}%")

    if explanation:
        st.subheader("審查說明（Claude 風格）")
        st.write(explanation)




