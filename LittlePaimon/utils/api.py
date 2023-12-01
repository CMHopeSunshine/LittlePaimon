import contextlib
import hashlib
import json
import random
import string
import time
from typing import Optional, Literal, Union, Tuple

from nonebot import logger as nb_logger
from tortoise.queryset import Q

from LittlePaimon.config import config
from LittlePaimon.database import PublicCookie, PrivateCookie, CookieCache
from LittlePaimon.utils import logger
from .requests import aiorequests

# MIHOYO_API = 'https://api-takumi-record.mihoyo.com/'
# MIHOYO_API_OLD = 'https://api-takumi.mihoyo.com/'
ABYSS_API = (
    'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/spiralAbyss'
)
PLAYER_CARD_API = (
    'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/index'
)
CHARACTER_DETAIL_API = (
    'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/character'
)
CHARACTER_SKILL_API = (
    'https://api-takumi.mihoyo.com/event/e20200928calculate/v1/sync/avatar/detail'
)
MONTH_INFO_API = 'https://hk4e-api.mihoyo.com/event/ys_ledger/monthInfo'
DAILY_NOTE_API = (
    'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/dailyNote'
)
GAME_RECORD_API = (
    'https://api-takumi-record.mihoyo.com/game_record/card/wapi/getGameRecordCard'
)
SIGN_INFO_API = 'https://api-takumi.mihoyo.com/event/luna/info'
SIGN_REWARD_API = 'https://api-takumi.mihoyo.com/event/luna/home'
SIGN_ACTION_API = 'https://api-takumi.mihoyo.com/event/luna/sign'
AUTHKEY_API = 'https://api-takumi.mihoyo.com/binding/api/genAuthKey'
STOKEN_API = 'https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket'
COOKIE_TOKEN_API = 'https://api-takumi.mihoyo.com/auth/api/getCookieAccountInfoBySToken'
LOGIN_TICKET_INFO_API = (
    'https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket'
)


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
    result = hex(random.randint(0, 16**length)).replace('0x', '').upper()
    if len(result) < length:
        result = '0' * (length - len(result)) + result
    return result


def random_text(length: int) -> str:
    """
    生成指定长度的随机字符串

    :param length: 长度
    :return: 随机字符串
    """
    return ''.join(random.sample(string.ascii_lowercase + string.digits, length))


def get_ds(q: str = '', b: dict = None, mhy_bbs_sign: bool = False) -> str:
    """
    生成米游社headers的ds_token

    :param q: 查询
    :param b: 请求体
    :param mhy_bbs_sign: 是否为米游社讨论区签到
    :return: ds_token
    """
    br = json.dumps(b) if b else ''
    if mhy_bbs_sign:
        s = 't0qEgfub6cvueAPgR5m9aQWWVciEer7v'
    else:
        s = 'xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs'
    t = str(int(time.time()))
    r = str(random.randint(100000, 200000))
    c = md5(f'salt={s}&t={t}&r={r}&b={br}&q={q}')
    return f'{t},{r},{c}'


def get_old_version_ds(mhy_bbs: bool = False) -> str:
    """
    生成米游社旧版本headers的ds_token
    """
    if mhy_bbs:
        s = 'N50pqm7FSy2AkFz2B3TqtuZMJ5TOl3Ep'
    else:
        s = 'z8DRIUjNDT7IT5IZXvrUAxyupA1peND9'
    t = str(int(time.time()))
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c = md5(f"salt={s}&t={t}&r={r}")
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
        'DS': get_ds(q, b),
        'Origin': 'https://webstatic.mihoyo.com',
        'Cookie': cookie,
        'x-rpc-app_version': "2.11.1",
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS '
        'X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer': 'https://webstatic.mihoyo.com/',
    }


def mihoyo_sign_headers(cookie: str, extra_headers: Optional[dict] = None) -> dict:
    """
    生成米游社签到headers
        :param cookie: cookie
        :param extra_headers: 额外的headers参数
        :return: headers
    """
    header = {
        'User_Agent': 'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36 miHoYoBBS/2.35.2',
        'Cookie': cookie,
        'x-rpc-device_id': random_hex(32),
        'Origin': 'https://act.mihoyo.com',
        'X_Requested_With': 'com.mihoyo.hyperion',
        'DS': get_old_version_ds(mhy_bbs=True),
        'x-rpc-client_type': '5',
        'Referer': 'https://act.mihoyo.com',
        "x-rpc-signgame":"hk4e",
        'x-rpc-app_version': '2.35.2',
    }
    if extra_headers:
        header.update(extra_headers)
    return header


