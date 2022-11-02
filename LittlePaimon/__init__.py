from pathlib import Path

from nonebot import load_plugins, get_driver, logger, load_plugin
from typing import List
# from LittlePaimon.utils.migration import migrate_database
from LittlePaimon.utils.tool import check_resource

DRIVER = get_driver()
__version__ = '3.0.0rc2'

try:
    SUPERUSERS: List[int] = [int(s) for s in DRIVER.config.superusers]
except KeyError:
    SUPERUSERS = []
    logger.warning('请在.env.prod文件中中配置超级用户SUPERUSERS')

try:
    NICKNAME: str = list(DRIVER.config.nickname)[0]
except KeyError:
    NICKNAME = '派蒙'

logo = """<g>
██╗     ██╗████████╗████████╗██╗     ███████╗  ██████╗  █████╗ ██╗███╗   ███╗ ██████╗ ███╗   ██╗
██║     ██║╚══██╔══╝╚══██╔══╝██║     ██╔════╝  ██╔══██╗██╔══██╗██║████╗ ████║██╔═══██╗████╗  ██║
██║     ██║   ██║      ██║   ██║     █████╗    ██████╔╝███████║██║██╔████╔██║██║   ██║██╔██╗ ██║
██║     ██║   ██║      ██║   ██║     ██╔══╝    ██╔═══╝ ██╔══██║██║██║╚██╔╝██║██║   ██║██║╚██╗██║
███████╗██║   ██║      ██║   ███████╗███████╗  ██║     ██║  ██║██║██║ ╚═╝ ██║╚██████╔╝██║ ╚████║
╚══════╝╚═╝   ╚═╝      ╚═╝   ╚══════╝╚══════╝  ╚═╝     ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝</g>"""


@DRIVER.on_startup
async def startup():
    from LittlePaimon.database import connect
    logger.opt(colors=True).info(logo)
    await connect()
    from LittlePaimon import web
    # await migrate_database()
    await check_resource()


@DRIVER.on_shutdown
async def shutdown():
    from LittlePaimon.database import disconnect
    await disconnect()


load_plugins(str(Path(__file__).parent / 'plugins'))
