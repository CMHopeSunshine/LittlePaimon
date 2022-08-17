import contextlib
import datetime
import random
import re
from asyncio import sleep
from collections import defaultdict

from littlepaimon_utils.tools import FreqLimiter
from nonebot import on_command, require, logger, get_bot
from nonebot.adapters.onebot.v11 import MessageEvent, Message, Bot, MessageSegment
from nonebot.params import CommandArg, Arg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me
from nonebot.typing import T_State

from .draw_abyss_info import draw_abyss_card
from .draw_daily_note import draw_daily_note_card
from .draw_month_info import draw_monthinfo_card
from .draw_player_card import draw_player_card, draw_all_chara_card, draw_chara_card
from .draw_role_card import draw_role_card
from .get_data import addStoken, get_bind_game, get_sign_info, sign, get_sign_list, get_abyss_data, get_daily_note_data, \
    get_enka_data
from .get_data import get_monthinfo_data, get_player_card_data, get_chara_detail_data, get_chara_skill_data
from ..utils.alias_handler import get_match_alias
from ..utils.auth_util import check_cookie
from ..utils.config import config
from ..utils.db_util import get_auto_sign, delete_auto_sign, get_last_query, get_private_stoken, update_private_stoken, \
    get_coin_auto_sign
from ..utils.db_util import insert_public_cookie, update_private_cookie, delete_cookie_cache, delete_private_cookie, \
    update_last_query, reset_public_cookie
from ..utils.db_util import update_note_remind2, update_note_remind, get_note_remind, delete_note_remind, \
    update_day_remind_count, get_private_cookie, add_auto_sign, get_all_query, add_coin_auto_sign, delete_coin_auto_sign
from ..utils.decorator import exception_handler
from ..utils.enka_util import PlayerInfo
from ..utils.message_util import MessageBuild as MsgBd
from ..utils.message_util import get_uid_in_msg, uid_userId_to_dict, replace_all, transform_uid, get_message_id

require('nonebot_plugin_apscheduler')
from nonebot_plugin_apscheduler import scheduler
from .get_coin import MihoyoBBSCoin

__plugin_meta__ = PluginMetadata(
    name="Paimon_Info",
    description="小派蒙的原神信息查询模块",
    usage=(
        "[ys (uid)]查看原神个人卡片(包含宝箱、探索度等数据)\n"
        "[ysa (uid)]查看所有公开的8角色的简略信息\n"
        "[ysc (uid) 角色名]查看公开的8角色的详细信息\n"
        "*绑定私人cookie之后就可以查看所有角色啦\n"
        "--------\n"
        "[ssbq/实时便签 (uid)]查询当前树脂、洞天宝钱、派遣状况等\n"
        "[ssbq (uid) 开启提醒(树脂数)/关闭提醒]开启/关闭树脂提醒，达到树脂数时会在群里艾特你\n"
        "*绑定私人cookie之后才能使用\n"
        "--------\n"
        "[sy/深渊查询/深境螺旋查询 (uid) (层数)]查询深渊战绩信息\n"
        "*绑定私人cookie之后才能查看层数具体阵容哦\n"
        "--------\n"
        "[mys签到]手动进行一次米游社原神签到\n"
        "[mys自动签到开启uid/关闭]开启米游社原神自动签到\n"
        "--------\n"
        "[myzj/每月札记/zj (uid) (月份)]查看该月份获得的原石、摩拉数\n"
        "*绑定私人cookie之后才能使用,只能查看最近3个月的记录,默认为本月\n"
        "--------\n"
        "[ysb cookie]绑定你的私人cookie以开启高级功能\n"
        "[删除ck]删除你的私人cookie\n"
        "[添加公共ck cookie]添加公共cookie以供大众查询*仅管理员\n"
        "--------\n"
        "[更新角色信息 uid]更新游戏内展柜8个角色的面板信息\n"
        "[ysd 角色名 uid]查看指定角色的详细面板信息\n"
        "--------\n"
        "[myb获取]手动进行一次米游币获取\n"
        "[myb自动获取开启uid/关闭]开启米游币原神自动获取\n"
        "--------\n"
        "[添加stoken+stoken]添加stoken"
    ),
    extra={
        'type':    '原神信息查询',
        'range':   ['private', 'group', 'guild'],
        "author":  "惜月 <277073121@qq.com>",
        "version": "0.1.3",
    },
)

