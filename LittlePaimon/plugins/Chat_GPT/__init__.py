import requests
from typing import Union
from nonebot import on_command
from nonebot.exception import FinishedException
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, PrivateMessageEvent
from nonebot.params import CommandArg
from nonebot.rule import to_me

from LittlePaimon.plugins.Chat_GPT.api_request import get_completions
from LittlePaimon.utils.message import CommandCharacter, CommandLang, MessageBuild


__plugin_meta__ = PluginMetadata(
    name='ChatGPT聊天',
    description='ChatGPT聊天',
    usage='@Bot chat [聊天内容]',
    extra={
        'author': 'meatjam',
        'version': '1.0',
        'priority': 11,
        # 'configs': {
        #     '签到开始小时': 0,
        #     '签到开始分钟': 5,
        #     '米游币开始小时': 0,
        #     '米游币开始分钟': 30
        # }
    }
)

chat_gpt = on_command('chat', priority=8, block=True, rule=to_me(), state={
    'pm_name': 'ChatGPT聊天',
    'pm_description': 'ChatGPT聊天',
    'pm_usage': '@Bot chat [聊天内容]',
    'pm_priority': 3
})

is_thinking = False


@chat_gpt.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent], msg: Message = CommandArg()):
    global is_thinking
    if not event.to_me:
        return
    if is_thinking:
        await chat_gpt.finish('正在思考中......（一次只能一条哦，请等待回复后再发送。）')
        return
    msg = msg.extract_plain_text().strip()
    is_thinking = True
    try:
        await chat_gpt.finish(get_completions(msg))
    except FinishedException:
        pass
    except Exception as e:
        await chat_gpt.finish(f'出错了，请稍后重试。{e}')
    finally:
        is_thinking = False
