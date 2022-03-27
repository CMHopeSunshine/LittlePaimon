import requests, json,re
from hoshino import R,MessageSegment
from hoshino.typing import CQEvent, Message
from hoshino.util import PriFreqLimiter
import hoshino
from ..util import Dict
from hoshino import aiorequests
from .gacha_role import *
from .gacha_wish import more_ten

lmt = PriFreqLimiter(60)
sv=hoshino.Service('原神模拟抽卡')
#activity = 301  限定卡池
#activity2 = 400  限定卡池2
#weapon = 302  武器卡池
#permanent = 200  常驻卡池


@sv.on_rex(r'^抽((?P<num>\d+)|(?:.*))十连(?P<pool>.*?)$')
async def gacha(bot, ev):
    gid = ev.group_id
    uid = ev.user_id
    init_user_info(uid)
    sd = ev.sender
    num = ev['match'].group('num')
    pool = ev['match'].group('pool')
    if num:
        if num.isdigit():
            num = int(num)
            if num > 5:
                await bot.send(ev, '最多只能同时5十连哦', at_sender=True)
                return
        else:
            num = 1
    else:
        num = 1
    if not pool: 
        pool = '角色1'
    gacha_type = gacha_type_by_name(pool)
    if gacha_type == 0:
        await bot.finish(ev, '卡池名称出错,请选择角色1|角色2|武器|常驻', at_sender=True)
        return
    if ev.message_type == 'group':
        if not lmt.check(gid,uid):
            await bot.finish(ev, f'模拟抽卡冷却中(剩余{int(lmt.left_time(gid,uid)) + 1}秒)', at_sender=True)
            return
        lmt.start_cd(gid,uid,60)
    if num >= 3:
        await bot.send(ev, '抽卡图正在生成中，请稍候')
    if isinstance(gacha_type,int):
        data = await gacha_info_list()
        f = lambda x: x.gacha_type == gacha_type
        gacha_data = sorted(list(filter(f, data)), key=lambda x: x.end_time)[-1]
        gacha_id = gacha_data.gacha_id
        gacha_data = await gacha_info(gacha_id)
    else:
        gacha_data = globals()[gacha_type]
    img = await more_ten(uid,gacha_data, num, sd)
    save_user_info()
    await bot.send(ev, MessageSegment.image(img), at_sender=True)

@sv.on_prefix('模拟抽卡记录')
async def gacharecord(bot, ev):
    uid = ev.user_id
    init_user_info(uid)
    if user_info[uid]['gacha_list']['wish_total'] == 0:
        await bot.send(ev,'你此前并没有抽过卡哦',at_sender=True)
        return
    msg = ev.message.extract_plain_text().strip()
    if msg == '角色' or msg == '武器':
        res = await getrwrecord(msg,uid)
    else:
        data = user_info[uid]['gacha_list']
        res = '你的模拟抽卡记录如下:\n'
        res += '你在本频道总共抽卡{%s}次\n其中五星共{%s}个,四星共{%s}个\n' % (user_info[uid]['gacha_list']['wish_total'],user_info[uid]['gacha_list']['wish_5'],user_info[uid]['gacha_list']['wish_4'])
        try:
            t5 = '{:.2f}%'.format(data['wish_5']/(data['wish_total']-data['gacha_5_role']-data['gacha_5_weapon']-data['gacha_5_permanent'])*100)
        except:
            t5 = '0.00%'
        try:
            u5 = '{:.2f}%'.format(data['wish_5_up']/data['wish_5']*100)
        except:
            u5 = '0.00%'
        try:
            t4 = '{:.2f}%'.format(data['wish_4']/(data['wish_total']-data['gacha_4_role']-data['gacha_4_weapon']-data['gacha_4_permanent'])*100)
        except:
            t4 = '0.00%'
        try:
            u4 = '{:.2f}%'.format(data['wish_4_up']/data['wish_4']*100)
        except:
            u4 = '0.00%'
        dg_name = data['dg_name'] if data['dg_name'] != '' else '未定轨'
        res += '五星出货率为{%s} up率为{%s}\n四星出货率为{%s} up率为{%s}\n' %(t5,u5,t4,u4)
        res += '·|角色池|·\n目前{%s}抽未出五星 {%s}抽未出四星\n下次五星是否up:{%s}\n' % (data['gacha_5_role'],data['gacha_4_role'],data['is_up_5_role'])
        res += '·|武器池|·\n目前{%s}抽未出五星 {%s}抽未出四星\n下次五星是否up:{%s}\n' % (data['gacha_5_weapon'],data['gacha_4_weapon'],data['is_up_5_weapon'])
        res += '定轨武器为{%s},能量值为{%s}\n' % (dg_name,data['dg_time'])
        res += '·|常驻池|·\n目前{%s}抽未出五星 {%s}抽未出四星\n' % (data['gacha_5_permanent'],data['gacha_4_permanent'])
    await bot.send(ev,res,at_sender=True)

