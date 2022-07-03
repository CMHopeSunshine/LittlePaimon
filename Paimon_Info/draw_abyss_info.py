import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from littlepaimon_utils import aiorequests
from littlepaimon_utils.files import load_image

from ..utils.message_util import MessageBuild

res_path = Path() / 'resources' / 'LittlePaimon'


def get_font(size, font='msyh.ttc'):
    return ImageFont.truetype(str(res_path / font), size)


def get_open_time(timeStamp1, timeStamp2):
    dateArray1 = datetime.datetime.utcfromtimestamp(timeStamp1) + datetime.timedelta(days=1)
    dateArray2 = datetime.datetime.utcfromtimestamp(timeStamp2) + datetime.timedelta(days=1)
    year = dateArray1.strftime("%Y.")
    otherStyleTime1 = dateArray1.strftime("%m.%d")
    otherStyleTime2 = dateArray2.strftime("%m.%d")
    return year + otherStyleTime1 + '-' + otherStyleTime2


def get_chan_time(timeStamp1, timeStamp2):
    dateArray1 = datetime.datetime.utcfromtimestamp(timeStamp1) + datetime.timedelta(hours=8)
    dateArray2 = datetime.datetime.utcfromtimestamp(timeStamp2) + datetime.timedelta(hours=8)
    date = dateArray1.strftime("%Y.%m.%d")
    otherStyleTime1 = dateArray1.strftime("%H:%M:%S")
    otherStyleTime2 = dateArray2.strftime("%H:%M:%S")
    time_consumed = timeStamp2 - timeStamp1
    return f'{date} {otherStyleTime1}-{otherStyleTime2} {str(time_consumed // 60).rjust(2, "0")}分{str(time_consumed % 60).rjust(2, "0")}秒'


async def draw_abyss_floor_card(floor, floor_n):
    floor_img = load_image(res_path / 'abyss' / f'floor{floor_n}_long.png', mode='RGBA')
    floor_draw = ImageDraw.Draw(floor_img)
    floor_draw.text((590, 68), f"{floor['star']}/9", font=get_font(30), fill='white')
    h, h1, h2 = 188.3, 230, 360
    for j in floor['levels']:
        star = load_image(res_path / 'abyss' / 'star.png', mode='RGBA')
        star_w = 500
        for i in range(0, j['star']):
            floor_img.alpha_composite(star, (star_w, h1 + 94))
            star_w += 50
        battles = j['battles']
        if not battles:
            floor_draw.text((183, h + 135), '未有战斗记录', font=get_font(25), fill='white')
        else:
            floor_draw.text((140, h), str(get_chan_time(int(battles[0]['timestamp']), int(battles[1]['timestamp']))),
                            font=get_font(21), fill='white')
            h += 330.3
            w = 37
            for role in battles[0]['avatars']:
                id = role['id']
                level = role['level']
                role_img = load_image(res_path / 'role_card' / f'{id}.png', size=(90, 110), mode='RGBA')
                role_draw = ImageDraw.Draw(role_img)
                role_draw.text((25, 86), f'Lv.{level}', font=get_font(18), fill='black')
                floor_img.alpha_composite(role_img, (w, h1))
                w += 105
            h1 += 330

            w = 37
            for role in battles[1]['avatars']:
                id = role['id']
                level = role['level']
                role_img = load_image(res_path / 'role_card' / f'{id}.png', size=(90, 110), mode='RGBA')
                role_draw = ImageDraw.Draw(role_img)
                role_draw.text((25, 86), f'Lv.{level}', font=get_font(18), fill='black')
                floor_img.alpha_composite(role_img, (w, h2))
                w += 105
            h2 += 330
    return floor_img


