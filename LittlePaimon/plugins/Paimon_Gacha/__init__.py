from typing import Dict

from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import MessageEvent, Message, GroupMessageEvent
from nonebot.params import RegexDict, CommandArg
from nonebot.plugin import PluginMetadata
from LittlePaimon.utils.tool import freq_limiter
from LittlePaimon.manager.plugin_manager import plugin_manager as pm

from .data_handle import load_user_data
from .draw import draw_gacha_img

__plugin_meta__ = PluginMetadata(
    name='原神模拟抽卡',
    description='原神模拟抽卡',
    usage='抽[数量]十连[卡池]',
    extra={
        'author':   '惜月',
        'version':  '3.0',
        'priority': 9,
        'configs': {
            '群冷却': 30,
            '群成员冷却': 60
        }
    }
)

sim_gacha = on_regex(r'^抽((?P<num>\d+)|(?:.*))十连(?P<pool>.*?)$', priority=13, block=True, state={
        'pm_name':        '模拟抽卡',
        'pm_description': '原神模拟抽卡，卡池有常驻|角色1|角色2|武器',
        'pm_usage':       '抽[数量]十连[卡池]',
        'pm_priority':    1
    })
show_log = on_command('模拟抽卡记录', aliases={'查看模拟抽卡记录'}, priority=13, block=True, state={
        'pm_name':        '模拟抽卡记录',
        'pm_description': '查看模拟抽卡记录',
        'pm_usage':       '模拟抽卡记录[角色|武器]',
        'pm_priority':    2
    })
# delete_log = on_command('删除模拟抽卡记录', priority=13, block=True, state={
#         'pm_name':        '删除模拟抽卡记录',
#         'pm_description': '删除你的模拟抽卡记录',
#         'pm_usage':       '删除模拟抽卡记录',
#         'pm_priority':    3
#     })
# show_dg = on_command('查看定轨', priority=13, block=True, state={
#         'pm_name':        '查看定轨',
#         'pm_description': '查看当前定轨的武器',
#         'pm_usage':       '查看定轨',
#         'pm_priority':    4
#     })
# delete_dg = on_command('删除定轨', priority=13, block=True, state={
#         'pm_name':        '删除定轨',
#         'pm_description': '删除当前定轨武器',
#         'pm_usage':       '删除定轨',
#         'pm_priority':    5
#     })
# choose_dg = on_command('选择定轨', priority=13, block=True, state={
#         'pm_name':        '选择定轨',
#         'pm_description': '选择定轨武器',
#         'pm_usage':       '选择定轨<武器名>',
#         'pm_priority':    6
#     })


@sim_gacha.handle()
async def _(event: MessageEvent, reGroup: Dict = RegexDict()):
    nickname = event.sender.nickname
    if isinstance(event, GroupMessageEvent):
        if not freq_limiter.check(f'gacha-group{event.group_id}'):
            await sim_gacha.finish(f'当前群模拟抽卡冷却ing...剩余{freq_limiter.left(f"gacha-group{event.group_id}")}秒')
        elif not freq_limiter.check(f'gacha-group{event.group_id}-{event.user_id}'):
            await sim_gacha.finish(f'你的模拟抽卡冷却ing...剩余{freq_limiter.left(f"gacha-group{event.group_id}-{event.user_id}")}秒', at_sender=True)
    num = reGroup['num']
    pool = reGroup['pool']
    num = int(num) if num and num.isdigit() else 1
    if num > pm.config.sim_gacha_max:
        await sim_gacha.finish(f'单次最多只能{pm.config.sim_gacha_max}十连哦！')
    pool = pool or '角色1'
    result = await draw_gacha_img(event.user_id, pool, num, nickname)
    if isinstance(event, GroupMessageEvent):
        freq_limiter.start(f'gacha-group{event.group_id}', pm.config.sim_gacha_cd_group)
        freq_limiter.start(f'gacha-group{event.group_id}-{event.user_id}', pm.config.sim_gacha_cd_member)
    await sim_gacha.finish(result)


