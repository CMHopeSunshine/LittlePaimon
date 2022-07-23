from nonebot import plugin as nb_plugin
from nonebot.plugin import Plugin
from nonebot import logger
from LittlePaimon.config.path import PLUGINMANAGER
from LittlePaimon.utils.files import load_yaml, save_yaml
from typing import Dict
from ruamel import yaml

# class PaimonMatcherData(BaseModel):
#     introduce: str
#     usage: str
#     status: bool = True
#     show_priority: int = 1
#     permit_range: List[Literal['private', 'public', 'guild']] = ['private', 'public', 'guild']
#     permit_member: List[Literal['superuser', 'admin', 'member']] = ['superuser', 'admin', 'member']
#     ban: List[int] = []
#     cooldown: int = 0
#
#
# class PaimonPluginData(BaseModel):
#     plugin_name: str
#     plugin_describe: str
#     plugin_type: str
#     plugin_usage: str
#     status: bool = True
#     show_priority: int = 99
#     permit_range: List[Literal['private', 'public', 'guild']] = ['private', 'public', 'guild']
#     permit_member: List[Literal['superuser', 'admin', 'member']] = ['superuser', 'admin', 'member']
#     ban: List[int] = []
#     cooldown: int = 0
#     matchers: List[dict] = []

hidden_plugins = [
    'LittlePaimon',
    'nonebot_plugin_apscheduler',
    'nonebot_plugin_gocqhttp',
    'nonebot_plugin_htmlrender'
]


