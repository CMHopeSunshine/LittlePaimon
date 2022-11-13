from nonebot import get_bot, on_command
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata

from LittlePaimon.database import GeneralSub
from LittlePaimon.utils import scheduler, logger, DRIVER, SUPERUSERS
from LittlePaimon.utils.message import CommandObjectID, CommandSwitch, CommandTime
from .generate import *

__plugin_meta__ = PluginMetadata(
    name="原神日历",
    description="查看原神活动日历",
    usage=(
        "原神日历 : 查看本群订阅服务器日历\n"
        "原神日历 on 时间/off : 订阅/取消订阅指定服务器的日历推送\n"
    ),
    extra={
        'type': '原神Wiki',
        "author": "nicklly <1134741727@qq.com>",
        "version": "1.0.1",
        'priority': 7,
    },
)

calendar = on_command('原神日历', aliases={'原神日程', '活动日历'}, priority=10, block=True)


@calendar.handle()
async def _(event: MessageEvent, sub_id=CommandObjectID(), switch=CommandSwitch(), sub_time=CommandTime()):
    if switch is None:
        im = await generate_day_schedule('cn')
        await calendar.finish(MessageSegment.image(im))
    else:
        if event.sender.role not in ['admin', 'owner'] and event.user_id not in SUPERUSERS:
            await calendar.finish('你没有权限管理原神日历订阅')
        sub_data = {'sub_id': sub_id, 'sub_type': event.message_type, 'sub_event': '原神日历'}

        if event.message_type == 'guild':
            sub_data['extra_id'] = event.guild_id
        if switch:
            if sub_time:
                await GeneralSub.update_or_create(**sub_data,
                                                  defaults={'sub_hour': sub_time[0], 'sub_minute': sub_time[1]})

                if scheduler.get_job(f'genshin_calendar_{sub_id}'):
                    scheduler.remove_job(f'genshin_calendar_{sub_id}')
                scheduler.add_job(func=send_calendar, trigger='cron', hour=sub_time[0], minute=sub_time[1],
                                  id=f'genshin_calendar_{sub_id}',
                                  args=(sub_data['sub_id'], sub_data['sub_type'], sub_data.get('extra_id', None)),
                                  misfire_grace_time=10)

                logger.info('原神日历', '', {sub_data['sub_type']: sub_id, 'time': f'{sub_time[0]}:{sub_time[1]}'}, '订阅成功',
                            True)

                await calendar.finish(f'原神日历订阅成功， 将在每日{sub_time[0]}:{sub_time[1]}推送')
            else:
                await calendar.finish('请给出正确的时间格式，如12:00')
        elif sub := await GeneralSub.get_or_none(**sub_data):
            await sub.delete()
            logger.info('原神日历', '', {sub_data['sub_type']: sub_id}, '取消订阅成功', True)
            await calendar.finish('原神日历订阅已取消')
        else:
            await calendar.finish('当前会话未开启原神日历订阅')


async def send_calendar(sub_id: int, sub_type: str, extra_id: Optional[int]):
    try:
        if sub_type == 'guild':
            api = 'send_guild_channel_msg'
            data = {'channel_id': sub_id, 'guild_id': extra_id}
        elif sub_type == 'private':
            api = 'send_private_msg'
            data = {'user_id': sub_id}
        else:
            api = 'send_group_msg'
            data = {'group_id': sub_id}
        im = await generate_day_schedule('cn')
        data['message'] = MessageSegment.image(im)
        await get_bot().call_api(api, **data)
        logger.info('原神日历', '', {sub_type: sub_id}, '推送成功', True)
    except Exception as e:
        logger.info('原神日历', '', {sub_type: sub_id}, f'推送失败: {e}', False)


@DRIVER.on_startup
async def _():
    try:
        all_sub_data = await GeneralSub.filter(sub_event='原神日历').all()
        if all_sub_data:
            for sub_data in all_sub_data:
                scheduler.add_job(
                    func=send_calendar,
                    trigger='cron',
                    hour=sub_data.sub_hour,
                    minute=sub_data.sub_minute,
                    id=f'genshin_calendar_{sub_data.sub_id}',
                    args=(sub_data.sub_id, sub_data.sub_type, sub_data.extra_id),
                    misfire_grace_time=10
                )
            logger.info('原神日历', '', {'订阅数量共': f'{len(all_sub_data)}个'}, '加载成功', True)
    except Exception as e:
        logger.info('原神日历', '订阅列表', {}, f'加载失败: {e}', True)
