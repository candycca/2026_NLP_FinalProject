"""
NLP 課程問答系統 — Streamlit 前端
用法：
    cd retrieval-system
    streamlit run app.py
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import openai
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# ── 路徑設定 ─────────────────────────────────────────────────────────────────
_BASE = Path(__file__).parent.resolve()
sys.path.insert(0, str(_BASE / "src"))

from llm_client import ask  # noqa: E402  (after sys.path)
from prompt_builder import build_system_prompt  # noqa: E402
from batch_infer import _process_all_gemini

# ── 環境變數 ──────────────────────────────────────────────────────────────────
load_dotenv(_BASE / ".env")

# 修正 Streamlit 環境下 google-genai 可能出現的 proxies 參數錯誤
for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"]:
    if key in os.environ:
        del os.environ[key]



DATA_DIR = str(_BASE / "data")
CSS_PATH = _BASE / "components" / "style.css"

# ─────────────────────────────────────────────────────────────────────────────
# 頁面設定（必須是第一個 Streamlit 呼叫）
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NLP 課程問答系統",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 注入自訂 CSS ───────────────────────────────────────────────────────────────
if CSS_PATH.exists():
    st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>",
                unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Session State 初始化
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="載入課程資料中…")
def _load_system_prompt() -> str:
    return build_system_prompt(DATA_DIR)


def _init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages: list[dict] = []
    if "system_prompt" not in st.session_state:
        try:
            st.session_state.system_prompt = _load_system_prompt()
        except Exception as exc:
            st.session_state.system_prompt = None
            st.session_state.load_error = str(exc)


_init_state()

# ─────────────────────────────────────────────────────────────────────────────
# API Key 檢查
# ─────────────────────────────────────────────────────────────────────────────
if not os.environ.get("GEMINI_API_KEY"):
    st.error(
        "⚠️ **GEMINI_API_KEY 未設定。**\n\n"
        "請複製 `.env.example` 為 `.env` 並填入你的 API 金鑰後重新啟動。"
    )
    st.stop()

if st.session_state.get("load_error"):
    st.error(f"⚠️ 課程資料載入失敗：{st.session_state.load_error}")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# 標題區
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="header-container">'
    '<h1 class="app-title">NLP 課程問答系統</h1>'
    '<p class="app-subtitle">針對課程內容提問，或詢問 NLP 學術知識</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────────────────────────────────────
tab_qa, tab_batch = st.tabs(["💬 互動式問答", "📂 批次推論"])

# ── 自訂 HTML 氣泡渲染 ─────────────────────────────────────────────────────────────────────────────────
def _bubble_html(messages: list[dict]) -> str:
    """將對話紀錄轉換成自訂 HTML 氣泡清單。"""
    import html as _html
    parts: list[str] = []
    for msg in messages:
        text = _html.escape(msg["content"]).replace("\n", "<br>")
        if msg["role"] == "user":
            parts.append(
                f'<div style="'
                f'display:flex;justify-content:flex-end;margin:10px 0;">'
                f'<div style="'
                f'background:#2c2c2e;color:#f0f0f0;'
                f'border-radius:22px;padding:16px 24px;'
                f'max-width:85%;font-size:1.08rem;line-height:1.7;'
                f'word-break:break-word;">'
                f'{text}</div></div>'
            )
        else:
            parts.append(
                f'<div style="'
                f'display:flex;justify-content:flex-start;margin:10px 0;">'
                f'<div style="'
                f'background:#1e1e1e;color:#e8e8e8;'
                f'border-radius:18px;padding:16px 24px;'
                f'max-width:85%;font-size:1.05rem;line-height:1.7;'
                f'word-break:break-word;">'
                f'{text}</div></div>'
            )
    return "\n".join(parts)


# ══════════════════════════════════════════════════════════════════════════════
with tab_qa:
    # 對話顯示區（自訂 HTML，避免 Streamlit flex 限制）
    chat_area = st.empty()
    chat_area.markdown(
        f'<div id="chat-history" style="padding-bottom:20px">{_bubble_html(st.session_state.messages)}</div>',
        unsafe_allow_html=True,
    )

    # 輸入欄
    if user_input := st.chat_input("傳送訊息給 NLP 助手...", key="chat_input"):
        # 儲存使用者訊息並立刻更新畫面
        st.session_state.messages.append({"role": "user", "content": user_input})
        chat_area.markdown(
            f'<div id="chat-history" style="padding-bottom:20px">{_bubble_html(st.session_state.messages)}</div>',
            unsafe_allow_html=True,
        )

        # 呼叫 LLM
        with st.spinner("思考中…"):
            try:
                answer = ask(user_input, st.session_state.system_prompt)
            except openai.APITimeoutError:
                answer = "⚠️ 請求逾時，請稍後再試。"
            except openai.APIConnectionError:
                answer = "⚠️ 無法連線至 API，請確認網路與 API 設定。"
            except Exception as exc:
                answer = f"⚠️ 發生錯誤：{exc}"

        # 儲存助手回答並更新畫面
        st.session_state.messages.append({"role": "assistant", "content": answer})
        chat_area.markdown(
            f'<div id="chat-history" style="padding-bottom:20px">{_bubble_html(st.session_state.messages)}</div>',
            unsafe_allow_html=True,
        )
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# Tab 2 — 批次推論
# ══════════════════════════════════════════════════════════════════════════════

def _get_gemini_client():
    """建立 Gemini 客戶端。"""
    from google import genai
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def _run_batch(df: pd.DataFrame) -> None:
    """執行批次推論並在頁面上顯示進度與結果。"""
    questions: list[str] = df["題目"].tolist()
    system_prompt: str = st.session_state.system_prompt
    model = os.environ.get("GEMINI_MODEL", "gemini-3-pro-preview")
    concurrency = int(os.environ.get("GEMINI_MAX_CONCURRENT", "10"))

    results: list[str] = [""] * len(questions)
    progress_bar = st.progress(0, text=f"推論中… 0 / {len(questions)}")

    async def _run_all() -> None:
        from google.genai import types
        client = _get_gemini_client()
        sem = asyncio.Semaphore(concurrency)

        async def _one(i: int, q: str) -> None:
            async with sem:
                try:
                    # 使用 Gemini 非同步介面
                    resp = await client.aio.models.generate_content(
                        model=model,
                        contents=q,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            max_output_tokens=1024,
                        ),
                    )
                    results[i] = resp.text or "（無內容）"
                except Exception as exc:
                    results[i] = f"（推論失敗：{exc}）"
            progress_bar.progress(
                (i + 1) / len(questions),
                text=f"推論中… {i + 1} / {len(questions)}",
            )

        await asyncio.gather(*[_one(i, q) for i, q in enumerate(questions)])

    try:
        asyncio.run(_run_all())
    except Exception as exc:
        progress_bar.empty()
        st.error(f"批次推論中止：{exc}")
        return

    progress_bar.empty()
    st.success(f"✅ 推論完成，共 {len(questions)} 題。")

    df_out = df.copy()
    df_out["答案"] = results

    # 下載按鈕
    csv_bytes = df_out.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="⬇ 下載結果 CSV",
        data=csv_bytes,
        file_name="output.csv",
        mime="text/csv",
        key="download_result",
    )

    # 結果預覽
    st.markdown("#### 結果預覽（前 10 列）")
    st.dataframe(df_out.head(10), use_container_width=True)


with tab_batch:
    st.markdown(
        '上傳含有 <span style="background:#2a2a2a;color:#a8c7fa;'
        'border-radius:5px;padding:2px 8px;font-weight:500;">題目</span>'
        ' 欄位的 CSV，系統將自動並行推論並產出答案。',
        unsafe_allow_html=True,
    )


    def clear_batch_result():
        if "batch_result" in st.session_state:
            del st.session_state.batch_result

    uploaded = st.file_uploader(
        "選擇 CSV 檔案",
        type="csv",
        key="batch_upload",
        help="CSV 需包含「題目」欄位，每列一題",
        on_change=clear_batch_result
    )

    if uploaded is not None:
        try:
            df_input = pd.read_csv(uploaded)
        except Exception as exc:
            st.error(f"無法解析 CSV：{exc}")
            df_input = None

        if df_input is not None:
            if "題目" not in df_input.columns:
                st.error(
                    "❌ CSV 缺少「題目」欄位。\n\n"
                    "請確認 CSV 格式，欄位名稱需為「題目」。"
                )
            else:
                st.info(f"📋 共讀入 **{len(df_input)}** 題，點擊「開始推論」執行。")

                # 預覽上傳內容
                with st.expander("預覽上傳內容", expanded=False):
                    st.dataframe(df_input.head(5), use_container_width=True)

                if st.button("🚀 開始推論", key="run_batch", use_container_width=True):
                    import time
                    questions = df_input["題目"].tolist()
                    
                    results = []
                    chunk_size = int(os.environ.get("BATCH_SIZE", "15"))
                    
                    progress_bar = st.progress(0, text="準備推論...")
                    status_text = st.empty()
                    
                    for i in range(0, len(questions), chunk_size):
                        chunk = questions[i:i+chunk_size]
                        end_idx = min(i+chunk_size, len(questions))
                        
                        progress_bar.progress(i / len(questions), text=f"進度：{i} / {len(questions)}")
                        #status_text.info(f"⏳ 正在推論第 {i+1} ~ {end_idx} 題，請稍候...")
                        
                        # 處理此批次
                        chunk_results = asyncio.run(_process_all_gemini(chunk, st.session_state.system_prompt))
                        results.extend(chunk_results)
                        
                        progress_bar.progress(end_idx / len(questions), text=f"進度：{len(results)} / {len(questions)}")
                        
                        # 如果還有剩餘題目，進入 60 秒等待器
                        if end_idx < len(questions):
                            for wait_sec in range(60, 0, -1):
                                #status_text.warning(f"⚠️ 為遵守每分鐘 15 題限制，等待 {wait_sec} 秒後處理下一批...")
                                time.sleep(1)
                                
                    status_text.empty()
                    
                    df_out = df_input.copy()
                    df_out["答案"] = results
                    st.session_state.batch_result = df_out
                
                if "batch_result" in st.session_state:
                    df_out = st.session_state.batch_result
                    st.success(f"✅ 推論完成，共 {len(df_out)} 題。")
                    # 下載按鈕
                    csv_bytes = df_out.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
                    st.download_button(
                        label="⬇ 下載結果 CSV",
                        data=csv_bytes,
                        file_name="output.csv",
                        mime="text/csv",
                        key="download_result",
                    )

                    # 結果預覽
                    st.markdown("#### 結果預覽（前 10 列）")
                    st.dataframe(df_out.head(10), use_container_width=True)
