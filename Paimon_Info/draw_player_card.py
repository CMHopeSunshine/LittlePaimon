import copy
import os
import random
import re

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from utils import aiorequests
from utils.message_util import MessageBuild
from utils.file_handler import load_image

res_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'res')

b = load_image(os.path.join(res_path, 'player_card', '角色卡底部.png'))
b_c = load_image(os.path.join(res_path, 'player_card', 'chara_botton.png'))
fetter = []
for i in range(0, 11):
    fetter.append(load_image(os.path.join(res_path, 'player_card', f'好感度{i}.png')))
weapon_bg = []
for i in range(1, 6):
    weapon_bg.append(load_image(os.path.join(res_path, 'player_card', f'{i}星武器.png')))
constellation = []
for i in range(0, 7):
    constellation.append(load_image(os.path.join(res_path, 'player_card', f'命之座{i}.png')))


def get_font(size):
    return ImageFont.truetype(os.path.join(res_path, 'msyh.ttc'), size)


def get_expl_per(percentage):
    if percentage < 10:
        return f'0.{percentage}%'
    elif percentage == 1000:
        return '100%'
    else:
        p = list(str(percentage))
        p.insert(-1, '.')
        return ''.join(p) + '%'


async def get_chara_card(data):
    chara_card = Image.new("RGBA", (226, 313), (255, 255, 255, 255))
    chara_img = load_image(os.path.join(res_path, 'role_card', f'{data["id"]}.png'))
    chara_card.alpha_composite(chara_img, (0, 0))
    chara_card.alpha_composite(b_c, (0, 236))
    # 命座
    if data['name'] != '埃洛伊':
        chara_card.alpha_composite(constellation[data["actived_constellation_num"]], (155, 0))
    # 好感度
    if data['name'] != '旅行者':
        chara_card.alpha_composite(fetter[data["fetter"]], (155, 166))
    # 武器背景
    chara_card.alpha_composite(weapon_bg[data["weapon"]["rarity"] - 1], (0, 227))
    # 武器图标
    weapon_icon = Path() / 'data' / 'LittlePaimon' / 'res' / 'weapon' / data['weapon']['icon'].split('/')[-1]
    weapon_icon = await aiorequests.get_img(url=data['weapon']['icon'], size=(63, 63), mode='RGBA', save_path=weapon_icon)
    chara_card.alpha_composite(weapon_icon, (0, 230))
    # 等级信息
    chara_draw = ImageDraw.Draw(chara_card)
    chara_draw.text((114, 225), f'Lv.{data["level"]}', font=get_font(25), fill='black')
    chara_draw.text((143 - 12 * len(data["weapon"]["name"]), 250), f'{data["weapon"]["name"]}', font=get_font(25),
                    fill='black')
    chara_draw.text((93, 280), f'Lv.{data["weapon"]["level"]} 精炼{data["weapon"]["affix_level"]}', font=get_font(20),
                    fill='black')
    return chara_card


async def draw_stats_data(bg_draw, stats):
    # 第一行
    bg_draw.text((203 - 10 * len(str(stats['active_day_number'])), 475), str(stats['active_day_number']),
                 font=get_font(30), fill='black')
    bg_draw.text((398 - 10 * len(str(stats['achievement_number'])), 475), str(stats['achievement_number']),
                 font=get_font(30), fill='black')
    bg_draw.text((574 - 10 * len(str(stats['avatar_number'])), 475), str(stats['avatar_number']),
                 font=get_font(30), fill='black')
    bg_draw.text((775 - 10 * len(str(stats['spiral_abyss'])), 475), str(stats['spiral_abyss']),
                 font=get_font(30), fill='black')
    # 第二行
    bg_draw.text((203 - 10 * len(str(stats['luxurious_chest_number'])), 570), str(stats['luxurious_chest_number']),
                 font=get_font(30), fill='black')
    bg_draw.text((398 - 10 * len(str(stats['precious_chest_number'])), 570), str(stats['precious_chest_number']),
                 font=get_font(30), fill='black')
    bg_draw.text((574 - 10 * len(str(stats['exquisite_chest_number'])), 570), str(stats['exquisite_chest_number']),
                 font=get_font(30), fill='black')
    bg_draw.text((774 - 10 * len(str(stats['common_chest_number'])), 570), str(stats['common_chest_number']),
                 font=get_font(30), fill='black')

    # 第三行
    bg_draw.text((203 - 10 * len(str(stats['anemoculus_number'])), 663), str(stats['anemoculus_number']),
                 font=get_font(30), fill='black')
    bg_draw.text((398 - 10 * len(str(stats['geoculus_number'])), 663), str(stats['geoculus_number']),
                 font=get_font(30), fill='black')
    bg_draw.text((574 - 10 * len(str(stats['electroculus_number'])), 663), str(stats['electroculus_number']),
                 font=get_font(30), fill='black')
    bg_draw.text((774 - 10 * len(str(stats['magic_chest_number'])), 663), str(stats['magic_chest_number']),
                 font=get_font(30), fill='black')


