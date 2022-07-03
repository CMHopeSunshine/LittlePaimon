from copy import deepcopy
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw
from littlepaimon_utils.files import load_json, load_image
from littlepaimon_utils.images import get_font, draw_center_text

from .common import resistance_coefficient as rc, defense_coefficient as dc, attr_common_fix, e_fix, a_fix, text_font, \
    number_font

skill_data = load_json(path=Path(__file__).parent.parent.parent / 'utils' / 'json_data' / 'roles_data.json')['魈']['skill']


def cal_attack_dmg(data: dict, extra: dict, type: str) -> Tuple[float, float]:
    """
    计算魈下落攻击的伤害
    :param data: 角色数据
    :param extra: 针对重击的额外数值
    :param type: 类型
    :return: 期望伤害和暴击后伤害
    """
    role_level = data['等级']
    skill_level = data['天赋'][0]['等级'] - 1
    attack = data['属性']['基础攻击'] + data['属性']['额外攻击']
    cr = data['属性']['暴击率'] + extra['下落攻击暴击率']
    cd = data['属性']['暴击伤害']
    dmg_bonus = 1 + data['属性']['伤害加成'][5] + extra['下落攻击增伤']
    percent_value = skill_data['普通攻击·卷积微尘']['数值']['低空/高空坠地冲击伤害'][skill_level].split('/')
    if type.startswith('低空下落'):
        percent_value = float(percent_value[0].replace('%', '')) / 100
    else:
        percent_value = float(percent_value[1].replace('%', '')) / 100
    if role_level >= 40:
        dmg_bonus += 0.25 if '首戳' not in type else 0
    q_skill_level = data['天赋'][2]['等级'] - 1
    q_bonus = float(skill_data['靖妖傩舞']['数值']['普通攻击/重击/下落攻击伤害提升'][q_skill_level].replace('%', '')) / 100
    dmg_bonus += q_bonus
    damage = (attack * percent_value) * (1 + cr * cd) * dmg_bonus * rc() * dc(role_level)
    return damage, damage / (1 + cr * cd) * (1 + cd)


def cal_e_dmg(data: dict, extra: dict) -> Tuple[float, float]:
    """
    计算魈元素战技的伤害
    :param data: 角色数据
    :param extra: 针对元素战技的额外数值
    :return: 期望伤害和暴击后伤害
    """
    role_level = data['等级']
    skill_level = data['天赋'][1]['等级'] - 1
    attack = data['属性']['基础攻击'] + data['属性']['额外攻击']
    cr = data['属性']['暴击率'] + extra['暴击率']
    cd = data['属性']['暴击伤害']
    dmg_bonus = 1 + data['属性']['伤害加成'][5] + extra['增伤']

    percent_value = float(skill_data['风轮两立']['数值']['技能伤害'][skill_level].replace('%', '')) / 100.0
    damage = (attack * percent_value) * (1 + cr * cd) * dmg_bonus * rc() * dc(role_level)
    return damage, damage / (1 + cr * cd) * (1 + cd)


def draw_xiao_dmg(data: dict):
    mask_top = load_image(path=Path() / 'resources' / 'LittlePaimon' / 'player_card2' / '遮罩top.png')
    mask_body = load_image(path=Path() / 'resources' / 'LittlePaimon' / 'player_card2' / '遮罩body.png')
    mask_bottom = load_image(path=Path() / 'resources' / 'LittlePaimon' / 'player_card2' / '遮罩bottom.png')

    data = deepcopy(data)
    height = 3 * 60 - 20
    if '伤害描述' in data and data['伤害描述']:
        height += 60
    data = attr_common_fix(data)
    data, e_value = e_fix(data)
    data, a_value = a_fix(data)

    bg = Image.new('RGBA', (948, height + 80), (0, 0, 0, 0))
    bg.alpha_composite(mask_top, (0, 0))
    bg.alpha_composite(mask_body.resize((948, height)), (0, 60))
    bg.alpha_composite(mask_bottom, (0, height + 60))
    bg_draw = ImageDraw.Draw(bg)
    # 画线
    bg_draw.line((250, 0, 250, 948), (255, 255, 255, 75), 2)
    bg_draw.line((599, 0, 599, 300), (255, 255, 255, 75), 2)
    bg_draw.line((0, 60, 948, 60), (255, 255, 255, 75), 2)
    bg_draw.line((0, 120, 948, 120), (255, 255, 255, 75), 2)
    bg_draw.line((0, 180, 948, 180), (255, 255, 255, 75), 2)
    # 顶栏
    draw_center_text(bg_draw, '伤害计算', 0, 250, 11, 'white', get_font(30, text_font))
    draw_center_text(bg_draw, '期望伤害', 250, 599, 11, 'white', get_font(30, text_font))
    draw_center_text(bg_draw, '暴击伤害', 599, 948, 11, 'white', get_font(30, text_font))

    # e
    draw_center_text(bg_draw, '风轮两立', 0, 250, 73, 'white', get_font(30, text_font))
    expect_dmg, crit_dmg = cal_e_dmg(data, e_value)
    draw_center_text(bg_draw, str(int(expect_dmg)), 250, 599, 76, 'white', get_font(30, number_font))
    draw_center_text(bg_draw, str(int(crit_dmg)), 599, 948, 76, 'white', get_font(30, number_font))

    # 重击蒸发
    draw_center_text(bg_draw, '低空下落首戳', 0, 250, 133, 'white', get_font(30, text_font))
    expect_dmg, crit_dmg = cal_attack_dmg(data, a_value, '低空下落首戳')
    draw_center_text(bg_draw, str(int(expect_dmg)), 250, 599, 136, 'white', get_font(30, number_font))
    draw_center_text(bg_draw, str(int(crit_dmg)), 599, 948, 136, 'white', get_font(30, number_font))

    # 大招蒸发
    draw_center_text(bg_draw, '高空下落首戳', 0, 250, 193, 'white', get_font(30, text_font))
    expect_dmg, crit_dmg = cal_attack_dmg(data, a_value, '高空下落首戳')
    draw_center_text(bg_draw, str(int(expect_dmg)), 250, 599, 196, 'white', get_font(30, number_font))
    draw_center_text(bg_draw, str(int(crit_dmg)), 599, 948, 196, 'white', get_font(30, number_font))

    # 额外说明
    if data['伤害描述']:
        bg_draw.line((0, 240, 948, 240), (255, 255, 255, 75), 2)
        draw_center_text(bg_draw, '额外说明', 0, 250, 256, 'white', get_font(30, text_font))
        draw_center_text(bg_draw, '，'.join(data['伤害描述']), 250, 948, 256, 'white', get_font(30, text_font))
    return bg
