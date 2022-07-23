import datetime

from tortoise import fields
from tortoise.models import Model


class PublicCookie(Model):
    """
    米游社公共cookie
    字段：
    cid: int, 自增主键id
    cookie: str, cookie
    status: int, cookie状态
    0为疑似失效，1为可用，2为每日限制
    """
    cid: int = fields.IntField(pk=True, source_field='no', auto_increment=True, generated=True)
    cookie: str = fields.TextField()
    status: int = fields.IntField(default=1)

    class Meta:
        table = 'public_cookie'
        table_description = '公共cookie池'
        indexes = ('cid',)


class PrivateCookie(Model):
    """
    米游社私人cookie
    字段：
    user_id: str, 用户id
    uid: str, 原神uid
    mys_id: str, 米游社id
    cookie: str, cookie
    stoken: str, stoken
    status: int, cookie状态
    0为疑似失效，1为可用，2为每日限制
    """
    user_id: str = fields.TextField()
    uid: str = fields.TextField()
    mys_id: str = fields.TextField()
    cookie: str = fields.TextField()
    stoken: str = fields.TextField()
    status: int = fields.IntField(default=1)

    class Meta:
        table = 'private_cookie'
        table_description = '私人cookie'
        indexes = ('user_id', 'uid')


class LastQuery(Model):
    """
    上次查询的uid
    字段：
    user_id: str, 用户id
    uid: str, 原神uid
    last_time: datetime, 上次查询时间
    """
    user_id: str = fields.TextField(pk=True)
    uid: str = fields.TextField()
    last_time: datetime.datetime = fields.DatetimeField()

    class Meta:
        table = 'last_query'
        table_description = '用户最后查询的uid'
        indexes = ('user_id',)


class CookieCache(Model):
    """
    cookie使用缓存
    字段：
    uid: str, 原神uid
    cookie: str, cookie
    """
    uid: str = fields.TextField(pk=True)
    cookie: str = fields.TextField()

    class Meta:
        table = 'cookie_cache'
        table_description = 'cookie缓存，每日0点清空'
        indexes = ('uid',)
