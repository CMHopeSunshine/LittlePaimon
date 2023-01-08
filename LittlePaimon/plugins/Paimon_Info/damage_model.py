import random
from typing import Tuple, Dict, Optional, List, Union

from LittlePaimon.utils.path import JSON_DATA
from LittlePaimon.utils.files import load_json
from LittlePaimon.utils.genshin import GenshinTools
from LittlePaimon.utils.image import PMImage, font_manager
from LittlePaimon.database import Character


def udc(dm: float,
        crit: Tuple[float, float],
        db: float,
        sl: int,
        rcb: Optional[float] = 0.1,
        rcd: Optional[float] = 0,
        el: Optional[int] = 90,
        dcr: Optional[float] = 0,
        dci: Optional[float] = 0,
        r: Optional[float] = 1,
        ) -> List[str]:
    """
    计算伤害
    :param dm: 倍率区
    :param crit: 暴击区
    :param db: 增伤区
    :param sl: 角色等级
    :param rcb: 怪物基础抗性
    :param rcd: 抗性减少
    :param el: 怪物等级
    :param dcr: 抗性系数减少
    :param dci: 无视防御系数
    :param r: 反应最终系数
    :return: 伤害
    """
    if crit[0] > 1:
        damage = dm * (1 + crit[1]) * (1 + db) * resistance_coefficient(rcb, rcd) * defense_coefficient(sl, el, dcr,
                                                                                                        dci) * r
        return [str(int(damage)), str(int(damage))]
    elif crit[0] <= 0:
        damage = dm * (1 + db) * resistance_coefficient(rcb, rcd) * defense_coefficient(sl, el, dcr, dci) * r
        return [str(int(damage)), ]
    else:
        damage = dm * (1 + crit[0] * crit[1]) * (1 + db) * resistance_coefficient(rcb, rcd) * defense_coefficient(sl,
                                                                                                                  el,
                                                                                                                  dcr,
                                                                                                                  dci) * r
        return [str(int(damage)), str(int(damage / (1 + crit[0] * crit[1]) * (1 + crit[1])))]


def resistance_coefficient(base_resistance: float = 0.1, reduction_rate: float = 0):
    """
    计算抗性系数
    :param base_resistance: 怪物基础抗性
    :param reduction_rate: 减抗系数
    :return: 抗性系数
    """
    resistance = base_resistance - reduction_rate
    if resistance > 0.75:
        return 1 / (1 + 4 * resistance)
    elif 0 <= resistance < 0.75:
        return 1 - resistance
    else:
        return 1 - (resistance / 2)


def defense_coefficient(self_level: int = 90, enemy_level: int = -1, reduction_rate: float = 0, ignore: float = 0):
    """
    计算防御力系数
    :param self_level: 角色自身等级
    :param enemy_level: 怪物等级
    :param reduction_rate: 减防系数
    :param ignore: 无视防御系数
    :return: 防御力系数
    """
    if enemy_level == -1:
        enemy_level = self_level
    return (self_level + 100) / ((self_level + 100) + (enemy_level + 100) * (1 - reduction_rate) * (1 - ignore))


def growth_reaction(mastery: int = 0, base_coefficient: float = 1.5, extra_coefficient: float = 0):
    """
    计算增幅反应的系数
    :param mastery: 元素精通
    :param base_coefficient: 基础系数，如蒸发为1.5， 融化为2
    :param extra_coefficient: 反应系数提高，如魔女4件套效果
    :return: 增幅系数
    """
    mastery_increase = (2.78 * mastery) / (mastery + 1400)
    return base_coefficient * (1 + mastery_increase + extra_coefficient)


upheaval_value = load_json(JSON_DATA / 'upheaval.json')


def upheaval_reaction(level: int, type: str, mastery: int = 0, extra_coefficient: float = 0, resistance: float = 0.9):
    """
    计算剧变反应的伤害
    :param level: 等级
    :param type: 反应类型
    :param mastery: 元素精通
    :param extra_coefficient: 反应系数提高，如如雷4件套效果
    :param resistance: 怪物抗性系数
    :return: 剧变伤害
    """
    if type == '超导':
        base_ratio = 1
    elif type == '扩散':
        base_ratio = 1.2
    elif type == '碎冰':
        base_ratio = 3
    elif type == '超载':
        base_ratio = 4
    else:
        base_ratio = 4.8
    base_coefficient = upheaval_value[level - 1]
    mastery_increase = (16 * mastery) / (mastery + 2000)
    return base_coefficient * base_ratio * (1 + mastery_increase + extra_coefficient) * resistance


def intensify_reaction(level: int, type: str, mastery: int = 0, extra_coefficient: float = 0):
    """
    计算激化反应的伤害
    :param level: 等级
    :param type: 反应类型
    :param mastery: 元素精通
    :param extra_coefficient: 反应系数提高，如如雷4件套效果
    :return: 激化伤害
    """
    r = 2.3 if type == '超激化' else 2.5
    base_coefficient = upheaval_value[level - 1]
    return r * base_coefficient * (1 + (mastery * 5) / (mastery + 1200)) * (1 + extra_coefficient)


