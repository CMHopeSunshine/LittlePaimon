from copy import deepcopy
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw
from littlepaimon_utils.files import load_json, load_image
from littlepaimon_utils.images import get_font, draw_center_text

from .common import resistance_coefficient as rc, defense_coefficient as dc, attr_common_fix, q_fix, e_fix, a_fix, \
    growth_reaction, text_font, number_font

skill_data = load_json(path=Path(__file__).parent.parent.parent / 'utils' / 'json_data' / 'roles_data.json')['香菱']['skill']


def cal_e_dmg(data: dict, extra: dict) -> Tuple[float, float]:
    """
    计算香菱锅巴的伤害
    :param data: 角色数据
    :param extra: 针对元素战技的额外数值
    :return: 期望伤害和暴击后伤害
    """
    role_level = data['等级']
    skill_level = data['天赋'][1]['等级'] - 1
    attack = data['属性']['基础攻击'] + data['属性']['额外攻击']
    cr = data['属性']['暴击率'] + extra['暴击率']
    cd = data['属性']['暴击伤害']
    dmg_bonus = 1 + data['属性']['伤害加成'][1] + extra['增伤']
    percent_value = float(skill_data['锅巴出击']['数值']['喷火伤害'][skill_level].replace('%', '')) / 100.0
    if len(data['命座']) >= 1:
        damage = (attack * percent_value) * (1 + cr * cd) * dmg_bonus * rc(0.1, 0.15) * dc(role_level)
    else:
        damage = (attack * percent_value) * (1 + cr * cd) * dmg_bonus * rc() * dc(role_level)
    return damage, damage / (1 + cr * cd) * (1 + cd)


def cal_q_dmg(data: dict, extra: dict) -> Tuple[float, float]:
    """
    计算香菱大招的伤害
    :param data: 角色数据
    :param extra: 针对大招的额外数值
    :return: 期望伤害和暴击后伤害
    """
    role_level = data['等级']
    skill_level = data['天赋'][2]['等级'] - 1
    attack = data['属性']['基础攻击'] + data['属性']['额外攻击']
    cr = data['属性']['暴击率'] + extra['暴击率']
    cd = data['属性']['暴击伤害']
    dmg_bonus = 1 + data['属性']['伤害加成'][1] + extra['增伤']
    percent_value = float(skill_data['旋火轮']['数值']['旋火轮伤害'][skill_level].replace('%', '')) / 100.0
    if len(data['命座']) >= 1:
        damage = (attack * percent_value) * (1 + cr * cd) * dmg_bonus * rc(0.1, 0.15) * dc(role_level)
    else:
        damage = (attack * percent_value) * (1 + cr * cd) * dmg_bonus * rc() * dc(role_level)
    return damage, damage / (1 + cr * cd) * (1 + cd)


def draw_xiangling_dmg(data: dict):
    mask_top = load_image(path=Path() / 'resources' / 'LittlePaimon' / 'player_card2' / '遮罩top.png')
    mask_body = load_image(path=Path() / 'resources' / 'LittlePaimon' / 'player_card2' / '遮罩body.png')
    mask_bottom = load_image(path=Path() / 'resources' / 'LittlePaimon' / 'player_card2' / '遮罩bottom.png')

    data = deepcopy(data)
    height = 3 * 60 - 20
    data['伤害描述'] = [] if len(data['命座']) < 1 else ['锅巴减抗']
    data = attr_common_fix(data)
    data, q_value = q_fix(data)
    data, e_value = e_fix(data)
    data, a_value = a_fix(data)
    if data['伤害描述']:
        height += 60
    # 蒸发系数
    if '蒸发系数' in data['属性']:
        zf = growth_reaction(data['属性']['元素精通'], 1.5, 0.15)
    else:
        zf = growth_reaction(data['属性']['元素精通'], 1.5)
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
    # 顶栏
    draw_center_text(bg_draw, '伤害计算', 0, 250, 11, 'white', get_font(30, text_font))
    draw_center_text(bg_draw, '期望伤害', 250, 599, 11, 'white', get_font(30, text_font))
    draw_center_text(bg_draw, '暴击伤害', 599, 948, 11, 'white', get_font(30, text_font))

    draw_center_text(bg_draw, '锅巴喷火', 0, 250, 73, 'white', get_font(30, text_font))
    expect_dmg, crit_dmg = cal_e_dmg(data, e_value)
    draw_center_text(bg_draw, str(int(expect_dmg)), 250, 599, 76, 'white', get_font(30, number_font))
    draw_center_text(bg_draw, str(int(crit_dmg)), 599, 948, 76, 'white', get_font(30, number_font))

    draw_center_text(bg_draw, '旋火轮', 0, 250, 133, 'white', get_font(30, text_font))
    expect_dmg, crit_dmg = cal_q_dmg(data, q_value)
    draw_center_text(bg_draw, str(int(expect_dmg)), 250, 599, 136, 'white', get_font(30, number_font))
    draw_center_text(bg_draw, str(int(crit_dmg)), 599, 948, 136, 'white', get_font(30, number_font))

    draw_center_text(bg_draw, '旋火轮蒸发', 0, 250, 193, 'white', get_font(30, text_font))
    draw_center_text(bg_draw, str(int(expect_dmg * zf)), 250, 599, 196, 'white', get_font(30, number_font))
    draw_center_text(bg_draw, str(int(crit_dmg * zf)), 599, 948, 196, 'white', get_font(30, number_font))

    # 额外说明
    if data['伤害描述']:
        bg_draw.line((0, 240, 948, 240), (255, 255, 255, 75), 2)
        draw_center_text(bg_draw, '额外说明', 0, 250, 253, 'white', get_font(30, text_font))
        draw_center_text(bg_draw, '，'.join(data['伤害描述']), 250, 948, 256, 'white', get_font(30, text_font))
    return bg
