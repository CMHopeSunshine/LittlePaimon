from tortoise import fields
from tortoise.models import Model
import datetime


class DailyNoteSub(Model):
    """
    原神实时便签提醒订阅
    """
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    user_id: int = fields.IntField()
    """用户id"""
    uid: str = fields.CharField(max_length=9)
    """原神uid"""
    remind_type: str = fields.CharField(max_length=255)
    """提醒类型(群/私聊)"""
    group_id: int = fields.IntField(null=True)
    """提醒所在的群号"""
    resin_num: int = fields.IntField(null=True)
    """需提醒的树脂数量"""
    coin_num: int = fields.IntField(null=True)
    """需提醒的银币数量"""
    last_remind_time: datetime.datetime = fields.DatetimeField(null=True)
    """上次提醒时间"""
    today_remind_num: int = fields.IntField(default=0)
    """今日已提醒次数"""

    class Meta:
        table = 'daily_note_sub'
        table_description = '原神实时便签提醒订阅'


class MihoyoBBSSub(Model):
    """
    米游社原神签到和米游币获取订阅
    """
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    user_id: int = fields.IntField()
    """用户id"""
    uid: str = fields.CharField(max_length=9)
    """原神uid"""
    group_id: int = fields.IntField(null=True)
    """订阅所在的群号(如果和user_id一致则为私聊)"""
    sub_event: str = fields.CharField(max_length=255)
    """订阅的事件类型"""

    class Meta:
        table = 'mhy_bbs_sub'
        table_description = '米游社订阅'


class MihoyoBBSPostSub(Model):
    """
    米游社用户帖子订阅
    """
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    mys_id: str = fields.CharField(max_length=255)
    """订阅的米游社用户id"""
    session_id: str = fields.CharField(max_length=255)
    """订阅者的qq号或群号"""
    session_type: str = fields.CharField(max_length=255, default='private')
    """订阅者的群号"""
    last_post_id: str = fields.CharField(max_length=255, null=True)
    """上次推送的帖子id"""

    class Meta:
        table = 'mhy_bbs_user_sub'
        table_description = '米游社用户帖子订阅'


class CloudGenshinSub(Model):
    """
    云原神
    """
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    user_id: str = fields.CharField(max_length=255)
    """用户id"""
    uid: str = fields.CharField(max_length=255)
    """原神uid"""
    group_id: int = fields.IntField(null=True)
    """订阅所在的群号(如果和user_id一致则为私聊)"""
    uuid: str = fields.CharField(max_length=255)
    """uuid"""
    token: str = fields.CharField(max_length=255)
    """token"""

    class Meta:
        table = 'cloud_genshin_sub'
        table_description = '云原神订阅'


class GeneralSub(Model):
    """
    群通用类订阅
    """
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    sub_id: int = fields.IntField()
    """订阅的群号或私聊号"""
    extra_id: int = fields.IntField(null=True)
    """额外的id，如频道的子频道id"""
    sub_type: str = fields.CharField(max_length=255)
    """订阅类型(群/私聊/频道)"""
    sub_event: str = fields.CharField(max_length=255)
    """订阅的事件类型"""
    sub_hour: int = fields.IntField()
    """订阅的小时"""
    sub_minute: int = fields.IntField()
    """订阅的分钟"""

    class Meta:
        table = 'general_sub'
        table_description = '通用订阅'





