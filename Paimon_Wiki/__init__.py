import os
from PIL import Image
from pathlib import Path
from nonebot import on_endswith
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent
from ..utils.character_alias import get_id_by_alias
from .blue import get_blue_pic
from ..utils.util import pil2b64
import re
import time

__usage__ = '''
1.[xx角色攻略]查看西风驿站出品的角色一图流攻略
2.[xx角色材料]查看惜月出品的角色材料统计
3.[xx参考面板]查看blue菌hehe出品的参考面板攻略
4.[xx收益曲线]查看blue菌hehe出品的收益曲线攻略
*感谢来自大佬们的授权。角色支持别名查询
5.[今日/明日/周x材料]查看每日角色天赋材料和武器突破材料表
'''
__help_version__ = '1.0.2'


res_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'res')

guide = on_endswith('角色攻略', priority=8)
material = on_endswith('角色材料', priority=6, block=True)
attribute = on_endswith('参考面板', priority=6, block=True)
attribute2 = on_endswith('收益曲线', priority=6, block=True)
daily_material = on_endswith(('材料', '天赋材料', '突破材料'), priority=6, block=True)


@guide.handle()
async def genshin_guide(event: MessageEvent):
    name: str = event.message.extract_plain_text().replace('角色攻略', '').strip()
    realname = get_id_by_alias(name)
    if not realname:
        await guide.finish(f'没有找到{name}的攻略', at_sender=True)
    elif realname[1][0] in ['八重神子', '神里绫华', '神里绫人', '温迪', '七七', '雷电将军']:
        path = os.path.join(res_path, 'role_guide', f'{realname[1][0]}.png')
        img = MessageSegment.image(file=Path(path))
        await guide.finish(img, at_sender=True)
    else:
        img = MessageSegment.image(file=f'https://adachi-bot.oss-cn-beijing.aliyuncs.com/Version2/guide/{realname[1][0]}.png')
        await guide.finish(img, at_sender=True)


@material.handle()
async def genshin_material(event: MessageEvent):
    name: str = event.message.extract_plain_text().replace('角色材料', '').strip()
    realname = get_id_by_alias(name)
    if name in ['夜兰', '久岐忍']:
        path = os.path.join(res_path, "role_material", f"{name}材料.png")
        img = MessageSegment.image(file=Path(path))
        await material.finish(img, at_sender=True)
    elif not realname:
        await material.finish(f'没有找到{name}的材料', at_sender=True)
    else:
        path = os.path.join(res_path, 'role_material', f'{realname[1][0]}材料.png')
        img = MessageSegment.image(file=Path(path))
        await material.finish(img, at_sender=True)


@attribute.handle()
async def genshinAttribute(event: MessageEvent):
    name: str = event.message.extract_plain_text().replace('参考面板', '').strip()
    if name not in ['风主', '岩主', '雷主']:
        realname = get_id_by_alias(name)
        if not realname:
            await attribute.finish(f'没有找到{name}的参考面板', at_sender=True)
            return
        realname = realname[1][0]
    else:
        realname = name
    pic_data = get_blue_pic(realname)
    pic = Image.open(os.path.join(res_path, 'blue', f'{pic_data[0]}.jpg'))
    pic = pic.crop((0, pic_data[1][0], 1080, pic_data[1][1]))
    pic = pil2b64(pic, 85)
    await attribute.finish(MessageSegment.image(pic), at_sender=True)


@attribute2.handle()
async def genshinAttribute2(event: MessageEvent):
    name: str = event.message.extract_plain_text().replace('收益曲线', '').strip()
    if name not in ['风主', '岩主', '雷主']:
        realname = get_id_by_alias(name)
        if not realname:
            await attribute2.finish(f'没有找到{name}的参考面板', at_sender=True)
        realname = realname[1][0]
    else:
        realname = name
    pic = Image.open(os.path.join(res_path, 'blue', f'{realname}.png'))
    pic = pil2b64(pic, 85)
    await attribute2.finish(MessageSegment.image(pic), at_sender=True)


@daily_material.handle()
async def daily_material_handle(event: MessageEvent):
    week: str = event.message.extract_plain_text().replace('材料', '').replace('天赋材料', '').replace('突破材料', '').strip()
    if week:
        find_week = re.search(r'(?P<week>今日|今天|现在|明天|明日|后天|后日|周一|周二|周三|周四|周五|周六|周日)', week)
        if find_week:
            if find_week.group('week') in ['今日', '今天', '现在']:
                week = time.strftime("%w")
            elif find_week.group('week') in ['明日', '明天']:
                week = str(int(time.strftime("%w")) + 1)
            elif find_week.group('week') in ['后日', '后天']:
                week = str(int(time.strftime("%w")) + 2)
            elif find_week.group('week') in ['周一', '周四']:
                week = '1'
            elif find_week.group('week') in ['周二', '周五']:
                week = '2'
            elif find_week.group('week') in ['周三', '周六']:
                week = '3'
            else:
                week = '0'
            if week == "0":
                await daily_material.finish('周日所有材料都可以刷哦!', at_sender=True)
            elif week in ['1', '4']:
                path = os.path.join(res_path, "daily_material", "周一周四.jpg")
            elif week in ['2', '5']:
                path = os.path.join(res_path, "daily_material", "周二周五.jpg")
            else:
                path = os.path.join(res_path, "daily_material", "周三周六.jpg")
            await daily_material.finish(MessageSegment.image(file=Path(path)), at_sender=True)
