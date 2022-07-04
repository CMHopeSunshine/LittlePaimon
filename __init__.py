import asyncio
import hashlib
import shutil
from pathlib import Path

from littlepaimon_utils.files import load_json, download
from nonebot import get_driver, logger


driver = get_driver()

resource_list = load_json(path=Path(__file__).parent / 'resource_list.json')
old_resource_path = Path(__file__).parent / 'res'
new_resource_path = Path().cwd() / 'resources' / 'LittlePaimon'

old_user_data_path = Path(__file__).parent / 'user_data'
new_user_data_path = Path().cwd() / 'data' / 'LittlePaimon' / 'user_data'


@driver.on_startup
async def check_resource():
    # 迁移旧用户数据文件
    if old_user_data_path.exists():
        new_user_data_path.mkdir(parents=True, exist_ok=True)
        for file in old_user_data_path.iterdir():
            shutil.move(file, new_user_data_path)

    # 迁移旧资源文件
    logger.info('检查LittlePaimon资源文件')
    if old_resource_path.exists():
        new_resource_path.mkdir(parents=True, exist_ok=True)
        for file in old_resource_path.iterdir():
            shutil.move(file, new_resource_path)

    # 检验资源文件并下载
    for resource in resource_list:
        res_path = new_resource_path / resource['path'].replace('LittlePaimon/', '')
        download_url = 'http://genshin.cherishmoon.fun/res/' + resource['path'].replace('LittlePaimon/', '')
        if res_path.exists() and hashlib.md5(res_path.read_bytes()).hexdigest() == resource['hash']:
            continue
        try:
            await download(download_url, res_path)
            await asyncio.sleep(0.3)
        except Exception as e:
            logger.warning(resource['path'].split('/')[-1] + 'download failed: ' + str(e))


