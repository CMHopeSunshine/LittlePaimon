import os
import random
from pathlib import Path

from nonebot import on_regex, logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.exception import FinishedException

from utils.config import config
from utils.auth_util import FreqLimiter2
from .chat_list import chat_list

res_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'res', 'voice')
chat_lmt = FreqLimiter2(60)


def create_matcher(chat_word: str, pattern: str, cooldown: int, pro: float, responses):
    hammer = on_regex(pattern, priority=10)

    @hammer.handle()
    async def handler(event: GroupMessageEvent):
        if event.group_id not in config.paimon_chat_group:
            return
        if not chat_lmt.check(event.group_id, chat_word):
            return
        else:
            if not random.random() < pro:
                return
            else:
                try:
                    chat_lmt.start_cd(event.group_id, chat_word, cooldown)
                    response = random.choice(responses)
                    if '.mp3' not in response:
                        await hammer.finish(response)
                    else:
                        await hammer.finish(MessageSegment.record(file=Path(os.path.join(res_path, response))))
                except FinishedException:
                    raise
                except Exception as e:
                    logger.error('派蒙发送语音失败', e)


for k, v in chat_list.items():
    create_matcher(k, v['pattern'], v['cooldown'], v['pro'], v['files'])


