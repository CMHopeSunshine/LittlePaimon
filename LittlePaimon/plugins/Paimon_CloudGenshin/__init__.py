import re
import uuid

from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, Message, GroupMessageEvent
from nonebot.params import CommandArg, ArgPlainText
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from LittlePaimon.database import CloudGenshinSub
from .handler import get_cloud_genshin_info

__plugin_meta__ = PluginMetadata(
    name='云原神',
    description='云原神',
    usage='...',
    extra={
        'priority': 16,
    }
)

yys_bind = on_command('云原神绑定', priority=12, block=True, state={
    'pm_name':        '云原神绑定',
    'pm_description': '绑定云原神账户token，开启自动签到',
    'pm_usage':       '云原神绑定<token>',
    'pm_priority':    1
})
yys_info = on_command('云原神信息', priority=12, block=True, state={
    'pm_name':        '云原神信息',
    'pm_description': '查看云原神账户信息',
    'pm_usage':       '云原神信息(米游社id)',
    'pm_priority':    2
})
yys_delete = on_command('云原神解绑', priority=12, block=True, state={
    'pm_name':        '云原神解绑',
    'pm_description': '解绑云原神账户并取消自动签到',
    'pm_usage':       '云原神解绑(米游社id)',
    'pm_priority':    3
})

uuid_ = str(uuid.uuid4())


@yys_bind.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    msg = msg.extract_plain_text().strip()
    if not msg:
        await yys_bind.finish('请给出要绑定的token', at_sender=True)
    if match := re.search(r'oi=\d+', msg):
        group_id = event.group_id if isinstance(event, GroupMessageEvent) else event.user_id
        uid = str(match.group()).split('=')[1]
        await CloudGenshinSub.update_or_create(user_id=str(event.user_id), uid=uid, defaults={'group_id': group_id, 'uuid': uuid_, 'token': msg})
        await yys_bind.finish(f'米游社账号{uid}云原神token绑定成功，将会每日为你自动领免费时长', at_sender=True)
    else:
        await yys_bind.finish('token格式错误哦~请按照https://blog.ethreal.cn/archives/yysgettoken所写的方法获取', at_sender=True)


@yys_info.handle()
async def _(event: MessageEvent, state: T_State, msg: Message = CommandArg()):
    if uids := await CloudGenshinSub.filter(user_id=str(event.user_id)):
        state['msg'] = '你已绑定的云原神账号有\n' + '\n'.join([str(uid.uid) for uid in uids]) + '\n请选择要查询的账号'
        state['uids'] = [uid.uid for uid in uids]
    else:
        await yys_info.finish('你还没有绑定云原神账号哦~请使用云原神绑定指令绑定账号', at_sender=True)
    if uid := re.search(r'\d+', msg.extract_plain_text().strip()):
        state['uid'] = Message(uid.group())


@yys_info.got('uid', prompt=Message.template('{msg}'))
async def _(event: MessageEvent, state: T_State, uid: str = ArgPlainText('uid')):
    if uid in state['uids']:
        await yys_info.finish(await get_cloud_genshin_info(str(event.user_id), uid))
    else:
        await yys_info.finish(state['msg'])


@yys_delete.handle()
async def _(event: MessageEvent, state: T_State, msg: Message = CommandArg()):
    if uids := await CloudGenshinSub.filter(user_id=str(event.user_id)):
        state['msg'] = '你已绑定的云原神账号有\n' + '\n'.join([str(uid.uid) for uid in uids]) + '\n请选择要解绑的账号'
        state['uids'] = [uid.uid for uid in uids]
    else:
        await yys_info.finish('你还没有绑定云原神账号哦~', at_sender=True)
    if '全部' in msg.extract_plain_text():
        state['uid'] = Message('全部')
    elif uid := re.search(r'\d+', msg.extract_plain_text().strip()):
        state['uid'] = Message(uid.group())


@yys_delete.got('uid', prompt=Message.template('{msg}，或者发送[全部]解绑全部云原神账号'))
async def _(event: MessageEvent, state: T_State, uid: str = ArgPlainText('uid')):
    if uid == '全部':
        await CloudGenshinSub.filter(user_id=str(event.user_id)).delete()
        await yys_delete.finish('你的云原神全部解绑成功', at_sender=True)
    elif uid in state['uids']:
        await CloudGenshinSub.filter(user_id=str(event.user_id), uid=uid).delete()
        await yys_delete.finish(f'米游社账号{uid}解绑云原神成功', at_sender=True)
    else:
        await yys_delete.reject(state['msg'], at_sender=True)
