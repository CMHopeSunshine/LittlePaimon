import asyncio
import datetime
import math
from typing import List

from LittlePaimon.database import Character, PlayerInfo, Player
from LittlePaimon.utils.alias import get_chara_icon
from LittlePaimon.utils.genshin import GenshinTools
from LittlePaimon.utils.image import PMImage, font_manager as fm, load_image
from LittlePaimon.utils.message import MessageBuild
from LittlePaimon.utils.path import RESOURCE_BASE_PATH
from .draw_player_card import get_avatar, draw_weapon_icon

RESOURCES = RESOURCE_BASE_PATH / 'chara_bag'
ICON = RESOURCE_BASE_PATH / 'icon'
ARTIFACT_ICON = RESOURCE_BASE_PATH / 'artifact'

talent_color = [('#d5f2b6', '#6d993d'), ('#d5f2b6', '#6d993d'), ('#d5f2b6', '#6d993d'),
                ('#b6d6f2', '#3d6e99'), ('#b6d6f2', '#3d6e99'), ('#b6d6f2', '#3d6e99'),
                ('#c8b6f2', '#593d99'), ('#c8b6f2', '#593d99'), ('#c8b6f2', '#593d99'),
                ('#f2d4b6', '#996b3d'), ('#f2d4b6', '#996b3d'), ('#f2d4b6', '#996b3d'),
                ('#f2b6b6', '#993d3d')]
weapon_affix_color = ['#ffffff', '#6d993d', '#3d6e99', '#593d99', '#996b3d', '#993d3d']
artifact_score_color = {'SSS': '#993d3d', 'SS': '#993d3d', 'S': '#996b3d', 'A': '#593d99', 'B': '#3d6e99',
                        'C':   '#6d993d'}


def sort_characters(characters: List[Character]) -> List[Character]:
    """
    计算角色的分并将排序后的角色列表返回
    :param characters: 角色列表
    :return: 角色列表
    """
    """
    角色等级每级0.7/1分，好感度每级3分，
    天赋等级前6级每级5分，6-13级8分，
    命座数量四星每个15分，五星每个30分，
    武器等级每级0.6/0.6/0.6/0.8/1分，精炼等级每级10/10/10/20/40，
    圣遗物每级0.5/0.8/1分，每个两件套20分，四件套60分，最后按降序排序
    """
    characters = [chara for chara in characters if chara is not None]
    for chara in characters:
        chara.score = chara.level * (0.8 if chara.rarity == 4 else 1) + chara.fetter * 3
        if chara.talents:
            for talent in chara.talents:
                chara.score += talent.level * (5 if talent.level <= 6 else 8)
        chara.score += len(chara.constellation) * (15 if chara.rarity == 4 else 50)
        if chara.weapon:
            chara.score += chara.weapon.level * (
                0.6 if chara.weapon.rarity <= 3 else 0.8 if chara.weapon.rarity == 4 else 1)
            chara.score += chara.weapon.affix_level * (
                10 if chara.weapon.rarity <= 3 else 20 if chara.weapon.rarity == 4 else 50)
        if chara.artifacts:
            suit = GenshinTools.get_artifact_suit(chara.artifacts)
            chara.suit = suit
            chara.score += 60 if len(suit) == 2 and suit[0] == suit[1] else 20 * len(suit)
            for artifact in chara.artifacts:
                chara.score += artifact.level * (0.5 if artifact.rarity <= 3 else 0.8 if artifact.rarity == 4 else 1)
        else:
            chara.suit = []
    return sorted(characters, key=lambda x: x.score, reverse=True)


