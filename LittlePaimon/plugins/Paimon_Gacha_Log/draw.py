import asyncio
import datetime
import math
import random
from typing import Tuple, List, Optional

from LittlePaimon.utils.image import PMImage, get_qq_avatar, font_manager as fm, load_image
from LittlePaimon.utils.message import MessageBuild
from LittlePaimon.utils.path import RESOURCE_BASE_PATH
from .models import GachaLogInfo, FiveStarItem, FourStarItem

avatar_point = [69, 156, 259, 358, 456, 558, 645, 746, 840, 945]
line_point = [88, 182, 282, 378, 477, 574, 673, 769, 864, 967]
bar_color = [('#b6d6f2', '#3d6e99'), ('#c8b6f2', '#593d99'), ('#abede0', '#3a9382'), ("#e3d809", "#646C04")]
name_level_color = [('#f6b9c9', '#a90d35'), ('#f2cab9', '#ff6f30'), ('#b9d8f2', '#157eaa'), ('#dedede', '#707070')]
small_avatar_cache = {}
"""
    角色  武器
欧 50以下 45以下
吉 50-60 45-55
中 60-70 55-65
非 70以上 65以上
"""


async def get_avatar(qid: str, size: Tuple[int, int] = (146, 146)) -> PMImage:
    try:
        avatar = await get_qq_avatar(qid)
        await avatar.resize(size)
        await avatar.to_circle('circle')
        await avatar.add_border(6, '#ddcdba', 'circle')
        return avatar
    except Exception:
        return PMImage(size=size, color=(255, 255, 255, 255))


async def small_avatar(info: FiveStarItem):
    if info.name in small_avatar_cache:
        return small_avatar_cache[info.name]
    bg = PMImage(await load_image(RESOURCE_BASE_PATH / 'gacha_log' / 'small_circle.png'))
    if info.icon:
        img = PMImage(
            await load_image(RESOURCE_BASE_PATH / ('avatar' if info.type == '角色' else 'weapon') / f'{info.icon}.png',
                             size=(42, 42)))
    else:
        img = PMImage(size=(42, 42), color=(255, 255, 255, 0))
    await img.to_circle('circle')
    await bg.paste(img.image, (2, 2))
    small_avatar_cache[info.name] = bg
    return bg


async def detail_avatar(info: FiveStarItem):
    bg = PMImage(await load_image(RESOURCE_BASE_PATH / 'gacha_log' / 'item_avatar_5.png'))
    if info.icon:
        img = PMImage(
            await load_image(RESOURCE_BASE_PATH / ('avatar' if info.type == '角色' else 'weapon') / f'{info.icon}.png',
                             size=(123, 123)))
    else:
        img = PMImage(size=(123, 123), color=(255, 255, 255, 0))
    await bg.paste(img, (14, 14))
    await bg.text(info.name, (0, bg.width), 140, fm.get('hywh', 24),
                  '#33231a', 'center')
    if info.type == '角色' and info.name not in {'迪卢克', '刻晴', '莫娜', '七七', '琴', '提纳里'}:
        up_icon = await load_image(RESOURCE_BASE_PATH / 'gacha_log' / 'up.png')
        await bg.paste(up_icon, (98, 119))
    if info.count < (25 if info.type == '角色' else 20):
        color = name_level_color[0]
    elif (25 if info.type == '角色' else 20) <= info.count < (45 if info.type == '角色' else 35):
        color = name_level_color[1]
    elif (45 if info.type == '角色' else 35) <= info.count < (70 if info.type == '角色' else 60):
        color = name_level_color[2]
    else:
        color = name_level_color[3]
    await bg.draw_rounded_rectangle2((76, 3), (58, 33), 10, color[0], ['ur', 'll'])
    await bg.text(str(info.count), (76, 134), 3, fm.get('bahnschrift_regular', 40, 'Bold'), color[1], 'center')
    return bg