async def draw_homes_data(bg_draw, homes):
    bg_draw.text((162 - 10 * len(str(homes['level'])), 1167), str(homes['level']),
                 font=get_font(30), fill='black')
    bg_draw.text((374 - 10 * len(str(homes['comfort_num'])), 1167), str(homes['comfort_num']),
                 font=get_font(30), fill='black')
    bg_draw.text((579 - 10 * len(str(homes['item_num'])), 1167), str(homes['item_num']),
                 font=get_font(30), fill='black')
    bg_draw.text((787 - 10 * len(str(homes['visit_num'])), 1167), str(homes['visit_num']),
                 font=get_font(30), fill='black')


async def draw_world_data(bg_draw, data):
    # 世界探索
    noneExp = {'level': 0, 'exploration_percentage': 0, 'offerings': [{'level': 0}]}
    for d in data['world_explorations']:
        if d['name'] == '渊下宫':
            Enkanomiya = d
        elif d['name'] == '稻妻':
            Daoqi = d
        elif d['name'] == '龙脊雪山':
            Dragonspine = d
        elif d['name'] == '璃月':
            Liyue = d
        elif d['name'] == '蒙德':
            Mengde = d
        elif d['name'] == '层岩巨渊':
            ChasmsMawH = d
        elif d['name'] == '层岩巨渊·地下矿区':
            ChasmsMawL = d
    # 蒙德
    try:
        type(Mengde)
    except:
        Mengde = noneExp
    bg_draw.text((1295, 148), get_expl_per(Mengde['exploration_percentage']),
                 font=get_font(30), fill='white')
    bg_draw.text((1296, 204), 'Lv.' + str(Mengde['level']), font=get_font(30), fill='white')
    # 雪山
    try:
        type(Dragonspine)
    except:
        Dragonspine = noneExp
    bg_draw.text((1747, 148),
                 get_expl_per(Dragonspine['exploration_percentage']),
                 font=get_font(30), fill='white')
    bg_draw.text((1746, 204), 'Lv.' + str(Dragonspine['level']), font=get_font(30), fill='white')
    # 璃月
    try:
        type(Liyue)
    except:
        Liyue = noneExp
    bg_draw.text((1295, 310),
                 get_expl_per(Liyue['exploration_percentage']),
                 font=get_font(30), fill='white')
    bg_draw.text((1296, 366), 'Lv.' + str(Liyue['level']), font=get_font(30), fill='white')
    # 稻妻
    try:
        type(Daoqi)
    except:
        Daoqi = noneExp
    bg_draw.text((1747, 291),
                 get_expl_per(Daoqi['exploration_percentage']),
                 font=get_font(30), fill='white')
    bg_draw.text((1746, 336), 'Lv.' + str(Daoqi['level']), font=get_font(30), fill='white')
    bg_draw.text((1746, 380), 'Lv.' + str(Daoqi['offerings'][0]['level']), font=get_font(30), fill='white')
    # 渊下宫
    try:
        type(Enkanomiya)
    except:
        Enkanomiya = noneExp
    bg_draw.text((1747, 505),
                 get_expl_per(Enkanomiya['exploration_percentage']),
                 font=get_font(30), fill='white')
    # 层岩巨渊
    try:
        type(ChasmsMawH)
    except:
        ChasmsMawH = noneExp
    try:
        type(ChasmsMawL)
    except:
        ChasmsMawL = noneExp
    bg_draw.text((1295, 455),
                 get_expl_per(ChasmsMawH['exploration_percentage']),
                 font=get_font(30), fill='white')
    bg_draw.text((1295, 503),
                 get_expl_per(ChasmsMawL['exploration_percentage']),
                 font=get_font(30), fill='white')
    bg_draw.text((1296, 547),
                 'Lv.' + str(ChasmsMawL['offerings'][0]['level']),
                 font=get_font(30), fill='white')