async def draw_chara_card(info: Character) -> PMImage:
    """
    绘制角色卡片
    :param info: 角色信息
    :return: 角色卡片图
    """
    # 头像
    avatar = PMImage(await load_image(RESOURCE_BASE_PATH / 'avatar' / f'{get_chara_icon(name=info.name)}.png'))
    await avatar.to_circle('circle')
    await avatar.resize((122, 122))
    # 背景
    img = PMImage(await load_image(RESOURCES / f'chara_{info.rarity}star.png'))
    await img.paste(avatar, (59, 26))
    name_length = img.text_length(info.name, fm.get('hywh', 24))
    level_length = img.text_length(f'LV{info.level}', fm.get('bahnschrift_bold', 24, 'Bold'))
    left_point = (img.width - level_length - name_length - 10) / 2
    # 角色名
    await img.text(info.name, left_point, 161, fm.get('hywh', 24), '#252525')
    # 等级
    await img.text(f'LV{info.level}', left_point + name_length + 10, 163, fm.get('bahnschrift_bold', 24, 'Bold'),
                   '#593d99' if info.rarity == 4 else '#964e2e')
    # 元素图标
    await img.paste(await load_image(ICON / f'{info.element}.png'), (9, 12))
    # 命座图标
    await img.paste(await load_image(ICON / f'命之座{len(info.constellation)}.png'), (197, 11))
    # 好感度
    await img.paste(await load_image(ICON / f'好感度{info.fetter}.png', size=0.6), (189, 118))
    # 武器图标
    weapon = await draw_weapon_icon(info.weapon, (60, 60))
    await img.paste(weapon, (14, 196))
    # 武器名
    await img.text(info.weapon.name, 79, 195, fm.get('hywh', 24), '#33231a')
    # 武器等级
    await img.text(f'Lv.{info.weapon.level}', 80, 227, fm.get('bahnschrift_bold', 24, 'Bold'),
                   weapon_affix_color[info.weapon.affix_level])
    # 武器精炼图标
    await img.paste(await load_image(ICON / f'精炼{info.weapon.affix_level}.png'), (150, 227))
    # 圣遗物图标
    if any(artifact.rarity == 5 for artifact in info.artifacts):
        artifact_bg = await load_image(ICON / 'star5.png', size=(60, 60))
    elif any(artifact.rarity == 4 for artifact in info.artifacts):
        artifact_bg = await load_image(ICON / 'star4.png', size=(60, 60))
    else:
        artifact_bg = await load_image(ICON / 'star3.png', size=(60, 60))
    await img.paste(artifact_bg, (14, 265))
    if len(info.suit) == 2:
        if info.suit[0] == info.suit[1]:
            await img.paste(await load_image(ARTIFACT_ICON / f'{info.suit[0][1]}.png', mode='RGBA', size=(60, 60)),
                            (14, 265))
            suit_name = f'{info.suit[0][0][:2]}四件套'
        else:
            await img.paste(await load_image(ARTIFACT_ICON / f'{info.suit[0][1]}.png', mode='RGBA', size=(42, 42)),
                            (14, 265))
            await img.paste(await load_image(ARTIFACT_ICON / f'{info.suit[1][1]}.png', mode='RGBA', size=(42, 42)),
                            (36, 283))
            suit_name = f'{info.suit[0][0][:2]}+{info.suit[1][0][:2]}'
    elif len(info.suit) == 1:
        suit_name = f'{info.suit[0][0][:2]}+散搭'
        await img.paste(await load_image(ARTIFACT_ICON / f'{info.suit[0][1]}.png', mode='RGBA', size=(42, 42)),
                        (14, 265))
        await img.paste(await load_image(ARTIFACT_ICON / '不知名花.png', mode='RGBA', size=(32, 32)),
                        (40, 290))
    elif len(info.artifacts):
        suit_name = '散搭圣遗物'
        await img.paste(await load_image(ARTIFACT_ICON / '不知名花.png', mode='RGBA', size=(32, 32)),
                        (18, 272))
        await img.paste(await load_image(ARTIFACT_ICON / '不知名毛.png', mode='RGBA', size=(32, 32)),
                        (40, 290))
    else:
        suit_name = '未装备圣遗物'
        await img.paste(await load_image(ARTIFACT_ICON / '不知名花.png', mode='RGBA', size=(50, 50)),
                        (19, 271))
    # 圣遗物名
    await img.text(suit_name, 82, 265, fm.get('hywh', 24), '#252525')
    # 圣遗物评分
    score, value = GenshinTools.artifacts_total_score(info, info.artifacts)
    if score is not None:
        rank = 'SSS' if value >= 140 else 'SS' if 120 <= value < 140 else 'S' if 100 <= value < 120 else 'A' if 75 <= value < 100 else 'B' if 50 <= value < 75 else 'C'
        await img.text(str(score), 81, 296, fm.get('bahnschrift_bold', 24, 'Bold'), artifact_score_color[rank])
        await img.paste(await load_image(ICON / f'rank{rank}.png'), (150, 297))
    else:
        await img.text('---', 81, 296, fm.get('hywh', 24), '#33231a')
    # 天赋等级色块
    if not info.talents:
        await img.draw_rounded_rectangle2((4, 339), (228, 69), 15, '#d5f2b6', ['ll', 'lr'])
        await img.text('未获取等级', (4, 232), (339, 408), fm.get('hywh', 24), '#6d993d', 'center')
    else:
        for i in range(3):
            bg_color = talent_color[info.talents[i].level - 1][0]
            text_color = talent_color[info.talents[i].level - 1][1]
            if i == 0:
                await img.draw_rounded_rectangle2((4, 339), (76, 69), 15, bg_color, ['ll'])
                await img.text(str(info.talents[i].level), (4, 80), (339, 408), fm.get('bahnschrift_bold', 48, 'Bold'),
                               text_color, 'center')
            elif i == 1:
                await img.draw_rounded_rectangle2((81, 339), (76, 69), 15, bg_color, [])
                await img.text(str(info.talents[i].level), (81, 157), (339, 408),
                               fm.get('bahnschrift_bold', 48, 'Bold'),
                               text_color, 'center')
            else:
                if info.name in ['神里绫华', '莫娜']:
                    i += 1
                await img.draw_rounded_rectangle2((156, 339), (76, 69), 15, bg_color, ['lr'])
                await img.text(str(info.talents[i].level), (157, 233), (339, 408),
                               fm.get('bahnschrift_bold', 48, 'Bold'),
                               text_color, 'center')
        await img.draw_line((80, 339), (80, 413), '#593d99' if info.rarity == 4 else '#964e2e', 2)
        await img.draw_line((157, 339), (157, 413), '#593d99' if info.rarity == 4 else '#964e2e', 2)
    await img.draw_line((0, 339), (237, 339), '#593d99' if info.rarity == 4 else '#964e2e', 2)
    return img


