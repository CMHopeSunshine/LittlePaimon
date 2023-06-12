from typing import Optional
from LittlePaimon.utils.path import USER_DATA_PATH
from LittlePaimon.utils.files import load_json, save_json
from LittlePaimon.utils.requests import aiorequests

from .models import Character

API = "https://api.mihomo.me/sr_info_parsed/"


def set_uid(user_id: str, uid: str):
    data = load_json(USER_DATA_PATH / "star_rail_uid.json")
    data[user_id] = uid
    save_json(data, USER_DATA_PATH / "star_rail_uid.json")


def get_uid(user_id: str) -> Optional[str]:
    data = load_json(USER_DATA_PATH / "star_rail_uid.json")
    return data.get(user_id)


async def update_info(uid: str) -> str:
    try:
        path = USER_DATA_PATH / "star_rail_info" / f"{uid}.json"
        resp = await aiorequests.get(
            API + uid, headers={"User-Agent": "LittlePaimon/3.0"}, follow_redirects=True
        )
        data = resp.json()
        if "player" not in data and "characters" not in data:
            return "获取星穹铁道面板数据失败，请检查uid是否正确或者稍后再试"
        if not path.exists():
            save_json(data, path)
        else:
            old_data = load_json(path)
            old_data["player"] = data["player"]
            # 如果旧数据和新数据都有相同ID的角色，就更新旧数据，否则就添加新数据
            for new_char in data["characters"]:
                for old_char in old_data["characters"]:
                    if new_char["id"] == old_char["id"]:
                        old_char.update(new_char)
                        break
                else:
                    old_data["characters"].append(new_char)
            save_json(old_data, path)
        new_char_name = " ".join([char["name"] for char in data["characters"]])
        return f"成功更新以下星穹铁道角色面板：\n{new_char_name}\n可以使用“星铁面板 角色名”命令查看面板"
    except Exception as e:
        return f"获取星穹铁道面板数据失败：{e}"
    

def get_info(uid: str, chara_name: str) -> Optional[Character]:
    path = USER_DATA_PATH / "star_rail_info" / f"{uid}.json"
    if not path.exists():
        return None
    data = load_json(path)
    for char in data["characters"]:
        if char["name"] == chara_name:
            return Character.parse_obj(char)
    return None
