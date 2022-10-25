from fastapi import APIRouter
from .cookie import route as cookie_route
from .plugin import route as plugin_route
from .bot_info import route as bot_info_route
from .status import route as status_route
from .login import route as login_route
from .utils import authentication
# from .learning_chat import route as chat_route

BaseApiRouter = APIRouter(prefix='/LittlePaimon/api')

BaseApiRouter.include_router(cookie_route)
BaseApiRouter.include_router(plugin_route)
BaseApiRouter.include_router(bot_info_route)
BaseApiRouter.include_router(status_route)
BaseApiRouter.include_router(login_route)
# BaseApiRouter.include_router(chat_route)
