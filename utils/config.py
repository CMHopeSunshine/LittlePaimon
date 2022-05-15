from pydantic import BaseModel
from nonebot import get_driver
from typing import List


class PluginConfig(BaseModel):
    # 群组模拟抽卡冷却（秒）
    paimon_gacha_cd_group: int = 30
    # 个人模拟抽卡冷却（秒）
    paimon_gacha_cd_user: int = 60
    # 树脂提醒停止检查时间（小时）
    paimon_remind_start: int = 0
    paimon_remind_end: int = 8
    # 树脂提醒检查间隔（分钟）
    paimon_check_interval: int = 16
    # 树脂提醒每日提醒次数上限
    paimon_remind_limit: int = 3
    # 自动签到开始时间（小时）
    paimon_sign_hour: int = 0
    # 自动签到开始时间（分钟）
    paimon_sign_minute: int = 0
    # 对联冷却（秒）
    paimon_couplets_cd: int = 6
    # 猫图冷却（秒）
    paimon_cat_cd: int = 12
    # 二次元图冷却（秒）
    paimon_ecy_cd: int = 6
    # 原神壁纸图冷却（秒）
    paimon_ysp_cd: int = 10
    # 是否自动通过好友请求
    paimon_add_friend: bool = False
    # 是否自动通过群组请求
    paimon_add_group: bool = False
    # 派蒙聊天开启群组
    paimon_chat_group: List[int] = []
    # 派蒙猜语音持续时间
    paimon_guess_voice: int = 30


driver = get_driver()
global_config = driver.config
config: PluginConfig = PluginConfig.parse_obj(global_config.dict())
