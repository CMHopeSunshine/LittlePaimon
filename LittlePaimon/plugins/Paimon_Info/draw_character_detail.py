from nonebot import logger

from LittlePaimon.config.path import ENKA_RES, RESOURCE_BASE_PATH
from LittlePaimon.utils import load_image, aiorequests
from LittlePaimon.utils.genshin import GenshinTools
from LittlePaimon.utils.image import PMImage, font_manager as fm
from LittlePaimon.utils.message import MessageBuild
from LittlePaimon.database.models import Character
from .damage_cal import get_role_dmg

# weapon_url = 'https://upload-bbs.mihoyo.com/game_record/genshin/equip/{}.png'
# artifact_url = 'https://upload-bbs.mihoyo.com/game_record/genshin/equip/{}.png'
# talent_url = 'https://upload-bbs.mihoyo.com/game_record/genshin/constellation_icon/{}.png'
# skill_url = 'https://static.cherishmoon.fun/LittlePaimon/skill/{}.png'

element_type = ['物理', '火元素', '雷元素', '水元素', '草元素', '风元素', '岩元素', '冰元素']
TALENT_ICON = RESOURCE_BASE_PATH / 'talent'
CON_ICON = RESOURCE_BASE_PATH / 'constellation'
WEAPON_ICON = RESOURCE_BASE_PATH / 'weapon'
ARTIFACT_ICON = RESOURCE_BASE_PATH / 'artifact'
ICON = RESOURCE_BASE_PATH / 'icon'


