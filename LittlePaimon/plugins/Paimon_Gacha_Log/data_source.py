import asyncio
import time
import datetime
from typing import Dict, Union, Tuple

from LittlePaimon import DRIVER
from LittlePaimon.database.models import PlayerInfo
from LittlePaimon.config import GACHA_LOG
from LittlePaimon.utils.api import get_authkey_by_stoken
from LittlePaimon.utils import aiorequests, logger
from LittlePaimon.utils.files import load_json
from .models import GachaItem, GachaLogInfo, GACHA_TYPE_LIST
from .draw import draw_gacha_log

GACHA_LOG_API = 'https://hk4e-api.mihoyo.com/event/gacha_info/api/getGachaLog'
HEADERS: Dict[str, str] = {
    'x-rpc-app_version': '2.11.1',
    'User-Agent':        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 ('
                         'KHTML, like Gecko) miHoYoBBS/2.11.1',
    'x-rpc-client_type': '5',
    'Referer':           'https://webstatic.mihoyo.com/',
    'Origin':            'https://webstatic.mihoyo.com',
}
PARAMS: Dict[str, Union[str, int]] = {
    'authkey_ver': '1',
    'sign_type':   '2',
    'auth_appid':  'webview_gacha',
    'init_type':   '200',
    'gacha_id':    'fecafa7b6560db5f3182222395d88aaa6aaac1bc',
    'lang':        'zh-cn',
    'device_type': 'mobile',
    'plat_type':   'ios',
    'game_biz':    'hk4e_cn',
    'size':        '20',
}


def load_history_info(user_id: str, uid: str) -> Tuple[GachaLogInfo, bool]:
    """
    读取历史抽卡记录数据
    :param user_id: 用户id
    :param uid: 原神uid
    :return: 抽卡记录数据
    """
    file_path = GACHA_LOG / f'gacha_log-{user_id}-{uid}.json'
    if file_path.exists():
        return GachaLogInfo.parse_obj(load_json(file_path)), True
    else:
        return GachaLogInfo(user_id=user_id,
                            uid=uid,
                            update_time=datetime.datetime.now()), False


def save_gacha_log_info(user_id: str, uid: str, info: GachaLogInfo):
    """
    保存抽卡记录数据
    :param user_id: 用户id
    :param uid: 原神uid
    :param info: 抽卡记录数据
    """
    save_path = GACHA_LOG / f'gacha_log-{user_id}-{uid}.json'
    save_path_bak = GACHA_LOG / f'gacha_log-{user_id}-{uid}.json.bak'
    # 将旧数据备份一次
    if save_path.exists():
        if save_path_bak.exists():
            save_path_bak.unlink()
        save_path.rename(save_path.parent / f'{save_path.name}.bak')
    # 写入新数据
    with save_path.open('w', encoding='utf-8') as f:
        f.write(info.json(ensure_ascii=False, indent=4))


async def get_gacha_log_data(user_id: str, uid: str):
    """
    使用authkey获取抽卡记录数据，并合并旧数据
    :param user_id: 用户id
    :param uid: 原神uid
    :return: 更新结果
    """
    new_num = 0
    server_id = 'cn_qd01' if uid[0] == '5' else 'cn_gf01'
    authkey, state, cookie_info = await get_authkey_by_stoken(user_id, uid)
    if not state:
        return authkey
    gacha_log, _ = load_history_info(user_id, uid)
    params = PARAMS.copy()
    params['region'] = server_id
    params['authkey'] = authkey
    logger.info('原神抽卡记录', '➤', {'用户': user_id, 'UID': uid}, '开始更新抽卡记录', True)
    for pool_id, pool_name in GACHA_TYPE_LIST.items():
        params['gacha_type'] = pool_id
        end_id = 0
        for page in range(1, 999):
            params['page'] = page
            params['end_id'] = end_id
            params['timestamp'] = str(int(time.time()))
            data = await aiorequests.get(url=GACHA_LOG_API,
                                         headers=HEADERS,
                                         params=params)
            data = data.json()
            if 'data' not in data or 'list' not in data['data']:
                logger.info('原神抽卡记录', '➤➤', {}, 'Stoken已失效，更新失败', False)
                cookie_info.stoken = None
                await cookie_info.save()
                return f'UID{uid}的Stoken已失效，请重新绑定后再更新抽卡记录'
            data = data['data']['list']
            if not data:
                break
            for item in data:
                item_info = GachaItem.parse_obj(item)
                if item_info not in gacha_log.item_list[pool_name]:
                    gacha_log.item_list[pool_name].append(item_info)
                    new_num += 1
            end_id = data[-1]['id']
            await asyncio.sleep(1)
        logger.info('原神抽卡记录', f'➤➤<m>{pool_name}</m>', {}, '获取完成', True)
    for i in gacha_log.item_list.values():
        i.sort(key=lambda x: (x.time, x.id))
    gacha_log.update_time = datetime.datetime.now()
    save_gacha_log_info(user_id, uid, gacha_log)
    if new_num == 0:
        return f'UID{uid}更新完成，本次没有新增数据'
    else:
        return f'UID{uid}更新完成，本次共新增{new_num}条抽卡记录'


async def get_gacha_log_img(user_id: str, uid: str, nickname: str):
    data, state = load_history_info(user_id, uid)
    if not state:
        return f'UID{uid}还没有抽卡记录数据，请先更新'
    player_info = await PlayerInfo.get_or_none(user_id=user_id, uid=uid)
    if player_info:
        return await draw_gacha_log(player_info.user_id, player_info.uid, player_info.nickname, player_info.signature, data)
    else:
        return await draw_gacha_log(user_id, uid, nickname, None, data)


