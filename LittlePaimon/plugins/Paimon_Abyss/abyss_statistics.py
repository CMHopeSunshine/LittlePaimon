import datetime
from collections import Counter
from typing import Any, Dict, Tuple

import pytz
from nonebot.adapters.onebot.v11 import Bot

from LittlePaimon.database import AbyssInfo
from LittlePaimon.utils.image import PMImage
from LittlePaimon.utils.image import font_manager as fm
from LittlePaimon.utils.image import get_qq_avatar, load_image
from LittlePaimon.utils.message import MessageBuild
from LittlePaimon.utils.path import RESOURCE_BASE_PATH
from LittlePaimon.utils.requests import aiorequests


async def get_user_avatar(user_id: str, size: Tuple[int, int] = (60, 60)):
    try:
        img = await get_qq_avatar(user_id)
        await img.resize(size)
        await img.to_circle('circle')
        return img
    except Exception:
        return PMImage(size=size, color=(255, 255, 255, 255))


async def get_group_avatar(group_id: str):
    try:
        img = await aiorequests.get_img(
            f'https://p.qlogo.cn/gh/{group_id}/{group_id}/100', size=(110, 110)
        )
        img = PMImage(img)
        await img.to_circle('circle')
        return img
    except Exception:
        return PMImage(size=(110, 110), color=(255, 255, 255, 255))


async def get_statistics(group_id: int, bot: Bot):
    if not (info_list := await AbyssInfo.all()):
        return '本群还没有深渊战斗数据哦！'
    member_list = await bot.get_group_member_list(group_id=group_id)
    member_id_list = [str(member['user_id']) for member in member_list]
    info_list = [
        info
        for info in info_list
        if info.user_id in member_id_list
        and info.total_battle
        and info.total_star
        and info.max_damage
        and info.max_take_damage
    ]
    now = datetime.datetime.now().replace(tzinfo=pytz.timezone('Asia/Shanghai'))
    info_list = [info for info in info_list if info.start_time <= now <= info.end_time]
    if not info_list:
        return '本群还没有深渊战斗数据哦！'
    elif len(info_list) < 3:
        return '本群深渊有效战斗数据不足3人，无法生成统计图！'
    for info in info_list:
        if info.nickname is None:
            for member in member_list:
                if info.user_id == str(member['user_id']):
                    info.nickname = member['card'] or member['nickname']
                    break
    data = {
        '群号': str(group_id),
        '群名称': (await bot.get_group_info(group_id=group_id))['group_name'],
    }
    # 数据数
    info_num = len(info_list)
    data['总人数'] = info_num
    # 满星人数
    full_star_num = len([info for info in info_list if info.total_star >= 36])
    data['满星人数'] = full_star_num
    # 平均星数
    average_star = round(sum(info.total_star for info in info_list) / info_num, 1)
    data['平均星数'] = average_star
    # 平均战斗次数
    average_battle_num = round(
        sum(info.total_battle for info in info_list) / info_num, 1
    )
    data['平均战斗次数'] = average_battle_num
    # 最高伤害角色
    # max_damage = max(info_list, key=lambda x: x.max_damage.value)
    max_damage = sorted(info_list, key=lambda x: x.max_damage.value, reverse=True)
    data['最高伤害'] = [
        {
            '图标': info.max_damage.icon,
            '稀有度': info.max_damage.rarity,
            '等级': info.max_damage.level,
            '数值': info.max_damage.value,
            # '命座': (await Character.filter(user_id=info.user_id, uid=info.uid, character_id=info.max_damage.character_id).first()).constellation,
            '用户名': info.nickname,
            'qq号': info.user_id,
            'uid': info.uid,
        }
        for info in max_damage[:3]
    ]
    # 最多承伤角色
    max_take_damage = sorted(
        info_list, key=lambda x: x.max_take_damage.value, reverse=True
    )
    data['最高承受伤害'] = [
        {
            '图标': info.max_take_damage.icon,
            '稀有度': info.max_take_damage.rarity,
            '等级': info.max_take_damage.level,
            '数值': info.max_take_damage.value,
            # '命座': (await Character.filter(user_id=info.user_id, uid=info.uid, character_id=info.max_damage.character_id).first()).constellation,
            '用户名': info.nickname,
            'qq号': info.user_id,
            'uid': info.uid,
        }
        for info in max_take_damage[:3]
    ]
    # 11、12层阵容
    battle_characters_up11 = Counter()
    battle_characters_down11 = Counter()
    battle_characters_up12 = Counter()
    battle_characters_down12 = Counter()
    for info in info_list:
        if floor11 := info.floors.get(11):
            for battles in floor11.battles_up:
                for character in battles.characters:
                    battle_characters_up11[f'{character.icon}-{character.rarity}'] += 1
            for battles in floor11.battles_down:
                for character in battles.characters:
                    battle_characters_down11[
                        f'{character.icon}-{character.rarity}'
                    ] += 1
        if floor12 := info.floors.get(12):
            for battles in floor12.battles_up:
                for character in battles.characters:
                    battle_characters_up12[f'{character.icon}-{character.rarity}'] += 1
            for battles in floor12.battles_down:
                for character in battles.characters:
                    battle_characters_down12[
                        f'{character.icon}-{character.rarity}'
                    ] += 1
    data['11层上半'] = battle_characters_up11.most_common(4)
    data['11层下半'] = battle_characters_down11.most_common(4)
    data['12层上半'] = battle_characters_up12.most_common(4)
    data['12层下半'] = battle_characters_down12.most_common(4)
    return await draw_statistics_img(data)


