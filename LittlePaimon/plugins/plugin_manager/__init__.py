from nonebot import on_regex, on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, PrivateMessageEvent, MessageEvent
from nonebot.params import RegexDict, CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from LittlePaimon import SUPERUSERS
from LittlePaimon.config import ConfigManager, PluginManager
from LittlePaimon.database import PluginDisable
from LittlePaimon.utils import logger
from LittlePaimon.utils.message import CommandObjectID, fullmatch_rule
from .draw_help import draw_help

__plugin_meta__ = PluginMetadata(
    name="插件管理",
    description="对派蒙插件进行管理",
    usage='...',
    extra={
        'author':   '惜月',
        'priority': 99,
    }
)


manage_cmd = on_regex(
    r'^pm (?P<func>ban|unban) (?P<plugin>([\w ]*)|all|全部) ?(-g (?P<group>[\d ]*) ?)?(-u (?P<user>[\d ]*) ?)?',
    priority=1, block=True, state={
        'pm_name':        'pm-ban|unban',
        'pm_description': '禁用|取消禁用插件的群|用户使用权限',
        'pm_usage':       'pm ban|unban <插件名>',
        'pm_priority':    1
    })
help_cmd = on_command('help', aliases={'帮助', '菜单', 'pm help'}, priority=1, rule=fullmatch_rule, block=True, state={
    'pm_name':        'pm-help',
    'pm_description': '查看本帮助',
    'pm_usage':       'help',
    'pm_priority':    3
})
set_config_cmd = on_command('pm set', priority=1, permission=SUPERUSER, block=True, state={
    'pm_name':        'pm-set',
    'pm_description': '设置bot的配置项',
    'pm_usage':       'pm set<配置名> <值>',
    'pm_priority':    2
})

cache_help = {}


@manage_cmd.handle()
async def _(event: GroupMessageEvent, state: T_State, match: dict = RegexDict(), session_id: int = CommandObjectID()):
    if event.user_id not in SUPERUSERS and event.sender.role not in ['admin', 'owner']:
        await manage_cmd.finish('你没有权限使用该命令', at_sender=True)
    state['session_id'] = session_id
    state['bool'] = match['func'] == 'unban'
    state['plugin_no_exist'] = []
    if any(w in match['plugin'] for w in {'all', '全部'}):
        state['is_all'] = True
        state['plugin'] = list(PluginManager.plugins.keys())
    else:
        state['is_all'] = False
        state['plugin'] = []
        for plugin in match['plugin'].strip().split(' '):
            if plugin in PluginManager.plugins.keys():
                state['plugin'].append(plugin)
            elif module_name := list(
                    filter(lambda x: PluginManager.plugins[x].name == plugin, PluginManager.plugins.keys())):
                state['plugin'].append(module_name[0])
            else:
                state['plugin_no_exist'].append(plugin)
    if not match['group'] or event.user_id not in SUPERUSERS:
        state['group'] = [event.group_id]
    else:
        state['group'] = [int(group) for group in match['group'].strip().split(' ')]
    state['user'] = [int(user) for user in match['user'].strip().split(' ')] if match['user'] else None


@manage_cmd.handle()
async def _(event: PrivateMessageEvent, state: T_State, match: dict = RegexDict(), session_id: int = CommandObjectID()):
    if event.user_id not in SUPERUSERS:
        await manage_cmd.finish('你没有权限使用该命令', at_sender=True)
    state['session_id'] = session_id
    state['bool'] = match['func'] == 'unban'
    state['plugin_no_exist'] = []
    if any(w in match['plugin'] for w in {'all', '全部'}):
        state['is_all'] = True
        state['plugin'] = [p for p in PluginManager.plugins.keys() if p != 'plugin_manager']
    else:
        state['is_all'] = False
        state['plugin'] = []
        for plugin in match['plugin'].strip().split(' '):
            if plugin in PluginManager.plugins.keys():
                state['plugin'].append(plugin)
            elif module_name := list(
                    filter(lambda x: PluginManager.plugins[x].name == plugin, PluginManager.plugins.keys())):
                state['plugin'].append(module_name[0])
            else:
                state['plugin_no_exist'].append(plugin)
    state['group'] = [int(group) for group in match['group'].strip().split(' ')] if match['group'] else None
    state['user'] = [int(user) for user in match['user'].strip().split(' ')] if match['user'] else None


