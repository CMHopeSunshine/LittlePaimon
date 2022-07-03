import re

from littlepaimon_utils import aiorequests
from littlepaimon_utils.files import load_json, save_json
from nonebot import on_command, require, get_bot, logger
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from ..utils.message_util import get_message_id

__plugin_meta__ = PluginMetadata(
    name="今日早报",
    description="60秒读世界早报",
    usage=(
        "今日早报 后加on时间/off可以开启/关闭推送"
    ),
    extra={
        'type':    '娱乐',
        'range':   ['private', 'group', 'guild'],
        "author":  "惜月 <277073121@qq.com>",
        "version": "1.0.0",
    },
)

news60s_pic = on_command('早报', aliases={'今日早报', '今日新闻', '60s读世界'}, priority=13, block=True)
news60s_pic.__paimon_help__ = {
    "usage":     "今日早报",
    "introduce": "获取60秒读世界早报，后加on时间/off可以开启/关闭推送",
    "priority": 10
}

scheduler = require('nonebot_plugin_apscheduler').scheduler


@news60s_pic.handle()
async def news60s_pic_handler(event: MessageEvent, msg: Message = CommandArg()):
    msg = msg.extract_plain_text().strip()
    if not msg:
        url = 'https://api.iyk0.com/60s/'
        res = await aiorequests.get(url=url)
        res = res.json()
        await news60s_pic.finish(MessageSegment.image(file=res['imageUrl']))
    elif msg.startswith(('开启', 'on', '打开')):
        # 匹配msg中的xx:xx时间
        time_str = re.search(r'(\d{1,2}):(\d{2})', msg)
        if time_str:
            push_data = load_json('news60s_push.json')
            push_id = str(get_message_id(event))
            push_data[push_id] = {
                'type':   event.message_type,
                'hour':   int(time_str.group(1)),
                'minute': int(time_str.group(2))
            }
            if event.message_type == 'guild':
                push_data[push_id]['guild_id'] = event.guild_id
            if scheduler.get_job('60sNews' + str(get_message_id(event))):
                scheduler.remove_job('60sNews' + str(get_message_id(event)))
            scheduler.add_job(
                func=news60s_push_task,
                trigger='cron',
                hour=int(time_str.group(1)),
                minute=int(time_str.group(2)),
                id='60sNews' + str(get_message_id(event)),
                args=(str(get_message_id(event)),
                      push_data[str(get_message_id(event))]),
                misfire_grace_time=10
            )
            save_json(push_data, 'news60s_push.json')
            await news60s_pic.finish('开启60s读世界推送成功', at_sender=True)
        else:
            await news60s_pic.finish('请给出正确的时间，格式为12:00', at_sender=True)
    elif msg.startswith(('关闭', 'off', 'close')):
        push_data = load_json('news60s_push.json')
        if str(get_message_id(event)) in push_data:
            del push_data[str(get_message_id(event))]
            if scheduler.get_job('60sNews' + str(get_message_id(event))):
                scheduler.remove_job('60sNews' + str(get_message_id(event)))
            save_json(push_data, 'news60s_push.json')
        await news60s_pic.finish('关闭60s读世界推送成功', at_sender=True)
    elif msg.startswith(('状态', 'status', 'setting')):
        push_data = load_json('news60s_push.json')
        if str(get_message_id(event)) not in push_data:
            await news60s_pic.finish('当前会话未开启60秒读世界订阅', at_sender=True)
        else:
            reply_msg = f'60秒读世界订阅时间: {push_data[str(get_message_id(event))]["hour"]}:{push_data[str(get_message_id(event))]["minute"]:02d}'
            await news60s_pic.finish(reply_msg, at_sender=True)
    else:
        await news60s_pic.finish('指令错误')


async def news60s_push_task(push_id, push_data: dict):
    try:
        url = 'https://api.iyk0.com/60s/'
        res = await aiorequests.get(url=url)
        res = res.json()
        if push_data['type'] == 'private':
            api = 'send_private_msg'
            data = {'user_id': push_id, 'message': MessageSegment.image(file=res['imageUrl'])}
        elif push_data['type'] == 'guild':
            api = 'send_guild_channel_msg'
            data = {'guild_id': push_id, 'channel_id': push_data['channel_id'], 'message': MessageSegment.image(file=res['imageUrl'])}
        else:
            api = 'send_group_msg'
            data = {'group_id': push_id, 'message': MessageSegment.image(file=res['imageUrl'])}
        await get_bot().call_api(api, **data)
        logger.info(f'{push_data["type"]}的{push_id}的60秒读世界推送成功')
    except Exception as e:
        logger.exception(f'{push_data["type"]}的{push_id}的60秒读世界推送失败：{e}')


for push_id, push_data in load_json('news60s_push.json').items():
    scheduler.add_job(
        func=news60s_push_task,
        trigger='cron',
        hour=push_data['hour'],
        minute=push_data['minute'],
        id='60sNews' + push_id,
        args=(push_id,
              push_data),
        misfire_grace_time=10
    )