def weapon_common_fix(info: Character):
    """
    对武器的通用面板属性修正
    :param info: 角色数据
    :return: 角色数据
    """
    # 针对q的额外属性
    extra_q = {
        '暴击率': 0,
        '增伤':  0,
        '减抗': 0
    }
    # 针对e的额外属性
    extra_e = {
        '暴击率':  0,
        '增伤':   0,
        '额外倍率': 0,
        '减抗': 0
    }
    # 针对a的额外属性
    extra_a = {
        '普攻暴击率':    0,
        '普攻增伤':     0,
        '普攻额外倍率':   0,
        '重击暴击率':    0,
        '重击增伤':     0,
        '重击额外倍率':   0,
        '下落攻击暴击率':  0,
        '下落攻击增伤':   0,
        '下落攻击额外倍率': 0,
        '减抗': 0
    }
    # 单手剑
    if info.weapon.name == '波乱月白经津':
        # for i in info.prop.dmg_bonus:
        #     info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + (0.09 + 0.03 * info.weapon.affix_level)
        extra_a['普攻增伤'] += 2 * (0.15 + 0.05 * info.weapon.affix_level)
        info.damage_describe.append('波乱满层')
    elif info.weapon.name == '辰砂之纺锤':
        extra_e['额外倍率'] += info.prop.defense * (0.3 + 0.1 * info.weapon.affix_level)
    elif info.weapon.name == '腐殖之剑':
        extra_e['增伤'] += 0.12 + 0.04 * info.weapon.affix_level
        extra_e['暴击率'] += 0.045 + 0.015 * info.weapon.affix_level
    elif info.weapon.name == '苍古自由之誓':
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + (0.075 + 0.025 * info.weapon.affix_level)
        info.prop.extra_attack += info.prop.base_attack * (0.15 + 0.05 * info.weapon.affix_level)
        extra_a['普攻增伤'] += 0.12 + 0.04 * info.weapon.affix_level
        extra_a['重击增伤'] += 0.12 + 0.04 * info.weapon.affix_level
        extra_a['下落攻击增伤'] += 0.12 + 0.04 * info.weapon.affix_level
        info.damage_describe.append('苍古触发')
    elif info.weapon.name == '雾切之回光':
        # TODO 吃不满3层的角色
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + (0.21 + 0.07 * info.weapon.affix_level)
        info.damage_describe.append('雾切满层')
    elif info.weapon.name == '铁蜂刺':
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + 2 * (0.045 + 0.015 * info.weapon.affix_level)
        info.damage_describe.append('铁蜂刺满层')
    elif info.weapon.name == '黑岩长剑':
        info.prop.extra_attack += info.prop.base_attack * (0.09 + 0.03 * info.weapon.affix_level)
        info.damage_describe.append('黑岩1层')
    elif info.weapon.name in ['暗巷闪光', '冷刃']:
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + (0.09 + 0.03 * info.weapon.affix_level)
    elif info.weapon.name == '飞天大御剑':
        info.prop.extra_attack += info.prop.base_attack * (0.09 + 0.03 * info.weapon.affix_level)
    elif info.weapon.name == '黎明神剑':
        info.prop.crit_rate += 0.115 + 0.025 * info.weapon.affix_level
    elif info.weapon.name == '暗铁剑':
        info.prop.extra_attack += info.prop.base_attack * (0.15 + 0.05 * info.weapon.affix_level)
    elif info.weapon.name == '黑剑':
        extra_a['普攻增伤'] += 0.15 + 0.05 * info.weapon.affix_level
        extra_a['重击增伤'] += 0.15 + 0.05 * info.weapon.affix_level
    elif info.weapon.name == '铁影阔剑':
        extra_a['重击增伤'] += 0.25 + 0.05 * info.weapon.affix_level
    elif info.weapon.name == '西福斯的月光':
        info.prop.elemental_efficiency += info.prop.elemental_mastery * (0.00027 + 0.00009 * info.weapon.affix_level)
    elif info.weapon.name == '圣显之钥':
        info.prop.elemental_mastery += info.prop.health * (0.0009 + 0.0003 * info.weapon.affix_level) * 3
        info.damage_describe.append('圣显之钥满层')

    # 双手剑
    elif info.weapon.name == '赤角石溃杵':
        extra_a['普攻额外倍率'] += info.prop.defense * (0.3 + 0.1 * info.weapon.affix_level)
    elif info.weapon.name == '松籁响起之时':
        info.prop.extra_attack += info.prop.base_attack * (0.09 + 0.03 * info.weapon.affix_level)
        info.damage_describe.append('松籁触发')
    elif info.weapon.name == '狼的末路':
        info.prop.extra_attack += info.prop.base_attack * (0.3 + 0.1 * info.weapon.affix_level)
        info.damage_describe.append('狼末触发')
    elif info.weapon.name == '天空之傲':
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + (0.06 + 0.02 * info.weapon.affix_level)
    elif info.weapon.name == '钟剑':
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + (0.09 + 0.03 * info.weapon.affix_level)
        info.damage_describe.append('钟剑触发')
    elif info.weapon.name == '白影剑':
        info.prop.extra_attack += info.prop.base_attack * 4 * (0.045 + 0.015 * info.weapon.affix_level)
        info.prop.base_defense += info.prop.base_defense * 4 * (0.045 + 0.015 * info.weapon.affix_level)
        info.damage_describe.append('白影剑满层')
    elif info.weapon.name == '螭骨剑':
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + 5 * (0.05 + 0.01 * info.weapon.affix_level)
        info.damage_describe.append('螭骨满层')
    elif info.weapon.name in ['沐浴龙血的剑', '鸦羽弓', '魔导绪论']:
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + (0.09 + 0.03 * info.weapon.affix_level)
    elif info.weapon.name == '飞天大御剑':
        info.prop.extra_attack += info.prop.base_attack * 4 * (0.05 + 0.01 * info.weapon.affix_level)
        info.damage_describe.append('白影剑满层')
    elif info.weapon.name == '衔珠海皇':
        extra_q['增伤'] += 0.09 + 0.03 * info.weapon.affix_level
    elif info.weapon.name == '桂木斩长正':
        extra_e['增伤'] += 0.045 + 0.015 * info.weapon.affix_level
    elif info.weapon.name == '玛海菈的水色':
        info.prop.extra_attack += info.prop.elemental_mastery * (0.18 + 0.06 * info.weapon.affix_level)

    # 弓
    elif info.weapon.name == '落霞':
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + (0.115 + 0.025 * info.weapon.affix_level)
        info.damage_describe.append('落霞最高层')
    elif info.weapon.name == '若水':
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + (0.15 + 0.05 * info.weapon.affix_level)
    elif info.weapon.name == '终末嗟叹之诗':
        info.prop.extra_attack += info.prop.base_attack * (0.15 + 0.05 * info.weapon.affix_level)
        info.prop.elemental_mastery += 75 + 25 * info.weapon.affix_level
        info.damage_describe.append('终末触发')
    elif info.weapon.name == '冬极白星':
        info.prop.extra_attack += info.prop.base_attack * (0.36 + 0.12 * info.weapon.affix_level)
        extra_q['增伤'] += 0.09 + 0.03 * info.weapon.affix_level
        extra_e['增伤'] += 0.09 + 0.03 * info.weapon.affix_level
        info.damage_describe.append('冬极满层')
    elif info.weapon.name == '试作澹月':
        info.prop.extra_attack += info.prop.base_attack * (0.27 + 0.09 * info.weapon.affix_level)
        info.damage_describe.append('试作触发')
    elif info.weapon.name == '钢轮弓':
        info.prop.extra_attack += info.prop.base_attack * 4 * (0.03 + 0.01 * info.weapon.affix_level)
        info.damage_describe.append('钢轮弓满层')
    elif info.weapon.name == '暗巷猎手':
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + 5 * (0.015 + 0.005 * info.weapon.affix_level)
        info.damage_describe.append('暗巷猎手5层')
    elif info.weapon.name == '风花之颂':
        info.prop.extra_attack += info.prop.base_attack * (0.12 + 0.04 * info.weapon.affix_level)
        info.damage_describe.append('风花触发')
    elif info.weapon.name == '绝弦':
        extra_q['增伤'] += 0.18 + 0.06 * info.weapon.affix_level
        extra_e['增伤'] += 0.18 + 0.06 * info.weapon.affix_level
    elif info.weapon.name == '幽夜华尔兹':
        extra_e['增伤'] += 0.15 + 0.05 * info.weapon.affix_level
        extra_a['普攻增伤'] += 0.15 + 0.05 * info.weapon.affix_level
    elif info.weapon.name == '掠食者':
        extra_a['普攻增伤'] += 0.1
        extra_a['重击增伤'] += 0.1
    elif info.weapon.name == '飞雷之弦振':
        extra_a['普攻增伤'] += 0.3 + 0.1 * info.weapon.affix_level
        info.damage_describe.append('飞雷满层')
    elif info.weapon.name == '破魔之弓':
        extra_a['普攻增伤'] += 0.24 + 0.08 * info.weapon.affix_level
        extra_a['重击增伤'] += 0.18 + 0.06 * info.weapon.affix_level
        info.damage_describe.append('破魔满能量')
    elif info.weapon.name == '阿莫斯之弓':
        extra_a['普攻增伤'] += 0.39 + 0.13 * info.weapon.affix_level
        extra_a['重击增伤'] += 0.39 + 0.13 * info.weapon.affix_level
        info.damage_describe.append('阿莫斯满层')
    elif info.weapon.name == '弓藏':
        extra_a['普攻增伤'] += 0.3 + 0.1 * info.weapon.affix_level
        extra_a['重击增伤'] -= 0.1
    elif info.weapon.name == '弹弓':
        extra_a['普攻增伤'] += 0.3 + 0.06 * info.weapon.affix_level
        extra_a['重击增伤'] += 0.3 + 0.06 * info.weapon.affix_level
    elif info.weapon.name == '猎人之径':
        extra_a['重击额外倍率'] += info.prop.elemental_mastery * (1.2 + 0.4 * info.weapon.affix_level)
        info.damage_describe.append('猎人弓触发')
    elif info.weapon.name == '王下近侍':
        info.prop.elemental_mastery += 40 + 20 * info.weapon.affix_level
        info.damage_describe.append('王下近侍触发')

    # 长柄武器
    elif info.weapon.name == '白缨枪':
        extra_a['普攻增伤'] += 0.18 + 0.06 * info.weapon.affix_level
    elif info.weapon.name == '护摩之杖':
        info.prop.extra_attack += info.prop.health * (0.008 + 0.002 * info.weapon.affix_level)
        if '半血以下' not in info.damage_describe:
            info.damage_describe.append('半血以下')
    elif info.weapon.name == '和璞鸢':
        info.prop.extra_attack += info.prop.base_attack * 7 * (0.025 + 0.007 * info.weapon.affix_level)
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + (0.09 + 0.03 * info.weapon.affix_level)
        info.damage_describe.append('和璞鸢满层')
    elif info.weapon.name == '决斗之枪':
        info.prop.extra_attack += info.prop.base_attack * 0.18 + 0.06 * info.weapon.affix_level
        info.damage_describe.append('决斗单怪')
    elif info.weapon.name == '息灾':
        # for i in info.prop.dmg_bonus:
        #     info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + (0.09 + 0.03 * info.weapon.affix_level)
        info.prop.extra_attack += info.prop.base_attack * 6 * (0.024 + 0.006 * info.weapon.affix_level)
        info.damage_describe.append('息灾前台满层')
    elif info.weapon.name == '薙草之稻光':
        # info.prop.extra_attack += info.prop.base_attack * (info.prop.elemental_efficiency - 1) * (
        #             0.21 + 0.07 * info.weapon.affix_level)
        info.prop.elemental_efficiency += 0.25 + 0.05 * info.weapon.affix_level
    elif info.weapon.name == '「渔获」':
        extra_q['增伤'] += 0.12 + 0.04 * info.weapon.affix_level
        extra_q['暴击率'] += 0.045 + 0.015 * info.weapon.affix_level
    elif info.weapon.name == '风信之锋':
        info.prop.extra_attack += info.prop.base_attack * (0.09 + 0.03 * info.weapon.affix_level)
        info.prop.elemental_mastery += 36 + 12 * info.weapon.affix_level
        info.damage_describe.append('风信之锋触发')
    elif info.weapon.name == '赤沙之杖':
        info.prop.extra_attack += info.prop.elemental_mastery * (1.02 + 0.34 * info.weapon.affix_level)
        info.damage_describe.append('赤沙之杖满层')

    # 法器
    elif info.weapon.name == '证誓之明瞳':
        info.prop.elemental_efficiency += 0.18 + 0.06 * info.weapon.affix_level
    elif info.weapon.name == '神乐之真意':
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + (0.09 + 0.03 * info.weapon.affix_level)
        extra_e['增伤'] += 3 * (0.09 + 0.03 * info.weapon.affix_level)
        info.damage_describe.append('神乐满层')
    elif info.weapon.name == '不灭月华':
        # info.prop.healing_bonus += 0.075 + 0.025 * info.weapon.affix_level
        extra_a['普攻额外倍率'] += (0.005 + 0.005 * info.weapon.affix_level) * info.prop.health
    elif info.weapon.name == '白辰之环':
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + (0.075 + 0.025 * info.weapon.affix_level)
        info.damage_describe.append('白辰触发')
    # elif info.weapon.name == '天空之卷':
    #     for i in info.prop.dmg_bonus:
    #         info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + (0.09 + 0.03 * info.weapon.affix_level)
    elif info.weapon.name == '四风原典':
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + 4 * (0.06 + 0.02 * info.weapon.affix_level)
        info.damage_describe.append('四风满层')
    elif info.weapon.name == '流浪乐章':
        t = random.randint(1, 3)
        if t == 1:
            info.prop.extra_attack += (0.45 + 0.15 * info.weapon.affix_level) * info.prop.base_attack
            info.damage_describe.append('流浪触发加攻')
        elif t == 2:
            for i in info.prop.dmg_bonus:
                info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + (0.36 + 0.12 * info.weapon.affix_level)
            info.damage_describe.append('流浪触发增伤')
        else:
            info.prop.elemental_mastery += 180 + 60 * info.weapon.affix_level
            info.damage_describe.append('流浪触发加精通')
    elif info.weapon.name == '万国诸海图谱':
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + 2 * (0.06 + 0.02 * info.weapon.affix_level)
        info.damage_describe.append('万国满层')
    elif info.weapon.name == '暗巷的酒与诗':
        info.prop.extra_attack += info.prop.base_attack * (0.15 + 0.05 * info.weapon.affix_level)
        info.damage_describe.append('暗巷触发')
    elif info.weapon.name == '嘟嘟可故事集':
        info.prop.extra_attack += info.prop.base_attack * (0.06 + 0.02 * info.weapon.affix_level)
        extra_a['重击增伤'] += 0.12 + 0.04 * info.weapon.affix_level
    elif info.weapon.name == '翡玉法球':
        info.prop.extra_attack += info.prop.base_attack * (0.15 + 0.05 * info.weapon.affix_level)
        info.damage_describe.append('翡玉触发')
    elif info.weapon.name == '匣里日月':
        extra_q['增伤'] += 0.15 + 0.05 * info.weapon.affix_level
        extra_e['增伤'] += 0.15 + 0.05 * info.weapon.affix_level
        extra_a['普攻增伤'] += 0.15 + 0.05 * info.weapon.affix_level
    elif info.weapon.name == '盈满之实':
        info.prop.elemental_mastery += 5 * (21 + 3 * info.weapon.affix_level)
        info.prop.extra_attack -= 5 * 0.05 * info.prop.base_attack
        info.damage_describe.append('盈满之实满层')
    elif info.weapon.name == '千夜浮梦':
        info.prop.elemental_mastery += 5 * (24 + 8 * info.weapon.affix_level)
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + 2 * (0.06 + 0.04 * info.weapon.affix_level)
        info.damage_describe.append('武器算1同2异')
    elif info.weapon.name == '流浪的晚星':
        info.prop.extra_attack += info.prop.elemental_mastery * (0.18 + 0.06 * info.weapon.affix_level)
    elif info.weapon.name == '魔导绪论':
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + 0.09 + 0.03 * info.weapon.affix_level

    # 系列武器
    elif info.weapon.name.startswith('千岩'):
        info.prop.crit_rate += (0.02 + 0.01 * info.weapon.affix_level)
        info.prop.extra_attack += info.prop.base_attack * (0.06 + 0.01 * info.weapon.affix_level)
        info.damage_describe.append('璃月人1层')
    elif info.weapon.name in ['匣里灭辰', '匣里龙吟', '雨裁']:
        for i in info.prop.dmg_bonus:
            info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + (0.16 + 0.04 * info.weapon.affix_level)
        info.damage_describe.append(f'{info.weapon.name[:2]}触发')
    elif info.weapon.name.startswith('黑岩'):
        info.prop.extra_attack += info.prop.base_attack * (0.09 + 0.03 * info.weapon.affix_level)
        info.damage_describe.append('黑岩1层')
    elif info.weapon.name in ['贯虹之槊', '斫峰之刃', '尘世之锁', '无工之剑']:
        info.prop.extra_attack += info.prop.base_attack * 2 * 5 * (0.003 + 0.001 * info.weapon.affix_level)
        info.prop.shield_strength += 0.15 + 0.05 * info.weapon.affix_level
        info.damage_describe.append('武器带盾满层')
    elif info.weapon.name in ['断浪长鳍', '恶王丸', '朦云之月']:
        extra_q['增伤'] += (0.0009 + 0.0003 * info.weapon.affix_level) * 240
        info.damage_describe.append('武器被动算240能量')

    return extra_q, extra_e, extra_a


