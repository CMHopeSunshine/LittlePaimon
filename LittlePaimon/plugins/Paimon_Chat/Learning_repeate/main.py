import asyncio
import os
import random
import re
import threading
import time

from nonebot import on_message, require, get_bot, logger
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11 import permission
from nonebot.exception import ActionFailed
from nonebot.permission import SUPERUSER
from nonebot.rule import keyword, to_me, Rule
from nonebot.typing import T_State

from .model import Chat
from ...utils.config import config

message_id_lock = threading.Lock()
message_id_dict = {}


# 检测是否开启该群的机器学习
def checkGroup(event: GroupMessageEvent) -> bool:
    if event.group_id in Chat.learningGroup:
        return True
    return False


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
    elif not checkGroup(event):  # 判断群组
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
    priority=99,
    block=False,
    rule=Rule(check_accounts, get_answer, checkGroup),
    permission=permission.GROUP  # | permission.PRIVATE_FRIEND
)


async def is_shutup(self_id: int, group_id: int) -> bool:
    info = await get_bot(str(self_id)).call_api('get_group_member_info', **{
        'user_id':  self_id,
        'group_id': group_id
    })
    flag: bool = info['shut_up_timestamp'] > time.time()

    if flag:
        logger.info(f'repeater：脑积水[{self_id}]在群[{group_id}] 处于禁言状态')

    return flag


@any_msg.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    delay = random.randint(2, 4)
    for item in state['answers']:
        logger.info(f'repeater：脑积水[{event.self_id}]准备向群[{event.group_id}]回复[{item}]')

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
    rule=to_me() & keyword('不可以', '达咩', '不行', 'no') & Rule(is_reply, checkGroup),
    priority=5,
    block=True,
    permission=permission.GROUP_OWNER | permission.GROUP_ADMIN | SUPERUSER
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

    logger.info(f'repeater：脑积水[{event.self_id}] ready to ban [{raw_message}] in group [{event.group_id}]')

    if Chat.ban(event.group_id, event.self_id, raw_message, str(event.user_id)):
        msg_send = ['脑积水知道错了...达咩!', '脑积水不会再这么说了...', '果面呐噻,脑积水说错话了...']
        await ban_msg.finish(random.choice(msg_send))


scheduler = require('nonebot_plugin_apscheduler').scheduler


async def message_is_ban(bot: Bot, event: GroupMessageEvent) -> bool:
    return event.get_plaintext().strip() == '不可以发这个'


ban_msg_latest = on_message(
    rule=to_me() & Rule(message_is_ban, checkGroup),
    priority=5,
    block=True,
    permission=permission.GROUP_OWNER | permission.GROUP_ADMIN | SUPERUSER
)


@ban_msg_latest.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    logger.info(
        f'repeater：脑积水[{event.self_id}]把群[{event.group_id}]最后的回复ban了')

    if Chat.ban(event.group_id, event.self_id, '', str(event.user_id)):
        msg_send = ['脑积水知道错了...达咩!', '脑积水不会再这么说了...', '果面呐噻,脑积水说错话了...']
        await ban_msg_latest.finish(random.choice(msg_send))


@scheduler.scheduled_job('interval', seconds=5, misfire_grace_time=5)
async def speak_up():
    ret = Chat.speak()
    if not ret:
        return

    bot_id, group_id, messages = ret

    for msg in messages:
        logger.info(f'repeater：脑积水[{bot_id}]准备向群[{group_id}]发送消息[{messages}]')
        await get_bot(str(bot_id)).call_api('send_group_msg', **{
            'message':  msg,
            'group_id': group_id
        })
        await asyncio.sleep(random.randint(2, 4))


update_scheduler = require('nonebot_plugin_apscheduler').scheduler


async def is_drink_msg(bot: Bot, event: GroupMessageEvent) -> bool:
    return event.get_plaintext().strip() in ['脑积水干杯', '应急食品开餐', '脑积水干饭']


drink_msg = on_message(
    rule=Rule(is_drink_msg, checkGroup),
    priority=5,
    block=True,
    permission=permission.GROUP_OWNER | permission.GROUP_ADMIN
)


