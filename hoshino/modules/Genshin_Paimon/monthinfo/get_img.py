import random
from PIL import Image, ImageDraw, ImageFont
import os
import matplotlib.pyplot as plt
from io import BytesIO
from ..util import pil2b64
from hoshino.typing import MessageSegment

res_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'res')

def get_font(size):
    return ImageFont.truetype(os.path.join(res_path,'msyh.ttc'), size)

def get_font_bd(size):
    return ImageFont.truetype(os.path.join(res_path,'msyhbd.ttc'), size)

async def get_box(t, num):
    box = Image.open(os.path.join(res_path, 'monthinfo', 'box.png')).convert('RGBA')
    img = Image.open(os.path.join(res_path, 'monthinfo', f'{t}.png')).convert('RGBA')
    box.alpha_composite(img, (11, 11))
    box_draw = ImageDraw.Draw(box)
    box_draw.text((83, 18), f'{t}：', font=get_font(25), fill='black')
    if t == '原石':
        box_draw.text((152, 18), f'{num}|{int(num / 160)}抽', font=get_font(25), fill='#9E8E7B')
    else:
        box_draw.text((152, 18), f'{num}', font=get_font(25), fill='#9E8E7B')
    return box

async def draw_circle(per, colors):
    plt.pie(per, startangle=90, colors=colors)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(per,
           wedgeprops={'width': 0.29},
           startangle=90,
           colors=colors)

    buffer = BytesIO()
    canvas = plt.get_current_fig_manager().canvas
    canvas.draw()
    pil_image = Image.frombytes('RGB', canvas.get_width_height(),
                                canvas.tostring_rgb())
    pil_image.save(buffer, 'PNG')
    plt.close()
    pil_image = pil_image.convert('RGBA')
    w, h = pil_image.size
    array = pil_image.load()
    for i in range(w):
        for j in range(h):
            pos = array[i, j]
            isEdit = (sum([1 for x in pos[0:3] if x > 240]) == 3)
            if isEdit:
                array[i, j] = (255, 255, 255, 0)
    return pil_image.resize((378, 378))

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
    bg_img = Image.open(os.path.join(res_path, 'monthinfo', 'bg.png')).convert('RGBA')
    bg_draw = ImageDraw.Draw(bg_img)
    line = Image.open(os.path.join(res_path, 'monthinfo', 'line.png')).convert('RGBA')
    # 顶标题
    bg_draw.text((60, 42), f'旅行者{data["data_month"]}月札记', font=get_font_bd(30), fill='#27384C')
    bg_draw.text((300, 52), f'{data["nickname"]} {data["uid"]}', font=get_font(21), fill='#27384C')
    bg_img.alpha_composite(line, (64, 95))
    # 月获取
    bg_draw.text((60, 110), '当月共获取：', font=get_font_bd(25), fill='#27384C')
    bg_img.alpha_composite(await get_box('原石', data['month_data']['current_primogems']), (40, 150))
    bg_img.alpha_composite(await get_box('摩拉', data['month_data']['current_mora']), (40, 210))
    # 日获取
    bg_draw.text((60, 288), '今日已获取：', font=get_font_bd(25), fill='#27384C')
    bg_img.alpha_composite(await get_box('原石', data['day_data']['current_primogems']), (40, 328))
    bg_img.alpha_composite(await get_box('摩拉', data['day_data']['current_mora']), (40, 388))
    # 表情
    emoticons_list = ['丽莎-干得漂亮', '九条裟罗-开心', '五郎-开心', '优菈-赞扬', '刻晴-点赞', '可莉-好耶', '宵宫-得意', '枫原万叶-偷笑', '派蒙-出货吧', '温迪-期待',
                      '珊瑚宫心海-祈祷', '琴-赞扬', '神里绫华-偷笑', '胡桃-爱心', '荒泷一斗-大笑', '钟离-我全都要', '雷电将军-轻笑']
    emoticon1 = Image.open(os.path.join(res_path, 'emoticons', f'{random.choice(emoticons_list)}.png')).convert('RGBA')
    bg_img.alpha_composite(emoticon1, (360, 140))
    emoticon2 = Image.open(os.path.join(res_path, 'emoticons', f'{random.choice(emoticons_list)}.png')).convert('RGBA')
    bg_img.alpha_composite(emoticon2, (360, 317))

    bg_img.alpha_composite(line, (64, 480))
    # 圆环比例图
    bg_draw.text((60, 495), '原石收入组成：', font=get_font_bd(25), fill='#27384C')
    circle = Image.open(os.path.join(res_path, 'monthinfo', 'circle.png')).convert('RGBA')

    bg_img.alpha_composite(circle, (50, 550))
    color = {'每日活跃': '#BD9A5A', '深境螺旋': '#739970', '活动奖励': '#5A7EA0', '邮件奖励': '#7A6CA7', '冒险奖励': '#D56564',
             '任务奖励': '#70B1B3', '其他': '#73A8C7'}
    per_list = [x['percent'] for x in data['month_data']['group_by']]
    name_list = [x['action'] for x in data['month_data']['group_by']]
    num_list = [x['num'] for x in data['month_data']['group_by']]
    color_list = [color[x] for x in name_list]
    bg_img.alpha_composite(await draw_circle(per_list, color_list), (-12, 489))
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
    bg_draw.text((165, 900), 'Created by 惜月の小派蒙', font=get_font(21), fill='#27384C')

    bg_img = pil2b64(bg_img, 70)
    bg_img = MessageSegment.image(bg_img)
    return bg_img