async def getrwrecord(msg,uid):
    if msg == '角色':
        if not len(user_info[uid]['role_list']):
            res = '你还没有角色'
        else:
            res = '你所拥有的角色如下:\n'
            for role in user_info[uid]['role_list'].items():
                if len(role[1]['星级']) == 5:
                    res += '%s%s 数量: %s 出货: %s\n' % (role[1]['星级'],role[0],role[1]['数量'],role[1]['出货'])
                else:
                    res += '%s%s 数量: %s\n' % (role[1]['星级'],role[0],role[1]['数量'])
    else:
        if not len(user_info[uid]['weapon_list']):
            res = '你还没有武器'
        else:
            res = '你所拥有的武器如下:\n'
            for wp in user_info[uid]['weapon_list'].items():
                if len(wp[1]['星级']) == 5:
                    res += '%s%s 数量: %s 出货: %s\n' % (wp[1]['星级'],wp[0],wp[1]['数量'],wp[1]['出货'])
                else:
                    res += '%s%s 数量: %s\n' % (wp[1]['星级'],wp[0],wp[1]['数量'])
    res = res.replace('[','')
    res = res.replace(']','')
    res = res.replace(',',' ')
    return res

@sv.on_fullmatch('删除模拟抽卡记录')
async def deleterecord(bot,ev):
    uid = ev.user_id
    init_user_info(uid)
    try:
        del user_info[uid]
        save_user_info()
        await bot.send(ev,'你的抽卡记录删除成功',at_sender=True)
    except:
        await bot.send(ev,'你的抽卡记录删除失败',at_sender=True)

@sv.on_prefix('选择定轨')
async def choosedg(bot,ev):
    uid = ev.user_id
    init_user_info(uid)
    dg_weapon = ev.message.extract_plain_text().strip()
    weapon_up_list = await getdg_weapon()
    if dg_weapon not in weapon_up_list:
        await bot.send(ev,f'该武器无定轨，请输入全称[{weapon_up_list[0]}|{weapon_up_list[1]}]',at_sender=True)
    else:
        if dg_weapon == user_info[uid]['gacha_list']['dg_name']:
            await bot.send(ev,'你当前已经定轨该武器，无需更改')
        else:
            user_info[uid]['gacha_list']['dg_name'] = dg_weapon
            user_info[uid]['gacha_list']['dg_time'] = 0
            await bot.send(ev,f'定轨成功，定轨能量值已重置，当前定轨武器为：{dg_weapon}')
    save_user_info()

@sv.on_fullmatch('删除定轨')
async def deletedg(bot,ev):
    uid = ev.user_id
    init_user_info(uid)
    if user_info[uid]['gacha_list']['dg_name'] == '':
        await bot.send(ev,'你此前并没有定轨记录哦',at_sender=True)
    else:
        user_info[uid]['gacha_list']['dg_name'] = ''
        user_info[uid]['gacha_list']['dg_time'] = 0
        save_user_info()
        await bot.send(ev,'你的定轨记录删除成功',at_sender=True)

@sv.on_fullmatch('查看定轨')
async def deletedg(bot,ev):
    uid = ev.user_id
    init_user_info(uid)
    weapon_up_list = await getdg_weapon()
    dg_weapon = user_info[uid]['gacha_list']['dg_name']
    dg_time = user_info[uid]['gacha_list']['dg_time']
    if dg_weapon == '':
        await bot.send(ev,f'你当前未定轨武器，可定轨武器有 {weapon_up_list[0]}|{weapon_up_list[1]} ，请使用[选择定轨 武器全称]来进行定轨',at_sender=True)
    else:
        await bot.send(ev,f'你当前定轨的武器为 {dg_weapon} ，能量值为 {dg_time}',at_sender=True)

async def getdg_weapon():
    weapon_up_list = []
    data = await gacha_info_list()
    f = lambda x: x.gacha_type == 302
    gacha_data = sorted(list(filter(f, data)), key=lambda x: x.end_time)[-1]
    gacha_id = gacha_data.gacha_id
    gacha_data = await gacha_info(gacha_id)
    for weapon in gacha_data['r5_up_items']:
        weapon_up_list.append(weapon['item_name'])
    return weapon_up_list

def gacha_type_by_name(gacha_type):
    # if re.match(r'^角色1|限定1|角色2|限定2(?:池)$', gacha_type):
        # return 301
    if re.match(r'^角色1|限定1(?:池)$', gacha_type):
        return 301
    if re.match(r'^角色2|限定2(?:池)$', gacha_type):
        return 400
    if re.match(r'^武器|武器池$', gacha_type):
        return 302
    if re.match(r'^常驻|普(?:池)$', gacha_type):
        return 200
    # if re.match(r'^新角色|新限定(?:池)$', gacha_type):
    #     return 'role_1_pool'
    if re.match(r'^彩蛋池?$', gacha_type):
        return 'all_star'
    if re.match(r'^新角色1|新限定1(?:池)$', gacha_type):
        return 'role_1_pool'
    if re.match(r'^新角色2|新限定2(?:池)$', gacha_type):
        return 'role_2_pool'
    if re.match(r'^新武器|新武器池$', gacha_type):
        return 'weapon_pool'
    return 0


BASE_URL = 'https://webstatic.mihoyo.com/hk4e/gacha_info/cn_gf01/%s'


async def gacha_info_list():
    res = await aiorequests.get(BASE_URL % 'gacha/list.json')
    json_data = await res.json(object_hook=Dict)

    if json_data.retcode != 0:
        raise Exception(json_data.message)

    return json_data.data.list


async def gacha_info(gacha_id):
    res = await aiorequests.get(BASE_URL % gacha_id + '/zh-cn.json')

    if res.status_code != 200:
        raise Exception("error gacha_id: %s" % gacha_id)

    return await res.json(object_hook=Dict)