async def draw_pool_detail(pool_name: str,
                           data: List[FiveStarItem],
                           total_count: int,
                           not_out: int,
                           record_time: Tuple[datetime.datetime, datetime.datetime]) -> Optional[
    PMImage]:

    if total_count == 0:
        return None

    total_height = 181 + (446 if len(data) > 3 else 0) + 47 + 192 * math.ceil(len(data) / 6) + 20 + 60
    img = PMImage(size=(1009, total_height), mode='RGBA', color=(255, 255, 255, 0))
    # 橙线
    await img.paste(await load_image(RESOURCE_BASE_PATH / 'general' / 'line.png'), (0, 0))
    pool_type = pool_name[:2]
    await img.text(f'{pool_type}卡池', 25, 11, fm.get('hywh', 30), 'white')
    await img.text(f'{record_time[0].strftime("%Y-%m-%d %H:%M")}~{record_time[1].strftime("%Y-%m-%d %H:%M")}', 990, 15,
                   fm.get('bahnschrift_regular', 30), '#252525', 'right')
    # 数据
    await img.text('平均出货', 174, 137, fm.get('hywh', 24), (24, 24, 24, 102))

    ave = 0
    if data:
        ave = round((total_count - not_out) / len(data), 2)

    await img.text(str(ave), (176, 270), 84,
                   fm.get('bahnschrift_regular', 48, 'Regular'),
                   '#252525', 'center')
    await img.text('总抽卡数', 372, 137, fm.get('hywh', 24), (24, 24, 24, 102))
    await img.text(str(total_count), (372, 467), 84, fm.get('bahnschrift_regular', 48, 'Regular'),
                   '#252525', 'center')
    await img.text('未出五星', 562, 137, fm.get('hywh', 24), (24, 24, 24, 102))
    await img.text(str(not_out), (562, 655), 84, fm.get('bahnschrift_regular', 48, 'Regular'),
                   '#252525', 'center')
    lucky_num = ave if ave > 0 else total_count
    lucky = '欧' if lucky_num <= (45 if pool_type == '武器' else 50) else '吉' if lucky_num <= (55 if pool_type == '武器' else 60) else '中' if lucky_num <= (65 if pool_type == '武器' else 70) else '非'
    await img.paste(await load_image(RESOURCE_BASE_PATH / 'gacha_log' / f'{lucky}{random.randint(1, 3)}.png'), (753, 68))
    # 折线图
    if len(data) > 3:
        last_point = None
        await img.paste(await load_image(RESOURCE_BASE_PATH / 'gacha_log' / 'broken_line_bg.png'), (1, 181))
        i = 0
        for chara in data[-10:]:
            height = int(583 - (chara.count / 90) * 340)
            if last_point:
                await img.draw_line(last_point, (line_point[i], height), '#ff6f30', 4)
            last_point = (line_point[i], height)
            i += 1
        i = 0
        for chara in data[-10:]:
            height = int(583 - (chara.count / 90) * 340)
            point = avatar_point[i]
            await img.paste(await small_avatar(chara), (point, height - 23))
            await img.text(str(chara.count), (point, point + 44), height - 48, fm.get('bahnschrift_regular', 30,
                                                                                      'Regular'), '#040404', 'center')
            i += 1
    if data:
        # 详细数据统计
        chara_bg = PMImage(await load_image(RESOURCE_BASE_PATH / 'gacha_log' / 'detail_bg.png'))
        await chara_bg.stretch((47, chara_bg.height - 20), 192 + 192 * (len(data) // 6), 'height')
        await img.paste(chara_bg, (1, 655 if len(data) > 3 else 181))
        await asyncio.gather(
            *[img.paste(await detail_avatar(data[i]),
                        (18 + i % 6 * 163, (708 if len(data) > 3 else 234) + i // 6 * 192))
            for i in range(len(data))])

    return img


async def draw_four_star(info: FourStarItem) -> PMImage:
    bg = PMImage(await load_image(RESOURCE_BASE_PATH / 'gacha_log' / 'item_avatar_4.png'))
    if info.icon:
        img = PMImage(
            await load_image(RESOURCE_BASE_PATH / ('avatar' if info.type == '角色' else 'weapon') / f'{info.icon}.png',
                             size=(123, 123)))
    else:
        img = PMImage(size=(123, 123), color=(255, 255, 255, 0))
    await img.to_circle('circle')
    await bg.paste(img, (34, 26))
    await bg.text(info.name, (0, bg.width), 163, fm.get('hywh', 24), '#221a33', 'center')
    await bg.text(str(info.num['角色祈愿']), (4, 64), 209, fm.get('bahnschrift_regular', 36, 'Bold'), '#3d6e99',
                  'center')
    await bg.text(str(info.num['武器祈愿']), (65, 125), 209, fm.get('bahnschrift_regular', 36, 'Bold'), '#593d99',
                  'center')
    await bg.text(str(info.num['常驻祈愿'] + info.num['新手祈愿'] + info.num['集录祈愿']), (126, 186), 209, fm.get('bahnschrift_regular', 36, 'Bold'),
                  '#3a9381',
                  'center')
    return bg


async def draw_four_star_detail(data: List[FourStarItem]):
    data.sort(key=lambda x: x.num['角色祈愿'] + x.num['武器祈愿'] + x.num['常驻祈愿'] + x.num['新手祈愿'] + x.num['集录祈愿'], reverse=True)
    bar = await load_image(RESOURCE_BASE_PATH / 'gacha_log' / 'four_star_bar.png')
    total_height = 105 + 260 * math.ceil(len(data) / 5)
    bg = PMImage(size=(1008, total_height), mode='RGBA', color=(255, 255, 255, 0))
    await bg.paste(bar, (0, 0))
    await asyncio.gather(*[bg.paste(await draw_four_star(data[i]), (i % 5 * 204, 105 + i // 5 * 260)) for i in range(len(data))])
    return bg


async def draw_gacha_log(user_id: str, uid: str, nickname: Optional[str], signature: Optional[str], gacha_log: GachaLogInfo):
    img = PMImage(size=(1080, 12000), mode='RGBA', color=(255, 255, 255, 0))
    bg = PMImage(await load_image(RESOURCE_BASE_PATH / 'gacha_log' / 'bg.png'))
    line = await load_image(RESOURCE_BASE_PATH / 'general' / 'line.png')
    # 头像
    avatar = await get_avatar(user_id, (108, 108))
    await img.paste(avatar, (38, 45))
    # 昵称
    await img.text(nickname, 166, 49, fm.get('hywh', 48), '#252525')
    # 签名和uid
    if signature:
        await img.text(signature, 165, 116, fm.get('hywh', 32), '#252525')
        nickname_length = img.text_length(nickname, fm.get('hywh', 48))
        await img.text(f'UID{uid}', 166 + nickname_length + 36, 58,
                       fm.get('bahnschrift_regular', 48, 'Regular'),
                       '#252525')
    else:
        await img.text(f'UID{uid}', 165, 103, fm.get('bahnschrift_regular', 48, 'Regular'), '#252525')

    data5, data4, data_not = gacha_log.get_statistics()
    record_time = gacha_log.get_record_time()
    # 数据总览
    await img.paste(line, (36, 181))
    await img.text('数据总览', 60, 192, fm.get('hywh', 30), 'white')
    await img.text(f'CREATED BY LITTLEPAIMON AT {datetime.datetime.now().strftime("%m-%d %H:%M")}', 1025, 196,
                   fm.get('bahnschrift_regular', 30), '#252525', 'right')
    total_gacha_count = sum(len(pool) for pool in gacha_log.item_list.values())
    out_gacha_count = total_gacha_count - sum(data_not.values())
    total_five_star_count = sum(len(pool) for pool in data5.values())
    five_star_average = round(out_gacha_count / total_five_star_count, 2) if total_five_star_count else 0
    await img.text('平均出货', 209, 335, fm.get('hywh', 24), (24, 24, 24, 102))
    await img.text(str(five_star_average), (211, 305), 286, fm.get('bahnschrift_regular', 48), '#040404', 'center')
    await img.text('总抽卡数', 407, 335, fm.get('hywh', 24), (24, 24, 24, 102))
    await img.text(str(total_gacha_count), (408, 503), 286, fm.get('bahnschrift_regular', 48), '#040404', 'center')
    await img.text('总计出金', 597, 335, fm.get('hywh', 24), (24, 24, 24, 102))
    await img.text(str(total_five_star_count), (598, 694), 286, fm.get('bahnschrift_regular', 48), '#040404', 'center')
    lucky_num = five_star_average if five_star_average>0 else total_gacha_count
    lucky = '欧' if lucky_num <= 50 else '吉' if lucky_num <= 60 else '中' if lucky_num <= 70 else '非'
    await img.paste(await load_image(RESOURCE_BASE_PATH / 'gacha_log' / f'{lucky}{random.randint(1, 3)}.png'), (788, 271))
    four_star_detail = await draw_four_star_detail(list(data4.values()))
    if total_five_star_count:
        chara_pool_per = round(len(data5['角色祈愿']) / total_five_star_count * 100, 1)
        weapon_pool_per = round(len(data5['武器祈愿']) / total_five_star_count * 100, 1)
        new_pool_per = round((len(data5['常驻祈愿']) + len(data5['新手祈愿'])) / total_five_star_count * 100, 1)
        jilu_pool_per = round(len(data5['集录祈愿']) / total_five_star_count * 100, 1)
        now_used_width = 56
        pers = [chara_pool_per, weapon_pool_per, new_pool_per, jilu_pool_per]
        i = 0
        for per in pers:
            if per >= 3:
                await img.draw_rectangle((now_used_width, 399, now_used_width + int(per / 100 * 967), 446),
                                         bar_color[i][0])
                if per >= 10:
                    await img.text(f'{per}%', now_used_width + 18, 410, fm.get('bahnschrift_regular', 30, 'Bold'),
                                   bar_color[i][1])
                now_used_width += int(per / 100 * 967)
            i += 1
        await img.paste(await load_image(RESOURCE_BASE_PATH / 'gacha_log' / 'text.png'), (484, 464))
        now_height = 525
        for pool_name, data in data5.items():
            pool_detail_img = await draw_pool_detail(pool_name, data, len(gacha_log.item_list[pool_name]),
                                                     data_not[pool_name], record_time[pool_name])
            if pool_detail_img:
                await img.paste(pool_detail_img, (36, now_height))
                now_height += pool_detail_img.height
        now_height += 10
        await img.paste(four_star_detail, (36, now_height))
        now_height += four_star_detail.height + 30

        await img.crop((0, 0, 1080, now_height))
        await bg.stretch((50, bg.height - 50), now_height - 100, 'height')

    else:
        await img.paste(four_star_detail, (36, 410))
        await img.crop((0, 0, 1080, 410 + four_star_detail.height + 30))
        await bg.stretch((50, bg.height - 50), img.height - 100, 'height')
    await bg.paste(img, (0, 0))
    return MessageBuild.Image(bg, mode='RGB', quality=80)
