import datetime
import re
from asyncio import sleep

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, PrivateMessageEvent
from nonebot.params import CommandArg, ArgPlainText
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from LittlePaimon.config import config
from LittlePaimon.database import LastQuery, PrivateCookie, PublicCookie, Character, PlayerInfo, DailyNoteSub, \
    MihoyoBBSSub
from LittlePaimon.utils import logger, NICKNAME
from LittlePaimon.utils.api import get_bind_game_info, get_stoken_by_login_ticket, get_cookie_token_by_stoken

try:
    from .get_cookie import *
except ImportError:
    logger.info('原神绑定', '导入扫码绑定功能<r>失败</r>，请检查是否已安装<m>qrcode</m>库(运行<m>poetry run pip install qrcode</m>)')
    bind_tips = '获取cookie的教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1\n获取后，使用[ysb cookie]指令绑定'
    bind_tips_web = '获取cookie的教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1\n获取后，使用[ysb cookie]指令绑定或前往{cookie_web_url}网页添加绑定'

__plugin_meta__ = PluginMetadata(
    name='原神绑定',
    description='原神绑定信息',
    usage='ysb',
    extra={
        'author':   '惜月',
        'version':  '3.0',
        'priority': 2,
    }
)

ysb = on_command('ysb', aliases={'原神绑定', '绑定uid', '绑定UID'}, priority=1, block=True, state={
    'pm_name':        'ysb',
    'pm_description': '绑定原神uid或者cookie',
    'pm_usage':       'ysb[uid|cookie]',
    'pm_priority':    1
})
ysbc = on_command('ysbc', aliases={'查询ck', '查询绑定', '绑定信息', '校验绑定'}, priority=1, block=True, state={
    'pm_name':        'ysbc',
    'pm_description': '查询已绑定的原神cookie情况',
    'pm_usage':       'ysbc',
    'pm_priority':    2
})
delete_ck = on_command('删除ck', aliases={'删除cookie'}, priority=1, block=True, state={
    'pm_name':        '删除ck',
    'pm_description': '删除你qq下绑定的cookie和订阅信息',
    'pm_usage':       '删除ck[uid|全部]',
    'pm_priority':    3
})
ysbca = on_command('校验所有ck', aliases={'校验所有cookie', '校验所有绑定'}, priority=1, block=True,
                   permission=SUPERUSER, state={
        'pm_name':        '校验所有ck',
        'pm_description': '校验所有cookie情况，仅超级管理员可用',
        'pm_usage':       '校验所有ck',
        'pm_priority':    4
    })
pck = on_command('添加公共cookie', aliases={'添加pck', '添加公共ck', 'add_pck'}, permission=SUPERUSER, block=True,
                 priority=1,
                 state={
                     'pm_name':        '添加公共ck',
                     'pm_description': '添加公共cookie，仅超级管理员可用',
                     'pm_usage':       '添加公共ck[cookie]',
                     'pm_priority':    5
                 })
clear = on_command('清除无效用户', permission=SUPERUSER, block=True, priority=1, state={
    'pm_name':        '清除无效用户',
    'pm_description': '清除所有已退群或已删好友的用户的cookie、订阅等信息，仅超级管理员可用',
    'pm_usage':       '清除无效用户',
    'pm_priority':    6
})
refresh_ck = on_command('刷新ck', aliases={'刷新cookie'}, priority=1, block=True, state={
    'pm_name':        '刷新ck',
    'pm_description': '如果你的cookie疑似失效了，可尝试使用该指令刷新cookie',
    'pm_usage':       '刷新ck',
    'pm_priority':    7
})
ysch = on_command('ysch', aliases={'原神切换', '切换uid', '切换UID'}, priority=1, block=True, state={
    'pm_name':        'ysch',
    'pm_description': '切换当前绑定的UID至下一个或指定序号的UID',
    'pm_usage':       'ysch[序号]',
    'pm_priority':    8
})


