import asyncio
import hashlib
import time
from collections import defaultdict
from LittlePaimon.utils import aiorequests, logger
from LittlePaimon.config import RESOURCE_BASE_PATH


class FreqLimiter:
    """
    频率限制器（冷却时间限制器）
    """

    def __init__(self):
        """
        初始化一个频率限制器
        """
        self.next_time = defaultdict(float)

    def check(self, key: str) -> bool:
        """
        检查是否冷却结束
        :param key: key
        :return: 布尔值
        """
        return time.time() >= self.next_time[key]

    def start(self, key: str, cooldown_time: int = 0):
        """
        开始冷却
        :param key: key
        :param cooldown_time: 冷却时间(秒)
        """
        self.next_time[key] = time.time() + (cooldown_time if cooldown_time > 0 else 60)

    def left(self, key: str) -> int:
        """
        剩余冷却时间
        :param key: key
        :return: 剩余冷却时间
        """
        return int(self.next_time[key] - time.time()) + 1


freq_limiter = FreqLimiter()


async def check_resource():
    logger.info('资源检查', '开始检查资源')
    resource_list = await aiorequests.get('http://img.genshin.cherishmoon.fun/resources/resources_list')
    resource_list = resource_list.json()
    flag = False
    for resource in resource_list:
        file_path = RESOURCE_BASE_PATH.parent / resource['path']
        if file_path.exists():
            if not resource['lock'] or hashlib.md5(file_path.read_bytes()).hexdigest() == resource['hash']:
                continue
            else:
                file_path.unlink()
        flag = True
        try:
            await aiorequests.download(url=f'http://img.genshin.cherishmoon.fun/resources/{resource["path"]}', save_path=file_path)
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.warning('资源检查', f'下载<m>{resource.split("/")[-1]}</m>时<r>出错: {e}</r>')
    if flag:
        logger.info('资源检查', '<g>资源下载完成</g>')
    else:
        logger.info('资源检查', '<g>资源完好，无需下载</g>')


