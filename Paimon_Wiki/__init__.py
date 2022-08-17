import time

from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment
from nonebot.adapters.onebot.v11.helpers import is_cancellation
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.params import RegexDict, ArgPlainText
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from ..utils.message_util import MessageBuild
from ..utils.alias_handler import get_match_alias
from .abyss_rate_draw import draw_rate_rank, draw_teams_rate

__paimon_help__ = {
    'type': '原神Wiki',
    'range': ['private', 'group', 'guild']
}

__plugin_meta__ = PluginMetadata(
    name='Paimon_Wiki',
    description='原神WIKI百科',
    usage="""
        "1.[xx角色攻略]查看西风驿站出品的角色一图流攻略\n"
        "2.[xx角色材料]查看惜月出品的角色材料统计\n"
        "3.[xx参考面板]查看blue菌hehe出品的参考面板攻略\n"
        "4.[xx收益曲线]查看blue菌hehe出品的收益曲线攻略\n"
        "5.[今日/明日/周x材料]查看每日角色天赋材料和武器突破材料表\n"
        "6.[深渊登场率]查看2.6深渊角色登场率\n"
        "7.[深渊上半/下半阵容出场率]查看2.6深渊阵容出场率\n"
        "8.[xx武器攻略]查看武器攻略\n"
        "9.[xx原魔图鉴]查看原魔图鉴\n"
    """,
    extra={
        'type': '原神Wiki',
        'range': ['private', 'group', 'guild'],
        "author": "惜月 <277073121@qq.com>",
        "version": "0.1.3",
    },
)

daily_material = on_regex(r'(?P<week>今日|今天|现在|明天|明日|后天|后日|周一|周二|周三|周四|周五|周六|周日)(天赋|角色)?材料', priority=12, block=True)
daily_material.__paimon_help__ = {
        "usage":  '<今日|周x>材料',
        "introduce": "查看可刷取的素材表",
        "priority": 4
    }
abyss_rate = on_command('syrate', aliases={'深渊登场率', '深境螺旋登场率', '深渊登场率排行', '深渊排行'}, priority=6, block=True)
abyss_rate.__paimon_help__ = {
        "usage":  '深渊登场率',
        "introduce": "查看本期深渊的角色登场率",
        "priority": 5
    }
abyss_team = on_regex(r'^(深渊|深境螺旋)(?P<floor>上半|下半)阵容(排行|出场率)?$', priority=5, block=True)
abyss_team.__paimon_help__ = {
    'introduce': '查看本期深渊的阵容出场率排行',
    'usage':       '深渊<上半|下半>阵容排行',
    'priority': 6
}


@daily_material.handle()
async def daily_material_handle(event: MessageEvent, find_week: dict = RegexDict()):
    if find_week['week'] in ['今日', '今天', '现在']:
        week = time.strftime("%w")
    elif find_week['week'] in ['明日', '明天']:
        week = str(int(time.strftime("%w")) + 1)
    elif find_week['week'] in ['后日', '后天']:
        week = str(int(time.strftime("%w")) + 2)
    elif find_week['week'] in ['周一', '周四']:
        week = '1'
    elif find_week['week'] in ['周二', '周五']:
        week = '2'
    elif find_week['week'] in ['周三', '周六']:
        week = '3'
    else:
        week = '0'
    if week == "0":
        await daily_material.finish('周日所有材料都可以刷哦!', at_sender=True)
    elif week in ['1', '4']:
        await daily_material.finish(
            MessageSegment.image(file='https://static.cherishmoon.fun/LittlePaimon/DailyMaterials/周一周四.jpg'))
    elif week in ['2', '5']:
        await daily_material.finish(
            MessageSegment.image(file='https://static.cherishmoon.fun/LittlePaimon/DailyMaterials/周二周五.jpg'))
    else:
        await daily_material.finish(
            MessageSegment.image(file='https://static.cherishmoon.fun/LittlePaimon/DailyMaterials/周三周六.jpg'))


@abyss_rate.handle()
async def abyss_rate_handler(event: MessageEvent):
    abyss_img = await draw_rate_rank()
    await abyss_rate.finish(abyss_img)


@abyss_team.handle()
async def abyss_team_handler(event: MessageEvent, reGroup=RegexDict()):
    abyss_img = await draw_teams_rate(reGroup['floor'])
    await abyss_team.finish(abyss_img)


