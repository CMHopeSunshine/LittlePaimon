from aiohttp import ClientSession
from urllib.parse import quote
from nonebot import on_command
from nonebot.params import CommandArg
from typing import Union
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent, MessageSegment
from ..utils.util import FreqLimiter
import random

duilian = on_command('对联', aliases={'对对联'}, priority=15, block=True)
cat_pic = on_command('猫图', aliases={'来点猫片', '看看猫猫', '来个猫猫'}, priority=15, block=True)
tcy_pic = on_command('二次元图', aliases={'来点二次元', '来点二刺螈'}, priority=15, block=True)

duilian_limit = FreqLimiter(5)
cat_lmt = FreqLimiter(10)
tcy_lmt = FreqLimiter(5)


@duilian.handle()
async def duilian_handler(event: Union[GroupMessageEvent, MessageEvent], msg=CommandArg()):
    if not msg:
        await duilian.finish('请输入对联内容')
    if not duilian_limit.check(event.group_id or event.user_id):
        await duilian.finish(f'对联冷却ing(剩余{duilian_limit.left_time(event.group_id or event.user_id)}秒)')
    else:
        duilian_limit.start_cd(event.group_id or event.user_id, 10)
        text = quote(str(msg))
        url = f'https://ai-backend.binwang.me/v0.2/couplet/{text}'
        async with ClientSession() as session:
            res = await session.get(url)
            res = await res.json()
            result = res['output'][0]
            await duilian.finish(f'上联：{msg}\n下联：{result}')


@cat_pic.handle()
async def cat_pic_handler(event: Union[GroupMessageEvent, MessageEvent]):
    if not cat_lmt.check(event.group_id or event.user_id):
        await cat_pic.finish(f'猫片冷却ing(剩余{cat_lmt.left_time(event.group_id or event.user_id)}秒)')
    else:
        cat_lmt.start_cd(event.group_id or event.user_id, 10)
        url = 'http://edgecats.net/'
        async with ClientSession() as session:
            res = await session.get(url)
            res = await res.read()
            await cat_pic.finish(MessageSegment.image(res))


@tcy_pic.handle()
async def tcy_pic_handler(event: Union[GroupMessageEvent, MessageEvent]):
    urls = [
        'https://www.dmoe.cc/random.php',
        'https://acg.toubiec.cn/random.php',
        'https://api.ixiaowai.cn/api/api.php'
    ]
    if not tcy_lmt.check(event.group_id or event.user_id):
        await tcy_pic.finish(f'二次元图片冷却ing(剩余{tcy_lmt.left_time(event.group_id or event.user_id)}秒)')
    else:
        tcy_lmt.start_cd(event.group_id or event.user_id, 5)
        async with ClientSession() as session:
            res = await session.get(random.choice(urls))
            res = await res.read()
            await cat_pic.finish(MessageSegment.image(res))
