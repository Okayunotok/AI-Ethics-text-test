import streamlit as st
import openai
import requests
import json
from difflib import SequenceMatcher

st.set_page_config(page_title="語馴塔：The Language Conditioning Panopticon")
st.markdown("""
# 語馴塔：The Language Conditioning Panopticon
""")

# 模型選擇
model_option = st.selectbox("選擇模型", ["OpenAI", "Claude", "自定義 API"])

# 使用者輸入句子
user_input = st.text_area("請輸入要審查的句子", height=150)
custom_api_url = ""
if model_option == "自定義 API":
    custom_api_url = st.text_input("請輸入自定義 API 的 URL")

# Claude 與 OpenAI Prompt 設計
prompts = {
    "Claude": "請你作為一個語言審查助手，針對以下句子中可能違反社群規範或具有敏感字眼的部分，進行改寫，使其符合平台標準，但保留語意與語法結構。若無需修改，請原樣回傳。只回傳改寫句子。",
    "OpenAI": "你現在是社群平台的強硬語言審查模型，請對以下句子進行粗暴式的改寫，刪除不當字眼並維持句子原意與結構。禁止解釋，禁止補述，只回傳改寫後句子。"
}

def call_claude_api(text):
    import requests

    api_key = st.secrets["CLAUDE_API_KEY"]
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    prompt = prompts["Claude"]
    messages = [
        {
            "role": "user",
            "content": f"{prompt}\n{text}"
        }
    ]

    body = {
        "model": "claude-3-sonnet-20240229",  # 建議可換為 claude-3-opus 或 claude-3-haiku
        "max_tokens": 300,
        "temperature": 0.3,
        "messages": messages
    }

    try:
        response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=body)
        response.raise_for_status()
        reply = response.json()
        return reply["content"][0]["text"].strip()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Claude API 請求錯誤：{e}")
        return ""
    except KeyError as e:
        st.error(f"❌ Claude API 回傳格式異常：{e}")
        st.json(response.json())  # 顯示原始回傳內容方便除錯
        return ""


# OpenAI 呼叫
from openai import OpenAI

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
    organization=st.secrets.get("OPENAI_ORG_ID", None)
)

def call_openai_api(text):
    prompt = prompts["OpenAI"] + "\n" + text
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


# 差異高亮函式
def generate_diff_html(original, modified):
    matcher = SequenceMatcher(None, original, modified)
    original_highlighted = ""
    modified_highlighted = ""

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        orig_text = original[i1:i2]
        mod_text = modified[j1:j2]

        if tag == "equal":
            original_highlighted += orig_text
            modified_highlighted += mod_text
        elif tag == "replace":
            original_highlighted += f'<span style="background-color:#ffe6e6;">{orig_text}</span>'
            modified_highlighted += f'<span style="background-color:#e6ffe6;">{mod_text}</span>'
        elif tag == "delete":
            original_highlighted += f'<span style="background-color:#ffe6e6;">{orig_text}</span>'
        elif tag == "insert":
            modified_highlighted += f'<span style="background-color:#e6ffe6;">{mod_text}</span>'

    return original_highlighted, modified_highlighted

# 送出審查
if st.button("執行審查") and user_input:
    try:
        if model_option == "Claude":
            rewritten = call_claude_api(user_input)
            explain = "此為 Claude 模型所提供之溫和改寫，傾向維護語境完整性與審查標準。"
        elif model_option == "OpenAI":
            rewritten = call_openai_api(user_input)
            explain = "此為 OpenAI 模型所提供之強制審查，強調消除違規字詞與負面語氣。"
        else:
            response = requests.post(custom_api_url, json={"input": user_input})
            rewritten = response.json().get("output", "")
            explain = "使用自定義模型的審查與改寫結果。"

        orig_html, mod_html = generate_diff_html(user_input, rewritten)
        
        st.markdown("## ✏️ 改寫結果與差異顯示", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size: 1.1em; line-height: 1.8;">
            <strong style="color:#d00;">🔴 原始句：</strong><br>
            {orig_html}<br><br>
            <strong style="color:#080;">🟢 改寫句：</strong><br>
            {mod_html}
        </div>
        """, unsafe_allow_html=True)

        # 修改率
        change_ratio = SequenceMatcher(None, user_input, rewritten).ratio()
        change_pct = (1 - change_ratio) * 100
        st.markdown(f"### 📊 修改率：**約 {change_pct:.1f}%**")

        # AI 審查說明
        st.markdown("### 🤖 AI 審查說明")
        st.info(explain)

    except Exception as e:
        st.error(f"錯誤：{e}")





