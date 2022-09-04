import time

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment
from nonebot.adapters.onebot.v11.helpers import is_cancellation
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.params import RegexDict, ArgPlainText
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from LittlePaimon import NICKNAME
from LittlePaimon.utils.alias import get_match_alias
from LittlePaimon.utils.message import MessageBuild
from LittlePaimon.database.models import PlayerAlias
# from .abyss_rate_draw import draw_rate_rank, draw_teams_rate

__paimon_help__ = {
    'type':  '原神Wiki',
    'range': ['private', 'group', 'guild']
}

help_msg = """"1.[xx角色攻略]查看西风驿站出品的角色一图流攻略\n"
"2.[xx角色材料]查看惜月出品的角色材料统计\n"
"3.[xx参考面板]查看blue菌hehe出品的参考面板攻略\n"
"4.[xx收益曲线]查看blue菌hehe出品的收益曲线攻略\n"
"5.[今日/明日/周x材料]查看每日角色天赋材料和武器突破材料表\n"
"6.[xx武器攻略]查看武器攻略\n"
"7.[xx原魔图鉴]查看原魔图鉴\n"
"""

__plugin_meta__ = PluginMetadata(
    name='原神Wiki',
    description='原神WIKI百科',
    usage=help_msg,
    extra={
        'author':   '惜月',
        'version':  '3.0',
        'priority': 3,
    }
)

daily_material = on_regex(r'(?P<day>现在|(今|明|后)(天|日)|周(一|二|三|四|五|六|日))(天赋|角色|武器)?材料', priority=11, block=True, state={
    'pm_name':        '每日材料',
    'pm_description': '查看某日开放材料刷取的角色和武器',
    'pm_usage':       '<今天|周几>材料',
    'pm_priority':    8
})
# abyss_rate = on_command('syrate', aliases={'深渊登场率', '深境螺旋登场率', '深渊登场率排行', '深渊排行'}, priority=11, block=True, state={
#     'pm_name':        '深渊登场率排行',
#     'pm_description': '查看本期深渊的角色登场率排行',
#     'pm_usage':       '深渊登场率',
#     'pm_priority':    9,
# })
# abyss_team = on_regex(r'^(深渊|深境螺旋)(?P<floor>上半|下半)阵容(排行|出场率)?$', priority=11, block=True, state={
#     'pm_name':        '深渊阵容出场率排行',
#     'pm_description': '查看本期深渊的阵容出场率排行',
#     'pm_usage':       '深渊<上半|下半>阵容排行',
#     'pm_priority':    10,
# })


@daily_material.handle()
async def _(event: MessageEvent, regex_dict: dict = RegexDict()):
    if regex_dict['day'] in ['今日', '今天', '现在']:
        day = time.strftime("%w")
    elif regex_dict['day'] in ['明日', '明天']:
        day = str(int(time.strftime("%w")) + 1)
    elif regex_dict['day'] in ['后日', '后天']:
        day = str(int(time.strftime("%w")) + 2)
    elif regex_dict['day'] in ['周一', '周四']:
        day = '1'
    elif regex_dict['day'] in ['周二', '周五']:
        day = '2'
    elif regex_dict['day'] in ['周三', '周六']:
        day = '3'
    else:
        day = '0'
    if day == "0":
        await daily_material.finish('周日所有材料都可以刷哦!', at_sender=True)
    elif day in ['1', '4']:
        await daily_material.finish(
            MessageSegment.image(file='https://static.cherishmoon.fun/LittlePaimon/DailyMaterials/周一周四.jpg'))
    elif day in ['2', '5']:
        await daily_material.finish(
            MessageSegment.image(file='https://static.cherishmoon.fun/LittlePaimon/DailyMaterials/周二周五.jpg'))
    else:
        await daily_material.finish(
            MessageSegment.image(file='https://static.cherishmoon.fun/LittlePaimon/DailyMaterials/周三周六.jpg'))


# @abyss_rate.handle()
# async def abyss_rate_handler(event: MessageEvent):
#     abyss_img = await draw_rate_rank()
#     await abyss_rate.finish(abyss_img)


# @abyss_team.handle()
# async def abyss_team_handler(event: MessageEvent, reGroup=RegexDict()):
#     abyss_img = await draw_teams_rate(reGroup['floor'])
#     await abyss_team.finish(abyss_img)


