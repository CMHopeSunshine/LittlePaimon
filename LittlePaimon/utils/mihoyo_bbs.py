import hashlib
import json
import random
import string
import time
import re
from typing import Optional, Union, Tuple, List, Literal
from nonebot import logger

from .requests import aiorequests
from LittlePaimon.database.models import PublicCookie, PrivateCookie, CookieCache
from tortoise.queryset import Q

# MIHOYO_API = 'https://api-takumi-record.mihoyo.com/'
# MIHOYO_API_OLD = 'https://api-takumi.mihoyo.com/'
ABYSS_API = 'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/spiralAbyss'
PLAYER_CARD_API = 'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/index'
CHARACTER_DETAIL_API = 'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/character'
CHARACTER_SKILL_API = 'https://api-takumi.mihoyo.com/event/e20200928calculate/v1/sync/avatar/detail'
MONTH_INFO_API = 'https://hk4e-api.mihoyo.com/event/ys_ledger/monthInfo'
DAILY_NOTE_API = 'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/dailyNote'
GAME_RECORD_API = 'https://api-takumi-record.mihoyo.com/game_record/card/wapi/getGameRecordCard'
SIGN_INFO_API = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/info'
SIGN_REWARD_API = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/home'
SIGN_ACTION_API = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'


def md5(text: str) -> str:
    """
    md5加密
    :param text: 文本
    :return: md5加密后的文本
    """
    md5_ = hashlib.md5()
    md5_.update(text.encode())
    return md5_.hexdigest()


def random_hex(length: int) -> str:
    """
    生成指定长度的随机字符串
    :param length: 长度
    :return: 随机字符串
    """
    result = hex(random.randint(0, 16 ** length)).replace('0x', '').upper()
    if len(result) < length:
        result = '0' * (length - len(result)) + result
    return result


def get_ds(q: str = "", b: str = None) -> str:
    """
    生成米游社headers的ds_token，对应版本2.11.1
    :param q: 查询
    :param b: 请求体
    :return: ds_token
    """
    if b:
        br = json.dumps(b)
    else:
        br = ""
    s = "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs"
    t = str(int(time.time()))
    r = str(random.randint(100000, 200000))
    c = md5("salt=" + s + "&t=" + t + "&r=" + r + "&b=" + br + "&q=" + q)
    return f"{t},{r},{c}"


def get_old_version_ds() -> str:
    """
    生成米游社旧版本headers的ds_token
    """
    s = 'h8w582wxwgqvahcdkpvdhbh2w9casgfl'
    t = str(int(time.time()))
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c = md5("salt=" + s + "&t=" + t + "&r=" + r)
    return f"{t},{r},{c}"


def mihoyo_headers(cookie, q='', b=None) -> dict:
    """
    生成米游社headers
    :param cookie: cookie
    :param q: 查询
    :param b: 请求体
    :return: headers
    """
    return {
        'DS':                get_ds(q, b),
        'Origin':            'https://webstatic.mihoyo.com',
        'Cookie':            cookie,
        'x-rpc-app_version': "2.11.1",
        'User-Agent':        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS '
                             'X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer':           'https://webstatic.mihoyo.com/'
    }


def mihoyo_sign_headers(cookie: str) -> dict:
    """
    生成米游社签到headers
    :param cookie: cookie
    :return: headers
    """
    return {
        'User_Agent':        'Mozilla/5.0 (Linux; Android 10; MIX 2 Build/QKQ1.190825.002; wv) AppleWebKit/537.36 ('
                             'KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.101 Mobile Safari/537.36 '
                             'miHoYoBBS/2.3.0',
        'Cookie':            cookie,
        'x-rpc-device_id':   random_hex(32),
        'Origin':            'https://webstatic.mihoyo.com',
        'X_Requested_With':  'com.mihoyo.hyperion',
        'DS':                get_old_version_ds(),
        'x-rpc-client_type': '5',
        'Referer':           'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id'
                             '=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon',
        'x-rpc-app_version': '2.3.0'
    }


