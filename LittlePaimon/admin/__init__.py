import nonebot
from fastapi import FastAPI
from LittlePaimon.utils import logger
from LittlePaimon.manager.plugin_manager import plugin_manager

app: FastAPI = nonebot.get_app()

if plugin_manager.config.CookieWeb_enable:
    from pywebio.platform.fastapi import webio_routes
    from .bind_cookie import bind_cookie_page
    logger.info('原神Cookie', f'<g>启用CookieWeb成功，地址{plugin_manager.config.CookieWeb_url}</g>')
    app.mount('/LittlePaimon/cookie', FastAPI(routes=webio_routes(bind_cookie_page)))
