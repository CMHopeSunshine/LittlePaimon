import os
import json
import traceback
import hashlib
import random
import time
import uuid
import requests
from hoshino import logger, aiorequests
from io import BytesIO
import base64
import datetime
import functools
import inspect

# user_cookies.json数据文件模版，如没有.json文件就会按这个模版生成文件
user_cookies_example = {
    "通用": [
        {
            "cookie": "",
            "no": 1
        },
        {
            "cookie": "",
            "no": 2
        }
    ],
    "私人":{}
    
}
user_cookies = {}
def load_data():
    path = os.path.join(os.path.dirname(__file__), 'user_data','user_cookies.json')
    if not os.path.exists(path):
        with open(path,'w',encoding='UTF-8') as f:
            json.dump(user_cookies_example,f,ensure_ascii=False)
    try:
        with open(path, encoding='utf8') as f:
            data = json.load(f)
            for k, v in data.items():
                user_cookies[k] = v
    except:
        traceback.print_exc()

def save_data():
    path = os.path.join(os.path.dirname(__file__), 'user_data','user_cookies.json')
    try:
        with open(path, 'w', encoding='utf8') as f:
            json.dump(user_cookies, f, ensure_ascii=False, indent=2)
    except:
        traceback.print_exc()

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
    #print(headers)
    return headers

# 检查cookie是否有效，通过查看个人主页是否返回ok来判断
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

# 通过qq号获取最后查询的uid
def get_uid_by_qq(qq):
    if qq not in user_cookies['私人']:
        return None
    return user_cookies['私人'][qq]['last_query']

# 检查qq号是否绑定uid
def check_uid_by_qq(qq, uid):
    if qq not in user_cookies['私人']:
        return False
    for cookie in user_cookies['私人'][qq]['cookies']:
        if cookie['uid'] == uid:
            return True
    return False

# 更新qq最后查询的uid
def update_last_query_to_qq(qq, uid):
    if qq not in user_cookies['私人']:
        user_cookies['私人'][qq] = {}
        user_cookies['私人'][qq]['cookies'] = []
    user_cookies['私人'][qq]['last_query'] = uid
    save_data()

# 绑定uid、cookie到qq号
async def bind_cookie(qq, uid, cookie):
    if qq not in user_cookies['私人']:
        user_cookies['私人'][qq] = {}
        user_cookies['私人'][qq]['cookies'] = []
    f = False
    for c in user_cookies['私人'][qq]['cookies']:
        if c['uid'] == uid:
            c['cookie'] = cookie
            f = True
            break
    if not f:
        c = {'cookie':cookie,'uid':uid}
        user_cookies['私人'][qq]['cookies'].append(c)
    user_cookies['私人'][qq]['last_query'] = uid
    save_data()

# 绑定cookie到公共cookie池
async def bind_public_cookie(cookie):
    if not await check_cookie(cookie):
        return '这cookie没有用哦，检查一下是不是复制错了或者过期了(试试重新登录米游社再获取)'
    else:
        user_cookies['通用'].append({"cookie": cookie, "no": len(user_cookies['通用']) + 1})
        save_data()
        return '添加公共cookie成功'

# 获取公共池可用的cookie
async def get_public_cookie():
    for cookie in user_cookies['通用']:
        if await check_cookie(cookie['cookie']):
            logger.info(f'--CMgenshin：调用公共cookie池-{cookie["no"]}号执行操作==')
            return cookie['cookie']
        else:
            logger.info(f'--CMgenshin：公共cookie池-{cookie["no"]}号已失效--')
    logger.error('--CMgenshin：原神查询公共cookie池已全部失效--')
    return None

# 获取可用的cookie，优先获取私人cookie，没有则获取公共池cookie
async def get_cookie(qq, uid, only_private = False, only_match_uid = False):
    if qq not in user_cookies['私人']:
        if only_private:
            return None
        else:
            return await get_public_cookie()
    else:
        valid_cookie = []
        for cookie in user_cookies['私人'][qq]['cookies']:
            if not await check_cookie(cookie['cookie']):
                logger.error(f'--CMgenshin：qq{qq}下的cookie-{cookie["uid"]}已失效--')
            else:
                valid_cookie.append(cookie)
                if cookie['uid'] == uid:
                    logger.info(f'--CMgenshin：调用qq{qq}的cookie-{cookie["uid"]}执行操作--')
                    return cookie['cookie']
        if valid_cookie and only_match_uid:
            logger.info(f'--CMgenshin：调用qq{qq}的cookie-{cookie["uid"]}执行操作--')
            return random.choice(valid_cookie)['cookie']
        else:
            if only_private:
                return None
            else:
                return await get_public_cookie()

# 初始化读取cookie数据
load_data()