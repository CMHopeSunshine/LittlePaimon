import asyncio
import datetime

from nonebot import on_regex, on_command
from nonebot.matcher import Matcher
from nonebot.exception import IgnoredException
from nonebot.params import RegexDict, CommandArg
from nonebot.permission import SUPERUSER
from nonebot.message import run_preprocessor
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, PrivateMessageEvent, MessageEvent
from nonebot.typing import T_State

from LittlePaimon import SUPERUSERS, DRIVER
from LittlePaimon.utils import logger
from LittlePaimon.utils.message import CommandObjectID
from LittlePaimon.database.models import PluginPermission, PluginStatistics
from .manager import PluginManager, hidden_plugins
from .model import MatcherInfo
from .draw_help import draw_help

plugin_manager = PluginManager()

manage_cmd = on_regex(r'^pm (?P<func>ban|unban) (?P<plugin>([\w ]*)|all|全部) ?(-g (?P<group>[\d ]*) ?)?(-u (?P<user>[\d ]*) ?)?(?P<reserve>-r)?', priority=1)
help_cmd = on_command('help', aliases={'帮助', '菜单', 'pm help'}, priority=1)
set_config_cmd = on_command('pm set', priority=1, permission=SUPERUSER)

cache_help = {}


@manage_cmd.handle()
async def _(event: GroupMessageEvent, state: T_State, match: dict = RegexDict(), session_id: int = CommandObjectID()):
    if event.user_id not in SUPERUSERS and event.sender.role not in ['admin', 'owner']:
        await manage_cmd.finish('你没有权限使用该命令', at_sender=True)
    state['session_id'] = session_id
    state['bool'] = match['func'] == 'unban'
    state['plugin'] = []
    state['plugin_no_exist'] = []
    for plugin in match['plugin'].strip().split(' '):
        if plugin not in plugin_manager.data.keys() and plugin not in ['all', '全部']:
            if module_name := list(filter(lambda x: plugin_manager.data[x].name == plugin, plugin_manager.data.keys())):
                state['plugin'].append(module_name[0])
            else:
                state['plugin_no_exist'].append(plugin)
    if not match['group'] or event.user_id not in SUPERUSERS:
        state['group'] = [event.group_id]
    else:
        state['group'] = [int(group) for group in match['group'].strip().split(' ')]
    state['user'] = [int(user) for user in match['user'].strip().split(' ')] if match['user'] else []


@manage_cmd.handle()
async def _(event: PrivateMessageEvent, state: T_State, match: dict = RegexDict(), session_id: int = CommandObjectID()):
    if event.user_id not in SUPERUSERS:
        await manage_cmd.finish('你没有权限使用该命令', at_sender=True)
    state['session_id'] = session_id
    state['bool'] = match['func'] == 'unban'
    state['plugin'] = []
    state['plugin_no_exist'] = []
    for plugin in match['plugin'].strip().split(' '):
        if plugin not in plugin_manager.data.keys() and plugin not in ['all', '全部']:
            if module_name := list(filter(lambda x: plugin_manager.data[x].name == plugin, plugin_manager.data.keys())):
                state['plugin'].append(module_name[0])
            else:
                state['plugin_no_exist'].append(plugin)
    state['group'] = [int(group) for group in match['group'].strip().split(' ')] if match['group'] else []
    state['user'] = [int(user) for user in match['user'].strip().split(' ')] if match['user'] else []


