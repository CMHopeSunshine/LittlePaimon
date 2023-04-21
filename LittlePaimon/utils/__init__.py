from typing import List

from nonebot import get_driver
from .logger import logger
from .scheduler import scheduler

__version__ = '1.8.9'

DRIVER = get_driver()
try:
    SUPERUSERS: List[int] = [int(s) for s in DRIVER.config.superusers]
except Exception:
    SUPERUSERS = []

if not SUPERUSERS or SUPERUSERS == ['123456']:
    logger.warning('超级用户配置', '请在.env.prod文件中配置超级用户SUPERUSERS')

try:
    NICKNAME: str = list(DRIVER.config.nickname)[0]
except Exception:
    NICKNAME = '脑积水'

__all__ = ['logger', 'scheduler', 'DRIVER', 'SUPERUSERS', 'NICKNAME', '__version__']
