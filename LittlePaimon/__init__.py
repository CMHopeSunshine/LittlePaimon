from nonebot import load_plugins, get_driver, logger
from typing import List
from pathlib import Path
from .database.connect import connect, disconnect
from .manager import plugin_manager

DRIVER = get_driver()

try:
    SUPERUSERS: List[str] = list(DRIVER.config.superusers)
except KeyError:
    logger.error('请在.env.prod中配置超级用户')

try:
    NICKNAME: str = list(DRIVER.config.superusers)[0]
except KeyError:
    NICKNAME = '派蒙'


@DRIVER.on_startup
async def startup():
    await connect()
    plugin_manager.init_plugins()


DRIVER.on_shutdown(disconnect)

# load_plugins(str(Path(__file__).parent / 'plugins'))