@manage_cmd.got('bool')
async def _(state: T_State):
    if not state['group'] and state['user']:
        await manage_cmd.finish('使用ban|unban -g 群号 -u 用户', at_sender=True)
    if state['session_id'] in cache_help:
        del cache_help[state['session_id']]
    if not state['plugin'] and state['plugin_no_exist']:
        await manage_cmd.finish(f'没有叫{" ".join(state["plugin_no_exist"])}的插件')
    extra_msg = f'但没有叫{" ".join(state["plugin_no_exist"])}的插件' if state['plugin_no_exist'] else ''
    if state['group'] and not state['user']:
        for group_id in state['group']:
            if 'all' in state['plugin']:
                await PluginPermission.filter(session_id=group_id, session_type='group').update(status=state['bool'])
            else:
                await asyncio.gather(*[PluginPermission.filter(name=plugin, session_id=group_id, session_type='group').update(status=state['bool']) for plugin in state['plugin']])
        logger.info('插件管理器', f'已{"<g>启用</g>" if state["bool"] else "<r>禁用</r>"}群<m>{" ".join(map(str, state["group"]))}</m>的插件<m>{" ".join(state["plugin"])}</m>使用权限')
        await manage_cmd.finish(f'已{"启用" if state["bool"] else "禁用"}群{" ".join(map(str, state["group"]))}的插件{" ".join(state["plugin"])}使用权限，{extra_msg}')
    elif state['user'] and not state['group']:
        for user_id in state['user']:
            if 'all' in state['plugin']:
                await PluginPermission.filter(session_id=user_id, session_type='user').update(status=state['bool'])
            else:
                await asyncio.gather(*[PluginPermission.filter(name=plugin, session_id=user_id, session_type='user').update(status=state['bool']) for plugin in state['plugin']])
        logger.info('插件管理器',
                    f'已{"<g>启用</g>" if state["bool"] else "<r>禁用</r>"}用户<m>{" ".join(map(str, state["user"]))}</m>的插件<m>{" ".join(state["plugin"])}</m>使用权限')
        await manage_cmd.finish(f'已{"启用" if state["bool"] else "禁用"}用户{" ".join(map(str, state["user"]))}的插件{" ".join(state["plugin"])}使用权限，{extra_msg}')
    else:
        for group_id in state['group']:
            if 'all' in state['plugin']:
                plugin_list = await PluginPermission.filter(session_id=group_id, session_type='group').all()
            else:
                plugin_list = list(await asyncio.gather(*[PluginPermission.get_or_none(name=p, session_id=group_id, session_type='group') for p in state['plugin']]))
            for plugin in plugin_list:
                if plugin is not None:
                    plugin.ban = list(set(plugin.ban) - set(state['user'])) if state['bool'] else list(set(plugin.ban) | set(state['user']))
                    await plugin.save()
        logger.info('插件管理器',
                    f'已{"<g>启用</g>" if state["bool"] else "<r>禁用</r>"}群<m>{" ".join(map(str, state["group"]))}</m>中用户<m>{" ".join(map(str, state["user"]))}</m>的插件<m>{" ".join(state["plugin"])}</m>使用权限')
    await manage_cmd.finish(f'已{"启用" if state["bool"] else "禁用"}群{" ".join(map(str, state["group"]))}中用户{" ".join(map(str, state["user"]))}的插件{" ".join(state["plugin"])}使用权限，{extra_msg}')


@help_cmd.handle()
async def _(event: MessageEvent, session_id: int = CommandObjectID()):
    if session_id in cache_help:
        await help_cmd.finish(cache_help[session_id])
    else:
        plugin_list = await plugin_manager.get_plugin_list(event.message_type, event.user_id if isinstance(event, PrivateMessageEvent) else event.group_id if isinstance(event, GroupMessageEvent) else event.guild_id)
        img = await draw_help(plugin_list)
        cache_help[session_id] = img
        await help_cmd.finish(img)


@set_config_cmd.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    msg = msg.extract_plain_text().strip().split(' ')
    if len(msg) != 2:
        await set_config_cmd.finish('参数错误，用法：pm set 配置名 配置值')
    else:
        result = plugin_manager.set_config(msg[0], msg[1])
        await set_config_cmd.finish(result)


@DRIVER.on_bot_connect
async def _():
    await plugin_manager.init_plugins()


@run_preprocessor
async def _(event: MessageEvent, matcher: Matcher):
    if matcher.plugin_name in hidden_plugins:
        return
    if isinstance(event, PrivateMessageEvent):
        session_id = event.user_id
        session_type = 'user'
    elif isinstance(event, GroupMessageEvent):
        session_id = event.group_id
        session_type = 'group'
    else:
        return

    # 权限检查
    perm = await PluginPermission.get_or_none(name=matcher.plugin_name, session_id=session_id, session_type=session_type)
    if not perm:
        return
    if not perm.status:
        raise IgnoredException('插件使用权限已禁用')
    if isinstance(event, GroupMessageEvent) and event.user_id in perm.ban:
        raise IgnoredException('用户被禁止使用该插件')

    # 命令调用统计
    if matcher.plugin_name in plugin_manager.data and 'pm_name' in matcher.state:
        if matcher_info := list(filter(lambda x: x.pm_name == matcher.state['pm_name'], plugin_manager.data[matcher.plugin_name].matchers)):
            matcher_info = matcher_info[0]
            await PluginStatistics.create(plugin_name=matcher.plugin_name,
                                          matcher_name=matcher_info.pm_name,
                                          matcher_usage=matcher_info.pm_usage,
                                          group_id=event.group_id if isinstance(event, GroupMessageEvent) else None,
                                          user_id=event.user_id,
                                          message_type=session_type,
                                          time=datetime.datetime.now())