def create_wiki_matcher(pattern: str, help_fun: str, help_name: str):
    maps = on_regex(pattern, priority=11, block=True, state={
        'pm_name':        help_fun,
        'pm_description': f"查看该{help_name}的{help_fun}",
        'pm_usage':       f'<{help_name}名> {help_fun}',
        'pm_priority':    5
    })
    maps.plugin_name = 'Paimon_Wiki'

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
        if state['type'] == '角色' and (match_alias := await PlayerAlias.get_or_none(user_id=str(event.user_id), alias=name)):
            try:
                await maps.finish(MessageSegment.image(state['img_url'].format(match_alias.character)))
            except ActionFailed:
                await maps.finish(MessageBuild.Text(f'没有找到{name}的图鉴'))
        match_alias = get_match_alias(name, state['type'])
        true_name = match_alias[0] if (
                isinstance(match_alias, list) and len(match_alias) == 1) else match_alias if isinstance(match_alias,
                                                                                                        str) else None
        if true_name:
            try:
                await maps.finish(MessageSegment.image(state['img_url'].format(match_alias)))
            except ActionFailed:
                await maps.finish(MessageBuild.Text(f'没有找到{name}的图鉴'))
        elif match_alias:
            if isinstance(match_alias, dict):
                match_alias = list(match_alias.keys())
            if 'choice' not in state:
                msg = f'你要查询的{state["type"]}是：\n'
                msg += '\n'.join([f'{int(i) + 1}. {name}' for i, name in enumerate(match_alias)])
                await maps.send(msg + '\n回答\"取消\"来取消查询', at_sender=True)
            state['match_alias'] = match_alias
        else:
            await maps.finish(MessageBuild.Text(f'没有找到{name}的图鉴'))

    @maps.got('choice')
    async def _(event: MessageEvent, state: T_State, choice: str = ArgPlainText('choice')):
        match_alias = state['match_alias']
        if is_cancellation(choice):
            await maps.finish()
        if choice.isdigit() and (1 <= int(choice) <= len(match_alias)):
            try:
                await maps.finish(MessageSegment.image(state['img_url'].format(match_alias[int(choice) - 1])))
            except ActionFailed:
                await maps.finish(MessageBuild.Text(f'没有找到{match_alias[int(choice) - 1]}的图鉴'))
        if choice not in match_alias:
            state['times'] = state['times'] + 1 if 'times' in state else 1
            if state['times'] == 1:
                await maps.reject(f'请旅行者从上面的{state["type"]}中选一个问{NICKNAME}\n回答\"取消\"可以取消查询', at_sender=True)

            elif state['times'] == 2:
                await maps.reject(f'别调戏{NICKNAME}啦，快选一个吧，不想问了请回答\"取消\"！', at_sender=True)
            elif state['times'] >= 3:
                await maps.finish(f'看来旅行者您有点神志不清哦(，下次再问{NICKNAME}吧{MessageSegment.face(146)}', at_sender=True)
        try:
            await maps.finish(MessageSegment.image(state['img_url'].format(choice)))
        except ActionFailed:
            await maps.finish(MessageBuild.Text(f'没有找到{choice}的图鉴'))


create_wiki_matcher(r'(?P<name1>\w*)(?P<type>(原魔|怪物)(图鉴|攻略))(?P<name2>\w*)', '原魔图鉴', '原魔')
create_wiki_matcher(r'(?P<name1>\w*)(?P<type>武器(图鉴|攻略))(?P<name2>\w*)', '武器图鉴', '武器')
create_wiki_matcher(r'(?P<name1>\w*)(?P<type>圣遗物(图鉴|攻略))(?P<name2>\w*)', '圣遗物图鉴', '圣遗物')
create_wiki_matcher(r'(?P<name1>\w*)(?P<type>角色攻略)(?P<name2>\w*)', '角色攻略', '角色')
create_wiki_matcher(r'(?P<name1>\w*)(?P<type>角色材料)(?P<name2>\w*)', '角色材料', '角色')
create_wiki_matcher(r'(?P<name1>\w*)(?P<type>收益曲线)(?P<name2>\w*)', '收益曲线', '角色')
create_wiki_matcher(r'(?P<name1>\w*)(?P<type>参考面板)(?P<name2>\w*)', '参考面板', '角色')
