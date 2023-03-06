import random

from LittlePaimon.utils.tool import FreqLimiter
from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from nonebot.params import RegexGroup
from nonebot.plugin import PluginMetadata
import httpx

# def auto_withdraw(seconds: int = -1):
#     def wrapper(func):

#         @functools.wraps(func)
#         async def wrapped(**kwargs):
#             try:
#                 message_id = await func(**kwargs)
#                 if message_id and seconds >= 1:
#                     await asyncio.sleep(seconds)
#                     await get_bot().delete_msg(message_id=message_id['message_id'])
#             except Exception as e:
#                 raise e
#         return wrapped
#     return wrapper
    
def get_message_id(event):
    if event.message_type == 'private':
        return event.user_id
    elif event.message_type == 'group':
        return event.group_id
    elif event.message_type == 'guild':
        return event.channel_id


__plugin_meta__ = PluginMetadata(
    name="随机图片",
    description="从各随机图片接口获取一张图片",
    usage=(
        "来点猫片\n"
        "来点二次元图  来点<银发|兽耳|星空|竖屏|横屏>\n"
        "来点原神图"
    ),
    extra={
        'type':    '娱乐',
        'range':   ['private', 'group', 'guild'],
        "author":  "惜月 <277073121@qq.com>",
        "version": "1.1.0",
    },
)

# cat_lmt = FreqLimiter(60)
# ecy_lmt = FreqLimiter(60)
# ys_lmt = FreqLimiter(60)

cat_img = on_command('猫图', aliases={'来点猫片', '看看猫猫', '来个猫猫'}, priority=13, block=True)
cat_img.__paimon_help__ = {
    "usage":     "来点猫片",
    "introduce": "谁会拒绝可爱的猫猫图呢",
    "priority": 13
}
ecy_img = on_regex(r'^来点(二次元|二刺螈|银发|兽耳|星空|竖屏|横屏)图?$', priority=13, block=True)
ecy_img.__paimon_help__ = {
    "usage":     "来点<类型>图",
    "introduce": "懂得都懂，类型有原神|二次元|二刺螈|银发|兽耳|星空|竖屏|横屏",
    "priority": 13
}
ys_img = on_command('原神壁纸', aliases={'来点原神图', '来点原神壁纸'}, priority=13, block=True)


@cat_img.handle()
async def cat_img_handler(event: MessageEvent):
    await cat_img.send('派蒙努力找图ing..请稍候...')
    url = 'http://edgecats.net/'
    await cat_img.finish(MessageSegment.image(file=url))


@ecy_img.handle()
#@auto_withdraw(15)
async def ecy_img_handler(bot: Bot, event: MessageEvent, regexGroup=RegexGroup()):
    urls = [
        'https://www.dmoe.cc/random.php',
        # 'https://acg.toubiec.cn/random.php',
        'https://api.ixiaowai.cn/api/api.php',
        'https://dev.iw233.cn/api.php?sort=iw233'
    ]
    img_type = regexGroup[0]
    if img_type in ['二次元', '二刺螈']:
        url = random.choice(urls)
    elif img_type == '银发':
        url = 'https://dev.iw233.cn/api.php?sort=yin'
    elif img_type == '兽耳':
        url = 'https://dev.iw233.cn/api.php?sort=cat'
    elif img_type == '星空':
        url = 'https://dev.iw233.cn/api.php?sort=xing'
    elif img_type == '竖屏':
        url = 'https://dev.iw233.cn/api.php?sort=mp'
    elif img_type == '横屏':
        url = 'https://dev.iw233.cn/api.php?sort=pc'
    else:
        url = ''
    if url:
        next_get=httpx.get(url=url)
        async with httpx.AsyncClient() as client:
            header = {'referer':"https://weibo.com/"}
            res = await client.get(url=next_get.next_request.url,headers=header)
            await ecy_img.send('派蒙努力找图ing..请稍候...')
            return await ecy_img.send(MessageSegment.image(file=res.content))


@ys_img.handle()
#@auto_withdraw(30)
async def ys_img_handler(event: MessageEvent):
    urls = [
        'https://api.dreamofice.cn/random-v0/img.php?game=ys'
    ]
    # if not ys_lmt.check(get_message_id(event)):
    #     await ys_img.finish(f'原神壁纸冷却ing(剩余{ys_lmt.left_time(get_message_id(event))}秒)')
    # else:
    await ys_img.send('派蒙努力找图ing..请稍候...')
    await ys_img.finish(MessageSegment.image(file=random.choice(urls)))