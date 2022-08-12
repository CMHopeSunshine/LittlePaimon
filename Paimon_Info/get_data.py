import datetime
import re

from littlepaimon_utils import aiorequests
from nonebot import logger

from ..utils.auth_util import get_headers, get_sign_headers, get_use_cookie, get_own_cookie, check_retcode
from ..utils.db_util import get_private_cookie, update_cookie_cache, update_private_cookie
from ..utils.decorator import cache


async def get_abyss_data(user_id, uid, schedule_type="1", use_cache=True):
    server_id = "cn_qd01" if uid[0] == '5' else "cn_gf01"
    url = "https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/spiralAbyss"
    params = {
        "schedule_type": schedule_type,
        "role_id":       uid,
        "server":        server_id}
    while True:
        cookie = await get_use_cookie(user_id, uid=uid, action='查询深渊')
        if not cookie:
            return '现在派蒙没有可以用的cookie哦，可能是:\n1.公共cookie全都达到了每日30次上限\n2.公共池全都失效了或没有cookie\n让管理员使用 添加公共ck 吧!'
        headers = get_headers(q=f'role_id={uid}&schedule_type={schedule_type}&server={server_id}',
                              cookie=cookie['cookie'])

        resp = await aiorequests.get(url=url, headers=headers, params=params)
        data = resp.json()
        check = await check_retcode(data, cookie, uid)
        if check == '私人cookie达到了每日30次查询上限':
            return check
        elif check:
            return data


async def get_daily_note_data(uid):
    server_id = "cn_qd01" if uid[0] == '5' else "cn_gf01"
    url = "https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/dailyNote"
    cookie = await get_own_cookie(uid, action='查询实时便签')
    if not cookie:
        return f'你的uid{uid}没有绑定对应的cookie,使用ysb绑定才能用实时便签哦!'
    await update_cookie_cache(cookie['cookie'], uid, 'uid')
    headers = get_headers(q=f'role_id={uid}&server={server_id}', cookie=cookie['cookie'])
    params = {
        "server":  server_id,
        "role_id": uid
    }
    resp = await aiorequests.get(url=url, headers=headers, params=params)
    data = resp.json()
    if await check_retcode(data, cookie, uid):
        return data
    else:
        return f'你的uid{uid}的cookie已过期,需要重新绑定哦!'


@cache(ttl=datetime.timedelta(hours=1))
async def get_player_card_data(user_id, uid, use_cache=True):
    server_id = "cn_qd01" if uid[0] == '5' else "cn_gf01"
    url = "https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/index"
    params = {
        "server":  server_id,
        "role_id": uid
    }
    while True:
        cookie = await get_use_cookie(user_id, uid=uid, action='查询原神卡片')
        if not cookie:
            return '现在派蒙没有可以用的cookie哦，可能是:\n1.公共cookie全都达到了每日30次上限\n2.公共池全都失效了或没有cookie\n让管理员使用 添加公共ck 吧!'
        headers = get_headers(q=f'role_id={uid}&server={server_id}', cookie=cookie['cookie'])
        resp = await aiorequests.get(url=url, headers=headers, params=params)
        data = resp.json()
        check = await check_retcode(data, cookie, uid)
        if check == '私人cookie达到了每日30次查询上限':
            return check
        elif check:
            return data


@cache(ttl=datetime.timedelta(hours=1))
async def get_chara_detail_data(user_id, uid, use_cache=True):
    server_id = "cn_qd01" if uid[0] == '5' else "cn_gf01"
    json_data = {
        "server":        server_id,
        "role_id":       uid,
        "character_ids": []
    }
    url = 'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/character'
    while True:
        cookie = await get_use_cookie(user_id, uid=uid, action='查询角色详情')
        if not cookie:
            return '现在派蒙没有可以用的cookie哦，可能是:\n1.公共cookie全都达到了每日30次上限\n2.公共池全都失效了或没有cookie\n让管理员使用 添加公共ck 吧!'
        headers = get_headers(b=json_data, cookie=cookie['cookie'])
        resp = await aiorequests.post(url=url, headers=headers, json=json_data)
        data = resp.json()
        check = await check_retcode(data, cookie, uid)
        if check == '私人cookie达到了每日30次查询上限':
            return check
        elif check:
            return data


@cache(ttl=datetime.timedelta(hours=1))
async def get_chara_skill_data(uid, chara_id, use_cache=True):
    server_id = "cn_qd01" if uid[0] == '5' else "cn_gf01"
    url = 'https://api-takumi.mihoyo.com/event/e20200928calculate/v1/sync/avatar/detail'
    cookie = await get_own_cookie(uid, action='查询角色天赋')
    if not cookie:
        return None
    await update_cookie_cache(cookie['cookie'], uid, 'uid')
    headers = get_headers(q=f'uid={uid}&region={server_id}&avatar_id={chara_id}', cookie=cookie['cookie'])
    params = {
        "region":    server_id,
        "uid":       uid,
        "avatar_id": chara_id
    }
    resp = await aiorequests.get(url=url, headers=headers, params=params)
    data = resp.json()
    return data


