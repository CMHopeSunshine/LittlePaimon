import numpy,random,datetime
import re, copy ,json
from enum import Enum
from pathlib import Path
from PIL import Image, PngImagePlugin, ImageDraw, ImageFont
from ..util import pil2b64
import os

from .gacha_role import init_user_info, user_info, save_user_info
assets_dir = Path(__file__) .parent.parent / 'res' / 'gacha_res'
font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'res', 'zh-cn.ttf')
countfont = ImageFont.truetype(font_path, 35)
timefont = ImageFont.truetype(font_path, 20)
with open(assets_dir / 'type.json', 'r', encoding="utf-8") as fp:
    type_json = json.load(fp)
    
cache_img = {}
cache_item = {}

def random_int():
    return numpy.random.randint(low=0, high=10000, size=None, dtype='l')

# 抽卡概率来自https://www.bilibili.com/read/cv10468091
# 角色抽卡概率
def character_probability(rank, count):
    ret = 0
    count += 1
    if rank == 5 and count <= 73:
        ret = 60
    elif rank == 5 and count >= 74:
        ret = 60 + 600 * (count - 73)
    elif rank == 4 and count <= 8:
        ret = 510
    elif rank == 4 and count >= 9:
        ret = 510 + 5100 * (count - 8)
    return ret

# 武器抽卡概率
def weapon_probability(rank, count):
    ret = 0
    count += 1
    if rank == 5 and count <= 62:
        ret = 70
    elif rank == 5 and count <= 73:
        ret = 70 + 700 * (count - 62)
    elif rank == 5 and count >= 74:
        ret = 7770 + 350 * (count - 73)
    elif rank == 4 and count <= 7:
        ret = 600
    elif rank == 4 and count == 8:
        ret = 6600
    elif rank == 4 and count >= 9:
        ret = 6600 + 3000 * (count - 8)
    return ret

def get_pool_type(gacha_type):
    if gacha_type == 301 or gacha_type == 400:
        return 'role'
    if gacha_type == 200:
        return 'permanent'
    return 'weapon'

def get_rank(uid , pool_str):
    value = random_int()
    if pool_str == 'weapon':
        index_5 = weapon_probability(5, user_info[uid]["gacha_list"][("gacha_5_%s" % pool_str)])
        index_4 = weapon_probability(4, user_info[uid]["gacha_list"][("gacha_4_%s" % pool_str)]) + index_5
    else:
        index_5 = character_probability(5, user_info[uid]["gacha_list"][("gacha_5_%s" % pool_str)])
        index_4 = character_probability(4, user_info[uid]["gacha_list"][("gacha_4_%s" % pool_str)]) + index_5
    if value <= index_5:
        return 5
    elif value <= index_4:
        return 4
    else:
        return 3

def is_Up(uid, rank, pool_str):
    if pool_str == 'permanent':
        return False
    elif pool_str == 'weapon':
        return random_int() <= 7500 or user_info[uid]["gacha_list"]["is_up_%s_weapon" % rank]
    else:
        return random_int() <= 5000 or user_info[uid]["gacha_list"]["is_up_%s_role" % rank]

def once(uid, gacha_data):
    role = {}
    init_user_info(uid)
    pool_str = get_pool_type(gacha_data['gacha_type'])
    # 判定星级
    rank = get_rank(uid, pool_str)
    # 是否为up
    if rank != 3:
        is_up = is_Up(uid, rank, pool_str)
    user_info[uid]["gacha_list"]["wish_total"] += 1
    if rank == 3:
        role = random.choice(gacha_data['r3_prob_list'])
        user_info[uid]["gacha_list"][("gacha_4_%s" % pool_str)] += 1
        user_info[uid]["gacha_list"][("gacha_5_%s" % pool_str)] += 1
        role['count'] = 1
    else:
        if rank == 5 and pool_str == 'weapon' and user_info[uid]["gacha_list"]["dg_time"] == 2 and "pool_type" not in gacha_data:
            role['item_name'] = user_info[uid]["gacha_list"]["dg_name"]
            role['item_type'] = '武器'
            role['rank'] = rank
        elif is_up:
            role = random.choice(gacha_data['r%s_up_items' % rank])
            user_info[uid]["gacha_list"]["wish_%s_up" % rank] += 1
            role['rank'] = rank
        else:
            role = random.choice(gacha_data['r%s_prob_list' % rank])
            while True:
                role = random.choice(gacha_data['r%s_prob_list' % rank])
                if role['is_up'] == 0:
                    break
        if rank == 4:
            user_info[uid]["gacha_list"][("gacha_5_%s" % pool_str)] += 1
        elif rank == 5:
            user_info[uid]["gacha_list"][("gacha_4_%s" % pool_str)] += 1
            if pool_str == 'weapon' and "pool_type" not in gacha_data:
                if user_info[uid]["gacha_list"]["dg_name"] == '':
                    role['dg_time'] = -1
                elif role['item_name'] != user_info[uid]["gacha_list"]["dg_name"]:
                    user_info[uid]["gacha_list"]["dg_time"] += 1
                    role['dg_time'] = user_info[uid]["gacha_list"]["dg_time"]
                else:
                    user_info[uid]["gacha_list"]["dg_name"] = ''
                    user_info[uid]["gacha_list"]["dg_time"] = 0
                    role['dg_time'] = 3
        user_info[uid]["gacha_list"]["wish_%s" % rank] += 1
        if gacha_data['gacha_type'] != 200:
            user_info[uid]["gacha_list"][("is_up_%s_%s"%(rank,pool_str))] = not is_up
        if role['item_type'] == '角色':
            itemname = 'role'
        else:
            itemname = 'weapon'
        if role['item_name'] not in user_info[uid]["role_list"]:
            user_info[uid]["%s_list" % itemname][role['item_name']] = {}
            user_info[uid]["%s_list" % itemname][role['item_name']]['数量'] = 1
            user_info[uid]["%s_list" % itemname][role['item_name']]['出货'] = []
            if rank == 5:
                user_info[uid]["%s_list" % itemname][role['item_name']]['星级'] = '★★★★★'
                user_info[uid]["%s_list" % itemname][role['item_name']]['出货'].append((user_info[uid]['gacha_list']['gacha_%s_%s' % (rank,pool_str)] + 1))
            else:
                user_info[uid]["%s_list" % itemname][role['item_name']]['星级'] = '★★★★'
        else:
            user_info[uid]["%s_list" % itemname][role['item_name']]['数量'] += 1
            if rank == 5:
                user_info[uid]["%s_list" % itemname][role['item_name']]['出货'].append((user_info[uid]['gacha_list']['gacha_%s_%s' % (rank,pool_str)] + 1))
        role['count'] = user_info[uid]["gacha_list"]["gacha_%s_%s" % (rank,pool_str)] + 1
        user_info[uid]["gacha_list"]["gacha_%s_%s" % (rank,pool_str)] = 0
    save_user_info()
    return role

