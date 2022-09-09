import asyncio
import random
import re
import threading
from collections import defaultdict

from nonebot import on_keyword, on_message, on_command, get_bot
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, GROUP, Message, ActionFailed
from nonebot.params import Arg, CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me, Rule
from nonebot.typing import T_State

from LittlePaimon import NICKNAME, SUPERUSERS
from LittlePaimon.utils import scheduler, logger
from .api import is_shutup
from .models import LearningChat
from .config import config_manager

__plugin_meta__ = PluginMetadata(
    name='群聊学习',
    description='群聊学习',
    usage='群聊学习',
    extra={
        'author':   '惜月',
        'priority': 16,
    }
)

message_id_lock = threading.Lock()
message_id_dict = defaultdict(list)


async def chat_rule(event: GroupMessageEvent, state: T_State) -> bool:
    if not config_manager.config.total_enable:
        return False
    if event.group_id in config_manager.config.ban_groups:
        return False
    if event.user_id in config_manager.config.ban_users:
        return False
    if any(w in event.raw_message for w in config_manager.config.ban_words):
        return False
    to_learn = True
    with message_id_lock:
        """多账号登陆，且在同一群中时；避免一条消息被处理多次"""
        message_id = event.message_id
        group_id = event.group_id
        if group_id in message_id_dict and message_id in message_id_dict[group_id]:
            to_learn = False

        message_id_dict[group_id].append(message_id)
        if len(message_id_dict[group_id]) > 100:
            message_id_dict[group_id] = message_id_dict[group_id][:-10]

    chat = LearningChat(event)
    answers = await chat.answer()
    if to_learn:
        await chat.learn()
    if answers:
        state['answers'] = answers
        return True
    return False


async def is_reply(event: GroupMessageEvent) -> bool:
    return bool(event.reply)


learning_chat = on_message(priority=99, block=False, rule=Rule(chat_rule), permission=GROUP, state={
    'pm_name':        '群聊学习',
    'pm_description': '(被动技能)bot会学习群友们的发言',
    'pm_usage':       '群聊学习',
    'pm_priority':    1
})
ban_chat = on_keyword({'不可以', '达咩', '不行', 'no'}, rule=to_me(), priority=1, block=True, state={
    'pm_name':        '群聊学习禁用',
    'pm_description': '如果bot说了不好的话，回复这句话，告诉TA不能这么说，需管理权限',
    'pm_usage':       '@bot 不可以',
    'pm_priority':    2
})
set_enable = on_keyword({'学说话', '快学', '开启学习', '闭嘴', '别学', '关闭学习'}, rule=to_me(), priority=1, block=True, state={
    'pm_name':        '群聊学习开关',
    'pm_description': '开启或关闭当前群的学习能力，需管理权限',
    'pm_usage':       '@bot 开启|关闭学习',
    'pm_priority':    3
})
# set_config = on_command('chat', aliases={'群聊学习设置'}, permission=SUPERUSER, priority=1, block=True, state={
#     'pm_name':        'ysbc',
#     'pm_description': '查询已绑定的原神cookie情况',
#     'pm_usage':       'ysbc',
#     'pm_priority':    2
# })


# ban_msg_latest = on_fullmatch(msg=('不可以发这个', '不能发这个', '达咩达咩'), rule=to_me(), priority=1, block=True, permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER)


@learning_chat.handle()
async def _(event: GroupMessageEvent, answers=Arg('answers')):
    for item in answers:
        logger.info('群聊学习', f'{NICKNAME}即将向群<m>{event.group_id}</m>发送<m>"{item}"</m>')
        await asyncio.sleep(random.randint(1, 3))
        try:
            await learning_chat.send(Message(item))
        except ActionFailed:
            if not await is_shutup(event.self_id, event.group_id):
                # Bot没用在禁言中但发送失败，说明该条消息被风控，禁用调
                logger.info('群聊学习', f'{NICKNAME}将群<m>{event.group_id}</m>的发言<m>"{item}"</m>列入禁用列表')
                await LearningChat.ban(event.group_id, event.self_id,
                                       str(item), 'ActionFailed')
                break


