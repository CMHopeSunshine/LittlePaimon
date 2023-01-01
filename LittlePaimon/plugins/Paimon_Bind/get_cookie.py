# main code from lulu: https://github.com/lulu666lulu
import asyncio
import contextlib
import datetime
import json
import random
import time
import uuid
import base64
from hashlib import md5
from io import BytesIO
from string import ascii_letters
from string import digits

import qrcode
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from nonebot import on_command, get_bot, get_app
from nonebot.adapters.onebot.v11 import Bot, MessageSegment, MessageEvent, GroupMessageEvent

from LittlePaimon.config import config
from LittlePaimon.database.models import PrivateCookie, LastQuery
from LittlePaimon.utils import NICKNAME
from LittlePaimon.utils.requests import aiorequests
from LittlePaimon.utils.scheduler import scheduler
from LittlePaimon.utils.api import get_bind_game_info
from LittlePaimon.utils.message import fullmatch_rule

CN_DS_SALT = 'JwYDpKvLj6MrMqqYU6jTKF17KNO2PXoS'
bind_tips = '绑定方法二选一：\n1.通过米游社扫码绑定：\n请发送指令[原神扫码绑定]\n2.通过Cookie绑定：获取教程\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1\n获取后，使用[ysb cookie]指令绑定'
bind_tips_web = '绑定方法二选一：\n1.通过米游社扫码绑定：\n请发送指令[原神扫码绑定]\n2.通过Cookie绑定：获取教程\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1\n获取后，使用[ysb cookie]指令绑定或前往{cookie_web_url}网页添加绑定'

running_login_data = {}


def md5_(self) -> str:
    return md5(self.encode()).hexdigest()


def get_ds(body=None, query=None) -> str:
    t = int(time.time())
    r = ''.join(random.choices(ascii_letters, k=6))
    b = json.dumps(body) if body else ''
    q = '&'.join((f"{k}={v}" for k, v in sorted(query.items()))) if query else ''
    h = md5_(f"salt={CN_DS_SALT}&t={t}&r={r}&b={b}&q={q}")
    return f"{t},{r},{h}"


async def get_stoken(aigis: str = '', data: dict = None):
    if data is None:
        data = {}
    resp = await aiorequests.post('https://passport-api.mihoyo.com/account/ma-cn-session/app/getTokenByGameToken',
                                  headers={'x-rpc-app_version':  '2.41.0',
                                           'DS':                 get_ds(data),
                                           'x-rpc-aigis':        aigis,
                                           'Content-Type':       'application/json',
                                           'Accept':             'application/json',
                                           'x-rpc-game_biz':     'bbs_cn',
                                           'x-rpc-sys_version':  '11',
                                           'x-rpc-device_id':    uuid.uuid4().hex,
                                           'x-rpc-device_fp':    ''.join(
                                               random.choices((ascii_letters + digits), k=13)),
                                           'x-rpc-device_name':  'Chrome 108.0.0.0',
                                           'x-rpc-device_model': 'Windows 10 64-bit',
                                           'x-rpc-app_id':       'bll8iq97cem8',
                                           'x-rpc-client_type':  '4',
                                           'User-Agent':         'okhttp/4.8.0'},
                                  json=data)
    return resp.json()


def generate_qrcode(url):
    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10,
                       border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    bio = BytesIO()
    img.save(bio)
    return f'base64://{base64.b64encode(bio.getvalue()).decode()}'


async def create_login_data():
    device_id = ''.join(random.choices((ascii_letters + digits), k=64))
    app_id = '4'
    data = {'app_id': app_id,
            'device': device_id}
    res = await aiorequests.post('https://hk4e-sdk.mihoyo.com/hk4e_cn/combo/panda/qrcode/fetch?',
                                 json=data)
    url = res.json()['data']['url']
    ticket = url.split('ticket=')[1]
    return {'app_id': app_id,
            'ticket': ticket,
            'device': device_id,
            'url':    url}


async def check_login(login_data: dict):
    data = {'app_id': login_data['app_id'],
            'ticket': login_data['ticket'],
            'device': login_data['device']}
    res = await aiorequests.post('https://hk4e-sdk.mihoyo.com/hk4e_cn/combo/panda/qrcode/query?',
                                 json=data)
    return res.json()


async def get_cookie_token(game_token: dict):
    res = await aiorequests.get(
        f"https://api-takumi.mihoyo.com/auth/api/getCookieAccountInfoByGameToken?game_token={game_token['token']}&account_id={game_token['uid']}")
    return res.json()


qrcode_bind = on_command('原神扫码绑定', aliases={'原神扫码登录', '原神扫码登陆'}, priority=1, block=True,
                         rule=fullmatch_rule,
                         state={
                             'pm_name':        '原神扫码绑定',
                             'pm_description': '通过米游社扫码的方式绑定原神Cookie',
                             'pm_usage':       '原神扫码绑定',
                             'pm_priority':    1
                         })