@ysch.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    if not (cookie_list := await PrivateCookie.filter(user_id=str(event.user_id))):
        await ysch.finish(f'你还没有绑定过Cookie的UID，如需绑定cookie可看教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1',
                          at_sender=True)
    if len(cookie_list) == 1:
        await ysch.finish(f'你只绑定了一个UID{cookie_list[0].uid}，无需切换', at_sender=True)
    uid_list = [i.uid for i in cookie_list]
    uid_list_text = '\n'.join([f'{uid_list.index(i) + 1}.{i}' for i in uid_list])
    msg = msg.extract_plain_text().strip()
    if msg.isdigit():
        # 如果指令后面跟了数字序号，就切换到对应序号的UID
        num = int(msg)
        if len(cookie_list) >= num:
            await LastQuery.update_or_create(user_id=str(event.user_id),
                                             defaults={'uid':       cookie_list[num - 1].uid,
                                                       'last_time': datetime.datetime.now()})
            await ysch.finish(f'当前已切换至UID{cookie_list[num - 1].uid}\n\n已绑定的UID有：{uid_list_text}\n可使用[切换uid 序号]来切换至指定UID',
                              at_sender=True)
        else:
            await ysch.finish(
                f'你没有绑定那么多UID哦\n已绑定的UID有：{uid_list_text}\n可使用[切换uid 序号]来切换至指定UID',
                at_sender=True)
    else:
        cache_uid = await LastQuery.get_or_none(user_id=str(event.user_id))
        if cache_uid and cache_uid.uid in uid_list:
            index = uid_list.index(cache_uid.uid)
            if index == len(uid_list) - 1:
                # 如果当前UID是最后一个，那么切换至第一个
                index = 0
            else:
                # 否则切换至下一个
                index += 1
            current_uid = cookie_list[index].uid
        else:
            current_uid = cookie_list[0].uid
        await LastQuery.update_or_create(user_id=str(event.user_id),
                                         defaults={'uid': current_uid, 'last_time': datetime.datetime.now()})
        await ysch.finish(f'当前已切换至UID{current_uid}\n\n已绑定的UID有：{uid_list_text}\n可使用[切换uid 序号]来切换至指定UID', at_sender=True)


