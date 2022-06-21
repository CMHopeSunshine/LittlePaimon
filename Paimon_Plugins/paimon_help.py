from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List
from nonebot import on_command
from nonebot import plugin as nb_plugin
from nonebot.params import Depends
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.plugin import PluginMetadata

from utils.message_util import MessageBuild


__plugin_meta__ = PluginMetadata(
    name="帮助菜单",
    description="自动读取插件的信息，生成帮助菜单图片",
    usage=(
        "help"
    ),
    extra={
        'type':    '工具',
        'range':   ['private', 'group', 'guild'],
        "author":  "惜月 <277073121@qq.com>",
        "version": "v1.0.0",
    },
)

help_ = on_command('help', aliases={'帮助菜单', '派蒙帮助'}, priority=1, block=True)
help_.__paimon_help__ = {
    "usage":     "帮助菜单|help",
    "introduce": "查看派蒙的帮助信息",
    "priority":  99
}

font_path = Path(__file__).parent.parent / 'res'
res_path = Path(__file__).parent.parent / 'res' / 'help'


def get_font(size, font='hywh.ttf') -> ImageFont:
    return ImageFont.truetype(str(font_path / font), size=size)


# 绘制带阴影的文字
def draw_shadow_text(draw: ImageDraw, pos: tuple, text: str, font: ImageFont, color: tuple, shadow_color: tuple,
                     shadow_offset: tuple = (1, 1)):
    draw.text(pos, text, font=font, fill=shadow_color)
    draw.text((pos[0] - shadow_offset[0], pos[1] - shadow_offset[1]), text, font=font, fill=color)


def draw_table(title: str, funcs: List[dict], total_width: int):
    row = len(funcs) // 3 if not len(funcs) % 3 else len(funcs) // 3 + 1
    total_height = 120 + row * 160
    bg_color = (100, 100, 100, 100)
    title_color = (40, 40, 40, 125)
    usage_color = (255, 255, 255, 255)
    introduce_color = (200, 200, 200, 255)
    radius = 50
    bg = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bg)

    bg_draw.ellipse((0, 0, radius, radius), fill=bg_color)
    bg_draw.ellipse((total_width - radius, 0, total_width, radius), fill=bg_color)
    bg_draw.ellipse((0, total_height - radius, radius, total_height), fill=bg_color)
    bg_draw.ellipse((total_width - radius, total_height - radius, total_width, total_height), fill=bg_color)
    bg_draw.rectangle((radius / 2, 0, total_width - radius / 2, total_height), fill=bg_color)
    bg_draw.rectangle((0, radius / 2, total_width, total_height - radius / 2), fill=bg_color)

    draw_shadow_text(bg_draw, (50, 23), title, get_font(50), (255, 255, 255), (0, 0, 0, 255), (2, 2))
    i = 0
    for func in funcs:
        x = (i % 3) * (total_width / 3) + 4
        y = 100 + (i // 3) * 160 + 4
        bg_draw.rectangle((x, y, x + total_width / 3 - 8, y + 160 - 8), fill=title_color)
        bg_draw.text((x + 7, y + 7), func['usage'], font=get_font(36), fill=usage_color)
        # 如果introduce长度大于15， 就分多行绘制
        if len(func['introduce']) > 15:
            bg_draw.text((x + 10, y + 60), func['introduce'][:15], font=get_font(30), fill=introduce_color)
            bg_draw.text((x + 10, y + 90), func['introduce'][15:], font=get_font(30), fill=introduce_color)
        else:
            bg_draw.text((x + 10, y + 60), func['introduce'], font=get_font(30), fill=introduce_color)
        i += 1
    return row, bg


def draw_help_info(help_info: dict):
    total_height = 400 + len(help_info) * 150 - 50
    for m in help_info:
        total_height += 160 * len(help_info[m]) // 3
        if len(help_info[m]) % 3:
            total_height += 160
    total_height += 150
    img = Image.new('RGBA', (1500, total_height), color=(255, 255, 255, 255))
    bg_img = Image.open(str(res_path / 'bg.jpg')).convert('RGBA').resize((1500, total_height))
    img.paste(bg_img, (0, 0), bg_img)
    draw = ImageDraw.Draw(img)
    draw_shadow_text(draw, (50, 50), '派蒙帮助', get_font(140), (255, 255, 255), (0, 0, 0, 255), (3, 3))
    draw_shadow_text(draw, (610, 140), __plugin_meta__.extra.get('version', '1.0.0'), get_font(50), (255, 255, 255), (0, 0, 0, 255), (3, 3))
    draw_shadow_text(draw, (520, 250), '<>内为必须，[]内为可选，()内只需要第一次', get_font(50), (255, 255, 255), (0, 0, 0, 255), (2, 2))
    draw_shadow_text(draw, (620, 300), '描述前带*号说明需要绑定私人cookie', get_font(50), (255, 255, 255), (0, 0, 0, 255), (2, 2))
    n = 400
    for type, func_list in help_info.items():
        row, table = draw_table(type, func_list, 1500 - 100)
        img.alpha_composite(table, (50, n))
        n += 170 + row * 160
    draw_shadow_text(draw, (800, n + 15), 'Created by LittlePaimon', get_font(50), (255, 255, 255), (0, 0, 0, 255), (2, 2))
    return MessageBuild.Image(img, size=0.7, mode='RGB', quality=80)


async def get_all_plugin(event: MessageEvent) -> dict:
    plugin_list = nb_plugin.get_loaded_plugins()
    help_info: Dict[str, List[dict]] = {}
    for plugin in plugin_list:
        try:
            plugin_type = plugin.metadata.extra.get('type', '其他')
            plugin_range = plugin.metadata.extra.get('range', ['private', 'group', 'guild'])
        except AttributeError:
            plugin_type = '其他'
            plugin_range = ['private', 'group', 'guild']
        if event.message_type not in plugin_range:
            continue
        if plugin_type not in help_info:
            help_info[plugin_type] = []
        matchers = plugin.matcher
        for matcher in matchers:
            try:
                matchers_info = matcher.__paimon_help__
                if 'priority' not in matchers_info:
                    matchers_info['priority'] = 99
                help_info[plugin_type].append(matchers_info)
            except AttributeError:
                pass
    help_info = {k: v for k, v in help_info.items() if v}
    if not help_info:
        await help_.finish('当前没有已加载的插件哦')
    for m in help_info:
        help_info[m].sort(key=lambda x: x['priority'])
    help_info = dict(sorted(help_info.items(), key=lambda x: len(x[1]), reverse=True))
    return help_info


@help_.handle()
async def _(event: MessageEvent, help_info: dict = Depends(get_all_plugin)):
    await help_.finish(draw_help_info(help_info))
