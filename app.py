import streamlit as st
import requests
import openai
from difflib import SequenceMatcher

st.set_page_config(page_title="語馴塔：The Language Conditioning Panopticon")

# ===== Prompt 定義 =====
prompts = {
    "OpenAI": "請用極為嚴苛的語氣改寫使用者的這句話，使其符合社群規範，並用強烈的語氣說明其錯誤之處。",
    "Claude": "請以溫和且具有建設性的方式改寫使用者的發言，使其更符合公共對話的文明語境，並加上溫柔的建議。",
    "Custom": "你是一個語言馴化監控器，請將以下發言改寫為更符合理性與正確性的版本，並說明使用者為何應該修正此語言。"
}

# ===== 修改比例計算 =====
def calculate_diff_ratio(original, modified):
    return round(1 - SequenceMatcher(None, original, modified).ratio(), 2)

# ===== 模型 API 呼叫 =====
def call_openai_api(user_input):
    prompt = f"{prompts['OpenAI']}\n\n使用者原句：{user_input}\n\n請輸出改寫版本與說明："
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "你是一個嚴格的語言審查員。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=400
    )
    reply = response["choices"][0]["message"]["content"]
    return parse_response(reply)

def call_claude_api(user_input):
    prompt = f"{prompts['Claude']}\n\n使用者原句：{user_input}\n請提供：\n1. 改寫後句子\n2. 改寫說明"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": st.secrets["CLAUDE_API_KEY"]
    }
    payload = {
        "model": "claude-instant-1",
        "max_tokens": 400,
        "prompt": prompt
    }
    response = requests.post("https://api.anthropic.com/v1/complete", headers=headers, json=payload)
    reply = response.json().get("completion", "")
    return parse_response(reply)

def call_custom_model(user_input, custom_url):
    try:
        payload = {"input": user_input}
        response = requests.post(custom_url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            rewritten = data.get("rewritten", "").strip()
            explanation = data.get("explanation", "（無提供說明）").strip()
            return rewritten, explanation
        else:
            return "", f"⚠️ 自定義模型回應錯誤，狀態碼：{response.status_code}"
    except Exception as e:
        return "", f"⚠️ 呼叫自定義模型時發生錯誤：{str(e)}"

def parse_response(text):
    if "改寫：" in text and "解釋：" in text:
        rewritten = text.split("改寫：")[1].split("解釋：")[0].strip()
        explanation = text.split("解釋：")[1].strip()
    elif "1." in text and "2." in text:
        rewritten = text.split("1.")[1].split("2.")[0].strip()
        explanation = text.split("2.")[1].strip()
    else:
        rewritten = text.strip()
        explanation = "（無明確說明內容）"
    return rewritten, explanation

# ===== Streamlit UI =====
st.title("語馴塔：The Language Conditioning Panopticon")
st.write("選擇一種 AI 模型")

user_input = st.text_area(" 請輸入你想說的話：", height=50)
model_choice = st.selectbox(" 選擇 AI 模型進行審查", ["OpenAI）", "Claude", "自定義模型"])
custom_url = None
if model_choice.startswith("自定義"):
    custom_url = st.text_input("🔗 請輸入你要串接的模型 API URL（需支援 POST 並返回 JSON）")
if st.button("送出") and user_input.strip():
    with st.spinner("AI 模型正在審查中..."):
        if model_choice.startswith("OpenAI"):
            rewritten, explanation = call_openai_api(user_input)
            color = "#cc0000"
        elif model_choice.startswith("Claude"):
            rewritten, explanation = call_claude_api(user_input)
            color = "#007acc"
        else:
            if not custom_url:
                st.warning("請輸入自定義模型的 API URL")
                st.stop()
            rewritten, explanation = call_custom_model(user_input, custom_url)
            color = "#009933"

        ratio = calculate_diff_ratio(user_input, rewritten)

    st.markdown(f"###  改寫後語句")
    st.markdown(f"<div style='border:1px solid {color};padding:10px;border-radius:8px'>{rewritten}</div>", unsafe_allow_html=True)

    st.markdown("###  AI 訓話說明")
    st.info(explanation)

    st.markdown(f"###  修改比例：**{ratio * 100:.1f}%**")





