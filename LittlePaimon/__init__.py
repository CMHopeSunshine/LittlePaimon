from pathlib import Path
import asyncio

from nonebot import load_plugins, logger
from LittlePaimon import database, web
from LittlePaimon.config import PluginManager
from LittlePaimon.utils import DRIVER, __version__, NICKNAME, SUPERUSERS
from LittlePaimon.utils.tool import check_resource

from typing import Dict, Any
from tortoise.connection import ConnectionHandler

DBConfigType = Dict[str, Any]


async def _init(self, db_config: "DBConfigType", create_db: bool):
    if self._db_config is None:
        self._db_config = db_config
    else:
        self._db_config.update(db_config)
    self._create_db = create_db
    await self._init_connections()


ConnectionHandler._init = _init

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
    await PluginManager.init()
    asyncio.ensure_future(check_resource())


DRIVER.on_shutdown(database.disconnect)

load_plugins(str(Path(__file__).parent / 'plugins'))