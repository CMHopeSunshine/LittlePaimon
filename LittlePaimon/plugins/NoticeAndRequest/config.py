from typing import Dict, Union
from LittlePaimon.utils.path import GREET_CONFIG, GREET_CONFIG_DEFAULT
from LittlePaimon.utils.files import load_yaml, save_yaml


class GreetConfig:
    def __init__(self):
        if GREET_CONFIG.exists():
            data = load_yaml(GREET_CONFIG)
        elif GREET_CONFIG_DEFAULT.exists():
            data = load_yaml(GREET_CONFIG_DEFAULT)
        else:
            data = {}
        self.new_friend: str = data.get('新好友见面语', '旅行者你好呀，这里是{nickname}，对我说“help”查看帮助吧~')
        self.new_group: str = data.get('新群见面语', '旅行者们大家好呀，这里是{nickname}，对我说“help”查看帮助吧~')
        self.group_greet: Dict[Union[str, int], str] = data.get('群新人欢迎语', {'默认': '欢迎新旅行者~{at_user}'})
        self.group_ban = data.get('群欢迎语禁用列表', [])
        self.save()

    def save(self):
        data = {
            '新好友见面语': self.new_friend,
            '新群见面语': self.new_group,
            '群新人欢迎语': self.group_greet,
            '群欢迎语禁用列表': self.group_ban
        }
        save_yaml(data, GREET_CONFIG)


config = GreetConfig()
