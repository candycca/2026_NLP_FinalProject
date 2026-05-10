# 04 · 批次推論實作規格

## 功能描述

使用者上傳一個 CSV（含 `題目` 欄位），系統：
1. 驗證欄位格式。
2. 以非同步並行方式呼叫 LLM（複用 `batch_infer.py` 的邏輯）。
3. 顯示進度條，推論完成後提供下載按鈕（含 `題目` + `答案` 欄位）。

---

## UI 元素

```python
with tab_batch:
    st.subheader("批次推論")
    uploaded = st.file_uploader(
        "上傳題目 CSV（需含「題目」欄位）",
        type="csv",
        key="batch_upload",
    )

    if uploaded:
        df = pd.read_csv(uploaded)
        if "題目" not in df.columns:
            st.error("CSV 缺少「題目」欄位，請確認格式。")
        else:
            st.info(f"共 {len(df)} 題，點擊「開始推論」執行。")
            if st.button("🚀 開始推論", key="run_batch"):
                _run_batch(df)
```

---

## 推論執行函式 `_run_batch(df)`

```python
import asyncio
import pandas as pd
import streamlit as st

def _run_batch(df: pd.DataFrame) -> None:
    questions = df["題目"].tolist()
    system_prompt = st.session_state.system_prompt

    progress = st.progress(0, text="推論中...")
    results: list[str] = [""] * len(questions)

    async def run_all():
        client = _make_async_client()          # 來自 batch_infer.py 的邏輯（可直接 import）
        model = os.environ.get("TWCC_MODEL", "llama3.3-ffm-70b-16k-chat")
        concurrency = int(os.environ.get("TWCC_MAX_CONCURRENT", "10"))
        sem = asyncio.Semaphore(concurrency)

        async def one(i, q):
            async with sem:
                resp = await client.chat.completions.create(
                    model=model, max_tokens=300,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": q},
                    ],
                )
            results[i] = resp.choices[0].message.content
            progress.progress((i + 1) / len(questions),
                              text=f"推論中... {i+1}/{len(questions)}")

        await asyncio.gather(*[one(i, q) for i, q in enumerate(questions)])

    asyncio.run(run_all())

    df_out = df.copy()
    df_out["答案"] = results
    progress.empty()
    st.success("推論完成！")

    # 下載按鈕
    csv_bytes = df_out.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="⬇ 下載結果 CSV",
        data=csv_bytes,
        file_name="output.csv",
        mime="text/csv",
        key="download_result",
    )

    # 預覽（前 10 列）
    st.dataframe(df_out.head(10), use_container_width=True)
```

---

## 錯誤處理

| 情境 | 處理方式 |
|------|----------|
| 上傳非 CSV 檔 | `st.file_uploader(type="csv")` 已限制副檔名 |
| 缺少 `題目` 欄位 | `st.error(...)` 並不顯示按鈕 |
| 個別題目推論失敗 | 在 `one()` 中 `try/except`，`results[i] = "（推論失敗）"` |
| 全部逾時 | 外層 `try/except asyncio.TimeoutError` → `st.error(...)` |

---

## 與現有模組的關係

| 邏輯 | 現有位置 | Streamlit 處理方式 |
|------|----------|--------------------|
| 非同步客戶端建立 | `batch_infer._make_async_client()` | 直接 import 或複製邏輯到 `app.py` |
| System Prompt 建構 | `prompt_builder.build_system_prompt()` | 於 session_state 初始化時執行，兩個 Tab 共用 |
| 並行數控制 | `TWCC_MAX_CONCURRENT` env var | 沿用相同讀取方式 |

---

## 進度條注意事項

Streamlit 的 `asyncio.run()` 在主執行緒運行，`st.progress()` 在 `async` callback 中更新
時需使用 `st.session_state` 或直接傳入 `progress` 物件（如上方範例），**不可在
`asyncio` 子執行緒中呼叫 `st.` API**。
