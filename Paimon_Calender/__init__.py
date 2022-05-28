import logging
from typing import Union

from nonebot import require, get_bot, on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent, Bot, Message, MessageSegment, ActionFailed
from nonebot.params import CommandArg

from ..utils.config import config
from ..utils.file_handler import load_json, save_json
from .generate import *
import re

HELP_STR = '''
原神活动日历
原神日历 : 查看本群订阅服务器日历
原神日历 on/off : 订阅/取消订阅指定服务器的日历推送
原神日历 time 时:分 : 设置日历推送时间
原神日历 status : 查看本群日历推送设置
'''.strip()

calendar = on_command('原神日历', aliases={"原神日历", 'ysrl', '原神日程'}, priority=24, block=True)
scheduler = require('nonebot_plugin_apscheduler').scheduler


async def send_calendar(group_id, group_data):
    for server in group_data[str(group_id)]['server_list']:
        im = await generate_day_schedule(server)
        base64_str = im2base64str(im)
        if 'cardimage' not in group_data or not group_data['cardimage']:
            msg = MessageSegment.image(base64_str)
        else:
            msg = f'[CQ:cardimage,file={base64_str}]'

        await get_bot().send_group_msg(group_id=int(group_id), message=msg)


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
async def _(bot: Bot, event: Union[GroupMessageEvent, MessageEvent], msg: Message = CommandArg()):
    if event.message_type == 'private':
        await calendar.finish('仅支持群聊模式下使用本指令')

    group_id = str(event.group_id)
    group_data = load_json('calender_push.json')
    server = 'cn'
    fun = str(msg).strip()
    action = re.search(r'(?P<action>on|off|time|status|test)', fun)

    if group_id not in config.paimon_calender_group or int(group_id) not in config.paimon_calender_group:
        await calendar.finish(f"尚未在群 {group_id} 开启本功能！", at_sender=True)

    if not fun:
        im = await generate_day_schedule(server)
        base64_str = im2base64str(im)
        group_data = load_json('calender_push.json')

        try:
            if group_id not in group_data or 'cardimage' not in group_data[group_id] or not group_data[group_id]['cardimage']:
                await calendar.finish(MessageSegment.image(base64_str))
            else:
                await calendar.finish(f'[CQ:cardimage,file={base64_str}]')
        except ActionFailed as e:
            await logging.ERROR(e)

    elif action:

        # 添加定时推送任务
        if action.group('action') == 'on':
            group_data[group_id] = {
                'server_list': [
                    str(server)
                ],
                'hour': 8,
                'minute': 0,
                'cardimage': False
            }
            if event.message_type == 'guild':
                await calendar.finish("暂不支持频道内推送~")

            if scheduler.get_job('genshin_calendar_' + group_id):
                scheduler.remove_job("genshin_calendar_" + group_id)
            save_json(group_data, 'calender_push.json')

            scheduler.add_job(
                func=send_calendar,
                trigger='cron',
                hour=8,
                minute=0,
                id="genshin_calendar_" + group_id,
                args=(group_id, group_data[group_id]),
                misfire_grace_time=10
            )

            await calendar.finish('原神日程推送已开启')

        # 关闭推送功能
        elif action.group('action') == 'off':
            del group_data[group_id]
            if scheduler.get_job("genshin_calendar_" + group_id):
                scheduler.remove_job("genshin_calendar_" + group_id)
            await calendar.finish('原神日程推送已关闭')

        # 设置推送时间
        elif action.group('action') == 'time':
            match = str(msg).split(" ")
            time = re.search(r'(\d{1,2}):(\d{2})', match[1])

            if re.match(r'(\d{1,2}):(\d{2})', match[1]):
                if not time or len(time.groups()) < 2:
                    await calendar.finish("请指定推送时间")
                else:
                    group_data[group_id]['hour'] = int(time.group(1))
                    group_data[group_id]['minute'] = int(time.group(2))
                    save_json(group_data, 'calender_push.json')
                    update_group_schedule(group_id, group_data)

                    await calendar.finish(
                        f"推送时间已设置为: {group_data[group_id]['hour']}:{group_data[group_id]['minute']:02d}")

            else:
                await calendar.finish("请给出正确的时间，格式为12:00", at_sender=True)
        # DEBUG
        elif action.group('action') == 'test':
            return

        # 查询订阅推送状态
        elif action.group('action') == "status":
            message = f"订阅日历: {group_data[group_id]['server_list']}"
            message += f"\n推送时间: {group_data[group_id]['hour']}:{group_data[group_id]['minute']:02d}"
            await calendar.finish(message)
        else:
            await calendar.finish('指令错误')

# 自动推送任务
for group_id, group_data in load_json('calender_push.json').items():
    scheduler.add_job(
        func=send_calendar,
        trigger='cron',
        hour=group_data['hour'],
        minute=group_data['minute'],
        id="genshin_calendar_" + group_id,
        args=(group_id, group_data),
        misfire_grace_time=10
    )
