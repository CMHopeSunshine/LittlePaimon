from pathlib import Path

from ...utils.enka_util import get_artifact_suit

text_font = str(Path() / 'resources' / 'LittlePaimon' / 'hywh.ttf')
number_font = str(Path() / 'resources' / 'LittlePaimon' / 'number.ttf')


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


def defense_coefficient(self_level: int, enemy_level: int = 90, reduction_rate: float = 0, ignore: float = 0):
    """
    计算防御力系数
    :param self_level: 角色自身等级
    :param enemy_level: 怪物等级
    :param reduction_rate: 减防系数
    :param ignore: 无视防御系数
    :return: 防御力系数
    """
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
    base_coefficient = 723  # 暂缺全等级剧变反应的系数，先写90级的
    mastery_increase = (16 * mastery) / (mastery + 2000)
    return base_coefficient * base_ratio * (1 + mastery_increase + extra_coefficient) * resistance


def polearm_common_fix(data: dict):
    """
    对长柄武器角色的通用面板属性修正
    :param data: 角色数据
    :return: 角色数据
    """
    attr = data['属性']
    weapon = data['武器']
    if weapon['名称'] == '护摩之杖':
        attr['额外攻击'] += (attr['基础生命'] + attr['额外生命']) * (0.008 + 0.002 * weapon['精炼等级'])
        if '半血以下' not in data['伤害描述']:
            data['伤害描述'].append('半血以下')
    elif weapon['名称'] == '和璞鸢':
        attr['额外攻击'] += attr['基础攻击'] * 7 * (0.025 + 0.007 * weapon['精炼等级'])
        for i, k in enumerate(attr['伤害加成']):
            attr['伤害加成'][i] = k + (0.09 + 0.03 * weapon['精炼等级'])
        data['伤害描述'].append('和璞鸢满层')
    elif weapon['名称'] == '贯虹之槊':
        attr['额外攻击'] += attr['基础攻击'] * 2 * 5 * (0.003 + 0.001 * weapon['精炼等级'])
        attr['护盾强效'] += 0.15 + 0.05 * weapon['精炼等级']
        data['伤害描述'].append('贯虹带盾满层')
    elif weapon['名称'] == '决斗之枪':
        attr['额外攻击'] += attr['基础攻击'] * 0.18 + 0.06 * weapon['精炼等级']
        data['伤害描述'].append('决斗单怪')
    elif weapon['名称'] == '息灾':
        for i, k in enumerate(attr['伤害加成']):
            attr['伤害加成'][i] = k + (0.09 + 0.03 * weapon['精炼等级'])
        attr['额外攻击'] += attr['基础攻击'] * 6 * (0.024 + 0.006 * weapon['精炼等级'])
        data['伤害描述'].append('息灾前台满层')
    elif weapon['名称'] == '薙草之稻光':
        attr['额外攻击'] += attr['基础攻击'] * (attr['元素充能效率'] - 1) * (0.21 + 0.07 * weapon['精炼等级'])
        attr['元素充能效率'] += 0.25 + 0.05 * weapon['精炼等级']
    elif weapon['名称'] == '天空之脊':
        attr['暴击率'] += (0.06 + 0.02 * weapon['精炼等级'])
    elif weapon['名称'] == '千岩长枪':
        attr['暴击率'] += (0.02 + 0.01 * weapon['精炼等级'])
        attr['额外攻击'] += attr['基础攻击'] * (0.06 + 0.01 * weapon['精炼等级'])
        data['伤害描述'].append('璃月人1层')
    elif weapon['名称'] == '匣里灭辰':
        for i, k in enumerate(attr['伤害加成']):
            attr['伤害加成'][i] = k + (0.16 + 0.04 * weapon['精炼等级'])
        data['伤害描述'].append('灭辰触发')
    elif weapon['名称'] == '黑岩刺枪':
        attr['额外攻击'] += attr['基础攻击'] * (0.09 + 0.03 * weapon['精炼等级'])
        data['伤害描述'].append('黑岩1层')

    data['属性'] = attr
    return data


