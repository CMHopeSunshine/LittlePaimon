from tortoise import fields
from tortoise.models import Model


class UserInfo(Model):
    """用户表"""
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    group_id: int = fields.IntField()
    """所属群号"""
    user_id: int = fields.IntField()
    """用户id"""
    nickname: str = fields.CharField(max_length=255)
    """自称昵称"""
    friendly: float = fields.FloatField(default=0)
    """好感度"""
    plugin_status: dict = fields.JSONField()
    """插件可用情况"""


class GroupInfo(Model):
    """群表"""
    group_id = fields.IntField(pk=True)
    """群号"""
    plugin_status: dict = fields.JSONField()
    """插件可用情况"""


class PluginInfo(Model):
    plugin_name: str = fields.CharField(pk=True, max_length=255)