@cache(ttl=datetime.timedelta(hours=1))
async def get_monthinfo_data(uid, month, use_cache=True):
    server_id = "cn_qd01" if uid[0] == '5' else "cn_gf01"
    url = 'https://hk4e-api.mihoyo.com/event/ys_ledger/monthInfo'
    cookie = await get_own_cookie(uid, action='查询每月札记')
    if not cookie:
        return f'你的uid{uid}没有绑定对应的cookie,使用ysb绑定才能用每月札记哦!'
    await update_cookie_cache(cookie['cookie'], uid, 'uid')
    headers = get_headers(q=f'month={month}&bind_uid={uid}&bind_region={server_id}', cookie=cookie['cookie'])
    params = {
        "month":       int(month),
        "bind_uid":    uid,
        "bind_region": server_id
    }
    resp = await aiorequests.get(url=url, headers=headers, params=params)
    data = resp.json()
    if await check_retcode(data, cookie, uid):
        return data
    else:
        return f'你的uid{uid}的cookie已过期,需要重新绑定哦!'


async def get_bind_game(cookie):
    finduid = re.search(r'account_id=(\d{6,12})', cookie)
    if not finduid:
        finduid = re.search(r'ltuid=(\d{6,12})', cookie)
        if not finduid:
            return None, None
    uid = finduid.group(1)
    url = 'https://api-takumi-record.mihoyo.com/game_record/card/wapi/getGameRecordCard'
    headers = get_headers(q=f'uid={uid}', cookie=cookie)
    params = {
        "uid": uid
    }
    resp = await aiorequests.get(url=url, headers=headers, params=params)
    data = resp.json()
    return data, uid


# 添加stoken
async def addStoken(stoken, uid):
    login_ticket = re.search(r'login_ticket=([0-9a-zA-Z]+)', stoken)
    if login_ticket:
        login_ticket = login_ticket.group(0).split('=')[1]
    else:
        return None, None, None, '你的cookie中没有login_ticket字段哦，请重新获取'
    ck = await get_private_cookie(uid, key='uid')
    if not ck:
        return None, None, None, '你还没绑定私人cookie哦，请先用ysb绑定吧'
    ck = ck[0][1]
    mys_id = re.search(r'account_id=(\d*)', ck)
    if mys_id:
        mys_id = mys_id.group(0).split('=')[1]
    else:
        return None, None, None, '你的cookie中没有account_id字段哦，请重新获取'
    raw_data = await get_stoken_by_login_ticket(login_ticket, mys_id)
    try:
        stoken = raw_data['data']['list'][0]['token']
    except TypeError:
        return None, None, None, '该stoken无效获取过期了，请重新获取'
    s_cookies = 'stuid={};stoken={}'.format(mys_id, stoken)
    return s_cookies, mys_id, raw_data, 'OK'


# 获取今日签到信息
async def get_sign_info(uid):
    server_id = "cn_qd01" if uid[0] == '5' else "cn_gf01"
    url = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/info'
    cookie = await get_own_cookie(uid, action='查询米游社签到')
    if not cookie:
        return f'你的uid{uid}没有绑定对应的cookie,使用ysb绑定才能用米游社签到哦!'
    headers = {
        'x-rpc-app_version': '2.11.1',
        'x-rpc-client_type': '5',
        'Origin':            'https://webstatic.mihoyo.com',
        'Referer':           'https://webstatic.mihoyo.com/',
        'Cookie':            cookie['cookie'],
        'User-Agent':        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS '
                             'X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
    }
    params = {
        'act_id': 'e202009291139501',
        'region': server_id,
        'uid':    uid
    }
    resp = await aiorequests.get(url=url, headers=headers, params=params)
    data = resp.json()
    if await check_retcode(data, cookie, uid):
        return data
    else:
        return f'你的uid{uid}的cookie已过期,需要重新绑定哦!'


# 执行签到操作
async def sign(uid):
    server_id = "cn_qd01" if uid[0] == '5' else "cn_gf01"
    url = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'
    cookie = await get_own_cookie(uid, action='米游社签到')
    if not cookie:
        return f'你的uid{uid}没有绑定对应的cookie,使用ysb绑定才能用米游社签到哦!'
    headers = get_sign_headers(cookie['cookie'])
    json_data = {
        'act_id': 'e202009291139501',
        'uid':    uid,
        'region': server_id
    }
    resp = await aiorequests.post(url=url, headers=headers, json=json_data)
    data = resp.json()
    logger.info(f'---UID{uid}的签到状态码为{data["retcode"]}，结果为{data["message"]}---')
    if await check_retcode(data, cookie, uid):
        return data
    else:
        return f'你的uid{uid}的cookie已过期,需要重新绑定哦!'


# 获取签到奖励列表
async def get_sign_list():
    url = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/home'
    headers = {
        'x-rpc-app_version': '2.11.1',
        'User-Agent':        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 ('
                             'KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer':           'https://webstatic.mihoyo.com/'
    }
    params = {
        'act_id': 'e202009291139501'
    }
    resp = await aiorequests.get(url=url, headers=headers, params=params)
    data = resp.json()
    return data


async def get_enka_data(uid):
    try:
        url = f'https://enka.network/u/{uid}/__data.json'
        resp = await aiorequests.get(url=url, headers={'User-Agent': 'LittlePaimon/2.0'}, follow_redirects=True)
        data = resp.json()
        return data
    except Exception:
        url = f'https://enka.microgg.cn/u/{uid}/__data.json'
        resp = await aiorequests.get(url=url, headers={'User-Agent': 'LittlePaimon/2.0'}, follow_redirects=True)
        data = resp.json()
        return data


async def get_stoken_by_login_ticket(loginticket, mys_id):
    req = await aiorequests.get(url='https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket',
                                params={
                                    'login_ticket': loginticket,
                                    'token_types':  '3',
                                    'uid':          mys_id
                                })
    return req.json()
