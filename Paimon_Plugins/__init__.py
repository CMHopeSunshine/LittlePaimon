from aiohttp import ClientSession
from urllib.parse import quote
from typing import Union
from nonebot import on_command, get_driver
from nonebot.params import CommandArg
from nonebot.message import event_preprocessor
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageEvent, MessageSegment, FriendRequestEvent, \
    GroupRequestEvent
from ..utils.util import FreqLimiter
from ..utils.config import config
from asyncio import sleep
from .chat import *

superuser = int(list(get_driver().config.superusers)[0])

duilian = on_command('对联', aliases={'对对联'}, priority=15, block=True)
cat_pic = on_command('猫图', aliases={'来点猫片', '看看猫猫', '来个猫猫'}, priority=15, block=True)
ecy_pic = on_command('二次元图', aliases={'来点二次元', '来点二刺螈'}, priority=15, block=True)
ys_pic = on_command('原神壁纸', aliases={'来点原神图', '来点原神壁纸'}, priority=15, block=True)

duilian_limit = FreqLimiter(config.paimon_duilian_cd)
cat_lmt = FreqLimiter(config.paimon_cat_cd)
ecy_lmt = FreqLimiter(config.paimon_ecy_cd)
ys_lmt = FreqLimiter(config.paimon_ysp_cd)


@duilian.handle()
async def duilian_handler(event: Union[GroupMessageEvent, MessageEvent], msg=CommandArg()):
    if not msg:
        await duilian.finish('请输入对联内容')
    if not duilian_limit.check(event.group_id or event.user_id):
        await duilian.finish(f'对联冷却ing(剩余{duilian_limit.left_time(event.group_id or event.user_id)}秒)')
    else:
        msg = str(msg).split(' ')
        word = msg[0].strip()
        try:
            num = int(msg[1]) if len(msg) > 1 else 1
        except:
            num = 1
        num = num if num < 10 else 10
        duilian_limit.start_cd(event.group_id or event.user_id, config.paimon_duilian_cd)
        text = quote(str(word))
        url = f'https://ai-backend.binwang.me/v0.2/couplet/{text}'
        async with ClientSession() as session:
            res = await session.get(url)
            res = await res.json()
            result = ''
            for n in range(0, num):
                result += res['output'][n] + '\n'
            await duilian.finish(f'上联：{word}\n下联：{result}')


@cat_pic.handle()
async def cat_pic_handler(event: Union[GroupMessageEvent, MessageEvent]):
    if not cat_lmt.check(event.group_id or event.user_id):
        await cat_pic.finish(f'猫片冷却ing(剩余{cat_lmt.left_time(event.group_id or event.user_id)}秒)')
    else:
        cat_lmt.start_cd(event.group_id or event.user_id, config.paimon_cat_cd)
        url = 'http://edgecats.net/'
        async with ClientSession() as session:
            res = await session.get(url)
            res = await res.read()
            await cat_pic.finish(MessageSegment.image(res))


@ecy_pic.handle()
async def ecy_pic_handler(event: Union[GroupMessageEvent, MessageEvent]):
    urls = [
        'https://www.dmoe.cc/random.php',
        'https://acg.toubiec.cn/random.php',
        'https://api.ixiaowai.cn/api/api.php'
    ]
    if not ecy_lmt.check(event.group_id or event.user_id):
        await ecy_pic.finish(f'二次元图片冷却ing(剩余{ecy_lmt.left_time(event.group_id or event.user_id)}秒)')
    else:
        ecy_lmt.start_cd(event.group_id or event.user_id, config.paimon_ecy_cd)
        async with ClientSession() as session:
            res = await session.get(random.choice(urls))
            res = await res.read()
            await cat_pic.finish(MessageSegment.image(res))


@ys_pic.handle()
async def ys_pic_handler(event: Union[GroupMessageEvent, MessageEvent]):
    urls = [
        'https://api.r10086.com/img-api.php?type=%E5%8E%9F%E7%A5%9E%E6%A8%AA%E5%B1%8F%E7%B3%BB%E5%88%971',
        'https://api.r10086.com/img-api.php?type=%E5%8E%9F%E7%A5%9E%E7%AB%96%E5%B1%8F%E7%B3%BB%E5%88%971',
        'https://api.dujin.org/pic/yuanshen/',
        'https://api.dreamofice.cn/random-v0/img.php?game=ys'
    ]
    if not ys_lmt.check(event.group_id or event.user_id):
        await ys_pic.finish(f'原神壁纸冷却ing(剩余{ys_lmt.left_time(event.group_id or event.user_id)}秒)')
    else:
        ys_lmt.start_cd(event.group_id or event.user_id, config.paimon_ysp_cd)
        async with ClientSession() as session:
            res = await session.get(random.choice(urls))
            res = await res.read()
            await ys_pic.finish(MessageSegment.image(res))


@event_preprocessor
async def addFriend(bot: Bot, event: FriendRequestEvent):
    superuser_msg = f'{event.user_id}请求添加派蒙为好友, 验证信息为：{event.comment}'
    if config.paimon_add_friend == 1:
        superuser_msg += '，已自动同意'
        await event.approve()
        await sleep(random.randint(3, 6))
        await bot.send_private_msg(user_id=event.user_id, message=f'旅行者你好呀，这里是小派蒙，发送/help查看帮助哦')
    elif config.paimon_add_friend == 2:
        superuser_msg += '，已自动拒绝'
        await event.reject()
    else:
        superuser_msg += '，请主人自行处理哦'
    await bot.send_private_msg(user_id=superuser, message=superuser_msg)


@event_preprocessor
async def addFriend(bot: Bot, event: GroupRequestEvent):
    if event.sub_type != 'invite':
        return
    superuser_msg = f'{event.user_id}邀请派蒙加入群{event.group_id}'
    if config.paimon_add_group == 1 or event.user_id == superuser:
        superuser_msg += '，已自动同意'
        await event.approve()
        await sleep(random.randint(3, 6))
        await bot.send_group_msg(group_id=event.group_id, message=f'旅行者们大家好呀，这里是小派蒙，发送/help查看帮助哦')
    elif config.paimon_add_group == 2:
        superuser_msg += '，已自动拒绝'
        await event.reject()
    else:
        superuser_msg += '，请主人自行处理哦'
    await bot.send_private_msg(user_id=superuser, message=superuser_msg)
