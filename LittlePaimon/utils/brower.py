# https://github.com/HibiKier/zhenxun_bot/blob/main/utils
import asyncio
from pathlib import Path
from typing import Optional, Literal, Union, List, Dict
from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageSegment
from playwright.async_api import Browser, async_playwright, Page, BrowserContext

_browser: Optional[Browser] = None


async def init(**kwargs) -> Optional[Browser]:
    global _browser
    browser = await async_playwright().start()
    try:
        _browser = await browser.chromium.launch(**kwargs)
        return _browser
    except Exception:
        await asyncio.get_event_loop().run_in_executor(None, install)
        _browser = await browser.chromium.launch(**kwargs)
    return None


async def get_browser(**kwargs) -> Browser:
    return _browser or await init(**kwargs)


def install():
    """自动安装、更新 Chromium"""
    logger.info("正在检查 Chromium 更新")
    import sys
    from playwright.__main__ import main

    sys.argv = ["", "install", "chromium"]
    try:
        main()
    except SystemExit:
        pass


class AsyncPlaywright:
    @classmethod
    async def _new_page(cls, user_agent: Optional[str] = None, **kwargs) -> Page:
        """
        说明:
            获取一个新页面
        参数:
            :param user_agent: 请求头
        """
        browser = await get_browser()
        if browser:
            return await browser.new_page(user_agent=user_agent, **kwargs)
        logger.info('获取浏览器失败')
        raise BrowserIsNone('获取浏览器失败')

    @classmethod
    async def new_context(cls, user_agent: Optional[str] = None, **kwargs) -> BrowserContext:
        """
        说明:
            获取一个新上下文
        参数:
            :param user_agent: 请求头
        """
        browser = await get_browser()
        if browser:
            return await browser.new_context(user_agent=user_agent, **kwargs)
        logger.info('获取浏览器失败')
        raise BrowserIsNone('获取浏览器失败')

    @classmethod
    async def goto(
            cls,
            url: str,
            *,
            timeout: Optional[float] = 100000,
            wait_until: Optional[
                Literal["domcontentloaded", "load", "networkidle"]
            ] = "networkidle",
            referer: str = None,
            **kwargs
    ) -> Optional[Page]:
        """
        说明:
            goto
        参数:
            :param url: 网址
            :param timeout: 超时限制
            :param wait_until: 等待类型
            :param referer:
        """
        page = None
        try:
            page = await cls._new_page(**kwargs)
            await page.goto(url, timeout=timeout, wait_until=wait_until, referer=referer)
            return page
        except Exception as e:
            logger.warning(f"Playwright 访问 url：{url} 发生错误 {type(e)}：{e}")
            if page:
                await page.close()
        return None

    @classmethod
    async def screenshot(
            cls,
            url: str,
            *,
            element: Optional[Union[str, List[str]]] = None,
            path: Optional[Union[Path, str]] = None,
            wait_time: Optional[int] = None,
            viewport_size: Dict[str, int] = None,
            wait_until: Optional[
                Literal["domcontentloaded", "load", "networkidle"]
            ] = "networkidle",
            timeout: float = None,
            **kwargs
    ) -> Optional[MessageSegment]:
        """
        说明:
            截图，该方法仅用于简单快捷截图，复杂截图请操作 page
        参数:
            :param url: 网址
            :param path: 存储路径
            :param element: 元素选择
            :param wait_time: 等待截取超时时间
            :param viewport_size: 窗口大小
            :param wait_until: 等待类型
            :param timeout: 超时限制
        """
        if not url.startswith(('https://', 'http://')):
            url = f'https://{url}'
        page = None
        if viewport_size is None:
            viewport_size = dict(width=1920, height=1080)
        if path and isinstance(path, str):
            path = Path(path)
        try:
            page = await cls.goto(url, wait_until=wait_until, **kwargs)
            await page.set_viewport_size(viewport_size)
            if element:
                if isinstance(element, str):
                    if wait_time:
                        card = await page.wait_for_selector(element, timeout=wait_time * 1000)
                    else:
                        card = await page.query_selector(element)
                else:
                    card = page
                    for e in element:
                        if wait_time:
                            card = await card.wait_for_selector(e, timeout=wait_time * 1000)
                        else:
                            card = await card.query_selector(e)
            else:
                card = page
            if path:
                img = await card.screenshot(path=path, timeout=timeout, full_page=False)
            else:
                img = await card.screenshot(timeout=timeout, full_page=False)
            return MessageSegment.image(img)
        except Exception as e:
            logger.warning(f"Playwright 截图 url：{url} element：{element} 发生错误 {type(e)}：{e}")
            return MessageSegment.text(f'截图失败，报错信息：{e}')
        finally:
            if page:
                await page.close()


class UrlPathNumberNotEqual(Exception):
    pass


class BrowserIsNone(Exception):
    pass