@ysb.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    msg = msg.extract_plain_text().strip()
    if uid := re.match(r'[125]\d{8}', msg):
        await LastQuery.update_or_create(user_id=str(event.user_id),
                                         defaults={'uid': uid[0], 'last_time': datetime.datetime.now()})
        msg = msg.replace(uid[0], '').strip()
        if not msg:
            await ysb.finish(f'成功绑定uid为{uid[0]}，如果还需绑定cookie可看教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1',
                             at_sender=True)
    if msg:
        if msg in {'cookie', 'Cookie', 'ck', 'CK'}:
            await ysb.finish(f'你在和{NICKNAME}开玩笑嘛？请看教程获取Cookie：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1',
                             at_sender=True)
        if mys_id := re.search(r'(?:(?:login_uid|account_mid|account_id|stmid|ltmid|stuid|ltuid)(?:_v2)?)=(\d+)', msg):
            mys_id = mys_id[1]
        else:
            await ysb.finish(
                'Cookie无效，缺少account_id、login_uid或stuid字段\n获取cookie的教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1',
                at_sender=True)
        cookie_token_match = re.search(r'(?:cookie_token|cookie_token_v2)=([0-9a-zA-Z]+)', msg)
        cookie_token = cookie_token_match[1] if cookie_token_match else None
        login_ticket_match = re.search(r'(?:login_ticket|login_ticket_v2)=([0-9a-zA-Z]+)', msg)
        login_ticket = login_ticket_match[1] if login_ticket_match else None
        stoken_match = re.search(r'(?:stoken|stoken_v2)=([0-9a-zA-Z]+)', msg)
        stoken = stoken_match[1] if stoken_match else None
        if login_ticket and not stoken:
            # 如果有login_ticket但没有stoken，就通过login_ticket获取stoken
            stoken = await get_stoken_by_login_ticket(login_ticket, mys_id)
        if stoken and not cookie_token:
            # 如果有stoken但没有cookie_token，就通过stoken获取cookie_token
            cookie_token = await get_cookie_token_by_stoken(stoken, mys_id)
        if not cookie_token:
            await ysb.finish(
                'Cookie无效，缺少cookie_token或login_ticket字段\n获取cookie的教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1',
                at_sender=True)
        if game_info := await get_bind_game_info(f'account_id={mys_id};cookie_token={cookie_token}', mys_id):
            if not game_info['list']:
                await ysb.finish('该账号尚未绑定任何游戏，请确认账号无误~', at_sender=True)
            if not (
                    genshin_games := [{'uid': game['game_role_id'], 'nickname': game['nickname']} for game in
                                      game_info['list']
                                      if game['game_id'] == 2]):
                await ysb.finish('该账号尚未绑定原神，请确认账号无误~', at_sender=True)
            await LastQuery.update_or_create(user_id=str(event.user_id),
                                             defaults={'uid':       genshin_games[0]['uid'],
                                                       'last_time': datetime.datetime.now()})
            send_msg = ''
            for info in genshin_games:
                send_msg += f'{info["nickname"]}({info["uid"]}) '
                await PrivateCookie.update_or_create(user_id=str(event.user_id), uid=info['uid'], mys_id=mys_id,
                                                     defaults={
                                                         'cookie': f'account_id={mys_id};cookie_token={cookie_token}',
                                                         'stoken': f'stuid={mys_id};stoken={stoken};' if stoken else None})
            await ysb.finish(
                f'玩家{send_msg.strip()}绑定Cookie{"和Stoken" if stoken else ""}成功{"" if stoken else "当未能绑定Stoken"}{"" if isinstance(event, PrivateMessageEvent) else "，当前非私聊对话建议将Cookie撤回哦"}',
                at_sender=True,
            )
        else:
            await ysb.finish(
                'Cookie无效，请确认是否已过期\n获取cookie的教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1',
                at_sender=True)
    elif config.CookieWeb_enable:
        await ysb.finish(bind_tips_web.format(cookie_web_url=config.CookieWeb_url), at_sender=True)
    else:
        await ysb.finish(bind_tips, at_sender=True)


@ysbc.handle()
async def _(event: MessageEvent):
    logger.info('原神Cookie', f'开始校验{str(event.user_id)}的绑定情况')
    ck = await PrivateCookie.filter(user_id=str(event.user_id))
    uid = await LastQuery.get_or_none(user_id=str(event.user_id))
    if ck:
        msg = f'{event.sender.card or event.sender.nickname}当前绑定情况:\n'
        for ck_ in ck:
            if await get_bind_game_info(ck_.cookie, ck_.mys_id):
                msg += f'{ck.index(ck_) + 1}.{ck_.uid}(有效)\n'
            else:
                msg += f'{ck.index(ck_) + 1}.{ck_.uid}(已失效)\n'
                await ck_.delete()
                logger.info('原神Cookie', '➤', {'用户': str(event.user_id), 'uid': ck_.uid}, 'cookie已失效', False)

        await ysbc.finish(msg.strip(), at_sender=True)
    elif uid:
        await ysbc.finish(f'{event.sender.card or event.sender.nickname}当前已绑定uid{uid.uid}，但未绑定cookie',
                          at_sender=True)

    else:
        await ysbc.finish(f'{event.sender.card or event.sender.nickname}当前无绑定信息', at_sender=True)


@delete_ck.handle()
async def _(event: MessageEvent, state: T_State, msg: Message = CommandArg()):
    if uids := await PrivateCookie.filter(user_id=str(event.user_id)):
        state['msg'] = '你已绑定cookie的uid有：\n' + '\n'.join([uid.uid for uid in uids]) + '\n请选择要删除的uid'
        state['uids'] = [uid.uid for uid in uids]
    else:
        await delete_ck.finish('你没有绑定过任何cookie哦', at_sender=True)
    if '全部' in msg.extract_plain_text():
        state['uid'] = Message('全部')
    elif uid := re.search(r'[125]\d{8}', msg.extract_plain_text().strip()):
        state['uid'] = Message(uid.group())


