import datetime
import re
import random
from collections import defaultdict
from asyncio import sleep
from nonebot import on_command, require, logger, get_bot
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import MessageEvent, Message, Bot
from .get_data import get_bind_game, get_sign_info, sign, get_sign_list, get_abyss_data, get_daily_note_data
from .get_data import get_monthinfo_data, get_player_card_data, get_chara_detail_data, get_chara_skill_data
from .draw_abyss_info import draw_abyss_card
from .draw_daily_note import draw_daily_note_card
from .draw_month_info import draw_monthinfo_card
from .draw_player_card import draw_player_card, draw_all_chara_card, draw_chara_card
from ..utils.character_alias import get_id_by_alias
from ..utils.util import get_uid_in_msg, check_cookie, exception_handler
from ..utils.db_util import update_note_remind2, update_note_remind, get_note_remind, delete_note_remind, \
    update_day_remind_count, get_private_cookie, add_auto_sign
from ..utils.db_util import insert_public_cookie, update_private_cookie, delete_cookie_cache, delete_private_cookie, \
    update_last_query, reset_public_cookie
from ..utils.db_util import get_auto_sign, delete_auto_sign
from ..utils.config import config

scheduler = require('nonebot_plugin_apscheduler').scheduler

__usage__ = '''
[ys (uid)]查看原神个人卡片(包含宝箱、探索度等数据)
[ysa (uid)]查看所有公开的8角色的简略信息
[ysc (uid) 角色名]查看公开的8角色的详细信息
*绑定私人cookie之后就可以查看所有角色啦
--------
[ssbq/实时便签 (uid)]查询当前树脂、洞天宝钱、派遣状况等
[ssbq (uid) 开启提醒(树脂数)/关闭提醒]开启/关闭树脂提醒，达到树脂数时会在群里艾特你
*绑定私人cookie之后才能使用
--------
[sy/深渊查询/深境螺旋查询 (uid) (层数)]查询深渊战绩信息
*绑定私人cookie之后才能查看层数具体阵容哦
--------
[mys签到]手动进行一次米游社原神签到
[mys自动签到开启uid/关闭]开启米游社原神自动签到
--------
[myzj/每月札记/zj (uid) (月份)]查看该月份获得的原石、摩拉数
*绑定私人cookie之后才能使用,只能查看最近3个月的记录,默认为本月
--------
[ysb cookie]绑定你的私人cookie以开启高级功能
[删除ck]删除你的私人cookie
[添加公共ck cookie]添加公共cookie以供大众查询*仅管理员
'''

__help_version__ = '1.1.0'

sy = on_command('sy', aliases={'深渊信息', '深境螺旋信息'}, priority=7, block=True)
ssbq = on_command('ssbq', aliases={'实时便笺', '实时便签', '当前树脂'}, priority=7, block=True)
myzj = on_command('myzj', aliases={'札记信息', '每月札记'}, priority=7, block=True)
ys = on_command('ys', aliases={'原神卡片', '个人卡片'}, priority=7, block=True)
ysa = on_command('ysa', aliases={'角色背包'}, priority=7, block=True)
ysc = on_command('ysc', aliases={'角色卡片', '角色详情'}, priority=7, block=True)
ysb = on_command('ysb', aliases={'原神绑定', '绑定cookie'}, priority=7, block=True)
mys_sign = on_command('mys_sign', aliases={'mys签到', '米游社签到'}, priority=7, block=True)
mys_sign_auto = on_command('mys_sign_auto', aliases={'mys自动签到', '米游社自动签到'}, priority=7, block=True)
mys_sign_all = on_command('mys_sign_all', aliases={'全部重签'}, priority=7, permission=SUPERUSER, rule=to_me(), block=True)
add_public_ck = on_command('add_ck', aliases={'添加公共cookie', '添加公共ck'}, permission=SUPERUSER, priority=7, block=True)
delete_ck = on_command('delete_ck', aliases={'删除ck', '删除cookie'}, priority=7, block=True)


