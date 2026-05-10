# 05 · 部署步驟

## 1. 本地啟動

### 前置條件

```bash
# 在 retrieval-system/ 目錄下
cp .env.example .env
# 編輯 .env，填入 TWCC_API_KEY
```

### 安裝套件

```bash
pip install -r requirements.txt
# requirements.txt 需包含 streamlit>=1.35
```

### 啟動

```bash
cd retrieval-system
streamlit run app.py
# 預設開啟 http://localhost:8501
```

---

## 2. Streamlit Community Cloud 部署（選項）

### 前置條件

- GitHub repo 公開或已授權 Streamlit Cloud 存取
- 帳號：[https://share.streamlit.io](https://share.streamlit.io)

### 步驟

1. **設定 Secrets**
   - 在 Streamlit Cloud Dashboard → App → Settings → Secrets，填入：
     ```toml
     TWCC_API_KEY = "你的-API-KEY"
     TWCC_API_URL = "https://api-ams.twcc.ai/api"
     TWCC_MODEL   = "llama3.3-ffm-70b-32k-chat"
     ```

2. **指定入口檔案**
   - Main file path：`retrieval-system/app.py`

3. **Python 版本**
   - 建議 `3.11`（與台智雲 SDK 相容）

4. **`requirements.txt` 路徑**
   - Streamlit Cloud 預設讀取 repo 根目錄的 `requirements.txt`；
     如入口在子目錄，需在 Streamlit Cloud 設定中指定
     `retrieval-system/requirements.txt`，或將套件清單移至根目錄。

---

## 3. 環境變數對照表

| 變數名稱 | 必填 | 預設值 | 說明 |
|----------|------|--------|------|
| `TWCC_API_KEY` | ✅ | — | 台智雲 AFS API 金鑰 |
| `TWCC_API_URL` | ❌ | `https://api-ams.twcc.ai/api` | API 基礎 URL |
| `TWCC_MODEL` | ❌ | `llama3.3-ffm-70b-16k-chat` | 使用的模型名稱 |
| `TWCC_TIMEOUT` | ❌ | `60` | 每次請求逾時秒數 |
| `TWCC_MAX_RETRY` | ❌ | `2` | 失敗自動重試次數 |
| `TWCC_MAX_CONCURRENT` | ❌ | `10` | 批次推論最大並行數 |

---

## 4. 目錄結構（最終）

```
retrieval-system/
├── app.py                    # Streamlit 入口（新增）
├── components/
│   └── style.css             # 客製化 CSS（新增）
├── main.py                   # 終端機互動式問答（保留）
├── batch_infer.py            # 終端機批次推論（保留）
├── src/
│   ├── llm_client.py
│   └── prompt_builder.py
├── data/
│   ├── NLP-Course-Info.csv
│   └── slides/
├── .env.example
└── requirements.txt          # 新增 streamlit>=1.35
```

---

## 5. 驗證清單

- [ ] `streamlit run app.py` 可成功啟動，無 import 錯誤
- [ ] 頁面背景為深黑色（`#0d0d0d`），標題置中顯示
- [ ] 互動式問答：輸入問題後顯示對話氣泡與 LLM 回答
- [ ] 批次推論：上傳 CSV 後顯示進度條，完成後可下載結果
- [ ] `.env` 未設定時顯示明確錯誤訊息
- [ ] 重新整理頁面後對話歷史清空（session_state 行為正確）
