import re

from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, Message
from nonebot.internal.params import Arg
from nonebot.params import CommandArg
from nonebot.typing import T_State

from LittlePaimon.database.models import LastQuery
from LittlePaimon.utils import MessageBuild
from LittlePaimon.utils import transform_uid, get_match_alias
from LittlePaimon.utils.enka import PlayerInfo
from .data_source import get_enka_data
from .draw import draw_role_card


update_info = on_command('udi', aliases={'更新角色信息', '更新角色面板', '更新玩家信息'}, priority=6, block=True)
role_info = on_command('角色面板', aliases={'角色详情', '角色信息', 'ysd'}, block=True, priority=7)


@update_info.handle()
async def _(event: MessageEvent, state: T_State, msg: Message = CommandArg()):
    uid = re.search(r'(?P<uid>(1|2|5)\d{8})', msg.extract_plain_text())
    if uid:
        state['uid'] = uid.group('uid')
    else:
        user = ''
        for msg_seg in msg:
            if msg_seg.type == "at":
                user = msg_seg.data['qq']
                break
        if user:
            uid = await LastQuery.get_uid(str(user))
            if uid:
                state['uid'] = uid
        else:
            uid = await LastQuery.get_uid(str(event.user_id))
            if uid:
                state['uid'] = uid
    # if 'uid' in state and not ud_lmt.check(state['uid']):
    #     await update_info.finish(f'每个uid每5分钟才能更新一次信息，请稍等一下吧~(剩余{ud_lmt.left_time(state["uid"])}秒)')
    # if not ud_p_lmt.check(get_message_id(event)):
    #     await update_info.finish(f'每个会话每15秒才能更新一次信息，请稍等一下吧~(剩余{ud_lmt.left_time(get_message_id(event))}秒)')


@update_info.got('uid', prompt='请把要更新的uid给派蒙哦~')
# @exception_handler()
async def _(event: MessageEvent, uid: Message = Arg('uid')):
    uid = transform_uid(uid)
    if not uid:
        await update_info.finish('这好像不是一个正确的uid哦~，请检查一下', at_sender=True)
    await LastQuery.update_uid(str(event.user_id), uid)

    await update_info.send('派蒙开始更新信息~请稍等哦~')
    enka_data = await get_enka_data(uid)
    if not enka_data:
        if uid[0] == '5' or uid[0] == '2':
            await update_info.finish('暂不支持B服账号哦~请等待开发者更新吧~')
        else:
            await update_info.finish('派蒙没有查到该uid的信息哦~')
    # ud_lmt.start_cd(uid, 300)
    # ud_lmt.start_cd(get_message_id(event), 15)
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
    uid = re.search(r'(?P<uid>(1|2|5)\d{8})', msg.extract_plain_text())
    if uid:
        state['uid'] = uid.group('uid')
        await LastQuery.update_uid(str(event.user_id), uid.group('uid'))
    else:
        user = ''
        for msg_seg in msg:
            if msg_seg.type == "at":
                user = msg_seg.data['qq']
        if user:
            uid = await LastQuery.get_uid(str(user))
            if uid:
                state['uid'] = uid
        else:
            uid = await LastQuery.get_uid(str(event.user_id))
            if uid:
                state['uid'] = uid
    msg = msg.extract_plain_text().replace(state['uid'] if 'uid' in state else 'ysd', '').strip()
    if not msg:
        await role_info.finish('请把要查询角色名给派蒙哦~')
    if msg.startswith(('a', '全部', '所有', '查看')):
        state['role'] = 'all'
    else:
        match_alias = get_match_alias(msg, 'roles', True)
        if match_alias:
            state['role'] = match_alias if isinstance(match_alias, str) else tuple(match_alias.keys())[0]
        else:
            await role_info.finish(MessageBuild.Text(f'哪有名为{msg}的角色啊，别拿派蒙开玩笑!'))


@role_info.got('uid', prompt='请把要查询的uid给派蒙哦~')
# @exception_handler()
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
        await role_info.finish(MessageBuild.Text(f'派蒙还没有你{role}的信息哦，先用 更新角色信息 命令更新吧~'), at_sender=True)
    else:
        role_data = player_info.get_roles_info(role)
        img = await draw_role_card(uid, role_data)
        await role_info.finish(img)
