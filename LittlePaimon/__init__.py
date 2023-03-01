from pathlib import Path
from typing import Union

import nonebot
from .log import init_logger
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter


def run(*args, **kwargs):
    init_logger()
    nonebot.init()
    app = nonebot.get_asgi()
    driver = nonebot.get_driver()
    driver.register_adapter(ONEBOT_V11Adapter)
    nonebot.run(app=app, *args, **kwargs)


def load_plugin(name: Union[str, Path]):
    nonebot.load_plugin(name)
