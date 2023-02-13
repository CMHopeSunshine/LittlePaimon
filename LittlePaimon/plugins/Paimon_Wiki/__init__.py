import datetime
import re

from nonebot import on_regex, on_command
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    Message,
    MessageSegment,
    GroupMessageEvent,
    PrivateMessageEvent,
    Bot,
)
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.adapters.onebot.v11.helpers import (
    HandleCancellation,
    convert_chinese_to_bool,
)
from nonebot.params import RegexDict, ArgPlainText, CommandArg, Arg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from LittlePaimon.database import PlayerAlias
from LittlePaimon.utils import NICKNAME
from LittlePaimon.config import config
from LittlePaimon.utils.alias import get_match_alias, WEAPON_TYPE_ALIAS
from LittlePaimon.utils.message import MessageBuild, fullmatch_rule
from LittlePaimon.utils.tool import freq_limiter
from LittlePaimon.utils.typing import COMMAND_START_RE
from LittlePaimon.utils.files import load_json
from LittlePaimon.utils.path import JSON_DATA
from .draw_daily_material import draw_material
from .draw_map import init_map, draw_map, get_full_map
from .SereniteaPot import draw_pot_materials
from .Atlas import (
    get_match_card,
    get_card_resources,
    get_match_specialty,
    get_all_specialty,
    get_atlas_full_path,
)
from .wiki_api import API

__plugin_meta__ = PluginMetadata(
    name='原神Wiki',
    description='原神WIKI百科',
    usage='',
    extra={
        'author': '惜月',
        'version': '3.0',
        'priority': 3,
    },
)

cancel = [HandleCancellation(f'好吧，有需要再找{NICKNAME}')]
BASE_TYPE = [
    '角色',
    '天赋',
    '培养',
    '命座',
    '技能',
    '武器',
    '圣遗物',
    '原魔',
    '怪物',
    '七圣召唤',
    '原牌',
    '卡牌',
    '特产',
    '材料',
]
BASE_TYPE_RE = '(' + '|'.join(BASE_TYPE) + ')'
IMG_TYPE = ['图鉴', '攻略', '材料', '参考面板', '收益曲线']
IMG_TYPE_RE = '(' + '|'.join(IMG_TYPE) + ')'

WIKI_RE = fr'{COMMAND_START_RE}(?P<name1>\w{{0,7}}?)(?P<type>{BASE_TYPE_RE}?{IMG_TYPE_RE})(?P<name2>\w{{0,7}})'

total_wiki = on_regex(
    WIKI_RE,
    priority=9,
    block=True,
    state={
        'pm_name': '原神WIKI',
        'pm_description': '支持查询：角色的图鉴、攻略、材料、参考面板、收益曲线，武器、圣遗物、原魔、七圣召唤图鉴，今日|周几材料'
        '\n示例：钟离攻略、护摩图鉴、今日材料',
        'pm_usage': '<对象名><图鉴|攻略|材料>',
        'pm_priority': 1,
    },
)
material_map_full = on_command(
    '材料地图',
    priority=8,
    block=True,
    state={
        'pm_name': '材料地图',
        'pm_description': '查看多个材料大地图采集点。\n示例：材料地图 鸣草 鬼兜虫 提瓦特',
        'pm_usage': '材料地图<材料名列表>[地图]',
        'pm_priority': 3,
    },
)
generate_map = on_command(
    '生成地图',
    priority=1,
    block=True,
    permission=SUPERUSER,
    state={
        'pm_name': '生成地图',
        'pm_description': '生成材料图鉴等所需要的地图资源，仅超级用户可用。',
        'pm_usage': '生成地图',
        'pm_priority': 4,
    },
)
pot_material = on_command(
    '尘歌壶摹本',
    aliases={'摹本材料', '尘歌壶材料', '尘歌壶摹本材料'},
    priority=11,
    block=True,
    state={
        'pm_name': '尘歌壶摹本材料',
        'pm_description': '查看尘歌壶摹本所需要的材料总览',
        'pm_usage': '尘歌壶材料<摹数>',
        'pm_priority': 5,
    },
)
card_wiki_list = on_command(
    '七圣召唤列表',
    aliases={'七圣召唤卡牌列表', '原牌列表', '原石传说列表'},
    priority=11,
    rule=fullmatch_rule,
    block=True,
    state={
        'pm_name': '七圣召唤图鉴列表',
        'pm_description': '查看已支持查询的七圣召唤卡牌图鉴列表',
        'pm_usage': '原牌列表',
        'pm_priority': 6,
    },
)


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


