import nonebot
from nonebot import RequestSession, NoticeSession, on_request, on_notice
from hoshino import util


@on_request('group.invite')
async def handle_group_invite(session: RequestSession):
    if session.ctx['user_id'] in nonebot.get_bot().config.SUPERUSERS:
        await session.approve()
    else:
        await session.reject(reason='邀请入群请联系维护组')

@on_notice('group_increase')
async def handle_unknown_group_invite(session):
    if session.ctx['user_id'] == session.ctx['self_id']:
        try:
            await nonebot.get_bot().send_private_msg(user_id=nonebot.get_bot().config.SUPERUSERS,message=f'群{session.ctx["group_id"]}未经允许拉了派蒙进群')
        except Exception as e:
            print('处理群聊邀请错误:',e)
    else:
        return
