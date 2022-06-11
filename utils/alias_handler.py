import difflib
from typing import Union
from .file_handler import load_json
import os


def get_short_name(name: str):
    short_name = load_json(path=os.path.join(os.path.dirname(__file__),'short_name.json'))
    return name if name not in short_name.keys() else short_name[name]


def get_id_by_name(name: str):
    alias_file = load_json(path=os.path.join(os.path.dirname(__file__), 'alias.json'))
    name_list = alias_file['roles']
    for role_id, alias in name_list.items():
        if name in alias:
            return role_id


def get_name_by_id(role_id: str):
    alias_file = load_json(path=os.path.join(os.path.dirname(__file__), 'alias.json'))
    name_list = alias_file['roles']
    if role_id in name_list:
        return name_list[role_id][0]
    else:
        return None



def get_match_alias(msg: str, type: str = 'roles', single_to_dict: bool = False) -> Union[str, list, dict]:
    alias_file = load_json(path=os.path.join(os.path.dirname(__file__), 'alias.json'))
    alias_list = alias_file[type]
    if msg in ['风主', '岩主', '雷主']:
        return msg
    elif type == 'roles':
        possible = {}
        for role_id, alias in alias_list.items():
            match_list = difflib.get_close_matches(msg, alias, cutoff=0.6, n=3)
            if msg in match_list:
                if single_to_dict:
                    return {alias[0]: role_id}
                else:
                    return alias[0]
            elif match_list:
                possible[alias[0]] = role_id
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
