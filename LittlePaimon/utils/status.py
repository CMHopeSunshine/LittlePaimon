import asyncio
import datetime

import psutil
from nonebot import get_bot

from . import DRIVER, NICKNAME

start_time: str


async def get_status():
    status_result = {
        'nickname': NICKNAME
    }
    try:
        status_result['start_time'] = start_time
    except Exception:
        status_result['start_time'] = '未知'
    try:
        bot = get_bot()
        bot_status = await bot.get_status()
        status_result['bot_id'] = bot.self_id
        if bot_status := bot_status.get('stat'):
            status_result['msg_received'] = bot_status.get('message_received', '未知')
            status_result['msg_sent'] = bot_status.get('message_sent', '未知')
    except Exception:
        status_result['bot_id'] = '未知'
        status_result['msg_received'] = '未知'
        status_result['msg_sent'] = '未知'

    status_result['system_start_time'] = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime(
        "%Y-%m-%d %H:%M:%S")

    psutil.cpu_percent()
    await asyncio.sleep(0.1)
    cpu_percent = psutil.cpu_percent()
    # cpu_count = psutil.cpu_count(logical=False)
    # cpu_count_logical = psutil.cpu_count()
    # cpu_freq = psutil.cpu_freq()
    ram_stat = psutil.virtual_memory()
    swap_stat = psutil.swap_memory()
    status_result['cpu_percent'] = f'{cpu_percent}%'
    status_result['ram_percent'] = f'{ram_stat.percent}%'
    status_result['swap_percent'] = f'{swap_stat.percent}%'

    return status_result


@DRIVER.on_startup
async def start_up():
    global start_time
    start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
