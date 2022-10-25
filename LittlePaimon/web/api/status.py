import asyncio

# from nonebot import logger
# from nonebot.log import default_filter, default_format
# from LittlePaimon import DRIVER
from LittlePaimon.utils.status import get_status

from fastapi.responses import JSONResponse
from fastapi import APIRouter

from .utils import authentication

show_logs = []


# @DRIVER.on_startup
# async def start_up():
#
#     def record_log(message: str):
#         show_logs.append(message)
#
#     logger.opt(colors=True, ansi=True).add(record_log, colorize=True, filter=default_filter, format=default_format)


route = APIRouter()


# @route.get('/log', response_class=StreamingResponse)
# async def get_log():
#     async def streaming_logs():
#         count = 0
#         while True:
#             if show_logs:
#                 yield show_logs.pop(0)
#                 count = 0
#             else:
#                 count += 1
#                 if count > 600:
#                     yield '超过一分钟没有新日志，日志已断开，请刷新页面重新连接\n'
#                     await asyncio.sleep(2)
#                     break
#                 else:
#                     yield '\n'
#             await asyncio.sleep(0.1)
#
#     return StreamingResponse(streaming_logs())


@route.get('/status', response_class=JSONResponse, dependencies=[authentication()])
async def status():
    return await get_status()
