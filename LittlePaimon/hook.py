import asyncio
import inspect

from nonebot import get_driver, get_bot
from nonebot.adapters import Bot
from nonebot.utils import is_coroutine_callable, run_sync
from typing import Callable

_start_up_func = []
_start_up_func_after_db = []
_shutdown_func = []
_shutdown_func_before_db = []

driver = get_driver()


@driver.on_startup
async def _run_start_up():
    await asyncio.gather(*_start_up_func)
    ...
    await asyncio.gather(*_start_up_func_after_db)


@driver.on_shutdown
async def _run_shutdown():
    await asyncio.gather(*_shutdown_func)
    ...
    await asyncio.gather(*_shutdown_func_before_db)


def on_startup(database: bool = False) -> Callable:
    """
    包裹一个函数，使其在bot启动完成时运行，如果该函数有数据库相关处理，参数database需为True

    :param database: 是否有数据库相关处理
    """

    def return_func(func: Callable) -> Callable:
        if database:
            _start_up_func_after_db.append(func)
        else:
            _start_up_func.append(func)
        return func

    return return_func


def on_shutdown(database: bool = False) -> Callable:
    """
    包裹一个函数，使其在bot停止前运行，如果该函数有数据库相关处理，参数database需为True

    :param database: 是否有数据库相关处理
    """

    def return_func(func: Callable) -> Callable:
        if database:
            _shutdown_func_before_db.append(func)
        else:
            _shutdown_func.append(func)
        return func

    return return_func


async def handle_func_params(func: Callable):
    """
    处理函数依赖注入，已支持的注入参数有：

    - bot: nonebot.adapters.Bot及其子类，默认值可为bot_id来指定bot，例如：bot: Bot = 123456789

    :param func:
    :return:
    """
    func = func if is_coroutine_callable(func) else run_sync(func)
    param = inspect.signature(func).parameters
    if 'bot' in param and issubclass(param['bot'].annotation, Bot):
        default = param['bot'].default
        if default == inspect.Parameter.empty:
            await func(bot=get_bot())
        elif isinstance(default, (int, str)):
            await func(bot=get_bot(default))
        else:
            await func()
    else:
        await func()
