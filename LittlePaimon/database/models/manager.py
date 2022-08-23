from typing import List

from tortoise import fields
from tortoise.models import Model

from LittlePaimon.config.models import Statistics


class PluginPermission(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    name: str = fields.CharField(max_length=255)
    """插件名称"""
    session_id: int = fields.IntField()
    """会话id"""
    session_type: str = fields.CharField(max_length=10, default='group')
    """会话类型，group/user"""
    status: bool = fields.BooleanField(default=True)
    """插件总开关"""
    ban: List[int] = fields.JSONField(default=[])
    """插件屏蔽列表"""
    statistics: Statistics = fields.JSONField(encoder=Statistics.json, decoder=Statistics.parse_raw, default=Statistics())
    """插件调用统计"""

    class Meta:
        table = 'plugin_permission'