@material_map_full.got('names', prompt='请输入要查询的材料名称，或回答【取消】退出', parameterless=cancel)
async def _(event: MessageEvent, map_: str = Arg('map'), names=Arg('names')):
    if isinstance(names, Message):
        names = names.extract_plain_text().split(' ')
    if not freq_limiter.check(
        f'材料地图_{event.group_id if isinstance(event, GroupMessageEvent) else event.user_id}'
    ):
        await material_map_full.finish(
            f'材料地图查询冷却中，剩余{freq_limiter.left(f"材料地图_{event.group_id if isinstance(event, GroupMessageEvent) else event.user_id}")}秒',
            at_sender=True,
        )
    freq_limiter.start(
        f'材料地图_{event.group_id if isinstance(event, GroupMessageEvent) else event.user_id}',
        15,
    )
    if len(names) > 3:
        names = names[:3]
    await material_map_full.send(MessageBuild.Text(f'开始查找{"、".join(names)}的资源点，请稍候...'))
    result = await get_full_map(names, map_)
    await material_map_full.finish(result, at_sender=True)


@generate_map.got(
    'confirm',
    prompt=f'生成材料地图资源要求大量内存，如果内存不足，可能会导致{NICKNAME}崩溃，请确认你的机器内存充足，回答【是|否】继续执行！',
)
async def _(event: MessageEvent):
    if convert_chinese_to_bool(event.message):
        await generate_map.send('开始生成地图资源，这可能需要较长时间...')
        result = await init_map()
        await generate_map.finish(result)
    else:
        await generate_map.finish('取消生成地图资源！')


@pot_material.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    msg = msg.extract_plain_text().strip()
    if len(msg) != 10 and not msg.isdigit():
        await pot_material.finish('这个尘歌壶摹数不对哦，必须是十位数的数字')
    else:
        try:
            code = int(msg)
            result = await draw_pot_materials(code, user_id=str(event.user_id))
        except Exception as e:
            result = f'绘制尘歌壶摹本材料失败，错误信息：{e}'
        await pot_material.finish(result, at_sender=True)


@total_wiki.handle()
async def _(state: T_State, regex_dict: dict = RegexDict()):
    if regex_dict['name1'] and regex_dict['name2']:
        await total_wiki.finish()
    name: str = regex_dict['name1'] or regex_dict['name2'] or ''
    type: str = regex_dict.get('type')
    if type.startswith(('角色', '天赋', '培养', '命座', '技能')):
        type = f'角色{type[2:]}'
    elif type.startswith('武器'):
        type = '武器图鉴'
    elif type.startswith('圣遗物'):
        type = '圣遗物图鉴'
    elif type.startswith(('材料', '特产')) and type != '材料':
        type = '特产图鉴'
    elif type.startswith(('原魔', '怪物')):
        type = '原魔图鉴'
    elif type.startswith(('七圣召唤', '原牌', '卡牌')):
        type = '七圣召唤图鉴'
    if type.endswith('材料') and re.match(r'现在|[今明后][天日]|周[一二三四五六日]', name):
        type = '每日材料'
    elif type.endswith(('参考面板', '收益曲线')):
        type = type[-4:]
    state['type'] = type
    if name:
        state['name'] = Message(name)
    elif type not in {'图鉴', '攻略', '材料'}:
        state['name'] = Message('全部')
    state['times'] = 1


week_str = ['周一', '周二', '周三', '周四', '周五', '周六']


