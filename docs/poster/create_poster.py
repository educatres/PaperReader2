"""Render the PaperReader poster at 3840 x 2160 (16:9)."""

from pathlib import Path
from functools import lru_cache
import math

import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter


OUT = Path(__file__).resolve().parent
S = 2
W, H = 1920, 1080
PAPER = '#FAFBF6'
GREEN = '#294F40'
INK = '#314839'
MUTED = '#75816F'
LINE = '#DFE5D9'
GOLD = '#D9B94F'
FONT_DIR = Path.home() / 'AppData/Local/Microsoft/Windows/Fonts'
im = Image.new('RGB', (W * S, H * S), PAPER)
d = ImageDraw.Draw(im)


def box(coords):
    return tuple(round(v * S) for v in coords)


@lru_cache(maxsize=100)
def font(size, weight='Regular'):
    if weight == 'Brand':
        return ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', round(size * S))
    return ImageFont.truetype(str(FONT_DIR / f'NotoSansTC-{weight}.ttf'), round(size * S))


def txt(x, y, text, size=20, color=INK, weight='Regular', anchor='lt'):
    d.text((round(x * S), round(y * S)), text, font=font(size, weight), fill=color, anchor=anchor)


def width(text, size, weight='Regular'):
    return d.textlength(text, font=font(size, weight)) / S


def line(points, fill=LINE, stroke=1):
    d.line([(round(x * S), round(y * S)) for x, y in points], fill=fill, width=max(1, round(stroke * S)), joint='curve')


def rr(rect, radius=12, fill='white', outline=None, stroke=1):
    d.rounded_rectangle(box(rect), round(radius * S), fill=fill, outline=outline, width=round(stroke * S))


def circle(x, y, r, fill, outline=None, stroke=1):
    d.ellipse(box((x - r, y - r, x + r, y + r)), fill=fill, outline=outline, width=round(stroke * S))


def shadow(rect, radius=16, opacity=26, blur=20, offset=(0, 10)):
    mask = Image.new('RGBA', im.size)
    md = ImageDraw.Draw(mask)
    dx, dy = offset
    md.rounded_rectangle(box((rect[0] + dx, rect[1] + dy, rect[2] + dx, rect[3] + dy)), round(radius * S), fill=(32, 58, 41, opacity))
    im.paste(mask.filter(ImageFilter.GaussianBlur(blur * S)), (0, 0), mask.filter(ImageFilter.GaussianBlur(blur * S)))


def arrow(points, fill='#A3B299', stroke=2, tip=7):
    line(points, fill, stroke)
    a, b = points[-2], points[-1]
    angle = math.atan2(b[1] - a[1], b[0] - a[0])
    for off in [-0.52, 0.52]:
        end = (b[0] - tip * math.cos(angle + off), b[1] - tip * math.sin(angle + off))
        line([b, end], fill, stroke)


def icon(kind, x, y, color=GREEN, scale=1):
    def p(a, b):
        return x + a * scale, y + b * scale
    def il(points):
        line([p(a, b) for a, b in points], color, 2.1 * scale)
    def ic(a, b, r):
        circle(*p(a, b), r * scale, None, color, 2 * scale)
    if kind == 'highlight':
        il([(4, 22), (17, 9), (25, 17), (12, 30), (4, 30), (4, 22)])
        il([(14, 12), (22, 20)])
        il([(2, 35), (31, 35)])
    elif kind == 'ai':
        il([(17, 3), (20, 13), (30, 17), (20, 21), (17, 31), (13, 21), (3, 17), (13, 13), (17, 3)])
        il([(30, 2), (30, 9)])
        il([(26.5, 5.5), (33.5, 5.5)])
    elif kind == 'connect':
        il([(10, 11), (25, 26)])
        il([(24, 10), (11, 26)])
        for a, b in [(6, 7), (28, 7), (6, 30), (28, 30)]:
            rr((x + (a-4)*scale, y + (b-4)*scale, x + (a+4)*scale, y + (b+4)*scale), 2*scale, PAPER, color, 2*scale)
    elif kind == 'pack':
        il([(4, 9), (14, 9), (18, 14), (33, 14), (33, 34), (4, 34), (4, 9)])
        il([(19, 17), (19, 29)])
        il([(14, 24), (19, 29), (24, 24)])


# Quiet editorial background with a radial field behind the visual.
for x in range(1080, 1920, 25):
    for y in range(130, 680, 25):
        if ((x - 1680) / 700) ** 2 + ((y - 350) / 430) ** 2 < 1:
            circle(x, y, 0.7, '#E1E8DB')

