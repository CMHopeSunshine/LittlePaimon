import random
from asyncio import sleep
from utils.config import config
from nonebot import get_driver
from nonebot.message import event_preprocessor
from nonebot.adapters.onebot.v11 import Bot, FriendRequestEvent, GroupRequestEvent

superuser = int(list(get_driver().config.superusers)[0])


@event_preprocessor
async def addFriend(bot: Bot, event: FriendRequestEvent):
    superuser_msg = f'{event.user_id}请求添加派蒙为好友, 验证信息为：{event.comment}'
    if config.paimon_add_friend:
        superuser_msg += '，已自动同意'
        await sleep(random.randint(2, 4))
        await event.approve(bot)
        await sleep(random.randint(3, 6))
        await bot.send_private_msg(user_id=event.user_id, message=f'旅行者你好呀，这里是小派蒙，发送/help查看帮助哦')
    else:
        superuser_msg += '，请主人自行处理哦'
    await bot.send_private_msg(user_id=superuser, message=superuser_msg)


@event_preprocessor
async def addGroup(bot: Bot, event: GroupRequestEvent):
    if event.sub_type != 'invite':
        return
    superuser_msg = f'{event.user_id}邀请派蒙加入群{event.group_id}'
    if config.paimon_add_group or event.user_id == superuser:
        superuser_msg += '，已自动同意'
        await sleep(random.randint(2, 4))
        await event.approve(bot)
        await sleep(random.randint(3, 6))
        await bot.send_group_msg(group_id=event.group_id, message=f'旅行者们大家好呀，这里是小派蒙，发送/help查看帮助哦')
    else:
        superuser_msg += '，请主人自行处理哦'
    await bot.send_private_msg(user_id=superuser, message=superuser_msg)