def common_fix(info: Character) -> Tuple[Character, dict, dict, dict]:
    """
    对武器、圣遗物的通用面板属性修正
    :param info: 角色数据
    :return: 角色数据
    """
    info.damage_describe = []
    extra_q, extra_e, extra_a = weapon_common_fix(info)
    suit = GenshinTools.get_artifact_suit(info.artifacts)
    # 两件套的情况
    if '逆飞的流星' in suit:
        info.prop.shield_strength += 0.35
    if '昔日宗室之仪' in suit:
        extra_q['增伤'] += 0.2
    if '赌徒' in suit:
        extra_e['增伤'] += 0.2
    if '武人' in suit:
        extra_a['普攻增伤'] += 0.15
        extra_a['重击增伤'] += 0.15
    if len(suit) == 2 and suit[0][0] == suit[1][0]:
        if suit[0][0] == '绝缘之旗印':
            extra_q['增伤'] += 0.25 * info.prop.elemental_efficiency
        if suit[0][0] == '苍白之火':
            info.prop.extra_attack += info.prop.base_attack * 0.18
            info.prop.dmg_bonus['物理'] += 0.25
            info.damage_describe.append('苍白满层')
        elif suit[0][0] == '华馆梦醒形骸记':
            info.prop.dmg_bonus['岩'] += 0.24
            info.prop.base_defense += info.prop.base_defense * 0.24
            info.damage_describe.append('华馆满层')
        elif suit[0][0] == '千岩牢固':
            info.prop.shield_strength += 0.3
            info.prop.extra_attack += info.prop.base_attack * 0.2
            info.damage_describe.append('千岩触发')
        elif suit[0][0] == '昔日宗室之仪':
            info.prop.extra_attack += info.prop.base_attack * 0.2
            info.damage_describe.append('宗室触发')
        elif suit[0][0] == '冰风迷途的勇士':
            info.prop.crit_rate += 0.2
            info.damage_describe.append('冰套暴击算20%')
        elif suit[0][0] == '勇士之心':
            for i in info.prop.dmg_bonus:
                info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + 0.3
            info.damage_describe.append('勇士触发')
        elif suit[0][0] == '教官':
            info.prop.elemental_mastery += 120
            info.damage_describe.append('教官触发')
        elif suit[0][0] == '炽烈的炎之魔女':
            if info.name in ['胡桃', '宵宫']:
                info.prop.dmg_bonus['火'] += 0.075
                info.damage_describe.append('魔女1层')
            else:
                info.prop.dmg_bonus['火'] += 0.225
                info.damage_describe.append('魔女满层')
            info.prop.reaction_coefficient['蒸发'] += 0.15
            info.prop.reaction_coefficient['融化'] += 0.15
            info.prop.reaction_coefficient['超载'] += 0.4
            info.prop.reaction_coefficient['燃烧'] += 0.4
            info.prop.reaction_coefficient['绽放'] += 0.4
        elif suit[0][0] == '如雷的盛怒':
            info.prop.reaction_coefficient['超载'] += 0.4
            info.prop.reaction_coefficient['感电'] += 0.4
            info.prop.reaction_coefficient['超导'] += 0.4
            info.prop.reaction_coefficient['绽放'] += 0.4
            info.prop.reaction_coefficient['激化'] += 0.2
        elif suit[0][0] == '翠绿之影':
            info.prop.reaction_coefficient['扩散'] += 0.6
        elif suit[0][0] == '渡过烈火的贤人':
            for i in info.prop.dmg_bonus:
                info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + 0.5
            info.damage_describe.append('渡火触发')
        elif suit[0][0] == '平息鸣雷的尊者':
            for i in info.prop.dmg_bonus:
                info.prop.dmg_bonus[i] = info.prop.dmg_bonus[i] + 0.5
            info.damage_describe.append('平雷触发')
        elif suit[0][0] == '战狂':
            info.prop.crit_rate += 0.24
            info.damage_describe.append('战狂触发')
        elif suit[0][0] == '辰砂往生录':
            info.prop.extra_attack += info.prop.base_attack * 0.48
            info.damage_describe.append('辰砂满层')
        elif suit[0][0] == '被怜爱的少女':
            info.prop.incoming_healing_bonus += 0.2
        elif suit[0][0] == '追忆之注连':
            extra_a['普攻增伤'] += 0.5
            extra_a['重击增伤'] += 0.5
            extra_a['下落攻击增伤'] += 0.5
            info.damage_describe.append('追忆触发')
        elif suit[0][0] == '流浪大地的乐团':
            if info.weapon.type in ['法器', '弓箭']:
                extra_a['重击增伤'] += 0.35
        elif suit[0][0] == '角斗士的终幕礼':
            if info.weapon.type in ['单手剑', '双手剑', '长柄武器']:
                extra_a['普攻增伤'] += 0.35
        elif suit[0][0] == '染血的骑士道':
            extra_a['重击增伤'] += 0.5
            info.damage_describe.append('染血触发')
        elif suit[0][0] == '沉沦之心':
            extra_a['普攻增伤'] += 0.3
            extra_a['重击增伤'] += 0.3
            info.damage_describe.append('沉沦触发')
        elif suit[0][0] == '逆飞的流星':
            extra_a['普攻增伤'] += 0.4
            extra_a['重击增伤'] += 0.4
            info.damage_describe.append('流星触发')
        elif suit[0][0] == '武人':
            extra_a['普攻增伤'] += 0.25
            extra_a['重击增伤'] += 0.25
            info.damage_describe.append('武人触发')
        elif suit[0][0] == '行者之心':
            extra_a['重击暴击率'] += 0.3
        elif suit[0][0] == '饰金之梦':
            info.prop.elemental_mastery += 3 * 50
            info.prop.extra_attack += 0.14 * info.prop.base_attack
            info.damage_describe.append('饰金之梦触发3不同元素')
        elif suit[0][0] == '深林的记忆':
            extra_a['减抗'] += 0.3
            extra_e['减抗'] += 0.3
            extra_q['减抗'] += 0.3
            info.damage_describe.append('草套减抗')
    return info, extra_q, extra_e, extra_a


