import datetime
import random
import re
import string
import time
from asyncio import sleep
from pathlib import Path

from littlepaimon_utils import aiorequests
from littlepaimon_utils.files import save_json, load_json
from nonebot import require, get_bot, get_driver

require('nonebot_plugin_apscheduler')
from nonebot_plugin_apscheduler import scheduler

driver = get_driver()


async def get_address(cookie):
    address_url = 'https://api-takumi.mihoyo.com/account/address/list'
    header = {
        'Accept':          'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Connection':      'keep-alive',
        'Cookie':          cookie,
        'Host':            'api-takumi.mihoyo.com',
        'Origin':          'https://user.mihoyo.com',
        'Referer':         'https://user.mihoyo.com/',
        'User-Agent':      'Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.25.1'
    }
    res = await aiorequests.get(url=address_url, headers=header)
    res = res.json()
    if res['message'] == 'OK':
        address = res['data']['list']
        add_list = []
        for add in address:
            add_list.append({'id': add['id'],
                             '地址': f'姓名:{add["connect_name"]} 电话:{add["connect_mobile"]} 地址:{add["province_name"] + add["city_name"] + add["county_name"] + add["addr_ext"]}'})
        return add_list
    else:
        return None


async def get_goods(game):
    game_type = {'崩坏3': 'bh3', '原神': 'hk4e', '崩坏学园2': 'bh2', '未定事件簿': 'nxx', '米游社': 'bbs'}
    url = 'https://api-takumi.mihoyo.com/mall/v1/web/goods/list?app_id=1&point_sn=myb&page_size=20&page={page}&game=' + \
          game_type[game]
    goods_list = []
    goods_list_new = []
    page = 1
    while True:
        res = await aiorequests.get(url=url.format(page=page))
        res = res.json()
        if not res['data']['list']:
            break
        else:
            goods_list += res['data']['list']
        page += 1

    for good in goods_list:
        if good['next_time'] == 0 and good['type'] == 1:
            continue
        good_info = {}
        good_info['id'] = good['goods_id']
        good_info['name'] = good['goods_name']
        good_info['price'] = good['price']
        good_info['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(good['next_time']))
        goods_list_new.append(good_info)

    return goods_list_new


def save_exchange_info(user_id, state):
    info = {}
    info['user_id'] = user_id
    info['类型'] = state['商品类型']
    info['cookie'] = state['cookie']
    info['商品'] = state['goods']
    info['地址'] = state['address_id']
    if info['类型'] == '虚拟':
        info['uid'] = state['uid']

    t = f"{user_id}-{info['商品']['id']}"

    path = Path() / 'data' / 'LittlePaimon' / 'myb_exchange' / f'{t}.json'
    path.parent.mkdir(parents=True, exist_ok=True)

    save_json(data=info, path=path)

    scheduler.add_job(
        id=t,
        replace_existing=True,
        misfire_grace_time=5,
        func=exchange_action,
        trigger='date',
        args=(info,),
        next_run_time=datetime.datetime.strptime(info['商品']['time'], '%Y-%m-%d %H:%M:%S')
    )


async def get_bbs_info(info, headers):
    url = 'https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie'
    res = (await aiorequests.get(url=url, headers=headers)).json()
    if res['retcode'] == 0:
        data = res['data']['list']
        for d in data:
            if d['game_uid'] == info['uid']:
                return d['game_biz'], d['region']
    return None, None


async def get_stoken(cookie):
    bbs_cookie_url = 'https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket={}'
    bbs_cookie_url2 = 'https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={}&token_types=3&uid={}'

    login_ticket = re.search('login_ticket=[a-zA-Z0-9]{0,100}', cookie)
    data = (await aiorequests.get(url=bbs_cookie_url.format(login_ticket.group().split('=')[1]))).json()
    if '成功' in data['data']['msg']:
        stuid = data['data']['cookie_info']['account_id']
        data2 = (await aiorequests.get(url=bbs_cookie_url2.format(login_ticket.group().split('=')[1], stuid))).json()
        return data2['data']['list'][0]['token']
    else:
        return None


async def exchange_action(info):
    url = 'https://api-takumi.mihoyo.com/mall/v1/web/goods/exchange'
    headers = {
        'Accept':             'application/json, text/plain, */*',
        'Accept-Encoding':    'gzip, deflate, br',
        'Accept-Language':    'zh-CN,zh-Hans;q=0.9',
        'Connection':         'keep-alive',
        # 'Content-Length':     '88',
        'Content-Type':       'application/json;charset=utf-8',
        'Cookie':             info['cookie'],
        'Host':               'api-takumi.mihoyo.com',
        'Origin':             'https://webstatic.mihoyo.com',
        'Referer':            'https://webstatic.mihoyo.com/',
        'User-Agent':         'Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHtimeL, like Gecko) miHoYoBBS/2.14.1',
        'x-rpc-app_version':  '2.14.1',
        'x-rpc-channel':      'appstore',
        'x-rpc-client_type':  '1',
        'x-rpc-device_id':    ''.join(random.sample(string.ascii_letters + string.digits, 32)).upper(),
        'x-rpc-device_model': 'iPhone10,2',
        'x-rpc-device_name':  ''.join(random.sample(string.ascii_letters + string.digits, random.randrange(5))).upper(),
        'x-rpc-sys_version':  '15.1'
    }
    data = {
        "app_id": 1,
        "point_sn": "myb",
        "goods_id": info['商品']['id'],
        "exchange_num": 1,
        "address_id": info['地址']['id']
    }
    if info['类型'] == '虚拟':
        game_biz, region = await get_bbs_info(info, headers)
        data['uid'] = info['uid']
        data['game_biz'] = game_biz
        data['region'] = region
        if 'stoken' not in info['cookie']:
            stoken = await get_stoken(info['cookie'])
            info['cookie'] += f'stoken={stoken};'

    exchange_url = 'https://api-takumi.mihoyo.com/mall/v1/web/goods/exchange'
    flag = False
    for _ in range(3):
        exchange_res = (await aiorequests.post(url=exchange_url, headers=headers, json=data)).json()
        if exchange_res['retcode'] == 0:
            await get_bot().send_private_msg(user_id=info['user_id'],
                                             message=f'你的米游币商品{info["商品"]["name"]}的兑换成功，结果为:\n{exchange_res["message"]}')
            flag = True
            break
        await sleep(0.2)
    try:
        if not flag:
            await get_bot().send_private_msg(user_id=info['user_id'],
                                             message=f'你的米游币商品{info["商品"]["name"]}兑换失败:\n{exchange_res["message"]}')
    except:
        pass

    path = Path() / 'data' / 'LittlePaimon' / 'myb_exchange' / f"{info['user_id']}-{info['商品']['id']}.json"
    path.unlink()


@driver.on_startup
async def _():
    path = Path() / 'data' / 'LittlePaimon' / 'myb_exchange'
    path.mkdir(parents=True, exist_ok=True)
    for exchange_data in path.iterdir():
        info = load_json(path=exchange_data)
        t = str(exchange_data).replace('data\\LittlePaimon\\myb_exchange\\', '').replace('data/LittlePaimon/myb_exchange/', '').replace(
            '.json', '')
        scheduler.add_job(
            id=t,
            replace_existing=True,
            misfire_grace_time=5,
            func=exchange_action,
            trigger='date',
            args=(info,),
            next_run_time=datetime.datetime.strptime(info['商品']['time'], '%Y-%m-%d %H:%M:%S')
        )


def get_exchange_info(user_id):
    result = ''
    path = Path() / 'data' / 'LittlePaimon' / 'myb_exchange'
    path.mkdir(parents=True, exist_ok=True)
    i = 1
    for exchange_data in path.iterdir():
        file_name = str(exchange_data).replace('data\\LittlePaimon\\myb_exchange\\', '').replace('data/LittlePaimon/myb_exchange/', '')
        if file_name.startswith(user_id):
            info = load_json(path=exchange_data)
            result += f"{i}.{info['商品']['name']} {info['商品']['time']}\n"
            if info['类型'] == '虚拟':
                result += f"兑换至uid{info['uid']}\n"
            else:
                result += f"兑换至{info['地址']['地址']}\n"
            i += 1
    return result or '你还没有米游币兑换计划哦'


def delete_exchange_info(user_id):
    path = Path() / 'data' / 'LittlePaimon' / 'myb_exchange'
    path.mkdir(parents=True, exist_ok=True)
    for exchange_data in path.iterdir():
        file_name = str(exchange_data).replace('data\\LittlePaimon\\myb_exchange\\', '').replace('data/LittlePaimon/myb_exchange/', '')
        if file_name.startswith(user_id):
            exchange_data.unlink()
