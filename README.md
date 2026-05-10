# NLP 課程問答系統 (Retrieval-System)

這是一個基於 Streamlit 開發的 NLP 課程專屬問答系統。系統結合了課程知識庫（CSV），並透過串接大語言模型 (Gemini API) 來回答學生的課程相關問題或是 NLP 學術知識。

## Live Demo: [https://2026nlpfinalproject.streamlit.app](https://2026nlpfinalproject.streamlit.app)

## 🌟 網頁功能

- **互動式問答 (Interactive QA)**：提供聊天介面，使用者可以直接輸入問題與 NLP 助手進行互動對話。
- **批次推論 (Batch Inference)**：支援上傳包含「題目」欄位的 CSV 檔案，系統會自動非同步、並行處理所有題目，並將答案產出為 CSV 提供下載。
- **智慧速率限制**：在批次處理時，系統實作了智慧限速機制（每分鐘最多 15 題），以遵守 API 速率限制（Rate Limit）並確保系統穩定性。

## 📝 使用說明

### 互動式問答
1. 切換至「💬 互動式問答」分頁。
2. 在下方輸入框輸入你對 NLP 課程的疑問（例如：「這堂課的期末專題要幹嘛？」、「什麼是馬可夫過程？」）。
3. 助手會根據載入的資料庫給予精確的回覆。

### 批次推論
1. 切換至「📂 批次推論」分頁。
2. 準備一個含有 **「題目」** 欄位的 CSV 檔案。範例如下 (`input.csv`)：
   | 題目 |
   | :--- |
   | 什麼是時間均勻的馬可夫過程？ |
   | HMM 的三個假設是什麼？ |
   | stemming和lemmatization有何不同? |
3. 將檔案上傳中。
4. 點擊「🚀 開始推論」。
5. 推論完成後，點擊「⬇ 下載結果 CSV」即可取得包含答案的檔案。



## 📂 目錄結構

```text
retrieval-system/
├── app.py                  # Streamlit 主程式介面
├── batch_infer.py          # 批次推論邏輯與非同步呼叫處理
├── main.py                 # (可選) 命令列執行腳本
├── requirements.txt        # Python 相依套件列表
├── components/
│   └── style.css           
├── src/
│   ├── llm_client.py       # 處理與 Gemini API 的連線與呼叫
└── └── prompt_builder.py   # 組合系統提示詞與知識庫資料

```

## 🚀 快速開始

### 1. 安裝環境依賴

請確保你已經安裝了 Python 3.9 以上版本。在 `retrieval-system` 目錄下執行：

```bash
pip install -r requirements.txt
```

### 2. 環境變數設定

複製專案中的環境變數範例檔：

```bash
cp .env.example .env
```

接著，使用文字編輯器打開 `.env` 檔案，填寫你的 Gemini API 金鑰及其他設定：

```env
# Gemini API Key (必填)
GEMINI_API_KEY="your_api_key_here"

# 使用的模型 (預設: gemini-3-pro-preview)
GEMINI_MODEL="gemini-3-pro-preview"

# 非同步最大並行數量
TWCC_MAX_CONCURRENT=10
```

### 3. 準備課程資料

確保 `data/` 目錄下已經有課程相關的 CSV 知識庫。系統會在啟動時自動讀取該目錄下的檔案，並將其作為 `system_prompt` 餵給模型。

### 4. 本地端啟動服務

在終端機執行以下指令啟動 Streamlit 伺服器：

```bash
cd retrieval-system
streamlit run app.py
```

伺服器啟動後，瀏覽器會自動開啟 `http://localhost:8501`。

