# 01 · 整體架構概覽

## 目標

在現有的 `retrieval-system/` 後端之上，新增一個 **Streamlit 前端**，提供：

1. **互動式問答**：使用者逐筆輸入問題，即時顯示 LLM 回答（對話串形式）。
2. **批次推論**：上傳 CSV（欄位：`題目`），系統並行推論後下載含 `答案` 欄位的結果 CSV。

## 技術限制

| 項目 | 規格 |
|------|------|
| 前端框架 | Streamlit ≥ 1.35 |
| UI 風格 | Minimalist AI Interface（見 `plan.md`） |
| 自訂 CSS | `components/style.css` 透過 `st.markdown` 注入 |
| 後端呼叫 | 直接 import `retrieval-system/src/` 的模組 |
| 部署方式 | `streamlit run app.py`（本地）；Streamlit Community Cloud（雲端選項） |

## 新增檔案清單

```
retrieval-system/
├── app.py                    # Streamlit 入口
└── components/
    └── style.css             # 全域客製化 CSS
spec/
├── 01_overview.md            # 本文件
├── 02_ui_design.md           # UI 設計規格
├── 03_interactive_qa.md      # 互動式問答實作
├── 04_batch_inference.md     # 批次推論實作
└── 05_deployment.md          # 部署步驟
```

## 相依套件（新增至 requirements.txt）

```
streamlit>=1.35
```

> `pandas`、`openai`、`python-dotenv` 已存在，無需重複新增。