async def draw_chara_detail(uid: str, info: Character):
    # 暂时用风
    if info.element == '草':
        img = PMImage(image=ENKA_RES / f'背景_风.png')
    else:
        img = PMImage(image=ENKA_RES / f'背景_{info.element}.png')
    try:
        dmg_img = await get_role_dmg(info)
    except Exception as e:
        logger.info(f'{info.name}的伤害计算制图失败：{e}')
        dmg_img = None
    if dmg_img:
        await img.stretch((730, 1377), dmg_img.height + 667, 'height')
        await img.paste(dmg_img, (71, 1846))
    await img.paste(await load_image(ENKA_RES / '底遮罩.png'), (0, 0))
    if info.name not in ['荧', '空', '埃洛伊']:
        await img.paste(await load_image(ENKA_RES / f'{info.region}.png', size=(130, 130)), (0, 0))

    await img.text(f"UID{uid}", 131, 100, fm.get('number.ttf', 48))
    await img.text(info.name, 134, 150, fm.get('优设标题黑.ttf', 72))

    level_mask = await load_image(ENKA_RES / '等级遮罩.png')
    await img.paste(level_mask, (298 + 60 * (len(info.name) - 2), 172))
    await img.text(f'LV{info.level}',
                   (298 + 60 * (len(info.name) - 2), 298 + 60 * (len(info.name) - 2) + 171),
                   (170, 172 + 52),
                   fm.get('number.ttf', 48),
                   'black',
                   'center')
    # 属性值
    await img.text('生命值', 89, 262, fm.get('hywh.ttf', 34))
    await img.text(f"{info.prop.base_health}",
                   480 - img.text_length(f"+{info.prop.extra_health}", fm.get('number.ttf', 34)) - 5,
                   264,
                   fm.get('number.ttf', 34),
                   align='right')
    await img.text(f"+{info.prop.extra_health}",
                   480,
                   264,
                   fm.get('number.ttf', 34),
                   '#59c538',
                   'right')

    await img.text('攻击力', 89, 319, fm.get('hywh.ttf', 34))
    await img.text(f"{info.prop.base_attack}",
                   480 - img.text_length(f"+{info.prop.extra_attack}", fm.get('number.ttf', 34)) - 5,
                   321,
                   fm.get('number.ttf', 34),
                   align='right')
    await img.text(f"+{info.prop.extra_attack}",
                   480,
                   321,
                   fm.get('number.ttf', 34),
                   '#59c538',
                   'right')

    await img.text('防御力', 89, 377, fm.get('hywh.ttf', 34))
    await img.text(f"{info.prop.base_defense}",
                   480 - img.text_length(f"+{info.prop.extra_defense}", fm.get('number.ttf', 34)) - 5,
                   379,
                   fm.get('number.ttf', 34),
                   align='right')
    await img.text(f"+{info.prop.extra_defense}",
                   480,
                   379,
                   fm.get('number.ttf', 34),
                   '#59c538',
                   'right')

    await img.text('暴击率', 89, 436, fm.get('hywh.ttf', 34))
    await img.text(f"{round(info.prop.crit_rate * 100, 1)}%",
                   480,
                   438,
                   fm.get('number.ttf', 34),
                   align='right')

    await img.text('暴击伤害', 89, 493, fm.get('hywh.ttf', 34))
    await img.text(f"{round(info.prop.crit_damage * 100, 1)}%",
                   480,
                   495,
                   fm.get('number.ttf', 34),
                   align='right')

    await img.text('元素精通', 89, 551, fm.get('hywh.ttf', 34))
    await img.text(str(int(info.prop.elemental_mastery)),
                   480,
                   553,
                   fm.get('number.ttf', 34),
                   align='right')

    await img.text('元素充能效率', 89, 610, fm.get('hywh.ttf', 34))
    await img.text(f"{round(info.prop.elemental_efficiency * 100, 1)}%",
                   480,
                   612,
                   fm.get('number.ttf', 34),
                   align='right')

    max_element = '物理', 0
    for e, v in info.prop.dmg_bonus.items():
        if v >= max_element[1]:
            max_element = e, v
    await img.text(f'{max_element[0]}伤害加成' if max_element[0] == '物理' else f'{max_element[0]}元素伤害加成',
                   89,
                   669,
                   fm.get('hywh.ttf', 34))
    await img.text(f"{round(max_element[1] * 100, 1)}%",
                   480,
                   671,
                   fm.get('number.ttf', 34),
                   align='right')

    # 天赋
    if info.element == '草':
        base_icon = await load_image(ENKA_RES / '图标_风.png', mode='RGBA')
    else:
        base_icon = await load_image(ENKA_RES / f'图标_{info.element}.png', mode='RGBA')
    base_icon_grey = await load_image(ENKA_RES / '图标_灰.png', mode='RGBA')
    if info.name in ['神里绫华', '莫娜']:
        info.talents.pop(2)
    for i in range(3):
        await img.paste(base_icon.resize((132, 142)), (564, 253 + 146 * i))
        await img.text(str(info.talents[i].level),
                       (510, 552),
                       (304 + 146 * i, 349 + 146 * i),
                       fm.get('number.ttf', 34),
                       'black',
                       'center')
        talent_icon = await load_image(TALENT_ICON / f'{info.talents[i].icon}.png', size=(57, 57), mode='RGBA')
        await img.paste(talent_icon, (603, 298 + 147 * i))

    # 命座
    lock = await load_image(ENKA_RES / '锁.png', mode='RGBA', size=(45, 45))
    t = 0
    for con in info.constellation:
        await img.paste(base_icon.resize((83, 90)), (510 + t * 84, 790))
        con_icon = await load_image(TALENT_ICON / f'{con.icon}.png', size=(45, 45), mode='RGBA')
        await img.paste(con_icon, (529 + t * 84, 813))
        t += 1
    for t2 in range(t, 6):
        await img.paste(base_icon_grey.resize((83, 90)), (510 + t2 * 84, 790))
        await img.paste(lock, (530 + t2 * 84, 813))

    # 武器
    weapon_bg = await load_image(ICON / f'star{info.weapon.rarity}.png', size=(150, 150))
    await img.paste(weapon_bg, (91, 760))
    weapon_icon = await load_image(WEAPON_ICON / f'{info.weapon.icon}.png', size=(150, 150), mode='RGBA')
    await img.paste(weapon_icon, (91, 760))
    await img.text(info.weapon.name, 268, 758, fm.get('hywh.ttf', 34))

    star = await load_image(ENKA_RES / 'star.png')
    for i in range(info.weapon.rarity):
        await img.paste(star, (267 + i * 30, 799))
    await img.text(f'LV{info.weapon.level}',
                   (268, 268 + 98),
                   (835, 864),
                   fm.get('number.ttf', 27),
                   'black',
                   'center')
    await img.text(f'精炼{info.weapon.affix_level}阶', 266, 869, fm.get('hywh.ttf', 34))

    # 圣遗物
    effective = GenshinTools.get_effective(info)
    average = GenshinTools.get_expect_score(effective)
    total_score = 0
    # 第一排
    for i in range(2):
        try:
            artifact = info.artifacts[i]
        except IndexError:
            break
        artifact_bg = await load_image(RESOURCE_BASE_PATH / 'other' / f'star{artifact.rarity}.png', size=(100, 100))
        await img.paste(artifact_bg, (587 + 317 * i, 1002))
        artifact_icon = await load_image(ARTIFACT_ICON / f'{artifact.icon}.png', size=(100, 100), mode='RGBA')
        await img.paste(artifact_icon, (587 + 317 * i, 1002))
        await img.text(artifact.name, 411 + 317 * i, 951, fm.get('hywh.ttf', 40))
        value, score = GenshinTools.artifact_score(info.prop, artifact, effective)
        total_score += value
        rank = 'SSS' if score >= 140 else 'SS' if 120 <= score < 140 else 'S' if 100 <= score < 120 else 'A' if 75 <= score < 100 else 'B' if 50 <= score < 75 else 'C'
        await img.text(f'{rank}-{value}', 412 + 317 * i, 998, fm.get('number.ttf', 28))
        await img.paste(level_mask.resize((98, 30)), (412 + 317 * i, 1032))
        await img.text(f"LV{artifact.level}",
                       (412 + 317 * i, 412 + 317 * i + 98),
                       (1032, 1062),
                       fm.get('number.ttf', 27),
                       'black',
                       'center')
        await img.text(artifact.main_property.name, 410 + 317 * i, 1069, fm.get('hywh.ttf', 25))
        value_text = f'+{artifact.main_property.value}%' if artifact.main_property.name not in ['生命值', '攻击力', '元素精通'] else f'+{int(artifact.main_property.value)}'
        await img.text(value_text, 408 + 317 * i, 1100, font=fm.get('number.ttf', 48))
        for j in range(len(artifact.prop_list)):
            if '百分比' in artifact.prop_list[j].name:
                text = artifact.prop_list[j].name.replace('百分比', '')
            else:
                text = artifact.prop_list[j].name
            await img.text(text, 411 + 317 * i, 1163 + 50 * j,
                           color='white' if GenshinTools.check_effective(artifact.prop_list[j].name,
                                                                         effective) else '#afafaf',
                           font=fm.get('hywh.ttf', 25))
            if artifact.prop_list[j].name not in ['攻击力', '防御力', '生命值', '元素精通']:
                num = '+' + str(artifact.prop_list[j].value) + '%'
            else:
                num = '+' + str(int(artifact.prop_list[j].value))
            await img.text(num, 679 + 317 * i, 1163 + 50 * j,
                           color='white' if GenshinTools.check_effective(artifact.prop_list[j].name,
                                                                         effective) else '#afafaf',
                           font=fm.get('number.ttf', 25), align='right')
    # 第二排
    for i in range(3):
        try:
            artifact = info.artifacts[i + 2]
        except IndexError:
            break
        artifact_bg = await load_image(RESOURCE_BASE_PATH / 'other' / f'star{artifact.rarity}.png', size=(100, 100))
        await img.paste(artifact_bg, (270 + 317 * i, 1439))
        artifact_icon = await load_image(ARTIFACT_ICON / f'{artifact.icon}.png', size=(100, 100), mode='RGBA')
        await img.paste(artifact_icon, (270 + 317 * i, 1439))
        await img.text(artifact.name, 94 + 317 * i, 1388, fm.get('hywh.ttf', 40))
        value, score = GenshinTools.artifact_score(info.prop, artifact, effective)
        total_score += value
        rank = 'SSS' if score >= 140 else 'SS' if 120 <= score < 140 else 'S' if 100 <= score < 120 else 'A' if 75 <= score < 100 else 'B' if 50 <= score < 75 else 'C'
        await img.text(f'{rank}-{value}', 95 + 317 * i, 1435, fm.get('number.ttf', 28))
        await img.paste(level_mask.resize((98, 30)), (95 + 317 * i, 1469))
        await img.text(f"LV{artifact.level}",
                       (95 + 317 * i, 95 + 317 * i + 98),
                       (1469, 1499),
                       fm.get('number.ttf', 27),
                       'black',
                       'center')
        await img.text(artifact.main_property.name, 94 + 317 * i, 1506, fm.get('hywh.ttf', 25))
        value_text = f'+{artifact.main_property.value}%' if artifact.main_property.name not in ['生命值', '攻击力',
                                                                                                '元素精通'] else f'+{int(artifact.main_property.value)}'
        await img.text(value_text, 91 + 317 * i, 1538, font=fm.get('number.ttf', 48))
        for j in range(len(artifact.prop_list)):
            if '百分比' in artifact.prop_list[j].name:
                text = artifact.prop_list[j].name.replace('百分比', '')
            else:
                text = artifact.prop_list[j].name
            await img.text(text, 94 + 317 * i, 1600 + 50 * j,
                           color='white' if GenshinTools.check_effective(artifact.prop_list[j].name,
                                                                         effective) else '#afafaf',
                           font=fm.get('hywh.ttf', 25))
            if artifact.prop_list[j].name not in ['攻击力', '防御力', '生命值', '元素精通']:
                num = '+' + str(artifact.prop_list[j].value) + '%'
            else:
                num = '+' + str(int(artifact.prop_list[j].value))
            await img.text(num, 362 + 317 * i, 1600 + 50 * j,
                           color='white' if GenshinTools.check_effective(artifact.prop_list[j].name,
                                                                         effective) else '#afafaf',
                           font=fm.get('number.ttf', 25), align='right')

    # 圣遗物评分
    await img.text('总有效词条数', 119, 1057, color='#afafaf', font=fm.get('hywh.ttf', 36))
    score_pro = total_score / (average * 5) * 100
    total_rank = 'SSS' if score_pro >= 140 else 'SS' if 120 <= score_pro < 140 else 'S' if 100 <= score_pro < 120 else 'A' if 75 <= score_pro < 100 else 'B' if 50 <= score_pro < 75 else 'C'
    rank_icon = await load_image(ENKA_RES / f'评分{total_rank[0]}.png', mode='RGBA')
    if len(total_rank) == 3:
        await img.paste(rank_icon, (95, 964))
        await img.paste(rank_icon, (145, 964))
        await img.paste(rank_icon, (195, 964))
        await img.text(str(round(total_score, 1)), 250, 974, font=fm.get('number.ttf', 60))
    elif len(total_rank) == 2:
        await img.paste(rank_icon, (125, 964))
        await img.paste(rank_icon, (175, 964))
        await img.text(str(round(total_score, 1)), 235, 974, font=fm.get('number.ttf', 60))
    else:
        await img.paste(rank_icon, (143, 964))
        await img.text(str(round(total_score, 1)), 217, 974, font=fm.get('number.ttf', 60))

    # 圣遗物套装
    suit = GenshinTools.get_artifact_suit(info.artifacts)
    if not suit:
        await img.text('未激活套装', 184, 1168, font=fm.get('hywh.ttf', 36))
        await img.text('未激活套装', 184, 1292, font=fm.get('hywh.ttf', 36))
    elif len(suit) == 1:
        artifact1 = await load_image(ARTIFACT_ICON / f'{suit[0][1]}.png', size=(110, 110), mode='RGBA')
        await img.paste(artifact1, (76, 1130))
        await img.text(f'{suit[0][0][:2]}二件套', 184, 1168, font=fm.get('hywh.ttf', 36))
        await img.text('未激活套装', 184, 1292, font=fm.get('hywh.ttf', 36))
    else:
        if suit[0][0] == suit[1][0]:
            artifact2 = artifact1 = await load_image(ARTIFACT_ICON / f'{suit[0][1]}.png', size=(110, 110), mode='RGBA')
            await img.text(f'{suit[0][0][:2]}四件套', 184, 1168, font=fm.get('hywh.ttf', 36))
            await img.text(f'{suit[0][0][:2]}四件套', 184, 1292, font=fm.get('hywh.ttf', 36))
        else:
            artifact1 = await load_image(ARTIFACT_ICON / f'{suit[0][1]}.png', size=(110, 110), mode='RGBA')
            artifact2 = await load_image(ARTIFACT_ICON / f'{suit[1][1]}.png', size=(110, 110), mode='RGBA')
            await img.text(f'{suit[0][0][:2]}两件套', 184, 1168, font=fm.get('hywh.ttf', 36))
            await img.text(f'{suit[1][0][:2]}两件套', 184, 1292, font=fm.get('hywh.ttf', 36))
        await img.paste(artifact1, (76, 1130))
        await img.paste(artifact2, (76, 1255))

    # 立绘
    await img.paste(await load_image(ENKA_RES / '立绘' / f'{info.name}.png'), (695, 234))
    await img.text(f'更新于{info.update_time.strftime("%m-%d %H:%M")}',
                   (0, 1080),
                   (img.height - 110, img.height - 50),
                   fm.get('优设标题黑.ttf', 33),
                   '#afafaf',
                   'center')
    await img.text('Created by LittlePaimon | Powered by Enka.Network',
                   (0, 1080),
                   (img.height - 60, img.height),
                   fm.get('优设标题黑.ttf', 36),
                   'white',
                   'center')

    return MessageBuild.Image(img, quality=75, mode='RGB')
