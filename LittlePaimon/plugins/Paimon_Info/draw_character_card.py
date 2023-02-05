import math

from LittlePaimon.database import Character
from LittlePaimon.utils.genshin import GenshinTools
from LittlePaimon.utils.image import PMImage, font_manager as fm, load_image
from LittlePaimon.utils.message import MessageBuild
from LittlePaimon.utils.path import RESOURCE_BASE_PATH
from LittlePaimon.utils.requests import aiorequests

ICON = RESOURCE_BASE_PATH / 'icon'
ARTIFACT_ICON = RESOURCE_BASE_PATH / 'artifact'

colors = [('#d5f2b6', '#6d993d'),
          ('#d5f2b6', '#6d993d'),
          ('#b6d6f2', '#3d6e99'),
          ('#c8b6f2', '#593d99'),
          ('#f2d4b6', '#996b3d'),
          ('#f2b6b6', '#993d3d'),
          ('#f2b6b6', '#993d3d')]

talent_color = [('#d5f2b6', '#6d993d'), ('#d5f2b6', '#6d993d'), ('#d5f2b6', '#6d993d'),
                ('#b6d6f2', '#3d6e99'), ('#b6d6f2', '#3d6e99'), ('#b6d6f2', '#3d6e99'),
                ('#c8b6f2', '#593d99'), ('#c8b6f2', '#593d99'), ('#c8b6f2', '#593d99'),
                ('#f2d4b6', '#996b3d'), ('#f2d4b6', '#996b3d'), ('#f2d4b6', '#996b3d'),
                ('#f2b6b6', '#993d3d')]