@sy.handle()
@exception_handler()
async def sy_handler(event: MessageEvent, msg: Message = CommandArg()):
    uid, msg, user_id, use_cache = await get_uid_in_msg(event, msg)
    if not uid:
        await sy.finish('请把正确的uid给派蒙哦,例如sy100123456!', at_sender=True)
    if not msg:
        floor = []
    else:
        floor = msg.split(' ')
    true_floor = []
    for f in floor:
        if f.isdigit() and (9 <= int(f) <= 12) and len(true_floor) < 2:
            true_floor.append(int(f))
    true_floor.sort()
    data = await get_abyss_data(user_id, uid, use_cache=use_cache)
    if isinstance(data, str):
        await sy.finish(data, at_sender=True)
    else:
        abyss_card = await draw_abyss_card(data, uid, true_floor)
        await sy.finish(abyss_card, at_sender=True)


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
            await ssbq.finish('关闭提醒成功', at_sender=True)
            await update_note_remind2(user_id, uid, gid, 0)
        elif find_remind_enable.group('action') == '删除提醒':
            await ssbq.finish('删除提醒成功', at_sender=True)
            await delete_note_remind(user_id, uid)
    else:
        data = await get_daily_note_data(uid)
        if isinstance(data, str):
            await ssbq.finish(data, at_sender=True)
        else:
            daily_note_card = await draw_daily_note_card(data, uid)
            await ssbq.finish(daily_note_card, at_sender=True)


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
        month_list = [str(month_now - 2), str(month_now - 1)]
    find_month = '(?P<month>' + '|'.join(month_list) + ')'
    match = re.search(find_month, msg)
    month = match.group('month') if match else month_now
    data = await get_monthinfo_data(uid, month, use_cache=use_cache)
    if isinstance(data, str):
        await myzj.finish(data, at_sender=True)
    else:
        monthinfo_card = await draw_monthinfo_card(data)
        await myzj.finish(monthinfo_card, at_sender=True)


@ys.handle()
@exception_handler()
async def ys_handler(bot: Bot, event: MessageEvent, msg: Message = CommandArg()):
    uid, msg, user_id, use_cache = await get_uid_in_msg(event, msg)
    if not uid:
        await ys.finish('请把正确的uid给派蒙哦,例如ys100123456!', at_sender=True)
    data = await get_player_card_data(user_id, uid, use_cache=use_cache)
    if isinstance(data, str):
        await ys.finish(data, at_sender=True)
    else:
        if event.message_type == 'group':
            user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=int(user_id))
            nickname = user_info['card'] or user_info['nickname']
        else:
            nickname = event.sender.nickname
        chara_data = await get_chara_detail_data(user_id, uid, use_cache=use_cache)
        chara_data = None if isinstance(chara_data, str) else chara_data
        player_card = await draw_player_card(data, chara_data, uid, nickname)
        await ys.finish(player_card, at_sender=True)


@ysa.handle()
@exception_handler()
async def ysa_handler(event: MessageEvent, msg: Message = CommandArg()):
    uid, msg, user_id, use_cache = await get_uid_in_msg(event, msg)
    if not uid:
        await ysa.finish('请把正确的uid给派蒙哦,例如ysa100123456!', at_sender=True)

    chara_data = await get_chara_detail_data(user_id, uid, use_cache=use_cache)
    if isinstance(chara_data, str):
        await ysa.finish(chara_data, at_sender=True)
    else:
        player_card = await draw_all_chara_card(chara_data, uid)
        await ysa.finish(player_card, at_sender=True)


@ysc.handle()
@exception_handler()
async def ysc_handler(event: MessageEvent, msg: Message = CommandArg()):
    uid, msg, user_id, use_cache = await get_uid_in_msg(event, msg)
    if not uid:
        await ysc.finish('请把正确的uid给派蒙哦,例如ysc100123456钟离', at_sender=True)
    if not msg:
        await ysc.finish(f'要把角色名给派蒙呀!例如ysc100123456钟离', at_sender=True)
    chara = msg.split(' ')[0]
    chara_name = get_id_by_alias(chara)
    if not chara_name:
        await ysc.finish(f'没有角色名叫{chara}哦！', at_sender=True)

    chara_data = await get_chara_detail_data(user_id, uid, use_cache=use_cache)
    if isinstance(chara_data, str):
        await ysc.finish(chara_data, at_sender=True)
    else:
        skill_data = await get_chara_skill_data(uid, chara_name[0], use_cache=use_cache)
        chara_card = await draw_chara_card(chara_data, skill_data, chara_name, uid)
        await ysc.finish(chara_card, at_sender=True)


cookie_error_msg = '这个cookie无效哦，请旅行者确认是否正确\n1.ck要登录mys帐号后获取,且不能退出登录\n2.ck中要有cookie_token和account_id两个参数\n3.建议在无痕模式下取'


