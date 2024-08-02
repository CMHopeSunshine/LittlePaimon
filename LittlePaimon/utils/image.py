from io import BytesIO
from pathlib import Path
from typing import Tuple, Union, Literal, List, Optional, Dict, Any

import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.ImageFont import FreeTypeFont
from nonebot.utils import run_sync

from LittlePaimon.config import config
from .path import FONTS_PATH
from .requests import aiorequests

plt.switch_backend('agg')

class PMImage:

    def __init__(self,
                 image: Union[Image.Image, Path, None] = None,
                 *,
                 size: Tuple[int, int] = (200, 200),
                 color: Union[str, Tuple[int, int, int, int], Tuple[int, int, int]] = (255, 255, 255, 255),
                 mode: Literal["1", "CMYK", "F", "HSV", "I", "L", "LAB", "P", "RGB", "RGBA", "RGBX", "YCbCr"] = 'RGBA'
                 ):
        """
        初始化图像，优先读取image参数，如无则新建图像

        :param image: PIL对象或图像路径
        :param size: 图像大小
        :param color: 图像颜色
        :param mode: 图像模式
        """
        if image:
            self.image = Image.open(image) if isinstance(image, Path) else image.copy()
        else:
            if mode == 'RGB' and isinstance(color, tuple):
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

    @run_sync
    def new(self, size: Tuple[int, int], color: Tuple[int, int, int] = (255, 255, 255), mode: str = 'RGBA'):
        self.image = Image.new(size=size, color=color, mode=mode)

    def convert(self, mode: str):
        return self.image.convert(mode)

    def save(self, path: Union[str, Path], **kwargs):
        """
        保存图像

        :param path: 保存路径
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
        return int(self.draw.textlength(text, font))

    def text_size(self, text: str, font: ImageFont.ImageFont) -> Tuple[int, int]:
        return self.draw.textsize(text, font)

    def text_box_height(self,
                        text: str,
                        width: Tuple[int, int],
                        height: Tuple[int, int],
                        font: ImageFont.ImageFont) -> int:
        text_height = self.draw.textsize(text, font=font)[1]
        width_now = width[0]
        height_now = height[0]
        for c in text:
            if c in ['.', '。'] and width_now == width[0] and c == text[-1]:
                continue
            c_length = self.draw.textlength(c, font=font)
            if width_now + c_length > width[1]:
                width_now = width[0]
                height_now += text_height
            else:
                width_now += c_length
        return height_now

    @run_sync
    def resize(self, size: Union[float, Tuple[int, int]]):
        """
        缩放图片
            :param size: 缩放大小/区域
        """
        if isinstance(size, (float, int)):
            self.image = self.image.resize((int(self.width * size), int(self.height * size)), Image.Resampling.LANCZOS)
        else:
            self.image = self.image.resize(size, Image.Resampling.LANCZOS)
        self.draw = ImageDraw.Draw(self.image)

    @run_sync
    def crop(self, box: Tuple[int, int, int, int]):
        """
        裁剪图像
            :param box: 目标区域
        """
        self.image = self.image.crop(box)
        self.draw = ImageDraw.Draw(self.image)

    @run_sync
    def rotate(self, angle: float, expand: bool = False, **kwargs):
        """
        旋转图像
            :param angle: 角度
            :param expand: expand
        """
        self.image.rotate(angle, resample=Image.BICUBIC, expand=expand, **kwargs)
        self.draw = ImageDraw.Draw(self.image)

    @run_sync
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
        if image is None:
            return
        if isinstance(image, PMImage):
            image = image.image
        if alpha:
            image = image.convert('RGBA')
            if self.image.mode != 'RGBA':
                self.image = self.convert('RGBA')
            self.image.alpha_composite(image, pos)
        else:
            self.image.paste(image, pos)
        self.draw = ImageDraw.Draw(self.image)

    @run_sync
    def text(self,
             text: str,
             width: Union[float, Tuple[float, float]],
             height: Union[float, Tuple[float, float]],
             font: ImageFont.ImageFont,
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
            _, _, w, h = self.draw.textbbox((0, 0), text, font)
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

    @run_sync
    def text_box(self,
                 text: str,
                 width: Tuple[int, int],
                 height: Tuple[int, int],
                 font: ImageFont.ImageFont,
                 color: Union[str, Tuple[int, int, int, int]] = 'white'):
        text_height = self.draw.textbbox((0, 0), text = text, font=font)[3] - self.draw.textbbox((0, 0), text = text, font=font)[1]
        width_now = width[0]
        height_now = height[0]
        for c in text:
            if c in ['.', '。'] and width_now == width[0] and c == text[-1]:
                continue
            if c == '^':
                width_now = width[0]
                height_now += text_height
                continue
            c_length = self.draw.textlength(c, font=font)
            if width_now == width[0] and height_now >= height[1]:
                break
            self.draw.text((width_now, height_now), c, color, font=font)
            if width_now + c_length > width[1]:
                width_now = width[0]
                height_now += text_height
            else:
                width_now += c_length

    @run_sync
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
            bottom = self.image.crop((0, pos[1], self.width, self.height))
            if length == 0:
                self.image = Image.new('RGBA', (self.width, top.height + bottom.height))
                self.image.paste(top, (0, 0))
                self.image.paste(bottom, (0, top.height))
            else:
                center = self.image.crop((0, pos[0], self.width, pos[1])).resize((self.width, length),
                                                                                 Image.Resampling.LANCZOS)
                self.image = Image.new('RGBA', (self.width, top.height + center.height + bottom.height))
                self.image.paste(top, (0, 0))
                self.image.paste(center, (0, top.height))
                self.image.paste(bottom, (0, top.height + center.height))
            self.draw = ImageDraw.Draw(self.image)
        elif type == 'width':
            if pos[1] >= self.width:
                raise ValueError('终止轴必须小于图片宽度')
            top = self.image.crop((0, 0, pos[0], self.height))
            bottom = self.image.crop((pos[1], 0, self.width, self.height))
            if length == 0:
                self.image = Image.new('RGBA', (top.width + bottom.width, self.height))
                self.image.paste(top, (0, 0))
                self.image.paste(bottom, (top.width, 0))
            else:
                center = self.image.crop((pos[0], 0, pos[1], self.height)).resize((length, self.height),
                                                                                  Image.Resampling.LANCZOS)
                self.image = Image.new('RGBA', (top.width + center.width + bottom.width, self.height))
                self.image.paste(top, (0, 0))
                self.image.paste(center, (top.width, 0))
                self.image.paste(bottom, (top.width + center.width, 0))
            self.draw = ImageDraw.Draw(self.image)
        else:
            raise ValueError('类型必须为\'width\'或\'height\'')

    @run_sync
    def draw_rectangle(self,
                       pos: Tuple[int, int, int, int],
                       color: Union[str, Tuple[int, int, int, int]] = 'white',
                       width: int = 1):
        """
        绘制矩形
            :param pos: 位置
            :param color: 颜色
            :param width: 宽度
        """
        self.draw.rectangle(pos, color, width=width)

    @run_sync
    def draw_rounded_rectangle(self,
                               pos: Tuple[int, int, int, int],
                               radius: int = 5,
                               color: Union[str, Tuple[int, int, int, int]] = 'white',
                               width: int = 1):
        """
        绘制圆角矩形
            :param pos: 圆角矩形的位置
            :param radius: 半径
            :param color: 颜色
            :param width: 宽度
        """
        # self.convert("RGBA")
        self.draw.rounded_rectangle(xy=pos, radius=radius, fill=color, width=width)

    @run_sync
    def draw_rounded_rectangle2(self,
                                pos: Tuple[int, int],
                                size: Tuple[int, int],
                                radius: int = 5,
                                color: Union[str, Tuple[int, int, int, int]] = 'white',
                                angles: List[Literal['ul', 'ur', 'll', 'lr']] = None):
        """
        选择最多4个角绘制圆角矩形

        :param pos: 左上角起点坐标
        :param size: 矩形大小
        :param radius: 半径
        :param color: 颜色
        :param angles: 角列表
        """
        self.draw.rectangle((pos[0] + radius / 2, pos[1], pos[0] + size[0] - (radius / 2), pos[1] + size[1]),
                            fill=color)
        self.draw.rectangle((pos[0], pos[1] + radius / 2, pos[0] + size[0], pos[1] + size[1] - (radius / 2)),
                            fill=color)
        angle_pos = {
            'ul': (pos[0], pos[1], pos[0] + radius, pos[1] + radius),
            'ur': (pos[0] + size[0] - radius, pos[1], pos[0] + size[0], pos[1] + radius),
            'll': (pos[0], pos[1] + size[1] - radius, pos[0] + radius, pos[1] + size[1]),
            'lr': (pos[0] + size[0] - radius, pos[1] + size[1] - radius, pos[0] + size[0], pos[1] + size[1]),
        }
        for angle, pos2 in angle_pos.items():
            if angle in angles:
                self.draw.ellipse(pos2, fill=color)
            else:
                self.draw.rectangle(pos2, fill=color)

    @run_sync
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
        """
        self.draw.line(begin + end, fill=color, width=width)

    @run_sync
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
            if percent < 0:
                percent = -percent
            if percent > 10:
                raise ValueError('图片传入百分比错误')
            if percent > 1 and percent < 10:
                percent /= 10
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
        self.image.alpha_composite(ring, pos)

    @run_sync
    def to_circle(self, shape: str = 'rectangle'):
        """
        将图片转换为圆形
        """
        if self.image.mode != 'RGBA':
            self.image = self.convert('RGBA')
        w, h = self.size
        r2 = min(w, h)
        if w != h:
            self.image.resize((r2, r2), Image.Resampling.LANCZOS)
        if shape == 'circle':
            mask = Image.new('RGBA', (r2, r2), (255, 255, 255, 0))
            pi = self.image.load()
            pim = mask.load()
            for i in range(r2):
                for j in range(r2):
                    lx = abs(i - r2 // 2)
                    ly = abs(j - r2 // 2)
                    l = (pow(lx, 2) + pow(ly, 2)) ** 0.5
                    if l < r2 // 2:
                        pim[i, j] = pi[i, j]
            self.image = mask
        else:
            width = 1
            antialias = 4
            ellipse_box = [0, 0, r2 - 2, r2 - 2]
            mask = Image.new(
                size=(int(self.image.size[0] * antialias), int(self.image.size[1] * antialias)),
                mode="L",
                color="black")
            draw = ImageDraw.Draw(mask)
            for offset, fill in (width / -2.0, "black"), (width / 2.0, "white"):
                left, top = [(value + offset) * antialias for value in ellipse_box[:2]]
                right, bottom = [(value - offset) * antialias for value in ellipse_box[2:]]
                draw.ellipse([left, top, right, bottom], fill=fill)
            mask = mask.resize(self.image.size, Image.Resampling.LANCZOS)
            self.image.putalpha(mask)

        self.draw = ImageDraw.Draw(self.image)

    @run_sync
    def to_rounded_corner(self, radii: int = 30):
        """
        将图片变为圆角
            :param radii: 半径
        """
        circle = Image.new("L", (radii * 2, radii * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)
        # self.convert("RGBA")
        w, h = self.image.size
        alpha = Image.new("L", self.image.size, 255)
        alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))
        alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))
        alpha.paste(
            circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii)
        )
        alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))
        self.image.putalpha(alpha)
        self.draw = ImageDraw.Draw(self.image)

    @run_sync
    def add_border(self, border_size: int = 10, color: Union[str, Tuple[int, int, int, int]] = 'black',
                   shape: Literal['rectangle', 'circle'] = 'rectangle'):
        """
        给图片添加边框
            :param border_size: 边框宽度
            :param color: 边框颜色
            :param shape: 边框形状，rectangle或circle
        """
        # self.convert("RGBA")
        if shape == 'circle':
            new_img = Image.new('RGBA', (self.width + border_size, self.height + border_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(new_img)
            draw.ellipse((0, 0, self.width + border_size, self.height + border_size), fill=color)
            new_img.alpha_composite(self.image, (border_size // 2, border_size // 2))
            self.image = new_img
            self.draw = ImageDraw.Draw(self.image)
        elif shape == 'rectangle':
            self.image = ImageOps.expand(self.image, border=border_size, fill=color)
            self.draw = ImageDraw.Draw(self.image)


class FontManager:
    """
    字体管理器，获取字体路径中的所有字体
    """

    def __init__(self):
        self.font_path = FONTS_PATH
        fonts = [font_name.stem + font_name.suffix for font_name in FONTS_PATH.iterdir() if font_name.is_file()]
        self.fonts = fonts
        self.fonts_cache = {}

    def get(self, font_name: str = 'hywh.ttf', size: int = 25, variation: Optional[str] = None) -> FreeTypeFont:
        """
        获取字体，如果已在缓存中，则直接返回
        
        :param font_name: 字体名称
        :param size: 字体大小
        :param variation: 字体变体
        """
        if 'ttf' not in font_name and 'ttc' not in font_name and 'otf' not in font_name:
            font_name += '.ttf'
        if font_name not in self.fonts:
            font_name = font_name.replace('.ttf', '.ttc')
        if font_name not in self.fonts:
            raise FileNotFoundError(f'不存在字体文件 {font_name} ，请补充至字体资源中')
        if f'{font_name}-{size}' in self.fonts_cache:
            font = self.fonts_cache[f'{font_name}-{size}']
        else:
            font = ImageFont.truetype(str(self.font_path / font_name), size)
        self.fonts_cache[f'{font_name}-{size}'] = font
        if variation:
            font.set_variation_by_name(variation)
        return font


font_manager = FontManager()

cache_image: Dict[str, Any] = {}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}


async def load_image(
        path: Union[Path, str],
        *,
        size: Optional[Union[Tuple[int, int], float]] = None,
        crop: Optional[Tuple[int, int, int, int]] = None,
        mode: Optional[str] = None,
) -> Image.Image:
    """
    读取图像，并预处理

    :param path: 图片路径
    :param size: 预处理尺寸
    :param crop: 预处理裁剪大小
    :param mode: 预处理图像模式
    :return: 图像对象
    """
    path = Path(path)
    if config.img_use_cache and str(path) in cache_image:
        img = cache_image[str(path)]
    else:
        if path.exists():
            img = Image.open(path)
        elif path.name.startswith(('UI_', 'Skill_')):
            img = await aiorequests.download_icon(path.name, headers=headers, save_path=path, follow_redirects=True)
            if img is None or isinstance(img, str):
                return Image.new('RGBA', size=size if isinstance(size, tuple) else (50, 50), color=(0, 0, 0, 0))
        else:
            raise FileNotFoundError(f'{path} not found')
        if config.img_use_cache:
            cache_image[str(path)] = img
        elif cache_image:
            cache_image.clear()
    if mode:
        img = img.convert(mode)
    if size:
        if isinstance(size, float):
            img = img.resize((int(img.size[0] * size), int(img.size[1] * size)), Image.LANCZOS)
        elif isinstance(size, tuple):
            img = img.resize(size, Image.LANCZOS)
    if crop:
        img = img.crop(crop)
    return img


async def get_qq_avatar(qid: str) -> PMImage:
    """
    获取QQ头像
    :param qid: qq号
    :return: PMImage
    """
    url = f"http://q1.qlogo.cn/g?b=qq&nk={qid}&s=640"
    img = await aiorequests.get_img(url=url)
    img = PMImage(image=img)
    return img