async def draw_player_card(data, chara_data, uid, nickname="旅行者"):
    if not data:
        return '数据出错'
    if data['retcode'] == 10102:
        return f'uid{uid}没有在米游社公开信息哦,请到 个人主页-管理 中打开'
    elif data['retcode'] == 10104:
        return f'uid{uid}有误哦，检查一下吧'
    elif data['retcode'] != 0:
        return f'派蒙获取{uid}数据失败了，获取状态：\n{data["message"]},{data["retcode"]}'
    data = data['data']
    bg_img = load_image(os.path.join(res_path, 'player_card', '背景.png'), mode='RGBA')
    bg_draw = ImageDraw.Draw(bg_img)
    # 头部名片
    name_id = random.choice(data['avatars'][0:8])['id']
    name_card = load_image(os.path.join(res_path, 'name_card', f'{name_id}.png'), crop=(0, 40, 840, 360), size=(846, 360))
    avatar = load_image(os.path.join(res_path, 'role_profile', f'{name_id}.png'), size=(240, 240))
    bg_img.alpha_composite(name_card, (57, 27))
    bg_img.alpha_composite(avatar, (360, 25))
    uid_bg = load_image(os.path.join(res_path, 'player_card', 'UID_bg.png'), size=(280, 100))
    bg_img.alpha_composite(uid_bg, (340, 247))
    bg_draw.text((354, 259), f'昵称 {nickname}', font=get_font(30), fill='white')
    bg_draw.text((354, 291), f'UID {uid}', font=get_font(30), fill='white')
    # 数据总览
    stats = data['stats']
    await draw_stats_data(bg_draw, stats)
    # 尘歌壶
    h_lock = load_image(os.path.join(res_path, 'player_card', '未解锁.png'))
    homes_list = {'罗浮洞': {'unlock': False, 'posi': (79, 852)}, '清琼岛': {'unlock': False, 'posi': (79, 1000)},
                  '翠黛峰': {'unlock': False, 'posi': (489, 852)}, '绘绮庭': {'unlock': False, 'posi': (489, 1000)}}
    if data['homes']:
        for hl in homes_list.items():
            for h in data['homes']:
                if hl[0] in h.values():
                    h_img = load_image(os.path.join(res_path, 'player_card', f'{hl[0]}.png'))
                    bg_img.alpha_composite(h_img, hl[1]['posi'])
                    homes_list[hl[0]]['unlock'] = True
        for hl in homes_list.items():
            if not hl[1]['unlock']:
                bg_img.alpha_composite(h_lock, hl[1]['posi'])
        homes = data['homes'][0]
    else:
        homes = {'level': '无数据', 'visit_num': '无数据', 'comfort_num': '无数据', 'item_num': '无数据'}
    await draw_homes_data(bg_draw, homes)
    # 世界探索
    await draw_world_data(bg_draw, data)
    # 角色
    nocha = ''
    if chara_data['data']:
        chara_data = chara_data['data']['avatars']
        w = 1045
        i = 0
        for chara in chara_data:
            i += 1
            chara_card = await get_chara_card(chara)
            if i <= 4:
                bg_img.alpha_composite(chara_card.resize((180, 249)), (840 + i * 205, 700))
            elif i > 4 and i <= 8:
                bg_img.alpha_composite(chara_card.resize((180, 249)), (840 + (i - 4) * 205, 974))
            elif i > 8:
                break
    else:
        nocha = f'*uid{uid}关闭了角色详情显示，派蒙看不到哦'
    return MessageBuild.Image(bg_img, quality=80) + MessageBuild.Text(nocha)


