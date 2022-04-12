import os
import json
import hashlib
import re
import random
import time
from hoshino import logger, aiorequests
from io import BytesIO
import base64
import datetime
import functools
import inspect
from nonebot import get_bot
from .db_util import get_private_cookie, get_cookie_cache, get_public_cookie, limit_public_cookie, update_cookie_cache,get_last_query,update_last_query,delete_cookie

async def get_use_cookie(user_id, uid='', mys_id='', action=''):
    cache_cookie = await get_cookie_cache(uid, 'uid')
    if cache_cookie:
        if cache_cookie['type'] == 'public':
            logger.info(f'---派蒙调用{uid}的缓存公共cookie执行{action}操作---')
        else:
            logger.info(f'---派蒙调用{uid}的缓存私人cookie执行{action}操作---')
        return cache_cookie
    cookies = await get_private_cookie(user_id, 'user_id')
    if not cookies:
        public_cookie = await get_public_cookie()
        if not public_cookie:
            return None
        else:
            logger.info(f'---派蒙调用{public_cookie[0]}号公共cookie执行{action}操作---')
            return {'type':'public', 'cookie': public_cookie[1], 'no': public_cookie[0]}
    else:
        for user_id_, cookie, uid_, mys_id_ in cookies:
            if (uid and uid_ == uid) or (mys_id and mys_id_ == mys_id):
                logger.info(f'---派蒙调用用户{user_id_}的uid{uid_}私人cookie执行{action}操作---')
                return {'type':'private', 'user_id': user_id_, 'cookie': cookie, 'uid': uid_, 'mys_id': mys_id_}
        use_cookie = random.choice(cookies)
        logger.info(f'---派蒙调用用户{use_cookie[0]}的uid{use_cookie[2]}私人cookie执行{action}操作---')
        return {'type':'private', 'user_id': use_cookie[0], 'cookie': use_cookie[1], 'uid': use_cookie[2], 'mys_id': use_cookie[3]}

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
        return {'type':'private', 'user_id': cookie[0], 'cookie': cookie[1], 'uid': cookie[2], 'mys_id': cookie[3]}

# 检查数据返回状态，10001为ck过期了，10101为达到每日30次上线了
async def check_retcode(data, cookie, uid):
    if data['retcode'] == 10001:
        await delete_cookie(cookie['cookie'], cookie['type'])
        await send_cookie_delete_msg(cookie)
        return False
    elif data['retcode'] == 10101:
        if cookie['type'] == 'public':
            logger.info(f'{cookie["no"]}号公共cookie达到了每日30次查询上限')
        elif cookie['type'] == 'private':
            logger.info(f'用户{cookie["user_id"]}的uid{cookie["uid"]}私人cookie达到了每日30次查询上限')
        await limit_public_cookie(cookie['cookie'])
        return False
    else:
        await update_cookie_cache(cookie['cookie'], uid, 'uid')
        return True


# 缓存装饰器 ttl为过期时间 参数use_cache决定是否使用缓存，默认为True
def cache(ttl=datetime.timedelta(hours=1), **kwargs):
    def wrap(func):
        cache_data = {}

        @functools.wraps(func)
        async def wrapped(*args, **kw):
            nonlocal cache_data
            bound = inspect.signature(func).bind(*args, **kw)
            bound.apply_defaults()
            ins_key = '|'.join(['%s_%s' % (k, v) for k, v in bound.arguments.items()])
            default_data = {"time": None, "value": None}
            data = cache_data.get(ins_key, default_data)

            now = datetime.datetime.now()
            if 'use_cache' not in kw:
                kw['use_cache'] = True
            if not kw['use_cache'] or not data['time'] or now - data['time'] > ttl:
                try:
                    data['value'] = await func(*args, **kw)
                    data['time'] = now
                    cache_data[ins_key] = data
                except Exception as e:
                    raise e

            return data['value']

        return wrapped

    return wrap

# 获取message中的艾特对象
async def get_at_target(msg):
    for msg_seg in msg:
        if msg_seg.type == "at":
            return msg_seg.data['qq']
    return None

# message预处理，获取uid、干净的msg、user_id、是否缓存
async def get_uid_in_msg(ev):
    msg = ev.message
    msgt = msg.extract_plain_text().strip()
    if not msg:
        uid = await get_last_query(str(ev.user_id))
        return uid, '', str(ev.user_id), True
    user_id = await get_at_target(msg) or str(ev.user_id)
    use_cache = False if '-r' in msgt else True
    msgt = msgt.replace('-r', '').strip()
    find_uid = r'(?P<uid>(1|2|5)\d{8})'
    for msg_seg in msg:
        if msg_seg.type == 'text':
            match = re.search(find_uid, msg_seg.data['text'])
            if match:
                await update_last_query(user_id, match.group('uid'), 'uid')
                return match.group('uid'), msgt.replace(match.group('uid'), '').strip(), user_id, use_cache
    uid = await get_last_query(user_id)
    return uid, msgt.strip(), user_id, use_cache


class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__

# 图片转b64，q为质量（压缩比例）
def pil2b64(data, q=85):
    bio = BytesIO()
    data = data.convert("RGB")
    data.save(bio, format='JPEG', quality=q)
    base64_str = base64.b64encode(bio.getvalue()).decode()
    return 'base64://' + base64_str

# md5加密
def md5(text: str) -> str:
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()

# 米游社headers的ds_token，对应版本2.11.1
def get_ds(q="", b=None) -> str:
    if b:
        br = json.dumps(b)
    else:
        br = ""
    s = "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs"
    t = str(int(time.time()))
    r = str(random.randint(100000, 200000))
    c = md5("salt=" + s + "&t=" + t + "&r=" + r + "&b=" + br + "&q=" + q)
    return f"{t},{r},{c}"

# 米游社爬虫headers
def get_headers(cookie, q='',b=None):
    headers ={
        'DS': get_ds(q, b),
        'Origin': 'https://webstatic.mihoyo.com',
        'Cookie': cookie,
        'x-rpc-app_version': "2.11.1",
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS '
                    'X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer': 'https://webstatic.mihoyo.com/'
    }
    return headers

# 检查cookie是否有效，通过查看个人主页来判断
async def check_cookie(cookie):
    url = 'https://bbs-api.mihoyo.com/user/wapi/getUserFullInfo?gids=2'
    headers ={
        'DS': get_ds(),
        'Origin': 'https://webstatic.mihoyo.com',
        'Cookie': cookie,
        'x-rpc-app_version': "2.11.1",
        'x-rpc-client_type': '5',
        'Referer': 'https://webstatic.mihoyo.com/'
    }
    res = await aiorequests.get(url=url,headers=headers)
    res = await res.json()
    if res['retcode'] != 0:
        return False
    else:
        return True

# 向超级用户私聊发送cookie删除信息
async def send_cookie_delete_msg(cookie_info):
    msg = ''
    if cookie_info['type'] == 'public':
        msg = f'公共池的{cookie_info["no"]}号cookie已失效'
    elif cookie_info['type'] == 'private':
        if cookie_info['uid']:
            msg = f'用户{cookie_info["user_id"]}的uid{cookie_info["uid"]}的cookie已失效'
        elif cookie_info['mys_id']:
            msg = f'用户{cookie_info["user_id"]}的mys_id{cookie_info["mys_id"]}的cookie已失效'
    if msg:
        logger.info(f'---{msg}---')
        for superuser in get_bot().config.SUPERUSERS:
            try:
                await get_bot().send_private_msg(user_id=superuser,message=msg + '，派蒙帮你删除啦!')
            except Exception as e:
                logger.error(f'发送cookie删除消息失败: {e}')

