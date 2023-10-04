import asyncio
import os
from pathlib import Path
from typing import Dict, Any

from nonebot import logger, load_plugin
from nonebot.plugin import PluginMetadata
from tortoise.connection import ConnectionHandler

from LittlePaimon import database, web
from LittlePaimon.config import PluginManager
from LittlePaimon.utils import DRIVER, __version__, NICKNAME, SUPERUSERS
from LittlePaimon.utils.tool import check_resource

# https://nonebot.dev/docs/developer/plugin-publishing#%E5%A1%AB%E5%86%99%E6%8F%92%E4%BB%B6%E5%85%83%E6%95%B0%E6%8D%AE
__plugin_meta__ = PluginMetadata(
    name="LittlePaimon",
    description="小派蒙！原神qq群机器人，基于NoneBot2的UID查询、抽卡导出分析、模拟抽卡、实时便签、札记等多功能小助手。",
    usage="https://docs.paimon.cherishmoon.fun/",
    type="application",
    homepage="https://github.com/CMHopeSunshine/LittlePaimon",
    supported_adapters={"~onebot.v11"},
)


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

# load_plugins(str(Path(__file__).parent / 'plugins'))
for plugin in os.listdir(str(Path(__file__).parent / 'plugins')):
    load_plugin(f"LittlePaimon.plugins.{plugin}")