# ysa
async def get_chara_card_long(data):
    chara_card = Image.new("RGBA", (226, 382), (255, 255, 255, 255))
    chara_img = load_image(os.path.join(res_path, 'role_card', f'{data["id"]}.png'))
    chara_card.alpha_composite(chara_img, (0, 0))
    chara_card.alpha_composite(b, (0, 282))
    # 命座
    if data['name'] != '埃洛伊':
        actived_constellation_num = load_image(
            os.path.join(res_path, 'player_card', f'命之座{data["actived_constellation_num"]}.png'))
        chara_card.alpha_composite(actived_constellation_num, (155, 0))
    # 好感度
    if data['name'] != '旅行者':
        chara_card.alpha_composite(fetter[data['fetter']], (155, 166))
    # 武器背景
    chara_card.alpha_composite(weapon_bg[data["weapon"]["rarity"] - 1], (3, 288))
    weapon_icon = Path() / 'data' / 'LittlePaimon' / 'res' / 'weapon' / data['weapon']['icon'].split('/')[-1]
    weapon_icon = await aiorequests.get_img(url=data['weapon']['icon'], size=(62, 62), mode='RGBA', save_path=weapon_icon)
    chara_card.alpha_composite(weapon_icon, (3, 291))
    # 等级信息
    chara_draw = ImageDraw.Draw(chara_card)
    chara_draw.text((90 - 10 * len(str(data["level"])), 230), f'Lv.{data["level"]}', font=get_font(35), fill='black')
    chara_draw.text((143 - 12 * len(data["weapon"]["name"]), 283), f'{data["weapon"]["name"]}', font=get_font(25),
                    fill='black')
    chara_draw.text((135 - 10 * len(str(data["weapon"]["level"])), 312), f'Lv.{data["weapon"]["level"]}',
                    font=get_font(22),
                    fill='black')
    chara_draw.text((114, 336), f'精炼{data["weapon"]["affix_level"]}', font=get_font(22),
                    fill='#BB9D7C')
    return chara_card


async def draw_all_chara_card(data, uid):
    if not data:
        return '数据出错'
    if data['retcode'] == 10102:
        return f'uid{uid}没有在米游社公开信息哦,请到 个人主页-管理 中打开'
    elif data['retcode'] == 10104:
        return f'uid{uid}有误哦，检查一下吧'
    elif data['retcode'] != 0:
        return f'派蒙获取{uid}数据失败了，获取状态：\n{data["message"]},{data["retcode"]}'
    data = data['data']['avatars']
    chara_num = len(data)
    col = int(chara_num / 4)
    if not chara_num % 4 == 0:
        col += 1
    for chara in data:
        if chara['name'] == '旅行者':
            chara['rarity'] = 4.5
        if chara['name'] == '埃洛伊':
            chara['rarity'] = 4.5
    chara_list = sorted(data, key=lambda i: (
    i['rarity'], i['actived_constellation_num'], i['level'], i['fetter'], i['weapon']['rarity']), reverse=True)
    bg_top = load_image(os.path.join(res_path, 'player_card', '卡片顶部.png'))
    avatar = load_image(os.path.join(res_path, 'role_profile', f'{chara_list[0]["id"]}.png'), size=(220, 220))
    bg_top.alpha_composite(avatar, (542, 30))
    draw = ImageDraw.Draw(bg_top)
    draw.text((538, 235), f'UID {uid}', font=get_font(30), fill='black')

    bg_middle = load_image(os.path.join(res_path, 'player_card', '卡片身体.png'), size=(1304, 474))
    bg_bottom = load_image(os.path.join(res_path, 'player_card', '卡片底部.png'))
    bg_img = Image.new('RGBA', (1304, 382 + col * 424 + (col - 1) * 50 + 87), (0, 0, 0, 0))
    bg_img.paste(bg_top, (0, 0))
    for i in range(0, col):
        bg_img.paste(bg_middle, (0, 382 + i * 474))
    n = 0
    for chara in chara_list:
        chara_card = (await get_chara_card_long(chara)).resize((251, 424))
        bg_img.alpha_composite(chara_card, (75 + 301 * (n % 4), 390 + 474 * int(n / 4)))
        n += 1
    bg_img.paste(bg_bottom, (0, 382 + col * 474 - 50))

    return MessageBuild.Image(bg_img, size=0.9, quality=70)


# ysc
shadow = load_image(os.path.join(res_path, 'other', 'shadow.png'))


async def draw_reli_icon(data):
    base_icon = load_image(os.path.join(res_path, 'other', f'star{data["rarity"]}.png'), size=(80, 80))
    icon = Path() / 'data' / 'LittlePaimon' / 'res' / 'reli' / data['icon'].split('/')[-1]
    icon = await aiorequests.get_img(url=data["icon"], size=(80, 80), mode='RGBA', save_path=icon)
    base_icon.alpha_composite(icon, (0, 0))
    base_icon.alpha_composite(shadow, (40, 60))
    base_icon_draw = ImageDraw.Draw(base_icon)
    base_icon_draw.text((43, 59), f'+{data["level"]}', font=get_font(16), fill="white")
    return base_icon


