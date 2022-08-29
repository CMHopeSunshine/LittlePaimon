from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.plugin import PluginMetadata

from LittlePaimon.utils import logger
from LittlePaimon.utils.message import CommandPlayer
from .data_source import get_gacha_log_img, get_gacha_log_data

__plugin_meta__ = PluginMetadata(
    name="原神抽卡记录分析",
    description="小派蒙的原神抽卡记录模块",
    usage='',
    extra={
        'type':     '原神抽卡记录',
        "author":   "惜月 <277073121@qq.com>",
        "version":  "3.0.0",
        'priority': 10,
    },
)

update_log = on_command('更新抽卡记录', aliases={'抽卡记录更新', '获取抽卡记录'}, priority=12, block=True, state={
    'pm_name':        '更新抽卡记录',
    'pm_description': '*通过stoken更新原神抽卡记录',
    'pm_usage':       '更新抽卡记录(uid)',
    'pm_priority':    1
})
show_log = on_command('查看抽卡记录', aliases={'抽卡记录'}, priority=12, block=True, state={
    'pm_name':        '查看抽卡记录',
    'pm_description': '*查看你的抽卡记录分析',
    'pm_usage':       '查看抽卡记录(uid)',
    'pm_priority':    2
})

running_update = []
running_show = []


@update_log.handle()
async def _(event: MessageEvent, player=CommandPlayer(1)):
    if f'{player[0].user_id}-{player[0].uid}' in running_update:
        await update_log.finish(f'UID{player[0].uid}已经在获取抽卡记录中，请勿重复发送')
    else:
        running_update.append(f'{player[0].user_id}-{player[0].uid}')
        await update_log.send(f'开始为UID{player[0].uid}更新抽卡记录，请稍候...')
        try:
            result = await get_gacha_log_data(player[0].user_id, player[0].uid)
            await update_log.send(result, at_sender=True)
        except Exception as e:
            logger.info('原神抽卡记录', f'➤➤更新抽卡记录时出现错误：<r>{e}</r>')
            await update_log.send(f'更新抽卡记录时出现错误：{e}')
        running_update.remove(f'{player[0].user_id}-{player[0].uid}')


@show_log.handle()
async def _(event: MessageEvent, player=CommandPlayer(1)):
    if f'{player[0].user_id}-{player[0].uid}' in running_show:
        await update_log.finish(f'UID{player[0].uid}已经在绘制抽卡记录分析中，请勿重复发送')
    else:
        logger.info('原神抽卡记录', '➤', {'用户': player[0].user_id, 'UID': player[0].uid}, '开始绘制抽卡记录图片', True)
        running_show.append(f'{player[0].user_id}-{player[0].uid}')
        await update_log.send(f'开始为UID{player[0].uid}绘制抽卡记录分析，请稍候...')
        try:
            result = await get_gacha_log_img(player[0].user_id, player[0].uid, event.sender.nickname)
            await show_log.send(result, at_sender=True)
        except Exception as e:
            logger.info('原神抽卡记录', f'➤➤绘制抽卡记录图片时出现错误：<r>{e}</r>')
            await update_log.send(f'绘制抽卡记录分析时出现错误：{e}')
        running_show.remove(f'{player[0].user_id}-{player[0].uid}')
