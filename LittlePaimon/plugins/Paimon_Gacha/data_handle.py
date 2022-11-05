from LittlePaimon.utils.files import load_json, save_json
from LittlePaimon.utils.path import GACHA_SIM


def load_user_data(user_id: int) -> dict:
    user_data_path = GACHA_SIM / f'{user_id}.json'
    if user_data_path.exists():
        return load_json(user_data_path)
    new_data = {
        '抽卡数据': {
            '抽卡总数':         0,
            '4星出货数':        0,
            '5星出货数':        0,
            '4星up出货数':      0,
            '5星up出货数':      0,
            '角色池未出5星数':     0,
            '武器池未出5星数':     0,
            '常驻池未出5星数':     0,
            '角色池未出4星数':     0,
            '武器池未出4星数':     0,
            '常驻池未出4星数':     0,
            '角色池5星下次是否为up': False,
            '武器池5星下次是否为up': False,
            '角色池4星下次是否为up': False,
            '武器池4星下次是否为up': False,
            '定轨武器名称':       '',
            '定轨能量':         0
        },
        '角色列表': {},
        '武器列表': {}
    }
    save_json(new_data, user_data_path)
    return new_data


def save_user_data(user_id: int, data: dict):
    user_data_path = GACHA_SIM / f'{user_id}.json'
    save_json(data, user_data_path)