@ysb.handle()
@exception_handler()
async def ysb_handler(event: MessageEvent, msg: Message = CommandArg()):
    cookie = str(msg).strip()
    if cookie == '':
        res = '''旅行者好呀，你可以直接用ys/ysa等指令附上uid来使用派蒙\n如果想看全部角色信息和实时便笺等功能，要把cookie给派蒙哦\ncookie
        获取方法：登录网页版米游社，在地址栏粘贴代码：\njavascript:(function(){prompt(document.domain,document.cookie)})(
        );\n复制弹窗出来的字符串（手机要via或chrome浏览器才行）\n然后添加派蒙私聊发送ysb接刚刚复制的字符串，例如:ysb 
        UM_distinctid=17d131d...\ncookie是账号重要安全信息，请确保机器人持有者可信赖！ '''
        await ysb.finish(res, at_sender=True)
    else:
        cookie_info, mys_id = await get_bind_game(cookie)
        if not cookie_info or cookie_info['retcode'] != 0:
            msg = cookie_error_msg
            if event.message_type != 'private':
                msg += '\n当前是在群聊里绑定，建议旅行者添加派蒙好友私聊绑定!'
            await ysb.finish(msg, at_sender=True)
        else:
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
                await ysb.finish(msg, at_sender=True)


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
        if isinstance(sign_action, str):
            await mys_sign.finish(sign_action, at_sender=True)
        else:
            await mys_sign.finish(
                f'签到成功,获得的奖励为:\n{sign_list["data"]["awards"][sign_day]["name"]} * {sign_list["data"]["awards"][sign_day]["cnt"]}',
                at_sender=True)


@mys_sign_auto.handle()
@exception_handler()
async def mys_sign_auto_handler(event: MessageEvent, msg: Message = CommandArg()):
    if event.message_type != 'group':
        await mys_sign_auto.finish('自动签到功能暂时只限Q群内使用哦')
    msg = str(msg).strip()
    find_uid = re.search(r'(?P<uid>(1|2|5)\d{8})', msg)
    if not find_uid:
        await mys_sign_auto.finish('请把正确的需要帮忙签到的uid给派蒙哦!', at_sender=True)
    else:
        uid = find_uid.group('uid')
        find_action = re.search(r'(?P<action>开启|启用|打开|关闭|禁用)', msg)
        if find_action:
            if find_action.group('action') in ['开启', '启用', '打开']:
                cookie = await get_private_cookie(uid, key='uid')
                if not cookie:
                    await mys_sign_auto.finish('你的该uid还没绑定cookie哦，先用ysb绑定吧!', at_sender=True)
                await add_auto_sign(str(event.user_id), uid, str(event.group_id))
                await mys_sign_auto.finish('开启米游社自动签到成功,派蒙会在每日0点帮你签到', at_sender=True)
            elif find_action.group('action') in ['关闭', '禁用']:
                await delete_auto_sign(str(event.user_id), uid)
                await mys_sign_auto.finish('关闭米游社自动签到成功', at_sender=True)
        else:
            await add_auto_sign(str(event.user_id), uid, str(event.group_id))
            await mys_sign_auto.finish('开启米游社自动签到成功,派蒙会在每日0点帮你签到', at_sender=True)


@mys_sign_all.handle()
async def sign_all():
    await auto_sign()


@scheduler.scheduled_job('cron', hour=config.paimon_sign_hour, minute=config.paimon_sign_minute)
async def auto_sign():
    data = await get_auto_sign()
    if data:
        ann = defaultdict(lambda: defaultdict(list))
        logger.info('---派蒙开始执行米游社自动签到---')
        sign_list = await get_sign_list()
        for user_id, uid, group_id in data:
            await sleep(random.randint(3, 8))
            sign_result = await sign(uid)
            if not isinstance(sign_result, str):
                await sleep(1)
                sign_info = await get_sign_info(uid)
                sign_day = sign_info['data']['total_sign_day'] - 1
                ann[group_id]['成功'].append(
                    f'.UID{uid}-{sign_list["data"]["awards"][sign_day]["name"]}*{sign_list["data"]["awards"][sign_day]["cnt"]}')
            else:
                await delete_auto_sign(user_id, uid)
                ann[group_id]['失败'].append(f'.UID{uid}')
        for group_id, content in ann.items():
            group_str = '米游社自动签到结果：\n'
            for type, ann_list in content.items():
                if ann_list:
                    group_str += f'签到{type}：\n'
                    for u in ann_list:
                        group_str += str(ann_list.index(u) + 1) + u + '\n'
            try:
                await get_bot().send_group_msg(group_id=group_id, message=group_str)
                await sleep(random.randint(3, 8))
            except Exception as e:
                logger.error(f'米游社签到结果发送失败：{e}')


@scheduler.scheduled_job('cron', minute=f'*/{config.paimon_check_interval}')
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
                await sleep(3)


@scheduler.scheduled_job('cron', hour=0)
async def daily_update():
    logger.info('---清空今日树脂提醒限制---')
    await update_day_remind_count()
    logger.info('---清空今日cookie缓存---')
    await delete_cookie_cache(all=True)
    logger.info('---清空今日cookie限制记录---')
    await reset_public_cookie()

