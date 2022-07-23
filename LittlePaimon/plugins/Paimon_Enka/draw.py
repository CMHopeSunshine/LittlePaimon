from nonebot import logger

from LittlePaimon.config.path import JSON_DATA, ENKA_RES, TEMP, RESOURCE_BASE_PATH
from LittlePaimon.utils import load_json, load_image, aiorequests, MessageBuild
from LittlePaimon.utils.enka import get_effective, get_expect_score, artifact_total_value, check_effective, \
    get_artifact_suit
from LittlePaimon.utils.image import PMImage, font_manager as fm
from .damage_cal import get_role_dmg

weapon_url = 'https://upload-bbs.mihoyo.com/game_record/genshin/equip/{}.png'
artifact_url = 'https://upload-bbs.mihoyo.com/game_record/genshin/equip/{}.png'
talent_url = 'https://upload-bbs.mihoyo.com/game_record/genshin/constellation_icon/{}.png'
skill_url = 'https://static.cherishmoon.fun/LittlePaimon/skill/{}.png'

element_type = ['物理', '火元素', '雷元素', '水元素', '草元素', '风元素', '岩元素', '冰元素']
region = load_json(JSON_DATA / 'role_region.json')


async def draw_role_card(uid, data):
    img = PMImage(image=ENKA_RES / f'背景_{data["元素"]}.png')
    img.convert('RGBA')
    try:
        dmg_img = get_role_dmg(data)
    except Exception as e:
        logger.warning(f'{data["名称"]}的伤害计算制图失败：{e}')
        dmg_img = None
    if dmg_img:
        img.stretch((730, 1377), dmg_img.height + 667, 'height')
        img.paste(dmg_img, (71, 1846))
    img.paste(load_image(ENKA_RES / '底遮罩.png'), (0, 0))
    if data['名称'] not in ['荧', '空', '埃洛伊']:
        img.paste(load_image(ENKA_RES / f'{region[data["名称"]]}.png', size=(130, 130)), (0, 0))

    img.text(f"UID{uid}", 131, 100, fm.get('number.ttf', 48))
    img.text(data['名称'], 134, 150, fm.get('优设标题黑.ttf', 72))

    level_mask = load_image(ENKA_RES / '等级遮罩.png')
    img.paste(level_mask, (298 + 60 * (len(data['名称']) - 2), 172))
    img.text(f'LV{data["等级"]}',
             (298 + 60 * (len(data['名称']) - 2), 298 + 60 * (len(data['名称']) - 2) + 171),
             (170, 172 + 52),
             fm.get('number.ttf', 48),
             'black',
             'center')
    # 属性值
    prop = data['属性']
    img.text('生命值', 89, 262, fm.get('hywh.ttf', 34))
    img.text(f"{prop['基础生命']}",
             480 - img.text_length(f"+{prop['额外生命']}", fm.get('number.ttf', 34)) - 5,
             264,
             fm.get('number.ttf', 34),
             align='right')
    img.text(f"+{prop['额外生命']}",
             480,
             264,
             fm.get('number.ttf', 34),
             '#59c538',
             'right')

    img.text('攻击力', 89, 319, fm.get('hywh.ttf', 34))
    img.text(f"{prop['基础攻击']}",
             480 - img.text_length(f"+{prop['额外攻击']}", fm.get('number.ttf', 34)) - 5,
             321,
             fm.get('number.ttf', 34),
             align='right')
    img.text(f"+{prop['额外攻击']}",
             480,
             321,
             fm.get('number.ttf', 34),
             '#59c538',
             'right')

    img.text('防御力', 89, 377, fm.get('hywh.ttf', 34))
    img.text(f"{prop['基础防御']}",
             480 - img.text_length(f"+{prop['额外防御']}", fm.get('number.ttf', 34)) - 5,
             379,
             fm.get('number.ttf', 34),
             align='right')
    img.text(f"+{prop['额外防御']}",
             480,
             379,
             fm.get('number.ttf', 34),
             '#59c538',
             'right')

    img.text('暴击率', 89, 436, fm.get('hywh.ttf', 34))
    img.text(f"{round(prop['暴击率'] * 100, 1)}%",
             480,
             438,
             fm.get('number.ttf', 34),
             align='right')

    img.text('暴击伤害', 89, 493, fm.get('hywh.ttf', 34))
    img.text(f"{round(prop['暴击伤害'] * 100, 1)}%",
             480,
             495,
             fm.get('number.ttf', 34),
             align='right')

    img.text('元素精通', 89, 551, fm.get('hywh.ttf', 34))
    img.text(str(prop['元素精通']),
             480,
             553,
             fm.get('number.ttf', 34),
             align='right')

    img.text('元素充能效率', 89, 610, fm.get('hywh.ttf', 34))
    img.text(f"{round(prop['元素充能效率'] * 100, 1)}%",
             480,
             612,
             fm.get('number.ttf', 34),
             align='right')

    max_element = max(prop['伤害加成'])
    img.text(f'{element_type[prop["伤害加成"].index(max_element)]}伤害加成',
             89,
             669,
             fm.get('hywh.ttf', 34))
    img.text(f"{round(max_element * 100, 1)}%",
             480,
             671,
             fm.get('number.ttf', 34),
             align='right')

    # 天赋
    base_icon = load_image(ENKA_RES / f'图标_{data["元素"]}.png', mode='RGBA')
    base_icon_grey = load_image(ENKA_RES / '图标_灰.png', mode='RGBA')
    if data['名称'] in ['神里绫华', '莫娜']:
        data['天赋'].pop(2)
    for i in range(3):
        img.paste(base_icon.resize((132, 142)), (564, 253 + 146 * i))
        img.text(str(data['天赋'][i]['等级']),
                 (510, 552),
                 (304 + 146 * i, 349 + 146 * i),
                 fm.get('number.ttf', 34),
                 'black',
                 'center')
        skill_icon = await aiorequests.get_img(url=skill_url.format(data["天赋"][i]["图标"]),
                                               size=(57, 57),
                                               save_path=TEMP / 'skill' / f'{data["天赋"][i]["图标"]}.png',
                                               mode='RGBA')
        img.paste(skill_icon, (603, 298 + 147 * i))

    # 命座
    lock = load_image(ENKA_RES / '锁.png', mode='RGBA', size=(45, 45))
    t = 0
    for talent in data['命座']:
        img.paste(base_icon.resize((83, 90)), (510 + t * 84, 790))
        talent_icon = await aiorequests.get_img(url=talent_url.format(talent["图标"]),
                                                size=(45, 45),
                                                save_path=TEMP / 'skill' / f'{talent["图标"]}.png',
                                                mode='RGBA')
        img.paste(talent_icon, (529 + t * 84, 813))
        t += 1
    for t2 in range(t, 6):
        img.paste(base_icon_grey.resize((83, 90)), (510 + t2 * 84, 790))
        img.paste(lock, (530 + t2 * 84, 813))

    # 武器
    weapon_bg = load_image(RESOURCE_BASE_PATH / 'other' / f'star{data["武器"]["星级"]}.png', size=(150, 150))
    img.paste(weapon_bg, (91, 760))
    weapon_icon = await aiorequests.get_img(url=weapon_url.format(data["武器"]["图标"]),
                                            size=(150, 150),
                                            save_path=TEMP / 'weapon' / f'{data["武器"]["图标"]}.png',
                                            mode='RGBA')
    img.paste(weapon_icon, (91, 760))
    img.text(data['武器']['名称'], 268, 758, fm.get('hywh.ttf', 34))

    star = load_image(ENKA_RES / 'star.png')
    for i in range(data['武器']['星级']):
        img.paste(star, (267 + i * 30, 799))
    img.text(f'LV{data["武器"]["等级"]}',
             (268, 268 + 98),
             (835, 864),
             fm.get('number.ttf', 27),
             'black',
             'center')
    img.text(f'精炼{data["武器"]["精炼等级"]}阶', 266, 869, fm.get('hywh.ttf', 34))

    # 圣遗物
    effective = get_effective(data['名称'], data['武器']['名称'], data['圣遗物'], data['元素'])
    average = get_expect_score(effective)
    total_score = 0
    # 第一排
    for i in range(2):
        try:
            artifact = data['圣遗物'][i]
        except IndexError:
            break
        artifact_bg = load_image(RESOURCE_BASE_PATH / 'other' / f'star{artifact["星级"]}.png', size=(100, 100))
        img.paste(artifact_bg, (587 + 317 * i, 1002))
        reli_path = await aiorequests.get_img(url=artifact_url.format(artifact["图标"]),
                                              size=(100, 100),
                                              save_path=TEMP / 'artifact' / f'{artifact["图标"]}.png',
                                              mode='RGBA')
        img.paste(reli_path, (587 + 317 * i, 1002))
        img.text(artifact['名称'], 411 + 317 * i, 951, fm.get('hywh.ttf', 40))
        value, score = artifact_total_value(data['属性'], artifact, effective)
        total_score += value
        rank = 'SSS' if score >= 140 else 'SS' if 120 <= score < 140 else 'S' if 100 <= score < 120 else 'A' if 75 <= score < 100 else 'B' if 50 <= score < 75 else 'C'
        img.text(f'{rank}-{value}', 412 + 317 * i, 998, fm.get('number.ttf', 28))
        img.paste(level_mask.resize((98, 30)), (412 + 317 * i, 1032))
        img.text(f"LV{artifact['等级']}",
                 (412 + 317 * i, 412 + 317 * i + 98),
                 (1032, 1062),
                 fm.get('number.ttf', 27),
                 'black',
                 'center')
        img.text(artifact['主属性']['属性名'], 410 + 317 * i, 1069, fm.get('hywh.ttf', 25))
        value_text = f"+{artifact['主属性']['属性值']}" + ('%' if artifact['主属性']['属性名'] not in ['生命值', '攻击力', '元素精通'] else '')
        img.text(value_text, 408 + 317 * i, 1100, font=fm.get('number.ttf', 48))
        for j in range(len(artifact['词条'])):
            if '百分比' in artifact['词条'][j]['属性名']:
                text = artifact['词条'][j]['属性名'].replace('百分比', '')
            else:
                text = artifact['词条'][j]['属性名']
            img.text(text, 411 + 317 * i, 1163 + 50 * j,
                     color='white' if check_effective(artifact['词条'][j]['属性名'], effective) else '#afafaf',
                     font=fm.get('hywh.ttf', 25))
            if artifact['词条'][j]['属性名'] not in ['攻击力', '防御力', '生命值', '元素精通']:
                num = '+' + str(artifact['词条'][j]['属性值']) + '%'
            else:
                num = '+' + str(artifact['词条'][j]['属性值'])
            img.text(num, 679 + 317 * i, 1163 + 50 * j,
                     color='white' if check_effective(artifact['词条'][j]['属性名'], effective) else '#afafaf',
                     font=fm.get('number.ttf', 25), align='right')
    # 第二排
    for i in range(3):
        try:
            artifact = data['圣遗物'][i + 2]
        except IndexError:
            break
        artifact_bg = load_image(RESOURCE_BASE_PATH / 'other' / f'star{artifact["星级"]}.png', size=(100, 100))
        img.paste(artifact_bg, (270 + 317 * i, 1439))
        reli_path = await aiorequests.get_img(url=artifact_url.format(artifact["图标"]),
                                              size=(100, 100),
                                              save_path=TEMP / 'artifact' / f'{artifact["图标"]}.png',
                                              mode='RGBA')
        img.paste(reli_path, (270 + 317 * i, 1439))
        img.text(artifact['名称'], 94 + 317 * i, 1388, fm.get('hywh.ttf', 40))
        value, score = artifact_total_value(data['属性'], artifact, effective)
        total_score += value
        rank = 'SSS' if score >= 140 else 'SS' if 120 <= score < 140 else 'S' if 100 <= score < 120 else 'A' if 75 <= score < 100 else 'B' if 50 <= score < 75 else 'C'
        img.text(f'{rank}-{value}', 95 + 317 * i, 1435, fm.get('number.ttf', 28))
        img.paste(level_mask.resize((98, 30)), (95 + 317 * i, 1469))
        img.text(f"LV{artifact['等级']}",
                 (95 + 317 * i, 95 + 317 * i + 98),
                 (1469, 1499),
                 fm.get('number.ttf', 27),
                 'black',
                 'center')
        img.text(artifact['主属性']['属性名'], 94 + 317 * i, 1506, fm.get('hywh.ttf', 25))
        value_text = f"+{artifact['主属性']['属性值']}" + ('%' if artifact['主属性']['属性名'] not in ['生命值', '攻击力', '元素精通'] else '')
        img.text(value_text, 91 + 317 * i, 1538, font=fm.get('number.ttf', 48))
        for j in range(len(artifact['词条'])):
            if '百分比' in artifact['词条'][j]['属性名']:
                text = artifact['词条'][j]['属性名'].replace('百分比', '')
            else:
                text = artifact['词条'][j]['属性名']
            img.text(text, 94 + 317 * i, 1600 + 50 * j,
                     color='white' if check_effective(artifact['词条'][j]['属性名'], effective) else '#afafaf',
                     font=fm.get('hywh.ttf', 25))
            if artifact['词条'][j]['属性名'] not in ['攻击力', '防御力', '生命值', '元素精通']:
                num = '+' + str(artifact['词条'][j]['属性值']) + '%'
            else:
                num = '+' + str(artifact['词条'][j]['属性值'])
            img.text(num, 362 + 317 * i, 1600 + 50 * j,
                     color='white' if check_effective(artifact['词条'][j]['属性名'], effective) else '#afafaf',
                     font=fm.get('number.ttf', 25), align='right')

    # 圣遗物评分
    img.text('总有效词条数', 119, 1057, color='#afafaf', font=fm.get('hywh.ttf', 36))
    score_pro = total_score / (average * 5) * 100
    total_rank = 'SSS' if score_pro >= 140 else 'SS' if 120 <= score_pro < 140 else 'S' if 100 <= score_pro < 120 else 'A' if 75 <= score_pro < 100 else 'B' if 50 <= score_pro < 75 else 'C'
    rank_icon = load_image(ENKA_RES / f'评分{total_rank[0]}.png', mode='RGBA')
    if len(total_rank) == 3:
        img.paste(rank_icon, (95, 964))
        img.paste(rank_icon, (145, 964))
        img.paste(rank_icon, (195, 964))
        img.text(str(round(total_score, 1)), 250, 974, font=fm.get('number.ttf', 60))
    elif len(total_rank) == 2:
        img.paste(rank_icon, (125, 964))
        img.paste(rank_icon, (175, 964))
        img.text(str(round(total_score, 1)), 235, 974, font=fm.get('number.ttf', 60))
    else:
        img.paste(rank_icon, (143, 964))
        img.text(str(round(total_score, 1)), 217, 974, font=fm.get('number.ttf', 60))

    # 圣遗物套装
    suit = get_artifact_suit(data['圣遗物'])
    if not suit:
        img.text('未激活套装', 184, 1168, font=fm.get('hywh.ttf', 36))
        img.text('未激活套装', 184, 1292, font=fm.get('hywh.ttf', 36))
    elif len(suit) == 1:
        artifact1 = await aiorequests.get_img(url=artifact_url.format(suit[0][1]),
                                              size=(110, 110),
                                              save_path=TEMP / 'artifact' / f'{suit[0][1]}.png',
                                              mode='RGBA')
        img.paste(artifact1, (76, 1130))
        img.text(f'{suit[0][0][:2]}二件套', 184, 1168, font=fm.get('hywh.ttf', 36))
        img.text('未激活套装', 184, 1292, font=fm.get('hywh.ttf', 36))
    else:
        if suit[0][0] == suit[1][0]:
            artifact1 = artifact2 = await aiorequests.get_img(url=artifact_url.format(suit[0][1]),
                                                              size=(110, 110),
                                                              save_path=TEMP / 'artifact' / f'{suit[0][1]}.png',
                                                              mode='RGBA')
            img.text(f'{suit[0][0][:2]}四件套', 184, 1168, font=fm.get('hywh.ttf', 36))
            img.text(f'{suit[0][0][:2]}四件套', 184, 1292, font=fm.get('hywh.ttf', 36))
        else:
            artifact1 = await aiorequests.get_img(url=artifact_url.format(suit[0][1]), size=(110, 110),
                                                  save_path=TEMP / 'artifact' / f'{suit[0][1]}.png',
                                                  mode='RGBA')
            artifact2 = await aiorequests.get_img(url=artifact_url.format(suit[1][1]), size=(110, 110),
                                                  save_path=TEMP / 'artifact' / f'{suit[1][1]}.png',
                                                  mode='RGBA')
            img.text(f'{suit[0][0][:2]}两件套', 184, 1168, font=fm.get('hywh.ttf', 36))
            img.text(f'{suit[1][0][:2]}两件套', 184, 1292, font=fm.get('hywh.ttf', 36))
        img.paste(artifact1, (76, 1130))
        img.paste(artifact2, (76, 1255))

    # 立绘
    img.paste(load_image(ENKA_RES / '立绘' / f'{data["名称"]}.png'), (695, 234))
    img.text(f'更新于{data["更新时间"].replace("2022-", "")[:-3]}',
             (0, 1080),
             (img.height - 110, img.height - 50),
             fm.get('优设标题黑.ttf', 33),
             '#afafaf',
             'center')
    img.text('Created by LittlePaimon | Powered by Enka.Network',
             (0, 1080),
             (img.height - 60, img.height),
             fm.get('优设标题黑.ttf', 36),
             'white',
             'center')

    return MessageBuild.Image(img.image, quality=75, mode='RGB')
