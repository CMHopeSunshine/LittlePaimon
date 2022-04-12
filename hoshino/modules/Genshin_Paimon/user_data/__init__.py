from hoshino import MessageSegment, Service, trigger, priv, CanceledException,logger
from hoshino.typing import CQEvent, Message
from nonebot import message_preprocessor
from ..get_data import get_bind_game
from ..db_util import insert_public_cookie, update_private_cookie, delete_cookie_cache, delete_cookie, delete_private_cookie,update_last_query, reset_public_cookie
from ..util import check_cookie

help_msg='''
1.[ysb cookie]绑定你的私人cookie以开启高级功能
2.[删除ck]删除你的私人cookie
3.[添加公共ck cookie]添加公共cookie以供大众查询*仅管理员
'''
sv = Service('派蒙绑定', visible=False, enable_on_default=True, bundle='派蒙', help_=help_msg)

cookie_error_msg = '这个cookie无效哦，请旅行者确认是否正确\n1.ck要登录mys帐号后获取\n2.获取ck后不能退出登录\n3.ck至少要包含cookie_token和account_id两个参数\n4.建议在无痕模式下取'

@sv.on_prefix(('原神绑定','ysb'))
async def bind(bot,ev):
    cookie = ev.message.extract_plain_text().strip()
    if cookie == '':
        res = '''旅行者好呀，你可以直接用ys/ysa等指令附上uid来使用派蒙\n如果想看全部角色信息和实时便笺等功能，要把cookie给派蒙哦\ncookie获取方法：登录网页版米游社，在地址栏粘贴代码：\njavascript:(function(){prompt(document.domain,document.cookie)})();\n复制弹窗出来的字符串（手机要via或chrome浏览器才行）\n然后添加派蒙私聊发送ysb接刚刚复制的字符串，例如:ysb UM_distinctid=17d131d...\ncookie是账号重要安全信息，请确保机器人持有者可信赖！'''
        await bot.send(ev,res,at_sender=True)
    else:
        cookie_info, mys_id = await get_bind_game(cookie)
        if not cookie_info or cookie_info['retcode'] != 0:
            msg = cookie_error_msg
            if ev.detail_type != 'private':
                msg += '\n当前是在群聊里绑定，建议旅行者添加派蒙好友私聊绑定!'
            await bot.send(ev,msg,at_sender=True)
        else:
            for data in cookie_info['data']['list']:
                if data['game_id'] == 2:
                    uid = data['game_role_id']
                    nickname = data['nickname']
                    break
            if uid:
                await update_private_cookie(user_id=str(ev.user_id), uid=uid, mys_id=mys_id, cookie=cookie)
                await update_last_query(str(ev.user_id), uid, 'uid')
                await delete_cookie_cache(uid, key='uid', all=False)
                msg = f'{nickname}绑定成功啦!使用ys/ysa等指令和派蒙互动吧!'
                if ev.detail_type != 'private':
                    msg += '\n当前是在群聊里绑定，建议旅行者把cookie撤回哦!'
                await bot.send(ev,msg,at_sender=True)
                    
@sv.on_prefix('删除ck')
async def delete(bot,ev):
    user_id = str(ev.user_id)
    await delete_private_cookie(str(ev.user_id))
    await bot.send(ev, '派蒙把你的私人cookie都删除啦!', at_sender=True)

@sv.on_prefix('添加公共ck')
async def bing_public(bot, ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '只有管理员或主人才能添加公共cookie哦!')
        return
    cookie = ev.message.extract_plain_text().strip()
    if await check_cookie(cookie):
        await insert_public_cookie(cookie)
        await bot.send(ev, '公共cookie添加成功啦,派蒙开始工作!')
    else:
        await bot.send(ev, cookie_error_msg)

@sv.scheduled_job('cron', hour='0')
async def delete_cache():
    logger.info('---清空今日cookie缓存---')
    await delete_cookie_cache(all=True)
    logger.info('---清空今日cookie限制记录---')
    await reset_public_cookie()
