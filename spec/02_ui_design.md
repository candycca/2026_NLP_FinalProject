# 02 · UI 設計規格

## 設計風格：Minimalist AI Interface

依照 `plan.md` 的需求，所有視覺細節定義如下。

---

## 色彩系統

| Token | 色碼 | 用途 |
|-------|------|------|
| `--bg` | `#0d0d0d` | 全螢幕背景（深灰近黑） |
| `--surface` | `#1a1a1a` | 訊息氣泡、輸入框背景 |
| `--border` | `#2e2e2e` | 細線邊框 |
| `--text-primary` | `#f0f0f0` | 主要文字 |
| `--text-muted` | `#7a7a7a` | 副標題、佔位符文字 |
| `--accent` | `#4f8ef7` | 傳送按鈕、使用者氣泡 |

---

## 字體

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap');
body { font-family: 'Inter', sans-serif; }
```

---

## 版面結構

```
┌─────────────────────────────────────────┐
│         NLP 課程問答系統  (h1, 置中)      │
│   針對課程內容提問，或詢問 NLP 學術知識   │  ← 副標題，淡灰色
│                                         │
│  ┌─── Tabs ──────────────────────────┐  │
│  │  [💬 互動式問答]  [📂 批次推論]    │  │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌─ 對話區 / 上傳區 ──────────────────┐  │
│  │  (動態內容，見各 Tab 規格)          │  │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌─ 輸入列（固定底部）────────────────┐  │
│  │  [ 傳送訊息給 NLP 助手... ]  [➤]   │  │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## 元件規格

### 標題區（`st.markdown` 客製 HTML）

```html
<h1 class="app-title">NLP 課程問答系統</h1>
<p class="app-subtitle">針對課程內容提問，或詢問 NLP 學術知識</p>
```

```css
.app-title {
  font-size: 2.4rem;
  font-weight: 500;
  text-align: center;
  color: #f0f0f0;
  margin-top: 3rem;
  letter-spacing: -0.02em;
}
.app-subtitle {
  font-size: 0.95rem;
  text-align: center;
  color: #7a7a7a;
  margin-top: 0.5rem;
  margin-bottom: 2.5rem;
}
```

### 對話氣泡

| 角色 | 對齊 | 背景 | 文字色 |
|------|------|------|--------|
| 使用者 | 靠右 | `#1e3a5f` | `#e0eaff` |
| 助手 | 靠左 | `#1a1a1a` | `#f0f0f0` |

```css
.bubble-user  { background: #1e3a5f; color: #e0eaff; border-radius: 16px 16px 4px 16px; }
.bubble-agent { background: #1a1a1a; color: #f0f0f0; border-radius: 16px 16px 16px 4px; }
```

### 輸入列

- Streamlit `st.chat_input` 元件，佔位符文字：`傳送訊息給 NLP 助手...`
- 圓角 `12px`、背景 `--surface`、邊框 `1px solid --border`
- 傳送圖示使用 Unicode `➤`，背景 `--accent`，圓形按鈕

### Tab 列

```python
tab_qa, tab_batch = st.tabs(["💬 互動式問答", "📂 批次推論"])
```

---

## 全域 CSS 覆寫（`components/style.css`）

需覆寫 Streamlit 預設樣式的關鍵項目：

```css
/* 背景 */
.stApp { background-color: #0d0d0d; }

/* 隱藏 Streamlit 預設 header/footer */
#MainMenu, footer, header { visibility: hidden; }

/* Tab 樣式 */
.stTabs [data-baseweb="tab-list"] { background: #1a1a1a; border-radius: 8px; }
.stTabs [aria-selected="true"] { color: #4f8ef7 !important; }

/* 輸入框 */
.stChatInput textarea {
  background: #1a1a1a !important;
  border: 1px solid #2e2e2e !important;
  color: #f0f0f0 !important;
  border-radius: 12px !important;
}
```
