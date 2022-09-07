from typing import Union
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent, PrivateMessageEvent
from nonebot.plugin import PluginMetadata

from LittlePaimon.utils import logger
from LittlePaimon.utils.message import CommandPlayer
from .data_source import get_gacha_log_img, get_gacha_log_data, create_import_command, gacha_log_to_UIGF

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
import_log = on_command('导入抽卡记录', aliases={'抽卡记录导入'}, priority=12, block=True, state={
    'pm_name':        '导入抽卡记录',
    'pm_description': '导入符合UIGF标准的抽卡记录json文件，发送命令后，于5分钟内上传json文件即可',
    'pm_usage':       '导入抽卡记录',
    'pm_priority':    3
})
export_log = on_command('导出抽卡记录', aliases={'抽卡记录导出'}, priority=12, block=True, state={
    'pm_name':        '导出抽卡记录',
    'pm_description': '导出符合UIGF标准的抽卡记录json文件',
    'pm_usage':       '导出抽卡记录',
    'pm_priority':    4
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


@import_log.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    create_import_command(event.user_id)
    await import_log.finish('请在5分钟内，上传或发送符合UIGF标准的抽卡记录json文件', at_sender=True)


@export_log.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent], bot: Bot, player=CommandPlayer(1)):
    state, msg, path = gacha_log_to_UIGF(player[0].user_id, player[0].uid)
    if not state:
        await export_log.finish(msg, at_sender=True)
    else:
        try:
            if isinstance(event, GroupMessageEvent):
                await bot.upload_group_file(group_id=event.group_id, file=str(path.absolute()), name=path.name)
            else:
                await bot.upload_private_file(user_id=event.user_id, file=str(path.absolute()), name=path.name)
        except Exception as e:
            await export_log.finish(f'上传文件失败，错误信息：{e}', at_sender=True)
