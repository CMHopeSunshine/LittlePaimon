import asyncio
from typing import Dict, List

from nonebot import plugin as nb_plugin
from nonebot import get_bot
from LittlePaimon.utils import logger
from LittlePaimon.config.path import PLUGIN_CONFIG, PAIMON_CONFIG
from LittlePaimon.utils.files import load_yaml, save_yaml
from LittlePaimon.database.models import PluginPermission
from .model import MatcherInfo, PluginInfo

hidden_plugins = [
    'LittlePaimon',
    'nonebot_plugin_apscheduler',
    'nonebot_plugin_gocqhttp',
    'nonebot_plugin_htmlrender',
    'plugin_manager',
    'admin'
]


class PluginManager:
    def __init__(self):
        self.plugin_config_path = PLUGIN_CONFIG
        self.config_path = PAIMON_CONFIG
        self.data: Dict[str, PluginInfo] = {}
        self.config: Dict[str, any] = {}
        self.load()

    def save(self):
        """
        保存数据
        """
        for name, plugin in self.data.items():
            save_yaml(plugin.dict(), self.plugin_config_path / f'{name}.yml')

    def load(self):
        """
        读取配置项以及插件数据
        """
        if self.config_path.exists():
            self.config = load_yaml(self.config_path)
        else:
            logger.warning('插件管理器', '<r>无法读取配置文件</r>，请检查是否已将<m>config/paimon_config_default.yml</m>复制为<m>config/paimon_config.yml</m>')
        for file in self.plugin_config_path.iterdir():
            if file.is_file() and file.name.endswith('.yml'):
                data = load_yaml(file)
                self.data[file.name.replace('.yml', '')] = PluginInfo.parse_obj(data)

    def get_config(self, config_name: str, default: any = None):
        """
        获取派蒙配置项
        :param config_name: 配置名
        :param default: 无配置时的默认值
        :return: 配置项
        """
        return self.config.get(config_name, default)

    def get_plugin_config(self, plugin_name: str, config_name: str, default: any = None):
        """
        获取派蒙插件配置项
        :param plugin_name：插件名
        :param config_name: 配置名
        :param default: 无配置时的默认值
        :return: 配置项
        """
        if plugin_name in self.data and self.data[plugin_name].configs:
            return self.data[plugin_name].configs.get(config_name, default)
        return default

    async def init_plugins(self):
        plugin_list = nb_plugin.get_loaded_plugins()
        group_list = await get_bot().get_group_list()
        user_list = await get_bot().get_friend_list()
        for plugin in plugin_list:
            if plugin.name not in hidden_plugins and not await PluginPermission.filter(name=plugin.name).exists():
                logger.info('插件管理器', f'新纳入插件<m>{plugin.name}</m>进行权限管理')
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
                            'configs':     metadata.extra.get('configs'),
                            'cooldown':    metadata.extra.get('cooldown')
                        })
                    else:
                        self.data[plugin.name] = PluginInfo(name=plugin.name, module_name=plugin.name)
                else:
                    if metadata and metadata.extra.get('configs'):
                        if self.data[plugin.name].configs:
                            for config in metadata.extra['configs']:
                                if config not in self.data[plugin.name].configs:
                                    self.data[plugin.name].configs[config] = metadata.extra['configs'][config]
                        else:
                            self.data[plugin.name].configs = metadata.extra['configs']
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
            if message_type == 'guild':
                plugin_info = await PluginPermission.get_or_none(name=plugin.module_name, session_id=session_id,
                                                                 session_type=message_type)
                plugin.status = True if plugin_info is None else plugin_info.status
            else:
                plugin.status = True
            if plugin.matchers:
                plugin.matchers.sort(key=lambda x: x.pm_priority)
                plugin.matchers = [m for m in plugin.matchers if m.pm_show and m.pm_usage]
        return plugin_list
