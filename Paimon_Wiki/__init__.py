import os
from nonebot import on_endswith, on_command, on_regex
from nonebot.params import RegexDict
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent
from ..utils.character_alias import get_id_by_alias
from ..utils.util import exception_handler
from .blue import get_blue_pic
from .abyss_rate_draw import draw_rate_rank, draw_teams_rate
import re
import time

__usage__ = '''
1.[xx角色攻略]查看西风驿站出品的角色一图流攻略
2.[xx角色材料]查看惜月出品的角色材料统计
3.[xx参考面板]查看blue菌hehe出品的参考面板攻略
4.[xx收益曲线]查看blue菌hehe出品的收益曲线攻略
*感谢来自大佬们的授权。角色支持别名查询
5.[今日/明日/周x材料]查看每日角色天赋材料和武器突破材料表
6.[深渊登场率]查看2.6深渊角色登场率
7.[深渊上半/下半阵容出场率]查看2.6深渊阵容出场率
'''
__help_version__ = '1.0.2'


res_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'res')

guide = on_endswith('角色攻略', priority=8)
material = on_endswith('角色材料', priority=6, block=True)
attribute = on_endswith('参考面板', priority=6, block=True)
attribute2 = on_endswith('收益曲线', priority=6, block=True)
daily_material = on_endswith(('材料', '天赋材料', '突破材料'), priority=6, block=True)
abyss_rate = on_command('syrate', aliases={'深渊登场率', '深境螺旋登场率', '深渊登场率排行', '深渊排行'}, priority=6, block=True)
abyss_team = on_regex(r'^(深渊|深境螺旋)(?P<floor>上半|下半)阵容(排行|出场率)?$', priority=5, block=True)
weapon_guide = on_endswith('武器攻略', priority=6, block=True)


@guide.handle()
@exception_handler()
async def genshin_guide(event: MessageEvent):
    name: str = event.message.extract_plain_text().replace('角色攻略', '').strip()
    realname = get_id_by_alias(name)
    if name in ['风主', '岩主', '雷主'] or realname:
        name = realname[1][0] if name not in ['风主', '岩主', '雷主'] else name
        img = MessageSegment.image(file=f'https://static.cherishmoon.fun/LittlePaimon/XFGuide/{name}.jpg')
        await guide.finish(img)
    else:
        await guide.finish(f'没有找到{name}的攻略', at_sender=True)


@material.handle()
@exception_handler()
async def genshin_material(event: MessageEvent):
    name: str = event.message.extract_plain_text().replace('角色材料', '').strip()
    realname = get_id_by_alias(name)
    if name in ['夜兰', '久岐忍'] or realname:
        name = realname[1][0] if realname else name
        print(name)
        img = MessageSegment.image(
            file=f'https://static.cherishmoon.fun/LittlePaimon/RoleMaterials/{name}材料.jpg')
        await material.finish(img)
    else:
        await material.finish(f'没有找到{name}的材料', at_sender=True)


@attribute.handle()
@exception_handler()
async def genshinAttribute(event: MessageEvent):
    name: str = event.message.extract_plain_text().replace('参考面板', '').strip()
    realname = get_id_by_alias(name)
    if name in ['风主', '岩主', '雷主'] or realname:
        name = realname[1][0] if name not in ['风主', '岩主', '雷主'] else name
        img = await get_blue_pic(name)
        await attribute.finish(MessageSegment.image(file=img))
    else:
        await attribute.finish(f'没有找到{name}的参考面板', at_sender=True)


@attribute2.handle()
@exception_handler()
async def genshinAttribute2(event: MessageEvent):
    name: str = event.message.extract_plain_text().replace('收益曲线', '').strip()
    realname = get_id_by_alias(name)
    if name in ['风主', '岩主', '雷主'] or realname:
        name = realname[1][0] if name not in ['风主', '岩主', '雷主'] else name
        img = MessageSegment.image(file=f'https://static.cherishmoon.fun/LittlePaimon/blue/{name}.jpg')
        await attribute2.finish(img)
    else:
        await attribute2.finish(f'没有找到{name}的收益曲线', at_sender=True)


@daily_material.handle()
@exception_handler()
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
                img = MessageSegment.image(file='https://static.cherishmoon.fun/LittlePaimon'
                                                '/DailyMaterials/周一周四.jpg')
            elif week in ['2', '5']:
                img = MessageSegment.image(file='https://static.cherishmoon.fun/LittlePaimon'
                                                '/DailyMaterials/周二周五.jpg')
            else:
                img = MessageSegment.image(file='https://static.cherishmoon.fun/LittlePaimon'
                                                '/DailyMaterials/周三周六.jpg')
            await daily_material.finish(img)


@abyss_rate.handle()
@exception_handler()
async def abyss_rate_handler(event: MessageEvent):
    abyss_img = await draw_rate_rank()
    await abyss_rate.finish(abyss_img)


@abyss_team.handle()
@exception_handler()
async def abyss_team_handler(event: MessageEvent, reGroup=RegexDict()):
    abyss_img = await draw_teams_rate(reGroup['floor'])
    await abyss_team.finish(abyss_img)


@weapon_guide.handle()
@exception_handler()
async def weapon_guide_handler(event: MessageEvent):
    name: str = event.message.extract_plain_text().replace('武器攻略', '').strip()
    await weapon_guide.finish(MessageSegment.image(file=f'https://static.cherishmoon.fun/LittlePaimon/WeaponGuild/{name}.png'))