@show_log.handle()
async def show_log_handler(event: MessageEvent, msg: Message = CommandArg()):
    user_info = load_user_data(event.user_id)
    if user_info['抽卡数据']['抽卡总数'] == 0:
        await show_log.finish('你此前并没有抽过卡哦', at_sender=True)
    msg = msg.extract_plain_text().strip()
    if msg in ['角色', '武器']:
        res = get_rw_record(msg, user_info)
    else:
        data = user_info['抽卡数据']
        res = '你的模拟抽卡记录如下:\n'
        res += '你在本频道总共抽卡{%s}次\n其中五星共{%s}个,四星共{%s}个\n' % (user_info['抽卡数据']['抽卡总数'], user_info['抽卡数据']['5星出货数'], user_info['抽卡数据']['4星出货数'])

        try:
            t5 = '{:.2f}%'.format(((data['5星出货数'] / (data['抽卡总数'] - data['角色池未出5星数'] - data['武器池未出5星数'] - data['常驻池未出5星数'])) * 100))

        except:
            t5 = '0.00%'
        try:
            u5 = '{:.2f}%'.format(data['5星up出货数'] / data['5星出货数'] * 100)
        except Exception:
            u5 = '0.00%'
        try:
            t4 = '{:.2f}%'.format(((data['4星出货数'] / (data['抽卡总数'] - data['角色池未出4星数'] - data['武器池未出4星数'] - data['常驻池未出4星数'])) * 100))

        except:
            t4 = '0.00%'
        try:
            u4 = '{:.2f}%'.format(data['4星up出货数'] / data['4星出货数'] * 100)
        except:
            u4 = '0.00%'
        dg_name = data['定轨武器名称'] if data['定轨武器名称'] != '' else '未定轨'
        res += '五星出货率为{%s} up率为{%s}\n四星出货率为{%s} up率为{%s}\n' % (t5, u5, t4, u4)
        res += '·|角色池|·\n目前{%s}抽未出五星 {%s}抽未出四星\n下次五星是否up:{%s}\n' % (data['角色池未出5星数'], data['角色池未出4星数'], data['角色池5星下次是否为up'])

        res += '·|武器池|·\n目前{%s}抽未出五星 {%s}抽未出四星\n下次五星是否up:{%s}\n' % (data['武器池未出5星数'], data['武器池未出4星数'], data['武器池5星下次是否为up'])

        res += '定轨武器为{%s},能量值为{%s}\n' % (dg_name, data['定轨能量'])
        res += '·|常驻池|·\n目前{%s}抽未出五星 {%s}抽未出四星\n' % (data['常驻池未出5星数'], data['常驻池未出4星数'])

    await show_log.finish(res, at_sender=True)


def get_rw_record(msg, user_info):
    if msg == '角色':
        if len(user_info['角色列表']):
            res = '你所拥有的角色如下:\n'
            for role in user_info['角色列表'].items():
                res += '%s%s 数量: %s 出货: %s\n' % (role[1]['星级'], role[0], role[1]['数量'], role[1]['出货']) if len(
                    role[1]['星级']) == 5 else '%s%s 数量: %s\n' % (role[1]['星级'], role[0], role[1]['数量'])

        else:
            res = '你还没有角色'
    elif not len(user_info['武器列表']):
        res = '你还没有武器'
    else:
        res = '你所拥有的武器如下:\n'
        for wp in user_info['武器列表'].items():
            if len(wp[1]['星级']) == 5:
                res += '%s%s 数量: %s 出货: %s\n' % (wp[1]['星级'], wp[0], wp[1]['数量'], wp[1]['出货'])
            else:
                res += '%s%s 数量: %s\n' % (wp[1]['星级'], wp[0], wp[1]['数量'])
    return res.replace('[', '').replace(']', '').replace(',', ' ')
