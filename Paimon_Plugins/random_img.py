import random
from nonebot import on_command, on_regex
from nonebot.params import RegexGroup
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from utils.config import config
from utils.auth_util import FreqLimiter
from utils.message_util import get_message_id
from utils.decorator import auto_withdraw

cat_lmt = FreqLimiter(config.paimon_cat_cd)
ecy_lmt = FreqLimiter(config.paimon_ecy_cd)
ys_lmt = FreqLimiter(config.paimon_ysp_cd)

cat_img = on_command('猫图', aliases={'来点猫片', '看看猫猫', '来个猫猫'}, priority=13, block=True)
ecy_img = on_regex(r'^来点(二次元|二刺螈|银发|兽耳|星空|竖屏|横屏)图?$', priority=13, block=True)
ys_img = on_command('原神壁纸', aliases={'来点原神图', '来点原神壁纸'}, priority=13, block=True)


@cat_img.handle()
async def cat_img_handler(event: MessageEvent):
    if not cat_lmt.check(get_message_id(event)):
        await cat_img.finish(f'猫片冷却ing(剩余{cat_lmt.left_time(get_message_id(event))}秒)')
    else:
        await cat_img.send('派蒙努力找图ing..请稍候...')
        cat_lmt.start_cd(get_message_id(event), config.paimon_cat_cd)
        url = 'http://edgecats.net/'
        await cat_img.finish(MessageSegment.image(file=url))


@ecy_img.handle()
@auto_withdraw(15)
async def ecy_img_handler(bot: Bot, event: MessageEvent, regexGroup=RegexGroup()):
    urls = [
        'https://www.dmoe.cc/random.php',
        'https://acg.toubiec.cn/random.php',
        'https://api.ixiaowai.cn/api/api.php',
        'https://iw233.cn/api.php?sort=iw233'
    ]
    img_type = regexGroup[0]
    if img_type in ['二次元', '二刺螈']:
        url = random.choice(urls)
    elif img_type == '银发':
        url = 'https://iw233.cn/api.php?sort=yin'
    elif img_type == '兽耳':
        url = 'https://iw233.cn/api.php?sort=cat'
    elif img_type == '星空':
        url = 'https://iw233.cn/api.php?sort=xing'
    elif img_type == '竖屏':
        url = 'https://iw233.cn/api.php?sort=mp'
    elif img_type == '横屏':
        url = 'https://iw233.cn/api.php?sort=pc'
    else:
        url = ''
    if not ecy_lmt.check(get_message_id(event)):
        await ecy_img.finish(f'二次元图片冷却ing(剩余{ecy_lmt.left_time(get_message_id(event))}秒)')
    elif url:
        await ecy_img.send('派蒙努力找图ing..请稍候...')
        ecy_lmt.start_cd(get_message_id(event), config.paimon_ecy_cd)
        return await ecy_img.send(MessageSegment.image(file=url))


@ys_img.handle()
@auto_withdraw(30)
async def ys_img_handler(event: MessageEvent):
    urls = [
        'https://api.dujin.org/img/yuanshen/',
        'https://api.dreamofice.cn/random-v0/img.php?game=ys'
    ]
    if not ys_lmt.check(get_message_id(event)):
        await ys_img.finish(f'原神壁纸冷却ing(剩余{ys_lmt.left_time(get_message_id(event))}秒)')
    else:
        await ys_img.send('派蒙努力找图ing..请稍候...')
        ys_lmt.start_cd(get_message_id(event), config.paimon_ysp_cd)
        await ys_img.finish(MessageSegment.image(file=random.choice(urls)))