import datetime
from io import BytesIO

from PIL import Image, ImageDraw

from LittlePaimon.utils.image import font_manager
from LittlePaimon.utils.message import MessageBuild
from LittlePaimon.utils.path import GACHA_RES
from .data_handle import load_json
from .data_source import get_once_data, get_gacha_data


def draw_center_text(draw_target, text: str, left_width: int, right_width: int, height: int, fill: str, font):
    """
    绘制居中文字
    :param draw_target: ImageDraw对象
    :param text: 文字
    :param left_width: 左边位置横坐标
    :param right_width: 右边位置横坐标
    :param height: 位置纵坐标
    :param fill: 字体颜色
    :param font: 字体
    """
    text_length = draw_target.textlength(text, font=font)
    draw_target.text((left_width + (right_width - left_width - text_length) / 2, height), text, fill=fill,
                     font=font)


def draw_single_item(rank, item_type, name, element, count, dg_time):
    type_json = load_json(GACHA_RES / 'type.json', encoding="utf-8")
    count_font = font_manager.get('hywh.ttf', 35)
    bg = Image.open(GACHA_RES / f'{rank}_background.png').resize((143, 845))
    item_img = Image.open(GACHA_RES / item_type / f'{name}.png')
    rank_img = Image.open(GACHA_RES / f'{rank}_star.png').resize((119, 30))
    if item_type == '角色':
        item_img = item_img.resize((item_img.size[0] + 12, item_img.size[1] + 45))
        item_img.alpha_composite(rank_img, (4, 510))

        item_type_icon = Image.open(GACHA_RES / '元素' / f'{element}.png').resize((80, 80))
        item_img.alpha_composite(item_type_icon, (25, 420))
        bg.alpha_composite(item_img, (3, 125))

    else:
        bg.alpha_composite(item_img, (3, 240))
        bg.alpha_composite(rank_img, (9, 635))

        if item_type_icon := type_json.get(name):
            item_type_icon = Image.open(GACHA_RES / '类型' / f'{item_type_icon}.png').resize((100, 100))

            bg.alpha_composite(item_type_icon, (18, 530))
    if rank == 5 and count != -1:
        draw = ImageDraw.Draw(bg)
        draw_center_text(draw, f'{str(count)}抽', 0, 143, 750, 'white', count_font)
        if dg_time != -1:
            if dg_time == 3:
                draw_center_text(draw, '定轨结束', 0, 143, 785, 'white', count_font)
            else:
                draw_center_text(draw, f'定轨{str(dg_time)}/2', 0, 143, 785, 'white', count_font)
    return bg


async def draw_ten_items(user_id, gacha_data, type_json):
    gacha_list = []
    for _ in range(10):
        role = get_once_data(user_id, gacha_data).copy()
        gacha_list.append(role)
    gacha_list.sort(key=lambda x: x["rank"], reverse=True)
    img = Image.open(GACHA_RES / 'background.png')
    for i, wish in enumerate(gacha_list, start=1):
        rank = wish['rank']
        item_type = wish['item_type']
        name = wish['item_name']
        element = wish.get('item_attr') or type_json[name]
        count = wish['count']
        try:
            dg_time = wish['dg_time']
        except KeyError:
            dg_time = -1
        i_img = draw_single_item(rank, item_type, name, element, count, dg_time)
        img.alpha_composite(i_img, (105 + i_img.size[0] * i, 123))
    img.thumbnail((1024, 768))
    img2 = Image.new("RGB", img.size, (255, 255, 255))
    img2.paste(img, mask=img.split()[3])
    bio = BytesIO()
    img2.save(bio, format='JPEG', quality=100)
    return img2


async def draw_gacha_img(user_id: int, pool: str, num: int, nickname: str):
    gacha_data = await get_gacha_data(pool)
    if not gacha_data:
        return '没有这个池哦，请选择角色1|角色2|武器|常驻'
    type_json = load_json(GACHA_RES / 'type.json', encoding="utf-8")
    time_str = datetime.datetime.strftime(datetime.datetime.now(), '%m-%d %H:%M')
    if num == 1:
        img = await draw_ten_items(user_id, gacha_data, type_json)
    else:
        img = Image.new('RGB', (1024, 575 * num), (255, 255, 255))
        for i in range(num):
            one_img = await draw_ten_items(user_id, gacha_data, type_json)
            img.paste(one_img, (0, 575 * i))
    draw = ImageDraw.Draw(img)
    draw.text((27, 575 * num - 30), f'@{nickname} {time_str}  Created By LittlePaimon', font=font_manager.get('hywh.ttf', 20),
              fill="#8E8E8E")
    return MessageBuild.Image(img, quality=75, mode='RGB')