all_skill_data = load_json(JSON_DATA / 'roles_data.json')


def get_damage_multipiler(info: Character) -> Optional[Dict[str, any]]:
    """
    获取伤害计算倍率
    :param info: 角色数据
    """
    if info.name not in all_skill_data:
        return None
    skill_data = all_skill_data[info.name]['skill']
    level_q = info.talents[3].level - 1 if info.name in ['神里绫华', '莫娜'] else info.talents[2].level - 1
    level_e = info.talents[1].level - 1
    level_a = info.talents[0].level - 1
    dm = {}
    if info.name == '钟离':
        return {
            '玉璋护盾': (float(skill_data['元素战技·地心']['数值']['护盾附加吸收量'][level_e].replace('%最大生命值', '')) / 100.0,
                     int(skill_data['元素战技·地心']['数值']['护盾基础吸收量'][level_e].replace(',', ''))),
            '原岩共鸣': float(skill_data['元素战技·地心']['数值']['岩脊伤害/共鸣伤害'][level_e].split('/')[1].replace('%', '')) / 100.0,
            '天星':   float(skill_data['元素爆发·天星']['数值']['技能伤害'][level_q].replace('%', '')) / 100.0,
            '踢枪':   float(skill_data['普通攻击·岩雨']['数值']['五段伤害'][level_a].replace('%×4', '')) / 100.0
        }
    if info.name == '胡桃':
        dm = {'B:l70-增伤-*': (0.33, '半血以下',)}
        dm['B:l1-攻击力'] = (float(skill_data['蝶引来生']['数值']['攻击力提高'][level_e].replace('%生命值上限', '')) / 100.0 * (
            info.prop.health), '开E后')
        dm['AZ-e火:裸重击'] = float(skill_data['普通攻击·往生秘传枪法']['数值']['重击伤害'][level_a].replace('%', '')) / 100.0
        dm['AZ-e火-r蒸发1.5:重击蒸发'] = float(skill_data['普通攻击·往生秘传枪法']['数值']['重击伤害'][level_a].replace('%', '')) / 100.0
        dm['E-e火-r蒸发1.5:雪梅香蒸发'] = float(skill_data['蝶引来生']['数值']['血梅香伤害'][level_e].replace('%', '')) / 100.0
        dm['Q-e火-r蒸发1.5:大招蒸发'] = float(skill_data['安神秘法']['数值']['低血量时技能伤害'][level_q].replace('%', '')) / 100.0
        return dm
    if info.name == '雷电将军':
        qa = skill_data['奥义·梦想真说']['数值']['重击伤害'][level_q].split('+')
        return {
            '协同攻击':     float(skill_data['神变·恶曜开眼']['数值']['协同攻击伤害'][level_e].replace('%', '')) / 100.0,
            'e增伤':      float(
                skill_data['神变·恶曜开眼']['数值']['元素爆发伤害提高'][level_e].replace('每点元素能量', '').replace('%', '')) / 100.0 * 90,
            '梦想一刀基础':   float(skill_data['奥义·梦想真说']['数值']['梦想一刀基础伤害'][level_q].replace('%', '')) / 100.0,
            '梦想一刀愿力':   float(
                skill_data['奥义·梦想真说']['数值']['愿力加成'][level_q].split('%/')[0].replace('每层', '')) / 100.0 * 60,
            '梦想一心重击基础': (float(qa[0].replace('%', '')) / 100.0, float(qa[1].replace('%', '')) / 100.0),
            '梦想一心愿力':   float(
                skill_data['奥义·梦想真说']['数值']['愿力加成'][level_q].split('%/')[1].replace('%攻击力', '')) / 100.0 * 60,
            '梦想一心能量':   float(skill_data['奥义·梦想真说']['数值']['梦想一心能量恢复'][level_q])
        }
    if info.name == '魈':
        a = skill_data['普通攻击·卷积微尘']['数值']['低空/高空坠地冲击伤害'][level_a].split('/')
        return {
            'B:l1-增伤-AX':   (float(skill_data['靖妖傩舞']['数值']['普通攻击/重击/下落攻击伤害提升'][level_q].replace('%', '')) / 100,),
            'E-e风:风轮两立':    float(skill_data['风轮两立']['数值']['技能伤害'][level_e].replace('%', '')) / 100.0,
            'AX-e风:低空下落首戳': float(a[0].replace('%', '')) / 100,
            'AX-e风:高空下落首戳': float(a[1].replace('%', '')) / 100,
        }
    if info.name == '香菱':
        return {
            'B:c1-减抗-*':         (0.15, '锅巴减抗'),
            'E-e火:锅巴喷火':         float(skill_data['锅巴出击']['数值']['喷火伤害'][level_e].replace('%', '')) / 100.0,
            'Q-e火:旋火轮':          float(skill_data['旋火轮']['数值']['旋火轮伤害'][level_q].replace('%', '')) / 100.0,
            'Q-e火-r蒸发1.5:旋火轮蒸发': float(skill_data['旋火轮']['数值']['旋火轮伤害'][level_q].replace('%', '')) / 100.0
        }
    if info.name == '申鹤':
        return {
            '冰翎':   float(skill_data['仰灵威召将役咒']['数值']['伤害值提升'][level_e].replace('%', '')) / 100.0,
            '大招减抗': float(skill_data['神女遣灵真诀']['数值']['抗性降低'][level_q].replace('%', '')) / 100.0,
            'e长按':  float(skill_data['仰灵威召将役咒']['数值']['长按技能伤害'][level_e].replace('%', '')) / 100.0,
            '大招持续': float(skill_data['神女遣灵真诀']['数值']['持续伤害'][level_q].replace('%', '')) / 100.0
        }
    if info.name == '刻晴':
        az = skill_data['普通攻击·云来剑法']['数值']['重击伤害'][level_a].split('+')
        return {
            'B:l70-暴击率-*': (0.15,),
            'B:c6-增伤-*':   (0.24, '六命满层'),
            'B:c4-攻击力':    (info.prop.base_attack * 0.25, '四命触发'),
            'AZ-e雷:重击':    (float(az[0].replace('%', '')) / 100.0, float(az[1].replace('%', '')) / 100.0),
            'AZ-e雷-j超激化:重击超激化': (float(az[0].replace('%', '')) / 100.0, float(az[1].replace('%', '')) / 100.0),
            'E-e雷:战技斩击':   float(skill_data['星斗归位']['数值']['斩击伤害'][level_e].replace('%', '')) / 100.0,
            'E-e雷-j超激化:战技斩击超激化': float(skill_data['星斗归位']['数值']['斩击伤害'][level_e].replace('%', '')) / 100.0,
            'Q-e雷:大招尾刀':   float(skill_data['天街巡游']['数值']['最后一击伤害'][level_q].replace('%', '')) / 100.0,
            'Q-e雷-j超激化:大招尾刀超激化': float(skill_data['天街巡游']['数值']['最后一击伤害'][level_q].replace('%', '')) / 100.0
        }
    if info.name == '可莉':
        return {
            'B:l50-增伤-AZ': (0.5, '砰砰礼物触发'),
            'B:c2-减防-*':   (0.23, '二命减防'),
            'B:c6-增伤-*':   (0.1,),
            'AZ-e火:重击':    float(skill_data['普通攻击·砰砰']['数值']['重击伤害'][level_a].replace('%', '')) / 100.0,
            'E-e火:蹦蹦炸弹':   float(skill_data['蹦蹦炸弹']['数值']['蹦蹦炸弹伤害'][level_e].replace('%', '')) / 100.0,
            'Q-e火:轰轰火花':   float(skill_data['轰轰火花']['数值']['轰轰火花伤害'][level_q].replace('%', '')) / 100.0,
        }
    if info.name == '八重神子':
        e = '杀生樱伤害·肆阶' if len(info.constellation) >= 2 else '杀生樱伤害·叁阶'
        return {
            'B:l70-增伤-E': (info.prop.elemental_mastery * 0.0015,),
            'B:c4-增伤-*':  (0.2,),
            'B:c6-减防-E':  (0.6,),
            'AZ-e雷:重击':   float(skill_data['普通攻击·狐灵食罪式']['数值']['重击伤害'][level_a].replace('%', '')) / 100.0,
            'E-e雷:杀生樱满阶': float(skill_data['野干役咒·杀生樱']['数值'][e][level_e].replace('%', '')) / 100.0,
            'E-e雷-j超激化:杀生樱满阶超激化': float(skill_data['野干役咒·杀生樱']['数值'][e][level_e].replace('%', '')) / 100.0,
            'Q-e雷:天狐霆雷':  float(skill_data['大密法·天狐显真']['数值']['天狐霆雷伤害'][level_q].replace('%', '')) / 100.0,
            'Q-e雷-j超激化:天狐霆雷超激化': float(skill_data['大密法·天狐显真']['数值']['天狐霆雷伤害'][level_q].replace('%', '')) / 100.0,
        }
    if info.name == '阿贝多':
        return {
            'E-t防御力-e岩:阳华绽放': float(skill_data['创生法·拟造阳华']['数值']['刹那之花伤害'][level_e].replace('%防御力', '')) / 100.0,
            'Q-e岩:大招首段':      float(skill_data['诞生式·大地之潮']['数值']['爆发伤害'][level_q].replace('%', '')) / 100.0
        }
    if info.name == '神里绫华':
        return {
            'B:l50-增伤-AZ': (0.3,),
            'B:l70-增伤-*':  (0.18,),
            'B:c4-减防-*':   (0.3,),
            'B:c6-增伤-AZ':  (2.98, '满命触发'),
            'AZ-n3-e冰:重击': float(skill_data['普通攻击·神里流·倾']['数值']['重击伤害'][level_a].replace('%*3', '')) / 100.0,
            'E-e冰:冰华伤害':   float(skill_data['神里流·冰华']['数值']['技能伤害'][level_e].replace('%', '')) / 100.0,
            'Q-e冰:霜灭每段':   float(skill_data['神里流·霜灭']['数值']['切割伤害'][level_q].replace('%', '')) / 100.0,
        }
    if info.name == '行秋':
        e = skill_data['古华剑·画雨笼山']['数值']['技能伤害'][level_e].split('+')
        dm = 1.5 if len(info.constellation) >= 4 else 1.0
        return {
            'B:l70-增伤-*':  (0.2,),
            'B:c2-减抗-*':   (0.15,),
            'E-e水:画雨笼山':   (float(e[0].replace('%', '')) / 100.0 * dm, float(e[1].replace('%', '')) / 100.0 * dm),
            'Q-e水:裁雨留虹每段': float(skill_data['古华剑·裁雨留虹']['数值']['剑雨伤害'][level_e].replace('%', '')) / 100.0
        }
    if info.name == '夜兰':
        return {
            'B:d':               ['不计算天赋增伤'],
            'B:l50-生命值':         (info.prop.base_health * 0.18, '天赋按3元素'),
            'AZ-t生命值-e水:破局矢':    float(skill_data['普通攻击·潜形隐曜弓']['数值']['破局矢伤害'][level_a].replace('%生命值上限', '')) / 100.0,
            'E-t生命值-e水:元素战技':    float(skill_data['萦络纵命索']['数值']['技能伤害'][level_e].replace('%生命值上限', '')) / 100.0,
            'Q-t生命值-e水-n3:大招每段': float(skill_data['渊图玲珑骰']['数值']['玄掷玲珑伤害'][level_q].replace('%生命值上限*3', '')) / 100.0,
        }
    if info.name == '甘雨':
        dm['B:l50-暴击率-AZ'] = (0.2,)
        dm['B:l70-增伤-AZ'] = (0.2,)
        dm['B:l70-增伤-E'] = (0.2,)
        dm['B:c4-增伤-*'] = (0.25, '四命满层')
        dm['B:c1-减抗-*'] = (0.15,)
        dm['AZ-e冰:霜华矢'] = (float(skill_data['普通攻击·流天射术']['数值']['霜华矢命中伤害'][level_a].replace('%', '')) / 100.0,
                           float(skill_data['普通攻击·流天射术']['数值']['霜华矢·霜华绽发伤害'][level_a].replace('%', '')) / 100.0)
        dm['AZ-r融化1.5-e冰:霜华矢融化'] = dm['AZ-e冰:霜华矢']
        dm['E-e冰:元素战技'] = float(skill_data['山泽麟迹']['数值']['技能伤害'][level_e].replace('%', '')) / 100.0
        dm['Q-e冰:冰棱伤害'] = float(skill_data['降众天华']['数值']['冰棱伤害'][level_q].replace('%', '')) / 100.0
        return dm
    if info.name == '优菈':
        n = 26 if len(info.constellation) >= 6 else 13
        return {
            'B:c1-增伤-*':   (0.3,),
            'B:c4-增伤-Q':   (0.25, '四命触发'),
            'B:l1-减抗-*':   (float(skill_data['冰潮的涡旋']['数值']['物理抗性降低'][level_e].replace('%', '')) / 100.0,),
            'A:普攻第一段':     float(skill_data['普通攻击·西风剑术·宗室']['数值']['一段伤害'][level_a].replace('%', '')) / 100.0,
            'E-e冰:战技长按':   float(skill_data['冰潮的涡旋']['数值']['长按伤害'][level_e].replace('%', '')) / 100.0,
            f'Q:光降之剑{n}层': float(skill_data['凝浪之光剑']['数值']['光降之剑基础伤害'][level_q].replace('%', '')) / 100.0 + float(
                skill_data['凝浪之光剑']['数值']['每层能量伤害'][level_e].replace('%', '')) / 100.0 * n,
        }
    if info.name == '达达利亚':
        e = skill_data['魔王武装·狂澜']['数值']['重击伤害'][level_e].split('+')
        return {
            'E-e水:近战重击':          (float(e[0].replace('%', '')) / 100.0, float(e[1].replace('%', '')) / 100.0),
            'E-e水:断流·斩':          float(skill_data['魔王武装·狂澜']['数值']['断流·斩伤害'][level_e].replace('%', '')) / 100.0,
            'A-e水:断流·破':          float(skill_data['普通攻击·断雨']['数值']['断流·破 伤害'][level_a].replace('%', '')) / 100.0,
            'Q-e水:近战大招':          float(skill_data['极恶技·尽灭闪']['数值']['技能伤害·近战'][level_q].replace('%', '')) / 100.0,
            'Q-e水-r蒸发2.0:近战大招蒸发': float(skill_data['极恶技·尽灭闪']['数值']['技能伤害·近战'][level_q].replace('%', '')) / 100.0,
            'Q-e水:断流·爆':          float(skill_data['极恶技·尽灭闪']['数值']['断流·爆伤害'][level_q].replace('%', '')) / 100.0
        }
    if info.name == '迪卢克':
        return {
            'B:l70-增伤-*':          (0.2,),
            'B:c4-增伤-E':           (0.4, '四命增伤'),
            'B:c2-攻击力':            (info.prop.base_attack * 0.3, '二命满层'),
            'B:c1-增伤-*':           (0.15, '一命增伤'),
            'E-e火:战技第三段':          float(skill_data['逆焰之刃']['数值']['三段伤害'][level_e].replace('%', '')) / 100.0,
            'E-e火-r蒸发1.5:战技第三段蒸发': float(skill_data['逆焰之刃']['数值']['三段伤害'][level_e].replace('%', '')) / 100.0,
            'Q-e火:大招斩击':           float(skill_data['黎明']['数值']['斩击伤害'][level_q].replace('%', '')) / 100.0,
            'Q-e火-r蒸发1.5:大招斩击蒸发':  float(skill_data['黎明']['数值']['斩击伤害'][level_q].replace('%', '')) / 100.0
        }
    if info.name == '凝光':
        return {
            'B:l70-增伤-*': (0.12, '穿屏增伤'),
            'AZ-e岩:重击':   float(skill_data['普通攻击·千金掷']['数值']['重击伤害'][level_a].replace('%', '')) / 100.0,
            'AZ-e岩:星璇伤害': float(
                skill_data['普通攻击·千金掷']['数值']['星璇伤害'][level_a].replace('%', '').replace('每个', '')) / 100.0,
            'E-e岩:璇玑屏':   float(skill_data['璇玑屏']['数值']['技能伤害'][level_e].replace('%', '')) / 100.0,
            'Q-e岩:大招每段':  float(skill_data['天权崩玉']['数值']['每颗宝石伤害'][level_q].replace('%', '').replace('每个', '')) / 100.0,
        }
    if info.name == '菲谢尔':
        dm = {'A:普攻第一段':           float(skill_data['普通攻击·罪灭之矢']['数值']['一段伤害'][level_a].replace('%', '')) / 100.0,
              'E-e雷:奥兹攻击':         float(skill_data['夜巡影翼']['数值']['奥兹攻击伤害'][level_e].replace('%', '')) / 100.0,
              'E-e雷-j超激化:奥兹攻击超激化': float(skill_data['夜巡影翼']['数值']['奥兹攻击伤害'][level_e].replace('%', '')) / 100.0,
              }
        if len(info.constellation) >= 6:
            dm['E-e雷:奥兹协同攻击'] = 0.3
        return dm
    if info.name == '北斗':
        return {
            'B:c6-减抗-*': (0.15, '六命减抗'),
            'E-e雷:完美弹反': float(skill_data['捉浪']['数值']['基础伤害'][level_e].replace('%', '')) / 100.0 + 2 * float(
                skill_data['捉浪']['数值']['每层伤害提升'][level_e].replace('%', '')) / 100.0,
            'E-e雷-j超激化:完美弹反超激化': float(skill_data['捉浪']['数值']['基础伤害'][level_e].replace('%', '')) / 100.0 + 2 * float(
                skill_data['捉浪']['数值']['每层伤害提升'][level_e].replace('%', '')) / 100.0,
            'Q-e雷:斫雷每段': float(skill_data['斫雷']['数值']['闪电伤害'][level_q].replace('%', '')) / 100.0
        }
    if info.name == '诺艾尔':
        extra = 0.5 if len(info.constellation) >= 6 else 0
        e = skill_data['护心铠']['数值']['吸收量'][level_e].split('+')
        ez = skill_data['护心铠']['数值']['治疗量'][level_e].split('+')
        return {
            'B:l1-攻击力':   (
                (float(skill_data['大扫除']['数值']['攻击力提高'][level_q].replace('%防御力',
                                                                         '')) / 100.0 + extra) * info.prop.defense,),
            'A-e岩:普攻第一段': float(skill_data['普通攻击·西风剑术·女仆']['数值']['一段伤害'][level_a].replace('%', '')) / 100.0,
            'T:Q攻击力提高:':  int(
                (float(skill_data['大扫除']['数值']['攻击力提高'][level_q].replace('%防御力',
                                                                         '')) / 100.0 + extra) * info.prop.defense),
            'T:E盾值':      int(float(e[0].replace('%防御力', '')) / 100.0 * info.prop.defense + float(e[1]) * 1.5),
            'T:普攻治疗量/概率': str(int((float(ez[0].replace('%防御力', '')) / 100.0 * info.prop.defense + float(ez[1])) * (
                    1 + info.prop.healing_bonus))) + '/' + skill_data['护心铠']['数值']['治疗触发几率'][level_e]
        }
    if info.name == '神里绫人':
        n = 2 if info.level >= 50 else 0
        return {
            'B:c1-增伤-A':   (0.4, '一命增伤'),
            'B:l1-额外倍率-A': (
                float(skill_data['神里流·镜花']['数值']['浪闪伤害值提高'][level_e].replace('%最大生命值/层', '')) / 100.0 * n * (
                    info.prop.health),),
            'B:l1-增伤-A':   (float(skill_data['神里流·水囿']['数值']['普通攻击伤害提升'][level_q].replace('%', '')) / 100.0,),
            'A-e水:瞬水剑第一段': float(skill_data['神里流·镜花']['数值']['一段瞬水剑伤害'][level_e].replace('%', '')) / 100.0,
            'Q-e水:大招每下':   float(skill_data['神里流·水囿']['数值']['水花剑伤害'][level_q].replace('%', '')) / 100.0
        }
    if info.name == '荒泷一斗':
        return {
            'B:d':           ['开启大招'],
            'B:l70-额外倍率-AZ': (0.35 * info.prop.defense,),
            'B:c6-暴击伤害-AZ':  (0.7,),
            'B:l1-攻击力':      (
            float(skill_data['最恶鬼王·一斗轰临！！']['数值']['攻击力提高'][level_q].replace('%防御力', '')) / 100.0 * info.prop.defense,),
            'AZ-e岩:荒泷逆袈裟连斩': float(skill_data['普通攻击·喧哗屋传说']['数值']['荒泷逆袈裟连斩伤害'][level_a].replace('%', '')) / 100.0,
            'E-e岩:赤牛发破':     float(skill_data['魔杀绝技·赤牛发破！']['数值']['技能伤害'][level_e].replace('%', '')) / 100.0,
        }
    if info.name == '宵宫':
        return {
            'B:l50-增伤-*':          (0.2, '被动一满层'),
            'B:c2-增伤-*':           (0.25, '二命触发'),
            'A-e火-n2:普攻第一段':       float(
                skill_data['焰硝庭火舞']['数值']['炽焰箭伤害'][level_e].replace('%普通攻击伤害', '')) / 100.0 * float(
                skill_data['普通攻击·烟火打扬']['数值']['一段伤害'][level_a].replace('%*2', '')) / 100.0,
            'A-e火-r蒸发1.5:普攻第三段蒸发': (float(
                skill_data['焰硝庭火舞']['数值']['炽焰箭伤害'][level_e].replace('%普通攻击伤害', '')) / 100.0) * float(
                skill_data['普通攻击·烟火打扬']['数值']['三段伤害'][level_a].replace('%', '')) / 100.0,
            'Q-e火:琉金火光爆炸':         float(skill_data['琉金云间草']['数值']['琉金火光爆炸伤害'][level_q].replace('%', '')) / 100.0
        }
    if info.name == '烟绯':
        max_ = 4 if len(info.constellation) >= 6 else 3
        AZB = float(skill_data['普通攻击·火漆制印']['数值']['重击伤害'][level_a].replace('%', '')) / 100.0
        AZ = (AZB, 0.8) if info.level >= 70 else (AZB,)
        return {
            'B:l50-增伤-*':   (0.05 * max_, '满层丹火印'),
            'B:c2-暴击率-AZ':  (0.2,),
            'B:l1-增伤-AZ':   (float(skill_data['凭此结契']['数值']['重击伤害提升'][level_q].replace('%', '')) / 100.0,),
            'AZ-e火:满丹火印重击': AZ,
            'E-e火:元素战技':    float(skill_data['丹书立约']['数值']['技能伤害'][level_e].replace('%', '')) / 100.0,
            'Q-e火:元素爆发':    float(skill_data['凭此结契']['数值']['技能伤害'][level_q].replace('%', '')) / 100.0,
        }
    if info.name == '珊瑚宫心海':
        return {
            '普攻第一段':  float(skill_data['普通攻击·水有常形']['数值']['一段伤害'][level_a].replace('%', '')) / 100.0,
            '水母伤害':   float(skill_data['海月之誓']['数值']['波纹伤害'][level_e].replace('%', '')) / 100.0,
            '水母治疗量':  skill_data['海月之誓']['数值']['治疗量'][level_e].split('+'),
            '大招伤害':   float(skill_data['海人化羽']['数值']['技能伤害'][level_q].replace('%生命值上限', '')) / 100.0,
            '普攻伤害提升': float(skill_data['海人化羽']['数值']['普通攻击伤害提升'][level_q].replace('%生命值上限', '')) / 100.0,
            'E伤害提升':  float(skill_data['海人化羽']['数值']['化海月伤害提升'][level_q].replace('%生命值上限', '')) / 100.0,
            '大招治疗量':  skill_data['海人化羽']['数值']['命中治疗量'][level_q].split('+')
        }
    if info.name == '枫原万叶':
        info.prop.elemental_mastery += 200 if len(info.constellation) >= 2 else 0
        return {
            'B:d':          ['技能仅计算风伤部分'],
            'B:c6-增伤-AX':   (info.prop.elemental_mastery * 0.002,),
            'AX-e风:E后高空下落': float(
                skill_data['普通攻击·我流剑术']['数值']['低空/高空坠地冲击伤害'][level_a].split('/')[1].replace('%', '')) / 100.0,
            'E-e风:E点按伤害':   float(skill_data['千早振']['数值']['点按技能伤害'][level_e].replace('%', '')) / 100.0,
            'Q-e风:大招斩击':    float(skill_data['万叶之一刀']['数值']['斩击伤害'][level_q].replace('%', '')) / 100.0,
            'Q-e风:大招持续':    float(skill_data['万叶之一刀']['数值']['持续伤害'][level_q].replace('%', '')) / 100.0,
            'T:扩散伤害':       int(
                upheaval_reaction(info.level, '扩散', info.prop.elemental_mastery, info.prop.reaction_coefficient['扩散']))
        }
    if info.name == '鹿野院平藏':
        e = skill_data['勠心拳']['数值']
        info.prop.elemental_mastery += 80 if info.level >= 70 else 0
        return {
            'B:c6-暴击率-E':  (0.16,),
            'B:c6-暴击伤害-E': (0.32,),
            'AZ-e风:重击':    float(skill_data['普通攻击·不动流格斗术']['数值']['重击伤害'][level_a].replace('%', '')) / 100.0,
            'E-e风:满层勠心拳':  (float(e['技能伤害'][level_e].replace('%', '')) + 4 * float(
                e['变格伤害提升'][level_e].replace('%/层', '')) + float(e['正论伤害提升'][level_e].replace('%', ''))) / 100.0,
            'Q-e风:聚风蹴真空弹': float(skill_data['聚风蹴']['数值']['不动流·真空弹伤害'][level_q].replace('%', '')) / 100.0,
            'T:扩散伤害':      int(
                upheaval_reaction(info.level, '扩散', info.prop.elemental_mastery, info.prop.reaction_coefficient['扩散']))
        }
    if info.name == '班尼特':
        attack_increase = float(skill_data['美妙旅程']['数值']['攻击力加成比例'][level_q].replace('%', '')) / 100.0 + (
            0.2 if len(info.constellation) >= 1 else 0)
        hp_recover = skill_data['美妙旅程']['数值']['持续治疗'][level_q].split('+')
        return {
            'B:c6-增伤-E':   (0.15,),
            'B:l1-攻击力':    (int(attack_increase * info.prop.base_attack),),
            'E-e火:元素战技点按': float(skill_data['热情过载']['数值']['点按伤害'][level_e].replace('%', '')) / 100.0,
            'Q-e火:大招伤害':   float(skill_data['美妙旅程']['数值']['技能伤害'][level_q].replace('%', '')) / 100.0,
            'T:大招攻击加成':    int(attack_increase * info.prop.base_attack),
            'T:大招持续治疗':    int(
                (float(hp_recover[0].replace('每秒', '').replace('%生命值上限', '')) / 100.0 * info.prop.health + int(
                    hp_recover[1])) * (
                        1 + info.prop.healing_bonus)),
        }
    if info.name == '温迪':
        return {
            'B:d':         ['技能仅计算风伤部分'],
            'B:c2-减抗-*':   (0.24, '二命减抗'),
            'B:c4-增伤-*':   (0.25, '四命增伤'),
            'B:c6-减抗-*':   (0.2, '六命减抗'),
            'E-e风:E点按伤害':  float(skill_data['高天之歌']['数值']['点按伤害'][level_e].replace('%', '')) / 100.0,
            'Q-e风:大招持续伤害': float(skill_data['风神之诗']['数值']['持续伤害'][level_q].replace('%', '')) / 100.0,
            'T:扩散伤害':      int(
                upheaval_reaction(info.level, '扩散', info.prop.elemental_mastery, info.prop.reaction_coefficient['扩散']))
        }
    if info.name == '莫娜':
        if len(info.constellation) >= 1:
            info.prop.reaction_coefficient['蒸发'] += 0.15
        return {
            'B:c4-暴击率-*':         (0.15,),
            'B:c6-增伤-AZ':         (1.8, '六命重击增伤满层'),
            'B:l1-增伤-*':          (float(skill_data['星命定轨']['数值']['伤害加成'][level_q].replace('%', '')) / 100.0, '星异增伤'),
            'AZ-e水:重击':           float(skill_data['普通攻击·因果点破']['数值']['重击伤害'][level_a].replace('%', '')) / 100.0,
            'E-e水:E持续伤害':         float(skill_data['水中幻愿']['数值']['持续伤害'][level_e].replace('%', '')) / 100.0,
            'Q-e水:泡影破裂':          float(skill_data['星命定轨']['数值']['泡影破裂伤害'][level_q].replace('%', '')) / 100.0,
            'Q-e水-r蒸发2.0:泡影破裂蒸发': float(skill_data['星命定轨']['数值']['泡影破裂伤害'][level_q].replace('%', '')) / 100.0,
        }
    if info.name == '琴':
        recovery1 = skill_data['蒲公英之风']['数值']['领域发动治疗量'][level_q].split('+')
        recovery2 = skill_data['蒲公英之风']['数值']['持续治疗'][level_q].split('+')
        return {
            'B:c1-增伤-E':     (0.4, '战技长按1秒'),
            'B:c4-减抗-E':     (0.4, '四命减抗'),
            'B:c4-减抗-Q':     (0.4,),
            'AZ:重击':         float(skill_data['普通攻击·西风剑术']['数值']['重击伤害'][level_a].replace('%', '')) / 100.0,
            'E-e风:风压剑':      float(skill_data['风压剑']['数值']['技能伤害'][level_e].replace('%', '')) / 100.0,
            'Q-e风:大招爆发伤害':   float(skill_data['蒲公英之风']['数值']['爆发伤害'][level_q].replace('%', '')) / 100.0,
            'Q-e风:大招出入领域伤害': float(skill_data['蒲公英之风']['数值']['出入领域伤害'][level_q].replace('%', '')) / 100.0,
            'T:大招瞬时治疗':      int(
                (float(recovery1[0].replace('%攻击力', '')) / 100.0 * info.prop.attack + int(recovery1[1])) * (
                        1 + info.prop.healing_bonus)),
            'T:大招持续治疗':      int(
                (float(recovery2[0].replace('每秒', '').replace('%攻击力', '')) / 100.0 * info.prop.attack + int(
                    recovery2[1])) * (
                        1 + info.prop.healing_bonus)),
        }
    if info.name == '七七':
        a = skill_data['普通攻击·云来古剑法']['数值']['重击伤害'][level_a].split('+')
        a_rec = skill_data['仙法·寒病鬼差']['数值']['命中治疗量'][level_e].split('+')
        e_rec = skill_data['仙法·寒病鬼差']['数值']['持续治疗量'][level_e].split('+')
        q_rec = skill_data['仙法·救苦度厄']['数值']['治疗量'][level_e].split('+')
        return {
            'B:c1-增伤-AZ': (0.15,),
            'AZ:重击':      (float(a[0].replace('%', '')) / 100.0, float(a[0].replace('%', '')) / 100.0),
            'E-e冰:E释放伤害': float(skill_data['仙法·寒病鬼差']['数值']['技能伤害'][level_e].replace('%', '')) / 100.0,
            'T:开E后普攻治疗量': int(
                (float(a_rec[0].replace('%攻击力', '')) / 100.0 * info.prop.attack + int(a_rec[1])) * (
                            1 + info.prop.healing_bonus)),
            'T:E持续治疗量':   int(
                (float(e_rec[0].replace('%攻击力', '')) / 100.0 * info.prop.attack + int(e_rec[1])) * (
                            1 + info.prop.healing_bonus)),
            'T:挂符每次治疗量':  int(
                (float(q_rec[0].replace('%攻击力', '')) / 100.0 * info.prop.attack + int(q_rec[1])) * (
                            1 + info.prop.healing_bonus)),
            'Q-e冰:大招伤害':  float(skill_data['仙法·救苦度厄']['数值']['技能伤害'][level_q].replace('%', '')) / 100.0,
        }
    if info.name == '提纳里':
        info.prop.elemental_mastery += 50 if info.level >= 50 else 0
        info.prop.elemental_mastery += 120 if len(info.constellation) >= 4 else 0
        return {
            'B:c1-暴击率-AZ': (0.15,),
            'B:c2-增伤-*': (0.2, '二命增伤'),
            'B:c4-增伤-*': (0, '四命精通'),
            'B:l70-增伤-AZ': (min(info.prop.elemental_mastery, 1000) * 0.0006, ),
            'B:l70-增伤-Q': (min(info.prop.elemental_mastery, 1000) * 0.0006,),
            'AZ-e草:重击花筥箭': float(skill_data['普通攻击·藏蕴破障']['数值']['花筥箭伤害'][level_a].replace('%', '')) / 100.0,
            'AZ-e草-j蔓激化:重击花筥箭蔓激化': float(skill_data['普通攻击·藏蕴破障']['数值']['花筥箭伤害'][level_a].replace('%', '')) / 100.0,
            'AZ-e草-n4:重击藏蕴花矢': float(skill_data['普通攻击·藏蕴破障']['数值']['藏蕴花矢伤害'][level_a].replace('%', '')) / 100.0,
            'Q-e草:缠藤箭':   float(skill_data['造生缠藤箭']['数值']['缠藤箭伤害'][level_q].replace('%', '')) / 100.0,
            'Q-e草-j蔓激化:缠藤箭蔓激化': float(skill_data['造生缠藤箭']['数值']['缠藤箭伤害'][level_q].replace('%', '')) / 100.0,
            'Q-e草:次级缠藤箭-n6': float(skill_data['造生缠藤箭']['数值']['次级缠藤箭伤害'][level_q].replace('%', '')) / 100.0,
        }
    if info.name == '柯莱':
        info.prop.elemental_mastery += 60 if len(info.constellation) >= 4 else 0
        return {
            'E-e草:飞叶轮': float(skill_data['拂花偈叶']['数值']['技能伤害'][level_e].replace('%', '')) / 100.0,
            'E-e草-j蔓激化:飞叶轮蔓激化': float(skill_data['拂花偈叶']['数值']['技能伤害'][level_e].replace('%', '')) / 100.0,
            'Q-e草:大招爆发伤害':         float(skill_data['猫猫秘宝']['数值']['爆发伤害'][level_q].replace('%', '')) / 100.0,
            'Q-e草-j蔓激化:大招爆发蔓激化': float(skill_data['猫猫秘宝']['数值']['爆发伤害'][level_q].replace('%', '')) / 100.0,
            'Q-e草:大招持续伤害':       float(skill_data['猫猫秘宝']['数值']['跃动伤害'][level_q].replace('%', '')) / 100.0,
            'Q-e草-j蔓激化:大招持续蔓激化': float(skill_data['猫猫秘宝']['数值']['跃动伤害'][level_q].replace('%', '')) / 100.0
        }
    if info.name == '多莉':
        h = skill_data['卡萨扎莱宫的无微不至']['数值']['持续治疗量'][level_q].split('生命值上限+')
        return {
            'E-e雷:断除烦恼炮': float(skill_data['镇灵之灯·烦恼解决炮']['数值']['断除烦恼炮伤害'][level_e].replace('%', '')) / 100.0,
            'T:大招持续治疗量': int(float(h[0].replace('%', '')) / 100.0 * info.prop.health + float(h[1]) * (1 + info.prop.healing_bonus)),
        }
    if info.name == '九条裟罗':
        atk = float(skill_data['鸦羽天狗霆雷召咒']['数值']['攻击力加成比例'][level_e].replace('%', '')) / 100.0 * info.prop.base_attack
        return {
            'T:乌羽攻击加成': int(atk),
            'B:l0-攻击力-*': (atk, ),
            'B:c6-暴击伤害-*': (0.6, ),
            'E-e雷:元素战技': float(skill_data['鸦羽天狗霆雷召咒']['数值']['天狗咒雷•伏伤害'][level_e].replace('%', '')) / 100.0,
            'Q-e雷:大招首段': float(skill_data['煌煌千道镇式']['数值']['天狗咒雷•金刚坏伤害'][level_q].replace('%', '')) / 100.0,
            'Q-e雷-j超激化:大招首段超激化': float(skill_data['煌煌千道镇式']['数值']['天狗咒雷•金刚坏伤害'][level_q].replace('%', '')) / 100.0,
            'Q-e雷:大招雷砾': float(skill_data['煌煌千道镇式']['数值']['天狗咒雷•雷砾伤害'][level_q].replace('%', '')) / 100.0,
        }
    if info.name == '纳西妲':
        c = 1 if len(info.constellation) == 0 else 2
        info.prop.elemental_mastery += 160 if len(info.constellation) >= 4 else 0
        eb = skill_data['所闻遍计']['数值']['灭净三业伤害'][level_e].split('+')
        return {
            'B:l0-增伤-E': (float(skill_data['心景幻成']['数值'][f'火：伤害提升{c}'][level_q].replace('%', '')) / 100.0, f'大招计算{c}火'),
            'B:l70-增伤-E': (0.8 if info.prop.elemental_mastery >= 1000 else (
                    0.001 * (info.prop.elemental_mastery - 200)) if info.prop.elemental_mastery >= 200 else 0, ),
            'B:l70-暴击率-E': (0.24 if info.prop.elemental_mastery >= 1000 else (
                        0.0003 * (info.prop.elemental_mastery - 200)) if info.prop.elemental_mastery >= 200 else 0,),
            'B:c2-减防-*': (0.3, '二命减防'),
            'B:l0-额外倍率-E': (float(eb[1].replace('%元素精通', '')) / 100.0 * info.prop.elemental_mastery, ),
            'E-e草:灭净三业': float(eb[0].replace('%攻击力', '')) / 100.0,
            'E-e草-j蔓激化:灭净三业蔓激化': float(eb[0].replace('%攻击力', '')) / 100.0
        }


