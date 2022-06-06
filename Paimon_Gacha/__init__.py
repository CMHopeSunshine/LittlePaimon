import re
from typing import Dict, Union

from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, Message
from nonebot.params import RegexDict, CommandArg

from utils.config import config
from utils import aiorequests
from utils.auth_util import FreqLimiter
from .gacha_info import *
from .gacha_res import more_ten

__usage__ = '''
1.[抽n十连xx池]抽n次xx池的十连，最多同时5次
*池子和官方同步，有角色1|角色2|武器|常驻，默认为角色1
2.[模拟抽卡记录]查看模拟抽卡记录总结
3.[模拟抽卡记录 角色/武器]查看模拟抽卡抽到的五星角色/武器
4.[删除模拟抽卡记录]顾名思义
5.[选择定轨 武器全名]选择武器定轨
6.[查看定轨]查看当前定轨的武器
7.[删除定轨]删除当前定轨的武器
'''
__help_version__ = '1.0.1'

sim_gacha = on_regex(r'^抽((?P<num>\d+)|(?:.*))十连(?P<pool>.*?)$', priority=5, block=True)
show_log = on_command('模拟抽卡记录', aliases={'查看模拟抽卡记录'}, priority=5, block=True)
delete_log = on_command('删除模拟抽卡记录', priority=5, block=True)
show_dg = on_command('查看定轨', priority=5, block=True)
delete_dg = on_command('删除定轨', priority=5, block=True)
choose_dg = on_command('选择定轨', priority=5, block=True)

lmt_group = FreqLimiter(config.paimon_gacha_cd_group)
lmt_user = FreqLimiter(config.paimon_gacha_cd_user)


@sim_gacha.handle()
async def gacha(event: Union[MessageEvent, GroupMessageEvent], reGroup: Dict = RegexDict()):
    uid = str(event.user_id)
    init_user_info(uid)
    sender = event.sender
    num = reGroup['num']
    pool = reGroup['pool']
    if num:
        if num.isdigit():
            num = int(num)
            if num > 5:
                await sim_gacha.finish('最多只能同时5十连哦', at_sender=True)
        else:
            num = 1
    else:
        num = 1
    if not pool:
        pool = '角色1'
    gacha_type = gacha_type_by_name(pool)
    if gacha_type == 0:
        await sim_gacha.finish('卡池名称出错,请选择角色1|角色2|武器|常驻', at_sender=True)
    if event.message_type == 'group':
        if not lmt_group.check(event.group_id):
            await sim_gacha.finish(f'本群模拟抽卡冷却中(剩余{lmt_group.left_time(event.group_id)}秒)')
        else:
            lmt_group.start_cd(event.group_id, config.paimon_gacha_cd_group)
    if event.message_type != 'guild':
        if not lmt_user.check(event.user_id):
            await sim_gacha.finish(f'个人模拟抽卡冷却中(剩余{lmt_user.left_time(event.user_id)}秒)')
        else:
            lmt_user.start_cd(event.user_id, config.paimon_gacha_cd_user)
    if isinstance(gacha_type, int):
        data = await gacha_info_list()
        gacha_data = sorted(list(filter(lambda x: x['gacha_type'] == gacha_type, data)), key=lambda x: x['end_time'])[
            -1]
        gacha_id = gacha_data['gacha_id']
        gacha_data = await gacha_info(gacha_id)
    else:
        gacha_data = globals()[gacha_type]
    img = await more_ten(uid, gacha_data, num, sender)
    save_user_info()
    await sim_gacha.finish(img, at_sender=True)


