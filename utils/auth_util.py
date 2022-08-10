import hashlib
import json
import random
import string
from collections import defaultdict
from time import time

from littlepaimon_utils import aiorequests
from nonebot import logger

from .db_util import get_cookie_cache, update_cookie_cache, delete_cookie_cache
from .db_util import get_private_cookie, delete_cookie
from .db_util import get_public_cookie, limit_public_cookie
from .message_util import send_cookie_delete_msg


# 双参数冷却时间限制器
class FreqLimiter2:
    def __init__(self, default_cd_seconds: int = 60):
        self.next_time = defaultdict(lambda: defaultdict(float))
        self.default_cd = default_cd_seconds

    def check(self, key1, key2) -> bool:
        return bool(time() >= self.next_time[key1][key2])

    def start_cd(self, key1, key2, cd_time=0):
        self.next_time[key1][key2] = time() + (cd_time if cd_time > 0 else self.default_cd)

    def left_time(self, key1, key2) -> int:
        return int(self.next_time[key1][key2] - time()) + 1


# 获取可用的cookie
async def get_use_cookie(user_id, uid='', mys_id='', action=''):
    cache_cookie = await get_cookie_cache(uid, 'uid')
    cookies = await get_private_cookie(user_id, 'user_id')
    if not cookies:
        if cache_cookie:
            if cache_cookie['type'] == 'public':
                logger.info(f'---派蒙调用{uid}的缓存公共cookie执行{action}操作---')
            else:
                logger.info(f'---派蒙调用{uid}的缓存私人cookie执行{action}操作---')
            return cache_cookie
        public_cookie = await get_public_cookie()
        if not public_cookie:
            logger.info(f'---派蒙当前没有可用的公共cookie，可能是都达到了上限或没有公共cookie---')
            return None
        else:
            logger.info(f'---派蒙调用{public_cookie[0]}号公共cookie执行{action}操作---')
            return {'type': 'public', 'cookie': public_cookie[1], 'no': public_cookie[0]}
    else:
        for user_id_, cookie, uid_, mys_id_ in cookies:
            if (uid and uid_ == uid) or (mys_id and mys_id_ == mys_id):
                logger.info(f'---派蒙调用用户{user_id_}的uid{uid_}私人cookie执行{action}操作---')
                return {'type': 'private', 'user_id': user_id_, 'cookie': cookie, 'uid': uid_, 'mys_id': mys_id_}
        if cache_cookie:
            if cache_cookie['type'] == 'public':
                logger.info(f'---派蒙调用{uid}的缓存公共cookie执行{action}操作---')
            else:
                logger.info(f'---派蒙调用{uid}的缓存私人cookie执行{action}操作---')
            return cache_cookie
        use_cookie = random.choice(cookies)
        logger.info(f'---派蒙调用用户{use_cookie[0]}的uid{use_cookie[2]}私人cookie执行{action}操作---')
        return {'type':   'private', 'user_id': use_cookie[0], 'cookie': use_cookie[1], 'uid': use_cookie[2],
                'mys_id': use_cookie[3]}


# 获取可用的私人cookie
async def get_own_cookie(uid='', mys_id='', action=''):
    if uid:
        cookie = (await get_private_cookie(uid, 'uid'))
    elif mys_id:
        cookie = (await get_private_cookie(mys_id, 'mys_id'))
    else:
        cookie = None
    if not cookie:
        return None
    else:
        cookie = cookie[0]
        logger.info(f'---派蒙调用用户{cookie[0]}的uid{cookie[2]}私人cookie执行{action}操作---')
        return {'type': 'private', 'user_id': cookie[0], 'cookie': cookie[1], 'uid': cookie[2], 'mys_id': cookie[3]}


# 检查数据返回状态，10001为ck过期了，10101为达到每日30次上线了
async def check_retcode(data, cookie, uid):
    if data['retcode'] == 10001 or data['retcode'] == -100:
        await delete_cookie(cookie['cookie'], cookie['type'])
        await send_cookie_delete_msg(cookie)
        return False
    elif data['retcode'] == 10101:
        if cookie['type'] == 'public':
            logger.info(f'{cookie["no"]}号公共cookie达到了每日30次查询上限')
            await limit_public_cookie(cookie['cookie'])
            await delete_cookie_cache(cookie['cookie'], key='cookie')
        elif cookie['type'] == 'private':
            logger.info(f'用户{cookie["user_id"]}的uid{cookie["uid"]}私人cookie达到了每日30次查询上限')
            return '私人cookie达到了每日30次查询上限'
        return False
    else:
        await update_cookie_cache(cookie['cookie'], uid, 'uid')
        return True


# md5加密
def md5(text: str) -> str:
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()


# 生成随机字符串
def random_hex(length):
    result = hex(random.randint(0, 16 ** length)).replace('0x', '').upper()
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


# 米游社headers的ds_token，对应版本2.11.1
def get_ds(q="", b=None) -> str:
    if b:
        br = json.dumps(b)
    else:
        br = ""
    s = "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs"
    t = str(int(time()))
    r = str(random.randint(100000, 200000))
    c = md5("salt=" + s + "&t=" + t + "&r=" + r + "&b=" + br + "&q=" + q)
    return f"{t},{r},{c}"


# 米游社爬虫headers
def get_headers(cookie, q='', b=None):
    headers = {
        'DS':                get_ds(q, b),
        'Origin':            'https://webstatic.mihoyo.com',
        'Cookie':            cookie,
        'x-rpc-app_version': "2.11.1",
        'User-Agent':        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS '
                             'X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer':           'https://webstatic.mihoyo.com/'
    }
    return headers


def get_old_version_ds(mhy_bbs: bool = False) -> str:
    """
    生成米游社旧版本headers的ds_token
    """
    if mhy_bbs:
        s = 'dWCcD2FsOUXEstC5f9xubswZxEeoBOTc'
    else:
        s = 'h8w582wxwgqvahcdkpvdhbh2w9casgfl'
    t = str(int(time()))
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c = md5(f"salt={s}&t={t}&r={r}")
    return f"{t},{r},{c}"


def get_sign_headers(cookie):
    headers = {
        'User_Agent':        'Mozilla/5.0 (Linux; Android 10; MIX 2 Build/QKQ1.190825.002; wv) AppleWebKit/537.36 ('
                             'KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.101 Mobile Safari/537.36 '
                             'miHoYoBBS/2.3.0',
        'Cookie':            cookie,
        'x-rpc-device_id':   random_hex(32),
        'Origin':            'https://webstatic.mihoyo.com',
        'X_Requested_With':  'com.mihoyo.hyperion',
        'DS':                get_old_version_ds(mhy_bbs=True),
        'x-rpc-client_type': '2',
        'Referer':           'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon',
        'x-rpc-app_version': '2.28.1'
    }
    return headers


# 检查cookie是否有效，通过查看个人主页来判断
async def check_cookie(cookie):
    url = 'https://bbs-api.mihoyo.com/user/wapi/getUserFullInfo?gids=2'
    headers = {
        'DS':                get_ds(),
        'Origin':            'https://webstatic.mihoyo.com',
        'Cookie':            cookie,
        'x-rpc-app_version': "2.11.1",
        'x-rpc-client_type': '5',
        'Referer':           'https://webstatic.mihoyo.com/'
    }
    res = await aiorequests.get(url=url, headers=headers)
    res = res.json()
    if res['retcode'] != 0:
        return False
    else:
        return True