async def draw_statistics_img(data: Dict[str, Any]):
    img = PMImage(image=RESOURCE_BASE_PATH / 'abyss' / 'statistics_bg.png')
    box = {
        '4big': await load_image(RESOURCE_BASE_PATH / 'abyss' / '4bigbox.png'),
        '4small': await load_image(RESOURCE_BASE_PATH / 'abyss' / '4smallbox.png'),
        '5big': await load_image(RESOURCE_BASE_PATH / 'abyss' / '5bigbox.png'),
        '5small': await load_image(RESOURCE_BASE_PATH / 'abyss' / '5smallbox.png'),
        '4bg': await load_image(
            RESOURCE_BASE_PATH / 'icon' / 'star4_no_line.png', size=(95, 95)
        ),
        '5bg': await load_image(
            RESOURCE_BASE_PATH / 'icon' / 'star5_no_line.png', size=(95, 95)
        ),
    }
    avatar = await get_group_avatar(data['群号'])
    await img.paste(avatar, (38, 47))
    await img.text(data['群名称'], 162, 58, fm.get('hywh', 48), '#040404')
    await img.text(data['群号'], 165, 116, fm.get('hywh', 36), '#040404')
    await img.text(
        f'CREATED BY LITTLEPAIMON AT {datetime.datetime.now().strftime("%m-%d %H:%M")}',
        1033,
        195,
        fm.get('bahnschrift_regular.ttf', 30),
        '#8c4c2e',
        'right',
    )
    await img.text(
        str(data['总人数']),
        (233, 352),
        296,
        fm.get('bahnschrift_regular.ttf', 48),
        '#040404',
        'center',
    )
    await img.text(
        str(data['平均星数']),
        (492, 586),
        296,
        fm.get('bahnschrift_regular.ttf', 48),
        '#040404',
        'center',
    )
    await img.text(
        str(data['平均战斗次数']),
        (698, 840),
        296,
        fm.get('bahnschrift_regular.ttf', 48),
        '#040404',
        'center',
    )
    # 满星人数
    full_num = [data['满星人数'] / data['总人数'], 1 - data['满星人数'] / data['总人数']]
    now_used_width = 36
    if full_num[0] > 0.03:
        await img.draw_rectangle(
            (now_used_width, 402, now_used_width + int(1007 * full_num[0]), 449),
            '#b6d6f2',
        )
        await img.text(
            str(data['满星人数']),
            now_used_width + 18,
            413,
            fm.get('bahnschrift_regular.ttf', 30),
            '#3d6e99',
        )
        now_used_width += int(1007 * full_num[0])
    if full_num[1] > 0.03:
        await img.draw_rectangle(
            (now_used_width, 402, now_used_width + int(1007 * full_num[1]), 449),
            '#c8b6f2',
        )
        await img.text(
            str(data['总人数'] - data['满星人数']),
            now_used_width + 18,
            413,
            fm.get('bahnschrift_regular.ttf', 30),
            '#593d99',
        )
    # 最高伤害
    await img.paste(box[f'{data["最高伤害"][0]["稀有度"]}big'], (39, 512))
    await img.paste(box[f'{data["最高伤害"][1]["稀有度"]}small'], (39, 664))
    await img.paste(box[f'{data["最高伤害"][2]["稀有度"]}small'], (296, 664))
    await img.paste(
        await load_image(
            RESOURCE_BASE_PATH / 'avatar' / f'{data["最高伤害"][0]["图标"]}.png',
            size=(124, 124),
        ),
        (44, 525),
    )
    await img.paste(
        await load_image(
            RESOURCE_BASE_PATH / 'avatar' / f'{data["最高伤害"][1]["图标"]}.png',
            size=(82, 82),
        ),
        (45, 673),
    )
    await img.paste(
        await load_image(
            RESOURCE_BASE_PATH / 'avatar' / f'{data["最高伤害"][2]["图标"]}.png',
            size=(82, 82),
        ),
        (300, 673),
    )
    await img.paste(await get_user_avatar(data['最高伤害'][0]['qq号']), (112, 588))
    await img.paste(await get_user_avatar(data['最高伤害'][1]['qq号'], (42, 42)), (87, 713))
    await img.paste(await get_user_avatar(data['最高伤害'][2]['qq号'], (42, 42)), (344, 713))
    await img.text('最强一击', 180, 515, fm.get('hywh', 30), '#040404')
    await img.text('第二名', 139, 668, fm.get('hywh', 22), '#040404')
    await img.text('第三名', 397, 668, fm.get('hywh', 22), '#040404')
    await img.text(
        str(data['最高伤害'][0]['数值']),
        180,
        547,
        fm.get('bahnschrift_regular.ttf', 68),
        '#040404',
    )
    await img.text(
        str(data['最高伤害'][1]['数值']),
        137,
        693,
        fm.get('bahnschrift_regular.ttf', 38),
        '#040404',
    )
    await img.text(
        str(data['最高伤害'][2]['数值']),
        395,
        693,
        fm.get('bahnschrift_regular.ttf', 38),
        '#040404',
    )
    await img.text(data['最高伤害'][0]['用户名'][:11], 180, 610, fm.get('hywh', 30), '#040404')
    await img.text(data['最高伤害'][1]['用户名'][:6], 137, 726, fm.get('hywh', 22), '#040404')
    await img.text(data['最高伤害'][2]['用户名'][:6], 395, 726, fm.get('hywh', 22), '#040404')

    # 最高承伤
    await img.paste(box[f'{data["最高承受伤害"][0]["稀有度"]}big'], (554, 512))
    await img.paste(box[f'{data["最高承受伤害"][1]["稀有度"]}small'], (552, 664))
    await img.paste(box[f'{data["最高承受伤害"][2]["稀有度"]}small'], (808, 664))
    await img.paste(
        await load_image(
            RESOURCE_BASE_PATH / 'avatar' / f'{data["最高承受伤害"][0]["图标"]}.png',
            size=(124, 124),
        ),
        (560, 525),
    )
    await img.paste(
        await load_image(
            RESOURCE_BASE_PATH / 'avatar' / f'{data["最高承受伤害"][1]["图标"]}.png',
            size=(82, 82),
        ),
        (557, 673),
    )
    await img.paste(
        await load_image(
            RESOURCE_BASE_PATH / 'avatar' / f'{data["最高承受伤害"][2]["图标"]}.png',
            size=(82, 82),
        ),
        (815, 673),
    )
    await img.paste(await get_user_avatar(data['最高承受伤害'][0]['qq号']), (623, 588))
    await img.paste(
        await get_user_avatar(data['最高承受伤害'][1]['qq号'], (42, 42)), (600, 713)
    )
    await img.paste(
        await get_user_avatar(data['最高承受伤害'][2]['qq号'], (42, 42)), (857, 713)
    )
    await img.text('最多承伤', 693, 515, fm.get('hywh', 30), '#040404')
    await img.text('第二名', 652, 668, fm.get('hywh', 22), '#040404')
    await img.text('第三名', 910, 668, fm.get('hywh', 22), '#040404')
    await img.text(
        str(data['最高承受伤害'][0]['数值']),
        693,
        547,
        fm.get('bahnschrift_regular.ttf', 68),
        '#040404',
    )
    await img.text(
        str(data['最高承受伤害'][1]['数值']),
        650,
        693,
        fm.get('bahnschrift_regular.ttf', 38),
        '#040404',
    )
    await img.text(
        str(data['最高承受伤害'][2]['数值']),
        908,
        693,
        fm.get('bahnschrift_regular.ttf', 38),
        '#040404',
    )
    await img.text(
        data['最高承受伤害'][0]['用户名'][:11], 693, 610, fm.get('hywh', 30), '#040404'
    )
    await img.text(
        data['最高承受伤害'][1]['用户名'][:6], 650, 726, fm.get('hywh', 22), '#040404'
    )
    await img.text(
        data['最高承受伤害'][2]['用户名'][:6], 908, 726, fm.get('hywh', 22), '#040404'
    )

    tag = await load_image(RESOURCE_BASE_PATH / 'general' / 'tag.png')
    # 角色出场率
    for i in range(4):
        try:
            icon, rarity, count = (
                data['11层上半'][i][0].split('-')[0],
                data['11层上半'][i][0].split('-')[1],
                data['11层上半'][i][1],
            )
            await img.paste(box[f'{rarity}bg'], (182 + i * 101, 867))
            await img.paste(
                await load_image(
                    RESOURCE_BASE_PATH / 'avatar' / f'{icon}.png', size=(95, 95)
                ),
                (182 + i * 101, 867),
            )
            await img.paste(tag, (236 + i * 101, 942))
            await img.text(
                str(count),
                (236 + i * 101, 277 + i * 101),
                943,
                fm.get('bahnschrift_regular.ttf', 19),
                'white',
                'center',
            )

            icon, rarity, count = (
                data['11层下半'][i][0].split('-')[0],
                data['11层下半'][i][0].split('-')[1],
                data['11层下半'][i][1],
            )
            await img.paste(box[f'{rarity}bg'], (642 + i * 101, 867))
            await img.paste(
                await load_image(
                    RESOURCE_BASE_PATH / 'avatar' / f'{icon}.png', size=(95, 95)
                ),
                (642 + i * 101, 867),
            )
            await img.paste(tag, (696 + i * 101, 942))
            await img.text(
                str(count),
                (696 + i * 101, 737 + i * 101),
                943,
                fm.get('bahnschrift_regular.ttf', 19),
                'white',
                'center',
            )

            icon, rarity, count = (
                data['12层上半'][i][0].split('-')[0],
                data['12层上半'][i][0].split('-')[1],
                data['12层上半'][i][1],
            )
            await img.paste(box[f'{rarity}bg'], (182 + i * 101, 983))
            await img.paste(
                await load_image(
                    RESOURCE_BASE_PATH / 'avatar' / f'{icon}.png', size=(95, 95)
                ),
                (182 + i * 101, 983),
            )
            await img.paste(tag, (236 + i * 101, 1058))
            await img.text(
                str(count),
                (236 + i * 101, 278 + i * 101),
                1059,
                fm.get('bahnschrift_regular.ttf', 19),
                'white',
                'center',
            )

            icon, rarity, count = (
                data['12层下半'][i][0].split('-')[0],
                data['12层下半'][i][0].split('-')[1],
                data['12层下半'][i][1],
            )
            await img.paste(box[f'{rarity}bg'], (642 + i * 101, 983))
            await img.paste(
                await load_image(
                    RESOURCE_BASE_PATH / 'avatar' / f'{icon}.png', size=(95, 95)
                ),
                (642 + i * 101, 983),
            )
            await img.paste(tag, (696 + i * 101, 1058))
            await img.text(
                str(count),
                (696 + i * 101, 737 + i * 101),
                1059,
                fm.get('bahnschrift_regular.ttf', 19),
                'white',
                'center',
            )
            i += 1
        except IndexError:
            pass

    return MessageBuild.Image(img, mode='RGB', quality=80)
