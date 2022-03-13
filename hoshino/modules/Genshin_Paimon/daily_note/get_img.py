import random
import datetime
from io import BytesIO
import os
from PIL import Image, ImageDraw, ImageFont
from hoshino import aiorequests
from ..util import pil2b64
from hoshino.typing import MessageSegment

res_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'res')

def get_font(size):
    return ImageFont.truetype(os.path.join(res_path,'msyhbd.ttc'), size)

def get_odd_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return "剩余%02d时%02d分%02d秒" % (h, m, s)

async def get_avater_pic(avater_url):
    res = await (await aiorequests.get(avater_url)).content
    avater = Image.open(BytesIO(res)).convert("RGBA").resize((60, 60))
    return avater

bg_card_color = {'1':'#C3B8A4','2':'#C3B8A4','3':'#4C74A7','4':'#D7B599'}

async def draw_daily_note_card(data, uid):
    if not data:
        return '数据出错'
    if data['retcode'] == 10102:
        return '这uid没有在米游社公开信息哦,请到 个人主页-管理 中打开'
    elif data['retcode'] == 10104:
        return 'uid有误哦，检查一下或再手动输入一次uid吧'
    elif data['retcode'] != 0:
        return f'派蒙获取数据失败了，获取状态：\n{data["message"]},{data["retcode"]}'
    data = data['data']
    # 载入所需素材图标
    bg_color = random.choice(list(bg_card_color.items()))
    bg_img = Image.open(os.path.join(res_path, 'daily_note', f'便签背景{bg_color[0]}.png')).convert("RGBA")
    enemy = Image.open(os.path.join(res_path, 'daily_note', '周本.png')).convert("RGBA")
    task = Image.open(os.path.join(res_path, 'daily_note', '委托.png')).convert("RGBA")
    power = Image.open(os.path.join(res_path, 'daily_note', '树脂.png')).convert("RGBA")
    money = Image.open(os.path.join(res_path, 'daily_note', '洞天宝钱.png')).convert("RGBA")
    send_icon = Image.open(os.path.join(res_path, 'daily_note', '派遣背景.png')).convert("RGBA").resize((110,55))
    send_finish_icon = Image.open(os.path.join(res_path, 'daily_note', '派遣完成.png')).convert("RGBA").resize((55,55))
    abyss = Image.open(os.path.join(res_path,'daily_note','深渊.png')).convert('RGBA').resize((160,160))
    bg_draw = ImageDraw.Draw(bg_img)

    bg_draw.text((23, 20), '实时便笺', font=get_font(30), fill='white')
    bg_draw.text((255, 20), 'UID：' + uid, font=get_font(30), fill='white')
    # 树脂
    bg_img.alpha_composite(power, (120, 150))
    bg_draw.text((170, 145), f'{data["current_resin"]}/160', font=get_font(30), fill=bg_color[1])
    if data["current_resin"] == 160:
        bg_draw.text((310, 144), '已回满', font=get_font(30), fill=bg_color[1])
    else:
        recover_time = datetime.datetime.now() + datetime.timedelta(seconds=int(data['resin_recovery_time']))
        # recover_time_day = recover_time.day > datetime.datetime.now().day and '明天' or '今天'
        recover_time_day = '今天' if recover_time.day == datetime.datetime.now().day else '明天'
        recover_time_str = f'将于{recover_time_day}{recover_time.strftime("%H:%M")}回满'
        bg_draw.text((320, 147), recover_time_str, font=get_font(25), fill=bg_color[1])
    # 洞天宝钱
    bg_img.alpha_composite(money, (120, 220))
    bg_draw.text((170, 220), f'{data["current_home_coin"]}/2400', font=get_font(30), fill=bg_color[1])
    if data["current_home_coin"] == 2400:
        bg_draw.text((350, 219), '已存满', font=get_font(30), fill=bg_color[1])
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
        # recover_time_str = f'将于{recover_time.strftime("%d日%H:%M")}攒满'
        bg_draw.text((360, 222), recover_time_str, font=get_font(25), fill=bg_color[1])
    # 委托
    bg_img.alpha_composite(task, (120, 296))
    bg_draw.text((170, 296), f'{data["finished_task_num"]}/4', font=get_font(30), fill=bg_color[1])
    if data["finished_task_num"] == 4:
        bg_draw.text((313, 294), '已完成', font=get_font(30), fill=bg_color[1])
    else:
        bg_draw.text((258, 297), '委托还没打完哦！', font=get_font(25), fill=bg_color[1])
    # 周本
    bg_img.alpha_composite(enemy, (120, 370))
    bg_draw.text((170, 370), f'{data["remain_resin_discount_num"]}/3', font=get_font(30), fill=bg_color[1])
    if data["remain_resin_discount_num"] == 0:
        bg_draw.text((313, 369), '已完成', font=get_font(30), fill=bg_color[1])
    else:
        bg_draw.text((258, 371), '周本还没打完哦！', font=get_font(25), fill=bg_color[1])
    # 深渊
    abyss_new_month = datetime.datetime.now().month if datetime.datetime.now().day < 16 else datetime.datetime.now().month + 1
    abyss_new_day = 16 if datetime.datetime.now().day < 16 else 1
    abyss_new = datetime.datetime.strptime('2022.' + str(abyss_new_month) + '.' + str(abyss_new_day) + '.04:00',
                                           '%Y.%m.%d.%H:%M') - datetime.datetime.now()
    abyss_new_str = f'{abyss_new.days+1}天后刷新' if abyss_new.days <= 8 else '已刷新'
    bg_img.alpha_composite(abyss,(500,264))
    bg_draw.text((548, 300), '深渊', font=get_font(30), fill=bg_color[1])
    if abyss_new_str == '已刷新':
        bg_draw.text((541, 350), abyss_new_str, font=get_font(25), fill=bg_color[1])
    else:
        bg_draw.text((520, 350), abyss_new_str, font=get_font(25), fill=bg_color[1])
    # 派遣
    h = 430
    if not data['expeditions']:
        bg_draw.text((300, h + 140), '没有派遣信息', font=get_font(30), fill=bg_color[1])
    else:
        for send in data['expeditions']:
            send_avatar = await get_avater_pic(send['avatar_side_icon'])
            send_status = '派遣已完成！' if send['status'] == 'Finished' else get_odd_time(send['remained_time'])
            bg_draw.rectangle((145, h, 645, h+55), fill=None, outline=bg_color[1], width=3)
            if send['status'] == 'Finished':
                bg_img.alpha_composite(send_finish_icon, (590, h))
            bg_img.alpha_composite(send_icon, (150, h))
            bg_img.alpha_composite(send_avatar, (150, h-10))
            if send_status == '派遣已完成！':
                bg_draw.text((329, h+10), send_status, font=get_font(25), fill=bg_color[1])
            else:
                bg_draw.text((300, h+10), send_status, font=get_font(25), fill=bg_color[1])
            h += 57
        last_finish_second = int(max([s['remained_time'] for s in data['expeditions']]))
        if last_finish_second != 0:
            last_finish_time = datetime.datetime.now() + datetime.timedelta(seconds=last_finish_second)
            last_finish_day = last_finish_time.day > datetime.datetime.now().day and '明天' or '今天'
            last_finish_str = f'将于{last_finish_day}{last_finish_time.strftime("%H:%M")}完成全部派遣'
            bg_draw.text((211, h + 3.5), last_finish_str, font=get_font(30), fill=bg_color[1])
        else:
            bg_draw.text((290, h + 3.5), '派遣已全部完成', font=get_font(30), fill=bg_color[1])
    bg_draw.text((274, 797),'Created by 惜月の小派蒙',font=get_font(20), fill=bg_color[1])

    bg_img = pil2b64(bg_img, 70)
    bg_img = MessageSegment.image(bg_img)
    return bg_img

