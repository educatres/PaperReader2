"""Create the A3 landscape PaperReader feature poster with searchable vector text.

Uses existing, local tutorial screenshots. No AI service or browser credentials
are used. Run from any working directory with ReportLab and Pillow installed.
"""

from __future__ import annotations

import os
from pathlib import Path

from PIL import Image
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "pdf"
ASSETS = ROOT / "output" / "pdf" / "assets"
SCREENSHOTS = ROOT / ".guide-build" / "screenshots"
FONTS = Path(os.environ["LOCALAPPDATA"]) / "Microsoft" / "Windows" / "Fonts"
URL = "https://educatres.github.io/PaperReader/"
PDF = OUT / "PaperReader_特色介紹海報_A3橫式.pdf"

W, H = landscape(A3)
PAPER = "#FAFAF5"
GREEN = "#234C3D"
TEXT = "#294638"
MUTED = "#758071"
LINE = "#DDE2D5"
GOLD = "#D3B239"
PURPLE = "#896AAD"
M = 46


def color(value):
    return colors.HexColor(value)


for family, filename in [("TC", "NotoSansTC-Regular.ttf"),
                         ("TC-Medium", "NotoSansTC-Medium.ttf"),
                         ("TC-Bold", "NotoSansTC-Bold.ttf"),
                         ("TC-Black", "NotoSansTC-Black.ttf")]:
    pdfmetrics.registerFont(TTFont(family, str(FONTS / filename)))
pdfmetrics.registerFont(TTFont("Brand", "C:/Windows/Fonts/segoeuib.ttf"))
pdfmetrics.registerFont(TTFont("Latin", "C:/Windows/Fonts/segoeui.ttf"))


def text(x, top, value, size=12, fill=TEXT, font="TC", max_width=None):
    width = pdfmetrics.stringWidth(value, font, size)
    if max_width is not None and width > max_width + 0.1:
        raise ValueError(f"Text exceeds {max_width}: {value} ({width:.2f})")
    c.setFillColor(color(fill))
    c.setFont(font, size)
    c.drawString(x, H - top - size * 0.88, value)
    return width


def right_text(right, top, value, size=10, fill=MUTED, font="TC"):
    width = pdfmetrics.stringWidth(value, font, size)
    return text(right - width, top, value, size, fill, font)


def rect(x, top, width, height, fill=None, stroke=None, radius=0, lw=0.7):
    c.setLineWidth(lw)
    if fill:
        c.setFillColor(color(fill))
    if stroke:
        c.setStrokeColor(color(stroke))
    if radius:
        c.roundRect(x, H - top - height, width, height, radius,
                    fill=bool(fill), stroke=bool(stroke))
    else:
        c.rect(x, H - top - height, width, height,
               fill=bool(fill), stroke=bool(stroke))


def line(points, stroke=LINE, lw=0.7):
    c.setStrokeColor(color(stroke))
    c.setLineWidth(lw)
    c.setLineCap(1)
    c.setLineJoin(1)
    p = c.beginPath()
    p.moveTo(points[0][0], H - points[0][1])
    for x, y in points[1:]:
        p.lineTo(x, H - y)
    c.drawPath(p)


def circle(x, y, radius, fill=None, stroke=None, lw=0.7):
    if fill:
        c.setFillColor(color(fill))
    if stroke:
        c.setStrokeColor(color(stroke))
    c.setLineWidth(lw)
    c.circle(x, H - y, radius, fill=bool(fill), stroke=bool(stroke))


def arrow(points, stroke=GREEN, lw=1.2, head=4):
    line(points, stroke, lw)
    x, y = points[-1]
    px, py = points[-2]
    import math
    angle = math.atan2(y - py, x - px)
    line([(x - head * math.cos(angle - 0.6), y - head * math.sin(angle - 0.6)),
          (x, y),
          (x - head * math.cos(angle + 0.6), y - head * math.sin(angle + 0.6))],
         stroke, lw)


def pill(x, top, label, fill, ink, size=9.2, pad=9, height=23):
    width = pdfmetrics.stringWidth(label, "TC-Medium", size) + pad * 2
    rect(x, top, width, height, fill, radius=height / 2)
    text(x + pad, top + (height - size) / 2 - 1, label, size, ink, "TC-Medium")
    return width


