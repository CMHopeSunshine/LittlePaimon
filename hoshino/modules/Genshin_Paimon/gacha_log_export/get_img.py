from PIL import Image, ImageDraw, ImageFont
import os
from ..util import pil2b64
from ..character_alias import get_short_name
from hoshino.typing import MessageSegment

res_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'res')

def get_font(size):
    return ImageFont.truetype(os.path.join(res_path, 'msyh.ttc'), size)

async def get_circle_avatar(avatar, size):
    avatar = Image.open(os.path.join(res_path, 'thumb', f'{avatar}.png'))
    w, h = avatar.size
    bg = Image.new('RGBA', (w, h), (213, 153, 77, 255))
    bg.alpha_composite(avatar, (0, 0))
    bg = bg.resize((size, size))
    scale = 5
    mask = Image.new('L', (size * scale, size * scale), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size * scale, size * scale), fill=255)
    mask = mask.resize((size, size), Image.ANTIALIAS)
    ret_img = bg.copy()
    ret_img.putalpha(mask)
    return ret_img

async def sort_data(gacha_data):
    sprog_data = {'type': '新手', 'total_num': 0, '5_star': [], '4_star': [], '5_gacha': 0, '4_gacha': 0}
    permanent_data = {'type': '常驻', 'total_num': 0, '5_star': [], '4_star': [], '5_gacha': 0, '4_gacha': 0}
    role_data = {'type': '角色', 'total_num': 0, '5_star': [], '4_star': [], '5_gacha': 0, '4_gacha': 0}
    weapon_data = {'type': '武器', 'total_num': 0, '5_star': [], '4_star': [], '5_gacha': 0, '4_gacha': 0}
    new_gacha_data = [sprog_data, permanent_data, role_data, weapon_data]
    i = 0
    for pool in gacha_data['gachaLog'].values():
        pool.reverse()
        new_gacha_data[i]['total_num'] = len(pool)
        for p in pool:
            if p['rank_type'] == "5":
                new_gacha_data[i]['5_star'].append((p['name'], new_gacha_data[i]['5_gacha'] + 1))
                new_gacha_data[i]['5_gacha'] = 0
                new_gacha_data[i]['4_gacha'] = 0
            elif p['rank_type'] == "4":
                new_gacha_data[i]['4_star'].append((p['name'], new_gacha_data[i]['4_gacha'] + 1))
                new_gacha_data[i]['5_gacha'] += 1
                new_gacha_data[i]['4_gacha'] = 0
            else:
                new_gacha_data[i]['5_gacha'] += 1
                new_gacha_data[i]['4_gacha'] += 1
        i += 1
    return new_gacha_data

