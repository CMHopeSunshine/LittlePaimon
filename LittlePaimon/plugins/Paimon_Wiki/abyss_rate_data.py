from LittlePaimon.utils import aiorequests

# 数据源自微信公众号原神创意工坊
headers = {
    'Host': 'www.youchuang.fun',
    'Referer': 'https://servicewechat.com/wxce4dbe0cb0f764b3/52/page-frame.html',
    'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 15_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                  'Mobile/15E148 MicroMessenger/8.0.20(0x1800142f) NetType/WIFI Language/zh_CN',
    'content-type': 'application/json'
}


async def get_rate(type: str = 'role'):
    url = f'https://www.youchuang.fun/gamerole/{type}Rate'
    json_data = {
        "version": "3.0"
    }
    res = await aiorequests.post(url=url, headers=headers, json=json_data)
    return res.json()


async def get_formation_rate(layer: int = 1):
    url = 'https://www.youchuang.fun/gamerole/formationRate'
    json_data = {
        "version": "3.0",
        "layer": layer
    }
    res = await aiorequests.post(url=url, headers=headers, json=json_data)
    return res.json()


async def get_teammates_rate(name: str):
    url = 'https://www.youchuang.fun/gamerole/teammatesRate'
    json_data = {
        "name": name,
        "version": "3.0"
    }
    res = await aiorequests.post(url=url, headers=headers, json=json_data)
    return res.json()


async def get_weapon_rate(name: str):
    url = 'https://www.youchuang.fun/gamerole/getWeaponByName'
    json_data = {
        "name": name,
        "version": "3.9"
    }
    res = await aiorequests.post(url=url, headers=headers, json=json_data)
    return res.json()
