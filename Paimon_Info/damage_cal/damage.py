from copy import deepcopy
from pathlib import Path

from littlepaimon_utils.files import load_json
from .common import common_fix, draw_dmg_pic, udc, get_damage_multipiler, growth_reaction


all_skill_data = load_json(path=Path(__file__).parent.parent.parent / 'utils' / 'json_data' / 'roles_data.json')


def get_role_dmg(data: dict):
    dm = get_damage_multipiler(data)
    if not dm:
        return None
    dmg_data = {}
    data, vq, ve, va = common_fix(deepcopy(data))
    level_role = data['等级']
    attack = data['属性']['基础攻击'] + data['属性']['额外攻击']
    health = data['属性']['基础生命'] + data['属性']['额外生命']
    defense = data['属性']['基础防御'] + data['属性']['额外防御']
    cr = data['属性']['暴击率']
    cd = data['属性']['暴击伤害']
    db = data['属性']['伤害加成']
    cons = len(data['命座'])
    # 物理, 火, 雷, 水, 草, 风, 岩, 冰
    if data['名称'] == '钟离':
        data['伤害描述'].insert(0, '护盾减抗')
        dmg_data['玉璋护盾'] = (str(int((health * dm['玉璋护盾'][0] + dm['玉璋护盾'][1]) * (1 + data['属性']['护盾强效']))),)
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
    elif data['名称'] == '胡桃':
        data['伤害描述'].insert(0, '半血以下')
        zf = growth_reaction(data['属性']['元素精通'], 1.5) if '蒸发系数' not in data['属性'] else growth_reaction(
            data['属性']['元素精通'], 1.5, data['属性']['蒸发系数'])
        attack += dm['攻击力提高'] * health
        db[1] += 0.33 if level_role >= 70 else 0
        dmg_data['裸重击'] = udc(dm['重击'] * attack, (cr + va['重击暴击率'], cd), db[1] + va['重击增伤'], level_role)
        dmg_data['重击蒸发'] = udc(dm['重击'] * attack, (cr + va['重击暴击率'], cd), db[1] + va['重击增伤'], level_role, r=zf)
        dmg_data['雪梅香蒸发'] = udc(dm['雪梅香'] * attack + ((health * 0.1) if cons >= 2 else 0), (cr + ve['暴击率'], cd),
                                db[1] + ve['增伤'], level_role, r=zf)
        dmg_data['大招蒸发'] = udc(dm['大招'] * attack, (cr + vq['暴击率'], cd),
                               db[1] + vq['增伤'], level_role, r=zf)
    elif data['名称'] == '香菱':
        zf = growth_reaction(data['属性']['元素精通'], 1.5) if '蒸发系数' not in data['属性'] else growth_reaction(
            data['属性']['元素精通'], 1.5, data['属性']['蒸发系数'])
        rcd = 0.15 if cons >= 1 else 0
        dmg_data['锅巴喷火'] = udc(dm['锅巴喷火'] * attack, (cr + ve['暴击率'], cd), db[1] + ve['增伤'], level_role, rcd=rcd)
        dmg_data['旋火轮'] = udc(dm['旋火轮'] * attack, (cr + vq['暴击率'], cd), db[1] + vq['增伤'], level_role, rcd=rcd)
        dmg_data['旋火轮蒸发'] = udc(dm['旋火轮'] * attack, (cr + vq['暴击率'], cd), db[1] + vq['增伤'], level_role, rcd=rcd, r=zf)
    elif data['名称'] == '魈':
        va['下落攻击增伤'] += dm['靖妖傩舞']
        dmg_data = get_dmg_data(dm, attack, cr, cd, db[5], level_role, va, ve, vq)
    elif data['名称'] == '申鹤':
        dmg_data['冰翎加成'] = str(int(dm['冰翎'] * attack))
        db[-1] += 0.15 if level_role >= 40 else 0
        vq['增伤'] += 0.15 if level_role >= 70 else 0
        dmg_data['战技长按'] = udc(dm['e长按'] * attack, (cr + ve['暴击率'], cd), db[-1] + ve['增伤'], level_role, rcd=dm['大招减抗'])
        dmg_data['大招持续伤害'] = udc(dm['大招持续'] * attack, (cr + vq['暴击率'], cd), db[-1] + vq['增伤'], level_role,
                                 rcd=dm['大招减抗'])
    elif data['名称'] == '八重神子':
        ve['增伤'] += (data['属性']['元素精通'] * 0.0015) if level_role >= 70 else 0
        db[2] += 0.2 if cons >= 4 else 0
        dci = 0.6 if cons >= 6 else 0
        dmg_data['重击'] = udc(dm['重击'] * attack, (cr + va['重击暴击率'], cd), db[2] + va['重击增伤'], level_role)
        dmg_data['杀生樱满阶'] = udc(dm['杀生樱'] * attack, (cr + ve['暴击率'], cd), db[2] + ve['增伤'], level_role, dci=dci)
        dmg_data['天狐霆雷'] = udc(dm['天狐霆雷'] * attack, (cr + vq['暴击率'], cd), db[2] + vq['增伤'], level_role)
    elif data['名称'] == '刻晴':
        cr += 0.15 if level_role >= 70 else 0
        if cons == 6:
            db[2] += 0.24
            data['伤害描述'].insert(0, '六命满层')
        if cons >= 4:
            attack += data['属性']['基础攻击'] * 0.25
            data['伤害描述'].insert(0, '四命触发')
        dmg_data = get_dmg_data(dm, attack, cr, cd, db[2], level_role, va, ve, vq)
    elif data['名称'] == '阿贝多':
        dmg_data['阳华绽放'] = udc(dm['阳华绽放'] * defense + ve['额外倍率'], (cr + ve['暴击率'], cd), db[6] + ve['增伤'], level_role)
        dmg_data['大招首段'] = udc(dm['大招首段'] * attack, (cr + vq['暴击率'], cd), db[6] + vq['增伤'], level_role)
    elif data['名称'] == '神里绫华':
        va['重击增伤'] += 0.3 if level_role >= 40 else 0
        db[-1] += 0.18 if level_role >= 70 else 0
        dcr = 0.3 if cons >= 4 else 0
        if cons == 6:
            data['伤害描述'].insert(0, '满命触发')
            va['重击增伤'] += 2.98
        a = udc(dm['重击'] * attack + va['重击额外倍率'], (cr + va['重击暴击率'], cd), db[-1] + va['重击增伤'], level_role, dcr=dcr)
        dmg_data['重击'] = (a[0] + '*3', a[1] + '*3')
        dmg_data['冰华伤害'] = udc(dm['冰华伤害'] * attack + ve['额外倍率'], (cr + ve['暴击率'], cd), db[-1] + ve['增伤'], level_role, dcr=dcr)
        dmg_data['霜灭每段'] = udc(dm['霜灭每段'] * attack, (cr + vq['暴击率'], cd), db[-1] + vq['增伤'], level_role, dcr=dcr)
    elif data['名称'] == '行秋':
        db[3] += 0.2 if level_role >= 70 else 0
        rcd = 0.15 if cons >= 2 else 0
        dme1 = dm['画雨笼山'][0] * (1.5 if cons >= 4 else 1)
        dme2 = dm['画雨笼山'][1] * (1.5 if cons >= 4 else 1)
        e1 = udc(dme1 * attack + ve['额外倍率'], (cr + ve['暴击率'], cd), db[3] + ve['增伤'], level_role, rcd=rcd)
        e2 = udc(dme2 * attack + ve['额外倍率'], (cr + ve['暴击率'], cd), db[3] + ve['增伤'], level_role, rcd=rcd)
        dmg_data['画雨笼山'] = (e1[0] + '+' + e2[0], e1[1] + '+' + e2[1])
        dmg_data['裁雨留虹每段'] = udc(dm['裁雨留虹每段'] * attack, (cr + vq['暴击率'], cd), db[3] + vq['增伤'], level_role, rcd=rcd)
    elif data['名称'] == '夜兰':
        data['伤害描述'].insert(0, '不计算天赋增伤')
        if level_role >= 40:
            health += data['属性']['基础生命'] * 0.18
            data['伤害描述'].insert(0, '天赋按3元素')
        dmg_data['破局矢'] = udc(dm['破局矢'] * health, (cr + va['重击暴击率'], cd), db[3] + va['重击增伤'], level_role)
        dmg_data['元素战技'] = udc(dm['元素战技'] * health, (cr + ve['暴击率'], cd), db[3] + ve['增伤'], level_role)
        q = udc(dm['大招每段'] * health, (cr + vq['暴击率'], cd), db[3] + vq['增伤'], level_role)
        if cons >= 2:
            q2 = udc(0.14 * health, (cr + vq['暴击率'], cd), db[3] + vq['增伤'], level_role)
            dmg_data['大招每段'] = (q[0] + '*3+' + q2[0], q[1] + '*3+' + q2[1])
        else:
            dmg_data['大招每段'] = (q[0] + '*3', q[1] + '*3')
    elif data['名称'] == '甘雨':
        rh = growth_reaction(data['属性']['元素精通'], 1.5) if '融化系数' not in data['属性'] else growth_reaction(
            data['属性']['元素精通'], 1.5, data['属性']['融化系数'])
        va['重击暴击率'] += 0.2 if level_role >= 40 else 0
        if level_role >= 70:
            va['重击增伤'] += 0.2
            ve['增伤'] += 0.2
        if cons >= 4:
            db[-1] += 0.25
            data['伤害描述'].insert(0, '四命满层')
        rcd = 0.15 if cons >= 1 else 0
        a1 = udc(dm['霜华矢'][0] * attack, (cr + va['重击暴击率'], cd), db[-1] + va['重击增伤'], level_role, rcd=rcd)
        a2 = udc(dm['霜华矢'][1] * attack, (cr + va['重击暴击率'], cd), db[-1] + va['重击增伤'], level_role, rcd=rcd)
        dmg_data['霜华矢'] = (a1[0] + '+' + a2[0], a1[1] + '+' + a2[1])
        a1 = udc(dm['霜华矢'][0] * attack, (cr + va['重击暴击率'], cd), db[-1] + va['重击增伤'], level_role, rcd=rcd, r=rh)
        a2 = udc(dm['霜华矢'][1] * attack, (cr + va['重击暴击率'], cd), db[-1] + va['重击增伤'], level_role, rcd=rcd, r=rh)
        dmg_data['霜华矢融化'] = (a1[0] + '+' + a2[0], a1[1] + '+' + a2[1])
        dmg_data['元素战技'] = udc(dm['元素战技'] * attack, (cr + ve['暴击率'], cd), db[-1] + ve['增伤'], level_role, rcd=rcd)
        dmg_data['冰棱伤害'] = udc(dm['冰棱伤害'] * attack, (cr + vq['暴击率'], cd), db[-1] + vq['增伤'], level_role, rcd=rcd)
    if data['伤害描述']:
        dmg_data['额外说明'] = ('，'.join(data['伤害描述']),)
    return draw_dmg_pic(dmg_data) if dmg_data else None


