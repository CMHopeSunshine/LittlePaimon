import random
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from littlepaimon_utils.files import load_image

from ..utils.message_util import MessageBuild

res_path = Path() / 'resources' / 'LittlePaimon'


def get_font(size, font='msyh.ttc'):
    return ImageFont.truetype(str(res_path / font), size)


async def get_box(t, num):
    box = load_image(res_path / 'monthinfo' / 'box.png', mode='RGBA')
    img = load_image(res_path / 'monthinfo' / f'{t}.png', mode='RGBA')
    box.alpha_composite(img, (11, 11))
    box_draw = ImageDraw.Draw(box)
    box_draw.text((83, 18), f'{t}：', font=get_font(25), fill='black')
    if t == '原石':
        box_draw.text((152, 18), f'{num}|{int(num / 160)}抽', font=get_font(25), fill='#9E8E7B')
    else:
        box_draw.text((152, 18), f'{num}', font=get_font(25), fill='#9E8E7B')
    return box


async def draw_ring(per, colors):
    plt.pie(per, startangle=90, colors=colors)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(per,
           wedgeprops={'width': 0.29},
           startangle=90,
           colors=colors)
    bio = BytesIO()
    plt.savefig(bio, transparent=True)
    bio.seek(0)
    img = Image.open(bio).resize((378, 378)).convert('RGBA')
    plt.cla()
    plt.close("all")
    return img


async def draw_monthinfo_card(data):
    if not data:
        return '数据出错'
    if data['retcode'] == 10102:
        return '这uid没有在米游社公开信息哦,请到 个人主页-管理 中打开'
    elif data['retcode'] == 10104:
        return 'uid有误哦，检查一下或再手动输入一次uid吧'
    elif data['retcode'] == -2:
        return '这个月份的信息查不到噢!'
    elif data['retcode'] == -110:
        return '这个uid没有绑定cookie哦!'
    elif data['retcode'] != 0:
        return f'派蒙获取数据失败了，获取状态：\n{data["message"]},{data["retcode"]}'
    data = data['data']
    bg_img = load_image(res_path / 'monthinfo' / 'bg.png', mode='RGBA')
    bg_draw = ImageDraw.Draw(bg_img)
    line = load_image(res_path / 'monthinfo' / 'line.png', mode='RGBA')
    # 顶标题
    bg_draw.text((60, 42), f'旅行者{data["data_month"]}月札记', font=get_font(30, 'msyhbd.ttc'), fill='#27384C')
    bg_draw.text((300, 52), f'{data["nickname"]} {data["uid"]}', font=get_font(21), fill='#27384C')
    bg_img.alpha_composite(line, (64, 95))
    # 月获取
    bg_draw.text((60, 110), '当月共获取：', font=get_font(25, 'msyhbd.ttc'), fill='#27384C')
    bg_img.alpha_composite(await get_box('原石', data['month_data']['current_primogems']), (40, 150))
    bg_img.alpha_composite(await get_box('摩拉', data['month_data']['current_mora']), (40, 210))
    # 日获取
    bg_draw.text((60, 288), '今日已获取：', font=get_font(25, 'msyhbd.ttc'), fill='#27384C')
    bg_img.alpha_composite(await get_box('原石', data['day_data']['current_primogems']), (40, 328))
    bg_img.alpha_composite(await get_box('摩拉', data['day_data']['current_mora']), (40, 388))
    # 表情
    emos = list((res_path / 'emoticons').iterdir())
    emoticon1 = load_image(random.choice(emos), mode='RGBA')
    bg_img.alpha_composite(emoticon1, (360, 140))
    emoticon2 = load_image(random.choice(emos), mode='RGBA')
    bg_img.alpha_composite(emoticon2, (360, 317))

    bg_img.alpha_composite(line, (64, 480))
    # 圆环比例图
    bg_draw.text((60, 495), '原石收入组成：', font=get_font(25, 'msyhbd.ttc'), fill='#27384C')
    circle = load_image(res_path / 'monthinfo' / 'circle.png', mode='RGBA')

    bg_img.alpha_composite(circle, (50, 550))
    color = {'每日活跃': '#BD9A5A', '深境螺旋': '#739970', '活动奖励': '#5A7EA0', '邮件奖励': '#7A6CA7', '冒险奖励': '#D56564',
             '任务奖励': '#70B1B3', '其他': '#73A8C7'}
    per_list = [x['percent'] for x in data['month_data']['group_by']]
    name_list = [x['action'] for x in data['month_data']['group_by']]
    num_list = [x['num'] for x in data['month_data']['group_by']]
    color_list = [color[x] for x in name_list]
    bg_img.alpha_composite(await draw_ring(per_list, color_list), (-12, 489))
    # 百分比描述
    h = 550
    for name in name_list:
        bg_draw.rectangle(((330, h), (340, h + 10)), fill=color[name])
        bg_draw.text((345, h - 6), name, font=get_font(17), fill='#27384C')
        bg_draw.text((430, h - 6), str(num_list[name_list.index(name)]), font=get_font(17), fill='#27384C')
        bg_draw.text((480, h - 6), str(per_list[name_list.index(name)]) + '%', font=get_font(17), fill='#27384C')
        h += 40
    if data['month_data']['primogems_rate'] < 0:
        ysstr = f'少了{-data["month_data"]["primogems_rate"]}%'
    else:
        ysstr = f'多了{data["month_data"]["primogems_rate"]}%'
    if data['month_data']['mora_rate'] < 0:
        mlstr = f'少了{-data["month_data"]["mora_rate"]}%'
    else:
        mlstr = f'多了{data["month_data"]["mora_rate"]}%'
    bg_img.alpha_composite(line, (64, 840))
    bg_draw.text((49, 857), f'本月相比上个月，原石{ysstr}，摩拉{mlstr}', font=get_font(23), fill='#27384C')
    bg_draw.text((167, 900), 'Created by LittlePaimon', font=get_font(21), fill='#27384C')

    return MessageBuild.Image(bg_img, quality=70, mode='RGB')
