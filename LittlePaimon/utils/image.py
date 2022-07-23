from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from typing import Tuple, Union, Literal, List
from pathlib import Path

from LittlePaimon.config import FONTS_PATH


class PMImage:

    def __init__(self,
                 image: Union[Image.Image, Path] = None,
                 size: Tuple[int, int] = (200, 200),
                 color: Union[str, Tuple[int, int, int, int]] = (255, 255, 255),
                 mode: str = 'RGBA'
                 ):
        """
            初始化图像，优先读取image参数，如无则新建图像
        :param image: PIL对象或图像路径
        :param size: 图像大小
        :param color: 图像颜色
        :param mode: 图像模式
        """
        if image:
            if isinstance(image, Path):
                self.image = Image.open(image)
            else:
                self.image = image
        else:
            if mode == 'RGB':
                color = (color[0], color[1], color[2])
            self.image = Image.new(mode, size, color)
        self.draw = ImageDraw.Draw(self.image)

    @property
    def width(self) -> int:
        return self.image.width

    @property
    def height(self) -> int:
        return self.image.height

    @property
    def size(self) -> Tuple[int, int]:
        return self.image.size

    @property
    def mode(self) -> str:
        return self.image.mode

    def show(self) -> None:
        self.image.show()

    def new(self, size: Tuple[int, int], color: Tuple[int, int, int] = (255, 255, 255), mode: str = 'RGBA'):
        self.image = Image.new(size=size, color=color, mode=mode)

    def convert(self, mode: str):
        self.image.convert(mode)

    def save(self, path: Union[str, Path], **kwargs):
        """
        保存图像
        :param path: 保存路径
        :return:
        """
        self.image.save(path, **kwargs)

    def save_to_io(self, **kwargs) -> BytesIO:
        """
        将图像保存到BytesIO中
        """
        bio = BytesIO()
        self.image.save(bio, **kwargs)
        return bio

    def copy(self) -> "PMImage":
        """
        返回一个本对象的复制
        :return: PMImage
        """
        return PMImage(self.image.copy())

    def text_length(self, text: str, font: ImageFont.ImageFont) -> int:
        return self.draw.textlength(text, font)

    def text_size(self, text: str, font: ImageFont.ImageFont) -> Tuple[int, int]:
        return self.draw.textsize(text, font)

    def resize(self, size: Union[float, Tuple[int, int]]):
        """
        缩放图片
        :param size: 缩放大小/区域
        """
        if isinstance(size, (float, int)):
            self.image = self.image.resize((int(self.width * size), int(self.height * size)), Image.Resampling.LANCZOS)
        else:
            self.image = self.image.resize(size, Image.Resampling.LANCZOS)

    def crop(self, box: Tuple[int, int, int, int]):
        """
        裁剪图像
        :param box: 目标区域
        """
        self.image.crop(box)

    def rotate(self, angle: float, expand: bool = False, **kwargs):
        """
        旋转图像
        :param angle: 角度
        :param expand: expand
        """
        self.image.rotate(angle, resample=Image.BICUBIC, expand=expand, **kwargs)

    def paste(self,
              image: Union[Image.Image, 'PMImage'],
              pos: Tuple[int, int],
              alpha: bool = True,
              ):
        """
        粘贴图像
        :param image: 图像
        :param pos: 位置
        :param alpha: 是否透明
        """
        if isinstance(image, PMImage):
            image = image.image
        if alpha:
            image = image.convert('RGBA')
            self.image.alpha_composite(image, pos)
        else:
            self.image.paste(image, pos)

    def text(self,
             text: str,
             width: Union[float, Tuple[float, float]],
             height: Union[float, Tuple[float, float]],
             font: ImageFont.ImageFont = None,
             color: Union[str, Tuple[int, int, int, int]] = 'white',
             align: Literal['left', 'center', 'right'] = 'left'
             ):
        """
        写文本
        :param text: 文本
        :param width: 位置横坐标
        :param height: 位置纵坐标
        :param font: 字体
        :param color: 颜色
        :param align: 对齐类型
        """
        if align == 'left':
            if isinstance(width, tuple):
                width = width[0]
            if isinstance(height, tuple):
                height = height[0]
            self.draw.text((width, height), text, color, font)
        elif align in ['center', 'right']:
            w, h = self.draw.textsize(text, font)
            if align == 'center':
                w = width[0] + (width[1] - width[0] - w) / 2 if isinstance(width, tuple) else width
                h = height[0] + (height[1] - height[0] - h) / 2 if isinstance(height, tuple) else height
            else:
                if isinstance(width, tuple):
                    width = width[1]
                w = width - w
                h = height[0] if isinstance(height, tuple) else height
            self.draw.text((w, h),
                           text,
                           color,
                           font)
        else:
            raise ValueError('对齐类型必须为\'left\', \'center\'或\'right\'')

    def stretch(self,
                pos: Tuple[int, int],
                length: int,
                type: Literal['width', 'height'] = 'height'):
        """
        将某一部分进行拉伸
        :param pos: 拉伸的部分
        :param length: 拉伸的目标长/宽度
        :param type: 拉伸方向，width:横向, height: 竖向
        """
        if pos[0] <= 0:
            raise ValueError('起始轴必须大于等于0')
        if pos[1] <= pos[0]:
            raise ValueError('结束轴必须大于起始轴')
        if type == 'height':
            if pos[1] >= self.height:
                raise ValueError('终止轴必须小于图片高度')
            top = self.image.crop((0, 0, self.width, pos[0]))
            center = self.image.crop((0, pos[0], self.width, pos[1])).resize((self.width, length),
                                                                             Image.Resampling.LANCZOS)
            bottom = self.image.crop((0, pos[1], self.width, self.height))
            self.image = Image.new('RGBA', (self.width, top.height + center.height + bottom.height))
            self.image.paste(top, (0, 0))
            self.image.paste(center, (0, top.height))
            self.image.paste(bottom, (0, top.height + center.height))
            self.draw = ImageDraw.Draw(self.image)
        elif type == 'width':
            if pos[1] >= self.width:
                raise ValueError('终止轴必须小于图片宽度')
            top = self.image.crop((pos[0], 0, pos[0], self.height))
            center = self.image.crop((pos[0], 0, pos[1], self.height)).resize((length, self.height),
                                                                              Image.Resampling.LANCZOS)
            bottom = self.image.crop((pos[1], 0, pos[1], self.height))
            self.image = Image.new('RGBA', (top.width + center.width + bottom.width, self.height))
            self.image.paste(top, (0, 0))
            self.image.paste(center, (top.width, 0))
            self.image.paste(bottom, (top.width + center.width, 0))
            self.draw = ImageDraw.Draw(self.image)
        else:
            raise ValueError('类型必须为\'width\'或\'height\'')

    def circle_corner(self, r: int = 5):
        """
        将图片裁剪为圆角矩形
        :param r: 圆角半径
        """
        self.convert("RGBA")
        w, h = self.size
        alpha = self.image.split()[-1]
        circle = Image.new("L", (r * 2, r * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, r * 2, r * 2), fill=255)
        alpha.paste(circle.crop((0, 0, r, r)), (0, 0))
        alpha.paste(circle.crop((r, 0, r * 2, r)), (w - r, 0))
        alpha.paste(circle.crop((r, r, r * 2, r * 2)), (w - r, h - r))
        alpha.paste(circle.crop((0, r, r, r * 2)), (0, h - r))
        self.image.putalpha(alpha)

    def draw_line(self,
                  begin: Tuple[int, int],
                  end: Tuple[int, int],
                  color: Union[str, Tuple[int, int, int, int]] = 'black',
                  width: int = 1):
        """
        画线
        :param begin: 起始点
        :param end: 终点
        :param color: 颜色
        :param width: 宽度
        :return:
        """
        self.draw.line(begin + end, fill=color, width=width)

    def draw_ring(self,
                  size: Tuple[int, int],
                  pos: Tuple[int, int],
                  width: float = 0.5,
                  percent: Union[float, List[float]] = 1,
                  colors: Union[str, List[str]] = 'black',
                  startangle: int = 90,
                  transparent: bool = True
                  ):
        """
        画百分比圆环
        :param size: 圆环大小
        :param pos: 圆环位置
        :param width: 圆环宽度
        :param percent: 百分比
        :param colors: 颜色
        :param startangle: 角度
        :param transparent: 是否透明
        """
        if isinstance(percent, float):
            if percent < 0 or percent > 1:
                raise ValueError('百分比必须在0-1之间')
            percent = [percent, 1 - percent]
        if isinstance(colors, str):
            colors = [colors, '#FFFFFF']
        if len(percent) != len(colors):
            raise ValueError('百分比和颜色数量不一致')
        plt.pie(percent, startangle=startangle, colors=colors)
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(percent,
               wedgeprops={'width': width},
               startangle=startangle,
               colors=colors)
        bio = BytesIO()
        plt.savefig(bio, transparent=transparent)
        bio.seek(0)
        ring = Image.open(bio).resize(size)
        plt.cla()
        plt.close("all")
        self.paste(ring, pos)


class FontManager:
    """
    字体管理器，获取字体路径中的所有字体
    """

    def __init__(self):
        self.font_path = FONTS_PATH
        fonts = []
        for font_name in FONTS_PATH.iterdir():
            if font_name.is_file():
                fonts.append(font_name.stem + font_name.suffix)
        self.fonts = fonts
        self.fonts_cache = {}

    def get(self, font_name: str = 'hywh.ttf', size: int = 25) -> ImageFont.ImageFont:
        """
        获取字体，如果已在缓存中，则直接返回
        :param font_name: 字体名称
        :param size: 字体大小
        """
        if font_name not in self.fonts:
            raise FileNotFoundError('不存在字体文件 {} ，请补充至字体资源中'.format(font_name))
        if f'{font_name}-{size}' in self.fonts_cache:
            return self.fonts_cache[f'{font_name}-{size}']
        else:
            font = ImageFont.truetype(str(self.font_path / font_name), size)
            self.fonts_cache[f'{font_name}-{size}'] = font
            return font


font_manager = FontManager()



