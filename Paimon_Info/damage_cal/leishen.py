from copy import deepcopy
from pathlib import Path
from typing import Tuple
from PIL import Image, ImageDraw
from utils.PIL_util import get_font, draw_center_text
from utils.file_handler import load_json, load_image
from .common import resistance_coefficient as rc, defense_coefficient as dc, attr_common_fix, q_fix, e_fix, a_fix

mask_top = load_image(path=Path(__file__).parent.parent.parent / 'res' / 'player_card2' / '遮罩top.png')
mask_body = load_image(path=Path(__file__).parent.parent.parent / 'res' / 'player_card2' / '遮罩body.png')
mask_bottom = load_image(path=Path(__file__).parent.parent.parent / 'res' / 'player_card2' / '遮罩bottom.png')
skill_data = load_json(path=Path(__file__).parent.parent.parent / 'utils' / 'json' / 'roles_data.json')['雷电将军']['skill']


def cal_e_dmg(data: dict, extra: dict) -> Tuple[float, float]:
    """
    计算雷神单次E的伤害
    :param data: 角色数据
    :param extra: 针对元素战技的额外数值
    :return: 期望伤害和暴击后伤害
    """
    role_level = data['等级']
    skill_level = data['天赋'][1]['等级'] - 1
    attack = data['属性']['基础攻击'] + data['属性']['额外攻击']
    cr = data['属性']['暴击率'] + extra['暴击率']
    cd = data['属性']['暴击伤害']
    if len(data['命座']) < 2:
        defense = dc(role_level)
    else:
        defense = dc(role_level, ignore=0.6)
    dmg_bonus = 1 + data['属性']['伤害加成'][2] + extra['增伤']
    percent_value = float(skill_data['神变·恶曜开眼']['数值']['协同攻击伤害'][skill_level].replace('%', '')) / 100.0
    damage = (attack * percent_value) * (1 + cr * cd) * dmg_bonus * rc() * defense
    return damage, damage / (1 + cr * cd) * (1 + cd)


def cal_q_dmg(data: dict, extra: dict, num: int) -> Tuple[float, float]:
    """
    计算雷神梦想一刀的伤害
    :param data: 角色数据
    :param extra: 针对大招的额外数值
    :param num: 愿力层数
    :return: 期望伤害和暴击后伤害
    """
    role_level = data['等级']
    skill_level = data['天赋'][2]['等级'] - 1
    e_skill_level = data['天赋'][1]['等级'] - 1
    e_bonus = float(
        skill_data['神变·恶曜开眼']['数值']['元素爆发伤害提高'][e_skill_level].replace('每点元素能量', '').replace('%', '')) / 100.0 * 90
    attack = data['属性']['基础攻击'] + data['属性']['额外攻击']
    cr = data['属性']['暴击率'] + extra['暴击率']
    cd = data['属性']['暴击伤害']
    if len(data['命座']) < 2:
        defense = dc(role_level)
    else:
        defense = dc(role_level, ignore=0.6)
    dmg_bonus = 1 + data['属性']['伤害加成'][2] + extra['增伤'] + e_bonus
    percent_value = float(skill_data['奥义·梦想真说']['数值']['梦想一刀基础伤害'][skill_level].replace('%', '')) / 100.0
    num_value = float(skill_data['奥义·梦想真说']['数值']['愿力加成'][skill_level].split('%/')[0].replace('每层', '')) / 100.0 * num
    damage = (attack * (percent_value + num_value)) * (1 + cr * cd) * dmg_bonus * rc() * defense
    return damage, damage / (1 + cr * cd) * (1 + cd)


def cal_q_a_dmg(data: dict, extra: dict, num: int) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """
    计算雷神梦想一心重击的伤害
    :param data: 角色数据
    :param extra: 针对大招的额外数值
    :param num: 愿力层数
    :return: 期望伤害和暴击后伤害
    """
    role_level = data['等级']
    skill_level = data['天赋'][2]['等级'] - 1
    e_skill_level = data['天赋'][1]['等级'] - 1
    e_bonus = float(
        skill_data['神变·恶曜开眼']['数值']['元素爆发伤害提高'][e_skill_level].replace('每点元素能量', '').replace('%', '')) / 100.0 * 90
    attack = data['属性']['基础攻击'] + data['属性']['额外攻击']
    cr = data['属性']['暴击率'] + extra['暴击率']
    cd = data['属性']['暴击伤害']
    if len(data['命座']) < 2:
        defense = dc(role_level)
    else:
        defense = dc(role_level, ignore=0.6)
    dmg_bonus = 1 + data['属性']['伤害加成'][2] + extra['增伤'] + e_bonus
    percent_value = skill_data['奥义·梦想真说']['数值']['重击伤害'][skill_level].split('+')
    percent_value1 = float(percent_value[0].replace('%', '')) / 100.0
    percent_value2 = float(percent_value[1].replace('%', '')) / 100.0
    num_value = float(skill_data['奥义·梦想真说']['数值']['愿力加成'][skill_level].split('%/')[1].replace('%攻击力', '')) / 100.0 * num
    damage1 = (attack * (percent_value1 + num_value)) * (1 + cr * cd) * dmg_bonus * rc() * defense
    damage2 = (attack * (percent_value2 + num_value)) * (1 + cr * cd) * dmg_bonus * rc() * defense
    return (damage1, damage1 / (1 + cr * cd) * (1 + cd)), (damage2, damage2 / (1 + cr * cd) * (1 + cd))


