from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .abyss_rate_data import get_rate, get_formation_rate
from ..utils.alias_handler import get_id_by_name
from ..utils.message_util import MessageBuild

res_path = Path() / 'resources' / 'LittlePaimon'


def get_font(size, font_type='msyh.ttc'):
    return ImageFont.truetype(str(res_path / font_type), size)


async def draw_rate_rank(type: str = 'role', mode: str = 'used'):
    data = await get_rate(type)
    if not data or data['code'] != '200':
        return '获取工坊数据失败，请稍后再试'
    col = int(len(data['result']['rateList']) / 5) if len(data['result']['rateList']) % 5 == 0 else int(len(data['result']['rateList']) / 5) + 1
    top_img = Image.open(res_path / 'player_card' / '卡片顶部无字.png').resize((1080, 316))
    body_img = Image.open(res_path / 'player_card' / '卡片身体.png').resize((1080, 226))
    bottom_img = Image.open(res_path / 'player_card' / '卡片底部.png').resize((1080, 72))
    bg_img = Image.new('RGBA', (1080, top_img.height + col * 220 + bottom_img.height + 50))
    bg_img.paste(top_img, (0, 0))
    bg_draw = ImageDraw.Draw(bg_img)
    bg_draw.text((70, 55), '2.8深境螺旋登场率排行榜', fill='black', font=get_font(40, 'msyhbd.ttc'))
    bg_draw.text((70, 110), f'当前共{data["result"]["userCount"]}份样本数据', fill='black', font=get_font(35))
    for i in range(0, col + 1):
        bg_img.paste(body_img, (0, top_img.height + i * body_img.height))
    bg_img.paste(bottom_img, (0, top_img.height + col * 220 + 50))
    bg_draw.text((130, bg_img.height - 86), 'Created by LittlePaimon | Data from 原神创意工坊', fill='black', font=get_font(35))
    n = 0
    for role in data['result']['rateList']:
        role_img = Image.open(res_path / 'role_card' / f'{get_id_by_name(role["name"])}.png').resize((160, 200))
        role_draw = ImageDraw.Draw(role_img)
        role_draw.text((28 if len(role['rate']) == 6 else 38, 158), role['rate'], font=get_font(30), fill='black')
        bg_img.alpha_composite(role_img, (50 + 204 * (n % 5), 180 + 240 * int(n / 5)))
        n += 1

    return MessageBuild.Image(bg_img, quality=75)


async def draw_teams_rate(floor='上半半'):
    data = await get_formation_rate(1 if floor == '上半' else 2)
    if not data or data['code'] != '200':
        return '获取工坊数据失败，请稍后再试'
    rateList = data['result']['rateList'][0:10]
    top_img = Image.open(res_path / 'player_card' / '卡片顶部无字.png').resize((1080, 316))
    body_img = Image.open(res_path / 'player_card' / '卡片身体.png').resize((1080, 240))
    bottom_img = Image.open(res_path / 'player_card' / '卡片底部.png').resize((1080, 72))
    bg_img = Image.new('RGBA', (1080, top_img.height + 10 * body_img.height + bottom_img.height - 130))
    bg_img.paste(top_img, (0, 0))
    bg_draw = ImageDraw.Draw(bg_img)
    bg_draw.text((70, 55), f'2.8深境螺旋阵容出场率 | {floor}', fill='black', font=get_font(40, 'msyhbd.ttc'))
    bg_draw.text((70, 110), f'当前共{data["result"]["userCount"]}份样本数据', fill='black', font=get_font(35))
    for i in range(0, 10):
        bg_img.paste(body_img, (0, top_img.height + i * body_img.height))
    bg_img.paste(bottom_img, (0, top_img.height + 10 * 240 - 130))
    bg_draw.text((130, bg_img.height - 86), 'Created by LittlePaimon | Data from 原神创意工坊', fill='black', font=get_font(35))
    n = 0
    for team in rateList:
        bg_draw.text((48, 240 + 240 * n), '排名', fill='grey', font=get_font(30))
        bg_draw.text((65 if n != 9 else 55, 275 + 240 * n), str(n + 1), fill='black', font=get_font(35))
        bg_draw.text((934, 240 + 240 * n), '出场率', fill='grey', font=get_font(30))
        bg_draw.text((930, 275 + 240 * n), team['rate'], fill='black', font=get_font(35))
        r = 0
        for role in team['formation']:
            role_img = Image.open(
                res_path / 'role_card' / f'{get_id_by_name(role["name"])}.png').resize((160, 200))
            role_draw = ImageDraw.Draw(role_img)
            role_draw.text((80 - 15 * len(role['name']), 158), role['name'], font=get_font(30), fill='black')
            bg_img.alpha_composite(role_img, (130 + 204 * r, 180 + 240 * n))
            r += 1
        n += 1

    return MessageBuild.Image(bg_img, quality=75)