async def check_retcode(data: dict, cookie_info, cookie_type: str, user_id: str, uid: str) -> bool:
    """
    检查数据响应状态冰进行响应处理
    :param data: 数据
    :param cookie_info: cookie信息
    :param cookie_type: cookie类型
    :param user_id: 用户id
    :param uid: 原神uid
    :return: 数据是否有效
    """
    if not data:
        return False
    if data['retcode'] == 10001 or data['retcode'] == -100:
        if cookie_type == 'private':
            if cookie_info.status == 1:
                cookie_info.status = 0
                await cookie_info.save()
                # await PrivateCookie.filter(cookie=cookie_info.cookie, user_id=user_id).update(status=0)
                logger.warning(f'用户{user_id}的私人cookie{uid}疑似失效')
            elif cookie_info.status == 0:
                # await PrivateCookie.filter(cookie=cookie_info.cookie, user_id=user_id).delete()
                await cookie_info.delete()
                # TODO 提醒超级用户
                logger.warning(f'用户{user_id}的私人cookie{uid}连续失效，已删除')
        else:
            await CookieCache.filter(cookie=cookie_info.cookie).delete()
            # await PublicCookie.filter(cookie=cookie_info.cookie, cid=cookie_info.cid).delete()
            await cookie_info.delete()
            # TODO 提醒超级用户
            logger.warning(f'{cookie_info.cid}号公共cookie已失效，已删除')
        return False
    elif data['retcode'] == 10101:
        cookie_info.status = 2
        await cookie_info.save()
        if cookie_info == 'private':
            logger.warning(f'用户{user_id}的私人cookie{uid}已达到每日30次查询上限')
            # await PrivateCookie.filter(cookie=cookie_info.cookie, user_id=user_id).update(status=2)
        else:
            logger.warning(f'{cookie_info["cid"]}号公共cookie已达到每日30次查询上限')
            # await PublicCookie.filter(cookie=cookie_info['cookie'], cid=cookie_info['cid']).update(status=2)
        return False
    else:
        await CookieCache.update_or_create(uid=uid, defaults={'cookie': cookie_info.cookie})
        return True


async def get_cookie(user_id: str, uid: str, check: bool = True, own: bool = False):
    """
    获取可用的cookie
    :param user_id: 用户id
    :param uid: 原神uid
    :param check: 是否获取疑似失效的cookie
    :param own: 是否只获取和uid对应的cookie
    :return:
    """
    if check:
        q = Q(status=1) | Q(status=0)
    else:
        q = Q(status=1)
    if private_cookie := await PrivateCookie.filter(Q(Q(q) & Q(user_id=user_id) & Q(uid=uid))).first():
        return private_cookie, 'private'
    elif not own:
        if cache_cookie := await CookieCache.get_or_none(uid=uid):
            return cache_cookie, 'cache'
        elif private_cookie := await PrivateCookie.filter(Q(Q(q) & Q(user_id=user_id))).first():
            return private_cookie, 'private'
        else:
            return await PublicCookie.filter(Q(q)).first(), 'public'
    else:
        return None, ''


async def get_bind_game_info(cookie) -> Optional[dict]:
    """
    通过cookie，获取米游社绑定的原神游戏信息
    :param cookie: cookie
    :return: 原神信息
    """
    if mys_id := re.search(r'(account_id|ltuid|stuid|login_uid)=(\d*)', cookie):
        mys_id = mys_id.group(2)
        data = (await aiorequests.get(url=GAME_RECORD_API,
                                      headers=mihoyo_headers(cookie, f'uid={mys_id}'),
                                      params={
                                          'uid': mys_id
                                      })).json()
        if data['retcode'] == 0:
            for game_data in data['data']['list']:
                if game_data['game_id'] == 2:
                    return game_data
    return None


async def get_mihoyo_public_data(
        uid: str,
        user_id: Optional[str],
        mode: Literal['abyss', 'player_card', 'role_detail', 'role_skill'],
        schedule_type: Optional[str] = '1',
        role_id: Optional[str] = '10000023'):
    server_id = "cn_qd01" if uid[0] == '5' else "cn_gf01"
    check = True
    while True:
        cookie_info, cookie_type = await get_cookie(user_id, uid, check)
        check = False
        if not cookie_info:
            return '无可用cookie'
        if mode == 'abyss':
            data = aiorequests.get(url=ABYSS_API,
                                   headers=mihoyo_headers(
                                       q=f'role_id={uid}&schedule_type={schedule_type}&server={server_id}',
                                       cookie=cookie_info.cookie),
                                   params={
                                       "schedule_type": schedule_type,
                                       "role_id":       uid,
                                       "server":        server_id}
                                   )
        elif mode == 'player_card':
            data = await aiorequests.get(url=PLAYER_CARD_API,
                                         headers=mihoyo_headers(q=f'role_id={uid}&server={server_id}',
                                                                cookie=cookie_info.cookie),
                                         params={
                                             'server':  server_id,
                                             'role_id': uid
                                         })
        elif mode == 'role_detail':
            json_data = {
                "server":        server_id,
                "role_id":       uid,
                "character_ids": []
            }
            data = await aiorequests.post(url=CHARACTER_DETAIL_API,
                                          headers=mihoyo_headers(b=json_data, cookie=cookie_info.cookie),
                                          json=json_data)
        elif mode == 'role_skill':
            data = await aiorequests.get(url=CHARACTER_SKILL_API,
                                         headers=mihoyo_headers(q=f'uid={uid}&region={server_id}&avatar_id={role_id}',
                                                                cookie=cookie_info.cookie),
                                         params={
                                             "region":    server_id,
                                             "uid":       uid,
                                             "avatar_id": role_id}
                                         )
        else:
            data = None
        data = data.json() if data else {}
        if await check_retcode(data, cookie_info, cookie_type, user_id, uid):
            return data


