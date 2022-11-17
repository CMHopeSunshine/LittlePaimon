import asyncio
from typing import Union

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from nonebot.log import logger, default_filter, default_format
from LittlePaimon.utils.status import get_status
from .utils import authentication

info_logs = []
debug_logs = []


def record_info_log(message: str):
    info_logs.append(message)
    if len(info_logs) > 500:
        info_logs.pop(0)


def record_debug_log(message: str):
    # 过滤一些无用日志
    if not any(w in message for w in {'Checking for matchers', 'Running PreProcessors', 'OneBot V11 | Calling API'}):
        debug_logs.append(message)
        if len(debug_logs) > 300:
            debug_logs.pop(0)


logger.add(record_info_log, level='INFO', colorize=True, filter=default_filter, format=default_format)
logger.add(record_debug_log, level='DEBUG', colorize=True, filter=default_filter, format=default_format)

route = APIRouter()


@route.get('/log', response_class=StreamingResponse, dependencies=[authentication()])
async def get_log(level: str = 'info', num: Union[int, str] = 100):
    show_logs = info_logs[-(num or 1):] if level == 'info' else debug_logs[-(num or 1):]

    async def streaming_logs():
        for log in show_logs:
            yield log
            await asyncio.sleep(0.02)

    return StreamingResponse(streaming_logs())


@route.get('/run_cmd', response_class=StreamingResponse, dependencies=[authentication()])
async def run_cmd(cmd: str):
    p = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    return StreamingResponse(p.stdout or p.stderr)


@route.get('/status', response_class=JSONResponse, dependencies=[authentication()])
async def status():
    return await get_status()
