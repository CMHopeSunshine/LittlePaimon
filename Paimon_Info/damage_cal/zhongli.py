from copy import deepcopy
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw
from littlepaimon_utils.files import load_json, load_image
from littlepaimon_utils.images import get_font, draw_center_text

from .common import resistance_coefficient as rc, defense_coefficient as dc, attr_common_fix, q_fix, e_fix, a_fix, \
    text_font, number_font

skill_data = load_json(path=Path(__file__).parent.parent.parent / 'utils' / 'json_data' / 'roles_data.json')['钟离']['skill']


def cal_shield_value(data: dict) -> float:
    """
    计算钟离的护盾值
    :param data: 角色数据
    :return: 护盾值
    """
    health = data['属性']['基础生命'] + data['属性']['额外生命']
    shield_power = data['属性']['护盾强效']
    skill_level = data['天赋'][1]['等级'] - 1
    fixed_value = int(skill_data['元素战技·地心']['数值']['护盾基础吸收量'][skill_level].replace(',', ''))
    percent_value = float(skill_data['元素战技·地心']['数值']['护盾附加吸收量'][skill_level].replace('%最大生命值', '')) / 100.0
    return (health * percent_value + fixed_value) * (1 + shield_power)


def cal_resonance_dmg(data: dict, extra: dict) -> Tuple[float, float]:
    """
    计算共鸣伤害
    :param data: 角色数据
    :param extra: 针对元素战技的额外数值
    :return: 单次共鸣的期望伤害和暴击后伤害
    """
    role_level = data['等级']
    skill_level = data['天赋'][1]['等级'] - 1
    health = data['属性']['基础生命'] + data['属性']['额外生命']
    attack = data['属性']['基础攻击'] + data['属性']['额外攻击']
    cr = data['属性']['暴击率'] + extra['暴击率']
    cd = data['属性']['暴击伤害']
    dmg_bonus = 1 + data['属性']['伤害加成'][6] + extra['增伤']
    percent_value = float(skill_data['元素战技·地心']['数值']['岩脊伤害/共鸣伤害'][skill_level].split('/')[1].replace('%', '')) / 100.0
    if role_level >= 70:
        damage = (attack * percent_value + health * 0.019) * (1 + cr * cd) * dmg_bonus * rc(0.1, 0.2) * dc(role_level)
    else:
        damage = (attack * percent_value) * (1 + cr * cd) * dmg_bonus * rc(0.1, 0.2) * dc(role_level)
    return damage, damage / (1 + cr * cd) * (1 + cd)


def cal_star_dmg(data: dict, extra: dict) -> Tuple[float, float]:
    """
    计算天星伤害
    :param data: 角色数据
    :param extra: 针对大招的额外数值
    :return: 大招天星的期望伤害和暴击后伤害
    """
    role_level = data['等级']
    skill_level = data['天赋'][2]['等级'] - 1
    health = data['属性']['基础生命'] + data['属性']['额外生命']
    attack = data['属性']['基础攻击'] + data['属性']['额外攻击']
    cr = data['属性']['暴击率'] + extra['暴击率']
    cd = data['属性']['暴击伤害']
    dmg_bonus = 1 + data['属性']['伤害加成'][6] + extra['增伤']
    percent_value = float(skill_data['元素爆发·天星']['数值']['技能伤害'][skill_level].replace('%', '')) / 100.0
    if role_level >= 70:
        damage = (attack * percent_value + health * 0.33) * (1 + cr * cd) * dmg_bonus * rc(0.1,
                                                                                           0.2) * dc(
            role_level)
    else:
        damage = (attack * percent_value) * (1 + cr * cd) * dmg_bonus * rc(0.1, 0.2) * dc(role_level)
    return damage, damage / (1 + cr * cd) * (1 + cd)


def cal_attack_dmg(data: dict, extra: dict) -> tuple:
    """
    计算踢枪单段伤害
    :param data: 角色数据
    :param extra: 针对普攻重击等的额外数值
    :return: 踢枪的期望伤害和暴击后伤害
    """
    role_level = data['等级']
    skill_level = data['天赋'][0]['等级'] - 1
    health = data['属性']['基础生命'] + data['属性']['额外生命']
    attack = data['属性']['基础攻击'] + data['属性']['额外攻击']
    cr = data['属性']['暴击率'] + extra['普攻暴击率']
    cr_ly = data['属性']['暴击率']
    cd = data['属性']['暴击伤害']
    dmg_bonus = 1 + data['属性']['伤害加成'][0] + extra['普攻增伤']
    dmg_bonus_ly = 1 + data['属性']['伤害加成'][0]
    percent_value = float(skill_data['普通攻击·岩雨']['数值']['五段伤害'][skill_level].replace('%×4', '')) / 100.0
    if role_level >= 70:
        damage = (attack * percent_value + health * 0.0139) * (1 + cr * cd) * dmg_bonus * rc(0.1, 0.2) * dc(role_level)
    else:
        damage = (attack * percent_value) * (1 + cr * cd) * dmg_bonus * rc(0.1, 0.2) * dc(role_level)
    if data['武器']['名称'] == '流月针':
        ly_damage = (attack * (0.15 + 0.05 * data['武器']['精炼等级'])) * (1 + cr_ly * cd) * dmg_bonus_ly * rc(0.1, 0.2) * dc(
            role_level)
        return (damage, ly_damage), (damage / (1 + cr * cd) * (1 + cd), ly_damage / (1 + cr_ly * cd) * (1 + cd))
    else:
        return damage, damage / (1 + cr * cd) * (1 + cd)


