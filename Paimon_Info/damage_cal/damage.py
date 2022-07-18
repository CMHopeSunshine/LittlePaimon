from copy import deepcopy
from pathlib import Path

from littlepaimon_utils.files import load_json
from .common import common_fix, draw_dmg_pic, udc, get_damage_multipiler, growth_reaction


all_skill_data = load_json(path=Path(__file__).parent.parent.parent / 'utils' / 'json_data' / 'roles_data.json')


def get_role_dmg(data: dict):
    dm = get_damage_multipiler(deepcopy(data))
    if not dm:
        return None
    dmg_data = {}
    data, vq, ve, va = common_fix(deepcopy(data))
    level_role = data['等级']
    attack = data['属性']['基础攻击'] + data['属性']['额外攻击']
    cr = data['属性']['暴击率']
    cd = data['属性']['暴击伤害']
    db = data['属性']['伤害加成']
    cons = len(data['命座'])
    # 物理, 火, 雷, 水, 草, 风, 岩, 冰
    if data['名称'] == '钟离':
        health = data['属性']['基础生命'] + data['属性']['额外生命']
        data['伤害描述'].insert(0, '护盾减抗')
        dmg_data['玉璋护盾'] = (str(int((health * dm['玉璋护盾'][0] + dm['玉璋护盾'][1]) * (1 + data['属性']['护盾强效']) * 1.5)),)
        dmg_data['原岩共鸣'] = udc(dm['原岩共鸣'] * attack + (health * 0.019) if level_role >= 70 else 0, (cr + ve['暴击率'], cd),
                               db[6] + ve['增伤'], level_role, rcd=0.2)
        dmg_data['天星伤害'] = udc(dm['天星'] * attack + (health * 0.33) if level_role >= 70 else 0, (cr + vq['暴击率'], cd),
                               db[6] + vq['增伤'], level_role, rcd=0.2)
        a = udc(dm['踢枪'] * attack + (health * 0.0139) if level_role >= 70 else 0, (cr + va['普攻暴击率'], cd),
                db[0] + va['普攻增伤'], level_role, rcd=0.2)
        if data['武器']['名称'] == '流月针':
            ly = udc((0.15 + 0.05 * data['武器']['精炼等级']) * attack, (cr, cd), db[0], level_role, rcd=0.2)
            a[0] += '+' + ly[0]
            a[1] += '+' + ly[1]
        dmg_data['踢枪伤害'] = a
    elif data['名称'] == '雷电将军':
        data['伤害描述'].insert(0, '满愿力')
        vq['增伤'] += dm['e增伤']
        dci = 0.6 if cons >= 2 else 0
        dmg_data['协同攻击'] = udc(dm['协同攻击'] * attack, (cr + ve['暴击率'], cd), db[2] + ve['增伤'], level_role, dci=dci)
        dmg_data['梦想一刀'] = udc((dm['梦想一刀基础'] + dm['梦想一刀愿力']) * attack, (cr + vq['暴击率'], cd), db[2] + vq['增伤'],
                               level_role, dci=dci)
        a1 = udc((dm['梦想一心重击基础'][0] + dm['梦想一心愿力']) * attack, (cr + vq['暴击率'], cd), db[2] + vq['增伤'], level_role,
                 dci=dci)
        a2 = udc((dm['梦想一心重击基础'][1] + dm['梦想一心愿力']) * attack, (cr + vq['暴击率'], cd), db[2] + vq['增伤'], level_role,
                 dci=dci)
        dmg_data['梦想一心重击'] = (a1[0] + '+' + a2[0], a1[1] + '+' + a2[1])
        extra_energy = (data['属性']['元素充能效率'] - 1) * 0.6 if level_role >= 70 else 0
        dmg_data['梦想一心能量'] = (str(round(dm['梦想一心能量'] * (1 + extra_energy) * 5, 1)),)
    elif data['名称'] == '申鹤':
        dmg_data['冰翎加成'] = (str(int(dm['冰翎'] * attack)),)
        db[-1] += 0.15 if level_role >= 40 else 0
        vq['增伤'] += 0.15 if level_role >= 70 else 0
        dmg_data['战技长按'] = udc(dm['e长按'] * attack, (cr + ve['暴击率'], cd), db[-1] + ve['增伤'], level_role, rcd=dm['大招减抗'])
        dmg_data['大招持续伤害'] = udc(dm['大招持续'] * attack, (cr + vq['暴击率'], cd), db[-1] + vq['增伤'], level_role,
                                 rcd=dm['大招减抗'])
    elif data['名称'] == '珊瑚宫心海':
        health = data['属性']['基础生命'] + data['属性']['额外生命']
        adb = 0.15 * data['属性']['治疗加成'] if level_role >= 70 else 0
        if cons >= 6:
            db[3] += 0.4
            data['伤害描述'].insert(0, '六命触发')
        ab = udc(dm['普攻第一段'] * attack, (cr + va['普攻暴击率'], cd), db[3] + va['普攻增伤'], level_role)
        aq = udc(dm['普攻伤害提升'] * health, (cr + va['普攻暴击率'], cd), db[3] + adb + va['普攻增伤'], level_role)
        if len(ab) == 1:
            dmg_data['开大普攻第一段'] = (str(int(ab[0]) + int(aq[0])), )
        else:
            dmg_data['开大普攻第一段'] = (str(int(ab[0]) + int(aq[0])), str(int(ab[1]) + int(aq[1])))
        dmg_data['开大战技伤害'] = udc(dm['水母伤害'] * attack + dm['E伤害提升'] * health, (cr + ve['暴击率'], cd), db[3] + ve['增伤'], level_role)
        dmg_data['大招释放伤害'] = udc(dm['大招伤害'] * health, (cr + vq['暴击率'], cd), db[3] + vq['增伤'], level_role)
        dmg_data['开大普攻治疗量'] = (str(int((float(dm['大招治疗量'][0].replace('%生命值上限', '')) / 100.0 * health + float(dm['大招治疗量'][1]) * (1 + data['属性']['治疗加成'])))),)
        dmg_data['战技治疗量'] = (str(int((float(dm['水母治疗量'][0].replace('%生命值上限', '')) / 100.0 * health + float(dm['水母治疗量'][1]) * (1 + data['属性']['治疗加成'])))),)
    else:
        dmg_data = get_dmg_data(data, dm, va, ve, vq)
    if data['伤害描述']:
        dmg_data['额外说明'] = ('，'.join(data['伤害描述']),)
    return draw_dmg_pic(dmg_data) if dmg_data else None


