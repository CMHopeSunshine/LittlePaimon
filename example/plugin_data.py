from nonebot import on_command
from nonebot.plugin import PluginMetadata

"""
一个插件配置例子，不是最终版本，可能会有更多的变动
"""

__plugin_meta__ = PluginMetadata(
    name='test plugin',
    description='a test plugin',
    usage='only test',
    extra={
        'author': '惜月',
        'type': '其他',
        'default_status': True,
        'priority': 1,
        'permit_range': ['private', 'group', 'guild'],
        'permit_member': ['superuser', 'admin', 'member'],
        'configs': {
            'config1': {
                'description': 'config1 description',
                'value': 1
            },
            'config2': {
                'description': 'config2 description',
                'value': 123
            }
        },
    }
)

command = on_command('example', priority=1, block=True)
command.__paimon_meta__ = {
    'name': 'test command',
    'description': 'a test command',
    'usage': 'only test',
    'default_status': True,
    'priority': 1,
    'cooldown': {
        'per_user': 1,
        'per_private_user': 1,
        'per_group': 1,
        'per_group_member': 2,
        'per_guild': 5,
        'per_guild_channel': 6,
        'per_guild_member': 7
    },
    'permit_range':  ['private', 'group', 'guild'],
    'permit_member': ['superuser', 'admin', 'member']
}