async def draw_chara_bag(player: Player, info: PlayerInfo, characters: List[Character]):
    characters = sort_characters(characters)
    # 确定角色行数，4个为一行
    row = math.ceil(len(characters) / 4)
    img = PMImage(await load_image(RESOURCES / 'bg.png'))
    await img.stretch((255, 1534), 428 * row - 21, 'height')
    # 头像
    avatar = await get_avatar(player.user_id, (108, 108))
    await img.paste(avatar, (38, 45))
    # 昵称
    await img.text(info.nickname, 166, 49, fm.get('hywh', 48), '#252525')
    # 签名和uid
    if info.signature:
        await img.text(info.signature, 165, 116, fm.get('hywh', 32), '#252525')
        nickname_length = img.text_length(info.nickname, fm.get('hywh', 48))
        await img.text(f'UID{player.uid}', 166 + nickname_length + 36, 58, fm.get('bahnschrift_regular', 48, 'Regular'),
                       '#252525')
    else:
        await img.text(f'UID{player.uid}', 165, 103, fm.get('bahnschrift_regular', 48, 'Regular'), '#252525')

    # 角色数量和logo
    await img.text(f'共计{len(characters)}名角色', 237, 190, fm.get('hywh', 30), '#252525')
    await img.text(f'CREATED BY LITTLEPAIMON AT {datetime.datetime.now().strftime("%m-%d %H:%M")}', 1031, 194,
                   fm.get('bahnschrift_bold', 30, 'Bold'), '#252525', 'right')

    # 角色列表
    await asyncio.gather(
        *[img.paste(await draw_chara_card(characters[i]), (38 + 257 * (i % 4), 255 + 428 * (i // 4))) for i in
          range(len(characters))])

    return MessageBuild.Image(img, quality=85, mode='RGB')
