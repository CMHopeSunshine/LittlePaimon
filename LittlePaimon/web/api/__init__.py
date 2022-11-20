from fastapi import APIRouter

from .bot_info import route as bot_info_route
from .cookie import route as cookie_route
from .login import route as login_route
from .plugin import route as plugin_route
from .status import route as status_route
from .utils import authentication
from .command_alias import route as command_alias_route

BaseApiRouter = APIRouter(prefix='/LittlePaimon/api')

BaseApiRouter.include_router(cookie_route)
BaseApiRouter.include_router(plugin_route)
BaseApiRouter.include_router(bot_info_route)
BaseApiRouter.include_router(status_route)
BaseApiRouter.include_router(login_route)
BaseApiRouter.include_router(command_alias_route)