@manage_cmd.got('bool')
async def _(state: T_State):
    if not state['group'] and not state['user']:
        await manage_cmd.finish('用法：pm ban|unban 插件名 -g 群号列表 -u 用户列表', at_sender=True)
    if state['session_id'] in cache_help:
        del cache_help[state['session_id']]
    if not state['plugin'] and state['plugin_no_exist']:
        await manage_cmd.finish(f'没有叫{" ".join(state["plugin_no_exist"])}的插件')
    extra_msg = f'，但没有叫{" ".join(state["plugin_no_exist"])}的插件。' if state['plugin_no_exist'] else '。'
    filter_arg = {}
    if state['group']:
        filter_arg['group_id__in'] = state['group']
        if state['user']:
            filter_arg['user_id__in'] = state['user']
            logger.info('插件管理器',
                        f'已{"<g>启用</g>" if state["bool"] else "<r>禁用</r>"}群<m>{" ".join(map(str, state["group"]))}</m>中用户<m>{" ".join(map(str, state["user"]))}</m>的插件<m>{" ".join(state["plugin"]) if not state["is_all"] else "全部"}</m>使用权限')
            msg = f'已{"启用" if state["bool"] else "禁用"}群{" ".join(map(str, state["group"]))}中用户{" ".join(map(str, state["user"]))}的插件{" ".join(state["plugin"]) if not state["is_all"] else "全部"}使用权限{extra_msg}'
        else:
            filter_arg['user_id'] = None
            logger.info('插件管理器',
                        f'已{"<g>启用</g>" if state["bool"] else "<r>禁用</r>"}群<m>{" ".join(map(str, state["group"]))}</m>的插件<m>{" ".join(state["plugin"]) if not state["is_all"] else "全部"}</m>使用权限')
            msg = f'已{"启用" if state["bool"] else "禁用"}群{" ".join(map(str, state["group"]))}的插件{" ".join(state["plugin"]) if not state["is_all"] else "全部"}使用权限{extra_msg}'
    else:
        filter_arg['user_id__in'] = state['user']
        filter_arg['group_id'] = None
        logger.info('插件管理器',
                    f'已{"<g>启用</g>" if state["bool"] else "<r>禁用</r>"}用户<m>{" ".join(map(str, state["user"]))}</m>的插件<m>{" ".join(state["plugin"]) if not state["is_all"] else "全部"}</m>使用权限')
        msg = f'已{"启用" if state["bool"] else "禁用"}用户{" ".join(map(str, state["user"]))}的插件{" ".join(state["plugin"]) if not state["is_all"] else "全部"}使用权限{extra_msg}'
    if state['bool']:
        await PluginDisable.filter(name__in=state['plugin'], **filter_arg).delete()
    else:
        for plugin in state['plugin']:
            if state['group']:
                for group in state['group']:
                    if state['user']:
                        for user in state['user']:
                            await PluginDisable.update_or_create(name=plugin, group_id=group, user_id=user)
                    else:
                        await PluginDisable.update_or_create(name=plugin, group_id=group, user_id=None)
            else:
                for user in state['user']:
                    await PluginDisable.update_or_create(name=plugin, user_id=user, group_id=None)

    await manage_cmd.finish(msg)


@help_cmd.handle()
async def _(event: MessageEvent, session_id: int = CommandObjectID()):
    if session_id in cache_help:
        await help_cmd.finish(cache_help[session_id])
    else:
        plugin_list = await PluginManager.get_plugin_list(event.message_type, event.user_id if isinstance(event,
                                                                                                          PrivateMessageEvent) else event.group_id if isinstance(
            event, GroupMessageEvent) else event.guild_id)
        img = await draw_help(plugin_list)
        cache_help[session_id] = img
        await help_cmd.finish(img)


@set_config_cmd.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    msg = msg.extract_plain_text().strip().split(' ')
    if len(msg) != 2:
        await set_config_cmd.finish('参数错误，用法：pm set 配置名 配置值')
    else:
        result = ConfigManager.set_config(msg[0], msg[1])
        await set_config_cmd.finish(result)