sy = on_command('sy', aliases={'深渊信息', '深境螺旋信息'}, priority=7, block=True)
sy.__paimon_help__ = {
    "usage":     "sy[层数](uid)",
    "introduce": "查看深渊战绩信息",
    "priority":  6
}
ssbq = on_command('ssbq', aliases={'实时便笺', '实时便签', '当前树脂'}, priority=7, block=True)
ssbq.__paimon_help__ = {
    "usage":     "ssbq(uid)",
    "introduce": "*查看当前树脂、洞天宝钱、派遣状况等",
    "priority":  7
}
myzj = on_command('myzj', aliases={'札记信息', '每月札记'}, priority=7, block=True)
myzj.__paimon_help__ = {
    "usage":     "myzj[月份](uid)",
    "introduce": "*查看该月份获得的原石、摩拉数",
    "priority":  8
}
ys = on_command('ys', aliases={'原神卡片', '个人卡片'}, priority=7, block=True)
ys.__paimon_help__ = {
    "usage":     "ys(uid)",
    "introduce": "查看原神个人卡片(宝箱、探索度等)",
    "priority":  1
}
ysa = on_command('ysa', aliases={'角色背包'}, priority=7, block=True)
ysa.__paimon_help__ = {
    "usage":     "ysa(uid)",
    "introduce": "查看原神公开角色的简略信息",
    "priority":  2
}
ysc = on_command('ysc', aliases={'角色卡片'}, priority=7, block=True)
ysc.__paimon_help__ = {
    "usage":     "ysc<角色名>(uid)",
    "introduce": "查看原神指定角色的简略信息",
    "priority":  3
}
ysb = on_command('ysb', aliases={'原神绑定', '绑定cookie'}, priority=7, block=True)
ysb.__paimon_help__ = {
    "usage":     "ysb<cookie>",
    "introduce": "绑定私人cookie以开启更多功能",
    "priority":  99
}
ysbjc = on_command('ysbjc', aliases={'原神绑定检查', '检查cookie绑定状态'}, priority=7, block=True)
ysbjc.__paimon_help__ = {
    "usage":     "ysbjc(uid)",
    "introduce": "检查私人cookie绑定状态，可检查指定的uid是否绑定cookie",
    "priority":  99
}
mys_sign = on_command('mys_sign', aliases={'mys签到', '米游社签到'}, priority=7, block=True)
mys_sign_auto = on_command('mys_sign_auto', aliases={'mys自动签到', '米游社自动签到'}, priority=7, block=True)
mys_sign_auto.__paimon_help__ = {
    "usage":     "mys自动签到<on|off uid>",
    "introduce": "*米游社原神区自动签到奖励获取",
    "priority":  9
}
mys_sign_all = on_command('mys_sign_all', aliases={'全部重签'}, priority=1, permission=SUPERUSER, rule=to_me(), block=True)
update_all = on_command('update_all', aliases={'更新全部玩家'}, priority=1, permission=SUPERUSER, rule=to_me(), block=True)
add_public_ck = on_command('add_ck', aliases={'添加公共cookie', '添加公共ck'}, permission=SUPERUSER, priority=7, block=True)
delete_ck = on_command('delete_ck', aliases={'删除ck', '删除cookie'}, priority=7, block=True)
update_info = on_command('udi', aliases={'更新角色信息', '更新角色面板', '更新玩家信息'}, priority=6, block=True)
update_info.__paimon_help__ = {
    "usage":     "更新角色信息(uid)",
    "introduce": "更新游戏内展柜8个角色的面板信息，以便使用ysd指令",
    "priority":  5
}
role_info = on_command('角色面板', aliases={'角色详情', '角色信息', 'ysd'}, block=True, priority=7)
role_info.__paimon_help__ = {
    "usage":     "ysd<角色名>(uid)",
    "introduce": "查看指定角色的详细面板信息",
    "priority":  4
}
get_mys_coin = on_command('myb获取', aliases={'米游币获取', '获取米游币'}, priority=7, block=True)
get_mys_coin_auto = on_command('myb自动获取', aliases={'米游币自动获取', '自动获取米游币'}, priority=7, block=True)
get_mys_coin_auto.__paimon_help__ = {
    "usage":     "myb自动获取<on|off uid>",
    "introduce": "自动获取米游币",
    "priority":  10
}
add_stoken = on_command('添加stoken', priority=7, block=True)
add_stoken.__paimon_help__ = {
    "usage":     "添加stoken[stoken]",
    "introduce": "添加stoken以获取米游币",
    "priority":  99
}


@sy.handle()
@ys.handle()
@ysa.handle()
@ysc.handle()
async def _(event: MessageEvent, state: T_State, msg: Message = CommandArg()):
    state['use_cache'] = False if '-r' in msg.extract_plain_text() else True
    msg_text = msg.extract_plain_text().replace('-r', '').strip()
    if not msg:
        uid = await get_last_query(str(event.user_id))
        if uid:
            state['uid'] = uid
        state['user_id'] = str(event.user_id)
    else:
        uid_list = []
        check_uid = msg_text.split(' ')
        for check in check_uid:
            uid = re.search(r'(?P<uid>(1|2|5)\d{8})', check)
            if uid:
                uid_list.append(uid.group('uid'))
                msg_text = msg_text.replace(uid.group('uid'), '')
                state['user_id'] = str(event.user_id)
        if not uid_list:
            user_list = []
            for msg_seg in msg:
                if msg_seg.type == "at":
                    user_list.append(msg_seg.data['qq'])
            if len(user_list) == 1:
                uid = await get_last_query(user_list[0])
                if uid:
                    state['uid'] = uid
                    state['user_id'] = user_list[0]
            elif user_list:
                state['uid'] = [await get_last_query(user) for user in user_list]
                state['user_id'] = user_list
            else:
                state['user_id'] = str(event.user_id)
                uid = await get_last_query(str(event.user_id))
                if uid:
                    state['uid'] = uid
        else:
            state['uid'] = uid_list[0] if len(uid_list) == 1 else uid_list if uid_list else None
    if msg_text:
        state['msg'] = msg_text.strip()


