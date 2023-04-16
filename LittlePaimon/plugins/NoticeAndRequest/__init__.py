import asyncio
import random
import datetime
from typing import Dict

from nonebot import on_command, on_notice, on_request
from nonebot.rule import Rule
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg, ArgPlainText
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, PrivateMessageEvent, FriendRequestEvent, \
    GroupRequestEvent, \
    RequestEvent, NoticeEvent, \
    GroupIncreaseNoticeEvent, FriendAddNoticeEvent, GroupMessageEvent, \
    ActionFailed
from nonebot.typing import T_State

from LittlePaimon.config import config as bot_config
from LittlePaimon.utils import scheduler, logger, NICKNAME, SUPERUSERS
from LittlePaimon.utils.message import format_message, replace_all
from .config import config

requests_list: Dict[str, Dict[str, Dict[str, any]]] = {
    '好友': {},
    '群':  {}
}
done: Dict[str, datetime.datetime] = {}  # 防止gocq重复上报事件导致多次处理


async def InviteRule(event: RequestEvent) -> bool:
    if not bot_config.request_event:
        return False
    if isinstance(event, FriendRequestEvent):
        return f'add_friend_{event.user_id}' not in done.keys()
    elif isinstance(event, GroupRequestEvent) and event.sub_type == 'invite':
        return f'add_group_{event.group_id}' not in done.keys()
    return False


async def IncreaseRule(event: NoticeEvent) -> bool:
    if not bot_config.notice_event:
        return False
    if isinstance(event, FriendAddNoticeEvent):
        return f'new_friend_{event.user_id}' not in done.keys()
    elif isinstance(event, GroupIncreaseNoticeEvent):
        return f'new_group_{event.group_id}' not in done.keys() and f'new_member_{event.group_id}_{event.user_id}' not in done.keys() and '全部' not in config.group_ban
    return False


approve_request = on_command('同意', priority=1, block=True, permission=SUPERUSER)
ban_greet = on_command('入群欢迎', priority=1, block=True, permission=SUPERUSER)
requests = on_request(priority=1, rule=Rule(InviteRule), block=True)
notices = on_notice(priority=1, rule=Rule(IncreaseRule), block=True)


@approve_request.handle()
async def _(event: PrivateMessageEvent, state: T_State, msg: Message = CommandArg()):
    msg = msg.extract_plain_text().strip()
    if not msg:
        await approve_request.finish('用法：同意<好友/群>[群号/qq号]，例如：同意好友123456')
    if msg.startswith('好友'):
        state['type'] = '好友'
        msg = msg.replace('好友', '').strip()
    elif msg.startswith('群'):
        state['type'] = '群'
        msg = msg.replace('群', '').strip()
    if not requests_list[state['type']]:
        await approve_request.finish(f'没有待处理的{state["type"]}请求')
    elif msg == '全部':
        state['id'] = Message('全部')
    elif msg in requests_list[state['type']].keys():
        state['id'] = Message(msg)
    else:
        state['id_list'] = '\n'.join([f'{v["name"]}({k})' for k, v in requests_list[state['type']].items()])


@approve_request.got('id', prompt=Message.template('你要同意的是以下哪个{type}:\n{id_list}\n请发送号码，或"全部"来同意全部请求'))
async def _(event: PrivateMessageEvent, bot: Bot, state: T_State, id_: str = ArgPlainText('id')):
    if id_ == '全部':
        for id__, info in requests_list[state['type']].items():
            if state['type'] == '好友':
                await bot.set_friend_add_request(flag=info['flag'], approve=True)
                del requests_list['好友'][id__]
                logger.info('好友添加请求', '', {'好友': id__}, '已同意', True)
            elif state['type'] == '群':
                await bot.set_group_add_request(flag=info['flag'], sub_type='invite', approve=True)
                del requests_list['群'][id__]
                logger.info('群邀请请求', '', {'群': id__}, '已同意', True)
            await asyncio.sleep(0.75)
        await approve_request.finish(f'已同意全部{state["type"]}请求')
    if id_ not in requests_list[state['type']].keys():
        await approve_request.reject(Message.template('请发送要同意的{type}号码:\n{id_list}'))
    else:
        flag = requests_list[state['type']][id_]['flag']
        if state['type'] == '好友':
            await bot.set_friend_add_request(flag=flag, approve=True)
            del requests_list['好友'][id_]
            logger.info('好友添加请求', '', {'好友': id_}, '已同意', True)
            await approve_request.finish(f'已同意{id_}的好友请求')
        elif state['type'] == '群':
            await bot.set_group_add_request(flag=flag, sub_type='invite', approve=True)
            del requests_list['群'][id_]
            logger.info('群邀请请求', '', {'群': id_}, '已同意', True)
            await approve_request.finish(f'已同意{id_}的群邀请')


