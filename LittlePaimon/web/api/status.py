import asyncio
from typing import Union, Optional

from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse, StreamingResponse
from nonebot.log import logger, default_filter, default_format
from LittlePaimon.config import config
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


@route.get('/log')
async def get_log(token: Optional[str] = Header(...), level: str = 'info', num: Union[int, str] = 100):
    if token != config.secret_key[:16]:
        return '非法请求'
    show_logs = info_logs[-(num or 1):] if level == 'info' else debug_logs[-(num or 1):]

    async def streaming_logs():
        for log in show_logs:
            yield log
            await asyncio.sleep(0.02)

    return StreamingResponse(streaming_logs())


@route.get('/run_cmd')
async def run_cmd(token: Optional[str] = Header(...), cmd: str = ''):
    if token != config.secret_key[:16]:
        return '非法请求'
    if not cmd:
        return '无效命令'
    p = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    return StreamingResponse(p.stdout or p.stderr)


@route.get('/status', response_class=JSONResponse, dependencies=[authentication()])
async def status():
    return await get_status()
