import asyncio
from typing import Dict, List

from nonebot import plugin as nb_plugin
from nonebot import get_bot
from LittlePaimon.utils import logger
from LittlePaimon.config.path import PLUGIN_CONFIG, PAIMON_CONFIG
from LittlePaimon.utils.files import load_yaml, save_yaml
from LittlePaimon.database.models import PluginPermission
from .model import MatcherInfo, PluginInfo, Config

hidden_plugins = [
    'LittlePaimon',
    'config',
    'nonebot_plugin_apscheduler',
    'nonebot_plugin_gocqhttp',
    'nonebot_plugin_htmlrender',
    'nonebot_plugin_imageutils',
    'plugin_manager',
    'database_manager',
    'admin',
    'NoticeAndRequest',
    'bot_manager'
]


class PluginManager:
    def __init__(self):
        self.plugin_config_path = PLUGIN_CONFIG
        self.config_path = PAIMON_CONFIG
        self.data: Dict[str, PluginInfo] = {}
        self.config: Config = Config()
        self.load()

    def save(self):
        """
        保存数据
        """
        save_yaml(self.config.dict(by_alias=True), self.config_path)
        for name, plugin in self.data.items():
            save_yaml(plugin.dict(), self.plugin_config_path / f'{name}.yml')

    def load(self):
        """
        读取配置项以及插件数据
        """
        if self.config_path.exists():
            self.config = Config.parse_obj(load_yaml(self.config_path))
        # else:
        #     logger.warning('插件管理器', '<r>无法读取配置文件</r>，请检查是否已将<m>config/paimon_config_default.yml</m>复制为<m>config/paimon_config.yml</m>')
        for file in self.plugin_config_path.iterdir():
            if file.is_file() and file.name.endswith('.yml'):
                data = load_yaml(file)
                self.data[file.name.replace('.yml', '')] = PluginInfo.parse_obj(data)

    def set_config(self, config_name: str, value: any):
        """
        设置派蒙配置项
        :param config_name: 配置名
        :param value: 新配置值
        """
        if config_name not in self.config.dict(by_alias=True).keys():
            return f'没有配置项为{config_name}'
        if '启用' in config_name or '开关' in config_name or config_name in {'自动接受好友请求', '自动接受群邀请'}:
            if value not in ['开', '关', 'true', 'false', 'on', 'off']:
                return '参数错误'
            value = value in ['开', 'true', 'on']
        elif config_name != 'CookieWeb地址' and not value.isdigit():
            return '配置项不合法，必须为数字'
        temp = self.config.dict(by_alias=True)
        temp[config_name] = value
        self.config = Config.parse_obj(temp)
        self.save()
        return f'成功设置{config_name}为{value}'

    async def init_plugins(self):
        plugin_list = nb_plugin.get_loaded_plugins()
        group_list = await get_bot().get_group_list()
        user_list = await get_bot().get_friend_list()
        for plugin in plugin_list:
            if plugin.name not in hidden_plugins:
                await asyncio.gather(*[PluginPermission.update_or_create(name=plugin.name, session_id=group['group_id'],
                                                                         session_type='group') for group in group_list])
                await asyncio.gather(*[PluginPermission.update_or_create(name=plugin.name, session_id=user['user_id'],
                                                                         session_type='user') for user in user_list])
            if plugin.name not in hidden_plugins:
                metadata = plugin.metadata
                if plugin.name not in self.data:
                    if metadata:
                        self.data[plugin.name] = PluginInfo.parse_obj({
                            'name':        metadata.name,
                            'module_name': plugin.name,
                            'description': metadata.description,
                            'usage':       metadata.usage,
                            'show':        metadata.extra.get('show', True),
                            'priority':    metadata.extra.get('priority', 99),
                            'cooldown':    metadata.extra.get('cooldown')
                        })
                    else:
                        self.data[plugin.name] = PluginInfo(name=plugin.name, module_name=plugin.name)
                matchers = plugin.matcher
                for matcher in matchers:
                    if matcher._default_state:
                        matcher_info = MatcherInfo.parse_obj(matcher._default_state)
                        if matcher_info.pm_name not in [m.pm_name for m in self.data[plugin.name].matchers]:
                            self.data[plugin.name].matchers.append(matcher_info)
        self.save()
        logger.success('插件管理器', '<g>初始化完成</g>')

    async def get_plugin_list(self, message_type: str, session_id: int) -> List[PluginInfo]:
        load_plugins = nb_plugin.get_loaded_plugins()
        load_plugins = [p.name for p in load_plugins]
        plugin_list = sorted(self.data.values(), key=lambda x: x.priority).copy()
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
