from typing import Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me

from LittlePaimon.database import MihoyoBBSSub, PrivateCookie
from LittlePaimon.utils import logger
from LittlePaimon.utils.message import CommandUID, CommandSwitch
from .coin_handle import mhy_bbs_coin, bbs_auto_coin
from .draw import draw_result
from .sign_handle import mhy_bbs_sign, bbs_auto_sign

__plugin_meta__ = PluginMetadata(
    name='米游社签到及获取',
    description='米游社',
    usage='mys签到',
    extra={
        'author': '惜月',
        'version': '3.0',
        'priority': 11,
        'configs': {'签到开始小时': 0, '签到开始分钟': 5, '米游币开始小时': 0, '米游币开始分钟': 30},
    },
)

sign = on_command(
    'mys签到',
    aliases={'米游社签到', 'mys自动签到', '米游社自动签到'},
    priority=8,
    block=True,
    state={
        'pm_name': '米游社签到',
        'pm_description': '*执行米游社签到操作，或开启每日自动签到',
        'pm_usage': '米游社签到(uid)[on|off]',
        'pm_priority': 1,
    },
)
all_sign = on_command(
    '全部重签',
    priority=8,
    block=True,
    permission=SUPERUSER,
    rule=to_me(),
    state={
        'pm_name': '米游社全部重签',
        'pm_description': '重签全部米游社签到任务，需超级用户权限',
        'pm_usage': '@Bot 全部重签',
        'pm_priority': 3,
    },
)

get_coin = on_command(
    'myb获取',
    aliases={'米游币获取', 'myb自动获取', '米游币自动获取', '米游币任务'},
    priority=8,
    block=True,
    state={
        'pm_name': '米游币获取',
        'pm_description': '*执行米游币任务操作，或开启每日自动获取米游币',
        'pm_usage': '米游币获取(uid)[on|off]',
        'pm_priority': 2,
    },
)

all_coin = on_command(
    'myb全部重做',
    priority=8,
    block=True,
    permission=SUPERUSER,
    rule=to_me(),
    state={
        'pm_name': '米游币获取全部重做',
        'pm_description': '重做全部米游币获取任务，需超级用户权限',
        'pm_usage': '@Bot myb全部重做',
        'pm_priority': 4,
    },
)


signing_list = []
coin_getting_list = []


@sign.handle()
async def _(
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    uid=CommandUID(),
    switch=CommandSwitch(),
):
    if switch is None:
        # 没有开关参数，手动执行米游社签到
        if f'{event.user_id}-{uid}' in signing_list:
            await sign.finish('你已经在执行签到任务中，请勿重复发送', at_sender=True)
        else:
            await sign.send(f'开始为UID{uid}执行米游社签到，请稍等...', at_sender=True)
            logger.info(
                '米游社原神签到', '', {'user_id': event.user_id, 'uid': uid, '执行签到': ''}
            )
            signing_list.append(f'{event.user_id}-{uid}')
            try:
                _, result = await mhy_bbs_sign(str(event.user_id), uid)
            except Exception as e:
                result = f'UID{uid}签到失败，报错信息：{str(e)}'
            finally:
                signing_list.remove(f'{event.user_id}-{uid}')
            await sign.finish(result, at_sender=True)
    else:
        sub_data = {'user_id': event.user_id, 'uid': uid, 'sub_event': '米游社原神签到'}
        if switch:
            # switch为开启，则添加订阅
            if await PrivateCookie.get_or_none(user_id=str(event.user_id), uid=uid):
                await MihoyoBBSSub.update_or_create(
                    **sub_data,
                    defaults={
                        'group_id': event.group_id
                        if isinstance(event, GroupMessageEvent)
                        else event.user_id
                    },
                )
                logger.info(
                    '米游社原神签到', '', {'user_id': event.user_id, 'uid': uid}, '开启成功', True
                )
                await sign.finish(f'UID{uid}开启米游社原神自动签到成功', at_sender=True)
            else:
                await sign.finish(f'UID{uid}尚未绑定Cookie！请先使用ysb指令绑定吧！', at_sender=True)
        else:
            # switch为关闭，则取消订阅
            if sub := await MihoyoBBSSub.get_or_none(**sub_data):
                await sub.delete()
                logger.info(
                    '米游社原神签到', '', {'user_id': event.user_id, 'uid': uid}, '关闭成功', True
                )
                await sign.finish(f'UID{uid}关闭米游社原神自动签到成功', at_sender=True)
            else:
                await sign.finish(f'UID{uid}尚未开启米游社原神自动签到，无需关闭！', at_sender=True)


@all_sign.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    await all_sign.send('开始执行全部重签，需要一定时间...')
    await bbs_auto_sign()


@get_coin.handle()
async def _(
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    uid=CommandUID(),
    switch=CommandSwitch(),
):
    if switch is None:
        # 没有开关参数，手动执行米游币获取
        if f'{event.user_id}-{uid}' in coin_getting_list:
            await get_coin.finish('你已经在执行米游币获取任务中，请勿重复发送', at_sender=True)
        else:
            await get_coin.send(f'开始为UID{uid}执行米游币获取，请稍等...', at_sender=True)
            logger.info(
                '米游币自动获取', '', {'user_id': event.user_id, 'uid': uid, '执行获取': ''}
            )
            coin_getting_list.append(f'{event.user_id}-{uid}')
            try:
                result = await mhy_bbs_coin(str(event.user_id), uid)
            except Exception as e:
                result = f'UID{uid}米游币执行失败，报错信息：{str(e)}'
            finally:
                coin_getting_list.remove(f'{event.user_id}-{uid}')
            await get_coin.finish(result, at_sender=True)
    else:
        sub_data = {'user_id': event.user_id, 'uid': uid, 'sub_event': '米游币自动获取'}
        if switch:
            # switch为开启，则添加订阅
            if (
                ck := await PrivateCookie.get_or_none(
                    user_id=str(event.user_id), uid=uid
                )
            ) and ck.stoken is not None:
                await MihoyoBBSSub.update_or_create(
                    **sub_data,
                    defaults={
                        'group_id': event.group_id
                        if isinstance(event, GroupMessageEvent)
                        else event.user_id
                    },
                )
                logger.info(
                    '米游币自动获取', '', {'user_id': event.user_id, 'uid': uid}, '开启成功', True
                )
                await sign.finish(f'UID{uid}开启米游币自动获取成功', at_sender=True)
            else:
                await get_coin.finish(
                    f'UID{uid}尚未绑定Cookie或Cookie中没有login_ticket！请先使用ysb指令绑定吧！',
                    at_sender=True,
                )
        else:
            # switch为关闭，则取消订阅
            if sub := await MihoyoBBSSub.get_or_none(**sub_data):
                await sub.delete()
                logger.info(
                    '米游币自动获取', '', {'user_id': event.user_id, 'uid': uid}, '关闭成功', True
                )
                await sign.finish(f'UID{uid}关闭米游币自动获取成功', at_sender=True)
            else:
                await sign.finish(f'UID{uid}尚未开启米游币自动获取，无需关闭！', at_sender=True)


@all_coin.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    await all_coin.send('开始执行myb全部重做，需要一定时间...')
    await bbs_auto_coin()
