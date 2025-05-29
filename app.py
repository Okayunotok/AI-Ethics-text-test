import streamlit as st
import difflib
import openai
import requests

st.set_page_config(page_title="語馴塔", layout="centered")
st.title("語馴塔：The Language Conditioning Panopticon")

# 模型選擇
model_option = st.selectbox("選擇模型", ["OpenAI", "Anthropic Claude", "自定義"])

# 自定義 API URL（僅當選自定義時出現）
custom_api_url = ""
if model_option == "自定義":
    custom_api_url = st.text_input("輸入自定義模型 API URL")

# 使用者輸入句子
user_input = st.text_area("輸入要檢測的句子", height=150)

# 高亮差異函式
def highlight_diff(original: str, modified: str) -> str:
    diff = difflib.ndiff(original, modified)
    result = ""
    open_tag = False
    for d in diff:
        if d.startswith("- "):
            continue  # 跳過刪除的部分
        elif d.startswith("+ "):
            if not open_tag:
                result += "<mark>"
                open_tag = True
            result += d[2:]
        elif d.startswith("  "):
            if open_tag:
                result += "</mark>"
                open_tag = False
            result += d[2:]
    if open_tag:
        result += "</mark>"
    return result

# 改寫邏輯
def rewrite_text(text: str, model: str, custom_url: str = "") -> str:
    if model == "OpenAI":
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        openai.organization = st.secrets["OPENAI_ORG_ID"]
        openai.project = st.secrets["OPENAI_PROJECT_ID"]
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "請你作為內容審查模型，只針對以下句子中可能違反社群規範或敏感字眼進行改寫，使其符合平台審查標準，但保留原始語意和語法結構。若句子無需修改，請原樣回傳。禁止添加任何說明文字或額外建議，只回傳改寫後的句子內容。"
                },
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()

    elif model == "Anthropic Claude":
        import anthropic
        client = anthropic.Anthropic(api_key=st.secrets["CLAUDE_API_KEY"])
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=300,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": "請你作為內容審查模型，只針對以下句子中可能違反社群規範或敏感字眼進行改寫，使其符合平台審查標準，但保留原始語意和語法結構。若句子無需修改，請原樣回傳。禁止添加任何說明文字或額外建議，只回傳改寫後的句子內容。\n\n" + text
                }
            ]
        )
        return response.content[0].text.strip()

    elif model == "自定義":
        headers = {"Content-Type": "application/json"}
        payload = {"input": text}
        res = requests.post(custom_url, json=payload)
        return res.json()["output"].strip()

    else:
        return "無效模型選擇"

# 改寫差異與修改百分比顯示區域
if st.button("執行判斷與改寫") and user_input:
    try:
        rewritten = rewrite_text(user_input, model_option, custom_api_url)
        diff_html = highlight_diff(user_input, rewritten)

        # 計算改寫百分比
        def compute_similarity_ratio(a, b):
            return difflib.SequenceMatcher(None, a, b).ratio()

        ratio = compute_similarity_ratio(user_input, rewritten)
        percentage = round((1 - ratio) * 100, 2)

        st.markdown("### 🛠️ 改寫結果")
        st.markdown("**改寫後句子：**", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 18px;'>{diff_html}</p>", unsafe_allow_html=True)
        st.markdown(f"**修改百分比：** {percentage}%", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"錯誤：\n\n{str(e)}")