def icon(name, x, top, stroke=GREEN, scale=1):
    c.saveState()
    c.translate(x, H - top)
    c.scale(scale, -scale)
    c.setStrokeColor(color(stroke))
    c.setLineWidth(1.5)
    c.setLineJoin(1)
    c.setLineCap(1)
    p = c.beginPath()
    if name == "highlight":
        pts = [(3, 18), (5, 11), (16, 0), (23, 7), (12, 18), (3, 18),
               (0, 23), (24, 23)]
        p.moveTo(*pts[0])
        for pt in pts[1:]:
            p.lineTo(*pt)
        p.moveTo(13, 3)
        p.lineTo(20, 10)
    elif name == "spark":
        for cx, cy, r in [(11, 13, 10), (23, 2, 4)]:
            pts = [(cx, cy-r), (cx+r*.25, cy-r*.25), (cx+r, cy),
                   (cx+r*.25, cy+r*.25), (cx, cy+r),
                   (cx-r*.25, cy+r*.25), (cx-r, cy),
                   (cx-r*.25, cy-r*.25), (cx, cy-r)]
            p.moveTo(*pts[0])
            for pt in pts[1:]:
                p.lineTo(*pt)
    elif name == "network":
        for a, b in [((4, 4), (12, 13)), ((23, 3), (12, 13)),
                     ((12, 13), (3, 24)), ((12, 13), (24, 23))]:
            p.moveTo(*a)
            p.lineTo(*b)
        for cx, cy in [(4, 4), (23, 3), (3, 24), (24, 23)]:
            c.setFillColor(color(PAPER))
            c.roundRect(cx-2.8, cy-2.8, 5.6, 5.6, 1, fill=1, stroke=1)
    elif name == "papers":
        for dx, dy in [(8, 0), (4, 4), (0, 8)]:
            pts = [(dx, dy), (dx+12, dy), (dx+18, dy+6),
                   (dx+18, dy+20), (dx, dy+20), (dx, dy)]
            p.moveTo(*pts[0])
            for pt in pts[1:]:
                p.lineTo(*pt)
            p.moveTo(dx+12, dy)
            p.lineTo(dx+12, dy+6)
            p.lineTo(dx+18, dy+6)
    elif name == "source":
        p.moveTo(3, 20)
        p.lineTo(20, 3)
        p.moveTo(9, 3)
        p.lineTo(20, 3)
        p.lineTo(20, 14)
    c.drawPath(p)
    c.restoreState()


def image_clipped(path, x, top, width, height, radius=0):
    c.saveState()
    p = c.beginPath()
    if radius:
        p.roundRect(x, H - top - height, width, height, radius)
    else:
        p.rect(x, H - top - height, width, height)
    c.clipPath(p, stroke=0)
    c.drawImage(ImageReader(str(path)), x, H - top - height,
                width=width, height=height, mask="auto")
    c.restoreState()


def mini_doc(x, top, label, accent):
    rect(x, top, 38, 28, "#FFFFFF", LINE, 4)
    rect(x + 5, top + 5, 3, 18, accent, radius=1)
    text(x + 12, top + 8, label, 9, GREEN, "Latin")


OUT.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)

# Screenshot crops preserve the application content. The poster labels the
# assembled view as excerpts and the captured AI response as a teaching example.
original = Image.open(SCREENSHOTS / "02-highlight.png").convert("RGB")
print("Highlight screenshot:", original.size)
original.crop((210, 325, 1570, 1515)).save(ASSETS / "pdf_highlight_crop.png")
note = Image.open(SCREENSHOTS / "07-note-ai.png").convert("RGB")
print("AI note screenshot:", note.size)
note.crop((5, 5, note.width - 5, note.height - 5)).save(ASSETS / "ai_note_crop.png")

c = canvas.Canvas(str(PDF), pagesize=(W, H), pageCompression=1)
c.setTitle("PaperReader｜把螢光標記，變成研究脈絡")
c.setAuthor("PaperReader")
c.setSubject("螢光成便條、逐張 AI 摘要與翻譯、關聯便條統整、跨文獻脈絡整理")
c.setCreator("PaperReader feature poster / ReportLab")

