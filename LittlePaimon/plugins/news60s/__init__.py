from typing import Optional

from nonebot import get_bot, on_command
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata

from LittlePaimon.config import config
from LittlePaimon.database import GeneralSub
from LittlePaimon.utils import scheduler, logger, DRIVER
from LittlePaimon.utils.message import CommandObjectID, CommandSwitch, CommandTime

__plugin_meta__ = PluginMetadata(
    name="60秒读世界",
    description="查看60秒读世界日历",
    usage=(
        "60秒读世界 : 查看本群订阅服务器日历\n"
        "60秒读世界 on 时间/off : 订阅/取消订阅日历推送\n"
    ),
    extra={
        'type':    '娱乐',
        "author":  "惜月 <277073121@qq.com>",
        "version": "1.0.0",
        'priority': 99,
    },
)


news = on_command('早报', aliases={'今日早报', '今日新闻', '60s读世界', '60秒读世界'}, priority=14, block=True)


@news.handle()
async def _(event: MessageEvent, sub_id=CommandObjectID(), switch=CommandSwitch(), sub_time=CommandTime()):
    if switch is None:
        await news.send('60秒读世界新闻获取中，请稍等...')
        await news.finish(MessageSegment.image(file=config.morning_news))
    else:
        sub_data = {
            'sub_id':    sub_id,
            'sub_type':  event.message_type,
            'sub_event': '60秒读世界'
        }
        if event.message_type == 'guild':
            sub_data['extra_id'] = event.guild_id
        if switch:
            if sub_time:
                await GeneralSub.update_or_create(**sub_data,
                                                  defaults={'sub_hour':   sub_time[0],
                                                            'sub_minute': sub_time[1]})
                if scheduler.get_job(f'news60s_{sub_id}'):
                    scheduler.remove_job(f'news60s_{sub_id}')

                scheduler.add_job(
                    func=send_news,
                    trigger='cron',
                    hour=sub_time[0],
                    minute=sub_time[1],
                    id=f'news60s_{sub_id}',
                    args=(sub_data['sub_id'], sub_data['sub_type'], sub_data.get('extra_id', None)),
                    misfire_grace_time=10
                )
                logger.info('60秒读世界', '', {sub_data['sub_type']: sub_id, 'time': f'{sub_time[0]}:{sub_time[1]}'}, '订阅成功',
                            True)
                await news.finish(f'60秒读世界订阅成功， 将在每日{sub_time[0]}:{sub_time[1]}推送')
            else:
                await news.finish('请给出正确的时间格式，如12:00')
        else:
            if sub := await GeneralSub.get_or_none(**sub_data):
                await sub.delete()
                logger.info('60秒读世界', '', {sub_data['sub_type']: sub_id}, '取消订阅成功', True)
                await news.finish(f'60秒读世界订阅已取消')
            else:
                await news.finish(f'当前会话未开启60秒读世界订阅')


@DRIVER.on_startup
async def _():
    try:
        all_sub_data = await GeneralSub.filter(sub_event='60秒读世界').all()
        if all_sub_data:
            for sub_data in all_sub_data:
                scheduler.add_job(
                    func=send_news,
                    trigger='cron',
                    hour=sub_data.sub_hour,
                    minute=sub_data.sub_minute,
                    id=f'news60s_{sub_data.sub_id}',
                    args=(sub_data.sub_id, sub_data.sub_type, sub_data.extra_id),
                    misfire_grace_time=10
                )
            logger.success('60秒读世界', '', {'订阅数量共': f'{len(all_sub_data)}个'}, '加载成功')
    except Exception as e:
        logger.warning('60秒读世界', '订阅列表', f'加载失败: {e}')


async def send_news(sub_id: int, sub_type: str, extra_id: Optional[int]):
    try:
        if sub_type == 'private':
            api = 'send_private_msg'
            data = {'user_id': sub_id}
        elif sub_type == 'guild':
            api = 'send_guild_channel_msg'
            data = {'channel_id': sub_id, 'guild_id': extra_id}
        else:
            api = 'send_group_msg'
            data = {'group_id': sub_id}
        data['message'] = MessageSegment.image(file=config.morning_news)
        await get_bot().call_api(api, **data)
        logger.info('60秒读世界', '', {sub_type: sub_id}, '推送成功', True)
    except Exception as e:
        logger.info('60秒读世界', '', {sub_type: sub_id}, f'推送失败: {e}', False)
