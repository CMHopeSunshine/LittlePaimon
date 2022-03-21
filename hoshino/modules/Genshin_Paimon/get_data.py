from hoshino import aiorequests
from .util import get_headers, cache
import datetime
import re

@cache(ttl=datetime.timedelta(minutes=30))
async def get_abyss_data(uid, cookie, schedule_type = "1", use_cache=True):
    if uid[0] == '5':
        server_id = "cn_qd01"
    else:
        server_id = "cn_gf01"
    url ="https://api-takumi.mihoyo.com/game_record/app/genshin/api/spiralAbyss"
    headers = get_headers(q="role_id=" + uid + "&schedule_type=" + schedule_type + "&server=" + server_id, cookie=cookie)
    params ={
        "schedule_type": schedule_type,
        "role_id": uid,
        "server": server_id
    }
    res = await aiorequests.get(url=url, headers=headers, params=params)
    return await res.json()

async def get_daily_note_data(uid, cookie):
    if uid[0] == '5':
        server_id = "cn_qd01"
    else:
        server_id = "cn_gf01"
    url ="https://api-takumi.mihoyo.com/game_record/app/genshin/api/dailyNote"
    headers = get_headers(q="role_id=" + uid + "&server=" + server_id, cookie=cookie)
    params = {
        "server": server_id,
        "role_id": uid
    }
    res = await aiorequests.get(url=url, headers=headers, params=params)
    return await res.json()

@cache(ttl=datetime.timedelta(hours=1))
async def get_player_card_data(uid, cookie, use_cache=True):
    if uid[0] == '5':
        server_id = "cn_qd01"
    else:
        server_id = "cn_gf01"
    url ="https://api-takumi.mihoyo.com/game_record/app/genshin/api/index"
    headers = get_headers(q="role_id=" + uid + "&server=" + server_id, cookie=cookie)
    params = {
        "server": server_id,
        "role_id": uid
    }
    res = await aiorequests.get(url=url, headers=headers, params=params)
    return await res.json()

@cache(ttl=datetime.timedelta(hours=1))
async def get_chara_detail_data(uid, cookie, use_cache=True):
    if uid[0] == '5':
        server_id = "cn_qd01"
    else:
        server_id = "cn_gf01"
    json_data = {
        "server": server_id,
        "role_id": uid,
        "character_ids": []
    }
    url = 'https://api-takumi.mihoyo.com/game_record/app/genshin/api/character'
    headers = get_headers(b=json_data, cookie=cookie)
    res = await aiorequests.post(url=url, headers=headers, json=json_data)
    return await res.json()

@cache(ttl=datetime.timedelta(hours=1))
async def get_chara_skill_data(uid, chara_id, cookie, use_cache=True):
    if uid[0] == '5':
        server_id = "cn_qd01"
    else:
        server_id = "cn_gf01"
    url = 'https://api-takumi.mihoyo.com/event/e20200928calculate/v1/sync/avatar/detail'
    headers = get_headers(q="uid=" + uid + "&region=" + server_id + "&avatar_id=" + str(chara_id), cookie=cookie)
    params = {
        "region": server_id,
        "uid": uid,
        "avatar_id": chara_id
    }
    res = await aiorequests.get(url=url, headers=headers, params=params)
    return await res.json()

@cache(ttl=datetime.timedelta(hours=1))
async def get_monthinfo_data(uid, month, cookie, use_cache=True):
    if uid[0] == '5':
        server_id = "cn_qd01"
    else:
        server_id = "cn_gf01"
    url = 'https://hk4e-api.mihoyo.com/event/ys_ledger/monthInfo'
    headers = get_headers(q='month='+ str(month) + '&bind_uid=' + uid + '&bind_region=' + server_id, cookie=cookie)
    params = {
        "month": int(month),
        "bind_uid": uid,
        "bind_region": server_id
    }
    res = await aiorequests.get(url=url, headers=headers, params=params)
    return await res.json()

async def get_bind_game(cookie):
    finduid = re.search(r'account_id=(\d{6,12})', cookie)
    if not finduid:
        return None
    uid = finduid.group(1)
    url = 'https://api-takumi.mihoyo.com/game_record/card/wapi/getGameRecordCard'
    headers = get_headers(q='uid=' + uid, cookie = cookie)
    params = {
        "uid": uid
    }
    res = await aiorequests.get(url=url, headers=headers, params=params)
    return await res.json()

    