@sy.got('uid', prompt='请把要查询的uid给派蒙哦~')
@exception_handler()
async def _(event: MessageEvent, state: T_State):
    uid = transform_uid(state['uid'])
    if uid:
        state['uid'] = uid
    else:
        await ysa.finish('这个uid不正确哦~，请检查一下', at_sender=True)
    if 'msg' not in state:
        floor = []
    else:
        floor = state['msg'].split(' ')
    true_floor = [int(f) for f in floor if f.isdigit() and (9 <= int(f) <= 12)]
    true_floor.sort()
    query_dict, total_result = uid_userId_to_dict(state['uid'], state['user_id'])
    for uid, user_id in query_dict.items():
        await update_last_query(user_id, uid)
        data = await get_abyss_data(user_id, uid, use_cache=state['use_cache'])
        if isinstance(data, str):
            total_result += MessageSegment.text(data + '\n')
        else:
            abyss_card = await draw_abyss_card(data, uid, true_floor)
            total_result += abyss_card
    await sy.finish(total_result)


@ssbq.handle()
@exception_handler()
async def ssbq_handler(event: MessageEvent, msg: Message = CommandArg()):
    if event.message_type == 'group':
        gid = str(event.group_id)
    else:
        gid = str(event.user_id)
    uid, msg, user_id, use_cache = await get_uid_in_msg(event, msg)
    if not uid:
        await ssbq.finish('请把要查的uid给派蒙哦!', at_sender=True)
    find_remind_enable = re.search(r'(?P<action>开启提醒|关闭提醒|删除提醒)\s*((?P<num>\d{1,3})|(?:.*))', msg)
    if find_remind_enable:
        if event.message_type == 'guild':
            await ssbq.finish('实时便签提醒功能暂时无法在频道内使用哦')
        if find_remind_enable.group('action') == '开启提醒':
            if find_remind_enable.group('num'):
                await update_note_remind2(user_id, uid, gid, 1, find_remind_enable.group('num'))
                await ssbq.finish(f'开启提醒成功,派蒙会在你的树脂达到{find_remind_enable.group("num")}时提醒你的', at_sender=True)
            else:
                await update_note_remind2(user_id, uid, gid, 1)
                await ssbq.finish('开启提醒成功', at_sender=True)
        elif find_remind_enable.group('action') == '关闭提醒':
            await update_note_remind2(user_id, uid, gid, 0)
            await ssbq.finish('关闭提醒成功', at_sender=True)
        elif find_remind_enable.group('action') == '删除提醒':
            await delete_note_remind(user_id, uid)
            await ssbq.finish('删除提醒成功', at_sender=True)
    else:
        data = await get_daily_note_data(uid)
        if isinstance(data, str):
            await ssbq.finish(data, at_sender=True)
        else:
            daily_note_card = await draw_daily_note_card(data, uid)
            await ssbq.finish(daily_note_card)


@myzj.handle()
@exception_handler()
async def myzj_handler(event: MessageEvent, msg: Message = CommandArg()):
    uid, msg, user_id, use_cache = await get_uid_in_msg(event, msg)
    # 札记只能查看最近3个月的，构造正则来获取月份
    month_now = datetime.datetime.now().month
    if month_now == 1:
        month_list = ['11', '12', '1']
    elif month_now == 2:
        month_list = ['12', '1', '2']
    else:
        month_list = [str(month_now - 2), str(month_now - 1), str(month_now)]
    find_month = '(?P<month>' + '|'.join(month_list) + ')'
    match = re.search(find_month, msg)
    month = match.group('month') if match else month_now
    data = await get_monthinfo_data(uid, month, use_cache=use_cache)
    if isinstance(data, str):
        await myzj.finish(data, at_sender=True)
    else:
        monthinfo_card = await draw_monthinfo_card(data)
        await myzj.finish(monthinfo_card)


@ys.got('uid', prompt='请把要查询的uid给派蒙哦~')
@exception_handler()
async def ys_handler(bot: Bot, event: MessageEvent, state: T_State):
    uid = transform_uid(state['uid'])
    if uid:
        state['uid'] = uid
    else:
        await ysa.finish('这个uid不正确哦~，请检查一下', at_sender=True)
    query_dict, total_result = uid_userId_to_dict(state['uid'], state['user_id'])
    for uid, user_id in query_dict.items():
        await update_last_query(user_id, uid)
        data = await get_player_card_data(user_id, uid, use_cache=state['use_cache'])
        if isinstance(data, str):
            total_result += MessageSegment.text(data + '\n')
        else:
            if event.message_type == 'group':
                user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=int(user_id))
                nickname = user_info['card'] or user_info['nickname']
            else:
                nickname = event.sender.nickname
            chara_data = await get_chara_detail_data(user_id, uid, use_cache=state['use_cache'])
            chara_data = None if isinstance(chara_data, str) else chara_data
            player_card = await draw_player_card(data, chara_data, uid, nickname)
            total_result += player_card
    await ys.finish(total_result)


@ysa.got('uid', prompt='请把要查询的uid给派蒙哦~')
@exception_handler()
async def ysa_handler(event: MessageEvent, state: T_State):
    uid = transform_uid(state['uid'])
    if uid:
        state['uid'] = uid
    else:
        await ysa.finish('这个uid不正确哦~，请检查一下', at_sender=True)
    query_dict, total_result = uid_userId_to_dict(state['uid'], state['user_id'])
    for uid, user_id in query_dict.items():
        await update_last_query(user_id, uid)
        chara_data = await get_chara_detail_data(user_id, uid, use_cache=state['use_cache'])
        if isinstance(chara_data, str):
            total_result += MessageSegment.text(chara_data + '\n')
        else:
            player_card = await draw_all_chara_card(chara_data, uid)
            total_result += player_card
    await ysa.finish(total_result)


