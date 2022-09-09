import time
from typing import List, Optional, Iterator
from pydantic import BaseModel

try:
    import ujson as json
except ImportError:
    import json

from tortoise import fields
from tortoise.models import Model


class BanWord(BaseModel):
    keywords: str
    group_id: int
    reason: Optional[str]
    time: Optional[int]


class BanWords(BaseModel):
    bans: List[BanWord] = []

    def __len__(self):
        return len(self.bans)

    def __getitem__(self, item):
        return self.bans[item]

    def __setitem__(self, key, value):
        self.bans[key] = value

    def __delitem__(self, key):
        del self.bans[key]

    def __iter__(self) -> Iterator[BanWord]:
        return iter(self.bans)

    def __reversed__(self):
        return reversed(self.bans)

    def append(self, ban: BanWord):
        self.bans.append(ban)

    def index(self, ban: BanWord) -> int:
        return self.bans.index(ban)



    # @staticmethod
    # def tortoise_decoder(text: str) -> List["BanWord"]:
    #     print('ban_decoder：', text)
    #     return [BanWord.parse_obj(item) for item in json.loads(text)]
    #
    # @staticmethod
    # def tortoise_encoder(models: List["BanWord"]) -> str:
    #     print('ban_encoder：', models)
    #     if not models:
    #         return ''
    #     elif isinstance(models[0], BanWord):
    #         return json.dumps([model.dict() for model in models])


class Answer(BaseModel):
    keywords: str
    group_id: int
    count: int
    time: int
    messages: List[str]

    # @staticmethod
    # def tortoise_decoder(text: str) -> List["Answer"]:
    #     print('answer_decoder：', text)
    #     return [Answer.parse_obj(item) for item in json.loads(text)]
    #
    # @staticmethod
    # def tortoise_encoder(models: List["Answer"]) -> str:
    #     print('answer_encoder：', models)
    #     if not models:
    #         return ''
    #     elif isinstance(models[0], BanWord):
    #         return json.dumps([model.dict() for model in models])


class Answers(BaseModel):
    answers: List[Answer] = []

    def __len__(self):
        return len(self.answers)

    def __getitem__(self, item):
        return self.answers[item]

    def __setitem__(self, key, value):
        self.answers[key] = value

    def __delitem__(self, key):
        del self.answers[key]

    def __iter__(self) -> Iterator[Answer]:
        return iter(self.answers)

    def __reversed__(self):
        return reversed(self.answers)

    def append(self, answer: Answer):
        self.answers.append(answer)

    def index(self, answer: Answer) -> int:
        return self.answers.index(answer)


class Message(Model):
    id: int = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增主键"""
    group_id: int = fields.IntField()
    """群id"""
    user_id: int = fields.IntField()
    """用户id"""
    raw_message: str = fields.TextField()
    """原始消息"""
    is_plain_text: bool = fields.BooleanField()
    """是否为纯文本"""
    plain_text: str = fields.TextField()
    """纯文本"""
    keywords: str = fields.TextField()
    """关键词"""
    time: int = fields.IntField()
    """时间戳"""

    class Meta:
        table = 'Message'
        indexes = ('time',)
        ordering = ['-time']


class Context(Model):
    id: int = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增主键"""
    keywords: str = fields.TextField()
    """关键词"""
    time: int = fields.IntField(default=int(time.time()))
    """时间戳"""
    count: int = fields.IntField(default=1)
    """次数"""
    answers: Answers = fields.JSONField(encoder=Answers.json, decoder=Answers.parse_raw, default=Answers())
    """答案列表"""
    clear_time: Optional[int] = fields.IntField(null=True)
    """清除时间戳"""
    ban: BanWords = fields.JSONField(encoder=BanWords.json, decoder=BanWords.parse_raw, default=BanWords())
    """禁用词列表"""

    class Meta:
        table = 'Context'
        indexes = ('keywords', 'count', 'time')
        ordering = ['-time', '-count']


class BlackList(Model):
    id: int = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增主键"""
    group_id: int = fields.IntField()
    """群id"""
    answers: List[str] = fields.JSONField(default=[])
    """答案"""
    answers_reserve: List[str] = fields.JSONField(default=[])
    """备用答案"""

    class Meta:
        table = 'BlackList'
        indexes = ('group_id',)