async def check_retcode(data: dict, cookie_info, user_id: str, uid: str) -> bool:
    """
    检查数据响应状态冰进行响应处理
        :param data: 数据
        :param cookie_info: cookie信息
        :param user_id: 用户id
        :param uid: 原神uid
        :return: 数据是否有效
    """
    if not data:
        return False
    if data['retcode'] in [10001, -100]:
        if isinstance(cookie_info, PrivateCookie):
            if cookie_info.status == 1:
                cookie_info.status = 0
                await cookie_info.save()
                logger.info('原神Cookie', f'用户<m>{user_id}</m>的私人cookie<m>{uid}</m>疑似失效')
            elif cookie_info.status == 0:
                await cookie_info.delete()
                logger.info(
                    '原神Cookie',
                    f'用户<m>{user_id}</m>的私人cookie<m>{uid}</m>连续失效，<r>已删除</r>',
                )
        elif isinstance(cookie_info, PublicCookie):
            await CookieCache.filter(cookie=cookie_info.cookie).delete()
            await cookie_info.delete()
            logger.info('原神Cookie', f'<m>{cookie_info.id}</m>号公共cookie已失效，<r>已删除</r>')
        else:
            await PublicCookie.filter(cookie=cookie_info.cookie).delete()
            await cookie_info.delete()
            logger.info(
                '原神Cookie', f'UID<m>{cookie_info.uid}</m>使用的缓存cookie已失效，<r>已删除</r>'
            )
        return False
    elif data['retcode'] == 10101:
        cookie_info.status = 2
        if isinstance(cookie_info, PrivateCookie):
            cookie_info.status = 2
            await cookie_info.save()
            logger.info(
                '原神Cookie', f'用户<m>{user_id}</m>的私人cookie<m>{uid}</m>已达到每日30次查询上限'
            )
        elif isinstance(cookie_info, PublicCookie):
            cookie_info.status = 2
            await cookie_info.save()
            logger.info('原神Cookie', f'<m>{cookie_info.id}</m>号公共cookie已达到每日30次查询上限')
        else:
            await PublicCookie.filter(cookie=cookie_info.cookie).update(status=2)
            await cookie_info.delete()
            logger.info(
                '原神Cookie', f'UID<m>{cookie_info.uid}</m>使用的缓存cookie已达到每日30次查询上限'
            )
        return False
    else:
        if isinstance(cookie_info, PublicCookie) and data['retcode'] != 1034:
            await CookieCache.update_or_create(
                uid=uid, defaults={'cookie': cookie_info.cookie}
            )
        return True


async def get_cookie(
    user_id: str, uid: str, check: bool = True, own: bool = False
) -> Union[None, PrivateCookie, PublicCookie, CookieCache]:
    """
    获取可用的cookie
        :param user_id: 用户id
        :param uid: 原神uid
        :param check: 是否获取疑似失效的cookie
        :param own: 是否只获取和uid对应的cookie
    """
    query = Q(status=1) | Q(status=0) if check else Q(status=1)
    if private_cookie := await PrivateCookie.filter(
        Q(Q(query) & Q(user_id=user_id) & Q(uid=uid))
    ).first():
        return private_cookie
    elif not own:
        if cache_cookie := await CookieCache.get_or_none(uid=uid):
            return cache_cookie
        elif private_cookie := await PrivateCookie.filter(
            Q(Q(query) & Q(user_id=user_id))
        ).first():
            return private_cookie
        else:
            return await PublicCookie.filter(Q(query)).first()
    else:
        return None


async def get_bind_game_info(cookie: str, mys_id: str):
    """
    通过cookie，获取米游社绑定的原神游戏信息
    :param cookie: cookie
    :param mys_id: 米游社id
    :return: 原神信息
    """
    with contextlib.suppress(Exception):
        data = await aiorequests.get(
            url=GAME_RECORD_API,
            headers=mihoyo_headers(cookie, f'uid={mys_id}'),
            params={'uid': mys_id},
        )
        data = data.json()
        nb_logger.debug(data)
        if data['retcode'] == 0:
            return data['data']
    return None


