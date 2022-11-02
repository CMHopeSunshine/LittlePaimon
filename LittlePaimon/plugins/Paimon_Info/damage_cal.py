from copy import deepcopy
from LittlePaimon.database import Character

from .damage_model import common_fix, draw_dmg_pic, udc, get_damage_multipiler, growth_reaction, intensify_reaction


async def get_role_dmg(info: Character):
    dm = get_damage_multipiler(deepcopy(info))
    if not dm:
        return None
    dmg_data = {}
    info, vq, ve, va = common_fix(deepcopy(info))
    # 物理, 火, 雷, 水, 草, 风, 岩, 冰
    if info.name == '钟离':
        info.damage_describe.insert(0, '护盾减抗')
        dmg_data['玉璋护盾'] = (str(int((info.prop.health * dm['玉璋护盾'][0] + dm['玉璋护盾'][1]) * (1 + info.prop.shield_strength) * 1.5)),)
        dmg_data['原岩共鸣'] = udc(dm['原岩共鸣'] * info.prop.attack + (info.prop.health * 0.019) if info.level >= 70 else 0, (info.prop.crit_rate + ve['暴击率'], info.prop.crit_damage),
                               info.prop.dmg_bonus['岩'] + ve['增伤'], info.level, rcd=0.2)
        dmg_data['天星伤害'] = udc(dm['天星'] * info.prop.attack + (info.prop.health * 0.33) if info.level >= 70 else 0, (info.prop.crit_rate + vq['暴击率'], info.prop.crit_damage),
                               info.prop.dmg_bonus['岩'] + vq['增伤'], info.level, rcd=0.2)
        a = udc(dm['踢枪'] * info.prop.attack + (info.prop.health * 0.0139) if info.level >= 70 else 0, (info.prop.crit_rate + va['普攻暴击率'], info.prop.crit_damage),
                info.prop.dmg_bonus['物理'] + va['普攻增伤'], info.level, rcd=0.2)
        if info.weapon.name == '流月针':
            ly = udc((0.15 + 0.05 * info.weapon.affix_level) * info.prop.attack, (info.prop.crit_rate, info.prop.crit_damage), info.prop.dmg_bonus['物理'], info.level, rcd=0.2)
            a[0] += f'+{ly[0]}'
            a[1] += f'+{ly[1]}'
        dmg_data['踢枪伤害'] = a
    elif info.name == '雷电将军':
        r = intensify_reaction(info.level, '超激化', info.prop.elemental_mastery, info.prop.reaction_coefficient['激化'])
        info.damage_describe.insert(0, '满愿力')
        vq['增伤'] += dm['e增伤']
        dci = 0.6 if len(info.constellation) >= 2 else 0
        dmg_data['协同攻击'] = udc(dm['协同攻击'] * info.prop.attack, (info.prop.crit_rate + ve['暴击率'], info.prop.crit_damage), info.prop.dmg_bonus['雷'] + ve['增伤'], info.level, dci=dci)
        dmg_data['梦想一刀'] = udc((dm['梦想一刀基础'] + dm['梦想一刀愿力']) * info.prop.attack,
                               (info.prop.crit_rate + vq['暴击率'], info.prop.crit_damage),
                               info.prop.dmg_bonus['雷'] + vq['增伤'],
                               info.level, dci=dci)
        dmg_data['梦想一刀超激化'] = udc((dm['梦想一刀基础'] + dm['梦想一刀愿力']) * info.prop.attack + r,
                               (info.prop.crit_rate + vq['暴击率'], info.prop.crit_damage),
                               info.prop.dmg_bonus['雷'] + vq['增伤'],
                               info.level, dci=dci)
        a1 = udc((dm['梦想一心重击基础'][0] + dm['梦想一心愿力']) * info.prop.attack, (info.prop.crit_rate + vq['暴击率'], info.prop.crit_damage), info.prop.dmg_bonus['雷'] + vq['增伤'], info.level,
                 dci=dci)
        a2 = udc((dm['梦想一心重击基础'][1] + dm['梦想一心愿力']) * info.prop.attack, (info.prop.crit_rate + vq['暴击率'], info.prop.crit_damage), info.prop.dmg_bonus['雷'] + vq['增伤'], info.level,
                 dci=dci)
        dmg_data['梦想一心重击'] = (f'{a1[0]}+{a2[0]}', f'{a1[1]}+{a2[1]}')
        extra_energy = (info.prop.elemental_efficiency - 1) * 0.6 if info.level >= 70 else 0
        dmg_data['梦想一心能量'] = (str(round(dm['梦想一心能量'] * (1 + extra_energy) * 5, 1)),)
    elif info.name == '申鹤':
        dmg_data['冰翎加成'] = (str(int(dm['冰翎'] * info.prop.attack)),)
        bl = int(dmg_data['冰翎加成'][0])
        info.prop.dmg_bonus['冰'] += 0.15 if info.level >= 40 else 0
        vq['增伤'] += 0.15 if info.level >= 70 else 0
        dmg_data['战技长按'] = udc(dm['e长按'] * info.prop.attack + bl, (info.prop.crit_rate + ve['暴击率'], info.prop.crit_damage), info.prop.dmg_bonus['冰'] + ve['增伤'], info.level, rcd=dm['大招减抗'])
        dmg_data['大招持续伤害'] = udc(dm['大招持续'] * info.prop.attack + bl, (info.prop.crit_rate + vq['暴击率'], info.prop.crit_damage), info.prop.dmg_bonus['冰'] + vq['增伤'], info.level,
                                 rcd=dm['大招减抗'])
    elif info.name == '珊瑚宫心海':
        adb = 0.15 * info.prop.healing_bonus if info.level >= 70 else 0
        if len(info.constellation) >= 6:
            info.prop.dmg_bonus['水'] += 0.4
            info.damage_describe.insert(0, '六命触发')
        ab = udc(dm['普攻第一段'] * info.prop.attack, (info.prop.crit_rate + va['普攻暴击率'], info.prop.crit_damage), info.prop.dmg_bonus['水'] + va['普攻增伤'], info.level)
        aq = udc(dm['普攻伤害提升'] * info.prop.health, (info.prop.crit_rate + va['普攻暴击率'], info.prop.crit_damage), info.prop.dmg_bonus['水'] + adb + va['普攻增伤'], info.level)
        if len(ab) == 1:
            dmg_data['开大普攻第一段'] = (str(int(ab[0]) + int(aq[0])), )
        else:
            dmg_data['开大普攻第一段'] = (str(int(ab[0]) + int(aq[0])), str(int(ab[1]) + int(aq[1])))
        dmg_data['开大战技伤害'] = udc(dm['水母伤害'] * info.prop.attack + dm['E伤害提升'] * info.prop.health, (info.prop.crit_rate + ve['暴击率'], info.prop.crit_damage), info.prop.dmg_bonus['水'] + ve['增伤'], info.level)
        dmg_data['大招释放伤害'] = udc(dm['大招伤害'] * info.prop.health, (info.prop.crit_rate + vq['暴击率'], info.prop.crit_damage), info.prop.dmg_bonus['水'] + vq['增伤'], info.level)
        dmg_data['开大普攻治疗量'] = (str(int((float(dm['大招治疗量'][0].replace('%生命值上限', '')) / 100.0 * info.prop.health + float(dm['大招治疗量'][1])) * (1 + info.prop.healing_bonus))),)
        dmg_data['战技治疗量'] = (str(int((float(dm['水母治疗量'][0].replace('%生命值上限', '')) / 100.0 * info.prop.health + float(dm['水母治疗量'][1])) * (1 + info.prop.healing_bonus))),)
    else:
        dmg_data = get_dmg_data(info, dm, va, ve, vq)
    if info.damage_describe:
        dmg_data['额外说明'] = ('，'.join(info.damage_describe),)
    return await draw_dmg_pic(dmg_data) if dmg_data else None