@ysc.got('uid', prompt='请把要查询的uid给派蒙哦~')
async def _(event: MessageEvent, state: T_State):
    uid = transform_uid(state['uid'])
    if uid:
        state['uid'] = uid
    else:
        await ysa.finish('这个uid不正确哦~，请检查一下', at_sender=True)


@ysc.got('msg', prompt='请把要查询的角色名给派蒙哦~')
async def _(event: MessageEvent, state: T_State):
    name = state['msg']
    if isinstance(name, Message):
        name = replace_all(name.extract_plain_text().strip().replace('ysc', ''), state['uid'])
        if name == 'q':
            await ysc.finish()
    match_alias = get_match_alias(name, '角色', True)
    if len(match_alias) == 1:
        state['choice'] = match_alias
    else:
        if not match_alias:
            await ysc.finish(MsgBd.Text(f'没有找到叫{name}的角色哦~'), at_sender=True)
        elif 'choice' not in state:
            msg = f'你要找的角色是哪个呀：\n'
            # 将字典中每个键拼接到msg中，并添加序号
            msg += '\n'.join([f'{int(i) + 1}. {name}' for i, name in enumerate(match_alias)])
            await ysc.send(msg + '\n回答\"q\"可以取消查询', at_sender=True)
        state['match_alias'] = match_alias


@ysc.got('choice')
async def _(event: MessageEvent, state: T_State):
    choice = state['choice']
    if isinstance(choice, dict):
        # 获取字典的键
        role = list(choice.items())[0]
    else:
        match_alias = state['match_alias']
        choice = replace_all(choice.extract_plain_text().strip().replace('ysc', ''), state['uid'])

        if choice == 'q':
            await ysc.finish()
        if choice.isdigit() and (1 <= int(choice) <= len(match_alias)):
            role = list(match_alias.items())[int(choice) - 1]
        elif choice not in match_alias.keys():
            state['times'] = state['times'] + 1 if 'times' in state else 1
            if state['times'] == 1:
                await ysc.reject(f'请旅行者从上面的角色中选一个问派蒙\n回答\"q\"可以取消查询', at_sender=True)
            elif state['times'] == 2:
                await ysc.reject(f'别调戏派蒙啦，快选一个吧，不想问了请回答\"q\"！', at_sender=True)
            elif state['times'] >= 3:
                await ysc.finish(f'看来旅行者您有点神志不清哦(，下次再问派蒙吧' + MessageSegment.face(146), at_sender=True)
        else:
            role = [m for m in list(match_alias.items()) if m[0] == choice][0]
    query_dict, total_result = uid_userId_to_dict(state['uid'], state['user_id'])
    for uid, user_id in query_dict.items():
        await update_last_query(user_id, uid)
        chara_data = await get_chara_detail_data(user_id, uid, use_cache=state['use_cache'])
        if isinstance(chara_data, str):
            total_result += MessageSegment.text(chara_data + '\n')
        else:
            skill_data = await get_chara_skill_data(uid, role[1], use_cache=state['use_cache'])
            chara_card = await draw_chara_card(chara_data, skill_data, role, uid)
            total_result += chara_card
    await ysc.finish(total_result)


cookie_error_msg = '这个cookie无效哦，请旅行者确认是否正确\n获取cookie的教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1\n'


@ysb.handle()
@exception_handler()
async def ysb_handler(event: MessageEvent, msg: Message = CommandArg()):
    cookie = msg.extract_plain_text().strip()
    if cookie == '':
        res = '获取cookie的教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1\n获取到后，添加派蒙好友私聊发送ysb接复制到的cookie就行啦~'
        await ysb.finish(res, at_sender=True)
    else:
        cookie_info, mys_id = await get_bind_game(cookie)
        if not cookie_info or cookie_info['retcode'] != 0:
            msg = cookie_error_msg
            if event.message_type != 'private':
                msg += '\n当前是在群聊里绑定，建议旅行者添加派蒙好友私聊绑定!'
            await ysb.finish(msg, at_sender=True)
        else:
            uid = nickname = None
            for data in cookie_info['data']['list']:
                if data['game_id'] == 2:
                    uid = data['game_role_id']
                    nickname = data['nickname']
                    break
            if uid:
                await update_private_cookie(user_id=str(event.user_id), uid=uid, mys_id=mys_id, cookie=cookie)
                await update_last_query(str(event.user_id), uid, 'uid')
                await delete_cookie_cache(uid, key='uid', all=False)
                msg = f'{nickname}绑定成功啦!使用ys/ysa等指令和派蒙互动吧!'
                if event.message_type != 'private':
                    msg += '\n当前是在群聊里绑定，建议旅行者把cookie撤回哦!'
                await ysb.finish(MsgBd.Text(msg), at_sender=True)


@ysbjc.handle()
@exception_handler()
async def ysbjc_handler(event: MessageEvent, msg: Message = CommandArg()):
    cookie = await get_private_cookie(event.user_id)
    if len(cookie) == 0:
        await ysbjc.finish("旅行者当前未绑定私人cookie")
        return
    uid = transform_uid(str(msg))
    if not uid:
        await ysbjc.finish(f"旅行者当前已绑定{len(cookie)}条私人cookie")
        return
    for data in cookie:
        if data['uid'] == uid:
            await ysbjc.finish("旅行者已为此uid绑定私人cookie！")
            return
    await ysbjc.finish("旅行者还没有为此uid绑定私人cookie哦~")