def draw_zhongli_dmg(data: dict):
    mask_top = load_image(path=Path() / 'resources' / 'LittlePaimon' / 'player_card2' / '遮罩top.png')
    mask_body = load_image(path=Path() / 'resources' / 'LittlePaimon' / 'player_card2' / '遮罩body.png')
    mask_bottom = load_image(path=Path() / 'resources' / 'LittlePaimon' / 'player_card2' / '遮罩bottom.png')

    data = deepcopy(data)
    height = 5 * 60 - 20
    data['伤害描述'] = ['护盾减抗']
    data = attr_common_fix(data)
    data, q_value = q_fix(data)
    data, e_value = e_fix(data)
    data, a_value = a_fix(data)
    bg = Image.new('RGBA', (948, height + 80), (0, 0, 0, 0))
    bg.alpha_composite(mask_top, (0, 0))
    bg.alpha_composite(mask_body.resize((948, height)), (0, 60))
    bg.alpha_composite(mask_bottom, (0, height + 60))
    bg_draw = ImageDraw.Draw(bg)
    # 画线
    bg_draw.line((250, 0, 250, 948), (255, 255, 255, 75), 2)
    bg_draw.line((599, 0, 599, 60), (255, 255, 255, 75), 2)
    bg_draw.line((599, 120, 599, 300), (255, 255, 255, 75), 2)
    bg_draw.line((0, 60, 948, 60), (255, 255, 255, 75), 2)
    bg_draw.line((0, 120, 948, 120), (255, 255, 255, 75), 2)
    bg_draw.line((0, 180, 948, 180), (255, 255, 255, 75), 2)
    bg_draw.line((0, 240, 948, 240), (255, 255, 255, 75), 2)
    bg_draw.line((0, 300, 948, 300), (255, 255, 255, 75), 2)

    # 顶栏
    draw_center_text(bg_draw, '伤害计算', 0, 250, 11, 'white', get_font(30, text_font))
    draw_center_text(bg_draw, '期望伤害', 250, 599, 11, 'white', get_font(30, text_font))
    draw_center_text(bg_draw, '暴击伤害', 599, 948, 11, 'white', get_font(30, text_font))

    # 护盾值
    draw_center_text(bg_draw, '玉璋护盾', 0, 250, 73, 'white', get_font(30, text_font))
    shield = cal_shield_value(data)
    draw_center_text(bg_draw, str(int(shield)), 250, 948, 76, 'white', get_font(30, number_font))

    # 共鸣伤害
    draw_center_text(bg_draw, '共鸣伤害', 0, 250, 133, 'white', get_font(30, text_font))
    expect_dmg, crit_dmg = cal_resonance_dmg(data, e_value)
    draw_center_text(bg_draw, str(int(expect_dmg)), 250, 599, 136, 'white', get_font(30, number_font))
    draw_center_text(bg_draw, str(int(crit_dmg)), 599, 948, 136, 'white', get_font(30, number_font))

    # 天星伤害
    draw_center_text(bg_draw, '天星伤害', 0, 250, 193, 'white', get_font(30, text_font))
    expect_dmg, crit_dmg = cal_star_dmg(data, q_value)
    draw_center_text(bg_draw, str(int(expect_dmg)), 250, 599, 196, 'white', get_font(30, number_font))
    draw_center_text(bg_draw, str(int(crit_dmg)), 599, 948, 196, 'white', get_font(30, number_font))

    # 踢枪伤害
    draw_center_text(bg_draw, '踢枪伤害', 0, 250, 253, 'white', get_font(30, text_font))
    expect_dmg, crit_dmg = cal_attack_dmg(data, a_value)
    if isinstance(expect_dmg, tuple):
        draw_center_text(bg_draw, f'{int(expect_dmg[0])}+{int(expect_dmg[1])}', 250, 599, 256, 'white', get_font(30, number_font))
    else:
        draw_center_text(bg_draw, str(int(expect_dmg)), 250, 599, 256, 'white', get_font(30, number_font))
    if isinstance(crit_dmg, tuple):
        draw_center_text(bg_draw, f'{int(crit_dmg[0])}+{int(crit_dmg[1])}', 599, 948, 256, 'white', get_font(30, number_font))
    else:
        draw_center_text(bg_draw, str(int(crit_dmg)), 599, 948, 256, 'white', get_font(30, number_font))

    # 额外说明
    draw_center_text(bg_draw, '额外说明', 0, 250, 313, 'white', get_font(30, text_font))
    draw_center_text(bg_draw, '，'.join(data['伤害描述']), 250, 948, 313, 'white', get_font(30, text_font))
    return bg
