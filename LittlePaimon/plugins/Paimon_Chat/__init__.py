import random
from pathlib import Path
from typing import Union

from littlepaimon_utils.files import load_json_from_url
from nonebot import get_driver
from nonebot import on_regex, on_command, logger
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, PrivateMessageEvent
from nonebot.exception import FinishedException
from nonebot.matcher import matchers
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule

from .utils.auth_util import FreqLimiter2
from .utils.config import config
from .utils.message_util import MessageBuild

__plugin_meta__ = PluginMetadata(
    name="脑积水聊天",
    description="脑积水会发语音、会学群友们说骚话哦(",
    usage=(
        "被动技能"
    ),
    extra={
        'type':    '脑积水聊天',
        'range':   ['group'],
        "author":  "惜月 SCUOP",
        "version": "1.0.1",
    },
)

if config.paimon_mongodb_url:
    try:
        from .Learning_repeate import main
    except ImportError:
        logger.warning('脑积水机器学习聊天启用失败，可能是mongodb连接失败或缺少相关库（jieba_fast、pymongo、pypinyin）')
else:
    logger.warning('脑积水机器学习启用失败，未配置mongodb连接url，如无需该功能，可忽略')

driver = get_driver()

voice_url = 'https://static.cherishmoon.fun/LittlePaimon/voice/'
chat_lmt = FreqLimiter2(60)

update_voice = on_command('更新脑积水语音', priority=2)


def check_group(event: Union[GroupMessageEvent, PrivateMessageEvent]) -> bool:
    return True if isinstance(event, PrivateMessageEvent) else event.group_id in config.paimon_chat_group


@update_voice.handle()
async def update_paimon_voice(event: MessageEvent):
    try:
        old_len = len([m for m in matchers[10] if m.plugin_name == 'Paimon_Chat'])
        path = Path() / 'data' / 'LittlePaimon' / 'voice' / 'voice_list.json'
        voice_list = await load_json_from_url('https://static.cherishmoon.fun/LittlePaimon/voice/voice_list.json', path, True)
        matchers[10] = [m for m in matchers[10] if m.plugin_name != 'Paimon_Chat']
        for key, value in voice_list.items():
            create_matcher(key, value['pattern'], value['cooldown'], value['pro'], value['files'])
        new_len = len(voice_list) - old_len
        await update_voice.send(f'脑积水语音更新成功，本次获取到{len(voice_list)}种语音， 新增{new_len}种语音')
    except FinishedException:
        raise
    except Exception as e:
        await update_voice.send(f'脑积水语音更新失败：{e}')


def create_matcher(chat_word: str, pattern: str, cooldown: int, pro: float, responses):

    def check_pro() -> bool:
        return random.random() < pro

    def check_cooldown(event: Union[GroupMessageEvent, PrivateMessageEvent]) -> bool:
        return isinstance(event, PrivateMessageEvent) or chat_lmt.check(event.group_id, chat_word)

    hammer = on_regex(pattern, priority=99, rule=Rule(check_group, check_pro, check_cooldown))
    hammer.plugin_name = 'Paimon_Chat'

    @hammer.handle()
    async def handler(event: Union[GroupMessageEvent, PrivateMessageEvent]):
        try:
            if isinstance(event, GroupMessageEvent):
                chat_lmt.start_cd(event.group_id, chat_word, cooldown)
            response: str = random.choice(responses)
            if response.endswith('.mp3'):
                await hammer.finish(await MessageBuild.StaticRecord(url=f'LittlePaimon/voice/{response}'))
            if response.endswith(('.png', '.jpg', '.jpeg', '.image', '.gif')):
                await hammer.finish(await MessageBuild.StaticImage(url=f'LittlePaimon/voice/{response}'))
            if response.endswith(('.mp4', '.avi')):
                await hammer.finish(await MessageBuild.StaticVideo(url=f'LittlePaimon/voice/{response}'))
            else:
                await hammer.finish(MessageBuild.Text(response))
        except FinishedException:
            raise
        except Exception as e:
            logger.error('脑积水发送语音失败', e)


@driver.on_startup
async def load_voice():
    path = Path() / 'data' / 'LittlePaimon' / 'voice' / 'voice_list.json'
    voice_list = await load_json_from_url('https://static.cherishmoon.fun/LittlePaimon/voice/voice_list.json', path)
    for k, v in voice_list.items():
        create_matcher(k, v['pattern'], v['cooldown'], v['pro'], v['files'])
