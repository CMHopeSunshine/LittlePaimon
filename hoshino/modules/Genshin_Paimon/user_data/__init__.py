from hoshino import MessageSegment, Service, trigger, priv, CanceledException
from hoshino.typing import CQEvent, Message
from ..util import update_last_query_to_qq, bind_cookie
from nonebot import message_preprocessor

sv = Service('原神绑定',visible=False,enable_on_default=True)

private_prefix = []

# support private message
@message_preprocessor
async def private_handler(bot, ev, _):
    if ev.detail_type != 'private':
        return
    for t in trigger.chain:
        for service in t.find_handler(ev):
            sv = service.sv
            if sv in private_prefix:
                if priv.get_user_priv(ev) >= priv.NORMAL:
                    try:
                        await service.func(bot, ev)
                    except CanceledException:
                        raise
                    sv.logger.info(
                        f'Private Message {ev.message_id} triggered {service.func.__name__}.'
                    )

def support_private(sv):
    def wrap(func):
        private_prefix.append(sv)
        return func
    return wrap

@support_private(sv)
@sv.on_prefix(('原神绑定','ysb'))
async def bind(bot,ev):
    msg = ev.message.extract_plain_text().strip().split('#')
    qq=str(ev.user_id)
    if msg[0] == '':
        res = '''请旅行者用[ysb+uid]指令来绑定uid哦，例如ysb100000011\n如果想看全部角色信息和实时便笺等功能，要把cookie也给派蒙\ncookie的获取方法：登录网页版米游社，在地址栏粘贴这段代码：\njavascript:(function(){prompt(document.domain,document.cookie)})();\n弹出来的一大串字符就是cookie（手机要via或chrome浏览器才行）\n然后在uid后面加#和cookie来绑定,例如ysb100000011#cookie_token=asdqwf...'''
        await bot.send(ev,res,at_sender=True)
    elif len(msg) == 1:
        if len(msg[0]) == 9 and msg[0].isdigit():
            update_last_query_to_qq(qq, msg[0])
            await bot.send(ev,'成功绑定uid',at_sender=True)
        else:
            await bot.send(ev,'请把要绑定的合规uid一起给派蒙',at_sender=True)
    else:
        uid = msg[0]
        if len(msg[0]) != 9 or not msg[0].isdigit():
            await bot.send(ev,'uid是不是写错了呀？要9位数全数字的uid哦',at_sender=True)
            return
        cookie = msg[1]
        res = await bind_cookie(qq,uid,cookie)
        await bot.send(ev,res,at_sender=True)
