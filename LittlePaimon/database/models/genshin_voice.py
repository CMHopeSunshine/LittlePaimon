import datetime

from tortoise import fields
from tortoise.models import Model


class GuessVoiceRank(Model):
    """
    猜语音排行榜
    """
    id: int = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增主键"""
    user_id: int = fields.IntField()
    """用户id"""
    group_id: int = fields.IntField()
    """群id"""
    answer: str = fields.CharField(max_length=255)
    """答案"""
    guess_time: datetime.datetime = fields.DatetimeField(default=datetime.datetime.now)
    """时间"""

    class Meta:
        table = 'guess_voice_rank'
        table_description = '猜语音排行榜'


class GenshinVoice(Model):
    """
    猜语音列表
    """
    id: int = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增主键"""
    character: str = fields.CharField(max_length=255)
    """角色名"""
    voice_name: str = fields.CharField(max_length=255)
    """语音名"""
    voice_content: str = fields.TextField()
    """语音内容"""
    voice_url: str = fields.TextField()
    """语音链接"""
    language: str = fields.CharField(max_length=255)
    """语言"""

    class Meta:
        table = 'voice_list'
        table_description = '语音列表'
