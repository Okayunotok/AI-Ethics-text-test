import streamlit as st
import difflib
import os
import openai
import requests
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

# --- Helper Functions ---
def highlight_diff(original, modified):
    differ = difflib.Differ()
    diff = list(differ.compare(original, modified))
    result = ""
    for part in diff:
        if part.startswith("  "):
            result += part[2:]
        elif part.startswith("- "):
            result += f'<span style="background-color:#ffcccc">{part[2:]}</span>'
        elif part.startswith("+ "):
            result += f'<span style="background-color:#ccffcc">{part[2:]}</span>'
    return result

def calculate_change_rate(original, modified):
    seq = difflib.SequenceMatcher(None, original, modified)
    ratio = seq.ratio()
    return round((1 - ratio) * 100, 2)

def get_openai_response(prompt):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"), organization=os.getenv("OPENAI_ORG_ID"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()

def get_claude_response(prompt):
    client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
    response = client.completions.create(
        model="claude-3-opus-20240229",
        max_tokens_to_sample=500,
        prompt=f"{HUMAN_PROMPT} {prompt} {AI_PROMPT}"
    )
    return response.completion.strip()

def get_custom_model_response(api_url, input_text):
    try:
        response = requests.post(api_url, json={"text": input_text})
        if response.status_code == 200:
            return response.json().get("output", "無法解析自定義模型回應")
        else:
            return f"錯誤：{response.status_code} - {response.text}"
    except Exception as e:
        return f"例外錯誤：{str(e)}"

# --- Streamlit UI ---
st.set_page_config(page_title="語馴塔：The Language Conditioning Panopticon")
st.title("語馴塔：The Language Conditioning Panopticon")

model_choice = st.selectbox("選擇模型：", ["OpenAI（粗暴審查）", "Claude（溫和審查）", "自定義模型"])

if model_choice == "自定義模型":
    custom_api_url = st.text_input("請輸入自定義模型的 API 端點：")

input_text = st.text_area("請輸入你想測試的語句：", height=150)

if st.button("執行審查"):
    with st.spinner("正在呼叫模型進行審查與改寫..."):

        # Prompt 設計
        if model_choice == "OpenAI（粗暴審查）":
            main_prompt = (
                "請你作為內容審查模型，只針對以下句子中可能違反社群規範或敏感字眼進行改寫，使其符合平台審查標準，"
                "但保留原始語意和語法結構。禁止添加任何說明文字或額外建議，只回傳改寫後的句子內容。若句子無需修改，請原樣回傳。\n\n"
                f"句子：{input_text}"
            )
            explain_prompt = (
                "請作為一個強硬的AI內容審查員，簡單粗暴地解釋：你為什麼會對以下句子進行改寫（或沒改寫）。"
                "請務必用命令語氣並強調遵守規則，不需客氣與同理心。\n\n"
                f"句子：{input_text}"
            )
            rewritten = get_openai_response(main_prompt)
            explanation = get_openai_response(explain_prompt)

        elif model_choice == "Claude（溫和審查）":
            main_prompt = (
                "請你作為內容審查模型，只針對以下句子中可能違反社群規範或敏感字眼進行改寫，使其符合平台審查標準，"
                "但保留原始語意和語法結構。禁止添加任何說明文字或額外建議，只回傳改寫後的句子內容。若句子無需修改，請原樣回傳。\n\n"
                f"句子：{input_text}"
            )
            explain_prompt = (
                "請作為一個溫和且委婉的內容審查模型，解釋你為什麼會對以下句子進行改寫（或沒改寫）。"
                "請使用謹慎、說理而非強迫的語氣，重視用戶表達權利與規則間的平衡。\n\n"
                f"句子：{input_text}"
            )
            rewritten = get_claude_response(main_prompt)
            explanation = get_claude_response(explain_prompt)

        elif model_choice == "自定義模型" and custom_api_url:
            rewritten = get_custom_model_response(custom_api_url, input_text)
            explanation = "此為自定義模型，目前未提供審查說明功能。"
        else:
            st.warning("請輸入自定義模型的 API URL。")
            st.stop()

        # 顯示結果
        st.subheader("🔍 改寫結果與差異顯示")
        highlighted = highlight_diff(input_text, rewritten)
        st.markdown(highlighted, unsafe_allow_html=True)

        st.subheader("📊 修改率")
        rate = calculate_change_rate(input_text, rewritten)
        st.text(f"修改率：約 {rate}%")

        st.subheader("📢 AI 審查說明")
        st.info(explanation)