async def get_mihoyo_public_data(
    uid: str,
    user_id: Optional[str],
    mode: Literal['abyss', 'player_card', 'role_detail'],
    schedule_type: Optional[str] = '1',
):
    server_id = 'cn_qd01' if uid[0] == '5' else 'cn_gf01'
    check = True
    while True:
        cookie_info = await get_cookie(user_id, uid, check)
        check = False
        if not cookie_info:
            return '当前没有可使用的cookie，请使用命令[原神扫码绑定]/[ysb]绑定私人cookie或联系超级管理员添加公共cookie，'
        if mode == 'abyss':
            data = await aiorequests.get(
                url=ABYSS_API,
                headers=mihoyo_headers(
                    q=f'role_id={uid}&schedule_type={schedule_type}&server={server_id}',
                    cookie=cookie_info.cookie,
                ),
                params={
                    "schedule_type": schedule_type,
                    "role_id": uid,
                    "server": server_id,
                },
            )
        elif mode == 'player_card':
            data = await aiorequests.get(
                url=PLAYER_CARD_API,
                headers=mihoyo_headers(
                    q=f'role_id={uid}&server={server_id}', cookie=cookie_info.cookie
                ),
                params={'server': server_id, 'role_id': uid},
            )
        elif mode == 'role_detail':
            json_data = {"server": server_id, "role_id": uid, "character_ids": []}
            data = await aiorequests.post(
                url=CHARACTER_DETAIL_API,
                headers=mihoyo_headers(b=json_data, cookie=cookie_info.cookie),
                json=json_data,
            )
        else:
            data = None
        data = data.json() if data else {'retcode': 999}
        nb_logger.debug(data)
        if await check_retcode(data, cookie_info, user_id, uid):
            return data


async def get_mihoyo_private_data(
    uid: str,
    user_id: Optional[str],
    mode: Literal['role_skill', 'month_info', 'daily_note', 'sign_info', 'sign_action'],
    role_id: Optional[str] = None,
    month: Optional[str] = None,
):
    server_id = 'cn_qd01' if uid[0] == '5' else 'cn_gf01'
    cookie_info = await get_cookie(user_id, uid, True, True)
    if not cookie_info:
        return (
            '未绑定私人cookie，绑定方法二选一：\n1.通过米游社扫码绑定：\n请发送指令[原神扫码绑定]\n2.获取cookie的教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1\n获取后，使用[ysb cookie]指令绑定'
            + (f'或前往{config.CookieWeb_url}网页添加绑定' if config.CookieWeb_enable else '')
        )
    if mode == 'role_skill':
        data = await aiorequests.get(
            url=CHARACTER_SKILL_API,
            headers=mihoyo_headers(
                q=f'uid={uid}&region={server_id}&avatar_id={role_id}',
                cookie=cookie_info.cookie,
            ),
            params={"region": server_id, "uid": uid, "avatar_id": role_id},
        )
    elif mode == 'month_info':
        data = await aiorequests.get(
            url=MONTH_INFO_API,
            headers=mihoyo_headers(
                q=f'month={month}&bind_uid={uid}&bind_region={server_id}',
                cookie=cookie_info.cookie,
            ),
            params={"month": month, "bind_uid": uid, "bind_region": server_id},
        )
    elif mode == 'daily_note':
        data = await aiorequests.get(
            url=DAILY_NOTE_API,
            headers=mihoyo_headers(
                q=f'role_id={uid}&server={server_id}', cookie=cookie_info.cookie
            ),
            params={"server": server_id, "role_id": uid},
        )
    elif mode == 'sign_info':
        data = await aiorequests.get(
            url=SIGN_INFO_API,
            headers={
                #'x-rpc-app_version': '2.11.1',
                #'x-rpc-client_type': '5',
                'Origin': 'https://act.mihoyo.com',
                'Referer': 'https://act.mihoyo.com/',
                'Cookie': cookie_info.cookie,
                "x-rpc-signgame":"hk4e",
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS '
                'X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.57.1',
            },
            params={'act_id': 'e202311201442471', 'region': server_id, 'uid': uid},
        )
    elif mode == 'sign_action':
        data = await aiorequests.post(
            url=SIGN_ACTION_API,
            headers=mihoyo_sign_headers(cookie_info.cookie),
            json={'act_id': 'e202311201442471', 'uid': uid, 'region': server_id},
        )
    else:
        data = None
    data = data.json() if data else {'retcode': 999}
    nb_logger.debug(data)
    if await check_retcode(data, cookie_info, user_id, uid):
        return data
    else:
        return f'你的UID{uid}的cookie疑似失效了'