def get_dmg_data(data, dm, va, ve, vq):
    dmg_data = {}
    element_type = ['物理', '火', '雷', '水', '草', '风', '岩', '冰']
    v = {'A': {
            '暴击率': va['普攻暴击率'],
            '暴击伤害': 0,
            '增伤':  va['普攻增伤'],
            '额外倍率': va['普攻额外倍率'],
            '减抗': 0,
            '减防': 0
        },
        'AZ': {
            '暴击率': va['重击暴击率'],
            '暴击伤害': 0,
            '增伤':  va['重击增伤'],
            '额外倍率': va['重击额外倍率'],
            '减抗': 0,
            '减防': 0
        },
        'AX': {
            '暴击率': va['下落攻击暴击率'],
            '暴击伤害': 0,
            '增伤':  va['下落攻击增伤'],
            '额外倍率': va['下落攻击额外倍率'],
            '减抗': 0,
            '减防': 0
        },
        'E':  {
            '暴击率': ve['暴击率'],
            '暴击伤害': 0,
            '增伤':  ve['增伤'],
            '额外倍率': ve['额外倍率'],
            '减抗': 0,
            '减防': 0
        },
        'Q':  {
            '暴击率': vq['暴击率'],
            '暴击伤害': 0,
            '增伤':  vq['增伤'],
            '额外倍率': 0,
            '减抗': 0,
            '减防': 0
        },
    }
    dmt = {
        '攻击力': data['属性']['基础攻击'] + data['属性']['额外攻击'],
        '生命值': data['属性']['基础生命'] + data['属性']['额外生命'],
        '防御力': data['属性']['基础防御'] + data['属性']['额外防御']
    }
    cr = data['属性']['暴击率']
    cd = data['属性']['暴击伤害']
    db = data['属性']['伤害加成']
    cons = len(data['命座'])
    level_role = data['等级']
    for name, num in dm.items():
        skill_name = name.split(':')[1]
        skill_type = name.split(':')[0]
        if skill_type == 'B':
            if skill_name == 'd':
                for d in num:
                    if d not in data['伤害描述']:
                        data['伤害描述'].insert(0, d)
            else:
                para = skill_name.split('-')
                if (para[0].startswith('c') and cons >= int(para[0][1])) or (para[0].startswith('l') and level_role >= int(para[0][1:])):
                    if para[1] in ['攻击力', '生命值', '防御力']:
                        dmt[para[1]] += num[0]
                    else:
                        if para[2] == '*':
                            for k in v:
                                v[k][para[1]] += num[0]
                        else:
                            v[para[2]][para[1]] += num[0]
                    if len(num) > 1 and num[1] not in data['伤害描述']:
                        data['伤害描述'].insert(0, num[1])
        elif skill_type == 'T':
            dmg_data[skill_name] = (str(num), )
        else:
            r = 1  # 反应系数
            n = '1'  # 段数
            e = 0  # 伤害元素类型序号
            t = '攻击力'  # 倍率区类型
            para = skill_type.split('-')
            skill_type = para[0]
            if len(para) != 1:
                for p in para[1:]:
                    if p.startswith('r'):
                        r = growth_reaction(data['属性']['元素精通'], float(p[3:])) if f'{p[1:3]}系数' not in data['属性'] else growth_reaction(
                            data['属性']['元素精通'], float(p[3:]), data['属性'][f'{p[1:3]}系数'])
                    if p.startswith('n'):
                        n = p[1:]
                    if p.startswith('e'):
                        e = element_type.index(p[1:])
                    if p.startswith('t'):
                        t = p[1:]
            if isinstance(num, tuple):
                n1 = udc(num[0] * dmt[t] + v[skill_type]['额外倍率'], (cr + v[skill_type]['暴击率'], cd + v[skill_type]['暴击伤害']), db[e] + v[skill_type]['增伤'], level_role, r=r, rcd=v[skill_type]['减抗'], dcr=v[skill_type]['减防'])
                n2 = udc(num[1] * dmt[t] + v[skill_type]['额外倍率'], (cr + v[skill_type]['暴击率'], cd + v[skill_type]['暴击伤害']), db[e] + v[skill_type]['增伤'], level_role, r=r, rcd=v[skill_type]['减抗'], dcr=v[skill_type]['减防'])
                dmg_data[skill_name] = (n1[0] + '+' + n2[0], n1[1] + '+' + n2[1])
            else:
                if n == '1':
                    dmg_data[skill_name] = udc(num * dmt[t] + v[skill_type]['额外倍率'], (cr + v[skill_type]['暴击率'], cd + v[skill_type]['暴击伤害']), db[e] + v[skill_type]['增伤'], level_role, r=r, rcd=v[skill_type]['减抗'], dcr=v[skill_type]['减防'])
                else:
                    dmg = udc(num * dmt[t] + v[skill_type]['额外倍率'], (cr + v[skill_type]['暴击率'], cd + v[skill_type]['暴击伤害']), db[e] + v[skill_type]['增伤'], level_role, r=r, rcd=v[skill_type]['减抗'], dcr=v[skill_type]['减防'])
                    dmg_data[skill_name] = (dmg[0] + '*' + n, dmg[1] + '*' + n)
    return dmg_data