@show_log.handle()
async def show_log_handler(event: MessageEvent, msg: Message = CommandArg()):
    uid = str(event.user_id)
    init_user_info(uid)
    # gacha_list = user_info[uid]['gacha_list']
    if user_info[uid]['gacha_list']['wish_total'] == 0:
        await show_log.finish('你此前并没有抽过卡哦', at_sender=True)
    msg = msg.extract_plain_text().strip()
    if msg == '角色' or msg == '武器':
        res = get_rw_record(msg, uid)
    else:
        data = user_info[uid]['gacha_list']
        res = '你的模拟抽卡记录如下:\n'
        res += '你在本频道总共抽卡{%s}次\n其中五星共{%s}个,四星共{%s}个\n' % (
            user_info[uid]['gacha_list']['wish_total'], user_info[uid]['gacha_list']['wish_5'],
            user_info[uid]['gacha_list']['wish_4'])
        try:
            t5 = '{:.2f}%'.format(data['wish_5'] / (
                    data['wish_total'] - data['gacha_5_role'] - data['gacha_5_weapon'] - data[
                'gacha_5_permanent']) * 100)
        except:
            t5 = '0.00%'
        try:
            u5 = '{:.2f}%'.format(data['wish_5_up'] / data['wish_5'] * 100)
        except:
            u5 = '0.00%'
        try:
            t4 = '{:.2f}%'.format(data['wish_4'] / (
                    data['wish_total'] - data['gacha_4_role'] - data['gacha_4_weapon'] - data[
                'gacha_4_permanent']) * 100)
        except:
            t4 = '0.00%'
        try:
            u4 = '{:.2f}%'.format(data['wish_4_up'] / data['wish_4'] * 100)
        except:
            u4 = '0.00%'
        dg_name = data['dg_name'] if data['dg_name'] != '' else '未定轨'
        res += '五星出货率为{%s} up率为{%s}\n四星出货率为{%s} up率为{%s}\n' % (t5, u5, t4, u4)
        res += '·|角色池|·\n目前{%s}抽未出五星 {%s}抽未出四星\n下次五星是否up:{%s}\n' % (
            data['gacha_5_role'], data['gacha_4_role'], data['is_up_5_role'])
        res += '·|武器池|·\n目前{%s}抽未出五星 {%s}抽未出四星\n下次五星是否up:{%s}\n' % (
            data['gacha_5_weapon'], data['gacha_4_weapon'], data['is_up_5_weapon'])
        res += '定轨武器为{%s},能量值为{%s}\n' % (dg_name, data['dg_time'])
        res += '·|常驻池|·\n目前{%s}抽未出五星 {%s}抽未出四星\n' % (data['gacha_5_permanent'], data['gacha_4_permanent'])
    await show_log.finish(res, at_sender=True)


def get_rw_record(msg, uid):
    if msg == '角色':
        if not len(user_info[uid]['role_list']):
            res = '你还没有角色'
        else:
            res = '你所拥有的角色如下:\n'
            for role in user_info[uid]['role_list'].items():
                if len(role[1]['星级']) == 5:
                    res += '%s%s 数量: %s 出货: %s\n' % (role[1]['星级'], role[0], role[1]['数量'], role[1]['出货'])
                else:
                    res += '%s%s 数量: %s\n' % (role[1]['星级'], role[0], role[1]['数量'])
    else:
        if not len(user_info[uid]['weapon_list']):
            res = '你还没有武器'
        else:
            res = '你所拥有的武器如下:\n'
            for wp in user_info[uid]['weapon_list'].items():
                if len(wp[1]['星级']) == 5:
                    res += '%s%s 数量: %s 出货: %s\n' % (wp[1]['星级'], wp[0], wp[1]['数量'], wp[1]['出货'])
                else:
                    res += '%s%s 数量: %s\n' % (wp[1]['星级'], wp[0], wp[1]['数量'])
    return res.replace('[', '').replace(']', '').replace(',', ' ')


@delete_log.handle()
async def delete_log_handler(event: MessageEvent):
    uid = str(event.user_id)
    init_user_info(uid)
    try:
        del user_info[uid]
        save_user_info()
        await delete_log.finish('你的抽卡记录删除成功', at_sender=True)
    except:
        await delete_log.finish('你的抽卡记录删除失败', at_sender=True)


