from typing import List, Dict

from pydantic import BaseModel, Field

from LittlePaimon.utils.path import LEARNING_CHAT_CONFIG
from LittlePaimon.utils.files import load_yaml, save_yaml


class ChatGroupConfig(BaseModel):
    enable: bool = Field(default=True, alias="群聊学习开关")
    ban_words: List[str] = Field(default_factory=list, alias="屏蔽词")
    ban_users: List[int] = Field(default_factory=list, alias="屏蔽用户")
    answer_threshold: int = Field(default=4, alias="回复阈值")
    answer_threshold_weights: List[int] = Field(default=[10, 30, 60], alias="回复阈值权重")
    repeat_threshold: int = Field(default=3, alias="复读阈值")
    break_probability: float = Field(default=0.25, alias="打断复读概率")
    speak_enable: bool = Field(default=True, alias="主动发言开关")
    speak_threshold: int = Field(default=5, alias="主动发言阈值")
    speak_min_interval: int = Field(default=300, alias="主动发言最小间隔")
    speak_continuously_probability: float = Field(default=0.5, alias="连续主动发言概率")
    speak_continuously_max_len: int = Field(default=3, alias="最大连续主动发言句数")
    speak_poke_probability: float = Field(default=0.5, alias="主动发言附带戳一戳概率")

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__fields__:
                self.__setattr__(key, value)


class ChatConfig(BaseModel):
    total_enable: bool = Field(default=True, alias="群聊学习总开关")
    ban_words: List[str] = Field(default_factory=list, alias="全局屏蔽词")
    ban_users: List[int] = Field(default_factory=list, alias="全局屏蔽用户")
    KEYWORDS_SIZE: int = Field(default=3, alias="单句关键词分词数量")
    cross_group_threshold: int = Field(default=3, alias="跨群回复阈值")
    learn_max_count: int = Field(default=6, alias="最高学习次数")
    dictionary: List[str] = Field(default_factory=list, alias="自定义词典")
    group_config: Dict[int, ChatGroupConfig] = Field(default_factory=dict, alias="分群配置")

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__fields__:
                self.__setattr__(key, value)


class ChatConfigManager:
    def __init__(self):
        self.file_path = LEARNING_CHAT_CONFIG
        if self.file_path.exists():
            self.config = ChatConfig.parse_obj(load_yaml(self.file_path))
        else:
            self.config = ChatConfig()
        self.save()

    def get_group_config(self, group_id: int) -> ChatGroupConfig:
        if group_id not in self.config.group_config:
            self.config.group_config[group_id] = ChatGroupConfig()
            self.save()
        return self.config.group_config[group_id]

    @property
    def config_list(self) -> List[str]:
        return list(self.config.dict(by_alias=True).keys())

    def save(self):
        save_yaml(self.config.dict(by_alias=True), self.file_path)


config_manager = ChatConfigManager()
