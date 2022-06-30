from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

res_path = Path(__file__).parent.parent / 'res'


def get_font(size, font='hywh.ttf'):
    return ImageFont.truetype(str(res_path / font), size)


def draw_right_text(draw, text, width, height, fill, font):
    text_length = draw.textlength(text, font=font)
    draw.text((width - text_length, height), text, fill=fill,
              font=font)


def draw_center_text(draw, text, left_width, right_width, height, fill, font):
    text_length = draw.textlength(text, font=font)
    draw.text((left_width + (right_width - left_width - text_length) / 2, height), text, fill=fill,
              font=font)
