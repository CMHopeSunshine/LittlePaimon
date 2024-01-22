from contextlib import asynccontextmanager
from contextlib import suppress
from typing import Optional, Literal, Tuple, Union, List, AsyncGenerator, AsyncIterator

from playwright.async_api import Page, Browser, Playwright, async_playwright, Error

from . import DRIVER
from .logger import logger
from LittlePaimon.config import config as bot_config

_playwright: Optional[Playwright] = None
_browser: Optional[Browser] = None
_browser_type = bot_config.browser_type


async def init(**kwargs) -> Browser:
    global _browser
    global _playwright
    try:
        _playwright = await async_playwright().start()
        _browser = await launch_browser(**kwargs)
    except NotImplementedError:
        logger.warning('Playwright', '初始化失败，请关闭FASTAPI_RELOAD')
    except Error:
        await install_browser()
        _browser = await launch_browser(**kwargs)
    return _browser


async def launch_browser(**kwargs) -> Browser:
    assert _playwright is not None, "Playwright is not initialized"

    if _browser_type == 'firefox':
        return await _playwright.firefox.launch(**kwargs)
    elif _browser_type == 'chromium':
        return await _playwright.chromium.launch(**kwargs)
    elif _browser_type == 'webkit':
        return await _playwright.webkit.launch(**kwargs)


async def get_browser(**kwargs) -> Browser:
    return _browser or await init(**kwargs)


async def install_browser():
    import os
    import sys

    from playwright.__main__ import main

    logger.info('Playwright', f'正在安装 {_browser_type}')
    sys.argv = ["", "install", f"{_browser_type}"]
    with suppress(SystemExit):
        logger.info('Playwright', '正在安装依赖')
        os.system("playwright install-deps")
        main()


@DRIVER.on_startup
async def start_browser(**kwargs):
    await get_browser(**kwargs)
    logger.info('Playwright', '浏览器初始化成功')


@DRIVER.on_shutdown
async def shutdown_browser():
    if _browser:
        await _browser.close()
    if _playwright:
        await _playwright.stop()  # type: ignore


@asynccontextmanager
async def get_new_page(**kwargs) -> AsyncGenerator[Page, None]:
    assert _browser, "playwright尚未初始化"
    page = await _browser.new_page(**kwargs)
    try:
        yield page
    finally:
        await page.close()


async def screenshot(url: str,
                     *,
                     elements: Optional[Union[List[str]]] = None,
                     timeout: Optional[float] = 100000,
                     wait_until: Literal["domcontentloaded", "load", "networkidle", "load", "commit"] = "networkidle",
                     viewport_size: Tuple[int, int] = (1920, 1080),
                     full_page=True,
                     **kwargs):
    if not url.startswith(('https://', 'http://')):
        url = f'https://{url}'
    viewport_size = {'width': viewport_size[0], 'height': viewport_size[1]}
    brower = await get_browser()
    page = await brower.new_page(
        viewport=viewport_size,
        **kwargs)
    try:
        await page.goto(url, wait_until=wait_until, timeout=timeout)
        assert page
        if not elements:
            return await page.screenshot(timeout=timeout, full_page=full_page)
        for e in elements:
            card = await page.wait_for_selector(e, timeout=timeout, state='visible')
            assert card
            clip = await card.bounding_box()
        return await page.screenshot(clip=clip, timeout=timeout, full_page=full_page, path='test.png')

    except Exception as e:
        raise e
    finally:
        if page:
            await page.close()


@asynccontextmanager
async def get_new_page(**kwargs) -> AsyncIterator[Page]:
    browser = await get_browser()
    page = await browser.new_page(**kwargs)
    try:
        yield page
    finally:
        await page.close()
