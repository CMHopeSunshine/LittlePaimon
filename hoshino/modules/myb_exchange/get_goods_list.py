import json
import requests
from collections import defaultdict

game_type = {'崩坏3': 'bh3', '原神': 'hk4e', '崩坏2': 'bh2', '未定': 'nxx', '米游社': 'bbs'}
url = 'https://api-takumi.mihoyo.com/mall/v1/web/goods/list'
header = {
    'Host': 'api-takumi.mihoyo.com',
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://user.mihoyo.com',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; MI NOTE Pro Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.98 Mobile Safari/537.36 miHoYoBBS/2.12.1',
    'x-rpc-client_type': '5',
    'x-rpc-device_id': '58cb65c8-463f-4503-8389-cd2ff1d7d36f',
    'Referer': 'https://webstatic.mihoyo.com/app/community-shop/index.html?bbs_presentation_style=no_header',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,en-US;q=0.8',
    'Cookie': '',
    'X-Requested-With': 'com.mihoyo.hyperion'
}

def get_goods_list():
    goods_list={}
    for game in game_type.values():
        for page in range(20):
            params = {
                'app_id': '1',
                'point_sn': 'myb',
                'page_size': '20',
                'page': str(page),
                'game': game
            }
            res = requests.get(url=url, headers=header, params=params)
            if res.json()['message'] != 'OK':
                return None
            goods = res.json()['data']['list']
            if goods:
                #print(f'成功获取到{game}的商品')
                pass
            else:
                break
            for good in goods:
                goods_list[good['goods_name']] = good['goods_id']
    return dict(goods_list)