@drink_msg.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    drunk_duration = random.randint(60, 600)
    logger.info(f'repeater：脑积水[{event.self_id}]即将在群[{event.group_id}]喝醉，在[{drunk_duration}秒]后醒来')
    Chat.drink(event.group_id)
    try:
        await drink_msg.send('呀，旅行者。你今天走起路来，怎么看着摇摇晃晃的？')
    except ActionFailed:
        pass

    await asyncio.sleep(drunk_duration)
    ret = Chat.sober_up(event.group_id)
    if ret:
        logger.info(f'repeater：脑积水[{event.self_id}]在群[{event.group_id}]醒酒了')
        await drink_msg.finish('呃...头好疼...下次不能喝那么多了...')


@update_scheduler.scheduled_job('cron', hour='4')
def update_data():
    Chat.clearup_context()
    Chat.completely_sober()


# 群组开启
onLearningGroup = on_message(
    rule=to_me() & keyword("脑积水学习开启", "说怪话"),
    priority=4,
    block=True,
    permission=permission.GROUP_ADMIN | permission.GROUP_OWNER | SUPERUSER
)
onLearningGroup.__paimon_help__ = {
    "usage":     "@脑积水 <说怪话>",
    "introduce": "开启脑积水在该群的机器学习能力",
    "priority":  94
}


@onLearningGroup.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if checkGroup(event):
        await onLearningGroup.finish("脑积水已经在学习群友的话了哦")
    else:
        Chat.learningGroup.append(event.group_id)
        await onLearningGroup.finish("脑积水开始学习群友说怪话!")


# 群组关闭
offLearningGroup = on_message(
    rule=to_me() & keyword("脑积水学习关闭", "不准说怪话"),
    priority=3,
    block=True,
    permission=permission.GROUP_ADMIN | permission.GROUP_OWNER | SUPERUSER
)
offLearningGroup.__paimon_help__ = {
    "usage":     "@脑积水 <不准说怪话>",
    "introduce": "关闭脑积水在该群的机器学习能力",
    "priority":  95
}


@offLearningGroup.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if not checkGroup(event):
        await offLearningGroup.finish("脑积水没有在学群友说话！")
    else:
        Chat.learningGroup.remove(event.group_id)
        await offLearningGroup.finish("脑积水不学就是了TAT")


# 发癫
fun_msg = on_message(
    rule=to_me() & keyword('发癫', '脑积水发癫', '喝酒') & Rule(checkGroup),
    priority=6,
    block=True,
    permission=permission.GROUP_ADMIN | permission.GROUP_OWNER | SUPERUSER
)
fun_msg.__paimon_help__ = {
    "usage":     "@脑积水 <发癫>",
    "introduce": "脑积水喝醉了在群里发癫",
    "priority":  96
}


@fun_msg.handle()
async def funmsg(bot: Bot, event: GroupMessageEvent):
    logger.info(f'repeater：脑积水开始发癫')
    Chat.answer_threshold = 1
    Chat.speak_threshold = 1
    Chat.speak_continuously_probability = 1
    Chat.speak_poke_probability = 1
    Chat.speak_continuously_max_len = 10
    Chat.cross_group_threshold = 1
    msg_send = ['呀，旅行者。你今天走起路来，怎么看着摇摇晃晃的？嘿嘿嘿~~~', '……&%*&U（*……&%']
    await fun_msg.finish(random.choice(msg_send))


# 停止发癫
stop_fun_msg = on_message(
    rule=to_me() & keyword('恢复', '不准发癫', '停止', 'stop'),
    priority=5,
    block=True,
    permission=permission.GROUP_ADMIN | permission.GROUP_OWNER | SUPERUSER
)
stop_fun_msg.__paimon_help__ = {
    "usage":     "@脑积水 <不准发癫>",
    "introduce": "让脑积水恢复正常",
    "priority":  97
}


@stop_fun_msg.handle()
async def stopfunmsg(bot: Bot, event: GroupMessageEvent):
    logger.info(f'repeater：脑积水停止发癫')
    Chat.answer_threshold = config.paimon_answer_threshold
    Chat.speak_threshold = config.paimon_speak_threshold
    Chat.speak_continuously_probability = config.paimon_speak_continuously_probability
    Chat.speak_poke_probability = config.paimon_speak_poke_probability
    Chat.speak_continuously_max_len = config.paimon_speak_continuously_max_len
    Chat.cross_group_threshold = config.paimon_cross_group_threshold
    msg_send = ['呃...头好疼...恢复了']
    await stop_fun_msg.finish(msg_send)