# Product signature.
rr((80, 48, 126, 94), 12, GREEN)
d.polygon([box(p) for p in [(94, 59), (107, 59), (115, 67), (115, 82), (94, 82)]], fill=PAPER)
line([(107, 59), (107, 67), (115, 67)], '#A9BDA3', 1.5)
line([(99, 72), (110, 72)], GREEN, 1.6)
line([(99, 77), (107, 77)], GREEN, 1.6)
txt(143, 51, 'PaperReader', 35, GREEN, 'Brand')
txt(144, 96, '繁體中文 PDF 研究閱讀器', 13, MUTED, 'Medium')
audience = '教授 · 研究生 · 大學生'
txt(1840, 60, audience, 20, GREEN, 'Medium', 'rt')
txt(1840, 94, '文獻回顧 ／ 論文研究 ／ 課程報告', 15, MUTED, anchor='rt')
line([(80, 135), (1840, 135)], LINE)

# Main message.
rr((82, 180, 114, 185), 2, GOLD)
txt(128, 170, '從閱讀，到研究洞見', 19, GREEN, 'Medium')
txt(77, 229, '把論文讀成', 80, GREEN, 'Black')
# Hand-drawn accent is deliberately behind the text, like a real marker.
rr((84, 403, 485, 427), 6, '#E9DA92')
txt(77, 328, '自己的知識。', 80, GREEN, 'Black')
txt(84, 453, '標記重點、理解內容、連結想法，', 25, INK, 'Regular')
txt(84, 493, '讓每一次閱讀，都成為研究的累積。', 25, INK, 'Regular')

flow = [('讀 PDF', 82), ('留重點', 250), ('連觀點', 419), ('帶走研究', 588)]
for idx, (label, x) in enumerate(flow):
    txt(x, 591, f'0{idx+1}', 13, '#98A18E', 'Medium')
    txt(x, 617, label, 21, GREEN, 'Bold')
    if idx < 3:
        arrow([(x+112, 631), (x+142, 631)], '#AAB59F', 1.6, 5)

# Main workbench illustration: a real feature narrative, explicitly marked as a diagram.
window = (794, 182, 1840, 661)
shadow(window, 22, 34, 24, (0, 13))
rr(window, 22, '#FFFFFF', '#DCE4D6')
rr((795, 183, 1839, 230), 21, '#EDF1E7')
d.rectangle(box((795, 207, 1839, 231)), fill='#EDF1E7')
circle(815, 206, 4, '#A6B79A')
circle(832, 206, 4, '#BECAB4')
circle(849, 206, 4, '#D2DACB')
txt(876, 195, 'PaperReader', 17, GREEN, 'Brand')
txt(1818, 199, '私人研究工作台', 13, MUTED, anchor='rt')
line([(795, 231), (1839, 231)], LINE)
txt(818, 248, '文獻閱讀', 15, GREEN, 'Medium')
txt(1231, 248, '知識白板', 15, GREEN, 'Medium')
txt(1818, 248, '功能示意', 12, '#95A18C', anchor='rt')
line([(1210, 239), (1210, 640)], LINE)

# Paper sheet with readable copy rather than decorative pseudo text.
paper = (818, 282, 1186, 611)
rr(paper, 6, '#FFFFFF', '#E1E6DB')
rr((834, 294, 870, 313), 4, '#EEF2E8')
txt(842, 295, 'PDF', 11, GREEN, 'Bold')
txt(854, 331, '閱讀與知識建構', 23, GREEN, 'Bold')
txt(854, 369, '從文獻重點，走向自己的研究觀點', 12, MUTED)
line([(854, 399), (1151, 399)], '#D9E1D2')
txt(854, 418, '摘要', 14, GREEN, 'Bold')
paper_lines = ['理解來自對主張、證據與限制的檢視。', '保留原文脈絡，能讓筆記回到來源，', '也讓每個研究問題都有跡可循。']
for i, copy in enumerate(paper_lines):
    if i < 2:
        rr((851, 451 + i*25, 1156 - i*13, 474 + i*25), 2, '#F5E9AC')
    txt(854, 452 + i*25, copy, 14, INK)
txt(854, 553, '關鍵字', 11, MUTED)
txt(905, 553, '閱讀 · 證據 · 知識連結', 11, GREEN)
txt(1164, 588, 'p. 1', 11, MUTED, anchor='rt')

# Dotted whiteboard field.
for x in range(1231, 1820, 18):
    for y in range(286, 626, 18):
        circle(x, y, .6, '#E3E9DC')