@choose_dg.handle()
async def choose_dg_handler(event: MessageEvent, msg: Message = CommandArg()):
    uid = str(event.user_id)
    init_user_info(uid)
    dg_weapon = msg.extract_plain_text().strip()
    weapon_up_list = await get_dg_weapon()
    if dg_weapon not in weapon_up_list:
        await choose_dg.finish(f'该武器无定轨，请输入全称[{weapon_up_list[0]}|{weapon_up_list[1]}]', at_sender=True)
    else:
        if dg_weapon == user_info[uid]['gacha_list']['dg_name']:
            await choose_dg.finish('你当前已经定轨该武器，无需更改')
        else:
            user_info[uid]['gacha_list']['dg_name'] = dg_weapon
            user_info[uid]['gacha_list']['dg_time'] = 0
            save_user_info()
            await choose_dg.finish(f'定轨成功，定轨能量值已重置，当前定轨武器为：{dg_weapon}')


@delete_dg.handle()
async def delete_dg_handler(event: MessageEvent):
    uid = str(event.user_id)
    init_user_info(uid)
    if user_info[uid]['gacha_list']['dg_name'] == '':
        await delete_dg.finish('你此前并没有定轨记录哦', at_sender=True)
    else:
        user_info[uid]['gacha_list']['dg_name'] = ''
        user_info[uid]['gacha_list']['dg_time'] = 0
        save_user_info()
        await delete_dg.finish('你的定轨记录删除成功', at_sender=True)


@show_dg.handle()
async def show_dg_handler(event: MessageEvent):
    uid = str(event.user_id)
    init_user_info(uid)
    weapon_up_list = await get_dg_weapon()
    dg_weapon = user_info[uid]['gacha_list']['dg_name']
    dg_time = user_info[uid]['gacha_list']['dg_time']
    if dg_weapon == '':
        await show_dg.finish(f'你当前未定轨武器，可定轨武器有 {weapon_up_list[0]}|{weapon_up_list[1]} ，请使用[选择定轨 武器全称]来进行定轨',
                             at_sender=True)
    else:
        await show_dg.finish(f'你当前定轨的武器为 {dg_weapon} ，能量值为 {dg_time}', at_sender=True)


async def get_dg_weapon():
    weapon_up_list = []
    data = await gacha_info_list()
    f = lambda x: x['gacha_type'] == 302
    gacha_data = sorted(list(filter(f, data)), key=lambda x: x['end_time'])[-1]
    gacha_id = gacha_data['gacha_id']
    gacha_data = await gacha_info(gacha_id)
    for weapon in gacha_data['r5_up_items']:
        weapon_up_list.append(weapon['item_name'])
    return weapon_up_list


def gacha_type_by_name(gacha_type):
    # if re.match(r'^角色1|限定1|角色2|限定2(?:池)$', gacha_type):
    #     return 301
    if re.match(r'^角色1|限定1(?:池)$', gacha_type):
        return 301
    if re.match(r'^角色2|限定2(?:池)$', gacha_type):
        return 400
    if re.match(r'^武器|武器池$', gacha_type):
        return 302
    if re.match(r'^常驻|普(?:池)$', gacha_type):
        return 200
    # if re.match(r'^新角色1|新限定1|新角色2|新限定2(?:池)$', gacha_type):
    #     return 'role_1_pool'
    if re.match(r'^彩蛋池?$', gacha_type):
        return 'all_star'
    # if re.match(r'^新角色1|新限定1(?:池)$', gacha_type):
    #     return 'role_1_pool'
    # if re.match(r'^新角色2|新限定2(?:池)$', gacha_type):
    #     return 'role_2_pool'
    if re.match(r'^新武器|新武器池$', gacha_type):
        return 'weapon_pool'
    return 0


BASE_URL = 'https://webstatic.mihoyo.com/hk4e/gacha_info/cn_gf01/%s'


async def gacha_info_list():
    res = await aiorequests.get(url=BASE_URL % 'gacha/list.json')
    json_data = res.json()
    return json_data['data']['list']


async def gacha_info(gacha_id):
    res = await aiorequests.get(url=BASE_URL % gacha_id + '/zh-cn.json')
    return res.json()