def attr_common_fix(data: dict):
    """
    对武器、圣遗物的通用面板属性修正
    :param data: 角色数据
    :return: 角色数据
    """
    if '伤害描述' not in data:
        data['伤害描述'] = []
    if '护盾强效' not in data['属性']:
        data['属性']['护盾强效'] = 0
    if data['武器']['类型'] == '长柄武器':
        data = polearm_common_fix(data)
    artifacts = data['圣遗物']
    attr = data['属性']
    suit = get_artifact_suit(artifacts)
    # 两件套的情况
    if '逆飞的流星' in suit:
        attr['护盾强效'] += 0.35
    if len(suit) == 2:
        # 四件套的情况
        if suit[0][0] == suit[1][0]:
            if suit[0][0] == '苍白之火':
                attr['额外攻击'] += attr['基础攻击'] * 0.18
                attr['伤害加成'][0] += 0.25
                data['伤害描述'].append('苍白满层')
            elif suit[0][0] == '华馆梦醒形骸记':
                attr['伤害加成'][6] += 0.24
                attr['额外防御'] += attr['基础防御'] * 0.24
                data['伤害描述'].append('华馆满层')
            elif suit[0][0] == '千岩牢固':
                attr['护盾强效'] += 0.3
                attr['额外攻击'] += attr['基础攻击'] * 0.2
                data['伤害描述'].append('千岩触发')
            elif suit[0][0] == '昔日宗室之仪':
                attr['额外攻击'] += attr['基础攻击'] * 0.2
                data['伤害描述'].append('宗室触发')
            elif suit[0][0] == '冰风迷途的勇士':
                attr['暴击率'] += 0.4
                data['伤害描述'].append('冰套暴击40%')
            elif suit[0][0] == '勇士之心':
                for i, k in enumerate(attr['伤害加成']):
                    attr['伤害加成'][i] = k + 0.3
                data['伤害描述'].append('勇士触发')
            elif suit[0][0] == '教官':
                attr['元素精通'] += 120
                data['伤害描述'].append('教官触发')
            elif suit[0][0] == '炽烈的炎之魔女':
                if data['名称'] in ['胡桃', '宵宫']:
                    attr['伤害加成'][1] += 0.075
                    data['伤害描述'].append('魔女1层')
                else:
                    attr['伤害加成'][1] += 0.225
                    data['伤害描述'].append('魔女满层')
                attr['蒸发系数'] = 0.15
            elif suit[0][0] == '渡过烈火的贤人':
                for i, k in enumerate(attr['伤害加成']):
                    attr['伤害加成'][i] = k + 0.5
                data['伤害描述'].append('渡火触发')
            elif suit[0][0] == '平息鸣雷的尊者':
                for i, k in enumerate(attr['伤害加成']):
                    attr['伤害加成'][i] = k + 0.5
                data['伤害描述'].append('平雷触发')
            elif suit[0][0] == '战狂':
                attr['暴击率'] += 0.24
                data['伤害描述'].append('战狂触发')
            elif suit[0][0] == '辰砂往生录':
                attr['额外攻击'] += attr['基础攻击'] * 0.48
                data['伤害描述'].append('辰砂满层')
            elif suit[0][0] == '被怜爱的少女':
                attr['受治疗加成'] += 0.2
    data['属性'] = attr
    return data


def q_fix(data: dict):
    # 武器
    attr = data['属性']
    extra_value = {
        '暴击率': 0,
        '增伤': 0
    }
    weapon = data['武器']
    if weapon['名称'] == '「渔获」':
        extra_value['增伤'] += 0.12 + 0.04 * weapon['精炼等级']
        extra_value['暴击率'] += 0.045 + 0.015 * weapon['精炼等级']
    if weapon['名称'] == '断浪长鳍':
        extra_value['增伤'] += (0.0009 + 0.0003 * weapon['精炼等级']) * 240
        data['伤害描述'].append('断浪算240能量')

    # 圣遗物
    artifacts = data['圣遗物']
    suit = get_artifact_suit(artifacts)
    # 两件套的情况
    if '昔日宗室之仪' in suit:
        extra_value['增伤'] += 0.2
    if len(suit) == 2:
        # 四件套的情况
        if suit[0][0] == suit[1][0]:
            if suit[0][0] == '绝缘之旗印':
                extra_value['增伤'] += 0.25 * attr['元素充能效率']

    return data, extra_value


def e_fix(data: dict):
    # 武器
    attr = data['属性']
    extra_value = {
        '暴击率': 0,
        '增伤': 0
    }
    # 圣遗物
    artifacts = data['圣遗物']
    suit = get_artifact_suit(artifacts)
    # 两件套的情况
    if '赌徒' in suit:
        extra_value['增伤'] += 0.2
    return data, extra_value


def a_fix(data: dict):
    # 武器
    attr = data['属性']
    extra_value = {
        '普攻暴击率': 0,
        '普攻增伤':  0,
        '重击暴击率': 0,
        '重击增伤': 0,
        '下落攻击暴击率': 0,
        '下落攻击增伤':  0
    }
    weapon = data['武器']
    if weapon['名称'] == '白缨枪':
        extra_value['普攻增伤'] += 0.18 + 0.06 * weapon['精炼等级']

    # 圣遗物
    artifacts = data['圣遗物']
    suit = get_artifact_suit(artifacts)
    # # 两件套的情况
    if '武人' in suit:
        extra_value['普攻增伤'] += 0.15
        extra_value['重击增伤'] += 0.15
    if len(suit) == 2:
        # 四件套的情况
        if suit[0][0] == suit[1][0]:
            if suit[0][0] == '追忆之注连':
                extra_value['普攻增伤'] += 0.5
                extra_value['重击增伤'] += 0.5
                extra_value['下落攻击增伤'] += 0.5
                data['伤害描述'].append('追忆触发')
            elif suit[0][0] == '流浪大地的乐团':
                if weapon['类型'] in ['法器', '弓箭']:
                    extra_value['重击增伤'] += 0.35
            elif suit[0][0] == '角斗士的终幕礼':
                if weapon['类型'] in ['单手剑', '双手剑', '长柄武器']:
                    extra_value['普攻增伤'] += 0.35
            elif suit[0][0] == '染血的骑士道':
                extra_value['重击增伤'] += 0.5
                data['伤害描述'].append('染血触发')
            elif suit[0][0] == '沉沦之心':
                extra_value['普攻增伤'] += 0.3
                extra_value['重击增伤'] += 0.3
                data['伤害描述'].append('沉沦触发')
            elif suit[0][0] == '逆飞的流星':
                extra_value['普攻增伤'] += 0.4
                extra_value['重击增伤'] += 0.4
                data['伤害描述'].append('流星触发')
            elif suit[0][0] == '武人':
                extra_value['普攻增伤'] += 0.25
                extra_value['重击增伤'] += 0.25
                data['伤害描述'].append('武人触发')
            elif suit[0][0] == '行者之心':
                extra_value['重击暴击率'] += 0.3

    return data, extra_value