def get_assets(path) -> PngImagePlugin.PngImageFile:
    base_path = assets_dir

    cache = cache_img.get(path)
    if cache:
        return copy.deepcopy(cache)
    else:
        cache_img[path] = Image.open(str(base_path / path))
    return get_assets(path)

def item_bg(rank):
    return get_assets('%s_background.png' % str(rank)).resize((143, 845))

def rank_icon(rank):
    return get_assets('%s_star.png' % str(rank))

async def create_item(rank, item_type, name, element, count, dg_time):
    bg = item_bg(rank)
    item_img = get_assets(Path(item_type) / (name + '.png'))
    rank_img = rank_icon(rank).resize((119, 30))

    if item_type == '角色':
        item_img = item_img.resize((item_img.size[0] + 12, item_img.size[1] + 45))
        item_img.alpha_composite(rank_img, (4, 510))

        item_type_icon = get_assets(Path('元素') / (element + '.png')).resize((80, 80))
        item_img.alpha_composite(item_type_icon, (25, 420))
        bg.alpha_composite(item_img, (3, 125))

    else:
        bg.alpha_composite(item_img, (3, 240))
        bg.alpha_composite(rank_img, (9, 635))

        item_type_icon = type_json.get(name)
        if item_type_icon:
            item_type_icon = get_assets(Path('类型') / (item_type_icon + '.png')).resize((100, 100))

            bg.alpha_composite(item_type_icon, (18, 530))
    if rank == 5 and count != -1:
        draw = ImageDraw.Draw(bg)
        if len(str(count)) == 2:
            draw.text((19,750),('['+str(count)+'抽]'), font=countfont, fill='white')
        else:
            draw.text((26,750),('['+str(count)+'抽]'), font=countfont, fill='white')
        if dg_time != -1:
            if dg_time == 3:
                draw.text((3,785),('定轨结束'), font=countfont, fill='white')
            else:
                draw.text((7,785),('定轨'+str(dg_time)+'/2'), font=countfont, fill='white')
    return bg


async def ten(uid, gacha_data, sd) -> PngImagePlugin.PngImageFile:
    gacha_list = []
    for i in range(0,10):
        if gacha_data['gacha_type'] == 'all_star':
            role = random.choice(gacha_data['list'])
            role['count'] = -1
            role['rank'] = 5
        else:
            role = once(uid,gacha_data).copy()
        gacha_list.append(role)
    gacha_list.sort(key = lambda x:x["rank"],reverse=True)
    img: PngImagePlugin.PngImageFile
    img = get_assets('background.png')
    i = 0
    for wish in gacha_list:
        i += 1
        rank = wish['rank']
        item_type = wish['item_type']
        name = wish['item_name']
        element = wish.get('item_attr') or type_json[name]
        count = wish['count']
        try:
            dg_time = wish['dg_time']
        except:
            dg_time = -1
        i_img = await create_item(rank, item_type, name, element, count, dg_time)
        img.alpha_composite(i_img, (105 + (i_img.size[0] * i), 123))

    img.thumbnail((1024, 768))
    img2 = Image.new("RGB", img.size, (255, 255, 255))
    img2.paste(img, mask=img.split()[3])
    return img2

async def more_ten(uid, gacha_data, num, sd):
    time_str = datetime.datetime.strftime(datetime.datetime.now(),'%m-%d %H:%M')
    if num == 1:
        img = await ten(uid,gacha_data, sd)
    else:
        img = Image.new("RGB", (1024, 575 * num), (255, 255, 255))
        for i in range(0, num):
            item_img = await ten(uid, gacha_data, sd)
            img.paste(item_img, (0, 575 * i))
    draw = ImageDraw.Draw(img)
    draw.text((27,575 * num - 30),('@%s %s  Created By 惜月の小派蒙' % (str(sd['nickname']),time_str)), font=timefont, fill="#8E8E8E")
    return pil2b64(img, 75)