rect(0, 0, W, H, PAPER)

# Masthead.
rect(M, 38, 35, 35, GREEN, radius=10)
line([(57, 46), (65, 46), (72, 53), (72, 66), (57, 66), (57, 46)], "#FFFFFF", 1.1)
line([(65, 46), (65, 53), (72, 53)], "#FFFFFF", 1.1)
line([(60, 57), (68, 57)], "#FFFFFF", 1)
line([(60, 61), (66, 61)], "#FFFFFF", 1)
text(94, 36, "PaperReader", 28, GREEN, "Brand")
text(95, 71, "AI 輔助的文獻閱讀與知識白板", 9, MUTED, "TC-Medium")
right_text(W-M, 44, "文獻回顧  /  論文研究  /  跨篇統整", 10.8, GREEN, "TC-Medium")
right_text(W-M, 64, "讓每次閱讀，累積成自己的研究觀點", 9.3, MUTED)
line([(M, 99), (W-M, 99)], LINE, .8)

# Hero headline.
rect(M, 122, 23, 3, GOLD, radius=1)
text(79, 115, "從一筆螢光，到一張研究地圖", 10.5, GREEN, "TC-Medium")
text(M-2, 153, "把螢光標記，", 47, GREEN, "TC-Black", 440)
rect(M-1, 252, 319, 15, "#EEDD83", radius=4)
text(M-2, 216, "變成研究脈絡。", 47, GREEN, "TC-Black", 440)
text(M, 296, "每張便條，都是可摘要、可翻譯的研究線索。", 13.5, TEXT, max_width=435)
text(M, 321, "連結多篇文獻，讓零散重點長成自己的觀點。", 13.5, TEXT, max_width=435)

steps = [(M, "01", "標記"), (155, "02", "理解"), (264, "03", "連結"), (373, "04", "統整")]
for i, (sx, n, label) in enumerate(steps):
    text(sx, 375, n, 8.8, MUTED, "Latin")
    text(sx, 393, label, 15.4, GREEN, "TC-Bold")
    if i < len(steps)-1:
        arrow([(sx+58, 402), (sx+84, 402)], "#A3AF98", .9, 3.5)
line([(M, 433), (450, 433)], LINE, .8)
text(M, 450, "從一篇理解，走向跨文獻統整。", 16.5, GREEN, "TC-Bold")
text(M, 480, "閱讀 × 便條 × AI × 知識白板", 9.6, MUTED, "TC-Medium")

# Assembled application view, using two genuine screenshot excerpts.
px, py, pw, ph = 518, 122, W-M-518, 350
for spread, offset, shade in [(5, 6, "#EDF0E7"), (2, 3, "#E8ECE3")]:
    rect(px-spread, py+offset, pw+spread*2, ph, shade, radius=13)
rect(px, py, pw, ph, "#FFFFFF", LINE, 12)
rect(px+.7, py+.7, pw-1.4, 29, "#F0F3E9", radius=11)
rect(px+.7, py+15, pw-1.4, 15, "#F0F3E9")
for i, dot in enumerate(["#A8B59B", "#C4CEBC", "#D7DED1"]):
    circle(px+16+i*11, py+15, 2.6, dot)
text(px+61, py+8, "PaperReader", 10.5, GREEN, "Brand")
right_text(px+pw-16, py+10, "閱讀與知識白板", 8, MUTED)
text(535, 164, "文獻閱讀", 9, GREEN, "TC-Medium")
text(850, 164, "知識白板", 9, GREEN, "TC-Medium")
for dx in range(816, int(px+pw)-7, 12):
    for dy in range(188, 458, 12):
        circle(dx, dy, .42, "#DDE3D5")

crop = ASSETS / "pdf_highlight_crop.png"
image_clipped(crop, 535, 185, 267, 267*1190/1360, 4)
rect(535, 185, 267, 267*1190/1360, stroke="#E0E6D8", radius=4, lw=.7)
pill(547, 425, "螢光標記 → 自動建立便條", "#F8F0C9", "#80702D", 8.6, 10, 22)

