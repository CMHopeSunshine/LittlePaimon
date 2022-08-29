from PIL import Image, ImageDraw, ImageFont

from LittlePaimon.utils.files import load_image
from LittlePaimon.utils.image import PMImage, font_manager as fm
from LittlePaimon.utils.alias import get_chara_icon
from LittlePaimon.utils.message import MessageBuild
from LittlePaimon.config import RESOURCE_BASE_PATH
from .abyss_rate_data import get_rate, get_formation_rate


async def draw_rate_rank(type: str = 'role'):
    data = await get_rate(type)
    if not data or data['code'] != '200':
        return '获取工坊数据失败，请稍后再试'
    col = len(data['result']['rateList']) // 5 if len(data['result']['rateList']) % 5 == 0 else len(
        data['result']['rateList']) // 5 + 1

    top_img = await load_image(RESOURCE_BASE_PATH / 'general' / '卡片顶部无字.png', size=(1080, 316))
    body_img = await load_image(RESOURCE_BASE_PATH / 'general' / '卡片身体.png', size=(1080, 226))
    bottom_img = await load_image(RESOURCE_BASE_PATH / 'general' / '卡片底部.png', size=(1080, 72))
    bg_img = PMImage(size=(1080, top_img.height + col * 220 + bottom_img.height + 50), mode='RGBA')
    await bg_img.paste(top_img, (0, 0))
    await bg_img.text('3.0深境螺旋登场率排行榜', 70, 55, color='black', font=fm.get('msyhbd.ttc', 40))
    await bg_img.text(f'当前共{data["result"]["userCount"]}份样本数据', 70, 110, color='black', font=fm.get('msyh.ttc', 35))
    for i in range(col + 1):
        await bg_img.paste(body_img, (0, top_img.height + i * body_img.height))
    await bg_img.paste(bottom_img, (0, top_img.height + col * 220 + 50))
    await bg_img.text('Created by LittlePaimon | Data from 原神创意工坊', 130, bg_img.height - 86, color='black',
                      font=fm.get('msyh.ttc', 35))
    for n, role in enumerate(data['result']['rateList']):
        role_card = PMImage(size=(160, 200), color=(200, 200, 200, 255), mode='RGBA')
        role_img = await load_image(RESOURCE_BASE_PATH / 'avatar_card' / f'{get_chara_icon(name=role["name"], icon_type="card")}.png', size=(160, 160))
        await role_card.paste(role_img, (0, 0))
        await role_card.text((28 if len(role['rate']) == 6 else 38, 158), role['rate'], font=fm.get('msyh.ttc', 30),
                             color='black')
        await bg_img.paste(role_card, (50 + 204 * (n % 5), 180 + 240 * int(n / 5)))
    return MessageBuild.Image(bg_img, quality=75)


# async def draw_teams_rate(floor='上半半'):
#     data = await get_formation_rate(1 if floor == '上半' else 2)
#     if not data or data['code'] != '200':
#         return '获取工坊数据失败，请稍后再试'
#     rateList = data['result']['rateList'][:10]
#     top_img = Image.open(RESOURCE_BASE_PATH / 'general' / '卡片顶部无字.png').resize((1080, 316))
#
#     body_img = Image.open(RESOURCE_BASE_PATH / 'general' / '卡片身体.png').resize((1080, 240))
#
#     bottom_img = Image.open(RESOURCE_BASE_PATH / 'general' / '卡片底部.png').resize((1080, 72))
#
#     bg_img = Image.new('RGBA', (1080, top_img.height + 10 * body_img.height + bottom_img.height - 130))
#
#     bg_img.paste(top_img, (0, 0))
#     bg_draw = ImageDraw.Draw(bg_img)
#     bg_draw.text((70, 55), f'3.0深境螺旋阵容出场率 | {floor}', fill='black', font=fm.get('msyhbd.ttc', 40))
#
#     bg_draw.text((70, 110), f'当前共{data["result"]["userCount"]}份样本数据', fill='black', font=fm.get('msyh.ttc', 35))
#
#     for i in range(10):
#         bg_img.paste(body_img, (0, top_img.height + i * body_img.height))
#     bg_img.paste(bottom_img, (0, top_img.height + 10 * 240 - 130))
#     bg_draw.text((130, bg_img.height - 86), 'Created by LittlePaimon | Data from 原神创意工坊', fill='black',
#                  font=fm.get('msyh.ttc', 35))
#
#     for n, team in enumerate(rateList):
#         bg_draw.text((48, 240 + 240 * n), '排名', fill='grey', font=get_font(30))
#         bg_draw.text((65 if n != 9 else 55, 275 + 240 * n), str(n + 1), fill='black', font=fm.get('msyh.ttc', 35))
#
#         bg_draw.text((934, 240 + 240 * n), '出场率', fill='grey', font=get_font(30))
#         bg_draw.text((930, 275 + 240 * n), team['rate'], fill='black', font=fm.get('msyh.ttc', 35))
#
#         for r, role in enumerate(team['formation']):
#             role_img = Image.open(CARD / f'{get_icon(name=role["name"], icon_type="card")}.png').resize((160, 200))
#
#             role_draw = ImageDraw.Draw(role_img)
#             role_draw.text((80 - 15 * len(role['name']), 158), role['name'], font=get_font(30), fill='black')
#
#             bg_img.alpha_composite(role_img, (130 + 204 * r, 180 + 240 * n))
#     return MessageBuild.Image(bg_img, quality=75)
