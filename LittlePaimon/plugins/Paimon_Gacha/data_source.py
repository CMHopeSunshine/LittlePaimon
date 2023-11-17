import random

import httpx
import numpy

from .data_handle import load_user_data, save_user_data


def random_int():
    return numpy.random.randint(low=0, high=10000, size=None, dtype='l')


# 抽卡概率来自https://www.bilibili.com/read/cv10468091
# 角色抽卡概率
def character_probability(rank, count):
    ret = 0
    count += 1
    if rank == 5 and count <= 73:
        ret = 60
    elif rank == 5 and count >= 74:
        ret = 60 + 600 * (count - 73)
    elif rank == 4 and count <= 8:
        ret = 510
    elif rank == 4 and count >= 9:
        ret = 510 + 5100 * (count - 8)
    return ret


# 武器抽卡概率
def weapon_probability(rank, count):
    ret = 0
    count += 1
    if rank == 5 and count <= 62:
        ret = 70
    elif rank == 5 and count <= 73:
        ret = 70 + 700 * (count - 62)
    elif rank == 5 and count >= 74:
        ret = 7770 + 350 * (count - 73)
    elif rank == 4 and count <= 7:
        ret = 600
    elif rank == 4 and count == 8:
        ret = 6600
    elif rank == 4 and count >= 9:
        ret = 6600 + 3000 * (count - 8)
    return ret


def get_pool_type(gacha_type):
    if gacha_type in [301, 400]:
        return '角色'
    if gacha_type == 200:
        return '常驻'
    return '武器'


def get_rank(user_data, pool_str):
    value = random_int()
    if pool_str == '武器':
        index_5 = weapon_probability(5, user_data["抽卡数据"][f"{pool_str}池未出5星数"])
        index_4 = weapon_probability(4, user_data["抽卡数据"][f"{pool_str}池未出4星数"]) + index_5
    else:
        index_5 = character_probability(5, user_data["抽卡数据"][f"{pool_str}池未出5星数"])
        index_4 = character_probability(4, user_data["抽卡数据"][f"{pool_str}池未出4星数"]) + index_5
    if value <= index_5:
        return 5
    elif value <= index_4:
        return 4
    else:
        return 3


def is_Up(user_data, rank, pool_str):
    if pool_str == '常驻':
        return False
    elif pool_str == '武器':
        return random_int() <= 7500 or user_data["抽卡数据"][f"武器池{rank}星下次是否为up"]
    else:
        return random_int() <= 5000 or user_data["抽卡数据"][f"角色池{rank}星下次是否为up"]


