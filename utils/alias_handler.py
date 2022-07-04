import difflib
from pathlib import Path
from typing import Union

from littlepaimon_utils.files import load_json


def get_short_name(name: str):
    """
        获取角色或武器的短名（2个字）
        :param name: 角色或武器名
        :return: 短名字符串
    """
    short_name = load_json(path=Path(__file__).parent / 'json_data' / 'short_name.json')
    return name if name not in short_name.keys() else short_name[name]


def get_id_by_name(name: str):
    """
        根据角色名字获取角色的id
        :param name: 角色名
        :return: id字符串
    """
    alias_file = load_json(path=Path(__file__).parent / 'json_data' / 'alias.json')
    name_list = alias_file['roles']
    for role_id, alias in name_list.items():
        if name in alias:
            return role_id


def get_name_by_id(role_id: str):
    """
        根据角色id获取角色名
        :param role_id: 角色id
        :return: 角色名字符串
    """
    alias_file = load_json(path=Path(__file__).parent / 'json_data' / 'alias.json')
    name_list = alias_file['roles']
    if role_id in name_list:
        return name_list[role_id][0]
    else:
        return None


def get_alias_by_name(name: str):
    """
        根据角色名字获取角色的别名
        :param name: 角色名
        :return: 别名列表
    """
    alias_file = load_json(path=Path(__file__).parent / 'json_data' / 'alias.json')
    name_list = alias_file['roles']
    for r in name_list.values():
        if name in r:
            return r
    return None


def get_match_alias(msg: str, type: str = 'roles', single_to_dict: bool = False) -> Union[str, list, dict]:
    """
        根据字符串消息，获取与之相似或匹配的角色、武器、原魔名
        :param msg: 消息
        :param type: 匹配类型，有roles、weapons、monsters
        :param single_to_dict: 是否将角色单结果也转换成{角色:id}字典
        :return: 匹配的字符串、列表或字典
    """
    alias_file = load_json(path=Path(__file__).parent / 'json_data' / 'alias.json')
    alias_list = alias_file[type]
    if msg in ['风主', '岩主', '雷主']:
        return msg
    elif type == 'roles':
        possible = {}
        for role_id, alias in alias_list.items():
            match_list = difflib.get_close_matches(msg, alias, cutoff=0.6, n=3)
            if msg in match_list:
                return {alias[0]: role_id} if single_to_dict else alias[0]
            elif match_list:
                possible[alias[0]] = role_id
        if len(possible) == 1:
            return {list(possible.keys())[0]: possible[list(possible.keys())[0]]} if single_to_dict else list(possible.keys())[0]
        return possible
    elif type == 'weapons':
        possible = []
        for name, alias in alias_list.items():
            match_list = difflib.get_close_matches(msg, alias, cutoff=0.4, n=3)
            if msg in match_list:
                return name
            elif match_list:
                possible.append(name)
        return possible
    elif type == 'monsters':
        match_list = difflib.get_close_matches(msg, alias_list, cutoff=0.4, n=5)
        return match_list[0] if len(match_list) == 1 else match_list
