from typing import Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, GroupMessageEvent, PrivateMessageEvent
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from LittlePaimon.database import DailyNoteSub
from LittlePaimon.utils import logger
from LittlePaimon.utils.message import CommandPlayer, CommandUID, CommandSwitch
from .handler import SubList, get_subs, handle_ssbq

__plugin_meta__ = PluginMetadata(
    name='原神实时便签',
    description='原神实时便签信息',
    usage='ssbq(uid)',
    extra={
        'author':   '惜月',
        'version':  '3.0',
        'priority': 4,
        'configs': {
            '检查间隔': 16
        }
    }
)

ssbq = on_command('ssbq', aliases={'实时便笺', '实时便签', '当前树脂'}, priority=9, block=True, state={
        'pm_name':        'ssbq',
        'pm_description': '*查看原神实时便笺(树脂情况)',
        'pm_usage':       'ssbq(uid)',
        'pm_priority':    1
    })
ssbq_sub = on_command('ssbq提醒', aliases={'实时便笺提醒', '实时便签提醒', '当前树脂提醒'}, priority=9, block=True, state={
        'pm_name':        'ssbq提醒',
        'pm_description': '*开启|关闭ssbq提醒，可订阅树脂以及尘歌壶钱币提醒',
        'pm_usage':       'ssbq提醒<开|关>[树脂|钱币]',
        'pm_priority':    1
    })


@ssbq.handle()
async def _(event: MessageEvent, state: T_State, players=CommandPlayer()):
    if state.get('clear_msg'):
        await ssbq.finish('开启提醒请用[ssbq提醒开启|关闭 提醒内容+数量]指令，比如[ssbq提醒开启树脂150]')
    logger.info('原神实时便签', '开始执行查询')
    result = Message()
    for player in players:
        result += await handle_ssbq(player)
    await ssbq.finish(result, at_sender=True)


@ssbq_sub.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent], uid=CommandUID(), switch=CommandSwitch(), subs=SubList()):
    sub_data = {
        'user_id':     event.user_id,
        'uid':         uid,
        'remind_type': event.message_type,
    }
    if isinstance(event, GroupMessageEvent):
        sub_data['group_id'] = event.group_id
    if switch is None or switch:
        await DailyNoteSub.update_or_create(**sub_data, defaults=subs)
        logger.info('原神实时便笺', '', sub_data.update(subs), '添加提醒成功', True)
        subs_info = await get_subs(**sub_data)
        await ssbq_sub.finish(f'开启提醒成功，{subs_info}', at_sender=True)
    else:
        s = await DailyNoteSub.get_or_none(**sub_data)
        if not s:
            await ssbq_sub.finish('你在当前会话尚未开启任何订阅', at_sender=True)
        else:
            if 'resin_num' in subs:
                s.resin_num = None
            if 'coin_num' in subs:
                s.coin_num = None
            if s.resin_num is None and s.coin_num is None:
                await s.delete()
            else:
                await s.save()
            await ssbq_sub.finish('已关闭当前会话的对应提醒', at_sender=True)