def get_once_data(uid: int, gacha_data: dict):
    user_data = load_user_data(uid)
    role = {}
    pool_str = get_pool_type(gacha_data['gacha_type'])
    # 判定星级
    rank = get_rank(user_data, pool_str)
    # 是否为up
    is_up = is_Up(user_data, rank, pool_str) if rank != 3 else False
    user_data["抽卡数据"]["抽卡总数"] += 1
    if rank == 3:
        role = random.choice(gacha_data['r3_prob_list'])
        user_data["抽卡数据"][f"{pool_str}池未出4星数"] += 1
        user_data["抽卡数据"][f"{pool_str}池未出5星数"] += 1
        role['count'] = 1
    else:
        if rank == 5 and pool_str == '武器' and user_data["抽卡数据"]["定轨能量"] == 2 and "pool_type" not in gacha_data:
            role['item_name'] = user_data["抽卡数据"]["定轨武器名称"]
            role['item_type'] = '武器'
            role['rank'] = rank
        elif is_up:
            role = random.choice(gacha_data[f'r{rank}_up_items'])
            user_data["抽卡数据"][f"{rank}星up出货数"] += 1
            role['rank'] = rank
        else:
            while True:
                role = random.choice(gacha_data[f'r{rank}_prob_list'])
                if role['is_up'] == 0:
                    break
        if rank == 4:
            user_data["抽卡数据"][f"{pool_str}池未出5星数"] += 1
        elif rank == 5:
            user_data["抽卡数据"][f"{pool_str}池未出4星数"] += 1
            if pool_str == '武器' and "pool_type" not in gacha_data:
                if user_data["抽卡数据"]["定轨武器名称"] == '':
                    role['dg_time'] = -1
                elif role['item_name'] != user_data["抽卡数据"]["定轨武器名称"]:
                    user_data["抽卡数据"]["定轨能量"] += 1
                    role['dg_time'] = user_data["抽卡数据"]["定轨能量"]
                else:
                    #user_data["抽卡数据"]["定轨武器名称"] = ''
                    user_data["抽卡数据"]["定轨能量"] = 0
                    role['dg_time'] = 3
        user_data["抽卡数据"][f"{rank}星出货数"] += 1
        if gacha_data['gacha_type'] != 200:
            user_data["抽卡数据"][f"{pool_str}池{rank}星下次是否为up"] = not is_up
        item_type = '角色' if role['item_type'] == '角色' else '武器'
        if role['item_name'] not in user_data[f"{item_type}列表"]:
            user_data[f"{item_type}列表"][role['item_name']] = {'数量': 1, '出货': []}
            if rank == 5:
                user_data[f"{item_type}列表"][role['item_name']]['星级'] = '★★★★★'
                user_data[f"{item_type}列表"][role['item_name']]['出货'].append(
                    (user_data['抽卡数据'][f"{pool_str}池未出{rank}星数"] + 1))
            else:
                user_data[f"{item_type}列表"][role['item_name']]['星级'] = '★★★★'
        else:
            user_data[f"{item_type}列表"][role['item_name']]['数量'] += 1
            if rank == 5:
                user_data[f"{item_type}列表"][role['item_name']]['出货'].append(
                    (user_data['抽卡数据'][f"{pool_str}池未出{rank}星数"] + 1))
        role['count'] = user_data["抽卡数据"][f"{pool_str}池未出{rank}星数"] + 1
        user_data["抽卡数据"][f"{pool_str}池未出{rank}星数"] = 0
    save_user_data(uid, user_data)
    return role


def get_pool_id(pool_name: str) -> int:
    if any(i in pool_name for i in ['角色1', '限定1', '活动1', 'role1']):
        return 301
    if any(i in pool_name for i in ['角色2', '限定2', '活动2', 'role2']):
        return 400
    if any(i in pool_name for i in ['武器', '神器', 'weapon']):
        return 302
    if any(i in pool_name for i in ['常驻', '普', 'permanent']):
        return 200
    # if any(i in pool_name for i in ['彩蛋', '五星', 'star']):
    #     return 999


BASE_URL = 'https://operation-webstatic.mihoyo.com/gacha_info/hk4e/cn_gf01/%s'


async def get_gacha_data(pool: str):
    pool_id = get_pool_id(pool)
    if not pool_id:
        return None
    data = await gacha_info_list()
    gacha_data = sorted(list(filter(lambda x: x['gacha_type'] == pool_id, data)), key=lambda x: x['end_time'])[-1]
    gacha_id = gacha_data['gacha_id']
    gacha_data = await gacha_info(gacha_id)
    return gacha_data


async def get_dg_weapon():
    data = await gacha_info_list()
    gacha_data = sorted(list(filter(lambda x: x['gacha_type'] == 302, data)), key=lambda x: x['end_time'])[-1]

    gacha_id = gacha_data['gacha_id']
    gacha_data = await gacha_info(gacha_id)
    return [weapon['item_name'] for weapon in gacha_data['r5_up_items']]


async def set_dg_weapon(user_id: int, weapon: str):
    weapon_list = await get_dg_weapon()
    if weapon not in weapon_list:
        return {'code': 500, 'message': '该武器不在当前up中'}
    user_data = load_user_data(user_id)
    if weapon == user_data['抽卡数据']['定轨武器名称']:
        return {'code': 200, 'message': '你当前已经定轨该武器'}
    else:
        user_data['抽卡数据']['定轨武器名称'] = weapon
        user_data['抽卡数据']['定轨能量'] = 0
        save_user_data(user_id, user_data)
        return {'code': 0, 'message': '定轨成功'}


async def gacha_info_list():
    async with httpx.AsyncClient() as client:
        res = await client.get(url=BASE_URL % 'gacha/list.json')
        json_data = res.json()
        return json_data['data']['list']


async def gacha_info(gacha_id):
    async with httpx.AsyncClient() as client:
        res = await client.get(url=BASE_URL % gacha_id + '/zh-cn.json')
        return res.json()
