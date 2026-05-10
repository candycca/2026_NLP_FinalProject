# 03 · 互動式問答實作規格

## 功能描述

使用者在底部固定的輸入欄打字送出問題，系統：
1. 立即將使用者訊息顯示在對話串（靠右氣泡）。
2. 以 **串流或一次性** 方式呼叫 LLM，回答顯示在左側氣泡。
3. 對話歷史保存在 `st.session_state`，重新整理前持續有效。

---

## Session State 結構

```python
# 初始化（於 app.py 頂層執行一次）
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 格式：[{"role": "user"|"assistant", "content": str}, ...]

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = build_system_prompt(DATA_DIR)
```

---

## 對話渲染邏輯

```python
# 顯示歷史訊息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
```

---

## 輸入與回答流程

```python
if user_input := st.chat_input("傳送訊息給 NLP 助手..."):
    # 1. 顯示使用者訊息
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. 呼叫 LLM
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            answer = ask(user_input, st.session_state.system_prompt)
        st.markdown(answer)

    # 3. 儲存回答
    st.session_state.messages.append({"role": "assistant", "content": answer})
```

> **注意**：`ask()` 使用同步 `openai.OpenAI`，在 Streamlit 中直接呼叫即可；
> 若未來需串流（`stream=True`），改用 `st.write_stream()`。

---

## 錯誤處理

| 情境 | 處理方式 |
|------|----------|
| `TWCC_API_KEY` 未設定 | `st.error("請先在 .env 中設定 TWCC_API_KEY")` 並 `st.stop()` |
| API 逾時 / 網路錯誤 | `try/except`，顯示 `st.warning("LLM 呼叫失敗，請稍後再試")` |
| 使用者輸入空字串 | `st.chat_input` 已內建防空送出，無需額外處理 |

---

## 清除對話按鈕

```python
if st.button("🗑 清除對話", key="clear_chat"):
    st.session_state.messages = []
    st.rerun()
```

位置：側邊欄（`st.sidebar`）或 Tab 頂部右側。

---

## 對應到現有模組

| 呼叫 | 來源檔案 |
|------|----------|
| `build_system_prompt(DATA_DIR)` | `retrieval-system/src/prompt_builder.py` |
| `ask(question, system_prompt)` | `retrieval-system/src/llm_client.py` |