async def draw_abyss_card(data, uid, floor_num):
    if not data:
        return '数据出错'
    if data['retcode'] == 10102:
        return f'uid{uid}没有在米游社公开信息哦'
    elif data['retcode'] == 10104:
        return f'uid{uid}有误哦，检查一下吧'
    elif data['retcode'] != 0:
        return f'派蒙获取{uid}数据失败了，可能是以下原因：\n1.达到每日30次查询上限了\n2.绑定的cookie失效了\n3.没有在米游社公开信息\n{data["message"]},{data["retcode"]}'
    data = data['data']
    if not data['defeat_rank']:
        return f'uid{uid}没有深渊数据，请打了8-3之后的层数再来!'
    total_star = '['
    for d in data['floors']:
        if not d['levels']:
            is_all = False
        total_star += str(d['star']) + '-'
    total_star = total_star.strip('-') + ']'
    time = (get_open_time(int(data['start_time']), int(data['end_time'])))
    top_img = load_image(res_path / 'abyss' / 'abyss_total.png', mode='RGBA')
    top_draw = ImageDraw.Draw(top_img)
    top_draw.text((15, 22), f'UID：{uid}', font=get_font(21), fill='white')
    top_draw.text((510, 22), time, font=get_font(21), fill='white')
    top_draw.text((200, 66), data['max_floor'], font=get_font(21), fill='white')
    top_draw.text((390, 66), str(data['total_battle_times']), font=get_font(21), fill='white')
    top_draw.text((490, 66), str(data['total_star']) + total_star, font=get_font(21), fill='white')
    width = 77
    for role in data['reveal_rank']:
        id = role['avatar_id']
        times = role['value']
        role_img = load_image(res_path / 'role_card' / f'{id}.png', size=(90, 110), mode='RGBA')
        role_draw = ImageDraw.Draw(role_img)
        role_draw.text((25, 86), f'{times}次', font=get_font(18), fill='black')
        top_img.alpha_composite(role_img, (width, 165))
        width += 150
    defeat_rank = data['defeat_rank'][0]
    avatar_img = Path() / 'data' / 'LittlePaimon' / 'res' / 'avatar_side' / defeat_rank['avatar_icon'].split('/')[-1]
    defeat_rank_img = await aiorequests.get_img(url=defeat_rank['avatar_icon'], size=(60, 60), mode='RGBA',
                                                save_path=avatar_img)
    top_draw.text((160, 343), str(defeat_rank['value']), font=get_font(21), fill='white')
    top_img.alpha_composite(defeat_rank_img, (280, 320))

    damage_rank = data['damage_rank'][0]
    avatar_img = Path() / 'data' / 'LittlePaimon' / 'res' / 'avatar_side' / damage_rank['avatar_icon'].split('/')[-1]
    damage_rank_img = await aiorequests.get_img(url=damage_rank['avatar_icon'], size=(60, 60), mode='RGBA',
                                                save_path=avatar_img)
    top_draw.text((495, 343), str(damage_rank['value']), font=get_font(21), fill='white')
    top_img.alpha_composite(damage_rank_img, (590, 320))

    take_damage_rank = data['take_damage_rank'][0]
    avatar_img = Path() / 'data' / 'LittlePaimon' / 'res' / 'avatar_side' / take_damage_rank['avatar_icon'].split('/')[
        -1]
    take_damage_rank_img = await aiorequests.get_img(url=take_damage_rank['avatar_icon'], size=(60, 60), mode='RGBA',
                                                     save_path=avatar_img)
    top_draw.text((180, 389), str(take_damage_rank['value']), font=get_font(21), fill='white')
    top_img.alpha_composite(take_damage_rank_img, (280, 365))

    energy_skill_rank = data['energy_skill_rank'][0]
    avatar_img = Path() / 'data' / 'LittlePaimon' / 'res' / 'avatar_side' / energy_skill_rank['avatar_icon'].split('/')[
        -1]
    energy_skill_rank_img = await aiorequests.get_img(url=energy_skill_rank['avatar_icon'], size=(60, 60), mode='RGBA',
                                                      save_path=avatar_img)
    top_draw.text((530, 389), str(energy_skill_rank['value']), font=get_font(21), fill='white')
    top_img.alpha_composite(energy_skill_rank_img, (590, 365))

    normal_skill_rank = data['normal_skill_rank'][0]
    avatar_img = Path() / 'data' / 'LittlePaimon' / 'res' / 'avatar_side' / normal_skill_rank['avatar_icon'].split('/')[
        -1]
    normal_skill_rank_img = await aiorequests.get_img(url=normal_skill_rank['avatar_icon'], size=(60, 60), mode='RGBA',
                                                      save_path=avatar_img)
    top_draw.text((195, 435), str(normal_skill_rank['value']), font=get_font(21), fill='white')
    top_img.alpha_composite(normal_skill_rank_img, (280, 410))

    floor_img_list = []
    for floor_n in floor_num:
        floor = data['floors'][floor_n - 9]
        if not floor['levels']:
            break
        floor_img = await draw_abyss_floor_card(floor, floor_n)
        floor_img_list.append(floor_img)
    floor_img_num = len(floor_img_list)
    total_img = Image.new("RGBA", (700, 5 + 524 + 5 + floor_img_num * 1210), (255, 255, 255, 255))
    total_img.alpha_composite(top_img, (5, 5))
    h = 0
    for floor_img in floor_img_list:
        total_img.alpha_composite(floor_img, (5, 5 + 524 + 5 + h))
        h += 1210

    return MessageBuild.Image(total_img, quality=75, mode='RGB')
