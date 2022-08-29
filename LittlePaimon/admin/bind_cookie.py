import datetime

from pywebio.input import *
from pywebio.output import *
from pywebio.platform import config
from pywebio.session import run_asyncio_coroutine

from LittlePaimon.utils import logger
from LittlePaimon.database.models import LastQuery, PrivateCookie
from LittlePaimon.utils.api import get_bind_game_info, get_stoken_by_cookie

css_style = 'body {background: #000000 url(https://static.cherishmoon.fun/blog/h-wallpaper/zhounianqing.png);} #input-container {background: rgba(0,0,0,0);} summary {background-color: rgba(255,255,255,1);} .markdown-body {background-color: rgba(255,255,255,1);}'


@config(title='小派蒙绑定原神Cookie', description='绑定Cookie', css_style=css_style)
async def bind_cookie_page():
    with put_collapse('获取Cookie的方法'):
        put_markdown('**重要提醒**：Cookie的作用相当于账号密码，非常重要，如是非可信任的机器人，请勿绑定！！')
        put_markdown('**方法**：详见[Cookie获取教程](https://docs.qq.com/doc/DQ3JLWk1vQVllZ2Z1)')
    data = await input_group('绑定Cookie', [
        input('QQ号', name='qq', required=True, validate=is_qq_number),
        textarea('米游社Cookie', name='cookie', required=True),
        checkbox(name='confirm', options=['我已知晓Cookie的重要性，确认绑定'], validate=is_confirm)
    ])
    result = await run_asyncio_coroutine(bind_cookie(data))
    popup('绑定结果', put_markdown(result))


def is_qq_number(qq: str):
    if not qq.isdigit():
        return '必须是合法的QQ号'


def is_cookie(cookie: str):
    if 'cookie_token' not in cookie or all(i not in cookie for i in ['account_id', 'login_uid', 'ltuid', 'stuid']):
        return 'Cookie必须包含cookie_token以及account_id、login_uid、ltuid、stuid其中之一'


def is_confirm(confirm: list):
    if not confirm:
        return '请先勾选确认'


async def bind_cookie(data: dict):
    if result := await get_bind_game_info(data['cookie']):
        game_name = result['nickname']
        game_uid = result['game_role_id']
        mys_id = result['mys_id']
        await LastQuery.update_or_create(user_id=str(data['qq']),
                                         defaults={'uid': game_uid, 'last_time': datetime.datetime.now()})
        logger.info('原神Cookie', '', {'用户': str(data['qq']), 'uid': game_uid}, '成功绑定cookie', True)
        if 'login_ticket' in data['cookie'] and (stoken := await get_stoken_by_cookie(data['cookie'])):
            await PrivateCookie.update_or_create(user_id=str(data['qq']), uid=game_uid, mys_id=mys_id,
                                                 defaults={'cookie': data['cookie'],
                                                           'stoken': f'stuid={mys_id};stoken={stoken};'})
            return f'QQ`{data["qq"]}`成功绑定原神玩家`{game_name}`-UID`{game_uid}`'
        else:
            await PrivateCookie.update_or_create(user_id=str(data['qq']), uid=game_uid, mys_id=mys_id,
                                                 defaults={'cookie': data['cookie']})
            return f'QQ`{data["qq"]}`成功绑定原神玩家`{game_name}`-UID`{game_uid}`\n但cookie中没有`login_ticket`或`login_ticket`无效，`米游币相关功能`无法使用哦'
    else:
        return '这个cookie**无效**，请确认是否正确\n请重新获取cookie后**刷新**本页面再次绑定'