@total_wiki.got('name', prompt=Message.template('你要查询谁的{type}呢？'), parameterless=cancel)
async def _(
    bot: Bot,
    event: MessageEvent,
    state: T_State,
    type: str = Arg('type'),
    name: str = ArgPlainText('name'),
):
    if not name:
        if state['times'] == 2:
            await total_wiki.finish('旅行者似乎不太能理解，下次再问我吧' + MessageSegment.face(146))
        else:
            state['times'] = state['times'] + 1
            await total_wiki.reject(f'你要查询谁的{type}呢？', at_sender=True)
    if type == '每日材料':
        if name in {'今日', '今天', '现在'}:
            day = datetime.datetime.now().weekday()
        elif name in {'明日', '明天'}:
            day = (datetime.datetime.now() + datetime.timedelta(days=1)).weekday()
        elif name in {'后日', '后天'}:
            day = (datetime.datetime.now() + datetime.timedelta(days=2)).weekday()
        elif name == '周日':
            await total_wiki.finish('周日所有材料都可以刷哦!', at_sender=True)
        elif name.startswith('周'):
            await total_wiki.send('开始获取每日材料，请稍候...')
            await total_wiki.finish(await draw_material(str(event.user_id), name))
        if day == 6:
            await total_wiki.finish('周日所有材料都可以刷哦!', at_sender=True)
        else:
            await total_wiki.send('开始获取每日材料，请稍候...')
            await total_wiki.finish(
                await draw_material(str(event.user_id), week_str[day]), at_sender=True
            )
    else:
        matches = {}
        if type == '参考面板' and name in {'火', '水', '冰', '雷', '风', '岩', '草'}:
            await total_wiki.finish(
                MessageSegment.image(
                    API[type].format(proxy=config.github_proxy, name=name)
                )
            )
        elif type.startswith('角色') or type in {'参考面板', '收益曲线'}:
            if name == '全部':
                matches = load_json(JSON_DATA / '类型.json')['角色']['元素类型']
            elif re.match('^[火水冰雷风岩草](元素|属性|系)?$', name):
                matches = {
                    '角色': load_json(JSON_DATA / '类型.json')['角色']['元素类型'][name[0]]
                }
            elif name in WEAPON_TYPE_ALIAS.keys():
                matches = {
                    '角色': load_json(JSON_DATA / '类型.json')['角色']['武器类型'][
                        WEAPON_TYPE_ALIAS[name]
                    ]
                }
            elif alias := await PlayerAlias.get_or_none(
                user_id=str(event.user_id), alias=name
            ):
                final_name = alias.character
                matches = {}
                try:
                    await total_wiki.finish(
                        MessageSegment.image(
                            API[type].format(proxy=config.github_proxy, name=final_name)
                        )
                    )
                except ActionFailed:
                    await total_wiki.finish(
                        MessageBuild.Text(f'{final_name}的{type}发送失败，可能是网络问题或者不存在该资源')
                    )
            else:
                matches = get_match_alias(name, '角色')
        elif type.startswith('武器'):
            if name == '全部':
                matches = load_json(JSON_DATA / '类型.json')['武器']
            elif name in WEAPON_TYPE_ALIAS.keys():
                matches = {
                    '武器': load_json(JSON_DATA / '类型.json')['武器'][
                        WEAPON_TYPE_ALIAS[name]
                    ]
                }
            else:
                matches = get_match_alias(name, '武器')
        elif type.startswith('原魔'):
            matches = (
                {'原魔': list(load_json(JSON_DATA / 'alias.json')['原魔'].keys())}
                if name == '全部'
                else get_match_alias(name, '原魔')
            )
        elif type.startswith('圣遗物'):
            matches = (
                {'圣遗物': list(load_json(JSON_DATA / 'alias.json')['圣遗物'].keys())}
                if name == '全部'
                else get_match_alias(name, '圣遗物')
            )
        elif type.startswith('七圣召唤'):
            if name == '全部':
                matches = await get_match_card(name)
            elif c := await get_match_card(name):
                matches = {'七圣召唤': c}
        elif type == '特产图鉴' and (s := await get_match_specialty(name)):
            matches = {'特产': s}
        else:
            if re.match('^[火水冰雷风岩草](元素|属性|系)?$', name):
                matches = {
                    '角色': load_json(JSON_DATA / '类型.json')['角色']['元素类型'][name[0]]
                }
            elif name in WEAPON_TYPE_ALIAS.keys():
                matches = {
                    '角色': load_json(JSON_DATA / '类型.json')['角色']['武器类型'][
                        WEAPON_TYPE_ALIAS[name]
                    ],
                    '武器': load_json(JSON_DATA / '类型.json')['武器'][
                        WEAPON_TYPE_ALIAS[name]
                    ],
                }
            elif alias := await PlayerAlias.get_or_none(
                user_id=str(event.user_id), alias=name
            ):
                final_name = alias.character
                if type in {'材料', '攻略', '图鉴'}:
                    type = f'角色{type}'
                try:
                    await total_wiki.finish(
                        MessageSegment.image(
                            API[type].format(proxy=config.github_proxy, name=final_name)
                        )
                    )
                except ActionFailed:
                    await total_wiki.finish(f'{final_name}的{type}发送失败，可能是网络问题或者不存在该资源')
            else:
                if type == '材料':
                    matches = get_match_alias(name, ['角色', '武器', '原魔'])
                else:
                    matches = get_match_alias(name, ['角色', '武器', '原魔', '圣遗物'])
                    if m := await get_match_card(name):
                        matches['七圣召唤'] = m
                if s := await get_match_specialty(name):
                    matches['特产'] = s
        if not matches:
            # await total_wiki.finish(MessageBuild.Text(f'没有名为{name}的{type}哦，是不是打错了~'), at_sender=True)
            await total_wiki.finish()
        elif len(matches) == 1 and len(list(matches.values())[0]) == 1:
            final_name = list(matches.values())[0][0]
            temp_type = list(matches.keys())[0]
            if type in {'材料', '攻略', '图鉴'}:
                type = f'{temp_type}图鉴' if temp_type != '角色' else f'{temp_type}{type}'
            if type in {'七圣召唤图鉴', '武器图鉴'}:
                final_name = await get_atlas_full_path(
                    final_name, 'card' if type == '七圣召唤图鉴' else 'weapon'
                )
            try:
                await total_wiki.finish(
                    MessageSegment.image(
                        API[type].format(proxy=config.github_proxy, name=final_name)
                    )
                )
            except ActionFailed:
                await total_wiki.finish(f'{final_name}的{type}发送失败，可能是网络问题或者不存在该资源')
        else:
            send_flag = False
            if sum(len(value) for value in matches.values()) >= 15 and isinstance(
                event, (PrivateMessageEvent, GroupMessageEvent)
            ):
                if len(matches) == 1:
                    matches = {
                        i: matches[list(matches.keys())[0]][i : i + 5]
                        for i in range(0, len(matches[list(matches.keys())[0]]), 5)
                    }
                index = 1
                msg = []
                for key, value in matches.items():
                    temp_msg = f'{key}:\n' if not isinstance(key, int) else ''
                    for v in value:
                        temp_msg += f'{index}.{v}\n'
                        index += 1
                    msg.append(
                        {
                            'type': 'node',
                            'data': {
                                'name': NICKNAME,
                                'uin': event.self_id,
                                'content': temp_msg.strip(),
                            },
                        }
                    )
                msg.insert(
                    0,
                    {
                        'type': 'node',
                        'data': {
                            'name': NICKNAME,
                            'uin': event.self_id,
                            'content': f'你要查询哪个的{type}呢？',
                        },
                    },
                )
                msg.append(
                    {
                        'type': 'node',
                        'data': {
                            'name': NICKNAME,
                            'uin': event.self_id,
                            'content': '回答\"序号\"查询或回答\"取消\"取消查询',
                        },
                    }
                )
                try:
                    send_flag = True
                    if isinstance(event, GroupMessageEvent):
                        await bot.call_api(
                            'send_group_forward_msg',
                            group_id=event.group_id,
                            messages=msg,
                        )
                    elif isinstance(event, PrivateMessageEvent):
                        await bot.call_api(
                            'send_private_forward_msg',
                            user_id=event.user_id,
                            messages=msg,
                        )
                except ActionFailed:
                    send_flag = False
            if not send_flag:
                index = 1
                msg = f'你要查询的{type}是：\n'
                for key, value in matches.items():
                    for v in value:
                        msg += (
                            f'{index}.{v}({key})\n'
                            if len(matches) > 1
                            else f'{index}.{v}\n'
                        )
                        index += 1
                msg += '回答\"序号\"查询或回答\"取消\"取消查询'
                await total_wiki.send(msg)
            state['matches'] = matches


