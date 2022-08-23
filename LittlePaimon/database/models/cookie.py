import datetime

from tortoise import fields
from tortoise.models import Model


class PublicCookie(Model):
    """
    米游社公共cookie
    """
    id: int = fields.IntField(pk=True, source_field='no', generated=True, auto_increment=True)
    """自增主键"""
    cookie: str = fields.TextField()
    """cookie内容"""
    status: int = fields.IntField(default=1)
    """cookie状态，0为疑似失效，1为可用，2为每日限制"""

    class Meta:
        table = 'public_cookie'
        table_description = '公共cookie池'


class PrivateCookie(Model):
    """
    米游社私人cookie
    """
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    user_id: str = fields.TextField()
    """用户id"""
    uid: str = fields.TextField()
    """原神uid"""
    mys_id: str = fields.TextField()
    """米游社id"""
    cookie: str = fields.TextField()
    """cookie内容"""
    stoken: str = fields.TextField(null=True)
    """stoken内容"""
    status: int = fields.IntField(default=1)
    """cookie状态，0为疑似失效，1为可用，2为每日限制"""

    class Meta:
        table = 'private_cookie'
        table_description = '私人cookie'


class LastQuery(Model):
    """
    上次查询的uid
    """
    user_id: str = fields.TextField(pk=True)
    """用户id"""
    uid: str = fields.TextField()
    """原神uid"""
    last_time: datetime.datetime = fields.DatetimeField()
    """上次查询的时间"""

    class Meta:
        table = 'last_query'
        table_description = '用户最后查询的uid'


class CookieCache(Model):
    """
    cookie使用缓存
    """
    uid: str = fields.TextField(pk=True)
    """原神uid"""
    cookie: str = fields.TextField()
    """cookie内容"""

    class Meta:
        table = 'cookie_cache'
        table_description = 'cookie缓存，每日0点清空'
