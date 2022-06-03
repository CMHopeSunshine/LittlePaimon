from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

from utils.file_handler import load_image
from utils.enka_util import artifact_total_score, check_effective
from utils import aiorequests
from utils.message_util import MessageBuild

res_path = Path(__file__).parent.parent / 'res'
res_path2 = Path() / 'data' / 'LittlePaimon' / 'res'
weapon_url = 'https://upload-bbs.mihoyo.com/game_record/genshin/equip/{}.png'
artifact_url = 'https://upload-bbs.mihoyo.com/game_record/genshin/equip/{}.png'
talent_url = 'https://upload-bbs.mihoyo.com/game_record/genshin/constellation_icon/{}.png'
skill_url = 'https://static.cherishmoon.fun/LittlePaimon/skill/{}.png'

element_type = ['物理', '火元素', '雷元素', '水元素', '草元素', '风元素', '岩元素', '冰元素']
element_list = ['火', '水', '冰', '雷', '岩', '风']
bg_card = {}
base_icon = {}
base_mask = load_image(res_path / 'player_card2' / '底遮罩.png')
level_mask = load_image(res_path / 'player_card2' / '等级遮罩.png')
star = load_image(res_path / 'player_card2' / 'star.png')
for e in element_list:
    bg_card[e] = load_image(res_path / 'player_card2' / f'背景_{e}.png', mode='RGBA')
    base_icon[e] = load_image(res_path / 'player_card2' / f'图标_{e}.png', mode='RGBA')
base_icon['灰'] = load_image(res_path / 'player_card2' / '图标_灰.png', mode='RGBA')
rank_list = ['S', 'A', 'B', 'C']
rank_icon = {}
for r in rank_list:
    rank_icon[r] = load_image(res_path / 'player_card2' / f'评分{r}.png', mode='RGBA')
weapon_bg = []
for i in range(1, 6):
    weapon_bg.append(load_image(res_path / 'other' / f'star{i}.png', size=(150, 150)))
paint = load_image(res_path / 'player_card2' / '立绘框.png', mode='RGBA')
lock = load_image(res_path / 'player_card2' / '锁.png', mode='RGBA', size=(45, 45))
loading = load_image(res_path / 'player_card2' / '加载中.png', mode='RGBA', size=(120, 120))


def get_font(size, font='hywh.ttf'):
    return ImageFont.truetype(str(res_path / font), size)


