from nonebot import on_regex, on_command, on_notice
from nonebot import plugin as nb_plugin
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, PrivateMessageEvent, MessageEvent
from nonebot.adapters.onebot.v11 import NoticeEvent, FriendAddNoticeEvent, GroupIncreaseNoticeEvent
from nonebot.params import RegexDict, CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule
from nonebot.typing import T_State

from LittlePaimon import SUPERUSERS
from LittlePaimon.config import ConfigManager, PluginManager, HIDDEN_PLUGINS
from LittlePaimon.database import PluginPermission
from LittlePaimon.utils import logger
from LittlePaimon.utils.message import CommandObjectID
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


def notice_rule(event: NoticeEvent):
    return isinstance(event, (FriendAddNoticeEvent, GroupIncreaseNoticeEvent))


def fullmatch(msg: Message = CommandArg()) -> bool:
    return not bool(msg)


manage_cmd = on_regex(
    r'^pm (?P<func>ban|unban) (?P<plugin>([\w ]*)|all|全部) ?(-g (?P<group>[\d ]*) ?)?(-u (?P<user>[\d ]*) ?)?(?P<reserve>-r)?',
    priority=1, block=True, state={
        'pm_name':        'pm-ban|unban',
        'pm_description': '禁用|取消禁用插件的群|用户使用权限',
        'pm_usage':       'pm ban|unban <插件名>',
        'pm_priority':    1
    })
help_cmd = on_command('help', aliases={'帮助', '菜单', 'pm help'}, priority=1, rule=Rule(fullmatch), block=True, state={
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
notices = on_notice(priority=1, rule=Rule(notice_rule), block=True, state={
    'pm_name':        'pm-new-group-user',
    'pm_description': '为新加入的群|用户添加插件使用权限',
    'pm_show':        False
})

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
        if plugin in PluginManager.plugins.keys() or plugin in ['all', '全部']:
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
        if plugin in PluginManager.plugins.keys() or plugin in ['all', '全部']:
            state['plugin'].append(plugin)
        elif module_name := list(
                filter(lambda x: PluginManager.plugins[x].name == plugin, PluginManager.plugins.keys())):
            state['plugin'].append(module_name[0])
        else:
            state['plugin_no_exist'].append(plugin)
    state['group'] = [int(group) for group in match['group'].strip().split(' ')] if match['group'] else []
    state['user'] = [int(user) for user in match['user'].strip().split(' ')] if match['user'] else []


@manage_cmd.got('bool')
async def _(state: T_State):
    if not state['group'] and not state['user']:
        await manage_cmd.finish('用法：pm ban|unban 插件名 -g 群号列表 -u 用户列表', at_sender=True)
    if state['session_id'] in cache_help:
        del cache_help[state['session_id']]
    if not state['plugin'] and state['plugin_no_exist']:
        await manage_cmd.finish(f'没有叫{" ".join(state["plugin_no_exist"])}的插件')
    extra_msg = f'，但没有叫{" ".join(state["plugin_no_exist"])}的插件。' if state['plugin_no_exist'] else '。'
    if state['group'] and not state['user']:
        for group_id in state['group']:
            if 'all' in state['plugin']:
                await PluginPermission.filter(session_id=group_id, session_type='group').update(status=state['bool'])
            else:
                await PluginPermission.filter(name__in=state['plugin'], session_id=group_id,
                                              session_type='group').update(
                    status=state['bool'])
        logger.info('插件管理器',
                    f'已{"<g>启用</g>" if state["bool"] else "<r>禁用</r>"}群<m>{" ".join(map(str, state["group"]))}</m>的插件<m>{" ".join(state["plugin"])}</m>使用权限')
        await manage_cmd.finish(
            f'已{"启用" if state["bool"] else "禁用"}群{" ".join(map(str, state["group"]))}的插件{" ".join(state["plugin"])}使用权限{extra_msg}')
    elif state['user'] and not state['group']:
        for user_id in state['user']:
            if 'all' in state['plugin']:
                await PluginPermission.filter(session_id=user_id, session_type='user').update(status=state['bool'])
            else:
                await PluginPermission.filter(name__in=state['plugin'], session_id=user_id, session_type='user').update(
                    status=state['bool'])
        logger.info('插件管理器',
                    f'已{"<g>启用</g>" if state["bool"] else "<r>禁用</r>"}用户<m>{" ".join(map(str, state["user"]))}</m>的插件<m>{" ".join(state["plugin"])}</m>使用权限')
        await manage_cmd.finish(
            f'已{"启用" if state["bool"] else "禁用"}用户{" ".join(map(str, state["user"]))}的插件{" ".join(state["plugin"])}使用权限{extra_msg}')
    else:
        for group_id in state['group']:
            if 'all' in state['plugin']:
                plugin_list = await PluginPermission.filter(session_id=group_id, session_type='group').all()
            else:
                plugin_list = await PluginPermission.filter(name__in=state['plugin'], session_id=group_id,
                                                            session_type='group').all()
            if plugin_list:
                for plugin in plugin_list:
                    plugin.ban = list(set(plugin.ban) - set(state['user'])) if state['bool'] else list(
                        set(plugin.ban) | set(state['user']))
                    await plugin.save()
        logger.info('插件管理器',
                    f'已{"<g>启用</g>" if state["bool"] else "<r>禁用</r>"}群<m>{" ".join(map(str, state["group"]))}</m>中用户<m>{" ".join(map(str, state["user"]))}</m>的插件<m>{" ".join(state["plugin"])}</m>使用权限')
    await manage_cmd.finish(
        f'已{"启用" if state["bool"] else "禁用"}群{" ".join(map(str, state["group"]))}中用户{" ".join(map(str, state["user"]))}的插件{" ".join(state["plugin"])}使用权限{extra_msg}')


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


@notices.handle()
async def _(event: NoticeEvent):
    plugin_list = nb_plugin.get_loaded_plugins()
    if isinstance(event, FriendAddNoticeEvent):
        models = [
            PluginPermission(name=plugin, session_id=event.user_id, session_type='user') for plugin in plugin_list if plugin not in HIDDEN_PLUGINS
        ]
    elif isinstance(event, GroupIncreaseNoticeEvent) and event.user_id == event.self_id:
        models = [
            PluginPermission(name=plugin, session_id=event.group_id, session_type='group') for plugin in plugin_list if
            plugin not in HIDDEN_PLUGINS
        ]
    else:
        return
    if models:
        await PluginPermission.bulk_create(
            models,
            ignore_conflicts=True
        )