@ban_chat.handle()
async def _(event: GroupMessageEvent):
    if event.sender.role not in ['admin', 'owner'] and event.user_id not in SUPERUSERS:
        await ban_chat.finish(random.choice([f'{NICKNAME}就喜欢说这个，哼！', f'你管得着{NICKNAME}吗！']))
    if event.reply:
        raw_message = ''
        for item in event.reply.message:
            raw_reply = str(item)
            # 去掉图片消息中的 url, subType 等字段
            raw_message += re.sub(r'(\[CQ:.+)(,url=*)(])',
                                  r'\1\2', raw_reply)
        logger.info('群聊学习', f'{NICKNAME}将群<m>{event.group_id}</m>的发言<m>"{raw_message}"</m>列入禁用列表')

        if await LearningChat.ban(event.group_id, event.self_id, raw_message, str(event.user_id)):
            await ban_chat.finish(
                random.choice([f'{NICKNAME}知道错了...达咩!', f'{NICKNAME}不会再这么说了...', f'果面呐噻,{NICKNAME}说错话了...']))
    else:
        logger.info('群聊学习', f'{NICKNAME}将群<m>{event.group_id}</m>的最后一条发言列入禁用列表')

        if await LearningChat.ban(event.group_id, event.self_id, '', str(event.user_id)):
            await ban_chat.finish(
                random.choice([f'{NICKNAME}知道错了...达咩!', f'{NICKNAME}不会再这么说了...', f'果面呐噻,{NICKNAME}说错话了...']))


@set_enable.handle()
async def _(event: MessageEvent):
    if event.user_id in SUPERUSERS:
        if any(w in event.raw_message for w in {'学说话', '快学', '开启学习'}):
            if config_manager.config.total_enable:
                msg = f'{NICKNAME}已经在努力尝试看懂你们说的话了！'
            else:
                config_manager.config.total_enable = True
                msg = f'{NICKNAME}会尝试学你们说怪话！'
        elif config_manager.config.total_enable:
            config_manager.config.total_enable = False
            msg = f'好好好，{NICKNAME}不学说话就是了！'
        else:
            msg = f'{NICKNAME}明明没有在学你们说话！'
    elif isinstance(event, GroupMessageEvent) and event.sender.role in {'admin', 'owner'}:
        if any(w in event.raw_message for w in {'学说话', '快学', '开启学习'}):
            if event.group_id in config_manager.config.ban_groups:
                config_manager.config.ban_groups.remove(event.group_id)
                msg = f'{NICKNAME}会尝试学你们说怪话！'
            else:
                msg = f'{NICKNAME}已经在努力尝试看懂你们说的话了！'
        elif event.group_id not in config_manager.config.ban_groups:
            config_manager.config.ban_groups.append(event.group_id)
            msg = f'好好好，{NICKNAME}不学说话就是了！'
        else:
            msg = f'{NICKNAME}明明没有在学你们说话！'
    else:
        msg = random.choice([f'你管得着{NICKNAME}吗！', f'你可没有权限要求{NICKNAME}！'])
    await set_enable.finish(msg)


# @set_config.handle()
# async def _(event: MessageEvent, state: T_State, msg: Message = CommandArg()):
#     state['config_list'] = config_manager.config_list
#     configs_str = '\n'.join([f'{k}: {v}' for k, v in config_manager.config.dict(by_alias=True).items()])
#     if msg:
#         msg = msg.extract_plain_text().strip().split(' ')
#         if state['key'] in state['config_list']:
#             state['key'] = msg[0]
#             if len(msg) > 1:
#                 state['value'] = msg[1]
#         else:
#             state['msg'] = '没有叫'

# @ban_msg_latest.handle()
# async def _(event: GroupMessageEvent):
#     logger.info('群聊学习', f'{NICKNAME}将群<m>{event.group_id}</m>的最后一条发言列入禁用列表')
#
#     if await LearningChat.ban(event.group_id, event.self_id, '', str(event.user_id)):
#         msg_send = ['派蒙知道错了...达咩!', '派蒙不会再这么说了...', '果面呐噻,派蒙说错话了...']
#         await ban_msg_latest.finish(random.choice(msg_send))


@scheduler.scheduled_job('interval', seconds=5, misfire_grace_time=5)
async def speak_up():
    if not config_manager.config.total_enable:
        return
    if not (ret := await LearningChat.speak()):
        return
    bot_id, group_id, messages = ret
    if group_id in config_manager.config.ban_groups:
        return
    for msg in messages:
        logger.info('群聊学习', f'{NICKNAME}即将向群<m>{group_id}</m>发送<m>"{msg}"</m>')
        await get_bot(str(bot_id)).send_group_msg(group_id=group_id, message=msg)
        await asyncio.sleep(random.randint(2, 4))


@scheduler.scheduled_job('cron', hour='4')
def update_data():
    if config_manager.config.total_enable:
        LearningChat.clear_up_context()