@add_public_ck.handle()
@exception_handler()
async def add_public_ck_handler(event: MessageEvent, msg: Message = CommandArg()):
    cookie = str(msg).strip()
    if await check_cookie(cookie):
        await insert_public_cookie(cookie)
        await add_public_ck.finish('公共cookie添加成功啦,派蒙开始工作!')
    else:
        await add_public_ck.finish(cookie_error_msg)


@delete_ck.handle()
@exception_handler()
async def delete_ck_handler(event: MessageEvent):
    await delete_private_cookie(str(event.user_id))
    await delete_ck.finish('派蒙把你的私人cookie都删除啦!', at_sender=True)


@mys_sign.handle()
@exception_handler()
async def mys_sign_handler(event: MessageEvent, msg: Message = CommandArg()):
    uid, msg, user_id, use_cache = await get_uid_in_msg(event, msg)
    sign_list = await get_sign_list()
    sign_info = await get_sign_info(uid)
    if isinstance(sign_info, str):
        await mys_sign.finish(sign_info, at_sender=True)
    elif sign_info['data']['is_sign']:
        sign_day = sign_info['data']['total_sign_day'] - 1
        await mys_sign.finish(
            f'你今天已经签过到了哦,获得的奖励为:\n{sign_list["data"]["awards"][sign_day]["name"]} * {sign_list["data"]["awards"][sign_day]["cnt"]}',
            at_sender=True)
    else:
        sign_day = sign_info['data']['total_sign_day']
        sign_action = await sign(uid)
        for _ in range(5):
            if isinstance(sign_action, dict):
                if sign_action['data']['success'] == 0:
                    await mys_sign.finish(
                        f'签到成功,获得的奖励为:\n{sign_list["data"]["awards"][sign_day]["name"]} * {sign_list["data"]["awards"][sign_day]["cnt"]}',
                        at_sender=True)
                else:
                    await sleep(random.randint(3, 6))
            else:
                await mys_sign.finish(sign_action, at_sender=True)


@mys_sign_auto.handle()
@exception_handler()
async def mys_sign_auto_handler(event: MessageEvent, msg: Message = CommandArg()):
    if event.message_type == 'group':
        remind_id = str(event.group_id)
    elif event.message_type == 'private':
        remind_id = 'q' + str(event.user_id)
    else:
        await mys_sign_auto.finish('自动签到功能暂时不支持频道使用哦')
    msg = str(msg).strip()
    find_uid = re.search(r'(?P<uid>(1|2|5)\d{8})', msg)
    if not find_uid:
        await mys_sign_auto.finish('请把正确的需要帮忙签到的uid给派蒙哦!', at_sender=True)
    else:
        uid = find_uid.group('uid')
        find_action = re.search(r'(?P<action>开启|启用|打开|关闭|禁用|on|off)', msg)
        if find_action:
            if find_action.group('action') in ['开启', '启用', '打开', 'on']:
                cookie = await get_private_cookie(uid, key='uid')
                if not cookie:
                    await mys_sign_auto.finish('你的该uid还没绑定cookie哦，先用ysb绑定吧!', at_sender=True)
                await add_auto_sign(str(event.user_id), uid, remind_id)
                await mys_sign_auto.finish('开启米游社自动签到成功,派蒙会在每日0点帮你签到', at_sender=True)
            elif find_action.group('action') in ['关闭', '禁用', 'off']:
                await delete_auto_sign(str(event.user_id), uid)
                await mys_sign_auto.finish('关闭米游社自动签到成功', at_sender=True)
        else:
            await mys_sign_auto.finish('指令错误，在后面加 开启/关闭 来使用哦', at_sender=True)


ud_lmt = FreqLimiter(180)
ud_p_lmt = FreqLimiter(15)


@update_info.handle()
async def _(event: MessageEvent, state: T_State, msg: Message = CommandArg()):
    if uid := re.search(r'(?P<uid>(1|2|5|8)\d{8})', msg.extract_plain_text().strip()):
        state['uid'] = uid.group('uid')
    else:
        if user := next((msg_seg.data['qq'] for msg_seg in msg if msg_seg.type == "at"), ''):
            uid = await get_last_query(str(user))
        else:
            uid = await get_last_query(str(event.user_id))
        if uid:
            state['uid'] = uid
    if 'uid' in state and not ud_lmt.check(state['uid']):
        await update_info.finish(f'每个uid每3分钟才能更新一次信息，请稍等一下吧~(剩余{ud_lmt.left_time(state["uid"])}秒)')
    if not ud_p_lmt.check(get_message_id(event)):
        await update_info.finish(f'每个会话每15秒才能更新一次信息，请稍等一下吧~(剩余{ud_lmt.left_time(get_message_id(event))}秒)')


@update_info.got('uid', prompt='请把要更新的uid给派蒙哦~')
@exception_handler()
async def _(event: MessageEvent, uid: Message = Arg('uid')):
    uid = transform_uid(uid)
    if not uid:
        await update_info.finish('这好像不是一个正确的uid哦~，请检查一下', at_sender=True)
    await update_last_query(str(event.user_id), uid)

    await update_info.send('派蒙开始更新信息~请稍等哦~')
    enka_data = await get_enka_data(uid)
    if not enka_data:
        await update_info.finish('派蒙没有获取到该uid的信息哦，可能是enka接口服务出现问题，稍候再试吧~')
    ud_lmt.start_cd(uid, 180)
    ud_lmt.start_cd(get_message_id(event), 15)
    player_info = PlayerInfo(uid)
    player_info.set_player(enka_data['playerInfo'])
    if 'avatarInfoList' not in enka_data:
        player_info.save()
        await update_info.finish('你未在游戏中打开角色展柜，派蒙查不到~请打开5分钟后再试~')
    else:
        for role in enka_data['avatarInfoList']:
            player_info.set_role(role)
        player_info.save()
        role_list = list(player_info.get_update_roles_list().keys())
        await update_info.finish(f'uid{uid}更新完成~本次更新的角色有：\n' + ' '.join(role_list))


