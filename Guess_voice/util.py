import os
from aiohttp import ClientSession
from pathlib import Path
import aiofiles


# def get_path(*paths):
#     return os.path.join(os.path.dirname(__file__), *paths)
def get_path(dirname, filename):
    return Path() / 'data' / 'LittlePaimon' / 'guess_voice' / dirname / filename


async def require_file(file=None,
                       r_mode='rb',
                       encoding=None,
                       url=None,
                       use_cache=True,
                       w_mode='wb',
                       timeout=30):
    async def read():
        async with aiofiles.open(file, r_mode, encoding=encoding) as fp:
            return await fp.read()

    if not any([file, url]):
        raise ValueError('file or url not null')

    file = file and Path(file)

    if file and file.exists() and use_cache:
        return await read()

    if not url:
        raise ValueError('url not null')

    async with ClientSession() as session:
        res = await session.get(url, timeout=timeout)
        content = await res.read()

        if file:
            os.makedirs(os.path.dirname(file), exist_ok=True)
            async with aiofiles.open(file, w_mode, encoding=encoding) as fp:
                await fp.write(content)
                return content
        return await read()
