from time import time
from urllib.parse import quote
from datetime import datetime
from typing import Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed
from LittlePaimon.utils import logger, scheduler

from LittlePaimon.utils.message import CommandUID
from LittlePaimon.utils.api import get_authkey_by_stoken

gacha_url = on_command(
    '查看抽卡记录链接',
    aliases={'导出抽卡记录链接'},
    priority=11,
    block=True,
    state={
        'pm_name': '查看抽卡记录链接',
        'pm_description': '*获取你的抽卡记录链接',
        'pm_usage': '查看抽卡记录链接(uid)',
        'pm_priority': 1,
    },
)


async def withdraw(bot: Bot, message_id: int) -> None:
    """撤回消息任务"""
    await bot.delete_msg(message_id=message_id)


@gacha_url.handle()
async def _(
    bot: Bot,
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    uid=CommandUID()
):
    await gacha_url.send("正在获取抽卡记录链接")
    logger.info('获取抽卡记录链接', '开始执行')
    authkey, state, _ = await get_authkey_by_stoken(event.user_id, uid)
    if not state:
        return authkey
    if authkey == {}:
        await gacha_url.finish(authkey, at_sender=True)
    now = time()
    region = 'cn_qd01' if uid[0] == '5' else 'cn_gf01'
    msgs = []
    url = (
        f"https://hk4e-api.mihoyo.com/event/gacha_info/api/getGachaLog?"
        f"authkey_ver=1&sign_type=2&auth_appid=webview_gacha&init_type=301&"
        f"gacha_id=fecafa7b6560db5f3182222395d88aaa6aaac1bc"
        f"&timestamp={str(int(now))}"
        f"&lang=zh-cn&device_type=mobile&plat_type=ios&region={region}"
        f"&authkey={quote(authkey,'utf-8')}"
        f"&game_biz=hk4e_cn&gacha_type=301&page=1&size=5&end_id=0"
    )
    msgs.append({"type": "node", "data": {"name": '抽卡记录',
                "uin": event.user_id, "content": f"uid:{uid}的抽卡记录链接为："}})
    msgs.append({"type": "node", "data": {"name": '抽卡记录',
                "uin": event.user_id, "content": url}})
    try:
        if isinstance(event, PrivateMessageEvent):
            msg = await bot.call_api(
                "send_private_forward_msg", user_id=event.user_id, messages=msgs
            )
        else:
            msg = await bot.call_api(
                "send_group_forward_msg", group_id=event.group_id, messages=msgs
            )
        scheduler.add_job(
            withdraw,
            "date",
            args=[bot, dict(msg)["message_id"]],
            run_date=datetime.fromtimestamp(time() + 90),
        )
    except ActionFailed:
        logger.info('获取抽卡记录链接', '➤', '', '发送失败', False)
    except Exception as e:
        logger.info('获取抽卡记录链接', '➤', e, '撤回任务异常！', False)
