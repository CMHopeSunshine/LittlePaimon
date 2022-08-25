import nonebot
from fastapi import FastAPI
from LittlePaimon.utils import logger
from LittlePaimon.manager.plugin_manager import plugin_manager

app: FastAPI = nonebot.get_app()

if plugin_manager.get_config('启用CookieWeb', False):
    from pywebio.platform.fastapi import webio_routes
    from .bind_cookie import bind_cookie_page
    logger.info('原神Cookie', f'<g>启用CookieWeb成功</g>，{plugin_manager.get_config("CookieWeb地址")}')
    app.mount('/LittlePaimon/cookie', FastAPI(routes=webio_routes(bind_cookie_page)))