class PluginManager:

    def __init__(self):
        self.file_path = PLUGINMANAGER
        self.data = load_yaml(self.file_path)

    def save(self):
        self.data.yaml_add_eol_comment('配置文件说明详见https://github.com/CMHopeSunshine/LittlePaimon', column=1)
        save_yaml(self.data, self.file_path)

    def init_plugins(self):
        plugin_list = nb_plugin.get_loaded_plugins()
        for plugin in plugin_list:
            if plugin.name not in self.data and plugin.name not in hidden_plugins:
                self.add_plugin(plugin)
        self.save()
        logger.opt(colors=True).success(f"<y>插件管理器初始化</y><r>成功</r>")

    def add_plugin(self, plugin: Plugin):
        name = plugin.name
        metadata = plugin.metadata
        if metadata:
            self.data[name] = {
                'name':          name,
                'type':          metadata.extra.get('type', '其他'),
                'description':   metadata.description,
                'usage':         metadata.usage,
                'author':        metadata.extra.get('author', '佚名'),
                'version':       metadata.extra.get('version', '未知'),
                'priority':      metadata.extra.get('priority', 99),
                'permit_range':  metadata.extra.get('permit_range', ['private', 'group', 'guild']),
                'permit_member': metadata.extra.get('permit_member', ['superuser', 'admin', 'member']),
                'status':        {
                    'group':   {
                        'enable':    metadata.extra.get('default_status', True),
                        'blacklist': [],
                        'whitelist': []
                    },
                    'private': {
                        'enable':    metadata.extra.get('default_status', True),
                        'blacklist': [],
                        'whitelist': []
                    },
                    'guild_member':   {
                        'enable':    metadata.extra.get('default_status', True),
                        'blacklist': [],
                        'whitelist': []
                    },
                    'guild_channel': {
                        'enable':    metadata.extra.get('default_status', True),
                        'blacklist': [],
                        'whitelist': []
                    },
                },
                'configs':       metadata.extra.get('config', {}),
                'commands':      {}
            }
        else:
            self.data[name] = {
                'name':          name,
                'type':          '其他',
                'description':   '',
                'usage':         '',
                'author':        '佚名',
                'priority':      99,
                'permit_range':  ['private', 'group', 'guild'],
                'permit_member': ['superuser', 'admin', 'member'],
                'status':        {
                    'group':   {
                        'enable':    True,
                        'blacklist': [],
                        'whitelist': []
                    },
                    'private': {
                        'enable':    True,
                        'blacklist': [],
                        'whitelist': []
                    },
                    'guild_member':   {
                        'enable':    True,
                        'blacklist': [],
                        'whitelist': []
                    },
                    'guild_channel': {
                        'enable':    True,
                        'blacklist': [],
                        'whitelist': []
                    },
                },
                'configs':       {},
                'commands':      {}
            }
        matchers = plugin.matcher
        for matcher in matchers:
            try:
                matcher_data: dict = matcher.__paimon_meta__
                if 'name' not in matcher_data:
                    raise ValueError(f'插件{name}的命令未写命令名')
                self.data[name]['commands'][matcher_data['name']] = {
                        'description':   matcher_data.get('matcher_data', ''),
                        'usage':         matcher_data.get('usage', ''),
                        'priority':      matcher_data.get('priority', 99),
                        'permit_range':  matcher_data.get('permit_range', ['private', 'group', 'guild']),
                        'permit_member': matcher_data.get('permit_member', ['superuser', 'admin', 'member']),
                        'cooldown':      {},
                        'status':        {
                            'group':   {
                                'enable':    True,
                                'blacklist': [],
                                'whitelist': []
                            },
                            'private': {
                                'enable':    True,
                                'blacklist': [],
                                'whitelist': []
                            },
                            'guild_member':   {
                                'enable':    True,
                                'blacklist': [],
                                'whitelist': []
                            },
                            'guild_channel': {
                                'enable':    True,
                                'blacklist': [],
                                'whitelist': []
                            },
                        },
                    }
            except AttributeError:
                pass

    def get_config(self, plugin_name: str, config_name: str, default: any = None):
        """
        获取插件指定配置值
        :param plugin_name: 插件名
        :param config_name: 配置名
        :param default: 未找到配置值时的默认值
        :return: 配置值
        """
        if plugin_name in self.data:
            if config_name in self.data[plugin_name]['configs']:
                return self.data[plugin_name]['configs'][config_name]['value']
        return default

    def get_enable(self,
                   plugin_name: str,
                   matcher_name: str,
                   target_type: str,
                   target_id: str,
                   channel_id: str = None) -> bool:
        if plugin_name in self.data:
            if target_type in ['group', 'private']:
                status = self.data[plugin_name]['status'][target_type]
                if (status['enable'] and target_id in status['blacklist']) or (not status['enable'] and target_id in status['whitelist']):
                    return False
                elif matcher_name in self.data[plugin_name]['commands']:
                    status = self.data[plugin_name]['commands']['status'][target_type]
                    return (status['enable'] and target_id not in status['blacklist']) or (not status['enable'] and target_id not in status['whitelist'])
                else:
                    return True
            elif target_type == 'guild':
                status_channel = self.data[plugin_name]['status']['guild_channel']
                if (status_channel['enable'] and channel_id in status_channel['blacklist']) or (
                        not status_channel['enable'] and channel_id in status_channel['whitelist']):
                    return False
                else:
                    status_member = self.data[plugin_name]['status']['guild_member']
                    if (status_member['enable'] and target_id in status_member['blacklist']) or (
                            not status_member['enable'] and target_id in status_member['whitelist']):
                        return False
                    elif matcher_name in self.data[plugin_name]['commands']:
                        status_channel = self.data[plugin_name]['commands']['status']['guild_channel']
                        if (status_channel['enable'] and channel_id in status_channel['blacklist']) or (
                                not status_channel['enable'] and channel_id in status_channel['whitelist']
                        ):
                            return False
                        else:
                            status_member = self.data[plugin_name]['commands']['status']['guild_member']
                            return (status_member['enable'] and target_id not in status_member['blacklist']) or (
                                    not status_member['enable'] and target_id not in status_member['whitelist'])
                    else:
                        return True
            else:
                return True
        else:
            return True