@role_info.handle()
async def _(event: MessageEvent, state: T_State, msg: Message = CommandArg()):
    if uid := re.search(r'(?P<uid>(1|2|5|8)\d{8})', msg.extract_plain_text().strip()):
        state['uid'] = uid.group('uid')
        await update_last_query(str(event.user_id), uid.group('uid'))
    else:
        user = ''
        for msg_seg in msg:
            if msg_seg.type == "at":
                user = msg_seg.data['qq']
        if user:
            uid = await get_last_query(str(user))
        else:
            uid = await get_last_query(str(event.user_id))
        if uid:
            state['uid'] = uid
    msg = msg.extract_plain_text().replace(state['uid'] if 'uid' in state else 'ysd', '').strip()
    if not msg:
        await role_info.finish('请把要查询角色名给派蒙哦~')
    if msg.startswith(('a', '全部', '所有', '查看')):
        state['role'] = 'all'
    else:
        match_alias = get_match_alias(msg, '角色', True)
        if match_alias:
            state['role'] = match_alias if isinstance(match_alias, str) else tuple(match_alias.keys())[0]
        else:
            await role_info.finish(MsgBd.Text(f'哪有名为{msg}的角色啊，别拿派蒙开玩笑!'))


@role_info.got('uid', prompt='请把要查询的uid给派蒙哦~')
@exception_handler()
async def _(event: MessageEvent, state: T_State):
    uid = transform_uid(state['uid'])
    if uid:
        state['uid'] = uid
    else:
        await role_info.finish('这个uid不正确哦~，请检查一下', at_sender=True)
    uid = state['uid']
    role = state['role']
    player_info = PlayerInfo(uid)
    roles_list = player_info.get_roles_list()
    if role == 'all':
        if not roles_list:
            await role_info.finish('你在派蒙这里没有角色面板信息哦，先用 更新角色信息 命令获取吧~', at_sender=True)
        res = '目前已获取的角色面板有：\n'
        for r in roles_list:
            res += r
            res += ' ' if (roles_list.index(r) + 1) % 4 else '\n'
        await role_info.finish(res, at_sender=True)
    if role not in roles_list:
        await role_info.finish(MsgBd.Text(f'派蒙还没有你{role}的信息哦，先用 更新角色信息 命令更新吧~'), at_sender=True)
    else:
        role_data = player_info.get_roles_info(role)
        img = await draw_role_card(uid, role_data)
        await role_info.finish(img)


@mys_sign_all.handle()
async def sign_all():
    await auto_sign()


@update_all.handle()
async def _():
    res = await all_update()
    await update_all.finish(res)


@scheduler.scheduled_job('cron', hour=config.paimon_sign_hour, minute=config.paimon_sign_minute, misfire_grace_time=10)
async def auto_sign():
    data = await get_auto_sign()
    if data:
        ann = defaultdict(lambda: defaultdict(list))
        logger.info('---派蒙开始执行米游社自动签到---')
        sign_list = await get_sign_list()
        for user_id, uid, remind_id in data:
            sign_info = await get_sign_info(uid)
            if isinstance(sign_info, str):
                with contextlib.suppress(Exception):
                    await delete_auto_sign(user_id, uid)
                    if remind_id.startswith('q'):
                        await get_bot().send_private_msg(user_id=remind_id[1:],
                                                         message=f'你的uid{uid}签到失败，请重新绑定cookie再开启自动签到')
                    else:
                        ann[remind_id]['失败'].append(f'.UID{uid}')
            elif sign_info['data']['is_sign']:
                logger.info(f'---qq{user_id}的UID{uid}已经签过，跳过---')
            else:
                for _ in range(5):
                    sign_result = await sign(uid)
                    if isinstance(sign_result, dict):
                        # success为0则说明没有出现验证码，不为0则有验证码，等待5-10秒再重试，重试最多5次
                        if sign_result['data']['success'] == 0:
                            await sleep(1)
                            sign_info = await get_sign_info(uid)
                            sign_day = sign_info['data']['total_sign_day'] - 1
                            with contextlib.suppress(Exception):
                                if remind_id.startswith('q'):
                                    await get_bot().send_private_msg(user_id=remind_id[1:],
                                                                     message=f'你的uid{uid}自动签到成功!签到奖励为{sign_list["data"]["awards"][sign_day]["name"]}*{sign_list["data"]["awards"][sign_day]["cnt"]}')
                                else:
                                    ann[remind_id]['成功'].append(
                                        f'.UID{uid}-{sign_list["data"]["awards"][sign_day]["name"]}*{sign_list["data"]["awards"][sign_day]["cnt"]}')
                            break
                        else:
                            await sleep(random.randint(5, 10))
            await sleep(random.randint(20, 35))
        for group_id, content in ann.items():
            group_str = '米游社自动签到结果：\n'
            for type, ann_list in content.items():
                if ann_list:
                    group_str += f'签到{type}：\n'
                    for u in ann_list:
                        group_str += str(ann_list.index(u) + 1) + u + '\n'
            try:
                await get_bot().send_group_msg(group_id=group_id, message=group_str)
                await sleep(random.randint(5, 10))
            except Exception as e:
                logger.error(f'米游社签到结果发送失败：{e}')


