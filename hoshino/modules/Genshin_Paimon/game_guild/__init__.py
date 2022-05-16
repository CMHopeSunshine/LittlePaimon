import hoshino,os
from PIL import Image
from hoshino import R,MessageSegment,aiorequests,logger,Service
from hoshino.typing import CQEvent, Message
from ..character_alias import get_id_by_alias
from .blue import get_blue_pic
from ..util import pil2b64
from hoshino.util import filt_message
import re
import time

help_msg='''
1.[xx角色攻略]查看西风驿站出品的角色一图流攻略
2.[xx角色材料]查看惜月出品的角色材料统计
3.[xx参考面板]查看blue菌hehe出品的参考面板攻略
4.[xx收益曲线]查看blue菌hehe出品的收益曲线攻略
*感谢来自大佬们的授权。角色支持别名查询
5.[今日/明日/周x材料]查看每日角色天赋材料和武器突破材料表
'''
sv = Service('派蒙WIKI', bundle='派蒙', help_=help_msg)


res_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'res')

@sv.on_prefix('角色攻略')
@sv.on_suffix('角色攻略')
async def genshinguide(bot,ev):
    name = ev.message.extract_plain_text().strip()
    realname = get_id_by_alias(name)
    if not realname:
        await bot.send(ev,f'没有找到{filt_message(name)}的攻略',at_sender=True)
    elif realname[1][0] in ['八重神子', '神里绫华', '神里绫人', '温迪', '七七', '雷电将军']:
        path = os.path.join(res_path, 'role_guide',f'{realname[1][0]}.png')
        cq_img = f'[CQ:image,file=file:///{path}]'
        await bot.send(ev,cq_img,at_sender=True)
    else:
        img = f'[CQ:image,file=https://cherishmoon.oss-cn-shenzhen.aliyuncs.com/LittlePaimon/XFGuide/{realname[1][0]}.png]'
        await bot.send(ev,img)

@sv.on_prefix('角色材料')
@sv.on_suffix('角色材料')
async def genshinmaterial(bot,ev):
    name = ev.message.extract_plain_text().strip()
    realname = get_id_by_alias(name)
    if name in ['夜兰', '久岐忍']:
        cq_img = f'[CQ:image,file=file:///{os.path.join(res_path, "role_material",f"{name}材料.png")}]'
        await bot.send(ev,cq_img,at_sender=True)
    elif not realname:
        await bot.send(ev,f'没有找到{filt_message(name)}的材料',at_sender=True)
    else:
        path = os.path.join(res_path, 'role_material',f'{realname[1][0]}材料.png')
        cq_img = f'[CQ:image,file=file:///{path}]'
        await bot.send(ev,cq_img,at_sender=True)

@sv.on_prefix('参考面板')
@sv.on_suffix('参考面板')
async def genshinAttribute(bot,ev):
    name = ev.message.extract_plain_text().strip()
    if name not in ['风主', '岩主', '雷主']:
        realname = get_id_by_alias(name)
        if not realname:
            await bot.send(ev,f'没有找到{filt_message(name)}的参考面板',at_sender=True)
            return
        realname = realname[1][0]
    else:
        realname = name
    pic_data = get_blue_pic(realname)
    pic = Image.open(os.path.join(res_path, 'blue', f'{pic_data[0]}.jpg'))
    pic = pic.crop((0, pic_data[1][0], 1080, pic_data[1][1]))
    pic = pil2b64(pic, 85)
    pic = MessageSegment.image(pic)
    await bot.send(ev,pic,at_sender=True)
        

@sv.on_prefix('收益曲线')
@sv.on_suffix('收益曲线')
async def genshinAttribute2(bot,ev):
    name = ev.message.extract_plain_text().strip()
    if name not in ['风主', '岩主', '雷主']:
        realname = get_id_by_alias(name)
        if not realname:
            await bot.send(ev,f'没有找到{filt_message(name)}的参考面板',at_sender=True)
            return
        realname = realname[1][0]
    else:
        realname = name
    pic = Image.open(os.path.join(res_path, 'blue', f'{realname}.png'))
    pic = pil2b64(pic, 85)
    pic = MessageSegment.image(pic)
    await bot.send(ev,pic,at_sender=True)

@sv.on_suffix(('材料', '天赋材料', '角色天赋材料', '突破材料', '武器突破材料'))
async def daily_material(bot, ev):
    week = ev.message.extract_plain_text().strip()
    if not week:
        return
    find_week = re.search(r'(?P<week>今日|今天|现在|明天|明日|后天|后日|周一|周二|周三|周四|周五|周六|周日)', week)
    if not find_week:
        return
    else:
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
            await bot.send(ev, '周日所有材料都可以刷哦!', at_sender = True)
        elif week in ['1', '4']:
            await bot.send(ev,f'[CQ:image,file=file:///{os.path.join(res_path, "daily_material","周一周四.jpg")}]',at_sender=True)
        elif week in ['2', '5']:
            await bot.send(ev,f'[CQ:image,file=file:///{os.path.join(res_path, "daily_material","周二周五.jpg")}]',at_sender=True)
        else:
            await bot.send(ev,f'[CQ:image,file=file:///{os.path.join(res_path, "daily_material","周三周六.jpg")}]',at_sender=True)
    