@total_wiki.got('choice', parameterless=cancel)
async def _(
    state: T_State,
    matches: dict = Arg('matches'),
    choice: str = ArgPlainText('choice'),
    type: str = Arg('type'),
):
    if choice.isdigit() and 1 <= int(choice) <= sum(
        len(value) for value in matches.values()
    ):
        choice_num = int(choice)
    else:
        choice_num = None
    final_name = None
    for key, value in matches.items():
        if choice_num:
            if len(value) >= choice_num:
                final_name = value[choice_num - 1]
                if type in {'材料', '攻略', '图鉴'}:
                    type = f'{key}图鉴' if key != '角色' else f'{key}{type}'
                break
            else:
                choice_num -= len(value)
        elif choice in value:
            final_name = choice
            if type in {'材料', '攻略', '图鉴'}:
                type = f'{key}图鉴' if key != '角色' else f'{key}{type}'
            break
    if final_name:
        if type in {'七圣召唤图鉴', '武器图鉴'}:
            final_name = await get_atlas_full_path(
                final_name, 'card' if type == '七圣召唤图鉴' else 'weapon'
            )
        try:
            await total_wiki.finish(
                MessageSegment.image(
                    API[type].format(proxy=config.github_proxy, name=final_name)
                )
            )
        except ActionFailed:
            await total_wiki.finish(f'{final_name}的{type}发送失败，可能是网络问题或者不存在该资源')
    elif state['times'] == 2:
        await total_wiki.finish('旅行者似乎不太能理解，下次再问我吧' + MessageSegment.face(146))
    else:
        state['times'] = state['times'] + 1
        await total_wiki.reject(
            f'请旅行者从上面的{type}中选一个问{NICKNAME}或回答\"取消\"可以取消查询', at_sender=True
        )


