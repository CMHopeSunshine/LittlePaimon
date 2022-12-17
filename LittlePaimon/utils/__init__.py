from typing import List

from nonebot import get_driver
from .logger import logger
from .scheduler import scheduler

__version__ = '3.0.0rc7'

DRIVER = get_driver()
try:
    SUPERUSERS: List[int] = [int(s) for s in DRIVER.config.superusers]
except Exception:
    SUPERUSERS = []
    logger.warning('请在.env.prod文件中中配置超级用户SUPERUSERS')

try:
    NICKNAME: str = list(DRIVER.config.nickname)[0]
except Exception:
    NICKNAME = '派蒙'

__all__ = [
    'logger',
    'scheduler',
    'DRIVER',
    'SUPERUSERS',
    'NICKNAME',
    '__version__'
]
