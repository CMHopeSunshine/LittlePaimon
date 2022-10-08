from typing import Optional, Literal, Tuple, Union, List, AsyncGenerator
from playwright.async_api import Page, Browser, Playwright, async_playwright
from contextlib import asynccontextmanager
from LittlePaimon import DRIVER
from LittlePaimon.utils import logger

_playwright: Optional[Playwright] = None
_browser: Optional[Browser] = None


def get_brower() -> Browser:
    assert _browser
    return _browser


@DRIVER.on_startup
async def start_browser():
    global _playwright
    global _browser
    try:
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(headless=True)
    except NotImplementedError:
        logger.warning('Playwright', '初始化失败，请关闭FASTAPI_RELOAD')
    except Exception as e:
        logger.warning('Playwright', f'初始化失败，错误信息：{e}')
        if _browser:
            await _browser.close()


@DRIVER.on_shutdown
async def shutdown_browser():
    if _browser:
        await _browser.close()
    if _playwright:
        await _playwright.stop()


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
    brower = get_brower()
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