def cal_q_energy(data: dict) -> float:
    """
    计算雷神大招的能量回复
    :param data: 角色数据
    :return: 能量回复
    """
    role_level = data['等级']
    if role_level >= 70:
        extra_energy = (data['属性']['元素充能效率'] - 1) * 0.6
    else:
        extra_energy = 0
    skill_level = data['天赋'][2]['等级'] - 1
    energy = float(skill_data['奥义·梦想真说']['数值']['梦想一心能量恢复'][skill_level]) * (1 + extra_energy) * 5
    return energy


def draw_leishen_dmg(data: dict):
    data = deepcopy(data)
    height = 5 * 60 - 20
    data['伤害描述'] = ['满愿力']
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
    bg_draw.line((599, 0, 599, 240), (255, 255, 255, 75), 2)
    bg_draw.line((0, 60, 948, 60), (255, 255, 255, 75), 2)
    bg_draw.line((0, 120, 948, 120), (255, 255, 255, 75), 2)
    bg_draw.line((0, 180, 948, 180), (255, 255, 255, 75), 2)
    bg_draw.line((0, 240, 948, 240), (255, 255, 255, 75), 2)
    bg_draw.line((0, 300, 948, 300), (255, 255, 255, 75), 2)
    # 顶栏
    draw_center_text(bg_draw, '伤害计算', 0, 250, 11, 'white', get_font(30))
    draw_center_text(bg_draw, '期望伤害', 250, 599, 11, 'white', get_font(30))
    draw_center_text(bg_draw, '暴击伤害', 599, 948, 11, 'white', get_font(30))

    # 协同攻击
    draw_center_text(bg_draw, '协同攻击', 0, 250, 73, 'white', get_font(30))
    expect_dmg, crit_dmg = cal_e_dmg(data, e_value)
    draw_center_text(bg_draw, str(int(expect_dmg)), 250, 599, 76, 'white', get_font(30, 'number.ttf'))
    draw_center_text(bg_draw, str(int(crit_dmg)), 599, 948, 76, 'white', get_font(30, 'number.ttf'))

    # 梦想一刀
    draw_center_text(bg_draw, '梦想一刀', 0, 250, 133, 'white', get_font(30))
    expect_dmg, crit_dmg = cal_q_dmg(data, q_value, 60)
    draw_center_text(bg_draw, str(int(expect_dmg)), 250, 599, 136, 'white', get_font(30, 'number.ttf'))
    draw_center_text(bg_draw, str(int(crit_dmg)), 599, 948, 136, 'white', get_font(30, 'number.ttf'))

    # 梦想一心重击
    draw_center_text(bg_draw, '梦想一心重击', 0, 250, 193, 'white', get_font(30))
    expect_dmg, crit_dmg = cal_q_a_dmg(data, q_value, 60)
    draw_center_text(bg_draw, f'{int(expect_dmg[0])}+{int(expect_dmg[1])}', 250, 599, 196, 'white',
                     get_font(30, 'number.ttf'))
    draw_center_text(bg_draw, f'{int(crit_dmg[0])}+{int(crit_dmg[1])}', 599, 948, 196, 'white',
                     get_font(30, 'number.ttf'))

    # 梦想一心能量回复
    draw_center_text(bg_draw, '梦想一心能量', 0, 250, 253, 'white', get_font(30))
    energy = cal_q_energy(data)
    draw_center_text(bg_draw, str(round(energy, 1)), 250, 948, 256, 'white', get_font(30, 'number.ttf'))

    # 额外说明
    draw_center_text(bg_draw, '额外说明', 0, 250, 313, 'white', get_font(30))
    draw_center_text(bg_draw, '，'.join(data['伤害描述']), 250, 948, 313, 'white', get_font(30))
    return bg
