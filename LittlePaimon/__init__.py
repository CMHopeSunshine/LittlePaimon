from pathlib import Path

from nonebot import load_plugins, logger
from LittlePaimon import database, web
from LittlePaimon.utils import DRIVER, __version__, NICKNAME, SUPERUSERS
from LittlePaimon.utils.tool import check_resource

logo = """<g>
██╗     ██╗████████╗████████╗██╗     ███████╗  ██████╗  █████╗ ██╗███╗   ███╗ ██████╗ ███╗   ██╗
██║     ██║╚══██╔══╝╚══██╔══╝██║     ██╔════╝  ██╔══██╗██╔══██╗██║████╗ ████║██╔═══██╗████╗  ██║
██║     ██║   ██║      ██║   ██║     █████╗    ██████╔╝███████║██║██╔████╔██║██║   ██║██╔██╗ ██║
██║     ██║   ██║      ██║   ██║     ██╔══╝    ██╔═══╝ ██╔══██║██║██║╚██╔╝██║██║   ██║██║╚██╗██║
███████╗██║   ██║      ██║   ███████╗███████╗  ██║     ██║  ██║██║██║ ╚═╝ ██║╚██████╔╝██║ ╚████║
╚══════╝╚═╝   ╚═╝      ╚═╝   ╚══════╝╚══════╝  ╚═╝     ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝</g>"""


@DRIVER.on_startup
async def startup():
    logger.opt(colors=True).info(logo)
    await database.connect()
    await check_resource()


DRIVER.on_shutdown(database.disconnect)

load_plugins(str(Path(__file__).parent / 'plugins'))