def create_wiki_matcher(pattern: str, help_fun: str, help_name: str):
    maps = on_regex(pattern, priority=10, block=True)
    maps.plugin_name = 'Paimon_Wiki'
    maps.__paimon_help__ = {'introduce': f"查看该{help_name}的{help_fun}",
                            'usage': f'<{help_name}名> {help_fun}', 'priority': 3}

    @maps.handle()
    async def _(event: MessageEvent, state: T_State, regex_dict: dict = RegexDict()):
        name = regex_dict['name1'] or regex_dict['name2']
        state['type'] = regex_dict['type']
        if '武器' in state['type']:
            state['type'] = '武器'
            state['img_url'] = 'https://static.cherishmoon.fun/LittlePaimon/WeaponMaps/{}.jpg'
        elif '圣遗物' in state['type']:
            state['type'] = '圣遗物'
            state['img_url'] = 'https://static.cherishmoon.fun/LittlePaimon/ArtifactMaps/{}.jpg'
        elif '怪物' in state['type'] or '原魔' in state['type']:
            state['type'] = '原魔'
            state['img_url'] = 'https://static.cherishmoon.fun/LittlePaimon/MonsterMaps/{}.jpg'
        elif state['type'] == '角色攻略':
            state['type'] = '角色'
            state['img_url'] = 'https://static.cherishmoon.fun/LittlePaimon/XFGuide/{}.jpg'
        elif state['type'] == '角色材料':
            state['type'] = '角色'
            state['img_url'] = 'https://static.cherishmoon.fun/LittlePaimon/RoleMaterials/{}材料.jpg'
        elif state['type'] == '收益曲线':
            state['type'] = '角色'
            state['img_url'] = 'https://static.cherishmoon.fun/LittlePaimon/blue/{}.jpg'
        elif state['type'] == '参考面板':
            state['type'] = '角色'
            state['img_url'] = 'https://static.cherishmoon.fun/LittlePaimon/blueRefer/{}.jpg'
        if name:
            state['name'] = name

    @maps.got('name', prompt=Message.template('请提供要查询的{type}'))
    async def _(event: MessageEvent, state: T_State):
        name = state['name']
        if isinstance(name, Message):
            if is_cancellation(name):
                await maps.finish()
            name = name.extract_plain_text().strip()
        match_alias = get_match_alias(name, state['type'])
        true_name = match_alias[0] if (
                isinstance(match_alias, list) and len(match_alias) == 1) else match_alias if isinstance(match_alias,
                                                                                                        str) else None
        if true_name:
            try:
                await maps.finish(MessageSegment.image(state['img_url'].format(match_alias)))
            except ActionFailed:
                await maps.finish(f'暂时没有{true_name}的资源哦')
        elif match_alias:
            if isinstance(match_alias, dict):
                match_alias = list(match_alias.keys())
            if 'choice' not in state:
                msg = f'你要查询的{state["type"]}是：\n'
                msg += '\n'.join([f'{int(i) + 1}. {name}' for i, name in enumerate(match_alias)])
                await maps.send(msg + '\n回答\"取消\"来取消查询', at_sender=True)
            state['match_alias'] = match_alias
        else:
            await maps.finish(MessageBuild.Text(f'没有找到叫{name}的{state["type"]}'))

    @maps.got('choice')
    async def _(event: MessageEvent, state: T_State, choice: str = ArgPlainText('choice')):
        match_alias = state['match_alias']
        if is_cancellation(choice):
            await maps.finish()
        if choice.isdigit() and (1 <= int(choice) <= len(match_alias)):
            try:
                await maps.finish(MessageSegment.image(state['img_url'].format(match_alias[int(choice) - 1])))
            except ActionFailed:
                await maps.finish(f'暂时没有{match_alias[int(choice) - 1]}的资源哦')
        if choice not in match_alias:
            state['times'] = state['times'] + 1 if 'times' in state else 1
            if state['times'] == 1:
                await maps.reject(f'请旅行者从上面的{state["type"]}中选一个问派蒙\n回答\"q\"可以取消查询', at_sender=True)

            elif state['times'] == 2:
                await maps.reject(f'别调戏派蒙啦，快选一个吧，不想问了请回答\"q\"！', at_sender=True)
            elif state['times'] >= 3:
                await maps.finish(f'看来旅行者您有点神志不清哦(，下次再问派蒙吧{MessageSegment.face(146)}', at_sender=True)
        try:
            await maps.finish(MessageSegment.image(state['img_url'].format(choice)))
        except ActionFailed:
            await maps.finish(f'暂时没有{choice}的资源哦')


create_wiki_matcher(r'(?P<name1>\w*)(?P<type>(原魔|怪物)(图鉴|攻略))(?P<name2>\w*)', '原魔图鉴', '原魔')
create_wiki_matcher(r'(?P<name1>\w*)(?P<type>武器(图鉴|攻略))(?P<name2>\w*)', '武器图鉴', '武器')
create_wiki_matcher(r'(?P<name1>\w*)(?P<type>圣遗物(图鉴|攻略))(?P<name2>\w*)', '圣遗物图鉴', '圣遗物')
create_wiki_matcher(r'(?P<name1>\w*)(?P<type>角色攻略)(?P<name2>\w*)', '角色攻略', '角色')
create_wiki_matcher(r'(?P<name1>\w*)(?P<type>角色材料)(?P<name2>\w*)', '角色材料', '角色')
create_wiki_matcher(r'(?P<name1>\w*)(?P<type>收益曲线)(?P<name2>\w*)', '收益曲线', '角色')
create_wiki_matcher(r'(?P<name1>\w*)(?P<type>参考面板)(?P<name2>\w*)', '参考面板', '角色')
