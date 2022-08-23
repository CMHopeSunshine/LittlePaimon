import nonebot
from fastapi import FastAPI
from pywebio.platform.fastapi import webio_routes
from .bind_cookie import bind_cookie_page

app: FastAPI = nonebot.get_app()

app.mount('/LittlePaimon/cookie', FastAPI(routes=webio_routes(bind_cookie_page)))