@scheduler.scheduled_job('cron', hour=config.paimon_coin_hour, minute=config.paimon_coin_minute, misfire_grace_time=10)
async def coin_auto_sign():
    data = await get_coin_auto_sign()
    ann = defaultdict(lambda: defaultdict(list))
    if data:
        logger.info('---派蒙开始执行米游币自动获取---')
        for user_id, uid, remind_id in data:
            await sleep(random.randint(20, 35))
            sk = await get_private_stoken(uid, key='uid')
            try:
                stoken = sk[0][4]
                get_coin_task = MihoyoBBSCoin(stoken, user_id, uid)
                data = await get_coin_task.run()
                if get_coin_task.state is False:
                    await delete_coin_auto_sign(user_id, uid)
                    if remind_id.startswith('q'):
                        await get_bot().send_private_msg(user_id=remind_id[1:],
                                                        message=f'你的uid{uid}米游币获取失败，请重新绑定stoken再开启')
                    else:
                        ann[remind_id]['失败'].append(f'.UID{uid}')
                else:
                    if remind_id.startswith('q'):
                        await get_bot().send_private_msg(user_id=remind_id[1:],
                                                        message=f'你的uid{uid}米游币自动获取成功')
                    else:
                        ann[remind_id]['成功'].append(f'.UID{uid}')
            except:
                await delete_coin_auto_sign(user_id, uid)
                if remind_id.startswith('q'):
                    await get_bot().send_private_msg(user_id=remind_id[1:],
                                    message=f'你的uid{uid}米游币获取失败，请重新绑定stoken再开启')
                logger.info('该成员未绑定stoken 获取失败, 已删除自动获取任务')
        for group_id, content in ann.items():
            group_str = '米游币自动获取结果：\n'
            for type, ann_list in content.items():
                if ann_list:
                    group_str += f'{type}：\n'
                    for u in ann_list:
                        group_str += str(ann_list.index(u) + 1) + u + '\n'
            try:
                await get_bot().send_group_msg(group_id=group_id, message=group_str)
                await sleep(random.randint(3, 8))
            except Exception as e:
                logger.error(f'米游币自动获取结果发送失败：{e}')


@scheduler.scheduled_job('cron', minute=f'*/{config.paimon_check_interval}', misfire_grace_time=10)
async def check_note():
    now_time = datetime.datetime.now()
    start_time = datetime.datetime(now_time.year, now_time.month, now_time.day, config.paimon_remind_start, 0, 0)
    end_time = datetime.datetime(now_time.year, now_time.month, now_time.day, config.paimon_remind_end, 0, 0)
    if start_time < now_time < end_time:
        return
    data = await get_note_remind()
    if data:
        logger.info('---派蒙开始检查实时便签树脂提醒---')
        for user_id, uid, count, remind_group, enable, last_remind_time, today_remind_count in data:
            if last_remind_time:
                last_remind_time = datetime.datetime.strptime(last_remind_time, '%Y%m%d %H:%M:%S')
                if now_time - last_remind_time > datetime.timedelta(minutes=30):
                    time_e = True
                else:
                    time_e = False
            else:
                time_e = True
            if enable and ((
                                   today_remind_count and today_remind_count < config.paimon_remind_limit) or not today_remind_count) and time_e:
                now_data = await get_daily_note_data(uid)
                if isinstance(now_data, str):
                    try:
                        await delete_note_remind(user_id, uid)
                        if user_id == remind_group:
                            await get_bot().send_private_msg(user_id=user_id,
                                                             message=f'[CQ:at,qq={user_id}]你的cookie失效了哦,派蒙没办法帮你检查树脂,'
                                                                     f'请重新添加ck后再叫派蒙开启提醒')
                        else:
                            await get_bot().send_group_msg(group_id=remind_group,
                                                           message=f'[CQ:at,qq={user_id}]你的cookie失效了哦,派蒙没办法帮你检查树脂,'
                                                                   f'请重新添加ck后再叫派蒙开启提醒')
                    except Exception as e:
                        logger.error(f'---派蒙发送树脂提醒失败:{e}---')
                else:
                    if now_data['data']['current_resin'] >= count:
                        logger.info(f'---用户{user_id}的uid{uid}的树脂已经达到阈值了,发送提醒---')
                        if today_remind_count:
                            today_remind_count += 1
                        else:
                            today_remind_count = 1
                        now_time_str = now_time.strftime('%Y%m%d %H:%M:%S')
                        try:
                            await update_note_remind(user_id, uid, count, remind_group, enable, now_time_str,
                                                     today_remind_count)
                            if user_id == remind_group:
                                await get_bot().send_private_msg(user_id=user_id,
                                                                 message=f'[CQ:at,qq={user_id}]⚠️你的树脂已经达到了{now_data["data"]["current_resin"]},记得清理哦!⚠️')
                            else:
                                await get_bot().send_group_msg(group_id=remind_group,
                                                               message=f'[CQ:at,qq={user_id}]⚠️你的树脂已经达到了{now_data["data"]["current_resin"]},记得清理哦!⚠️')
                        except Exception as e:
                            logger.error(f'---派蒙发送树脂提醒失败:{e}---')
                await sleep(random.randint(8, 15))