async def draw_dmg_pic(dmg: Dict[str, Union[tuple, list]]) -> PMImage:
    """
    绘制伤害图片
    :param dmg: 伤害字典
    :return: 伤害图片
    """
    height = 60 * len(dmg) - 20
    img = PMImage(size=(1002, height + 80), color=(0, 0, 0, 0), mode='RGBA')
    await img.draw_rounded_rectangle((0, 0, img.width, img.height), 10, (14, 41, 68, 115))
    await img.draw_line((250, 0), (250, 1002), (255, 255, 255, 75), 2)
    await img.draw_line((626, 0), (626, 60), (255, 255, 255, 75), 2)
    await img.draw_line((0, 60), (1002, 60), (255, 255, 255, 75), 2)
    await img.text('伤害计算', (0, 250), (0, 60), font_manager.get('hywh.ttf', 30), 'white', 'center')
    await img.text('期望伤害', (250, 626), (0, 60), font_manager.get('hywh.ttf', 30), 'white', 'center')
    await img.text('暴击伤害', (626, 1002), (0, 60), font_manager.get('hywh.ttf', 30), 'white', 'center')
    i = 1
    for describe, dmg_list in dmg.items():
        await img.draw_line((0, 60 * i), (1002, 60 * i), (255, 255, 255, 75), 2)
        await img.text(describe, (0, 250), (60 * i, 60 * (i + 1)), font_manager.get('hywh.ttf', 30), 'white', 'center')
        if len(dmg_list) == 1:
            if describe == '额外说明':
                await img.text(dmg_list[0], (250, 1002), (60 * i, 60 * (i + 1)), font_manager.get('hywh.ttf', 30),
                               'white',
                               'center')
            else:
                await img.text(dmg_list[0], (250, 1002), (60 * i, 60 * (i + 1)), font_manager.get('number.ttf', 30),
                               'white',
                               'center')
        else:
            await img.draw_line((626, 60 * i), (626, 60 * (i + 1)), (255, 255, 255, 75), 2)
            await img.text(dmg_list[0], (250, 626), (60 * i, 60 * (i + 1)), font_manager.get('number.ttf', 30), 'white',
                           'center')
            await img.text(dmg_list[1], (626, 1002), (60 * i, 60 * (i + 1)), font_manager.get('number.ttf', 30), 'white',
                           'center')
        i += 1

    return img
