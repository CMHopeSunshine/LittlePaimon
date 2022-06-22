import os
import re
import time

from nonebot import on_endswith, on_command, on_regex
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment
from nonebot.params import RegexDict
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata

from utils.alias_handler import get_match_alias
from utils.file_handler import load_json_from_url
from utils.message_util import MessageBuild
from .abyss_rate_draw import draw_rate_rank, draw_teams_rate


__paimon_help__ = {
    'type': '原神Wiki',
    'range': ['private', 'group', 'guild']
}

__plugin_meta__ = PluginMetadata(
    name="Paimon_Wiki",
    description="小派蒙的wiki查询模块",
    usage=(
        "1.[xx角色攻略]查看西风驿站出品的角色一图流攻略\n"
        "2.[xx角色材料]查看惜月出品的角色材料统计\n"
        "3.[xx参考面板]查看blue菌hehe出品的参考面板攻略\n"
        "4.[xx收益曲线]查看blue菌hehe出品的收益曲线攻略\n"
        "5.[今日/明日/周x材料]查看每日角色天赋材料和武器突破材料表\n"
        "6.[深渊登场率]查看2.6深渊角色登场率\n"
        "7.[深渊上半/下半阵容出场率]查看2.6深渊阵容出场率\n"
        "8.[xx武器攻略]查看武器攻略\n"
        "9.[xx原魔图鉴]查看原魔图鉴\n"
    ),
    extra={
        'type': '原神Wiki',
        'range': ['private', 'group', 'guild'],
        "author": "惜月 <277073121@qq.com>",
        "version": "0.1.3",
    },
)


res_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'res')

guide = on_endswith('角色攻略', priority=8)
material = on_endswith('角色材料', priority=6, block=True)
attribute = on_endswith('参考面板', priority=6, block=True)
attribute2 = on_endswith('收益曲线', priority=6, block=True)
daily_material = on_endswith(('材料', '天赋材料', '突破材料'), priority=6, block=True)
abyss_rate = on_command('syrate', aliases={'深渊登场率', '深境螺旋登场率', '深渊登场率排行', '深渊排行'}, priority=6, block=True)
abyss_team = on_regex(r'^(深渊|深境螺旋)(?P<floor>上半|下半)阵容(排行|出场率)?$', priority=5, block=True)
weapon_guide = on_endswith('武器攻略', priority=6, block=True)
monster_map = on_endswith('原魔图鉴', priority=6, block=True)


@attribute.handle()
async def genshinAttribute(event: MessageEvent):
    name = event.message.extract_plain_text().replace('参考面板', '').strip()
    realname = get_match_alias(name)
    if realname:
        blue = await load_json_from_url('https://static.cherishmoon.fun/LittlePaimon/blue/blue.json')
        if realname in blue.keys():
            img = await MessageBuild.StaticImage(url=f'LittlePaimon/blue/{blue[realname][0]}.jpg',
                                                 crop=(0, int(blue[realname][1][0]), 1080, int(blue[realname][1][1])))
        else:
            img = MessageBuild.Text(f'没有找到{name}的参考面板')
        await attribute.finish(img)
    else:
        await attribute.finish(MessageBuild.Text(f'没有找到{name}的参考面板'), at_sender=True)


@daily_material.handle()
async def daily_material_handle(event: MessageEvent):
    week = event.message.extract_plain_text().replace('材料', '').replace('天赋材料', '').replace('突破材料', '').strip()
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
                url = 'LittlePaimon/DailyMaterials/周一周四.jpg'
            elif week in ['2', '5']:
                url = 'LittlePaimon/DailyMaterials/周二周五.jpg'
            else:
                url = 'LittlePaimon/DailyMaterials/周三周六.jpg'
            await daily_material.finish(await MessageBuild.StaticImage(url=url))


@abyss_rate.handle()
async def abyss_rate_handler(event: MessageEvent):
    abyss_img = await draw_rate_rank()
    await abyss_rate.finish(abyss_img)