async def draw_const_skill_icon(data, name):
    base_icon = load_image(os.path.join(res_path, 'other', '命座.png'), size=(65, 65))
    icon = Path() / 'data' / 'LittlePaimon' / 'res' / 'skill' / data['icon'].split('/')[-1]
    icon = await aiorequests.get_img(url=data["icon"], size=(65, 65), mode='RGBA', save_path=icon)
    base_icon.alpha_composite(icon, (0, 0))
    if 'is_actived' in data and not data['is_actived']:
        unlock_icon = load_image(os.path.join(res_path, 'other', '命座未解锁.png'), size=(65, 65))
        base_icon.alpha_composite(unlock_icon, (0, 0))
    return base_icon


async def draw_line(p):
    img = Image.new('RGBA', (1000, 80), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((840, 0, 880, 80), fill='white')
    draw.ellipse((0, 0, 40, 80), fill='white')
    draw.rectangle((20, 0, 860, 80), fill='white')
    if p <= 0:
        p = 0.01
    elif p > 1:
        p = 1
    w = 800 * p
    draw.ellipse((w + 40 - 8, 80 / 6, w + 80 - 8, 80 / 6 * 5), fill='#CE9B51')
    draw.ellipse((8, 80 / 6, 40 + 8, 80 / 6 * 5), fill='#CE9B51')
    draw.rectangle((20 + 8, 80 / 6, w + 60 - 8, 80 / 6 * 5), fill='#CE9B51')
    img = img.resize((250, 20), Image.ANTIALIAS)
    return img


async def draw_chara_card(data, skill_data, chara_name, uid):
    if not data:
        return f'{uid}数据出错'
    if data['retcode'] == 10102:
        return f'uid{uid}没有在米游社公开信息哦,请到 个人主页-管理 中打开'
    elif data['retcode'] == 10104:
        return f'uid{uid}有误哦，检查一下吧'
    elif data['retcode'] != 0:
        return f'派蒙获取{uid}数据失败了，获取状态:\n{data["message"]},{data["retcode"]}'
    data = data['data']['avatars']
    f = False
    for chara in data:
        if chara['id'] == int(chara_name[1]) or (chara_name[0] in ['空', '荧'] and chara['name'] == '旅行者'):
            character = chara
            f = True
            break
    if not f:
        return f'{chara_name[0]}不在{uid}公开的8个角色中或没有这个角色哦'
    # 立绘
    bg_img = load_image(os.path.join(res_path, 'name_card', f'{character["id"]}.png'))
    bg_draw = ImageDraw.Draw(bg_img)
    if character['id'] == 10000007:
        chara_img = load_image(os.path.join(res_path, 'role_splash', '荧.png'), mode='RGBA')
    elif character['id'] == 10000005:
        chara_img = load_image(os.path.join(res_path, 'role_splash', '空.png'), mode='RGBA')
    else:
        chara_img = load_image(os.path.join(res_path, 'role_splash', f'{character["name"]}.png'), mode='RGBA')
    W, H = chara_img.size
    chara_img = chara_img.resize((int(W * 400 / H), 400))
    bg_img.alpha_composite(chara_img, (0, 0))

    # 名称 UID 等级 亲密度
    bg_draw.text((260, 20), f'{character["name"]}', font=get_font(36), fill='white')
    bg_draw.text((275 + 36 * len(character["name"]), 35), f'UID{uid}', font=get_font(23), fill='white')
    bg_draw.text((260, 83), '等级', font=get_font(25), fill='white')
    bg_draw.text((260, 128), '亲密', font=get_font(25), fill='white')
    if character['name'] == '旅行者':
        character['fetter'] = 10
    bg_img.alpha_composite(await draw_line(character['level'] / 90), (330, 92))
    bg_img.alpha_composite(await draw_line(character['fetter'] / 10), (330, 137))
    bg_draw.text((560, 83), f'Lv.{character["level"]}', font=get_font(25), fill='white')
    fetter = load_image(os.path.join(res_path, 'player_card', f'好感度{character["fetter"]}.png'), size=(57, 49))
    bg_img.alpha_composite(fetter, (560, 122))

    # 武器
    weapon_bg = load_image(os.path.join(res_path, 'other', f'star{character["weapon"]["rarity"]}.png'), size=(100, 100))
    weapon_icon = Path() / 'data' / 'LittlePaimon' / 'res' / 'weapon' / character['weapon']['icon'].split('/')[-1]
    weapon_icon = await aiorequests.get_img(url=character['weapon']['icon'], size=(100, 100), mode='RGBA', save_path=weapon_icon)
    bg_img.alpha_composite(weapon_bg, (293, 175))
    bg_img.alpha_composite(weapon_icon, (293, 175))
    bg_img.alpha_composite(shadow.resize((50, 25)), (344, 250))
    bg_draw.text((348, 250), f'Lv.{character["weapon"]["level"]}', font=get_font(18), fill='white')
    weapon_star = load_image(
        os.path.join(res_path, 'player_card', f'命之座{character["weapon"]["affix_level"]}.png'), size=(40, 40))
    bg_img.alpha_composite(weapon_star, (353, 175))

    # 圣遗物
    reli_p = [(406, 195), (499, 195), (313, 289), (406, 289), (499, 289)]
    i = 0
    for reli in character['reliquaries']:
        reli_icon = await draw_reli_icon(reli)
        bg_img.alpha_composite(reli_icon, reli_p[i])
        i += 1

    if not skill_data:
        skill_data_ = {'retcode': 'error'}
    else:
        skill_data_ = copy.deepcopy(skill_data)

    # 补上三命和五命的技能等级提升
    if skill_data_['retcode'] == 0 and character['constellations'][2]['is_actived']:
        skill_name = re.search(r'>(.*)</color>', character['constellations'][2]['effect'])
        if skill_name:
            skill_name = skill_name.group(1)
            for skill in skill_data_['data']['skill_list']:
                if skill['name'] == skill_name:
                    skill['level_current'] += 3
    if skill_data_['retcode'] == 0 and character['constellations'][4]['is_actived']:
        skill_name = re.search(r'>(.*)</color>', character['constellations'][4]['effect'])
        if skill_name:
            skill_name = skill_name.group(1)
            for skill in skill_data_['data']['skill_list']:
                if skill['name'] == skill_name:
                    skill['level_current'] += 3

    # 天赋等级
    i = 0
    if skill_data_['retcode'] == 0:
        skill_p = [(621, 98), (621, 168), (621, 238)]
        skill_data_t = skill_data_['data']['skill_list']
        for skill in skill_data_t[0:2]:
            skill_icon = await draw_const_skill_icon(skill, character['name'])
            bg_img.alpha_composite(skill_icon, skill_p[i])
            bg_img.alpha_composite(shadow.resize((50, 25)), (skill_p[i][0] + 69, skill_p[i][1] + 22))
            bg_draw.text((skill_p[i][0] + 73 + (6 if skill["level_current"] < 10 else 0), skill_p[i][1] + 22),
                         f'Lv.{skill["level_current"]}', font=get_font(18), fill='white')
            i += 1
        # 绫华和莫娜特别
        if character['name'] == '神里绫华' or character['name'] == '莫娜':
            skill = skill_data_t[3]
        else:
            skill = skill_data_t[2]
        skill_icon = await draw_const_skill_icon(skill, character['name'])
        bg_img.alpha_composite(skill_icon, skill_p[i])
        bg_img.alpha_composite(shadow.resize((50, 25)), (skill_p[i][0] + 69, skill_p[i][1] + 22))
        bg_draw.text((skill_p[i][0] + 73 + (6 if skill["level_current"] < 10 else 0), skill_p[i][1] + 22),
                     f'Lv.{skill["level_current"]}', font=get_font(18), fill='white')
    # 命座
    i = 0
    if skill_data_['retcode'] == 0:
        const_p = [(669, 8), (734, 60), (757, 130), (757, 207), (734, 277), (669, 329)]
    else:
        const_p = [(626, 8), (691, 60), (714, 130), (714, 207), (691, 277), (626, 329)]
    for const in character['constellations']:
        const_icon = await draw_const_skill_icon(const, character['name'])
        bg_img.alpha_composite(const_icon, const_p[i])
        i += 1

    bg_draw.text((330, 371), 'Created by LittlePaimon', font=get_font(20), fill='white')

    return MessageBuild.Image(bg_img, size=0.95, quality=80, mode='RGB')
