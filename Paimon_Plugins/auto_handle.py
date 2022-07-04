import random
from asyncio import sleep
from pathlib import Path

from nonebot import get_driver, on_request, on_notice
from nonebot.adapters.onebot.v11 import Bot, FriendRequestEvent, GroupRequestEvent, GroupIncreaseNoticeEvent, \
    MessageSegment, Message, FriendAddNoticeEvent, HonorNotifyEvent

from ..utils.config import config
from ..utils.message_util import MessageBuild

superuser = int(list(get_driver().config.superusers)[0])

requests_handle = on_request(priority=5, block=True)
notice_handle = on_notice(priority=5, block=True)


@requests_handle.handle()
async def addFriend(bot: Bot, event: FriendRequestEvent):
    superuser_msg = f'{event.user_id}请求添加派蒙为好友, 验证信息为：{event.comment}'
    if config.paimon_add_friend:
        superuser_msg += '，已自动同意'
        await sleep(random.randint(4, 8))
        await event.approve(bot)
    else:
        superuser_msg += '，请主人自行处理哦'
    if config.paimon_request_remind:
        await bot.send_private_msg(user_id=superuser, message=superuser_msg)


@requests_handle.handle()
async def addGroup(bot: Bot, event: GroupRequestEvent):
    if event.sub_type != 'invite':
        return
    superuser_msg = f'{event.user_id}邀请派蒙加入群{event.group_id}'
    if config.paimon_add_group or event.user_id == superuser:
        superuser_msg += '，已自动同意'
        await sleep(random.randint(4, 8))
        await event.approve(bot)
    else:
        superuser_msg += '，请主人自行处理哦'
    if config.paimon_request_remind:
        await bot.send_private_msg(user_id=superuser, message=superuser_msg)


@notice_handle.handle()
async def FriendNew(bot: Bot, event: FriendAddNoticeEvent):
    greet_emoticon = MessageBuild.Image(Path() / 'resources' / 'LittlePaimon' / 'emoticons' / '派蒙-干杯.png', mode='RGBA')
    await sleep(random.randint(4, 8))
    await bot.send_private_msg(user_id=event.user_id, message=Message(MessageSegment.text('旅行者你好呀~，这里是小派蒙，对我说help查看帮助吧~\n') + greet_emoticon))


@notice_handle.handle()
async def GroupNewMember(bot: Bot, event: GroupIncreaseNoticeEvent):
    greet_emoticon = MessageBuild.Image(Path() / 'resources' / 'LittlePaimon' / 'emoticons' / '派蒙-干杯.png', mode='RGBA')
    if event.user_id == event.self_id:
        await sleep(random.randint(4, 8))
        await bot.send_group_msg(group_id=event.group_id, message=Message(
            MessageSegment.text('旅行者们大家好呀~，这里是小派蒙，对我说help查看帮助吧~\n') + greet_emoticon))
    elif event.group_id not in config.paimon_greet_ban:
        await sleep(random.randint(4, 8))
        await bot.send_group_msg(group_id=event.group_id, message=Message(
            MessageSegment.at(event.user_id) + MessageSegment.text("欢迎新旅行者哦~\n") + greet_emoticon))


@notice_handle.handle()
async def GroupTalkative(bot: Bot, event: HonorNotifyEvent):
    if event.group_id not in config.paimon_greet_ban and event.honor_type == 'talkative':
        await sleep(random.randint(4, 8))
        if event.user_id == event.self_id:
            honor_emoticon = MessageBuild.Image(Path() / 'resources' / 'LittlePaimon' / 'emoticons' / '派蒙-哼哼.png',
                                                mode='RGBA')
            text = random.choice(['诶嘿~本应急食品是龙王~~', '哦豁，派蒙又是龙王，你们好逊哦(', '怎么回事，你们这么多人居然说不过我一个应急食品?~', '请叫我龙王派蒙~诶嘿'])
            await bot.send_group_msg(group_id=event.group_id,
                                     message=Message(MessageSegment.text(text) + honor_emoticon))
        elif random.random() <= 0.5:
            honor2_emoticon = MessageBuild.Image(Path() / 'resources' / 'LittlePaimon' / 'emoticons' / '派蒙-黑线.png',
                                                 mode='RGBA')
            text = random.choice(['怎么这人比我派蒙话还多!!', '咦~是个话唠龙王(', '好气哦，怎么能抢我派蒙的龙王啊!!'])
            await bot.send_group_msg(group_id=event.group_id,
                                     message=Message(MessageSegment.at(event.user_id) + MessageSegment.text(text) + honor2_emoticon))
