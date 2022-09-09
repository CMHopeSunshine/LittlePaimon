from typing import List

from pydantic import BaseModel, Field

from LittlePaimon.config import LEARNING_CHAT_CONFIG
from LittlePaimon.utils.files import load_yaml, save_yaml


class ChatConfig(BaseModel):
    total_enable: bool = Field(True, alias='群聊学习总开关')
    ban_words: List[str] = Field([], alias='屏蔽词')
    ban_groups: List[int] = Field([], alias='屏蔽群')
    ban_users: List[int] = Field([], alias='屏蔽用户')
    KEYWORDS_SIZE: int = Field(3, alias='单句关键词分词数量')
    answer_threshold: int = Field(4, alias='发言阈值')
    answer_threshold_weights: List[int] = Field([10, 30, 60], alias='发言阈值权重')
    cross_group_threshold: int = Field(2, alias='跨群回复阈值')
    repeat_threshold: int = Field(3, alias='复读阈值')
    speak_threshold: int = Field(5, alias='主动发言阈值')
    split_probability: float = Field(0.5, alias='按逗号分割回复概率')
    voice_probability: float = Field(0.1, alias='以语音回复概率')
    speak_continuously_probability: float = Field(0.5, alias='连续主动发言概率')
    speak_poke_probability: float = Field(0.5, alias='主动发言附带戳一戳概率')
    speak_continuously_max_len: int = Field(3, alias='最大连续说话句数')
    save_time_threshold: int = Field(3600, alias='持久化间隔秒数')
    save_count_threshold: int = Field(1000, alias='持久化间隔条数')


class ChatConfigManager:

    def __init__(self):
        self.file_path = LEARNING_CHAT_CONFIG
        if self.file_path.exists():
            self.config = ChatConfig.parse_obj(load_yaml(self.file_path))
        else:
            self.config = ChatConfig()
        self.save()

    @property
    def config_list(self) -> List[str]:
        return list(self.config.dict(by_alias=True).keys())

    def save(self):
        save_yaml(self.config.dict(by_alias=True), self.file_path)

    # def set_config(self, config_name: str, value: any):
    #     if config_name not in self.config.dict(by_alias=True).keys():


config_manager = ChatConfigManager()
