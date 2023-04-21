import copy
import json
import time
import random
import string
from LittlePaimon.utils import logger
from LittlePaimon.database import PrivateCookie
from typing import Union
from LittlePaimon.utils.api import md5,get_cookie,random_text, random_hex, get_old_version_ds
import httpx
from .config import config


http = httpx.Client(timeout=20, transport=httpx.HTTPTransport(retries=10))

#米游社的API
#签到列表
SIGN_LIST_URL = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/home'
#签到信息
SIGN_INFO_URL = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/info'
#执行签到
SIGN_URL = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'

# 通用设置
bbs_api = "https://bbs-api.mihoyo.com"
bbs_get_captcha = bbs_api + "/misc/api/createVerification?is_high=true"
bbs_captcha_verify = bbs_api + "/misc/api/verifyVerification"

def query_score():
    response = http.get("http://api.rrocr.com/api/integral.html?appkey="+config.appkey)
    data = response.json()
    if data['status'] == -1:
        logger.info('查询积分失败')
        return True,'查询积分失败'
    integral = data['integral']
    if int(integral) < 10:
        logger.info('积分不足')
        return True,f'积分还剩{integral}'
    logger.info('积分还剩' + integral)
    return False,f'积分还剩{integral}'

def vaapigt(gt: str, challenge: str,referer: str):
    """validate,challenge"""
    response = http.get(config.vaapi + 
                         f'gt={gt}&challenge={challenge}',
                        timeout=60)
    data = response.json()
    if 'data' in data and 'validate' in data['data']:
        logger.info('[第三方]成功')
        validate =data['data']['validate']
        challenge =data['data']['challenge']
        return validate,challenge
    else:
        logger.info('[第三方]失败')# 打码失败输出错误信息,返回'j'
        validate="j"
        challenge ="j"
        return validate,challenge  # 失败返回'j' 成功返回validate

def rrocr(gt: str, challenge: str, referer: str):
    """validate,challenge"""
    jifen,_ = query_score()
    if jifen:
        validate="j"
        challenge ="j"
        return validate,challenge
    response = http.post('http://api.rrocr.com/api/recognize.html', params={
        'appkey': config.appkey,
        'gt': gt,
        'challenge': challenge,
        'referer': referer,
        'sharecode': 'a83baa99828342ccac180b19217e2a93'#？不明
    }, timeout=60)
    data = response.json()
    if 'data' in data and 'validate' in data['data']:
        logger.info(data['msg'])  
        validate =data['data']['validate']
        challenge =data['data']['challenge']
        return validate,challenge
    else:
        logger.info(data['msg'])# 打码失败输出错误信息,返回'j'
        validate="j"
        challenge ="j"
        return validate,challenge  # 失败返回'j' 成功返回validate

def get_validate(gt: str, challenge: str, referer: str):
    if config.vaapikai:
        validate,challenge = vaapigt(gt, challenge, referer)   
    else:
        validate,challenge = rrocr(gt, challenge, referer)
    return validate,challenge  # 失败返回'j' 成功返回validate
    
async def get_pass_challenge(uid: str,user_id: str):
    cookie_info = await get_cookie(user_id, uid, True, True)
    headers = {
        "DS": get_old_version_ds(),
        "cookie": cookie_info.stoken,
        "x-rpc-client_type": '2',
        "x-rpc-app_version": "2.38.1",
        "x-rpc-sys_version": "12",
        "x-rpc-channel": "miyousheluodi",
        "x-rpc-device_id": random_hex(32),
        "x-rpc-device_name": random_text(random.randint(1, 10)),
        "x-rpc-device_model": "Mi 10",
        "Referer": "https://app.mihoyo.com",
        "Host": "bbs-api.mihoyo.com",
        "User-Agent": "okhttp/4.8.0"
    }
    req = http.get(url=bbs_get_captcha, headers=headers)
    data = req.json()
    if data["retcode"] != 0:
        return None
    validate,_ = get_validate(data["data"]["gt"], data["data"]["challenge"],
                    "https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id"
                    "=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon")
    if validate != 'j':
        check_req = http.post(url=bbs_captcha_verify, headers=headers,
                                json={"geetest_challenge": data["data"]["challenge"],
                                    "geetest_seccode": validate+"|jordan",
                                    "geetest_validate": validate})
        check = check_req.json()
        if check["retcode"] == 0:
            return check["data"]["challenge"]
    return None


_HEADER = {
    'x-rpc-app_version': '2.11.1',
    'User-Agent': (
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) '
        'AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1'
    ),
    'x-rpc-client_type': '5',
    'Referer': 'https://webstatic.mihoyo.com/',
    'Origin': 'https://webstatic.mihoyo.com',
}



async def get_sign_info(user_id: str, uid: str,cookie:str) -> Union[dict, str]:
    server_id = 'cn_qd01' if uid[0] == '5' else 'cn_gf01'
    HEADER = copy.deepcopy(_HEADER)
    HEADER['Cookie'] = cookie
    req = http.get(url=SIGN_INFO_URL, headers=HEADER,
                    params={"act_id": 'e202009291139501', 'region': server_id,'uid': uid})
    data = req.json()
    return data



def old_version_get_ds_token(mysbbs=False):
    n = 'N50pqm7FSy2AkFz2B3TqtuZMJ5TOl3Ep'
    i = str(int(time.time()))
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c = md5('salt=' + n + '&t=' + i + '&r=' + r)
    return i + ',' + r + ',' + c

async def mihoyo_bbs_sign(user_id: str, uid: str,Header={}) -> Union[dict, str]:
    #cookie_info = await PrivateCookie.get_or_none(user_id=user_id, uid=uid)
    cookie_info = await get_cookie(user_id, uid, True, True)
    server_id = 'cn_qd01' if uid[0] == '5' else 'cn_gf01'
    HEADER = copy.deepcopy(_HEADER)
    HEADER['User_Agent'] = (
        'Mozilla/5.0 (Linux; Android 10; MIX 2 Build/QKQ1.190825.002; wv) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 '
        'Chrome/83.0.4103.101 Mobile Safari/537.36 miHoYoBBS/2.35.2'
    )
    HEADER['Cookie'] =  cookie_info.cookie
    HEADER['x-rpc-device_id'] = random_hex(32)
    HEADER['x-rpc-app_version'] = '2.35.2'
    HEADER['x-rpc-client_type'] = '5'
    HEADER['X_Requested_With'] = 'com.mihoyo.hyperion'
    HEADER['DS'] = old_version_get_ds_token(True)
    HEADER['Referer'] = (
        'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html'
        '?bbs_auth_required=true&act_id=e202009291139501&utm_source=bbs'
        '&utm_medium=mys&utm_campaign=icon'
    )
    HEADER.update(Header)
    req = http.post(url=SIGN_URL, headers=HEADER,
                    json={'act_id': 'e202009291139501', 'uid': uid,'region': server_id})
    data = req.json()
    return data


async def get_sign_list() -> dict:
    req = http.get(url=SIGN_LIST_URL,headers=_HEADER,params={'act_id': 'e202009291139501'})
    data = req.json()
    return data