async def get_sign_reward_list() -> dict:
    headers = {
        'x-rpc-app_version': '2.11.1',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 ('
        'KHTML, like Gecko) miHoYoBBS/2.57.1',
        #'x-rpc-client_type': '5',
        "x-rpc-signgame":"hk4e",
        'Referer': 'https://act.mihoyo.com/',
    }
    resp = await aiorequests.get(
        url=SIGN_REWARD_API, headers=headers, params={'act_id': 'e202311201442471'}
    )
    data = resp.json()
    nb_logger.debug(data)
    return data


async def get_stoken_by_login_ticket(login_ticket: str, mys_id: str) -> Optional[str]:
    with contextlib.suppress(Exception):
        data = await aiorequests.get(
            STOKEN_API,
            headers={
                'x-rpc-app_version': '2.11.2',
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
                'x-rpc-client_type': '5',
                'Referer': 'https://webstatic.mihoyo.com/',
                'Origin': 'https://webstatic.mihoyo.com',
            },
            params={'login_ticket': login_ticket, 'token_types': '3', 'uid': mys_id},
        )
        data = data.json()
        return data['data']['list'][0]['token']
    return None


async def get_cookie_token_by_stoken(stoken: str, mys_id: str) -> Optional[str]:
    with contextlib.suppress(Exception):
        data = await aiorequests.get(
            COOKIE_TOKEN_API,
            headers={
                'x-rpc-app_version': '2.11.2',
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
                'x-rpc-client_type': '5',
                'Referer': 'https://webstatic.mihoyo.com/',
                'Origin': 'https://webstatic.mihoyo.com',
                'Cookie': f'stuid={mys_id};stoken={stoken}',
            },
            params={'uid': mys_id, 'stoken': stoken},
        )
        data = data.json()
        return data['data']['cookie_token']
    return None


async def get_authkey_by_stoken(
    user_id: str, uid: str
) -> Tuple[Optional[str], bool, Optional[PrivateCookie]]:
    """
    根据stoken获取authkey

    :param user_id: 用户id
    :param uid: 原神uid
    :return: authkey
    """
    server_id = 'cn_qd01' if uid[0] == '5' else 'cn_gf01'
    cookie_info = await get_cookie(user_id, uid, True, True)
    if not cookie_info:
        return (
            '未绑定私人cookie，绑定方法二选一：\n1.通过米游社扫码绑定：\n请发送指令[原神扫码绑定]\n2.获取cookie的教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1\n获取后，使用[ysb cookie]指令绑定'
            + (f'或前往{config.CookieWeb_url}网页添加绑定' if config.CookieWeb_enable else ''),
            False,
            cookie_info,
        )
    if not cookie_info.stoken:
        return 'cookie中没有stoken字段，请重新绑定', False, cookie_info
    headers = {
        'Cookie': cookie_info.stoken,
        'DS': get_old_version_ds(True),
        'User-Agent': 'okhttp/4.8.0',
        'x-rpc-app_version': '2.35.2',
        'x-rpc-sys_version': '12',
        'x-rpc-client_type': '5',
        'x-rpc-channel': 'mihoyo',
        'x-rpc-device_id': random_hex(32),
        'x-rpc-device_name': random_text(random.randint(1, 10)),
        'x-rpc-device_model': 'Mi 10',
        'Referer': 'https://app.mihoyo.com',
        'Host': 'api-takumi.mihoyo.com',
    }
    data = await aiorequests.post(
        url=AUTHKEY_API,
        headers=headers,
        json={
            'auth_appid': 'webview_gacha',
            'game_biz': 'hk4e_cn',
            'game_uid': uid,
            'region': server_id,
        },
    )
    data = data.json()
    if data.get('data') is not None and 'authkey' in data['data']:
        return data['data']['authkey'], True, cookie_info
    else:
        return None, False, cookie_info


async def get_enka_data(uid: str):
    urls = [
        'https://enka.network/api/uid/{uid}',
        'https://profile.microgg.cn/api/uid/{uid}',  # 以下两个api由小灰灰提供
        'https://enka.microgg.cn/api/uid/{uid}',
    ]
    for url in urls:
        with contextlib.suppress(Exception):
            resp = await aiorequests.get(
                url=url.format(uid=uid),
                headers={'User-Agent': 'LittlePaimon/3.0'},
                follow_redirects=True,
            )
            data = resp.json()
            nb_logger.debug(data)
            if 'playerInfo' in data:
                return data