def get_dmg_data(dm, attack, cr, cd, db, level_role, va, ve, vq):
    dmg_data = {}
    v = {'A': {
        '暴击率': va['普攻暴击率'],
        '增伤':  va['普攻增伤'],
        '额外倍率': va['普攻额外倍率']
    },
        'AZ': {
            '暴击率': va['重击暴击率'],
            '增伤':  va['重击增伤'],
            '额外倍率': va['重击额外倍率']
        },
        'AX': {
            '暴击率': va['下落攻击暴击率'],
            '增伤':  va['下落攻击增伤'],
            '额外倍率': va['下落攻击额外倍率']
        },
        'E':  {
            '暴击率': ve['暴击率'],
            '增伤':  ve['增伤'],
            '额外倍率': ve['额外倍率']
        },
        'Q':  {
            '暴击率': vq['暴击率'],
            '增伤':  vq['增伤'],
            '额外倍率': 0
        },
    }
    for name, num in dm.items():
        skill_name = name.split(':')[1]
        skill_type = name.split(':')[0]
        if skill_type == 'B':
            continue
        if isinstance(num, tuple):
            n1 = udc(num[0] * attack + v[skill_type]['额外倍率'], (cr + v[skill_type]['暴击率'], cd), db + v[skill_type]['增伤'], level_role)
            n2 = udc(num[1] * attack + v[skill_type]['额外倍率'], (cr + v[skill_type]['暴击率'], cd), db + v[skill_type]['增伤'], level_role)
            dmg_data[skill_name] = (n1[0] + '+' + n2[0], n1[1] + '+' + n2[1])
        else:
            dmg_data[skill_name] = udc(num * attack + v[skill_type]['额外倍率'], (cr + v[skill_type]['暴击率'], cd), db + v[skill_type]['增伤'], level_role)
    return dmg_data
