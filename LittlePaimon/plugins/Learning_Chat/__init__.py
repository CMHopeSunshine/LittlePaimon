import asyncio
import random
import time

from nonebot import on_message, get_bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, GROUP, Message, ActionFailed
from nonebot.params import Arg
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule
from nonebot.typing import T_State

from LittlePaimon.utils import scheduler, logger, NICKNAME
from .handler import LearningChat
from .models import ChatMessage
from .config import config_manager
from . import web_api, web_page

__plugin_meta__ = PluginMetadata(
    name="群聊学习",
    description="群聊学习",
    usage="群聊学习",
    extra={
        "author": "惜月",
        "priority": 16,
    },
)


async def ChatRule(event: GroupMessageEvent, state: T_State) -> bool:
    if answers := await LearningChat(event).answer():
        state["answers"] = answers
        return True
    return False


learning_chat = on_message(
    priority=99,
    block=False,
    rule=Rule(ChatRule),
    permission=GROUP,
    state={
        "pm_name": "群聊学习",
        "pm_description": "(被动技能)bot会学习群友们的发言",
        "pm_usage": "群聊学习",
        "pm_priority": 1,
    },
)


@learning_chat.handle()
async def _(event: GroupMessageEvent, answers=Arg("answers")):
    for answer in answers:
        try:
            logger.info(
                "群聊学习", f'{NICKNAME}将向群<m>{event.group_id}</m>回复<m>"{answer}"</m>'
            )
            msg = await learning_chat.send(Message(answer))
            await ChatMessage.create(
                group_id=event.group_id,
                user_id=event.self_id,
                message_id=msg["message_id"],
                message=answer,
                raw_message=answer,
                time=int(time.time()),
                plain_text=Message(answer).extract_plain_text(),
            )
            await asyncio.sleep(random.random() + 0.5)
        except ActionFailed:
            logger.info(
                "群聊学习",
                f'{NICKNAME}向群<m>{event.group_id}</m>的回复<m>"{answer}"</m>发送<r>失败，可能处于风控中</r>',
            )


@scheduler.scheduled_job("interval", minutes=3, misfire_grace_time=5)
async def speak_up():
    if not config_manager.config.total_enable:
        return
    try:
        bot = get_bot()
    except ValueError:
        return
    if not (speak := await LearningChat.speak(int(bot.self_id))):
        return
    group_id, messages = speak
    for msg in messages:
        try:
            logger.info("群聊学习", f'{NICKNAME}向群<m>{group_id}</m>主动发言<m>"{msg}"</m>')
            send_result = await bot.send_group_msg(
                group_id=group_id, message=Message(msg)
            )
            await ChatMessage.create(
                group_id=group_id,
                user_id=int(bot.self_id),
                message_id=send_result["message_id"],
                message=msg,
                raw_message=msg,
                time=int(time.time()),
                plain_text=Message(msg).extract_plain_text(),
            )
            await asyncio.sleep(random.randint(2, 4))
        except ActionFailed:
            logger.info(
                "群聊学习",
                f'{NICKNAME}向群<m>{group_id}</m>主动发言<m>"{msg}"</m><r>发送失败，可能处于风控中</r>',
            )