note_width = 265
note_height = note_width * (note.height-10) / (note.width-10)
nx, ny = 854, 202
rect(nx-2, ny+4, note_width+4, note_height, "#ECF0E5", radius=6)
image_clipped(ASSETS / "ai_note_crop.png", nx, ny, note_width, note_height, 5)
rect(nx, ny, note_width, note_height, stroke="#CCD4BC", radius=5, lw=.65)
rect(nx+5, ny, note_width-10, 2.3, GOLD, radius=1)
arrow([(643, 255), (660, 255), (660, 230), (828, 230), (828, 317), (850, 317)], GOLD, 1.2, 4)
circle(643, 255, 2.4, GOLD)
pill(935, 164, "AI 摘要與翻譯", "#EEE8F6", PURPLE, 8.1, 8, 21)
text(px+2, 484, "PaperReader 範例操作畫面節錄；AI 文字為教學示例。", 7.8, MUTED, max_width=pw)

# Four equally weighted product promises.
line([(M, 525), (W-M, 525)], LINE, .8)
available = W - M*2
column = available / 4
copy = [
    ("highlight", "01", ["螢光一畫，", "便條就留下。"],
     ["在 PDF 選字標記，自動建立便條。", "保留原文來源，隨時回到該段落。"]),
    ("spark", "02", ["每一張便條，", "都有 AI 幫你讀。"],
     ["一鍵摘要與翻譯，釐清段落重點。", "保留原文，也留下自己的研究筆記。"]),
    ("network", "03", ["便條一連，", "AI 統整整組觀點。"],
     ["建立支持、對比或延伸等關係。", "AI 依多張關聯便條，生成整合摘要。"]),
    ("papers", "04", ["多篇文獻，", "整理在同一張白板。"],
     ["跨 PDF 排列重點，比較不同觀點。", "把分散的研究，連成可回查的脈絡。"]),
]
for i, (symbol, number, heading, body) in enumerate(copy):
    sx = M + i*column + (15 if i else 0)
    width = column - (30 if i else 15)
    if i:
        line([(M+i*column-3, 550), (M+i*column-3, 742)], LINE, .7)
    icon(symbol, sx+1, 552, GREEN, .91)
    text(sx+39, 555, number, 10.3, MUTED, "Latin")
    for j, value in enumerate(heading):
        text(sx, 590+j*27, value, 20.8, GREEN, "TC-Bold", width)
    for j, value in enumerate(body):
        text(sx, 659+j*18.5, value, 10.4, TEXT, max_width=width)

    if i == 0:
        rect(sx, 717, 59, 13, "#F0DF8C", radius=2)
        text(sx+4, 715, "文獻重點", 9.3, "#77672C", "TC-Medium")
        arrow([(sx+68, 724), (sx+89, 724)], "#9BA88D", .9, 3)
        rect(sx+100, 711, 88, 26, "#FFFFFF", "#D3DCBF", 4)
        rect(sx+104, 711, 80, 2.2, GOLD, radius=1)
        text(sx+112, 719, "來源便條", 9.3, GREEN, "TC-Medium")
    elif i == 1:
        a = pill(sx, 711, "AI 摘要", "#EDF1E6", GREEN, 9.2, 12, 26)
        pill(sx+a+9, 711, "AI 翻譯", "#F7EFCE", "#81702E", 9.2, 12, 26)
    elif i == 2:
        for j, tone in enumerate(["#E8D67C", "#AEC59B", "#B7CCE1"]):
            rect(sx+j*27, 716, 18, 18, tone, radius=4)
            if j < 2:
                line([(sx+j*27+18, 725), (sx+(j+1)*27, 725)], "#A6B395", 1)
        arrow([(sx+73, 725), (sx+98, 725)], PURPLE, 1.1, 3)
        pill(sx+108, 711, "AI 關聯摘要", "#EEE8F6", PURPLE, 8.7, 10, 26)
    else:
        for j, tone in enumerate(["#E4D27B", "#AFC599", "#ADC5DD"]):
            mini_doc(sx+j*45, 710, chr(65+j), tone)
        arrow([(sx+133, 724), (sx+151, 724)], "#9BA88D", .9, 3)
        rect(sx+160, 710, 63, 28, "#EEF2E8", "#CDD7C2", 5)
        text(sx+169, 719, "同一白板", 8.7, GREEN, "TC-Medium")

