import asyncio
import datetime
from typing import Dict, List

from nonebot import plugin as nb_plugin
from nonebot import get_bot
from nonebot.matcher import Matcher
from nonebot.exception import IgnoredException
from nonebot.message import run_preprocessor
from nonebot.adapters.onebot.v11 import MessageEvent, PrivateMessageEvent, GroupMessageEvent
from LittlePaimon.utils import logger, DRIVER, SUPERUSERS
from LittlePaimon.utils.path import PLUGIN_CONFIG
from LittlePaimon.utils.files import load_yaml, save_yaml
from LittlePaimon.database.models import PluginPermission, PluginStatistics
from .model import MatcherInfo, PluginInfo

HIDDEN_PLUGINS = [
    'LittlePaimon',
    'config',
    'nonebot_plugin_apscheduler',
    'nonebot_plugin_gocqhttp',
    'nonebot_plugin_htmlrender',
    'nonebot_plugin_imageutils',
    'NoticeAndRequest'
]


class PluginManager:
    plugins: Dict[str, PluginInfo] = {}
    for file in PLUGIN_CONFIG.iterdir():
        if file.is_file() and file.name.endswith('.yml'):
            data = load_yaml(file)
            plugins[file.name.replace('.yml', '')] = PluginInfo.parse_obj(data)

    @classmethod
    def save(cls):
        """
        保存数据
        """
        for name, plugin in cls.plugins.items():
            save_yaml(plugin.dict(exclude={'status'}), PLUGIN_CONFIG / f'{name}.yml')

    @classmethod
    async def init(cls):
        plugin_list = nb_plugin.get_loaded_plugins()
        group_list = await get_bot().get_group_list()
        user_list = await get_bot().get_friend_list()
        for plugin in plugin_list:
            if plugin.name not in HIDDEN_PLUGINS:
                # 将所有PluginPermission相同的，只保留一个
                if group_list:
                    for group in group_list:
                        count = await PluginPermission.filter(
                            name=plugin.name, session_id=group['group_id'], session_type='group'
                        ).count()
                        if count > 1:
                            first = await PluginPermission.filter(
                                name=plugin.name, session_id=group['group_id'], session_type='group'
                            ).order_by('id').first()
                            await PluginPermission.filter(
                                name=plugin.name, session_id=group['group_id'], session_type='group'
                            ).delete()
                            await first.save()
                        elif count == 0:
                            await PluginPermission.create(name=plugin.name, session_id=group['group_id'],
                                                          session_type='group')
                if user_list:
                    for user in user_list:
                        count = await PluginPermission.filter(
                            name=plugin.name, session_id=user['user_id'], session_type='user'
                        ).count()
                        if count > 1:
                            first = await PluginPermission.filter(
                                name=plugin.name, session_id=user['user_id'], session_type='user'
                            ).order_by('id').first()
                            await PluginPermission.filter(
                                name=plugin.name, session_id=user['user_id'], session_type='user'
                            ).delete()
                            await first.save()
                        elif count == 0:
                            await PluginPermission.create(name=plugin.name, session_id=user['user_id'],
                                                          session_type='user')
            if plugin.name not in HIDDEN_PLUGINS:
                if plugin.name not in cls.plugins:
                    if metadata := plugin.metadata:
                        cls.plugins[plugin.name] = PluginInfo.parse_obj({
                            'name':        metadata.name,
                            'module_name': plugin.name,
                            'description': metadata.description,
                            'usage':       metadata.usage,
                            'show':        metadata.extra.get('show', True),
                            'priority':    metadata.extra.get('priority', 99),
                            'cooldown':    metadata.extra.get('cooldown')
                        })
                    else:
                        cls.plugins[plugin.name] = PluginInfo(name=plugin.name, module_name=plugin.name)
                matchers = plugin.matcher
                for matcher in matchers:
                    if matcher._default_state:
                        matcher_info = MatcherInfo.parse_obj(matcher._default_state)
                        if cls.plugins[plugin.name].matchers is not None and matcher_info.pm_name not in [m.pm_name for
                                                                                                          m
                                                                                                          in
                                                                                                          cls.plugins[
                                                                                                              plugin.name].matchers]:
                            cls.plugins[plugin.name].matchers.append(matcher_info)
        cls.save()
        logger.success('插件管理器', '<g>初始化完成</g>')

    @classmethod
    async def get_plugin_list(cls, message_type: str, session_id: int) -> List[PluginInfo]:
        """
        获取插件列表（供帮助图使用）
            :param message_type: 消息类型
            :param session_id: 消息ID
        """
        load_plugins = nb_plugin.get_loaded_plugins()
        load_plugins = [p.name for p in load_plugins]
        plugin_list = sorted(cls.plugins.values(), key=lambda x: x.priority).copy()
        plugin_list = [p for p in plugin_list if p.show and p.module_name in load_plugins]
        for plugin in plugin_list:
            if message_type != 'guild':
                plugin_info = await PluginPermission.get_or_none(name=plugin.module_name, session_id=session_id,
                                                                 session_type=message_type)
                plugin.status = True if plugin_info is None else plugin_info.status
            else:
                plugin.status = True
            if plugin.matchers:
                plugin.matchers.sort(key=lambda x: x.pm_priority)
                plugin.matchers = [m for m in plugin.matchers if m.pm_show and m.pm_usage]
        return plugin_list

    @classmethod
    async def get_plugin_list_for_admin(cls) -> List[dict]:
        """
        获取插件列表（供Web UI使用）
        """
        load_plugins = nb_plugin.get_loaded_plugins()
        load_plugins = [p.name for p in load_plugins]
        plugin_list = [p.dict(exclude={'status'}) for p in cls.plugins.values()]
        for plugin in plugin_list:
            plugin['matchers'].sort(key=lambda x: x['pm_priority'])
            plugin['isLoad'] = plugin['module_name'] in load_plugins
            plugin['status'] = await PluginPermission.filter(name=plugin['module_name'], status=True).exists()
        plugin_list.sort(key=lambda x: (x['isLoad'], x['status'], -x['priority']), reverse=True)
        return plugin_list


@DRIVER.on_bot_connect
async def _():
    await PluginManager.init()


@run_preprocessor
async def _(event: MessageEvent, matcher: Matcher):
    if event.user_id in SUPERUSERS:
        return
    if not matcher.plugin_name or matcher.plugin_name in HIDDEN_PLUGINS:
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
    perm = await PluginPermission.get_or_none(name=matcher.plugin_name, session_id=session_id,
                                              session_type=session_type)
    if not perm:
        await PluginPermission.create(name=matcher.plugin_name, session_id=session_id, session_type=session_type)
        return
    if not perm.status:
        raise IgnoredException('插件使用权限已禁用')
    if isinstance(event, GroupMessageEvent) and event.user_id in perm.ban:
        raise IgnoredException('用户被禁止使用该插件')

    # 命令调用统计
    if matcher.plugin_name in PluginManager.plugins and 'pm_name' in matcher.state:
        if matcher_info := list(filter(lambda x: x.pm_name == matcher.state['pm_name'],
                                       PluginManager.plugins[matcher.plugin_name].matchers)):
            matcher_info = matcher_info[0]
            await PluginStatistics.create(plugin_name=matcher.plugin_name,
                                          matcher_name=matcher_info.pm_name,
                                          matcher_usage=matcher_info.pm_usage,
                                          group_id=event.group_id if isinstance(event, GroupMessageEvent) else None,
                                          user_id=event.user_id,
                                          message_type=session_type,
                                          time=datetime.datetime.now())