@delete_ck.got('uid', prompt=Message.template('{msg}，或者发送[全部]解绑cookie'))
async def _(event: MessageEvent, state: T_State, uid: str = ArgPlainText('uid')):
    if uid == '全部':
        await PrivateCookie.filter(user_id=str(event.user_id)).delete()
        await DailyNoteSub.filter(user_id=event.user_id).delete()
        await MihoyoBBSSub.filter(user_id=event.user_id).delete()
        await delete_ck.finish('已删除你号下绑定的ck和订阅信息', at_sender=True)
    elif uid in state['uids']:
        await PrivateCookie.filter(user_id=str(event.user_id), uid=uid).delete()
        await DailyNoteSub.filter(user_id=event.user_id, uid=uid).delete()
        await MihoyoBBSSub.filter(user_id=event.user_id, uid=uid).delete()
        await delete_ck.finish(f'已删除UID{uid}绑定的ck和订阅信息', at_sender=True)
    else:
        await delete_ck.finish(state['msg'], at_sender=True)


@ysbca.handle()
async def _(event: MessageEvent):
    logger.info('原神Cookie', '开始校验所有cookie情况')
    await ysbc.send('开始校验全部cookie，请稍等...', at_sender=True)
    private_cookies = await PrivateCookie.all()
    public_cookies = await PublicCookie.all()
    useless_private = []
    useless_public = []
    for cookie in private_cookies:
        if not await get_bind_game_info(cookie.cookie, cookie.mys_id):
            useless_private.append(cookie.uid)
            await cookie.delete()
        await sleep(1)
    for cookie in public_cookies:
        if mys_id := re.search(r'(?:(?:login_uid|account_mid|account_id|stmid|ltmid|stuid|ltuid)(?:_v2)?)=(\d+)',
                               cookie.cookie):
            mys_id = mys_id[1]
            if not await get_bind_game_info(cookie.cookie, mys_id):
                useless_public.append(str(cookie.id))
                await cookie.delete()
        else:
            useless_public.append(str(cookie.id))
        await sleep(0.5)
    msg = f'当前共{len(public_cookies)}个公共ck，{len(private_cookies)}个私人ck。\n'
    if useless_public:
        msg += '其中失效的公共ck有:' + ' '.join(useless_public) + '\n'
    else:
        msg += '公共ck全部有效\n'
    if useless_private:
        msg += '其中失效的私人ck有:' + ' '.join(useless_private) + '\n'
    else:
        msg += '私人ck全部有效\n'
    await ysbca.finish(msg, at_sender=True)


@pck.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    if msg := msg.extract_plain_text().strip():
        if mys_id := re.search(r'(?:(?:login_uid|account_mid|account_id|stmid|ltmid|stuid|ltuid)(?:_v2)?)=(\d+)', msg):
            mys_id = mys_id[1]
        else:
            await pck.finish(
                'Cookie无效，缺少account_id、login_uid或stuid字段\n获取cookie的教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1',
                at_sender=True)
        cookie_token_match = re.search(r'(?:cookie_token|cookie_token_v2)=([0-9a-zA-Z]+)', msg)
        cookie_token = cookie_token_match[1] if cookie_token_match else None
        login_ticket_match = re.search(r'(?:login_ticket|login_ticket_v2)=([0-9a-zA-Z]+)', msg)
        login_ticket = login_ticket_match[1] if login_ticket_match else None
        stoken_match = re.search(r'(?:stoken|stoken_v2)=([0-9a-zA-Z]+)', msg)
        stoken = stoken_match[1] if stoken_match else None
        if login_ticket and not stoken:
            # 如果有login_ticket但没有stoken，就通过login_ticket获取stoken
            stoken = await get_stoken_by_login_ticket(login_ticket, mys_id)
        if stoken and not cookie_token:
            # 如果有stoken但没有cookie_token，就通过stoken获取cookie_token
            cookie_token = await get_cookie_token_by_stoken(stoken, mys_id)
        if not cookie_token:
            await pck.finish(
                'Cookie无效，缺少cookie_token或login_ticket字段\n获取cookie的教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1',
                at_sender=True)
        if await get_bind_game_info(f'account_id={mys_id};cookie_token={cookie_token}', mys_id):
            ck = await PublicCookie.create(cookie=f'account_id={mys_id};cookie_token={cookie_token}')
            logger.info('原神Cookie', f'{ck.id}号公共cookie', None, '添加成功', True)
            await pck.finish(f'成功添加{ck.id}号公共cookie', at_sender=True)
        else:
            logger.info('原神Cookie', '公共cookie', None, '添加失败，cookie已失效', True)
            await pck.finish('Cookie无效，请确认是否已过期\n获取cookie的教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1',
                             at_sender=True)
    else:
        await pck.finish('获取cookie的教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1\n获取到后，用[添加公共ck cookie]指令添加',
                         at_sender=True)


