import asyncio
import datetime
import time
from pathlib import Path
from typing import Dict, Union, Tuple, Optional

from nonebot import on_notice
from nonebot.adapters.onebot.v11 import GroupUploadNoticeEvent, NoticeEvent
from nonebot.rule import Rule

from LittlePaimon.database import PlayerInfo, LastQuery
from LittlePaimon.utils import logger, __version__
from LittlePaimon.utils.requests import aiorequests
from LittlePaimon.utils.api import get_authkey_by_stoken
from LittlePaimon.utils.files import load_json, save_json
from LittlePaimon.utils.path import GACHA_LOG
from .draw import draw_gacha_log
from .models import GachaItem, GachaLogInfo, GACHA_TYPE_LIST

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
        old_gacha_info = load_json(file_path)
        if "集录祈愿" not in old_gacha_info["item_list"]:
            old_gacha_info["item_list"]["集录祈愿"] = []
        return GachaLogInfo.parse_obj(old_gacha_info), True
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


def gacha_log_to_UIGF(user_id: str, uid: str) -> Tuple[bool, str, Optional[Path]]:
    """
    将抽卡记录转换为UIGF格式

    :param user_id: 用户id
    :param uid: 原神uid
    """
    data, state = load_history_info(user_id, uid)
    if not state:
        return False, f'UID{uid}还没有抽卡记录数据，可使用命令[更新抽卡记录]更新', None
    logger.info('原神抽卡记录', '➤', {'用户': user_id, 'UID': uid}, '导出抽卡记录', True)
    save_path = Path() / 'data' / 'LittlePaimon' / 'user_data' / 'gacha_log_data' / f'gacha_log_UIGF-{user_id}-{uid}.json'
    uigf_dict = {
        'info': {
            'uid':          uid,
            'lang':         'zh-cn',
            'export_time':  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'export_timestamp': int(time.time()),
            'export_app':   'LittlePaimon',
            'export_app_version': __version__,
            'uigf_version': 'v2.2'
        },
        'list': []
    }
    for items in data.item_list.values():
        for item in items:
            uigf_dict['list'].append({
                'gacha_type':      item.gacha_type,
                'item_id':         '',
                'count':           '1',
                'time':            item.time.strftime('%Y-%m-%d %H:%M:%S'),
                'name':            item.name,
                'item_type':       item.item_type,
                'rank_type':       item.rank_type,
                'id':              item.id,
                'uigf_gacha_type': item.gacha_type,
                'uid':             uid
            })
    save_json(uigf_dict, save_path)
    return True, '导出成功', save_path


async def get_gacha_log_data(user_id: str, uid: str):
    """
    使用authkey获取抽卡记录数据，并合并旧数据

    :param user_id: 用户id
    :param uid: 原神uid
    :return: 更新结果
    """
    await LastQuery.update_last_query(user_id, uid)
    new_num = 0
    type_new_num = {
        '角色祈愿': 0,
        '武器祈愿': 0,
        '常驻祈愿': 0,
        '新手祈愿': 0,
        '集录祈愿': 0
    }
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
                return f'UID{uid}的Stoken已失效，请重新绑定或刷新cookie后再更新抽卡记录'
            data = data['data']['list']
            if not data:
                break
            for item in data:
                item_info = GachaItem.parse_obj(item)
                if item_info not in gacha_log.item_list[pool_name]:
                    gacha_log.item_list[pool_name].append(item_info)
                    new_num += 1
                    type_new_num[pool_name] += 1
            end_id = data[-1]['id']
            await asyncio.sleep(1)
        logger.info('原神抽卡记录', f'➤➤<m>{pool_name}</m>', {}, '获取完成', True)
    for i in gacha_log.item_list.values():
        i.sort(key=lambda x: (x.time, x.id))
    gacha_log.update_time = datetime.datetime.now()
    save_gacha_log_info(user_id, uid, gacha_log)
    if new_num == 0:
        return f'UID{uid}更新完成，本次没有新增数据，可使用命令[查看抽卡记录]查看'
    msg = f'UID{uid}更新完成，本次共新增{new_num}条抽卡记录：\n'
    for pool_name, num in type_new_num.items():
        if num != 0:
            msg += f'{pool_name}{num}条\n'
    msg += '\n可使用命令[查看抽卡记录]查看'
    return msg


async def get_gacha_log_img(user_id: str, uid: str, nickname: str):
    """
    绘制抽卡记录图片入口

    :param user_id: 用户id
    :param uid: 原神uid
    :param nickname: 用户昵称
    :return: 抽卡记录图片
    """
    await LastQuery.update_last_query(user_id, uid)
    data, state = load_history_info(user_id, uid)
    if not state:
        return f'UID{uid}还没有抽卡记录数据，可使用命令[更新抽卡记录]更新'
    if player_info := await PlayerInfo.get_or_none(user_id=user_id, uid=uid):
        return await draw_gacha_log(player_info.user_id, player_info.uid, player_info.nickname, player_info.signature,
                                    data)
    else:
        return await draw_gacha_log(user_id, uid, nickname, None, data)


def create_import_command(user_id: int):
    """
    创建抽卡记录导入命令

    :param user_id: 用户id
    """
    def file_rule(event: NoticeEvent):
        if isinstance(event, GroupUploadNoticeEvent) or event.notice_type == 'offline_file':
            return event.dict()['user_id'] == user_id
        return False

    import_cmd = on_notice(priority=12, rule=Rule(file_rule), expire_time=datetime.timedelta(minutes=5), temp=True)
    import_cmd.plugin_name = 'Paimon_Gacha_Log'

    @import_cmd.handle()
    async def _(event: NoticeEvent):
        event_data = event.dict()
        file_name = event_data['file']['name']
        if not file_name.endswith('.json'):
            await import_cmd.finish('文件格式错误，请上传json文件', at_sender=True)
        file_url = event_data['file']['url']
        try:
            data = await aiorequests.get(url=file_url)
            data = data.json()
            new_num = 0
            uid = data['info']['uid']
            await import_cmd.send(f'开始导入UID{uid}的抽卡记录，请稍候...', at_sender=True)
            logger.info('原神抽卡记录', '➤', {'用户': user_id, 'UID': uid}, '导入抽卡记录', True)
            gacha_log, _ = load_history_info(str(event_data['user_id']), uid)
            for item in data['list']:
                pool_name = GACHA_TYPE_LIST[item['gacha_type']]
                item_info = GachaItem.parse_obj(item)
                if item_info not in gacha_log.item_list[pool_name]:
                    gacha_log.item_list[pool_name].append(item_info)
                    new_num += 1
            for i in gacha_log.item_list.values():
                i.sort(key=lambda x: (x.time, x.id))
            gacha_log.update_time = datetime.datetime.now()
            save_gacha_log_info(str(event_data['user_id']), uid, gacha_log)
            if new_num == 0:
                await import_cmd.send(f'UID{uid}抽卡记录导入完成，本次没有新增数据', at_sender=True)
            else:
                await import_cmd.send(f'UID{uid}抽卡记录导入完成，共新增{new_num}条抽卡记录', at_sender=True)
        except Exception:
            await import_cmd.finish('导入抽卡记录失败，请确认文件是否符合UIGF统一祈愿可交换标准', at_sender=True)
