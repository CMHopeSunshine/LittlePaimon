import re
from difflib import get_close_matches
from typing import Union, Literal, List, Optional, Dict

from .files import load_json
from .path import JSON_DATA, GACHA_RES

alias_file = load_json(JSON_DATA / 'alias.json')
info_file = load_json(JSON_DATA / 'genshin_info.json')
weapon_file = load_json(JSON_DATA / 'weapon.json')
item_type_file = load_json(GACHA_RES / 'type.json')
type_file = load_json(JSON_DATA / '类型.json')

WEAPON_TYPE_ALIAS = {
    '单手剑': '单手剑',
    '双手剑': '双手剑',
    '大剑': '双手剑',
    '长柄武器': '长柄武器',
    '枪': '长柄武器',
    '长枪': '长柄武器',
    '长柄': '长柄武器',
    '法器': '法器',
    '法书': '法器',
    '书': '法器',
    '弓': '弓',
    '弓箭': '弓'
}


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


ALIAS_TYPE = Literal['角色', '武器', '原魔', '圣遗物']


def get_match_alias(name: str, types: Union[List[ALIAS_TYPE], ALIAS_TYPE] = None,
                    one_to_list: bool = False) -> Union[
    Dict[str, List[str]], List[str]]:
    """
    根据字符串消息，获取与之相似或匹配的角色、武器、原魔名
        :param name: 名称
        :param types: 匹配类型，有'角色', '武器', '原魔', '圣遗物'
        :param one_to_list: 只有一种匹配结果时是否直接返回其列表
        :return: 匹配结果
    """
    if types is None:
        types = ['角色']
    elif isinstance(types, str):
        types = [types]
    matches = {}
    for type in types:
        alias_list = alias_file[type]
        matches[type] = []
        if type == '角色':
            if name.startswith(('风', '岩', '雷', '草', '水', '火', '冰')) and name.endswith(
                    ('主', '主角', '旅行者')):
                matches[type].append(f'旅行者{name[0]}')
            elif name.startswith('旅行者') and name.endswith(('风', '岩', '雷', '草', '水', '火', '冰')):
                matches[type].append(name)
            else:
                for alias in alias_list.values():
                    if name in alias:
                        matches[type] = [alias[0]]
                        break
                    if get_close_matches(name, alias, cutoff=0.6):
                        matches[type].append(alias[0])
        elif type in {'武器', '圣遗物'}:
            for raw_name, alias in alias_list.items():
                if name in alias:
                    matches[type] = [raw_name]
                    break
                else:
                    if get_close_matches(name, alias, cutoff=0.6):
                        matches[type].append(raw_name)
        elif type == '原魔':
            for raw_name, alias in alias_list.items():
                if get_close_matches(name, alias, cutoff=0.5):
                    matches[type].append(raw_name)
        if not matches[type]:
            del matches[type]
    if one_to_list and len(matches) == 1:
        return list(matches.values())[0]
    else:
        return matches


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
    if info := info_file.get(str(chara_id)):
        side_icon = info['SideIconName']
    else:
        return None
    # UI_AvatarIcon_Side_Wanderer
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
