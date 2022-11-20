import datetime

from tortoise import fields
from tortoise.models import Model


class MysAuthKey(Model):
    id: int = fields.IntField(pk=True, generated=True, auto_increment=True)
    user_id: str = fields.TextField()
    """用户id"""
    uid: str = fields.TextField()
    """原神uid"""
    authkey: str = fields.TextField()
    """authkey"""
    generate_time: datetime.datetime = fields.DatetimeField(auto_now_add=True)
    """生成时间"""