@card_wiki_list.handle()
async def _(bot: Bot, event: MessageEvent):
    result = await get_card_resources()
    if not result:
        await card_wiki_list.finish('读取七圣召唤卡牌列表失败')
    msg = [
        {
            'type': 'node',
            'data': {
                'name': NICKNAME,
                'uin': event.self_id,
                'content': f'{type}：\n' + '\n'.join(cards),
            },
        }
        for type, cards in result.items()
    ]
    msg.insert(
        0,
        {
            'type': 'node',
            'data': {'name': NICKNAME, 'uin': event.self_id, 'content': '七圣召唤卡牌列表如下'},
        },
    )
    try:
        if isinstance(event, GroupMessageEvent):
            await bot.call_api(
                'send_group_forward_msg', group_id=event.group_id, messages=msg
            )
        elif isinstance(event, PrivateMessageEvent):
            await bot.call_api(
                'send_private_forward_msg', user_id=event.user_id, messages=msg
            )
        else:
            msg = '七圣召唤卡牌列表:\n'
            for type, cards in result.items():
                msg += (
                    f'{type}：\n'
                    + '\n'.join(
                        [' '.join(cards[i : i + 3]) for i in range(0, len(cards), 3)]
                    )
                    + '\n'
                )
            await card_wiki_list.send(msg)
    except ActionFailed:
        await card_wiki_list.finish('七圣召唤卡牌列表发送失败，账号可能被风控')
