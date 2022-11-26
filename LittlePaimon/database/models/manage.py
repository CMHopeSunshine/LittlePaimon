import datetime
from typing import List
from enum import Enum

from tortoise import fields
from tortoise.models import Model


class PluginPermission(Model):
    """将在N个版本后废弃"""
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    name: str = fields.TextField()
    """插件名称"""
    session_id: int = fields.IntField()
    """会话id"""
    session_type: str = fields.CharField(max_length=10, default='group')
    """会话类型，group/user"""
    status: bool = fields.BooleanField(default=True)
    """插件总开关"""
    ban: List[int] = fields.JSONField(default=[])
    """插件屏蔽列表"""
    statistics: dict = fields.JSONField(default=dict)
    """插件调用统计，废弃选项，不再使用"""

    class Meta:
        table = 'plugin_permission'


class PluginDisable(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    name: str = fields.TextField()
    """插件名称"""
    global_disable: bool = fields.BooleanField(default=False)
    """全局禁用"""
    user_id: int = fields.IntField(null=True)
    """用户id"""
    group_id: int = fields.IntField(null=True)
    """群组id"""

    class Meta:
        table = 'plugin_disable'


class PluginStatistics(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    plugin_name: str = fields.TextField()
    """插件名称"""
    matcher_name: str = fields.TextField()
    """命令名称"""
    matcher_usage: str = fields.TextField(null=True)
    """命令用法"""
    group_id: int = fields.IntField(null=True)
    """群id"""
    user_id: int = fields.IntField()
    """用户id"""
    message_type: str = fields.CharField(max_length=10)
    """消息类型，group/user"""
    time: datetime.datetime = fields.DatetimeField()
    """调用时间"""

    class Meta:
        table = 'plugin_statistics'


class AliasMode(Enum):
    prefix: str = '前缀'
    suffix: str = '后缀'
    full_match: str = '全匹配'


class CommandAlias(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    command: str = fields.TextField()
    """目标命令"""
    alias: str = fields.TextField()
    """命令别名"""
    mode: AliasMode = fields.CharEnumField(AliasMode, max_length=10)
    """别名模式"""
    is_regex: bool = fields.BooleanField(default=False)
    """是否为正则表达式"""
    is_reverse: bool = fields.BooleanField(default=False)
    """是否反转"""
    group_id: str = fields.CharField(max_length=30)
    """启用的群id，all为全局启用"""
    priority: int = fields.IntField(default=99)
    """优先级，数字越大优先级越高"""

    class Meta:
        table = 'command_alias'