@scheduler.scheduled_job('cron', hour=0, misfire_grace_time=10)
async def daily_update():
    logger.info('---清空今日树脂提醒限制---')
    await update_day_remind_count()
    logger.info('---清空今日cookie缓存---')
    await delete_cookie_cache(all=True)
    logger.info('---清空今日cookie限制记录---')
    await reset_public_cookie()


# @scheduler.scheduled_job('cron', hour=3, misfire_grace_time=10)
async def all_update():
    uid_list = await get_all_query()
    logger.info(f'派蒙开始更新用户角色信息，共{len(uid_list)}个用户')
    failed_time = 0
    for uid in uid_list:
        try:
            data = await get_enka_data(uid)
            if data:
                player_info = PlayerInfo(uid)
                player_info.set_player(data['playerInfo'])
                if 'avatarInfoList' in data:
                    for role in data['avatarInfoList']:
                        player_info.set_role(role)
                player_info.save()
                logger.info(f'---派蒙更新{uid}的角色信息成功---')
            await sleep(random.randint(8, 15))
        except Exception:
            failed_time += 1
            if failed_time > 5:
                break
    return f'玩家信息uid更新共{len(uid_list)}个，更新完成'


@get_mys_coin.handle()
@exception_handler()
async def get_mys_coin_handler(event: MessageEvent, msg: Message = CommandArg()): \
        # 获取UID
    uid, msg, user_id, use_cache = await get_uid_in_msg(event, msg)
    if not uid:
        await get_mys_coin.finish('没有找到你的uid哦')
    sk = await get_private_stoken(uid, key='uid')
    if not sk:
        await get_mys_coin.finish('请旅行者先添加cookie和stoken哦')
    cookie = sk[0][1]
    if not cookie:
        await get_mys_coin.finish('你的该uid还没绑定cookie哦，先用ysb绑定吧')
    stoken = sk[0][4]
    await get_mys_coin.send('开始执行米游币获取，请稍等哦~')
    get_coin_task = MihoyoBBSCoin(stoken, str(event.user_id), uid)
    data = await get_coin_task.run()
    msg = "米游币获取完成\n" + data
    await get_mys_coin.finish(msg)


@get_mys_coin_auto.handle()
@exception_handler()
async def get_mys_coin_auto_handler(event: MessageEvent, msg: Message = CommandArg()):
    if event.message_type == 'group':
        remind_id = str(event.group_id)
    elif event.message_type == 'private':
        remind_id = 'q' + str(event.user_id)
    else:
        await get_mys_coin_auto.finish('米游币自动获取功能暂时不支持频道使用哦')
    msg = msg.extract_plain_text().strip()
    find_uid = re.search(r'(?P<uid>(1|2|5)\d{8})', msg)
    if not find_uid:
        await get_mys_coin_auto.finish('请把正确的需要帮忙获取的uid给派蒙哦!', at_sender=True)
    else:
        uid = find_uid.group('uid')
        find_action = re.search(r'(?P<action>开启|启用|打开|关闭|禁用|on|off)', msg)
        if find_action:
            if find_action.group('action') in ['开启', '启用', '打开', 'on']:
                sk = await get_private_stoken(uid, key='uid')
                stoken = sk[0][4]
                if not stoken:
                    await get_mys_coin_auto.finish('你的该uid还没绑定stoken哦，先用添加stoken绑定吧!', at_sender=True)
                await add_coin_auto_sign(str(event.user_id), uid, remind_id)
                await get_mys_coin_auto.finish('开启米游币自动获取成功,派蒙会在每日0点帮你签到', at_sender=True)
            elif find_action.group('action') in ['关闭', '禁用', 'off']:
                await delete_coin_auto_sign(str(event.user_id), uid)
                await get_mys_coin_auto.finish('关闭米游币自动获取成功', at_sender=True)
        else:
            await get_mys_coin_auto.finish('指令错误，在后面加 开启/关闭 来使用哦', at_sender=True)


@add_stoken.handle()
@exception_handler()
async def add_stoken_handler(event: MessageEvent, msg: Message = CommandArg()):
    stoken = msg.extract_plain_text().strip()
    if stoken == '':
        res = '获取stoken的教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1\n获取到后，添加派蒙好友私聊发送ysb接复制到的cookie就行啦~'
        await add_stoken.finish(res, at_sender=True)
    else:
        uid = (await get_private_cookie(event.user_id, key='user_id'))[0][2]
        stoken, mys_id, stoken_info, m = await addStoken(stoken, uid)
        if not stoken_info and not mys_id:
            await add_stoken.finish(m)
        if not stoken_info or stoken_info['retcode'] != 0:
            msg = cookie_error_msg
            if event.message_type != 'private':
                msg += '\n当前是在群聊里绑定，建议旅行者添加派蒙好友私聊绑定!'
            await add_stoken.finish(msg, at_sender=True)
        else:
            if uid:
                await update_private_stoken(user_id=str(event.user_id), uid=uid, mys_id=mys_id, cookie='',
                                            stoken=stoken)
                await update_last_query(str(event.user_id), uid, 'uid')
                msg = f'stoken绑定成功啦!'
                if event.message_type != 'private':
                    msg += '\n当前是在群聊里绑定，建议旅行者把stoken撤回哦!'
                await add_stoken.finish(MsgBd.Text(msg), at_sender=True)
