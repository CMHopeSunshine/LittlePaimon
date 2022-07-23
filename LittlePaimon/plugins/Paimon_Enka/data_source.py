from asyncio import sleep

from nonebot import logger

from LittlePaimon.utils import aiorequests


async def get_enka_data(uid):
    for i in range(3):
        try:
            url = f'https://enka.shinshin.moe/u/{uid}/__data.json'
            resp = await aiorequests.get(url=url, follow_redirects=True)
            data = resp.json()
            return data
        except Exception as e:
            logger.warning(f'获取enka数据失败，重试第{i + 1}次，{e}')
            await sleep(1.5)
