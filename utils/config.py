from pydantic import BaseModel
from nonebot import get_driver
from typing import List


class PluginConfig(BaseModel):
    paimon_gacha_cd_group: int = 30
    paimon_gacha_cd_user: int = 60
    paimon_remind_start: int = 0
    paimon_remind_end: int = 8
    paimon_check_interval: int = 16
    paimon_remind_limit: int = 3
    paimon_sign_hour: int = 0
    paimon_sign_minute: int = 0
    paimon_duilian_cd: int = 6
    paimon_cat_cd: int = 12
    paimon_ecy_cd: int = 6
    paimon_ysp_cd: int = 10
    paimon_add_friend: bool = False
    paimon_add_group: bool = False
    paimon_chat_group: List[int] = []


driver = get_driver()
global_config = driver.config
config: PluginConfig = PluginConfig.parse_obj(global_config.dict())