# 上调学习能力和主动发言
upLearning = on_message(
    rule=to_me() & keyword('加强学习能力', '脑积水快学', '再学快点', '多说点话') & Rule(checkGroup),
    priority=6,
    block=True,
    permission=permission.GROUP_ADMIN | permission.GROUP_OWNER | SUPERUSER
)
upLearning.__paimon_help__ = {
    "usage":     "@脑积水 <多说点话>",
    "introduce": "增强脑积水的学习能力",
    "priority":  98
}


@upLearning.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if Chat.speak_threshold == 1:
        Chat.answer_threshold = Chat.speak_threshold
        await upLearning.finish("脑积水已经学满贯了")
    else:
        Chat.speak_threshold -= 1
        Chat.answer_threshold = Chat.speak_threshold
        await upLearning.finish("脑积水会努力学习的")


# 降低学习能力和主动发言
downLearning = on_message(
    rule=to_me() & keyword('降低学习能力', '脑积水变笨', '笨比脑积水', '少说点话') & Rule(checkGroup),
    priority=6,
    block=True,
    permission=permission.GROUP_ADMIN | permission.GROUP_OWNER | SUPERUSER
)
downLearning.__paimon_help__ = {
    "usage":     "@脑积水 <笨比脑积水>",
    "introduce": "降低脑积水的学习能力",
    "priority":  99
}


@downLearning.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if Chat.speak_threshold == 6:
        Chat.answer_threshold = Chat.speak_threshold
        await downLearning.finish("脑积水不说话就是了o(￣ヘ￣o＃)")
    else:
        Chat.speak_threshold += 1
        Chat.answer_threshold = Chat.speak_threshold
        await downLearning.finish("知道了知道了，旅行者就是嫌脑积水吵了")


add_ban_word = on_message(
    rule=to_me() & Rule(checkGroup) & keyword('添加禁用词', '不准说'),
    priority=4,
    block=True,
    permission=permission.GROUP_ADMIN | permission.GROUP_OWNER | SUPERUSER
)
add_ban_word.__paimon_help__ = {
    "usage":     "@脑积水 <不准说> (关键词)",
    "introduce": "禁用某些不想让脑积水说的关键词, 括号(英语)内部为关键词内容",
    "priority":  99
}
@add_ban_word.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    msg = str(event.message)
    msg = re.findall(re.compile(r"[(](.*)[)]", re.S), msg)
    if msg:
        msg = str(msg[0])
        if '&#91;' in msg:
            msg = msg.replace('&#91;', '[')
        if '&#93;' in msg:
            msg = msg.replace('&#93;', ']')
        Chat.chat_word_ban.append(msg)
        await add_ban_word.finish('脑积水不会说这个词了')
    else:
        await add_ban_word.finish('那你倒是告诉脑积水什么不能说啊😡😡😡')

del_ban_word = on_message(
    rule=to_me() & Rule(checkGroup) & keyword('删除禁用词', '可以说'),
    priority=4,
    block=True,
    permission = permission.GROUP_ADMIN | permission.GROUP_OWNER | SUPERUSER
)
del_ban_word.__paimon_help__ = {
    "usage":     "@脑积水 <可以说> (关键词)",
    "introduce": "让脑积水可以说某些关键词, 括号(英语)内部为关键词内容",
    "priority":  99
}
@del_ban_word.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    msg = str(event.message)
    msg = re.findall(re.compile(r"[(](.*)[)]", re.S), msg)
    if msg:
        msg = str(msg[0])
        if '&#91;' in msg:
            msg = msg.replace('&#91;', '[')
        if '&#93;' in msg:
            msg = msg.replace('&#93;', ']')
        answer = '怎么又允许脑积水说了捏？'
        try:
            Chat.chat_word_ban.remove(msg)
        except:
            answer = '没有ban这个词, 不要耍我'
        await del_ban_word.finish(answer)
    else:
        await del_ban_word.finish('可以说你是🤡吗')

check_ban_word = on_message(
    rule=to_me() & Rule(checkGroup) & keyword('查看禁用词', '哪些不准说'),
    priority=4,
    block=True,
    permission = permission.GROUP_ADMIN | permission.GROUP_OWNER | SUPERUSER
)
check_ban_word.__paimon_help__ = {
    "usage":     "@脑积水 <查看禁用词>",
    "introduce": "查看当前的禁用词内容",
    "priority":  99
}
@check_ban_word.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    msg = '当前的违禁词: '
    if Chat.chat_word_ban:
        for word in Chat.chat_word_ban:
            msg += str(word) + ' | '
        await check_ban_word.finish(msg)
    else:
        await check_ban_word.finish('当前还没有违禁词哦')
