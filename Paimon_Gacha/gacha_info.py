import os
from utils.file_handler import load_json, save_json

RES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'res', 'gacha_res')
USER_INFO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_data', 'user_gacha_info.json')
ROLE_1_PATH = os.path.join(RES_PATH, "DIY_gacha_pool", "role_1.json")
ROLE_2_PATH = os.path.join(RES_PATH, "DIY_gacha_pool", "role_2.json")
WEAPON_PATH = os.path.join(RES_PATH, "DIY_gacha_pool", "weapon.json")
All_STAR_PATH = os.path.join(RES_PATH, "DIY_gacha_pool", "all_star.json")

user_info = load_json(path=USER_INFO_PATH)
role_1_pool = load_json(path=ROLE_1_PATH)
role_2_pool = load_json(path=ROLE_2_PATH)
weapon_pool = load_json(path=WEAPON_PATH)
all_star = load_json(path=All_STAR_PATH)


def save_user_info():
    save_json(data=user_info, path=USER_INFO_PATH)


def init_user_info(uid: str):
    if uid not in user_info:
        user_info[uid] = {}
        user_info[uid]["fate"] = 200
        user_info[uid]["gacha_list"] = {}
        user_info[uid]["gacha_list"]["wish_total"] = 0
        user_info[uid]["gacha_list"]["wish_4"] = 0
        user_info[uid]["gacha_list"]["wish_5"] = 0
        user_info[uid]["gacha_list"]["wish_4_up"] = 0
        user_info[uid]["gacha_list"]["wish_5_up"] = 0
        user_info[uid]["gacha_list"]["gacha_5_role"] = 0
        user_info[uid]["gacha_list"]["gacha_5_weapon"] = 0
        user_info[uid]["gacha_list"]["gacha_5_permanent"] = 0
        user_info[uid]["gacha_list"]["gacha_4_role"] = 0
        user_info[uid]["gacha_list"]["gacha_4_weapon"] = 0
        user_info[uid]["gacha_list"]["gacha_4_permanent"] = 0
        user_info[uid]["gacha_list"]["is_up_5_role"] = False
        user_info[uid]["gacha_list"]["is_up_5_weapon"] = False
        user_info[uid]["gacha_list"]["is_up_4_role"] = False
        user_info[uid]["gacha_list"]["is_up_4_weapon"] = False
        user_info[uid]["gacha_list"]["dg_name"] = ''
        user_info[uid]["gacha_list"]["dg_time"] = 0
        user_info[uid]["role_list"] = {}
        user_info[uid]["role_list"]["旅行者"] = {}
        user_info[uid]["role_list"]["旅行者"]["星级"] = '★★★★★'
        user_info[uid]["role_list"]["旅行者"]["数量"] = 6
        user_info[uid]["role_list"]["旅行者"]["出货"] = [0]
        user_info[uid]["weapon_list"] = {}
        save_user_info()
