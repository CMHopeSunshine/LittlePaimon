import random

from LittlePaimon.utils.image import PMImage, font_manager as fm, load_image
from LittlePaimon.utils.message import MessageBuild
from LittlePaimon.utils.path import RESOURCE_BASE_PATH

RES = RESOURCE_BASE_PATH / 'monthinfo'


async def draw_box(t: str, num: int) -> PMImage:
    img = await load_image(RES / f'{t}.png', mode='RGBA')
    box = PMImage(await load_image(RES / 'box.png', mode='RGBA'))
    await box.paste(img, (11, 11))
    await box.text(f'{t}：', 83, 18, fm.get('hywh', 25), 'black')
    if t == '原石':
        await box.text(f'{num}|{num // 160}抽', 152, 18, fm.get('hywh', 25), '#9E8E7B')
    else:
        await box.text(f'{num}', 152, 18, fm.get('hywh', 25), '#9E8E7B')
    return box


async def draw_monthinfo_card(data: dict):
    img = PMImage(await load_image(RES / 'bg.png', mode='RGBA'))
    line = await load_image(RES / 'line.png', mode='RGBA')
    # 顶标题
    await img.text(f'旅行者{data["data_month"]}月札记', 60, 42, fm.get('msyhbd.ttc', 30), '#27384C')
    await img.text(f'{data["nickname"]} {data["uid"]}', 300, 52, fm.get('msyh.ttc', 25), '#27384C')
    await img.paste(line, (64, 95))
    await img.paste(line, (64, 95))
    # 月获取
    await img.text('当月共获取：', 60, 110, fm.get('msyhbd.ttc', 25), '#27384C')
    await img.paste(await draw_box('原石', data['month_data']['current_primogems']), (40, 150))
    await img.paste(await draw_box('摩拉', data['month_data']['current_mora']), (40, 210))
    # 日获取
    await img.text('今日已获取：', 60, 288, fm.get('msyhbd.ttc', 25), '#27384C')
    await img.paste(await draw_box('原石', data['day_data']['current_primogems']), (40, 328))
    await img.paste(await draw_box('摩拉', data['day_data']['current_mora']), (40, 388))
    # 表情
    emos = list((RESOURCE_BASE_PATH / 'emoticons').iterdir())
    emoticon1 = await load_image(random.choice(emos), mode='RGBA')
    await img.paste(emoticon1, (360, 140))
    emoticon2 = await load_image(random.choice(emos), mode='RGBA')
    await img.paste(emoticon2, (360, 317))

    await img.paste(line, (64, 480))
    # 圆环比例图
    await img.text('原石收入组成：', 60, 495, fm.get('msyhbd.ttc', 25), '#27384C')
    circle = await load_image(RES / 'circle.png', mode='RGBA')

    await img.paste(circle, (50, 550))
    color = {'每日活跃': '#BD9A5A', '深境螺旋': '#739970', '活动奖励': '#5A7EA0', '邮件奖励': '#7A6CA7', '冒险奖励': '#D56564',
             '任务奖励': '#70B1B3', '其他': '#73A8C7'}
    per_list = [x['percent'] for x in data['month_data']['group_by']]
    name_list = [x['action'] for x in data['month_data']['group_by']]
    num_list = [x['num'] for x in data['month_data']['group_by']]
    color_list = [color[x] for x in name_list]
    await img.draw_ring((378, 378), (-12, 489), 0.29, per_list, color_list)
    # 百分比描述
    h = 550
    for name in name_list:
        await img.draw_rectangle((330, h, 340, h + 10), color=color[name])
        await img.text(name, 345, h - 6, fm.get('msyh.ttc', 17), '#27384C')
        await img.text(str(num_list[name_list.index(name)]), 430, h - 6, fm.get('msyh.ttc', 17), '#27384C')
        await img.text(f'{str(per_list[name_list.index(name)])}%', 480, h - 6, fm.get('msyh.ttc', 17), '#27384C')

        h += 40
    if data['month_data']['primogems_rate'] < 0:
        ys_str = f'少了{-data["month_data"]["primogems_rate"]}%'
    else:
        ys_str = f'多了{data["month_data"]["primogems_rate"]}%'
    if data['month_data']['mora_rate'] < 0:
        ml_str = f'少了{-data["month_data"]["mora_rate"]}%'
    else:
        ml_str = f'多了{data["month_data"]["mora_rate"]}%'
    await img.paste(line, (64, 840))
    await img.text(f'本月相比上个月，原石{ys_str}，摩拉{ml_str}', 49, 857, fm.get('msyh.ttc', 23), '#27384C')
    await img.text('Created by LittlePaimon', 167, 900, fm.get('msyh.ttc', 21), '#27384C')

    return MessageBuild.Image(img, quality=80, mode='RGB')
