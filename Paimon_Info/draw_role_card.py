from PIL import Image, ImageDraw
from pathlib import Path

from utils.file_handler import load_image, load_json
from utils.enka_util import get_artifact_suit, artifact_total_value, get_expect_score, get_effective, check_effective
from utils import aiorequests
from utils.message_util import MessageBuild
from utils.PIL_util import get_font, draw_right_text, draw_center_text
from .damage_cal.damage import get_role_dmg

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
region = load_json(path=Path(__file__).parent.parent / 'utils' / 'json' / 'role_region.json')


async def draw_role_card(uid, data):
    dmg_img = get_role_dmg(data['名称'], data)
    if dmg_img:
        bg = Image.new('RGBA', (1080, 1920 + dmg_img.size[1] + 20), (0, 0, 0, 0))
        bg_card_center = bg_card[data['元素']].crop((0, 730, 1080, 1377)).resize((1080, dmg_img.size[1] + 667))
        bg.alpha_composite(bg_card[data['元素']].crop((0, 0, 1080, 730)), (0, 0))
        bg.alpha_composite(bg_card_center, (0, 730))
        bg.alpha_composite(bg_card[data['元素']].crop((0, 1377, 1080, 1920)), (0, dmg_img.size[1] + 1397))
        bg.alpha_composite(dmg_img, (71, 1846))
    else:
        bg = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
        bg.alpha_composite(bg_card[data['元素']], (0, 0))
    bg.alpha_composite(base_mask, (0, 0))
    if data['名称'] not in ['荧', '空', '埃洛伊']:
        region_icon = load_image(path=res_path / 'player_card2' / f'{region[data["名称"]]}.png', size=(130, 130))
        bg.alpha_composite(region_icon, (0, 4))
    bg_draw = ImageDraw.Draw(bg)
    bg_draw.text((131, 100), f"UID {uid}", fill='white', font=get_font(48, 'number.ttf'))
    bg_draw.text((134, 150), data['名称'], fill='white', font=get_font(72, '优设标题黑.ttf'))
    bg.alpha_composite(level_mask, (298 + 60 * (len(data['名称']) - 2), 172))
    draw_center_text(bg_draw, f'LV{data["等级"]}', 298 + 60 * (len(data['名称']) - 2),
                     298 + 60 * (len(data['名称']) - 2) + 171, 174, 'black', get_font(48, 'number.ttf'))
    # 属性值
    prop = data['属性']
    bg_draw.text((89, 262), '生命值', fill='white', font=get_font(34, 'hywh.ttf'))
    text_length = bg_draw.textlength(f"+{prop['额外生命']}", font=get_font(34, 'number.ttf'))
    draw_right_text(bg_draw, f"{prop['基础生命']}", 480 - text_length - 5, 264, 'white', get_font(34, 'number.ttf'))
    draw_right_text(bg_draw, f"+{prop['额外生命']}", 480, 264, '#59c538', get_font(34, 'number.ttf'))

    bg_draw.text((89, 319), '攻击力', fill='white', font=get_font(34, 'hywh.ttf'))
    text_length = bg_draw.textlength(f"+{prop['额外攻击']}", font=get_font(34, 'number.ttf'))
    draw_right_text(bg_draw, f"{prop['基础攻击']}", 480 - text_length - 5, 321, 'white', get_font(34, 'number.ttf'))
    draw_right_text(bg_draw, f"+{prop['额外攻击']}", 480, 321, '#59c538', get_font(34, 'number.ttf'))

    bg_draw.text((89, 377), '防御力', fill='white', font=get_font(34, 'hywh.ttf'))
    text_length = bg_draw.textlength(f"+{prop['额外防御']}", font=get_font(34, 'number.ttf'))
    draw_right_text(bg_draw, f"{prop['基础防御']}", 480 - text_length - 5, 379, 'white', get_font(34, 'number.ttf'))
    draw_right_text(bg_draw, f"+{prop['额外防御']}", 480, 379, '#59c538', get_font(34, 'number.ttf'))

    text = round(prop['暴击率'] * 100, 1)
    bg_draw.text((89, 436), '暴击率', fill='white', font=get_font(34, 'hywh.ttf'))
    draw_right_text(bg_draw, f"{text}%", 480, 438, 'white', get_font(34, 'number.ttf'))

    text = round(prop['暴击伤害'] * 100, 1)
    bg_draw.text((89, 493), '暴击伤害', fill='white', font=get_font(34, 'hywh.ttf'))
    draw_right_text(bg_draw, f"{text}%", 480, 495, 'white', get_font(34, 'number.ttf'))

    bg_draw.text((89, 551), '元素精通', fill='white', font=get_font(34, 'hywh.ttf'))
    draw_right_text(bg_draw, str(prop['元素精通']), 480, 553, 'white', get_font(34, 'number.ttf'))

    text = round(prop['元素充能效率'] * 100, 1)
    bg_draw.text((89, 610), '元素充能效率', fill='white', font=get_font(34, 'hywh.ttf'))
    draw_right_text(bg_draw, f"{text}%", 480, 612, 'white', get_font(34, 'number.ttf'))

    max_element = max(prop['伤害加成'])
    text = round(max_element * 100, 1)

    bg_draw.text((89, 669), f'{element_type[prop["伤害加成"].index(max_element)]}伤害加成', fill='white',
                 font=get_font(34, 'hywh.ttf'))
    draw_right_text(bg_draw, f"{text}%", 480, 671, 'white', get_font(34, 'number.ttf'))

    # 天赋
    if data['名称'] in ['神里绫华', '莫娜']:
        data['天赋'].pop(2)
    for i in range(3):
        bg.alpha_composite(base_icon[data['元素']].resize((132, 142)), (564, 253 + 147 * i))
        draw_center_text(bg_draw, str(data['天赋'][i]['等级']), 510, 552, 310 + 147 * i, 'black',
                         get_font(34, 'number.ttf'))
        skill_icon = res_path2 / 'skill' / f'{data["天赋"][i]["图标"]}.png'
        skill_icon = await aiorequests.get_img(url=skill_url.format(data["天赋"][i]["图标"]), size=(57, 57),
                                               save_path=skill_icon)
        bg.alpha_composite(skill_icon, (603, 298 + 147 * i))

    # 命座
    t = 0
    for talent in data['命座']:
        bg.alpha_composite((base_icon[data['元素']]).resize((83, 90)), (510 + t * 84, 790))
        talent_icon = res_path2 / 'skill' / f'{talent["图标"]}.png'
        talent_icon = await aiorequests.get_img(url=talent_url.format(talent["图标"]), size=(45, 45),
                                                save_path=talent_icon)
        bg.alpha_composite(talent_icon, (529 + t * 84, 813))
        t += 1
    for t2 in range(t, 6):
        bg.alpha_composite((base_icon['灰']).resize((83, 90)), (510 + t2 * 84, 790))
        bg.alpha_composite(lock, (530 + t2 * 84, 813))

    # 武器
    bg.alpha_composite(weapon_bg[data['武器']['星级'] - 1], (91, 760))
    weapon_icon = res_path2 / 'weapon' / f'{data["武器"]["图标"]}.png'
    weapon_icon = await aiorequests.get_img(url=weapon_url.format(data["武器"]["图标"]), size=(150, 150),
                                            save_path=weapon_icon)
    bg.alpha_composite(weapon_icon, (91, 760))
    bg_draw.text((268, 758), data['武器']['名称'], fill='white', font=get_font(34, 'hywh.ttf'))
    for i in range(data['武器']['星级']):
        bg.alpha_composite(star, (267 + i * 30, 799))
    draw_center_text(bg_draw, f'LV{data["武器"]["等级"]}', 268, 268 + 98, 835, 'black', get_font(27, 'number.ttf'))
    bg_draw.text((266, 869), f'精炼{data["武器"]["精炼等级"]}阶', fill='white', font=get_font(34, 'hywh.ttf'))

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
        bg.alpha_composite(weapon_bg[artifact['星级'] - 1].resize((100, 100)), (587 + 317 * i, 1002))
        reli_path = res_path2 / 'reli' / f'{artifact["图标"]}.png'
        reli_path = await aiorequests.get_img(url=artifact_url.format(artifact["图标"]), size=(100, 100),
                                              save_path=reli_path)
        bg.alpha_composite(reli_path, (587 + 317 * i, 1002))
        bg_draw.text((411 + 317 * i, 951), artifact['名称'], fill='white', font=get_font(40))
        value, score = artifact_total_value(data['属性'], artifact, effective)
        total_score += value
        rank = 'SSS' if score >= 140 else 'SS' if 120 <= score < 140 else 'S' if 100 <= score < 120 else 'A' if 75 <= score < 100 else 'B' if 50 <= score < 75 else 'C'
        bg_draw.text((412 + 317 * i, 998), f'{rank}-{value}', fill='#ffde6b', font=get_font(28, 'number.ttf'))
        bg.alpha_composite(level_mask.resize((98, 30)), (412 + 317 * i, 1032))
        draw_center_text(bg_draw, f"LV{artifact['等级']}", 412 + 317 * i, 412 + 317 * i + 98, 1033, 'black',
                         get_font(27, 'number.ttf'))
        bg_draw.text((411 + 317 * i, 1069), artifact['主属性']['属性名'], fill='white', font=get_font(25))
        if artifact['主属性']['属性名'] not in ['生命值', '攻击力', '元素精通']:
            bg_draw.text((408 + 317 * i, 1100), f"+{artifact['主属性']['属性值']}%", fill='white',
                         font=get_font(25, 'number.ttf'))
        else:
            bg_draw.text((408 + 317 * i, 1100), f"+{artifact['主属性']['属性值']}", fill='white',
                         font=get_font(48, 'number.ttf'))
        for j in range(len(artifact['词条'])):
            if '百分比' in artifact['词条'][j]['属性名']:
                text = artifact['词条'][j]['属性名'].replace('百分比', '')
            else:
                text = artifact['词条'][j]['属性名']
            bg_draw.text((411 + 317 * i, 1163 + 50 * j), text,
                         fill='white' if check_effective(artifact['词条'][j]['属性名'], effective) else '#afafaf',
                         font=get_font(25))
            if artifact['词条'][j]['属性名'] not in ['攻击力', '防御力', '生命值', '元素精通']:
                num = '+' + str(artifact['词条'][j]['属性值']) + '%'
            else:
                num = '+' + str(artifact['词条'][j]['属性值'])
            draw_right_text(bg_draw, num, 679 + 317 * i, 1163 + 50 * j,
                            fill='white' if check_effective(artifact['词条'][j]['属性名'], effective) else '#afafaf',
                            font=get_font(25, 'number.ttf'))
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
        bg_draw.text((94 + 317 * i, 1388), artifact['名称'], fill='white', font=get_font(40))
        value, score = artifact_total_value(data['属性'], artifact, effective)
        total_score += value
        rank = 'SSS' if score >= 140 else 'SS' if 120 <= score < 140 else 'S' if 100 <= score < 120 else 'A' if 75 <= score < 100 else 'B' if 50 <= score < 75 else 'C'
        bg_draw.text((95 + 317 * i, 1435), f'{rank}-{value}', fill='#ffde6b', font=get_font(28, 'number.ttf'))
        bg.alpha_composite(level_mask.resize((98, 30)), (95 + 317 * i, 1469))
        draw_center_text(bg_draw, f"LV{artifact['等级']}", 95 + 317 * i, 95 + 317 * i + 98, 1470, 'black',
                         get_font(27, 'number.ttf'))
        bg_draw.text((94 + 317 * i, 1506), artifact['主属性']['属性名'], fill='white', font=get_font(25))
        if artifact['主属性']['属性名'] not in ['生命值', '攻击力', '元素精通']:
            bg_draw.text((91 + 317 * i, 1537), f"+{artifact['主属性']['属性值']}%", fill='white',
                         font=get_font(48, 'number.ttf'))
        else:
            bg_draw.text((91 + 317 * i, 1537), f"+{artifact['主属性']['属性值']}", fill='white',
                         font=get_font(48, 'number.ttf'))
        for j in range(len(artifact['词条'])):
            if '百分比' in artifact['词条'][j]['属性名']:
                text = artifact['词条'][j]['属性名'].replace('百分比', '')
            else:
                text = artifact['词条'][j]['属性名']
            bg_draw.text((94 + 317 * i, 1600 + 50 * j), text,
                         fill='white' if check_effective(artifact['词条'][j]['属性名'], effective) else '#afafaf',
                         font=get_font(25))
            if artifact['词条'][j]['属性名'] not in ['攻击力', '防御力', '生命值', '元素精通']:
                num = '+' + str(artifact['词条'][j]['属性值']) + '%'
            else:
                num = '+' + str(artifact['词条'][j]['属性值'])
            draw_right_text(bg_draw, num, 362 + 317 * i, 1600 + 50 * j,
                            fill='white' if check_effective(artifact['词条'][j]['属性名'], effective) else '#afafaf',
                            font=get_font(25, 'number.ttf'))

    # 圣遗物评分
    bg_draw.text((119, 1057), '总有效词条数', fill='#afafaf', font=get_font(36))
    score_pro = total_score / (average * 5) * 100
    total_rank = 'SSS' if score_pro >= 140 else 'SS' if 120 <= score_pro < 140 else 'S' if 100 <= score_pro < 120 else 'A' if 75 <= score_pro < 100 else 'B' if 50 <= score_pro < 75 else 'C'
    if len(total_rank) == 3:
        bg.alpha_composite(rank_icon[total_rank[0]], (95, 964))
        bg.alpha_composite(rank_icon[total_rank[0]], (145, 964))
        bg.alpha_composite(rank_icon[total_rank[0]], (195, 964))
        bg_draw.text((250, 974), str(round(total_score, 1)), fill='white', font=get_font(60, 'number.ttf'))
    elif len(total_rank) == 2:
        bg.alpha_composite(rank_icon[total_rank[0]], (125, 964))
        bg.alpha_composite(rank_icon[total_rank[0]], (175, 964))
        bg_draw.text((235, 974), str(round(total_score, 1)), fill='white', font=get_font(60, 'number.ttf'))
    else:
        bg.alpha_composite(rank_icon[total_rank[0]], (143, 964))
        bg_draw.text((217, 974), str(round(total_score, 1)), fill='white', font=get_font(60, 'number.ttf'))

    # 圣遗物套装
    suit = get_artifact_suit(data['圣遗物'])
    if not suit:
        bg_draw.text((184, 1168), '未激活套装', fill='white', font=get_font(36))
        bg_draw.text((184, 1292), '未激活套装', fill='white', font=get_font(36))
    elif len(suit) == 1:
        artifact_path = res_path2 / 'reli' / f'{suit[0][1]}.png'
        artifact_path = await aiorequests.get_img(url=artifact_url.format(suit[0][1]), size=(110, 110),
                                                  save_path=artifact_path)
        bg.alpha_composite(artifact_path, (76, 1130))
        bg_draw.text((184, 1168), f'{suit[0][0][:2]}二件套', fill='white', font=get_font(36))
        bg_draw.text((184, 1292), '未激活套装', fill='white', font=get_font(36))
    else:
        if suit[0][0] == suit[1][0]:
            artifact_path1 = res_path2 / 'reli' / f'{suit[0][1]}.png'
            artifact_path1 = artifact_path2 = await aiorequests.get_img(url=artifact_url.format(suit[0][1]),
                                                                        size=(110, 110),
                                                                        save_path=artifact_path1)
            bg_draw.text((184, 1168), f'{suit[0][0][:2]}四件套', fill='white', font=get_font(36))
            bg_draw.text((184, 1292), f'{suit[0][0][:2]}四件套', fill='white', font=get_font(36))
        else:
            artifact_path1 = res_path2 / 'reli' / f'{suit[0][1]}.png'
            artifact_path1 = await aiorequests.get_img(url=artifact_url.format(suit[0][1]), size=(110, 110),
                                                       save_path=artifact_path1)
            artifact_path2 = res_path2 / 'reli' / f'{suit[1][1]}.png'
            artifact_path2 = await aiorequests.get_img(url=artifact_url.format(suit[1][1]), size=(110, 110),
                                                       save_path=artifact_path2)
            bg_draw.text((184, 1168), f'{suit[0][0][:2]}两件套', fill='white', font=get_font(36))
            bg_draw.text((184, 1292), f'{suit[1][0][:2]}两件套', fill='white', font=get_font(36))
        bg.alpha_composite(artifact_path1, (76, 1130))
        bg.alpha_composite(artifact_path2, (76, 1255))

    # 立绘
    paint_path = res_path / 'player_card2' / '立绘' / f'{data["名称"]}.png'
    if not paint_path.exists():
        bg.alpha_composite(paint, (695, 234))
        bg.alpha_composite(loading, (872, 411))
    else:
        bg.alpha_composite(load_image(path=paint_path), (695, 234))

    draw_center_text(bg_draw, f'更新于{data["更新时间"].replace("2022-", "")[:-3]}', 0, 1080, bg.size[1] - 95, '#afafaf', get_font(33, '优设标题黑.ttf'))
    bg_draw.text((24, bg.size[1] - 50), 'Created by LittlePaimon | Powered by Enka.Network', fill='white',
                 font=get_font(36, '优设标题黑.ttf'))

    return MessageBuild.Image(bg, quality=75, mode='RGB')