# Conversion strip: a working link and a vector QR code, without invented claims.
rect(0, 770, W, H-770, GREEN)
text(M, 786, "打開 PaperReader，開始累積研究脈絡。", 17, "#FFFFFF", "TC-Bold", 490)
text(M, 817, "免登入・繁體中文介面", 9, "#D6E0D0", "TC-Medium")
text(560, 790, "educatres.github.io/PaperReader/", 16, "#FFFFFF", "Latin", 490)
text(560, 817, "AI 需連網及自備 API 金鑰，費用依供應商計算。", 7.9, "#D6E0D0", max_width=490)
c.linkURL(URL, (M, 0, W-M, H-770), relative=0, thickness=0)
qr_size = 56
qx, qt = W-M-qr_size, 779
rect(qx-2, qt-2, qr_size+4, qr_size+4, "#FFFFFF")
qr = QrCodeWidget(URL, barFillColor=color(GREEN), barStrokeColor=color(GREEN))
bx, by, bx2, by2 = qr.getBounds()
d = Drawing(qr_size, qr_size, transform=[qr_size/(bx2-bx), 0, 0, qr_size/(by2-by), 0, 0])
d.add(qr)
renderPDF.draw(d, c, qx, H-qt-qr_size)
c.linkURL(URL, (qx, H-qt-qr_size, qx+qr_size, H-qt), relative=0, thickness=0)

c.showPage()
c.save()

COPY = """# PaperReader 特色介紹海報文案

主標：把螢光標記，變成研究脈絡。

引言：從一筆螢光，到一張研究地圖。

每張便條，都是可摘要、可翻譯的研究線索。連結多篇文獻，讓零散重點長成自己的觀點。

閱讀流程：標記 → 理解 → 連結 → 統整。

## 01 螢光一畫，便條就留下。
在 PDF 選字標記，自動建立便條。保留原文來源，隨時回到該段落。

## 02 每一張便條，都有 AI 幫你讀。
一鍵摘要與翻譯，釐清段落重點。保留原文，也留下自己的研究筆記。

## 03 便條一連，AI 統整整組觀點。
建立支持、對比或延伸等關係。AI 依多張關聯便條，生成整合摘要。

## 04 多篇文獻，整理在同一張白板。
跨 PDF 排列重點，比較不同觀點。把分散的研究，連成可回查的脈絡。

收束標語：從一篇理解，走向跨文獻統整。

行動文案：打開 PaperReader，開始累積研究脈絡。

網站：https://educatres.github.io/PaperReader/

頁尾：免登入・繁體中文介面。AI 需連網及自備 API 金鑰，費用依供應商計算。

## 製作與素材說明

- A3 橫式，420 × 297 mm，單頁 PDF；正文為可搜尋的向量文字，繁體中文字型已嵌入。
- 主視覺使用本專案既有範例截圖的節錄與排版拼接，不是未來介面的概念圖。
- 截圖來源：`.guide-build/screenshots/02-highlight.png`、`07-note-ai.png`。
- AI 截圖為既有教學用模擬結果，海報已明確標示；此次製作沒有呼叫 AI API。
- 下方流程圖為功能示意；文獻 A、B、C 代表不同 PDF。
- 網址與 QR Code 皆指向實際 PaperReader 網站。
- 生成原始碼：`docs/poster/create_feature_poster_pdf.py`。

## 文案參考

參考以下網站「以閱讀情境引出效益，再串起摘錄、組織與運用」的介紹方式。海報文案為 PaperReader 原創撰寫，功能依本專案 README 與使用者指定的四項亮點整理，未沿用他站的功能、圖像、使用者評語或效能數據。

- https://www.marginnote.com/en/index.html
- https://www.marginnote.com.cn/
- https://leadingmrk.com/marginnote-tutorial/
"""
(OUT / "PaperReader_海報文案.md").write_text(COPY, encoding="utf-8")
print(PDF)
print(f"Page: {W:.2f} x {H:.2f} pt; {PDF.stat().st_size:,} bytes")
