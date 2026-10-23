"""Create a 160 x 160 PaperReader feature graphic in the project's palette."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
SCALE = 4
image = Image.new('RGB', (160 * SCALE, 160 * SCALE), '#294F40')
draw = ImageDraw.Draw(image)
FONT_DIR = Path.home() / 'AppData/Local/Microsoft/Windows/Fonts'


def coords(values):
    return tuple(round(v * SCALE) for v in values)


def font(size, weight='Regular'):
    path = ('C:/Windows/Fonts/segoeuib.ttf' if weight == 'Brand'
            else str(FONT_DIR / f'NotoSansTC-{weight}.ttf'))
    return ImageFont.truetype(path, round(size * SCALE))


def text(x, y, value, size, fill, weight='Regular', anchor='lt'):
    draw.text(coords((x, y)), value, font=font(size, weight), fill=fill, anchor=anchor)


def line(points, fill, width=1.5):
    draw.line([coords(p) for p in points], fill=fill, width=round(width * SCALE), joint='curve')


def rounded(bounds, radius, fill):
    draw.rounded_rectangle(coords(bounds), radius=round(radius * SCALE), fill=fill)


# Product signature, following public/favicon.svg.
rounded((12, 12, 29, 31), 4, '#FAFBF6')
line([(17, 18), (24, 18)], '#294F40', 1.3)
line([(17, 22), (24, 22)], '#294F40', 1.3)
line([(17, 26), (21, 26)], '#294F40', 1.3)
text(35, 12, 'PaperReader', 17, '#FAFBF6', 'Brand')
text(80, 40, '讓論文變成知識', 16, '#FAFBF6', 'Bold', 'mt')

# A highlighted PDF passage becomes connected research notes.
rounded((22, 67, 66, 122), 5, '#FAFBF6')
text(29, 72, 'PDF', 9, '#294F40', 'Brand')
line([(30, 89), (56, 89)], '#BAC9B8', 1.7)
rounded((28, 95, 60, 102), 1, '#E5C867')
line([(31, 98.5), (56, 98.5)], '#6C6235', 1.2)
line([(30, 109), (50, 109)], '#BAC9B8', 1.7)

line([(69, 98), (85, 98)], '#E5C867', 2)
line([(80, 93), (85, 98), (80, 103)], '#E5C867', 2)
line([(114, 89), (114, 105)], '#B9C9B6', 1.5)
rounded((93, 68, 140, 91), 4, '#EAE7FA')
text(116.5, 73, 'AI 摘要', 9, '#524574', 'Bold', 'mt')
rounded((93, 104, 140, 126), 4, '#F3E4A2')
text(116.5, 108, '研究筆記', 9, '#63542C', 'Bold', 'mt')
draw.ellipse(coords((111.5, 96, 116.5, 101)), fill='#E5C867')

text(80, 140, 'AI 翻譯 × 知識白板', 10.5, '#E0E9DC', 'Medium', 'mt')

target = OUT / 'PaperReader_亮點圖_160x160.png'
image.resize((160, 160), Image.Resampling.LANCZOS).save(target, optimize=True)
with Image.open(target) as result:
    assert result.size == (160, 160)
    print(f'{target} | {result.width} x {result.height} | {result.mode}')
