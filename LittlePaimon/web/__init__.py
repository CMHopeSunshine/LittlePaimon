import nonebot
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from LittlePaimon.config import config
from LittlePaimon.utils import logger, DRIVER
from .api import BaseApiRouter
from .pages import admin_app, login_page, bind_cookie_page, blank_page


requestAdaptor = """
requestAdaptor(api) {
    api.headers["token"] = localStorage.getItem("token");
    return api;
},
"""
responseAdaptor = """
responseAdaptor(api, payload, query, request, response) {
    if (response.data.detail == '登录验证失败或已失效，请重新登录') {
        window.location.href = '/LittlePaimon/login'
        window.localStorage.clear()
        window.sessionStorage.clear()
        window.alert('登录验证失败或已失效，请重新登录')
    }
    return payload
},
"""

icon_path = "https://s1.ax1x.com/2023/02/05/pS62DJK.png"
cdn = "https://npm.onmicrosoft.cn"


@DRIVER.on_startup
def init_web():
    app: FastAPI = nonebot.get_app()
    app.include_router(BaseApiRouter)
    logger.info(
        "Web UI",
        f"<g>启用成功</g>，默认地址为<m>http://127.0.0.1:{DRIVER.config.port}/LittlePaimon/login</m>",
    )

    @app.get("/LittlePaimon/admin", response_class=HTMLResponse)
    async def admin():
        if config.admin_enable:
            return admin_app.render(
                site_title="LittlePaimon 后台管理",
                site_icon=icon_path,
                theme=config.admin_theme,
                cdn=cdn,
                requestAdaptor=requestAdaptor,
                responseAdaptor=responseAdaptor,
            )
        else:
            return blank_page.render(site_title="LittlePaimon", site_icon=icon_path)

    @app.get("/LittlePaimon/login", response_class=HTMLResponse)
    async def login():
        if config.admin_enable:
            return login_page.render(
                site_title="登录 | LittlePaimon 后台管理",
                cdn=cdn,
                site_icon=icon_path,
                theme=config.admin_theme,
            )
        else:
            return blank_page.render(site_title="LittlePaimon", site_icon=icon_path)

    @app.get("/LittlePaimon/cookie", response_class=HTMLResponse)
    async def bind_cookie():
        if config.CookieWeb_enable:
            return bind_cookie_page.render(
                site_title="绑定Cookie | LittlePaimon",
                cdn=cdn,
                site_icon=icon_path,
                theme=config.admin_theme,
            )
        else:
            return blank_page.render(site_title="LittlePaimon", site_icon=icon_path)
