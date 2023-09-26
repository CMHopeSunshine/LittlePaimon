import datetime
from difflib import get_close_matches
from re import escape
from typing import Dict

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Message, MessageSegment, ActionFailed
from nonebot.internal.matcher import Matcher
from nonebot.internal.params import Arg, ArgPlainText
from nonebot.params import RegexDict
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from LittlePaimon.config import config
from LittlePaimon.utils import DRIVER, NICKNAME, logger
from LittlePaimon.utils.requests import aiorequests
from LittlePaimon.utils.typing import COMMAND_START_RE

wiki_data: Dict[str, Dict[str, str]] = {}
last_update_time: datetime.datetime = datetime.datetime.now()

GAME_ALIAS = ['星穹铁道', '星铁', '崩铁', '穹轨', '铁轨', '铁道', escape('*'), '']
BASE_TYPE = ['图鉴', '材料', '角色图鉴', '角色材料', '攻略', '角色攻略', '遗器图鉴', '光锥图鉴']
GAME_ALIAS_RE = '(' + '|'.join(GAME_ALIAS) + ')'
BASE_TYPE_RE = '(' + '|'.join(BASE_TYPE) + ')'
WIKI_RE = fr'{COMMAND_START_RE}(?P<name>\w{{0,10}}?)(?P<game>{GAME_ALIAS_RE})(?P<type>{BASE_TYPE_RE})'
TYPE_MAP = {
    '角色图鉴': 'role',
    '角色材料': 'material for role',
    '遗器图鉴': 'relic',
    '光锥图鉴': 'lightcone',
    '角色攻略': 'guide for role'
}

__plugin_meta__ = PluginMetadata(
    name='星穹铁道Wiki',
    description='星穹铁道WIKI百科',
    usage='',
    extra={
        'author': '惜月',
        'version': '3.0',
        'priority': 15,
    },
)

wiki = on_regex(WIKI_RE,
                priority=8,
                block=False,
                state={
                    'pm_name': '星穹铁道wiki',
                    'pm_description': '支持查询：角色、光锥、遗器图鉴和角色材料，攻略\n示例：希儿星铁图鉴、与行星相会光锥图鉴',
                    'pm_usage': '<对象名><星铁图鉴|材料|攻略>',
                    'pm_priority': 1
                })


@wiki.handle()
async def sr_wiki_handler(state: T_State, regex_dict: dict = RegexDict()):
    name: str = regex_dict['name']
    game: str = regex_dict['game']
    type: str = regex_dict['type']
    if type in {'图鉴', '材料', '攻略', '角色图鉴', '角色材料', '角色攻略'} and not game:
        await wiki.finish()
    if not wiki_data or datetime.datetime.now() - last_update_time > datetime.timedelta(hours=2):
        await init_data()
    if not wiki_data:
        await wiki.finish('无法获取到星穹铁道资源列表，可能是网络问题~')
    if type in {'攻略', '角色攻略'}:
        type = '角色攻略'
    if type in {'图鉴', '角色图鉴'}:
        type = '角色图鉴'
    elif type in {'材料', '角色材料'}:
        type = '角色材料'
    elif type.startswith('遗器'):
        type = '遗器图鉴'
    elif type.startswith('光锥'):
        type = '光锥图鉴'
    state['type'] = type
    if name:
        state['name'] = Message(name)
    else:
        data = list(wiki_data[TYPE_MAP[type]].keys())
        state['name_list'] = '\n'.join(
            [' '.join(data[i: i + 3]) for i in range(0, len(data), 3)]
        )
    state['times'] = 1


@wiki.got('name', prompt=Message.template('目前支持以下{type}：\n{name_list}\n你要查询哪个呢？'))
async def sr_wiki_got(matcher: Matcher,
                      state: T_State,
                      type: str = Arg('type'),
                      name: str = ArgPlainText('name')):
    if name in {'取消', '退出', '结束'}:
        await wiki.finish(f'好吧，有需要再找{NICKNAME}')
    if not name:
        if state['times'] == 2:
            await wiki.finish('旅行者似乎不太能理解，下次再问我吧' + MessageSegment.face(146))
        else:
            state['times'] += 1
            await wiki.reject(f'你要查询谁的{type}呢？', at_sender=True)
    data = wiki_data[TYPE_MAP[type]]
    matcher.stop_propagation()
    if matches := get_close_matches(name, data.keys(), cutoff=0.4, n=1):
        final_name = str(matches[0])
        try:
            await wiki.finish(MessageSegment.image(
                f'{config.github_proxy}https://raw.githubusercontent.com/Nwflower/star-rail-atlas/master{data[final_name]}'
            ))
        except ActionFailed:
            await wiki.finish(f'{final_name}的{type}发送失败，可能是网络问题')
    else:
        data = list(data.keys())
        msg = '\n'.join(
            [' '.join(data[i: i + 3]) for i in range(0, len(data), 3)]
        )
        await wiki.finish(f'没有找到相关{type}哦!目前支持以下{type}：\n{msg}\n请重新发起查询！')


async def init_data():
    try:
        resp = await aiorequests.get(
            f'{config.github_proxy}https://raw.githubusercontent.com/Nwflower/star-rail-atlas/master/path.json')
        data = resp.json()
        wiki_data.update(data)
        global last_update_time
        last_update_time = datetime.datetime.now()
    except Exception:
        logger.warning('星穹铁道WIKI', '获取<m>WIKI资源</m>时<r>出错</r>，请尝试更换<m>github资源地址</m>')


DRIVER.on_startup(init_data)
