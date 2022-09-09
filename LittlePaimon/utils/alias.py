import difflib
from typing import Union, Literal, List, Optional

from .files import load_json
from LittlePaimon.config import JSON_DATA

alias_file = load_json(JSON_DATA / 'alias.json')
info_file = load_json(JSON_DATA / 'genshin_info.json')
weapon_file = load_json(JSON_DATA / 'weapon.json')


def get_id_by_name(name: str) -> Optional[str]:
    """
        根据角色名字获取角色的id
        :param name: 角色名
        :return: id字符串
    """
    name_list = alias_file['角色']
    for role_id, alias in name_list.items():
        if name in alias:
            return role_id


def get_name_by_id(role_id: Union[str, int]) -> Optional[str]:
    """
        根据角色id获取角色名
        :param role_id: 角色id
        :return: 角色名字符串
    """
    if isinstance(role_id, int):
        role_id = str(role_id)
    name_list = alias_file['角色']
    return name_list[role_id][0] if role_id in name_list else None


def get_alias_by_name(name: str) -> Optional[List[str]]:
    """
        根据角色名字获取角色的别名
        :param name: 角色名
        :return: 别名列表
    """
    name_list = alias_file['角色']
    return next((r for r in name_list.values() if name in r), None)


def get_match_alias(msg: str, type: Literal['角色', '武器', '原魔', '圣遗物'] = '角色', single_to_dict: bool = False) -> Union[
    str, list, dict]:
    """
        根据字符串消息，获取与之相似或匹配的角色、武器、原魔名
        :param msg: 消息
        :param type: 匹配类型，有roles、weapons、monsters
        :param single_to_dict: 是否将角色单结果也转换成{角色:id}字典
        :return: 匹配的字符串、列表或字典
    """
    alias_list = alias_file[type]
    if msg in {'风主', '岩主', '雷主', '草主'}:
        return msg
    elif type == '角色':
        possible = {}
        for role_id, alias in alias_list.items():
            match_list = difflib.get_close_matches(msg, alias, cutoff=0.6, n=3)
            if msg in match_list:
                return {alias[0]: role_id} if single_to_dict else alias[0]
            elif match_list:
                possible[alias[0]] = role_id
        if len(possible) == 1:
            return {list(possible.keys())[0]: possible[list(possible.keys())[0]]} if single_to_dict else \
            list(possible.keys())[0]
        return possible
    elif type in {'武器', '圣遗物'}:
        possible = []
        for name, alias in alias_list.items():
            match_list = difflib.get_close_matches(msg, alias, cutoff=0.4, n=3)
            if msg in match_list:
                return name
            elif match_list:
                possible.append(name)
        return possible
    elif type == '原魔':
        match_list = difflib.get_close_matches(msg, alias_list, cutoff=0.4, n=5)
        return match_list[0] if len(match_list) == 1 else match_list


def get_chara_icon(name: Optional[str] = None, chara_id: Optional[int] = None,
                   icon_type: Literal['avatar', 'card', 'splash', 'slice', 'side'] = 'avatar') -> Optional[str]:
    """
        根据角色名字或id获取角色的图标
        :param name: 角色名
        :param chara_id：角色id
        :param icon_type: 图标类型，有roles、weapons、monsters
        :return: 图标字符串
    """
    if name and not chara_id:
        chara_id = get_id_by_name(name)
    info = info_file.get(str(chara_id))
    if not info:
        return None
    side_icon = info['SideIconName']
    if icon_type == 'side':
        return side_icon
    elif icon_type == 'avatar':
        return side_icon.replace('_Side', '')
    elif icon_type == 'card':
        return side_icon.replace('_Side', '') + '_Card'
    elif icon_type == 'splash':
        return side_icon.replace('Icon_Side', 'Img').replace('UI_', 'UI_Gacha_')
    elif icon_type == 'slice':
        return side_icon.replace('_Side', '').replace('UI_', 'UI_Gacha_')


def get_weapon_icon(name: str) -> Optional[str]:
    icon_list = weapon_file['Icon']
    return icon_list.get(name)
