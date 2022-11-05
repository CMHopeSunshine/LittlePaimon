from pathlib import Path
from typing import Union

from nonebot.adapters.onebot.v11 import Message

from .path import JSON_DATA


class DFAFilter:
    """
    敏感词过滤
    参考 https://github.com/observerss/textfilter
    """
    def __init__(self):
        self.keyword_chains = {}
        self.delimit = '\x00'

    def add(self, keyword: str):
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path: Path):
        with path.open('r', encoding='utf-8') as f:
            for keyword in f:
                self.add(keyword.strip())

    def filter(self, message: str, repl: str = "*"):
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1

        return ''.join(ret)


text_filter = DFAFilter()
text_filter.parse(JSON_DATA / 'ban_word.txt')


def filter_msg(message: Union[Message, str], repl: str = "*"):
    """
    过滤违禁词
    :param message: 过滤的消息
    :param repl: 替换词
    """
    if isinstance(message, str):
        return text_filter.filter(message)
    elif isinstance(message, Message):
        for seg in message['text']:
            seg.data['text'] = text_filter.filter(seg.data.get('text', ''), repl)
        return message