def get_dmg_data(info: Character, dm: dict, va: dict, ve: dict, vq: dict) -> dict:
    dmg_data = {}
    v = {'A': {
            '暴击率': va['普攻暴击率'],
            '暴击伤害': 0,
            '增伤':  va['普攻增伤'],
            '额外倍率': va['普攻额外倍率'],
            '减抗': va['减抗'],
            '减防': 0
        },
        'AZ': {
            '暴击率': va['重击暴击率'],
            '暴击伤害': 0,
            '增伤':  va['重击增伤'],
            '额外倍率': va['重击额外倍率'],
            '减抗': va['减抗'],
            '减防': 0
        },
        'AX': {
            '暴击率': va['下落攻击暴击率'],
            '暴击伤害': 0,
            '增伤':  va['下落攻击增伤'],
            '额外倍率': va['下落攻击额外倍率'],
            '减抗': va['减抗'],
            '减防': 0
        },
        'E':  {
            '暴击率': ve['暴击率'],
            '暴击伤害': 0,
            '增伤':  ve['增伤'],
            '额外倍率': ve['额外倍率'],
            '减抗': ve['减抗'],
            '减防': 0
        },
        'Q':  {
            '暴击率': vq['暴击率'],
            '暴击伤害': 0,
            '增伤':  vq['增伤'],
            '额外倍率': 0,
            '减抗': vq['减抗'],
            '减防': 0
        },
    }
    dmt = {
        '攻击力': info.prop.attack,
        '生命值': info.prop.health,
        '防御力': info.prop.defense,
    }
    for name, num in dm.items():
        skill_name = name.split(':')[1]
        skill_type = name.split(':')[0]
        if skill_type == 'B':
            if skill_name == 'd':
                for d in num:
                    if d not in info.damage_describe:
                        info.damage_describe.insert(0, d)
            else:
                para = skill_name.split('-')
                if (para[0].startswith('c') and len(info.constellation) >= int(para[0][1])) or (para[0].startswith('l') and info.level >= int(para[0][1:])):
                    if para[1] in ['攻击力', '生命值', '防御力']:
                        dmt[para[1]] += num[0]
                    else:
                        if para[2] == '*':
                            for k in v:
                                v[k][para[1]] += num[0]
                        else:
                            v[para[2]][para[1]] += num[0]
                    if len(num) > 1 and num[1] not in info.damage_describe:
                        info.damage_describe.insert(0, num[1])
        elif skill_type == 'T':
            dmg_data[skill_name] = (str(num), )
        else:
            r = 1  # 反应系数
            j = 0  # 激化反应系数
            n = '1'  # 段数
            e = '物理'  # 伤害元素类型序号
            t = '攻击力'  # 倍率区类型
            para = skill_type.split('-')
            skill_type = para[0]
            if len(para) != 1:
                for p in para[1:]:
                    if p.startswith('r'):
                        r = growth_reaction(info.prop.elemental_mastery, float(p[3:]), info.prop.reaction_coefficient[f'{p[1:3]}'])
                    if p.startswith('j'):
                        j = intensify_reaction(info.level, p[1:], info.prop.elemental_mastery, info.prop.reaction_coefficient['激化'])
                    if p.startswith('n'):
                        n = p[1:]
                    if p.startswith('e'):
                        e = p[1:]
                    if p.startswith('t'):
                        t = p[1:]
            if isinstance(num, tuple):
                n1 = udc(num[0] * dmt[t] + v[skill_type]['额外倍率'] + j, (info.prop.crit_rate + v[skill_type]['暴击率'], info.prop.crit_damage + v[skill_type]['暴击伤害']), info.prop.dmg_bonus[e] + v[skill_type]['增伤'], info.level, r=r, rcd=v[skill_type]['减抗'], dcr=v[skill_type]['减防'])
                n2 = udc(num[1] * dmt[t] + v[skill_type]['额外倍率'] + j, (info.prop.crit_rate + v[skill_type]['暴击率'], info.prop.crit_damage + v[skill_type]['暴击伤害']), info.prop.dmg_bonus[e] + v[skill_type]['增伤'], info.level, r=r, rcd=v[skill_type]['减抗'], dcr=v[skill_type]['减防'])
                dmg_data[skill_name] = (n1[0] + '+' + n2[0], n1[1] + '+' + n2[1])
            else:
                if n == '1':
                    dmg_data[skill_name] = udc(num * dmt[t] + v[skill_type]['额外倍率'] + j, (info.prop.crit_rate + v[skill_type]['暴击率'], info.prop.crit_damage + v[skill_type]['暴击伤害']), info.prop.dmg_bonus[e] + v[skill_type]['增伤'], info.level, r=r, rcd=v[skill_type]['减抗'], dcr=v[skill_type]['减防'])
                else:
                    dmg = udc(num * dmt[t] + v[skill_type]['额外倍率'] + j, (info.prop.crit_rate + v[skill_type]['暴击率'], info.prop.crit_damage + v[skill_type]['暴击伤害']), info.prop.dmg_bonus[e] + v[skill_type]['增伤'], info.level, r=r, rcd=v[skill_type]['减抗'], dcr=v[skill_type]['减防'])
                    dmg_data[skill_name] = (dmg[0] + '*' + n, dmg[1] + '*' + n)
    return dmg_data
