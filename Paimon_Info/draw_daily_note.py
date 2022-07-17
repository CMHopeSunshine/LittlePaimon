import datetime
import random
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from littlepaimon_utils import aiorequests
from littlepaimon_utils.files import load_image

from ..utils.message_util import MessageBuild

res_path = Path() / 'resources' / 'LittlePaimon'


def get_font(size, font='msyhbd.ttc'):
    return ImageFont.truetype(str(res_path / font), size)


async def draw_ring(per):
    if per > 1:
        per = 1
    elif per < 0:
        per = 0
    per_list = [per, 1 - per]
    colors = ['#507bd0', '#FFFFFF']
    plt.pie(per_list, startangle=90, colors=colors)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(per_list,
           wedgeprops={'width': 0.18},
           startangle=90,
           colors=colors)
    bio = BytesIO()
    plt.savefig(bio, transparent=True)
    bio.seek(0)
    img = Image.open(bio).resize((266, 266)).convert('RGBA')
    plt.cla()
    plt.close("all")
    return img


async def draw_daily_note_card(data, uid):
    if not data:
        return '数据出错'
    if data['retcode'] == 10102:
        return f'uid{uid}没有在米游社公开信息哦,请到 个人主页-管理 中打开'
    elif data['retcode'] == 10104:
        return f'uid{uid}有误哦，检查一下或再手动输入一次uid吧'
    elif data['retcode'] != 0:
        return f'派蒙获取{uid}数据失败了，获取状态：\n{data["message"]},{data["retcode"]}'
    data = data['data']
    circle_img = load_image(res_path / 'daily_note' / '透明圆.png')
    finished_icon = load_image(res_path / 'daily_note' / 'finished.png')
    bg_img = load_image(res_path / 'daily_note' / 'ssbq.png', mode='RGBA')

    bg_draw = ImageDraw.Draw(bg_img)
    # uid文字
    bg_draw.text((152, 251), f"uid{uid}", fill='#5680d2', font=get_font(60, 'number.ttf'))
    # 树脂文字
    bg_draw.text((337, 480), f"{data['current_resin']}/160", fill='white', font=get_font(48, 'number.ttf'))
    bg_img.alpha_composite(await draw_ring(data['current_resin'] / 160), (98, 369))
    if data['current_resin'] == 160:
        bg_draw.text((892, 480), f"树脂满了哦~", fill='white', font=get_font(40, '优设标题黑.ttf'))
    else:
        recover_time = datetime.datetime.now() + datetime.timedelta(seconds=int(data['resin_recovery_time']))
        recover_time_day = '今天' if recover_time.day == datetime.datetime.now().day else '明天'
        recover_time_str = f'将于{recover_time_day}{recover_time.strftime("%H:%M")}回满'
        bg_draw.text((780, 480), recover_time_str, fill='white', font=get_font(40, '优设标题黑.ttf'))
    # 宝钱文字
    bg_draw.text((337, 701), f"{data['current_home_coin']}/{data['max_home_coin']}", fill='white',
                 font=get_font(48, 'number.ttf'))
    bg_img.alpha_composite(await draw_ring(data['current_home_coin'] / data['max_home_coin']), (98, 593))
    if data['current_home_coin'] == data['max_home_coin']:
        bg_draw.text((820, 701), f"洞天宝钱满了哦~", fill='white', font=get_font(40, '优设标题黑.ttf'))
    else:
        recover_time = datetime.datetime.now() + datetime.timedelta(seconds=int(data['home_coin_recovery_time']))
        recover_time_day = recover_time.day - datetime.datetime.now().day
        if recover_time_day == 1:
            recover_time_day_str = '明天'
        elif recover_time_day == 0:
            recover_time_day_str = '今天'
        else:
            recover_time_day_str = str(recover_time.day) + '日'
        recover_time_str = f'将于{recover_time_day_str}{recover_time.strftime("%H:%M")}攒满'
        bg_draw.text((762, 701), recover_time_str, fill='white', font=get_font(40, '优设标题黑.ttf'))
    # 委托文字
    bg_draw.text((337, 924), f"{data['finished_task_num']}/4", fill='white', font=get_font(48, 'number.ttf'))
    bg_img.alpha_composite(await draw_ring(data['finished_task_num'] / 4), (98, 816))
    if data['finished_task_num'] == 4:
        bg_draw.text((750, 924), "今日委托已全部完成~", fill='white', font=get_font(40, '优设标题黑.ttf'))
    else:
        bg_draw.text((790, 924), "今日委托完成情况", fill='white', font=get_font(40, '优设标题黑.ttf'))
    # 质变文字
    if data['transformer']['obtained']:
        bg_draw.text((337, 1147), f"{7 - data['transformer']['recovery_time']['Day']}/7", fill='white',
                     font=get_font(48, 'number.ttf'))
        bg_img.alpha_composite(await draw_ring((7 - data['transformer']['recovery_time']['Day']) / 7), (98, 1039))
        rt = data['transformer']['recovery_time']
        if rt['Day'] == 0 and rt['reached']:
            bg_draw.text((465, 1147), "可使用", fill='white', font=get_font(40, '优设标题黑.ttf'))
        elif rt['Day'] == 0 and not rt['reached']:
            bg_draw.text((463, 1127), f"{rt['Hour']}时后", fill='white', font=get_font(40, '优设标题黑.ttf'))
            bg_draw.text((465, 1167), "可使用", fill='white', font=get_font(40, '优设标题黑.ttf'))
        else:
            bg_draw.text((471, 1127), f"{rt['Day']}天后", fill='white',
                         font=get_font(40, '优设标题黑.ttf'))
            bg_draw.text((465, 1167), "可使用", fill='white', font=get_font(40, '优设标题黑.ttf'))
    else:
        bg_draw.text((337, 1143), "未获得", fill='white', font=get_font(48, '优设标题黑.ttf'))
    # 周本文字
    bg_draw.text((843, 1147), f"{3 - data['remain_resin_discount_num']}/3", fill='white',
                 font=get_font(48, 'number.ttf'))
    bg_img.alpha_composite(await draw_ring((3 - data['remain_resin_discount_num']) / 3), (604, 1039))
    if data['remain_resin_discount_num'] == 0:
        bg_draw.text((1005, 1147), "已完成", fill='white', font=get_font(40, '优设标题黑.ttf'))
    else:
        bg_draw.text((977, 1127), f"剩余{data['remain_resin_discount_num']}次", fill='white',
                     font=get_font(40, '优设标题黑.ttf'))
        bg_draw.text((965, 1167), "周本减半", fill='white', font=get_font(40, '优设标题黑.ttf'))
    # 深渊文字
    abyss_new_month = datetime.datetime.now().month if datetime.datetime.now().day < 16 else datetime.datetime.now().month + 1
    abyss_new_day = 16 if datetime.datetime.now().day < 16 else 1
    abyss_new = datetime.datetime.strptime('2022.' + str(abyss_new_month) + '.' + str(abyss_new_day) + '.00:00',
                                           '%Y.%m.%d.%H:%M') - datetime.datetime.now()
    abyss_new_total = datetime.datetime.strptime('2022.' + str(abyss_new_month) + '.' + str(abyss_new_day) + '.00:00',
                                                 '%Y.%m.%d.%H:%M') - datetime.datetime.strptime(
        '2022.' + str(abyss_new_month if abyss_new_month == datetime.datetime.now().month else abyss_new_month - 1) + '.' + str(1 if datetime.datetime.now().day < 16 else 16) + '.00:00',
        '%Y.%m.%d.%H:%M')
    bg_draw.text((337, 1358), f"{abyss_new.days}/{abyss_new_total.days}", fill='white',
                 font=get_font(48, 'number.ttf'))
    bg_draw.text((745, 1358), f"本期深渊还有{abyss_new.days if abyss_new.days <= abyss_new_total.days else abyss_new_total.days}天结束", fill='white',
                 font=get_font(40, '优设标题黑.ttf'))
    bg_img.alpha_composite(await draw_ring(abyss_new.days / abyss_new_total.days), (100, 1249))

    # 派遣情况
    exp = data['expeditions']
    if exp:
        i = 0
        for role in exp:
            role_avatar = Path() / 'data' / 'LittlePaimon' / 'res' / 'avatar_side' / \
                          role['avatar_side_icon'].split('/')[-1]
            role_avatar = await aiorequests.get_img(url=role['avatar_side_icon'], size=(135, 135), mode='RGBA',
                                                    save_path=role_avatar)
            bg_img.alpha_composite(role_avatar, (i * 200 + 168, 1537))
            bg_img.alpha_composite(await draw_ring(1 - int(role['remained_time']) / 72000), (i * 201 + 101, 1490))
            if role['status'] == 'Ongoing':
                bg_img.alpha_composite(circle_img, (i * 201 + 172, 1559))
                hour = int(role['remained_time']) // 3600
                bg_draw.text((i * 200 + 212, 1580), f"{hour}h", fill='white', font=get_font(40, 'number.ttf'))
                minute = int(role['remained_time']) % 3600 // 60
                bg_draw.text((i * 200 + 197, 1620), f"{minute}m", fill='white', font=get_font(40, 'number.ttf'))
            else:
                bg_img.alpha_composite(finished_icon, (i * 200 + 191, 1576))
            i += 1

        bg_draw.text((1220, 1580), "派遣全部", fill="#5680d2", font=get_font(40, '优设标题黑.ttf'))
        bg_draw.text((1220, 1620), "完成时间", fill="#5680d2", font=get_font(40, '优设标题黑.ttf'))
        max_time = int(max([s['remained_time'] for s in exp]))
        if max_time == 0:
            bg_draw.text((1410, 1583), "已全部完成~", fill="#5680d2",
                         font=get_font(60, '优设标题黑.ttf'))
        else:
            last_finish_time = datetime.datetime.now() + datetime.timedelta(seconds=max_time)
            last_finish_day = last_finish_time.day > datetime.datetime.now().day and '明天' or '今天'
            last_finish_str = f'{last_finish_day}{last_finish_time.strftime("%H:%M")}'
            bg_draw.text((1408, 1588), last_finish_str, fill="#5680d2",
                         font=get_font(60, '优设标题黑.ttf'))
    else:
        bg_draw.text((1408, 1588), '未安排派遣', fill="#5680d2",
                     font=get_font(60, '优设标题黑.ttf'))
    role_img = load_image(random.choice(list((res_path / 'emoticons').iterdir())), size=3.5, mode='RGBA')
    bg_img.alpha_composite(role_img, (1220, 200))
    now = datetime.datetime.now().strftime('%m月%d日%H:%M')
    bg_draw.text((554, 1794), 'Created by LittlePaimon·' + now, fill='#5680d2', font=get_font(40, '优设标题黑.ttf'))
    return MessageBuild.Image(bg_img, size=0.35, quality=70, mode='RGB')
