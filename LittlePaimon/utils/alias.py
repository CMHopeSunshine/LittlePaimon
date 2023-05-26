from difflib import get_close_matches
from typing import Union, Literal, List, Optional, Dict

from .files import load_json
from .path import JSON_DATA


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
    name_list = load_json(JSON_DATA / 'alias.json')['角色']
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
    name_list = load_json(JSON_DATA / 'alias.json')['角色']
    return name_list[role_id][0] if role_id in name_list else None


def get_alias_by_name(name: str) -> Optional[List[str]]:
    """
    根据角色名字获取角色的别名
        :param name: 角色名
        :return: 别名列表
    """
    name_list = load_json(JSON_DATA / 'alias.json')['角色']
    return next((r for r in name_list.values() if name in r), None)


ALIAS_TYPE = Literal['角色', '武器', '原魔', '圣遗物']


def get_match_alias(name: str, types: Union[List[ALIAS_TYPE], ALIAS_TYPE] = None,
                    one_to_list: bool = False) -> Union[Dict[str, List[str]], List[str]]:
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
    alias_file = load_json(JSON_DATA / 'alias.json')
    include_flag = False
    for type in types:
        alias_list = alias_file[type]
        matches[type] = []
        if type == '角色':
            # 如果是主角，则返回旅行者+元素类型
            if name.startswith(('风', '岩', '雷', '草', '水', '火', '冰')) and name.endswith(
                    ('主', '主角', '旅行者')):
                matches[type].append(f'旅行者{name[0]}')
            elif name.startswith('旅行者') and name.endswith(('风', '岩', '雷', '草', '水', '火', '冰')):
                matches[type].append(name)
            else:
                for alias in alias_list.values():
                    # 如果该角色别名列表里有和待匹配的name，则只保留该角色
                    if name in alias:
                        matches[type] = [alias[0]]
                        include_flag = True
                        break
                    # 否则，则模糊匹配，有匹配到的别名，具把角色添加到匹配列表
                    if get_close_matches(name, alias, cutoff=0.6):
                        matches[type].append(alias[0])
        elif type in {'武器', '圣遗物'}:
            # 逻辑和角色一样
            for raw_name, alias in alias_list.items():
                if name in alias:
                    matches[type] = [raw_name]
                    include_flag = True
                    break
                if get_close_matches(name, alias, cutoff=0.6):
                    matches[type].append(raw_name)
        elif type == '原魔':
            # 如果已经有精准匹配到的角色、武器或圣遗物，则不再继续匹配原魔
            if not include_flag:
                # 尽可能的匹配所有类似的原魔名
                for raw_name, alias in alias_list.items():
                    if get_close_matches(name, alias, cutoff=0.5):
                        matches[type].append(raw_name)
        if not matches[type]:
            del matches[type]

    if one_to_list and len(matches) == 1:
        # 如果one_to_list为true且匹配到的种类只有一种，则以列表形式直接返回该种类匹配结果
        return list(matches.values())[0]
    else:
        # 否则，以字典形式返回各种类的匹配结果
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
    if info := load_json(JSON_DATA / 'genshin_info.json').get(str(chara_id)):
        side_icon = info['SideIconName']
    else:
        return None
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
    icon_list = load_json(JSON_DATA / 'weapon.json')['Icon']
    return icon_list.get(name)


def get_artifact_icon(name: str) -> Optional[str]:
    icon_list = load_json(JSON_DATA / 'artifact.json')
    for k, v in icon_list['Name'].items():
        if name == v:
            return k
        


def get_constellation_icon(name: str) -> Optional[str]:
    icon_list = load_json(JSON_DATA / 'role_talent.json')
    for k, v in icon_list['Name'].items():
        if name == v:
            return icon_list['Icon'].get(k)
