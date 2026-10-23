# PaperReader 特色海報

對象：教授、研究生與大學生。繁體中文，16:9 橫式。

- `PaperReader_特色海報_16x9_4K.png`：3840 × 2160 正式圖檔。
- `PaperReader_特色海報_16x9_預覽.jpg`：1920 × 1080 預覽圖檔。
- `create_poster.py`：可修改文案、配色與版面的繪製原始碼。
- `PaperReader_GitHub展示圖_2x1.png`：1600 × 800，為 GitHub README 重新排版的 2:1 展示圖；點擊 README 中的展示圖可開啟網站。
- `create_github_banner.py`：GitHub 展示圖的繪製原始碼，執行 `python docs/poster/create_github_banner.py` 可重製。沿用海報配色與功能示意，精簡小字與頁尾，保留四項特色。

主題為「把論文讀成自己的知識」，沿用軟體的森林綠與米白配色。右側是功能示意，非操作介面截圖。四項特色根據本專案 README 及交接文件中的已實作功能整理：

1. PDF 四色標記、框選截圖便條，以及便條與原文的雙向定位。
2. AI 段落翻譯、全文摘要與關聯摘要；原文、AI 整理與筆記分開保存。
3. 跨 PDF 白板便條、人工連線與研究觀點整理。
4. 瀏覽器本機儲存、完整載入快取後離線閱讀，以及研究封裝備份。

網站與 QR Code 皆指向 <https://educatres.github.io/PaperReader/>。頁尾說明 AI 需連網、自備 API 金鑰且依供應商計費。

本次圖片服務的憑證驗證未通過，成品改用 Pillow 精準繪製與文字排版，不是 AI 生成圖。繪製需要 Python、Pillow、qrcode 及本機的 Noto Sans TC 字型；在專案目錄執行 `python docs/poster/create_poster.py` 即可重製。
