import random
import asyncio
import re
import time
import os
import threading

from nonebot import on_message, require, get_bot, logger
from nonebot.exception import ActionFailed
from nonebot.typing import T_State
from nonebot.rule import keyword, to_me, Rule
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from nonebot.adapters.onebot.v11 import permission

from .model import Chat
from utils.config import config

message_id_lock = threading.Lock()
message_id_dict = {}


async def check_accounts(event: GroupMessageEvent) -> bool:
    # 不响应其他nonebot_plugin_gocqhttp机器人账号的信息
    if os.path.exists('accounts'):
        accounts = [int(d) for d in os.listdir('accounts')
                    if d.isnumeric()]
        if event.user_id in accounts:
            return False
    return True


async def get_answer(event: GroupMessageEvent, state: T_State) -> bool:
    # 不响应被屏蔽的人的信息
    if event.user_id in config.paimon_chat_ban:
        return False
    chat: Chat = Chat(event)
    to_learn = True
    # 多账号登陆，且在同一群中时；避免一条消息被处理多次
    with message_id_lock:
        message_id = event.message_id
        group_id = event.group_id
        if group_id in message_id_dict:
            if message_id in message_id_dict[group_id]:
                to_learn = False
        else:
            message_id_dict[group_id] = []

        group_message = message_id_dict[group_id]
        group_message.append(message_id)
        if len(group_message) > 100:
            group_message = group_message[:-10]
    answers = chat.answer()
    if to_learn:
        chat.learn()

    if answers:
        state['answers'] = answers
        return True
    return False


any_msg = on_message(
    priority=20,
    block=False,
    rule=Rule(check_accounts, get_answer),
    permission=permission.GROUP  # | permission.PRIVATE_FRIEND
)


async def is_shutup(self_id: int, group_id: int) -> bool:
    info = await get_bot(str(self_id)).call_api('get_group_member_info', **{
        'user_id':  self_id,
        'group_id': group_id
    })
    flag: bool = info['shut_up_timestamp'] > time.time()

    if flag:
        logger.info(f'repeater：派蒙[{self_id}]在群[{group_id}] 处于禁言状态')

    return flag


@any_msg.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):

    delay = random.randint(2, 4)
    for item in state['answers']:
        logger.info(f'repeater：派蒙[{event.self_id}]准备向群[{event.group_id}]回复[{item}]')

        await asyncio.sleep(delay)
        try:
            await any_msg.send(item)
        except ActionFailed:
            # 自动删除失效消息。若 bot 处于风控期，请勿开启该功能
            shutup = await is_shutup(event.self_id, event.group_id)
            if not shutup:  # 说明这条消息失效了
                logger.info('repeater | bot [{}] ready to ban [{}] in group [{}]'.format(
                    event.self_id, str(item), event.group_id))
                Chat.ban(event.group_id, event.self_id, str(item), 'ActionFailed')
                break
        delay = random.randint(2, 4)


async def is_reply(bot: Bot, event: GroupMessageEvent) -> bool:
    return bool(event.reply)


ban_msg = on_message(
    rule=to_me() & keyword('不可以', '达咩', '不行', 'no') & Rule(is_reply),
    priority=5,
    block=True,
    permission=permission.GROUP_OWNER | permission.GROUP_ADMIN
)


@ban_msg.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if '[CQ:reply,' not in event.raw_message:
        return False

    raw_message = ''
    for item in event.reply.message:
        raw_reply = str(item)
        # 去掉图片消息中的 url, subType 等字段
        raw_message += re.sub(r'(\[CQ\:.+)(?:,url=*)(\])',
                              r'\1\2', raw_reply)

    logger.info(f'repeater：派蒙[{event.self_id}] ready to ban [{raw_message}] in group [{event.group_id}]')

    if Chat.ban(event.group_id, event.self_id, raw_message, str(event.user_id)):
        msg_send = ['派蒙知道错了...达咩!', '派蒙不会再这么说了...', '果面呐噻,派蒙说错话了...']
        await ban_msg.finish(random.choice(msg_send))


scheduler = require('nonebot_plugin_apscheduler').scheduler


async def message_is_ban(bot: Bot, event: GroupMessageEvent) -> bool:
    return event.get_plaintext().strip() == '不可以发这个'


ban_msg_latest = on_message(
    rule=to_me() & Rule(message_is_ban),
    priority=5,
    block=True,
    permission=permission.GROUP_OWNER | permission.GROUP_ADMIN
)


@ban_msg_latest.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    logger.info(
        f'repeater：派蒙[{event.self_id}]把群[{event.group_id}]最后的回复ban了')

    if Chat.ban(event.group_id, event.self_id, '', str(event.user_id)):
        msg_send = ['派蒙知道错了...达咩!', '派蒙不会再这么说了...', '果面呐噻,派蒙说错话了...']
        await ban_msg_latest.finish(random.choice(msg_send))


@scheduler.scheduled_job('interval', seconds=5, misfire_grace_time=5)
async def speak_up():
    ret = Chat.speak()
    if not ret:
        return

    bot_id, group_id, messages = ret

    for msg in messages:
        logger.info(f'repeater：派蒙[{bot_id}]准备向群[{group_id}]发送消息[{messages}]')
        await get_bot(str(bot_id)).call_api('send_group_msg', **{
            'message':  msg,
            'group_id': group_id
        })
        await asyncio.sleep(random.randint(2, 4))


update_scheduler = require('nonebot_plugin_apscheduler').scheduler


async def is_drink_msg(bot: Bot, event: GroupMessageEvent) -> bool:
    return event.get_plaintext().strip() in ['派蒙干杯', '应急食品开餐', '派蒙干饭']


drink_msg = on_message(
    rule=Rule(is_drink_msg),
    priority=5,
    block=True,
    permission=permission.GROUP_OWNER | permission.GROUP_ADMIN
)


@drink_msg.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    drunk_duration = random.randint(60, 600)
    logger.info(f'repeater：派蒙[{event.self_id}]即将在群[{event.group_id}]喝醉，在[{drunk_duration}秒]后醒来')
    Chat.drink(event.group_id)
    try:
        await drink_msg.send('呀，旅行者。你今天走起路来，怎么看着摇摇晃晃的？')
    except ActionFailed:
        pass

    await asyncio.sleep(drunk_duration)
    ret = Chat.sober_up(event.group_id)
    if ret:
        logger.info(f'repeater：派蒙[{event.self_id}]在群[{event.group_id}]醒酒了')
        await drink_msg.finish('呃...头好疼...下次不能喝那么多了...')


@update_scheduler.scheduled_job('cron', hour='4')
def update_data():
    Chat.clearup_context()
    Chat.completely_sober()
