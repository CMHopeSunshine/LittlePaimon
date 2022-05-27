from PIL import Image, ImageDraw, ImageFont
import os

font_Path = res_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'res')
font = ImageFont.truetype(os.path.join(res_path, 'wqy-microhei.ttc'), 20)

width = 500

color = [
    {'front': 'black', 'back': 'white'},
    {'front': 'white', 'back': 'ForestGreen'},
    {'front': 'white', 'back': 'DarkOrange'},
    {'front': 'white', 'back': 'BlueViolet'},
]


def create_image(item_number):
    height = item_number * 30
    im = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    return im


def draw_rec(im, color, x, y, w, h, r):
    draw = ImageDraw.Draw(im)
    draw.rectangle((x+r, y, x+w-r, y+h), fill=color)
    draw.rectangle((x, y+r, x+w, y+h-r), fill=color)
    r = r * 2
    draw.ellipse((x, y, x+r, y+r), fill=color)
    draw.ellipse((x+w-r, y, x+w, y+r), fill=color)
    draw.ellipse((x, y+h-r, x+r, y+h), fill=color)
    draw.ellipse((x+w-r, y+h-r, x+w, y+h), fill=color)


def draw_text(im, x, y, w, h, text, align, color):
    draw = ImageDraw.Draw(im)
    tw, th = draw.textsize(text, font=font)
    y = y + (h - th) / 2
    if align == 0:  # 居中
        x = x + (w - tw) / 2
    elif align == 1:  # 左对齐
        x = x + 5
    elif align == 2:  # 右对齐
        x = x + w - tw - 5
    draw.text((x, y), text, fill=color, font=font)


def draw_item(im, n, t, text, days, forever):
    if t >= len(color):
        t = 1
    x = 0
    y = n * 30
    height = 28

    draw_rec(im, color[t]['back'], x, y, width, height, 6)

    im1 = Image.new('RGBA', (width - 120, 28), (255, 255, 255, 0))
    draw_text(im1, 0, 0, width, height, text, 1, color[t]['front'])
    _, _, _, a = im1.split()
    im.paste(im1, (x, y), mask=a)

    if days > 0:
        if forever:
            text1 = '永久开放'
        else:
            text1 = f'{days}天后结束'
    elif days < 0:
        text1 = f'{-days}天后开始'
    else:
        text1 = '即将结束'
    draw_text(im, x, y, width, height, text1, 2, color[t]['front'])


def draw_title(im, n, left=None, middle=None, right=None):
    x = 0
    y = n * 30
    height = 28

    draw_rec(im, color[0]['back'], x, y, width, height, 6)
    if middle:
        draw_text(im, x, y, width, height, middle, 0, color[0]['front'])
    if left:
        draw_text(im, x, y, width, height, left, 1, color[0]['front'])
    if right:
        draw_text(im, x, y, width, height, right, 2, color[0]['front'])


def draw_title1(im, n, day_list):
    x = 0
    y = n * 30
    height = 28
    color = 'black'

    n = len(day_list)
    for i in range(n):
        x = width / n * i
        draw_text(im, x, y, width, height, day_list[i], 1, color)