@qrcode_bind.handle()
async def _(event: MessageEvent):  # sourcery skip: use-fstring-for-concatenation
    if str(event.user_id) in running_login_data:
        await qrcode_bind.finish('你已经在绑定中了，请扫描上一次的二维码')
    login_data = await create_login_data()
    running_login_data[str(event.user_id)] = login_data
    img_b64 = generate_qrcode(login_data['url'])
    running_login_data[str(event.user_id)]['img_b64'] = img_b64
    img = f'二维码链接：{config.CookieWeb_url}/qrcode?user_id={event.user_id}' if config.qrcode_bind_use_url else MessageSegment.image(img_b64)
    msg_data = await qrcode_bind.send(
        img + f'\n请在3分钟内使用米游社扫码并确认进行绑定。\n注意：1.扫码即代表你同意将Cookie信息授权给{NICKNAME}\n2.扫码时会提示登录原神，实际不会把你顶掉原神\n3.其他人请不要乱扫，否则会将你的账号绑到TA身上！',
        at_sender=True)
    running_login_data[str(event.user_id)]['msg_id'] = msg_data['message_id']
    if isinstance(event, GroupMessageEvent):
        running_login_data[str(event.user_id)]['group_id'] = event.group_id
    elif event.message_type == 'guild':
        running_login_data[str(event.user_id)]['guild_id'] = event.guild_id
        running_login_data[str(event.user_id)]['channel_id'] = event.channel_id
    running_login_data[str(event.user_id)]['bot_id'] = event.self_id
    running_login_data[str(event.user_id)]['nickname'] = event.sender.card or event.sender.nickname


@scheduler.scheduled_job('cron', second='*/10', misfire_grace_time=10)
async def check_qrcode():
    with contextlib.suppress(RuntimeError):
        for user_id, data in running_login_data.items():
            send_msg = None
            status_data = await check_login(data)
            if status_data['retcode'] != 0:
                send_msg = '绑定二维码已过期，请重新发送扫码绑定指令'
                running_login_data.pop(user_id)
            elif status_data['data']['stat'] == 'Confirmed':
                game_token = json.loads(status_data['data']['payload']['raw'])
                running_login_data.pop(user_id)
                cookie_token_data = await get_cookie_token(game_token)
                stoken_data = await get_stoken(data={'account_id': int(game_token['uid']),
                                                     'game_token': game_token['token']})
                mys_id = stoken_data['data']['user_info']['aid']
                mid = stoken_data['data']['user_info']['mid']
                cookie_token = cookie_token_data['data']['cookie_token']
                stoken = stoken_data['data']['token']['token']
                if game_info := await get_bind_game_info(f"account_id={mys_id};cookie_token={cookie_token}", mys_id):
                    if not game_info['list']:
                        send_msg = '该账号尚未绑定任何游戏，请确认扫码的账号无误'
                    elif not (genshin_games := [{'uid': game['game_role_id'], 'nickname': game['nickname']} for game in
                                                game_info['list'] if game['game_id'] == 2]):
                        send_msg = '该账号尚未绑定原神，请确认扫码的账号无误'
                    else:
                        send_msg = '成功绑定原神账号：'
                        for info in genshin_games:
                            send_msg += f'{info["nickname"]}({info["uid"]}) '
                            await PrivateCookie.update_or_create(user_id=user_id, uid=info['uid'], mys_id=mys_id,
                                                                 defaults={
                                                                     'cookie': f"account_id={mys_id};cookie_token={cookie_token}",
                                                                     'stoken': f'stuid={mys_id};stoken={stoken};mid={mid};'})
                        send_msg = send_msg.strip()
                        await LastQuery.update_or_create(user_id=user_id,
                                                         defaults={'uid':       genshin_games[0]['uid'],
                                                                   'last_time': datetime.datetime.now()})
            if send_msg:
                bot: Bot = get_bot(str(data['bot_id']))
                if 'group_id' in data:
                    await bot.send_group_msg(group_id=data['group_id'],
                                             message=MessageSegment.reply(data['msg_id']) + MessageSegment.at(
                                                 int(user_id)) + send_msg)
                elif 'guild_id' in data:
                    await bot.send_guild_channel_msg(guild_id=data['guild_id'], channel_id=data['channel_id'],
                                                     message=MessageSegment.at(int(user_id)) + send_msg)
                else:
                    await bot.send_private_msg(user_id=int(user_id),
                                               message=MessageSegment.reply(data['msg_id']) + send_msg)
            if not running_login_data:
                break
            await asyncio.sleep(1)


app: FastAPI = get_app()


@app.get('/LittlePaimon/cookie/qrcode')
async def qrcode_img_url(user_id: str):
    if not config.qrcode_bind_use_url:
        return {'status': 'error', 'msg': '请在QQ内查看二维码'}
    if user_id not in running_login_data:
        return {'status': 'error', 'msg': '二维码不存在'}
    img_base64 = running_login_data[user_id]['img_b64'].lstrip('base64://')
    return StreamingResponse(BytesIO(base64.b64decode(img_base64)), media_type='image/png')