async def draw_role_card(uid, data):
    bg = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    bg.alpha_composite(bg_card[data['元素']], (0, 0))
    bg.alpha_composite(base_mask, (0, 0))
    bg_draw = ImageDraw.Draw(bg)
    bg_draw.text((131, 100), f"UID{uid}", fill='white', font=get_font(48, 'number.ttf'))
    bg_draw.text((134, 150), data['名称'], fill='white', font=get_font(72, '优设标题黑.ttf'))
    bg.alpha_composite(level_mask, (298 + 60 * (len(data['名称']) - 2), 172))
    bg_draw.text((330 + 60 * (len(data['名称']) - 2), 174), f'LV{data["等级"]}', fill='black',
                 font=get_font(48, 'number.ttf'))
    # 属性值
    prop = data['属性']
    bg_draw.text((89, 262), '生命值', fill='white', font=get_font(34, 'hywh.ttf'))
    text_length = 473 - (len(str(prop['基础生命'])) + len(str(prop['额外生命']))) * 20 - 12
    bg_draw.text((text_length, 264), f"{prop['基础生命']}", fill='white', font=get_font(34, 'number.ttf'))
    bg_draw.text((text_length + len(str(prop['基础生命'])) * 20 + 3, 264), f"+{prop['额外生命']}", fill='#59c538',
                 font=get_font(34, 'number.ttf'))

    bg_draw.text((89, 319), '攻击力', fill='white', font=get_font(34, 'hywh.ttf'))
    text_length = 473 - (len(str(prop['基础攻击'])) + len(str(prop['额外攻击']))) * 20 - 12
    bg_draw.text((text_length, 321), f"{prop['基础攻击']}", fill='white', font=get_font(34, 'number.ttf'))
    bg_draw.text((text_length + len(str(prop['基础攻击'])) * 20 + 3, 321), f"+{prop['额外攻击']}", fill='#59c538',
                 font=get_font(34, 'number.ttf'))

    bg_draw.text((89, 377), '防御力', fill='white', font=get_font(34, 'hywh.ttf'))
    text_length = 473 - (len(str(prop['基础防御'])) + len(str(prop['额外防御']))) * 20 - 12
    bg_draw.text((text_length, 379), f"{prop['基础防御']}", fill='white', font=get_font(34, 'number.ttf'))
    bg_draw.text((text_length + len(str(prop['基础防御'])) * 20 + 3, 379), f"+{prop['额外防御']}", fill='#59c538',
                 font=get_font(34, 'number.ttf'))

    text = round(prop['暴击率'] * 100, 1)
    bg_draw.text((89, 436), '暴击率', fill='white', font=get_font(34, 'hywh.ttf'))
    bg_draw.text((473 - len(str(text)) * 17 - 17, 438), f"{text}%", fill='white',
                 font=get_font(34, 'number.ttf'))

    text = round(prop['暴击伤害'] * 100, 1)
    bg_draw.text((89, 493), '暴击伤害', fill='white', font=get_font(34, 'hywh.ttf'))
    bg_draw.text((473 - len(str(text)) * 17 - 17, 495), f"{text}%", fill='white',
                 font=get_font(34, 'number.ttf'))

    bg_draw.text((89, 551), '元素精通', fill='white', font=get_font(34, 'hywh.ttf'))
    bg_draw.text((473 - len(str(prop['元素精通'])) * 18, 553), f"{prop['元素精通']}", fill='white',
                 font=get_font(34, 'number.ttf'))

    text = round(prop['元素充能效率'] * 100, 1)
    bg_draw.text((89, 610), '充能效率', fill='white', font=get_font(34, 'hywh.ttf'))
    bg_draw.text((473 - len(str(text)) * 17 - 17, 612), f"{text}%", fill='white',
                 font=get_font(34, 'number.ttf'))

    max_element = max(prop['伤害加成'])
    text = round(max_element * 100, 1)

    bg_draw.text((89, 669), f'{element_type[prop["伤害加成"].index(max_element)]}伤害加成', fill='white',
                 font=get_font(34, 'hywh.ttf'))
    bg_draw.text((473 - len(str(text)) * 16 - 16, 671), f"{text}%", fill='white',
                 font=get_font(34, 'number.ttf'))

    # 天赋
    if data['名称'] in ['神里绫华', '莫娜']:
        data['天赋'].pop(2)
    for i in range(3):
        bg.alpha_composite(base_icon[data['元素']].resize((132, 142)), (564, 253 + 147 * i))
        bg_draw.text((522 if data['天赋'][i]['等级'] < 10 else 513, 310 + 147 * i), str(data['天赋'][i]['等级']), fill='black',
                     font=get_font(34, 'number.ttf'))
        skill_icon = res_path2 / 'skill' / f'{data["天赋"][i]["图标"]}.png'
        skill_icon = await aiorequests.get_img(url=skill_url.format(data["天赋"][i]["图标"]), size=(57, 57), save_path=skill_icon)
        bg.alpha_composite(skill_icon, (603, 298 + 147 * i))

    # 命座
    t = 0
    for talent in data['命座']:
        bg.alpha_composite((base_icon[data['元素']]).resize((83, 90)), (510 + t * 84, 790))
        talent_icon = res_path2 / 'skill' / f'{talent["图标"]}.png'
        talent_icon = await aiorequests.get_img(url=talent_url.format(talent["图标"]), size=(45, 45), save_path=talent_icon)
        bg.alpha_composite(talent_icon, (529 + t * 84, 813))
        t += 1
    for t2 in range(t, 6):
        bg.alpha_composite((base_icon['灰']).resize((83, 90)), (510 + t2 * 84, 790))
        bg.alpha_composite(lock, (530 + t2 * 84, 813))

    # 武器
    bg.alpha_composite(weapon_bg[data['武器']['星级'] - 1], (91, 760))
    weapon_icon = res_path2 / 'weapon' / f'{data["武器"]["图标"]}.png'
    weapon_icon = await aiorequests.get_img(url=weapon_url.format(data["武器"]["图标"]), size=(150, 150), save_path=weapon_icon)
    bg.alpha_composite(weapon_icon, (91, 760))
    bg_draw.text((268, 758), data['武器']['名称'], fill='white', font=get_font(34, 'hywh.ttf'))
    for i in range(data['武器']['星级']):
        bg.alpha_composite(star, (267 + i * 30, 799))
    bg_draw.text((283, 835), f'LV{data["武器"]["等级"]}', fill='black', font=get_font(27, 'number.ttf'))
    bg_draw.text((266, 869), f'精炼{data["武器"]["精炼等级"]}阶', fill='white', font=get_font(34, 'hywh.ttf'))

    # 圣遗物
    total_score = 0
    # 第一排
    for i in range(2):
        try:
            artifact = data['圣遗物'][i]
        except IndexError:
            break
        bg.alpha_composite(weapon_bg[artifact['星级'] - 1].resize((100, 100)), (587 + 317 * i, 1002))
        reli_path = res_path2 / 'reli' / f'{artifact["图标"]}.png'
        reli_path = await aiorequests.get_img(url=artifact_url.format(artifact["图标"]), size=(100, 100), save_path=reli_path)
        bg.alpha_composite(reli_path, (587 + 317 * i, 1002))
        bg_draw.text((412 + 317 * i, 950), artifact['名称'], fill='white', font=get_font(40))
        score = artifact_total_score(artifact['词条'])
        total_score += score
        rank = 'SSS' if score >= 45 else 'SS' if 40 <= score < 45 else 'S' if 35 <= score < 40 else 'A' if 30 <= score < 35 else 'B' if 25 <= score < 30 else 'C'
        bg_draw.text((412 + 317 * i, 998), f'{rank}-{score}', fill='#ffde6b', font=get_font(28, 'number.ttf'))
        bg.alpha_composite(level_mask.resize((98, 30)), (412 + 317 * i, 1032))
        bg_draw.text((433 + 317 * i, 1033), f"LV{artifact['等级']}", fill='black', font=get_font(27, 'number.ttf'))
        bg_draw.text((411 + 317 * i, 1067), artifact['主属性']['属性名'], fill='white', font=get_font(25))
        if artifact['主属性']['属性名'] not in ['生命值', '攻击力', '元素精通']:
            bg_draw.text((408 + 317 * i, 1100), f"+{artifact['主属性']['属性值']}%", fill='white', font=get_font(25, 'number.ttf'))
        else:
            bg_draw.text((408 + 317 * i, 1100), f"+{artifact['主属性']['属性值']}", fill='white', font=get_font(48, 'number.ttf'))
        for j in range(len(artifact['词条'])):
            if '百分比' in artifact['词条'][j]['属性名']:
                text = artifact['词条'][j]['属性名'].replace('百分比', '')
            else:
                text = artifact['词条'][j]['属性名']
            bg_draw.text((411 + 317 * i, 1163 + 50 * j), text, fill='white' if check_effective(data['名称'], artifact['词条'][j]['属性名']) else '#afafaf', font=get_font(25))
            if artifact['词条'][j]['属性名'] not in ['攻击力', '防御力', '生命值', '元素精通']:
                num = '+' + str(artifact['词条'][j]['属性值']) + '%'
                text_length = 671 - len(str(artifact['词条'][j]['属性值'])) * 13 + 317 * i - 35 + 8
                if '.' not in str(artifact['词条'][j]['属性值']):
                    text_length -= 5
            else:
                num = '+' + str(artifact['词条'][j]['属性值'])
                text_length = 671 - len(str(artifact['词条'][j]['属性值'])) * 13 + 317 * i - 15
            bg_draw.text((text_length, 1163 + 50 * j), num, fill='white' if check_effective(data['名称'], artifact['词条'][j]['属性名']) else '#afafaf', font=get_font(25, 'number.ttf'))
    # 第二排
    for i in range(3):
        try:
            artifact = data['圣遗物'][i + 2]
        except IndexError:
            break
        bg.alpha_composite(weapon_bg[artifact['星级'] - 1].resize((100, 100)), (270 + 317 * i, 1439))
        reli_path = res_path2 / 'reli' / f'{artifact["图标"]}.png'
        reli_path = await aiorequests.get_img(url=artifact_url.format(artifact["图标"]), size=(100, 100),
                                              save_path=reli_path)
        bg.alpha_composite(reli_path, (270 + 317 * i, 1439))
        bg_draw.text((95 + 317 * i, 1387), artifact['名称'], fill='white', font=get_font(40))
        score = artifact_total_score(artifact['词条'])
        total_score += score
        rank = 'SSS' if score >= 45 else 'SS' if 40 <= score < 45 else 'S' if 35 <= score < 40 else 'A' if 30 <= score < 35 else 'B' if 25 <= score < 30 else 'C'
        bg_draw.text((95 + 317 * i, 1435), f'{rank}-{score}', fill='#ffde6b', font=get_font(28, 'number.ttf'))
        bg.alpha_composite(level_mask.resize((98, 30)), (95 + 317 * i, 1469))
        bg_draw.text((116 + 317 * i, 1470), f"LV{artifact['等级']}", fill='black', font=get_font(27, 'number.ttf'))
        bg_draw.text((94 + 317 * i, 1504), artifact['主属性']['属性名'], fill='white', font=get_font(25))
        if artifact['主属性']['属性名'] not in ['生命值', '攻击力', '元素精通']:
            bg_draw.text((91 + 317 * i, 1537), f"+{artifact['主属性']['属性值']}%", fill='white', font=get_font(48, 'number.ttf'))
        else:
            bg_draw.text((91 + 317 * i, 1537), f"+{artifact['主属性']['属性值']}", fill='white', font=get_font(48, 'number.ttf'))
        for j in range(len(artifact['词条'])):
            if '百分比' in artifact['词条'][j]['属性名']:
                text = artifact['词条'][j]['属性名'].replace('百分比', '')
            else:
                text = artifact['词条'][j]['属性名']
            bg_draw.text((94 + 317 * i, 1600 + 50 * j), text, fill='white' if check_effective(data['名称'], artifact['词条'][j]['属性名']) else '#afafaf', font=get_font(25))
            if artifact['词条'][j]['属性名'] not in ['攻击力', '防御力', '生命值', '元素精通']:
                num = '+' + str(artifact['词条'][j]['属性值']) + '%'
                text_length = 354 - len(str(artifact['词条'][j]['属性值'])) * 13 + 317 * i - 35 + 8
                if '.' not in str(artifact['词条'][j]['属性值']):
                    text_length -= 5
            else:
                num = '+' + str(artifact['词条'][j]['属性值'])
                text_length = 354 - len(str(artifact['词条'][j]['属性值'])) * 13 + 317 * i - 15
            bg_draw.text((text_length, 1600 + 50 * j), num, fill='white' if check_effective(data['名称'], artifact['词条'][j]['属性名']) else '#afafaf', font=get_font(25, 'number.ttf'))

    # 圣遗物评分
    bg_draw.text((118, 1057), '圣遗物总评分', fill='#afafaf', font=get_font(36))
    bg_draw.text((192, 974), str(round(total_score, 1)), fill='white', font=get_font(60, 'number.ttf'))
    total_rank = 'S' if total_score >= 200 else 'A' if 160 <= total_score < 200 else 'B' if 120 <= total_score < 160 else 'C'
    bg.alpha_composite(rank_icon[total_rank], (110, 964))

    # 圣遗物套装
    suit = []
    suit2 = []
    flag = False
    for artifact in data['圣遗物']:
        suit.append(artifact['所属套装'])
    for s in suit:
        if suit.count(s) == 4:
            reli_path = res_path2 / 'reli' / f'{data["圣遗物"][0]["图标"]}.png'
            reli_path = await aiorequests.get_img(url=artifact_url.format(data["圣遗物"][0]["图标"]), size=(110, 110),
                                                  save_path=reli_path)
            bg.alpha_composite(reli_path, (76, 1130))
            bg.alpha_composite(reli_path, (76, 1255))
            bg_draw.text((184, 1168), f'{s[:2]}四件套', fill='white', font=get_font(36))
            bg_draw.text((184, 1292), f'{s[:2]}四件套', fill='white', font=get_font(36))
            flag = True
            break
        if s not in suit2 and 1 < suit.count(s) < 4:
            suit2.append(s)
    if len(suit2) == 2:
        bg_draw.text((184, 1168), f'{suit2[0][:2]}两件套', fill='white', font=get_font(36))
        bg_draw.text((184, 1292), f'{suit2[1][:2]}两件套', fill='white', font=get_font(36))
        n = 0
        for r in data["圣遗物"]:
            if n == 2:
                break
            if r['所属套装'] in suit2:
                suit2.remove(r['所属套装'])
                reli_path = res_path2 / 'reli' / f'{r["图标"]}.png'
                reli_path = await aiorequests.get_img(url=artifact_url.format(r["图标"]), size=(110, 110),
                                                      save_path=reli_path)
                bg.alpha_composite(reli_path, (76, 1130 + n * 125))
                n += 1
    elif len(suit2) == 1:
        bg_draw.text((184, 1168), f'{suit2[0][:2]}两件套', fill='white', font=get_font(36))
        bg_draw.text((184, 1292), '未激活套装', fill='white', font=get_font(36))
        for r in data["圣遗物"]:
            if r['所属套装'] in suit2:
                reli_path = res_path2 / 'reli' / f'{r["图标"]}.png'
                reli_path = await aiorequests.get_img(url=artifact_url.format(r["图标"]), size=(110, 110),
                                                      save_path=reli_path)
                bg.alpha_composite(reli_path, (76, 1130))

                break
    elif not flag:
        bg_draw.text((184, 1168), '未激活套装', fill='white', font=get_font(36))
        bg_draw.text((184, 1292), '未激活套装', fill='white', font=get_font(36))

    # 立绘
    paint_path = res_path / 'player_card2' / '立绘' / f'{data["名称"]}.png'
    if not paint_path.exists():
        bg.alpha_composite(paint, (695, 234))
        bg.alpha_composite(loading, (872, 411))
    else:
        bg.alpha_composite(load_image(path=paint_path), (695, 234))

    bg_draw.text((50, 1870), f'更新于{data["更新时间"].replace("2022-", "")}', fill='white', font=get_font(36, '优设标题黑.ttf'))
    bg_draw.text((560, 1869), 'Created by LittlePaimon', fill='white', font=get_font(36, '优设标题黑.ttf'))

    return MessageBuild.Image(bg, quality=75)


