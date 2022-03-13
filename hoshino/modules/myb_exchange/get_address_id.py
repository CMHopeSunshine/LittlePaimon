import json
import requests
from collections import defaultdict

url = 'https://api-takumi.mihoyo.com/account/address/list'


async def get_address(cookie):
    add_list = defaultdict(str)
    header = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': cookie,
        'Host': 'api-takumi.mihoyo.com',
        'Origin': 'https://user.mihoyo.com',
        'Referer': 'https://user.mihoyo.com/',
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 15_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.21.2'
    }
    res = requests.get(url=url, headers=header)
    res = res.json()
    if res['message'] == 'OK':
        address = res['data']['list']
        if address:
            for add in address:
                add_list[add['id']] = f'姓名:{add["connect_name"]} 电话:{add["connect_mobile"]} 地址:{add["province_name"] + add["city_name"] + add["county_name"] + add["addr_ext"]}'
        return add_list
    else:
        return None
