from hoshino import MessageSegment, Service, trigger, priv, CanceledException
from hoshino.typing import CQEvent, Message
from ..util import update_last_query_to_qq, bind_cookie, bind_public_cookie
from nonebot import message_preprocessor
from ..get_data import get_bind_game

sv = Service('原神绑定',visible=False,enable_on_default=True)

@sv.on_prefix(('原神绑定','ysb'))
async def bind(bot,ev):
    cookie = ev.message.extract_plain_text().strip()
    qq=str(ev.user_id)
    if cookie == '':
        res = '''旅行者好呀，你可以直接用ys/ysa等指令附上uid来使用派蒙\n如果想看全部角色信息和实时便笺等功能，要把cookie给派蒙哦\ncookie获取方法：登录网页版米游社，在地址栏粘贴代码：\njavascript:(function(){prompt(document.domain,document.cookie)})();\n复制弹窗出来的字符串（手机要via或chrome浏览器才行）\n然后添加派蒙私聊发送ysb接刚刚复制的字符串，例如:ysb UM_distinctid=17d131d...\ncookie是账号重要安全信息，请确保机器人持有者可信赖！'''
        await bot.send(ev,res,at_sender=True)
    else:
        cookie_info = await get_bind_game(cookie)
        if not cookie_info or cookie_info['retcode'] != 0:
            msg = '这cookie没有用哦，检查一下是不是复制错了或者过期了(试试重新登录米游社再获取)'
            if ev.detail_type != 'private':
                msg += '\n当前是在群聊里绑定，建议旅行者添加派蒙好友私聊绑定！'
            await bot.send(ev,msg,at_sender=True)
        else:
            for data in cookie_info['data']['list']:
                if data['game_id'] == 2:
                    uid = data['game_role_id']
                    nickname = data['nickname']
                    # level = data['level']
                    break
            if uid:
                await bind_cookie(qq,uid,cookie)
                msg = f'{nickname}绑定成功啦！使用ys/ysa等指令和派蒙互动吧！'
                if ev.detail_type != 'private':
                    msg += '\n当前是在群聊里绑定，建议旅行者把cookie撤回哦！'
                await bot.send(ev,msg,at_sender=True)
                    

@sv.on_prefix('添加公共ck')
async def bing_public(bot,ev):
    cookie = ev.message.extract_plain_text().strip()
    res = await bind_public_cookie(cookie)
    await bot.send(ev,res,at_sender=True)