async def draw_chara_card(info: Character):
    img = await aiorequests.get_img(f'https://genshin-res.cherishmoon.fun/img?name={info.name}', mode='RGBA', follow_redirects=True)
    if img == 'No Such File':
        return '暂时没有这个角色的同人图哦~', None
    # 新建卡片
    card = PMImage(size=(385, 500), color=(0, 0, 0, 0), mode='RGBA')
    await card.draw_rounded_rectangle2((0, 0), (card.width, card.height), 80, (0, 0, 0, 153), ['ur'])
    # 好感度
    await card.paste(await load_image(ICON / f'好感度{info.fetter}.png', size=0.8), (58, 28))
    # UID
    await card.text(f'UID{info.uid}', 334, 36, fm.get('bahnschrift_regular', 36), 'white', 'right')
    # 角色名
    await card.text(info.name, (0, card.width), 60, fm.get('SourceHanSerifCN-Bold.otf', 64), 'white', 'center')
    # 等级 0-20, 20-40, 40-60, 60-80, 80-90
    color = colors[math.ceil(info.level / 20)]
    await card.draw_rounded_rectangle((117, 153, 184, 185), 5, color[1])
    await card.draw_rounded_rectangle((119, 155, 182, 183), 5, color[0])
    await card.text(f'LV{info.level}', (119, 182), 158, fm.get('bahnschrift_regular', 24), color[1], 'center')
    # 命座
    color = colors[len(info.constellation)]
    await card.draw_rounded_rectangle((194, 153, 264, 185), 5, color[1])
    await card.draw_rounded_rectangle((196, 155, 262, 183), 5, color[0])
    await card.text(f'命座{len(info.constellation)}', (196, 263), 156, fm.get('hywh', 24), color[1], 'center')
    # 武器
    await card.paste(await load_image(ICON / f'star{info.weapon.rarity}.png', size=(76, 76)), (69, 203))
    await card.paste(await load_image(RESOURCE_BASE_PATH / 'weapon' / f'{info.weapon.icon}.png', size=(76, 76)),
                     (69, 206))
    await card.text(info.weapon.name, 158, 203, fm.get('hywh', 32), 'white')
    await card.text(f'LV{info.weapon.level}', 155, 249, fm.get('bahnschrift_bold', 30), 'white')
    await card.paste(await load_image(ICON / f'精炼{info.weapon.affix_level}.png', size=(30, 30)), (247, 249))
    # 圣遗物图标
    if any(artifact.rarity == 5 for artifact in info.artifacts):
        artifact_bg = await load_image(ICON / 'star5.png', size=(76, 76))
    elif any(artifact.rarity == 4 for artifact in info.artifacts):
        artifact_bg = await load_image(ICON / 'star4.png', size=(76, 76))
    else:
        artifact_bg = await load_image(ICON / 'star3.png', size=(76, 76))
    await card.paste(artifact_bg, (69, 292))
    suit = GenshinTools.get_artifact_suit(info.artifacts) if info.artifacts else []
    if len(suit) == 2:
        if suit[0] == suit[1]:
            await card.paste(await load_image(ARTIFACT_ICON / f'{suit[0][1]}.png', mode='RGBA', size=(76, 76)),
                             (69, 295))
            suit_name = f'{suit[0][0][:2]}四件套'
        else:
            await card.paste(await load_image(ARTIFACT_ICON / f'{suit[0][1]}.png', mode='RGBA', size=(53, 53)),
                             (66, 295))
            await card.paste(await load_image(ARTIFACT_ICON / f'{suit[1][1]}.png', mode='RGBA', size=(53, 53)),
                             (96, 319))
            suit_name = f'{suit[0][0][:2]}+{suit[1][0][:2]}'
    elif len(suit) == 1:
        suit_name = f'{suit[0][0][:2]}+散搭'
        await card.paste(await load_image(ARTIFACT_ICON / f'{suit[0][1]}.png', mode='RGBA', size=(53, 53)),
                         (69, 295))
        await card.paste(await load_image(ARTIFACT_ICON / '不知名花.png', mode='RGBA', size=(40, 40)),
                         (102, 325))
    elif len(info.artifacts):
        suit_name = '散搭圣遗物'
        await card.paste(await load_image(ARTIFACT_ICON / '不知名花.png', mode='RGBA', size=(40, 40)),
                         (75, 300))
        await card.paste(await load_image(ARTIFACT_ICON / '不知名毛.png', mode='RGBA', size=(40, 40)),
                         (102, 325))
    else:
        suit_name = '未装备圣遗物'
        await card.paste(await load_image(ARTIFACT_ICON / '不知名花.png', mode='RGBA', size=(63, 63)),
                         (74, 300))
    # 圣遗物名
    await card.text(suit_name, 158, 291, fm.get('hywh', 32), 'white')
    # 圣遗物评分
    score, value = GenshinTools.artifacts_total_score(info, info.artifacts)
    if score is not None:
        rank = 'SSS' if value >= 140 else 'SS' if 120 <= value < 140 else 'S' if 100 <= value < 120 else 'A' if 75 <= value < 100 else 'B' if 50 <= value < 75 else 'C'
        await card.text(str(score), 157, 333, fm.get('bahnschrift_bold', 30, 'Bold'), 'white')
        await card.paste(await load_image(ICON / f'rank{rank}.png'), (252, 333))
    else:
        await card.text('---', 157, 333, fm.get('hywh', 30), 'white')
    # 天赋
    if not info.talents:
        await card.text('CREATED BY LITTLEPAIMON', (0, card.width), 389, fm.get('bahnschrift_regular', 24), 'white',
                        'center')
        await card.crop((0, 0, card.width, 435))
    else:
        if info.name in ['神里绫华', '莫娜']:
            info.talents.pop(2)
        await card.draw_rounded_rectangle((69, 380, 145, 452), 8, talent_color[info.talents[0].level - 1][1])
        await card.draw_rounded_rectangle((71, 382, 143, 450), 8, talent_color[info.talents[0].level - 1][0])
        await card.text(str(info.talents[0].level), (71, 143), 392, fm.get('bahnschrift_bold', 48),
                        talent_color[info.talents[0].level - 1][1], 'center')

        await card.draw_rounded_rectangle((159, 380, 235, 452), 8, talent_color[info.talents[1].level - 1][1])
        await card.draw_rounded_rectangle((161, 382, 233, 450), 8, talent_color[info.talents[1].level - 1][0])
        await card.text(str(info.talents[1].level), (161, 233), 392, fm.get('bahnschrift_bold', 48),
                        talent_color[info.talents[1].level - 1][1], 'center')

        await card.draw_rounded_rectangle((247, 380, 323, 452), 8, talent_color[info.talents[2].level - 1][1])
        await card.draw_rounded_rectangle((249, 382, 321, 450), 8, talent_color[info.talents[2].level - 1][0])
        await card.text(str(info.talents[2].level), (249, 321), 392, fm.get('bahnschrift_bold', 48),
                        talent_color[info.talents[2].level - 1][1], 'center')
        await card.text('CREATED BY LITTLEPAIMON', (0, card.width), 466, fm.get('bahnschrift_regular', 24), 'white',
                        'center')

    if img.width >= img.height:
        per = 1 / ((card.height / img.height) / 0.4)
    else:
        per = 1 / ((card.width / img.width) / 0.4)

    await card.resize(per)
    raw_img = img.copy()

    img.alpha_composite(card.image, (0, img.height - card.height))
    return MessageBuild.Image(img, mode='RGB'), raw_img
