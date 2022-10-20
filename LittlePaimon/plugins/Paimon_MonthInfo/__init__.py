import datetime
import re

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from LittlePaimon.utils.message import CommandPlayer
from .handler import handle_myzj

__plugin_meta__ = PluginMetadata(
    name='原神每月札记',
    description='原神每月札记信息',
    usage='myzj(uid)[月份]',
    extra={
        'author':   '惜月',
        'version':  '3.0',
        'priority': 5,
    }
)

myzj = on_command('myzj', aliases={'札记信息', '每月札记'}, priority=10, block=True, state={
        'pm_name':        'myzj',
        'pm_description': '*查看指定月份的原石、摩拉获取情况',
        'pm_usage':       'myzj(uid)[月份]',
        'pm_priority':    1
    })


@myzj.handle()
async def myzj_handler(event: MessageEvent, state: T_State, players=CommandPlayer()):
    msg = state['clear_msg']
    month_now = datetime.datetime.now().month
    if month_now == 1:
        month_list = ['11', '12', '1']
    elif month_now == 2:
        month_list = ['12', '1', '2']
    else:
        month_list = [str(month_now - 2), str(month_now - 1), str(month_now)]
    if match := re.search('(?P<month>' + '|'.join(month_list) + ')', msg):
        month = match['month']
    else:
        month = month_now
    result = Message()
    for player in players:
        result += await handle_myzj(player, month)
    await myzj.finish(result, at_sender=True)