# Relationships sit below the note cards.
arrow([(1157, 464), (1219, 464), (1219, 353), (1251, 353)], '#C5B15C', 2.2, 7)
arrow([(1381, 413), (1381, 437), (1354, 437), (1354, 473)], '#9CA98B', 2.2, 7)
arrow([(1512, 357), (1633, 357), (1633, 412)], '#B6A5C3', 2.2, 7)
arrow([(1480, 543), (1538, 543)], '#B6A5C3', 2.2, 7)
rr((1503, 337, 1560, 361), 8, '#FAFBF6')
txt(1516, 340, '整合', 12, '#866B98', 'Medium')
rr((1315, 425, 1362, 449), 7, '#FAFBF6')
txt(1326, 428, '對比', 12, MUTED, 'Medium')


def note(rect, tint, edge, title, rows, footer):
    x1, y1, x2, y2 = rect
    shadow(rect, 11, 15, 8, (0, 5))
    rr(rect, 11, '#FFFFFF', '#DCE3D5')
    rr((x1+1, y1+1, x2-1, y1+11), 9, tint)
    d.rectangle(box((x1+1, y1+7, x2-1, y1+11)), fill=tint)
    txt(x1+18, y1+24, title, 20, GREEN, 'Bold')
    for i, row in enumerate(rows):
        txt(x1+18, y1+61+i*23, row, 13.5, INK)
    txt(x1+18, y2-27, footer, 11.5, MUTED)
    txt(x2-15, y2-30, '↗', 17, edge, 'Bold', 'rt')


note((1253, 290, 1515, 415), '#EBD47F', '#A38A2F', '研究發現', ['選字就能留下重點，', '原文與自己的筆記分開保存。'], '來源 p. 1')
note((1230, 475, 1483, 609), '#B8C9A5', '#738C59', '方法與限制', ['跨文獻比較不同觀點，', '連結研究主張、證據與問題。'], '來源 p. 3')
note((1540, 414, 1815, 588), '#D7C5E8', '#8E70A5', '關聯摘要', ['把相連便條交給 AI 整理，', '掌握共同主題與觀點差異。'], '保留來源，方便回查')

# Hero caption reinforces the most distinctive interaction.
rr((848, 625, 1165, 648), 8, '#F1F4EC')
txt(865, 628, '選字即成便條 · 點一下回到原文', 12.5, GREEN, 'Medium')

# Four evenly spaced benefits.
line([(80, 709), (1840, 709)], LINE)
benefits = [
    ('highlight', '重點一劃，來源不丟', '四色標記、圖表截圖便條', '點選便條，回到原文位置'),
    ('ai', 'AI 協助，讀得更懂', '段落翻譯、全文與關聯摘要', '原文、AI 整理與筆記分開保存'),
    ('connect', '文獻一連，觀點成形', '跨 PDF 便條自由排列連線', '比較主張，整理證據與問題'),
    ('pack', '研究累積，隨時帶走', '資料本機保存、支援離線閱讀', '完整封裝備份，接續研究進度'),
]
for i, (kind, title, desc1, desc2) in enumerate(benefits):
    x = 83 + i*450
    icon(kind, x, 745)
    txt(x+53, 754, f'0{i+1}', 14, '#A1AB97', 'Medium')
    txt(x, 802, title, 25, GREEN, 'Bold')
    txt(x, 850, desc1, 19, INK)
    txt(x, 882, desc2, 18, MUTED)
    if i < 3:
        line([(x+418, 752), (x+418, 911)], LINE)

# Footer and real QR code. No fake generated QR or unsupported product claims.
d.rectangle(box((0, 954, 1920, 1080)), fill=GREEN)
txt(82, 978, '打開網站，先試讀一篇範例', 28, '#FFFFFF', 'Bold')
txt(84, 1025, '免登入 · 繁體中文介面', 18, '#CAD7C4')
txt(866, 982, 'educatres.github.io/PaperReader/', 24, '#FFFFFF', 'Medium')
txt(868, 1025, 'AI 功能需連網並自備 API 金鑰；使用依供應商計費。', 14, '#CAD7C4')

qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=3)
qr.add_data('https://educatres.github.io/PaperReader/')
qr.make(fit=True)
qr_image = qr.make_image(fill_color=GREEN, back_color='white').convert('RGB')
qr_image = qr_image.resize((104*S, 104*S), Image.Resampling.NEAREST)
im.paste(qr_image, (1736*S, 965*S))

OUT.mkdir(parents=True, exist_ok=True)
full = OUT / 'PaperReader_特色海報_16x9_4K.png'
preview = OUT / 'PaperReader_特色海報_16x9_預覽.jpg'
im.save(full, optimize=True, dpi=(200, 200))
im.resize((1920, 1080), Image.Resampling.LANCZOS).save(preview, quality=95, subsampling=0)
print(full)
print(preview)
print(f'{im.width} x {im.height}; ratio 16:9')