async def draw_gacha_log(data):
    if data['total_num'] == 0:
        return None
    top = Image.open(os.path.join(res_path, 'player_card', 'gacha_log_top.png'))
    mid = Image.open(os.path.join(res_path, 'player_card', '卡片身体.png')).resize((768, 80))
    bottom = Image.open(os.path.join(res_path, 'player_card', '卡片底部.png')).resize((768, 51))
    five_star = data['5_star']
    col = int(len(five_star) / 6)
    if not len(five_star) % 6 == 0:
        col += 1
    top_draw = ImageDraw.Draw(top)
    top_draw.text((348, 30), f'{data["type"]}池', font=get_font(24), fill='#F8F5F1')
    top_draw.text((145 - 6 * len(str(data["total_num"])), 88), f'{data["total_num"]}', font=get_font(24), fill='black')
    five_ave = round(sum([x[1] for x in five_star]) / len(five_star), 1) if five_star else ' '
    top_draw.text((321 - 10 * len(str(five_ave)), 88), f'{five_ave}', font=get_font(24), fill='black' if five_ave != ' ' and five_ave > 60 else 'red')
    five_per = round(len(five_star) / (data['total_num'] - data['5_gacha']) * 100, 2) if five_star else -1
    five_per_str = str(five_per) + '%' if five_per > -1 else ' '
    top_draw.text((427, 88), f'{five_per_str}', font=get_font(24), fill='black' if five_per < 1.7 else 'red')
    five_up = round(len([x[0] for x in five_star if not x[0] in ['刻晴', '迪卢克', '七七', '莫娜', '琴']]) / len(five_star) * 100,
                        1) if five_star else -1
    five_up_str = str(five_up) + '%' if five_per > -1 else ' '
    top_draw.text((578 if len(five_up_str) != 6 else 569, 88), f'{five_up_str}', font=get_font(24), fill='black' if five_up < 75 else 'red')
    most_five = sorted(five_star, key=lambda x: x[1], reverse=False)[0][0] if five_star else ' '
    top_draw.text((152 - 14 * len(most_five), 163), f'{most_five}', font=get_font(24), fill='red')
    four_ave = round(sum([x[1] for x in data['4_star']]) / len(data['4_star']), 1) if data['4_star'] else ' '
    top_draw.text((316 - 10 * len(str(four_ave)), 163), f'{four_ave}', font=get_font(24), fill='black' if four_ave != ' ' and four_ave > 7 else 'red')
    top_draw.text((461 - 6 * len(str(data['5_gacha'])), 163), f'{data["5_gacha"]}', font=get_font(24), fill='black')
    top_draw.text((604, 163), f'{data["4_gacha"]}', font=get_font(24), fill='black')
    bg_img = Image.new('RGBA', (768, 288 + col * 80 - (20 if col > 0 else 0) + 51), (0, 0, 0, 0))
    bg_img.paste(top, (0, 0))
    for i in range(0, col):
        bg_img.paste(mid, (0, 288 + i * 80))
    bg_img.paste(bottom, (0, 288 + col * 80 - (20 if col > 0 else 0)))
    bg_draw = ImageDraw.Draw(bg_img)
    n = 0
    for c in five_star:
        avatar = await get_circle_avatar(c[0], 45)
        f = 10 if data['type'] == '武器' else 0
        if c[1] <= 20:
            color = 'red'
        elif 20 < c[1] <= 50 - f:
            color = 'orangered'
        elif 50 - f < c[1] < 70 - f:
            color = 'darkorange'
        else:
            color = 'black'
        bg_img.alpha_composite(avatar, (30 + 120 * (n % 6), 298 + 80 * int(n / 6)))
        name = get_short_name(c[0])
        bg_draw.text((111 + 120 * (n % 6) - 8 * len(name), 298 + 80 * int(n / 6)), name, font=get_font(16), fill=color)
        bg_draw.text((107 - 5 * len(str(c[1])) + 120 * (n % 6), 317 + 80 * int(n / 6)), f'[{c[1]}]', font=get_font(16), fill=color)
        n += 1
    return bg_img

async def get_gacha_log_img(gacha_data, pool):
    all_gacha_data = await sort_data(gacha_data)
    if pool != 'all':
        for pd in all_gacha_data:
            if pd['type'] == pool:
                img = await draw_gacha_log(pd)
                break
        if not img:
            return '这个池子没有抽卡记录哦'
        total_height = (img.size)[1]
    else:
        img_list = []
        total_height = 0
        now_height = 0
        for pd in all_gacha_data:
            p_img = await draw_gacha_log(pd)
            if p_img:
                img_list.append(p_img)
                total_height += (p_img.size)[1]
        if not img_list:
            return '没有找到任何抽卡记录诶！'
        img = Image.new('RGBA', (768, total_height), (0, 0, 0, 255))
        for i in img_list:
            img.paste(i, (0, now_height))
            now_height += (i.size)[1]
    img_draw = ImageDraw.Draw(img)
    img_draw.text((595, 44), f'UID:{gacha_data["uid"]}', font=get_font(16), fill='black')
    img_draw.text((530, total_height - 45), 'Created by 惜月の小派蒙', font=get_font(16), fill='black')

    img = pil2b64(img, 95)
    img = MessageSegment.image(img)
    return img

        