async def get_mihoyo_private_data(
        uid: str,
        user_id: Optional[str],
        mode: Literal['role_skill', 'month_info', 'daily_note'],
        role_id: Optional[str] = '10000023',
        month: Optional[str] = 1):
    server_id = "cn_qd01" if uid[0] == '5' else "cn_gf01"
    cookie_info, _ = await get_cookie(user_id, uid, True, True)
    if not cookie_info:
        return '未绑定私人cookie'
    if mode == 'role_skill':
        data = await aiorequests.get(url=CHARACTER_SKILL_API,
                                     headers=mihoyo_headers(q=f'uid={uid}&region={server_id}&avatar_id={role_id}',
                                                            cookie=cookie_info.cookie),
                                     params={
                                         "region":    server_id,
                                         "uid":       uid,
                                         "avatar_id": role_id}
                                     )
    elif mode == 'month_info':
        data = await aiorequests.get(url=MONTH_INFO_API,
                                     headers=mihoyo_headers(q=f'month={month}&bind_uid={uid}&bind_region={server_id}',
                                                            cookie=cookie_info.cookie),
                                     params={
                                         "month":       month,
                                         "bind_uid":    uid,
                                         "bind_region": server_id
                                     })
    elif mode == 'daily_note':
        data = await aiorequests.get(url=DAILY_NOTE_API,
                                     headers=mihoyo_headers(q=f'role_id={uid}&server={server_id}',
                                                            cookie=cookie_info.cookie),
                                     params={
                                         "server":  server_id,
                                         "role_id": uid
                                     })
    elif mode == 'sign_info':
        data = await aiorequests.get(url=SIGN_INFO_API,
                                     headers={
                                         'x-rpc-app_version': '2.11.1',
                                         'x-rpc-client_type': '5',
                                         'Origin':            'https://webstatic.mihoyo.com',
                                         'Referer':           'https://webstatic.mihoyo.com/',
                                         'Cookie':            cookie_info.cookie,
                                         'User-Agent':        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS '
                                                              'X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
                                     },
                                     params={
                                         'act_id': 'e202009291139501',
                                         'region': server_id,
                                         'uid':    uid
                                     })
    elif mode == 'sign_action':
        data = await aiorequests.post(url=SIGN_ACTION_API,
                                      headers=mihoyo_sign_headers(cookie_info.cookie),
                                      json_data={
                                          'act_id': 'e202009291139501',
                                          'uid':    uid,
                                          'region': server_id
                                      })
    else:
        data = None
    data = data.json() if data else {}
    if await check_retcode(data, cookie_info, 'private', user_id, uid):
        return data
    else:
        return 'cookie疑似失效'


async def get_sign_reward_list() -> dict:
    headers = {
        'x-rpc-app_version': '2.11.1',
        'User-Agent':        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 ('
                             'KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer':           'https://webstatic.mihoyo.com/'
    }
    resp = await aiorequests.get(url=SIGN_REWARD_API,
                                 headers=headers,
                                 params={
                                     'act_id': 'e202009291139501'
                                 })
    data = resp.json()
    return data


async def get_stoken_by_cookie(cookie: str) -> Optional[str]:
    bbs_cookie_url = 'https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket={}'
    bbs_cookie_url2 = 'https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={}&token_types=3&uid={}'

    if login_ticket := re.search('login_ticket=([0-9a-zA-Z]+)', cookie):
        data = (await aiorequests.get(url=bbs_cookie_url.format(login_ticket.group(0).split('=')[1]))).json()
        if '成功' in data['data']['msg']:
            stuid = data['data']['cookie_info']['account_id']
            data2 = (
                await aiorequests.get(url=bbs_cookie_url2.format(login_ticket.group().split('=')[1], stuid))).json()
            return data2['data']['list'][0]['token']
        else:
            return None
    return None