@abyss_team.handle()
async def abyss_team_handler(event: MessageEvent, reGroup=RegexDict()):
    abyss_img = await draw_teams_rate(reGroup['floor'])
    await abyss_team.finish(abyss_img)


def create_choice_command(endswith: str, type_: str, url: str, tips: str = None, help_tips: str = None):
    command = on_endswith(endswith, priority=6, block=True)
    command.plugin_name = 'Paimon_Wiki'
    command.__paimon_help__ = {
        "usage":  f'<{help_tips}名> ' + endswith,
        "introduce": f"查看该{help_tips}的{endswith}",
        "priority": 3
    }

    @command.handle()
    async def _(event: MessageEvent, state: T_State):
        name = event.message.extract_plain_text().replace(endswith, '').strip()
        if name:
            state['name'] = name

    @command.got('name', prompt=f'请把要查询的{help_tips}告诉我哦~')
    async def _(event: MessageEvent, state: T_State):
        name = state['name']
        if isinstance(name, Message):
            name = name.extract_plain_text().strip()
            if name == 'q':
                await command.finish()
        match_alias = get_match_alias(name, type_)
        if isinstance(match_alias, str):
            await command.finish(
                await MessageBuild.StaticImage(url=url.format(match_alias), tips=tips.format(match_alias)))
        elif isinstance(match_alias, list) and len(match_alias) == 1:
            await command.finish(
                await MessageBuild.StaticImage(url=url.format(match_alias[0]), tips=tips.format(match_alias[0])))
        else:
            if not match_alias:
                await command.finish(MessageBuild.Text(f'没有{state["name"]}的{endswith}哦~'), at_sender=True)
            else:
                if isinstance(match_alias, dict):
                    match_alias = list(match_alias.keys())
                if 'choice' not in state:
                    msg = f'你要找的{endswith[0:2]}是哪个呀：\n'
                    msg += '\n'.join([f'{int(i) + 1}. {name}' for i, name in enumerate(match_alias)])
                    await command.send(msg + '\n回答\"q\"可以取消查询', at_sender=True)
                state['match_alias'] = match_alias

    @command.got('choice')
    async def _(event: MessageEvent, state: T_State):
        match_alias = state['match_alias']
        choice = state['choice']
        choice = choice.extract_plain_text().strip().replace(endswith, '')
        if choice == 'q':
            await command.finish()
        if choice.isdigit() and (1 <= int(choice) <= len(match_alias)):
            await command.finish(
                await MessageBuild.StaticImage(url=url.format(match_alias[int(choice) - 1]),
                                               tips=tips.format(match_alias[int(choice) - 1])))
        if choice not in match_alias:
            state['times'] = state['times'] + 1 if 'times' in state else 1
            if state['times'] == 1:
                await command.reject(f'请旅行者从上面的{endswith[0:2]}中选一个问派蒙\n回答\"q\"可以取消查询', at_sender=True)
            elif state['times'] == 2:
                await command.reject(f'别调戏派蒙啦，快选一个吧，不想问了请回答\"q\"！', at_sender=True)
            elif state['times'] >= 3:
                await command.finish(f'看来旅行者您有点神志不清哦(，下次再问派蒙吧' + MessageSegment.face(146), at_sender=True)
        await command.finish(await MessageBuild.StaticImage(url=url.format(choice), tips=tips.format(choice)))


create_choice_command('原魔图鉴', 'monsters', 'LittlePaimon/MonsterMaps/{}.jpg', '暂时没有{}的原魔图鉴哦~', '原魔')
create_choice_command('武器攻略', 'weapons', 'LittlePaimon/WeaponGuild/{}.png', '暂时没有{}的武器攻略哦~', '武器')
create_choice_command('角色攻略', 'roles', 'LittlePaimon/XFGuide/{}.jpg', '暂时没有{}的角色攻略哦~', '角色')
create_choice_command('角色材料', 'roles', 'LittlePaimon/RoleMaterials/{}材料.jpg', '暂时没有{}的角色材料哦~', '角色')
create_choice_command('收益曲线', 'roles', 'LittlePaimon/blue/{}.jpg', '暂时没有{}的收益曲线哦~', '角色')
