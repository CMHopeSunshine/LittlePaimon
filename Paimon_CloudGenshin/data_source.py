import json

from littlepaimon_utils import aiorequests

host = 'https://api-cloudgame.mihoyo.com/'


def get_header(uuid: str, token: str):
    headers = {
        'x-rpc-combo_token': token,
        'x-rpc-client_type': '2',
        'x-rpc-app_version': '2.4.0',
        'x-rpc-sys_version': '10',
        'x-rpc-channel': 'mihoyo',
        'x-rpc-device_id': uuid,
        'x-rpc-device_name': 'Samsung SM-G988N',
        'x-rpc-device_model': 'SM-G988N',
        'x-rpc-app_id': '1953439974',
        'Referer': 'https://app.mihoyo.com',
        'Host': 'api-cloudgame.mihoyo.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/4.9.0'
    }
    return headers


async def check_token(uuid: str, cookie: str):
    headers = get_header(uuid, cookie)
    req = await aiorequests.post(host + 'hk4e_cg_cn/gamer/api/login', headers=headers)
    data = json.loads(req.text)
    if data['retcode'] == 0 and data['message'] == 'OK':
        return True
    return False


async def get_Info(uuid: str, cookie: str):
    headers = get_header(uuid, cookie)
    req = await aiorequests.get(host + 'hk4e_cg_cn/wallet/wallet/get', headers=headers)
    return json.loads(req.text)


async def get_Announcement(uuid: str, cookie: str):
    headers = get_header(uuid, cookie)
    req = await aiorequests.get(host + 'hk4e_cg_cn/gamer/api/getAnnouncementInfo', headers=headers)
    return json.loads(req.text)


async def get_Notification(uuid: str, cookie: str):
    headers = get_header(uuid, cookie)
    req = await aiorequests.get(
        host + 'hk4e_cg_cn/gamer/api/listNotifications?status=NotificationStatusUnread&type=NotificationTypePopup'
               '&is_sort=true',
        headers=headers)
    return json.loads(req.text)