@requests.handle()
async def _(bot: Bot, event: FriendRequestEvent):
    done[f'add_friend_{event.user_id}'] = datetime.datetime.now()
    try:
        user_info = await bot.get_stranger_info(user_id=event.user_id)
    except ActionFailed:
        user_info = {'nickname': '未知'}
    base_msg = f'{user_info["nickname"]}({event.user_id})请求添加好友，验证信息为"{event.comment or "无"}"'
    if bot_config.auto_add_friend:
        await asyncio.sleep(random.randint(10, 20))
        await bot.send_private_msg(user_id=SUPERUSERS[0], message=f'{base_msg}，已自动同意')
        await event.approve(bot)
        logger.info('好友添加请求', '', {'好友': event.user_id}, '申请添加好友，已自动同意', True)
    else:
        requests_list['好友'][str(event.user_id)] = {'name': user_info['nickname'], 'flag': event.flag}
        await bot.send_private_msg(user_id=SUPERUSERS[0], message=f'{base_msg}，可发送"同意好友{event.user_id}"来同意')
        logger.info('好友添加请求', '', {'好友': event.user_id}, '申请添加好友', True)


@requests.handle()
async def _(bot: Bot, event: GroupRequestEvent):
    done[f'add_group_{event.group_id}'] = datetime.datetime.now()
    try:
        user_info = await bot.get_stranger_info(user_id=event.user_id)
    except ActionFailed:
        user_info = {'nickname': '未知'}
    try:
        group_info = await bot.get_group_info(group_id=event.group_id)
    except ActionFailed:
        group_info = {'group_name': '未知'}
    base_msg = f'{user_info["nickname"]}({event.user_id})邀请{NICKNAME}加入群{group_info["group_name"]}({event.group_id})'
    if bot_config.auto_add_group or event.user_id in SUPERUSERS:
        await asyncio.sleep(random.randint(10, 20))
        await bot.send_private_msg(user_id=SUPERUSERS[0], message=f'{base_msg}，已自动同意')
        await event.approve(bot)
        logger.info('群邀请请求', '', {'群': event.group_id}, '邀请进群，已自动同意', True)
    else:
        requests_list['群'][str(event.group_id)] = {'name': group_info['group_name'], 'flag': event.flag}
        await bot.send_private_msg(user_id=SUPERUSERS[0], message=f'{base_msg}，可发送"同意群{event.group_id}"来同意')
        logger.info('群邀请请求', '', {'群': event.group_id}, '邀请进群', True)


@notices.handle()
async def _(bot: Bot, event: FriendAddNoticeEvent):
    done[f'new_friend_{event.user_id}'] = datetime.datetime.now()
    await asyncio.sleep(random.randint(10, 20))
    await bot.send_private_msg(user_id=event.user_id, message=format_message(config.new_friend))


@notices.handle()
async def _(bot: Bot, event: GroupIncreaseNoticeEvent):
    if event.user_id == event.self_id:
        done[f'new_group_{event.group_id}'] = datetime.datetime.now()
        await asyncio.sleep(random.randint(10, 20))
        await bot.send_group_msg(group_id=event.group_id, message=format_message(config.new_group))
    elif event.group_id not in config.group_ban:
        done[f'new_member_{event.group_id}_{event.user_id}'] = datetime.datetime.now()
        await asyncio.sleep(random.randint(10, 20))
        if event.group_id in config.group_greet:
            msg = config.group_greet[event.group_id]
        else:
            msg = config.group_greet['默认']
        await bot.send_group_msg(group_id=event.group_id, message=format_message(msg, user_id=event.user_id))


@ban_greet.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    msg = msg.extract_plain_text().strip()
    if any(i in msg for i in {'开启', '启用', '打开', 'on'}):
        type = True
        target = replace_all(msg, ['开启', '启用', '打开', 'on'])
    elif any(i in msg for i in {'禁用', '关闭', 'off'}):
        type = False
        target = replace_all(msg, ['禁用', '关闭', 'off'])
    else:
        await ban_greet.finish('指令格式错误，应为[入群欢迎启用|禁用 群号]')
        return
    if any(i in target for i in {'全部', 'all', '所有'}):
        target = ['全部']
    else:
        try:
            target = list(map(int, target.split(' ')))
        except Exception:
            await ban_greet.finish(f'请发送正确的要{"启用" if type else "禁用"}入群欢迎的群号或者"全部"')
    if not target:
        if isinstance(event, GroupMessageEvent):
            target = [event.group_id]
        else:
            await ban_greet.finish(f'请发送正确的要{"启用" if type else "禁用"}入群欢迎的群号或者"全部"')
    for t in target:
        if t == '全部':
            config.group_ban = [] if type else ['全部']
        elif not type:
            if t not in config.group_ban:
                config.group_ban.append(t)
        elif t in config.group_ban:
            config.group_ban.remove(t)
    config.save()
    await ban_greet.finish(f'已{"启用" if type else "禁用"}群{" ".join(map(str, target))}的群欢迎')


@scheduler.scheduled_job('cron', hour='*/1')
def _():
    # 删除done中超过1小时的记录
    for k, v in done.copy().items():
        if (datetime.datetime.now() - v).seconds > 3600:
            del done[k]
