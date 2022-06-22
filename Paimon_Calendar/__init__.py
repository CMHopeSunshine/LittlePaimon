from nonebot import get_bot, on_command, logger
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from utils.file_handler import load_json, save_json
from utils.message_util import get_message_id
from .generate import *
import re

require('nonebot_plugin_apscheduler')
from nonebot_plugin_apscheduler import scheduler

__plugin_meta__ = PluginMetadata(
    name="原神日历",
    description="查看原神活动日历",
    usage=(
        "原神日历 : 查看本群订阅服务器日历\n"
        "原神日历 on 时间/off : 订阅/取消订阅指定服务器的日历推送\n"
    ),
    extra={
        'type':    '原神Wiki',
        'range':   ['private', 'group', 'guild'],
        "author":  "nicklly <1134741727@qq.com>",
        "version": "1.0.1",
    },
)

calendar = on_command('原神日历', aliases={"原神日历", '原神日程', 'ysrl', 'ysrc'}, priority=24, block=True)
calendar.__paimon_help__ = {
    "usage":     "原神日历",
    "introduce": "查看原神活动日历，后加on时间/off可以开启定时推送",
    "priority":  99
}


async def send_calendar(push_id, push_data):
    try:
        if push_data['type'] == 'private':
            api = 'send_private_msg'
            data = {'user_id': push_id}
        elif push_data['type'] == 'guild':
            api = 'send_guild_channel_msg'
            data = {'channel_id': push_id, 'guild_id': push_data['guild_id']}
        else:
            api = 'send_group_msg'
            data = {'group_id': push_id}

        for server in push_data['server_list']:
            im = await generate_day_schedule(server)
            data['message'] = MessageSegment.image(im)
            await get_bot().call_api(api, **data)
        logger.info(f'{push_data["type"]}的{push_id}的原神日历推送成功')
    except Exception as e:
        logger.exception(f'{push_data["type"]}的{push_id}的原神日历推送失败：{e}')


def update_group_schedule(group_id, group_data):
    group_id = str(group_id)
    if group_id not in group_data:
        return

    scheduler.add_job(
        func=send_calendar,
        trigger='cron',
        args=(group_id, group_data),
        id=f'genshin_calendar_{group_id}',
        replace_existing=True,
        hour=group_data[group_id]['hour'],
        minute=group_data[group_id]['minute'],
        misfire_grace_time=10
    )


@calendar.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    server = 'cn'
    msg = msg.extract_plain_text().strip()

    if not msg:
        im = await generate_day_schedule(server)
        await calendar.finish(MessageSegment.image(im))
    else:
        push_data = load_json('calender_push.json')
        if msg.startswith(('开启', 'on', '打开')):
            # 添加定时推送任务
            time_str = re.search(r'(\d{1,2}):(\d{2})', msg)
            if time_str:
                push_id = str(get_message_id(event))
                push_data[push_id] = {
                    'server_list': [
                        str(server)
                    ],
                    'hour':        int(time_str.group(1)),
                    'minute':      int(time_str.group(2)),
                    'type':        event.message_type
                }
                if event.message_type == 'guild':
                    push_data[push_id]['guild_id'] = event.guild_id
                if scheduler.get_job('genshin_calendar_' + push_id):
                    scheduler.remove_job("genshin_calendar_" + push_id)

                save_json(push_data, 'calender_push.json')

                scheduler.add_job(
                    func=send_calendar,
                    trigger='cron',
                    hour=int(time_str.group(1)),
                    minute=int(time_str.group(2)),
                    id="genshin_calendar_" + push_id,
                    args=(push_id, push_data[push_id]),
                    misfire_grace_time=10
                )

                await calendar.finish('原神日程推送已开启', at_sender=True)
            else:
                await calendar.finish('请给出正确的时间，格式为12:00', at_sender=True)
        # 关闭推送功能
        elif msg.startswith(('关闭', 'off', 'close')):
            if str(get_message_id(event)) in push_data:
                del push_data[str(get_message_id(event))]
                if scheduler.get_job("genshin_calendar_" + str(get_message_id(event))):
                    scheduler.remove_job("genshin_calendar_" + str(get_message_id(event)))
                save_json(push_data, 'calender_push.json')
            await calendar.finish('原神日程推送已关闭', at_sender=True)
        elif msg.startswith(('状态', 'status', 'setting')):
            if str(get_message_id(event)) not in push_data:
                await calendar.finish('当前会话未开启原神日历订阅', at_sender=True)
            else:
                reply_msg = f'原神日历订阅：\n'
                reply_msg += f'推送时间: {push_data[str(get_message_id(event))]["hour"]}:{push_data[str(get_message_id(event))]["minute"]:02d}\n'
                reply_msg += f'服务器: {" ".join(push_data[str(get_message_id(event))]["server_list"])}'
                await calendar.finish(reply_msg, at_sender=True)
        else:
            await calendar.finish('指令错误')


# 自动推送任务
for push_id, push_data in load_json('calender_push.json').items():
    scheduler.add_job(
        func=send_calendar,
        trigger='cron',
        hour=push_data['hour'],
        minute=push_data['minute'],
        id="genshin_calendar_" + push_id,
        args=(push_id, push_data),
        misfire_grace_time=10
    )