@clear.handle()
async def _(bot: Bot, event: MessageEvent):
    total_user_list = []
    group_list = await bot.get_group_list()
    for group in group_list:
        group_member_list = await bot.get_group_member_list(group_id=group['group_id'])
        for member in group_member_list:
            if member['user_id'] not in total_user_list:
                total_user_list.append(member['user_id'])
    friend_list = await bot.get_friend_list()
    for friend in friend_list:
        if friend['user_id'] not in total_user_list:
            total_user_list.append(friend['user_id'])
    # 删除私人cookie
    all_private_cookies = await PrivateCookie.all()
    for ck in all_private_cookies:
        if int(ck.user_id) not in total_user_list:
            logger.info('原神Cookie', '私人cookie', {'用户': ck.user_id, 'UID': ck.uid}, '已清除', True)
            await ck.delete()
    # 删除最后查询记录
    all_last_query = await LastQuery.all()
    for q in all_last_query:
        if int(q.user_id) not in total_user_list:
            await q.delete()
    # 删除原神玩家信息
    all_player = await PlayerInfo.all()
    for p in all_player:
        if int(p.user_id) not in total_user_list:
            await p.delete()
    # 删除原神角色
    all_character = await Character.all()
    for chara in all_character:
        if int(chara.user_id) not in total_user_list:
            await chara.delete()
    # # 删除通用订阅信息
    # all_sub = await GeneralSub.all()
    # for s in all_sub:
    #     if int(s.sub_id) not in total_user_list:
    #         await s.delete()
    # 删除原神树脂提醒信息
    all_note = await DailyNoteSub.all()
    for n in all_note:
        if int(n.user_id) not in total_user_list:
            await n.delete()
    # 删除米游社签到及获取信息
    all_sign = await MihoyoBBSSub.all()
    for s in all_sign:
        if int(s.user_id) not in total_user_list:
            await s.delete()

    await clear.finish('清除完成', at_sender=True)


@refresh_ck.handle()
async def _(event: MessageEvent):
    cks = await PrivateCookie.filter(user_id=str(event.user_id))
    if cks:
        mys_id_done = []
        refresh_done = []
        for ck in cks:
            if ck.mys_id not in mys_id_done and ck.stoken is not None:
                mys_id_done.append(ck.mys_id)
                if new_cookie := await get_cookie_token_by_stoken(ck.stoken.split('stoken=')[-1], ck.mys_id):
                    await PrivateCookie.filter(user_id=str(event.user_id), mys_id=ck.mys_id).update(
                        cookie=f'account_id={ck.mys_id};cookie_token={new_cookie}', status=1)
                    refresh_done.append(ck.mys_id)
        if not refresh_done:
            await refresh_ck.finish('刷新cookie失败，请重新绑定', at_sender=True)
        else:
            await refresh_ck.finish(f'成功刷新米游社ID为{"、".join(refresh_done)}的账号的cookie', at_sender=True)
    else:
        await refresh_ck.finish('你还未绑定私人cookie或过期太久已被移除，请重新绑定', at_sender=True)
