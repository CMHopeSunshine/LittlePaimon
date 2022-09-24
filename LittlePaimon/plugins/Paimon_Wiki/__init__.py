import time

from nonebot import on_regex, on_command
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment, GroupMessageEvent
from nonebot.adapters.onebot.v11.helpers import HandleCancellation
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.params import RegexDict, ArgPlainText, CommandArg, Arg
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State

from LittlePaimon import NICKNAME
from LittlePaimon.utils.alias import get_match_alias
from LittlePaimon.utils.tool import freq_limiter
from LittlePaimon.utils.message import MessageBuild
from LittlePaimon.database.models import PlayerAlias
from LittlePaimon.config import RESOURCE_BASE_PATH
from .draw_map import init_map, draw_map, get_full_map
from .draw_daily_material import draw_material

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
material_map = on_command('材料图鉴', priority=11, block=True, state={
    'pm_name':        '材料图鉴',
    'pm_description': '查看某个材料的介绍和采集点。',
    'pm_usage':       '材料图鉴<材料名>[地图]',
    'pm_priority':    9
})
material_map_full = on_command('材料地图', priority=11, block=True, state={
    'pm_name':        '材料地图',
    'pm_description': '查看多个材料大地图采集点。\n示例：材料地图 鸣草 鬼兜虫 提瓦特',
    'pm_usage':       '材料地图<材料名列表>[地图]',
    'pm_priority':    10
})
generate_map = on_command('生成地图', priority=1, block=True, permission=SUPERUSER, state={
    'pm_name':        '生成地图',
    'pm_description': '生成材料图鉴等所需要的地图资源，仅超级用户可用。',
    'pm_usage':       '生成地图',
    'pm_priority':    11
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
    await daily_material.send('开始获取每日材料，请稍候...')
    if regex_dict['day'] in ['今日', '今天', '现在']:
        day = time.strftime("%w")
    elif regex_dict['day'] in ['明日', '明天']:
        day = str(int(time.strftime("%w")) + 1)
    elif regex_dict['day'] in ['后日', '后天']:
        day = str(int(time.strftime("%w")) + 2)
    elif regex_dict['day'] == '周日':
        await daily_material.finish('周日所有材料都可以刷哦!', at_sender=True)
    elif regex_dict['day'].startswith('周'):
        await daily_material.finish(await draw_material(str(event.user_id), regex_dict['day']))
    if day == '0':
        await daily_material.finish('周日所有材料都可以刷哦!', at_sender=True)
    else:
        await daily_material.finish(await draw_material(str(event.user_id), {
            '1': '周一',
            '2': '周二',
            '3': '周三',
            '4': '周四',
            '5': '周五',
            '6': '周六',
        }[day]), at_sender=True)


@material_map.handle()
async def _(event: MessageEvent, state: T_State, msg: Message = CommandArg()):
    if params := msg.extract_plain_text().strip():
        params = params.split(' ')
        state['name'] = Message(params[0])
        if len(params) > 1:
            if params[1] in {'提瓦特', '层岩巨渊', '渊下宫'}:
                state['map'] = params[1]
        else:
            state['map'] = Message('提瓦特')
    else:
        state['map'] = Message('提瓦特')


@material_map.got('map', prompt='地图名称有误，请在【提瓦特、层岩巨渊、渊下宫】中选择，或回答【取消】退出',
                  parameterless=[HandleCancellation(f'好吧，有需要再找{NICKNAME}')])
async def _(event: MessageEvent, state: T_State, map_: str = ArgPlainText('map')):
    if map_ not in {'提瓦特', '层岩巨渊', '渊下宫'}:
        await material_map.reject('地图名称有误，请在【提瓦特、层岩巨渊、渊下宫】中选择')
    else:
        state['map'] = Message(map_)


@material_map.got('name', prompt='请输入要查询的材料名称，或回答【取消】退出', parameterless=[HandleCancellation(f'好吧，有需要再找{NICKNAME}')])
async def _(event: MessageEvent, map_: str = ArgPlainText('map'), name: str = ArgPlainText('name')):
    if (file_path := RESOURCE_BASE_PATH / 'genshin_map' / 'results' / f'{map_}_{name}.png').exists():
        await material_map.finish(MessageSegment.image(file_path), at_sender=True)
    else:
        await material_map.send(MessageBuild.Text(f'开始查找{name}的资源点，请稍候...'))
        result = await draw_map(name, map_)
        await material_map.finish(result, at_sender=True)


@material_map_full.handle()
async def _(event: MessageEvent, state: T_State, msg: Message = CommandArg()):
    state['map'] = '提瓦特'
    if params := msg.extract_plain_text().strip():
        params = params.split(' ')
        for p in params.copy():
            if p in {'提瓦特', '层岩巨渊', '渊下宫'}:
                params.remove(p)
                state['map'] = p
        state['names'] = params


@material_map_full.got('names', prompt='请输入要查询的材料名称，或回答【取消】退出',
                       parameterless=[HandleCancellation(f'好吧，有需要再找{NICKNAME}')])
async def _(event: MessageEvent, map_: str = Arg('map'), names=Arg('names')):
    if isinstance(names, Message):
        names = names.extract_plain_text().split(' ')
    if not freq_limiter.check(f'材料地图_{event.group_id if isinstance(event, GroupMessageEvent) else event.user_id}'):
        await material_map_full.finish(
            f'材料地图查询冷却中，剩余{freq_limiter.left(f"材料地图_{event.group_id if isinstance(event, GroupMessageEvent) else event.user_id}")}秒',
            at_sender=True)
    freq_limiter.start(f'材料地图_{event.group_id if isinstance(event, GroupMessageEvent) else event.user_id}', 15)
    if len(names) > 3:
        names = names[:3]
    await material_map_full.send(MessageBuild.Text(f'开始查找{"、".join(names)}的资源点，请稍候...'))
    result = await get_full_map(names, map_)
    await material_map_full.finish(result, at_sender=True)


@generate_map.handle()
async def _(event: MessageEvent):
    await generate_map.send('开始生成地图资源，这可能需要较长时间。')
    result = await init_map()
    await generate_map.finish(result)


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

    @maps.got('name', prompt=Message.template('请提供要查询的{type}'),
              parameterless=[HandleCancellation(f'好吧，有需要再找{NICKNAME}')])
    async def _(event: MessageEvent, state: T_State):
        name = state['name']
        if isinstance(name, Message):
            name = name.extract_plain_text().strip()
        if state['type'] == '角色' and (
                match_alias := await PlayerAlias.get_or_none(user_id=str(event.user_id), alias=name)):
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

    @maps.got('choice', parameterless=[HandleCancellation(f'好吧，有需要再找{NICKNAME}')])
    async def _(event: MessageEvent, state: T_State, choice: str = ArgPlainText('choice')):
        match_alias = state['match_alias']
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
