from typing import List

from nonebot import get_driver
from pydantic import BaseModel


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
    # 自动米游币获取开始时间（小时）
    paimon_coin_hour: int = 0
    # 自动米游币获取开始时间（分钟）
    paimon_coin_minute: int = 5
    # 对联冷却（秒）
    paimon_couplets_cd: int = 6
    # 猫图冷却（秒）
    paimon_cat_cd: int = 12
    # 二次元图冷却（秒）
    paimon_ecy_cd: int = 6
    # 原神壁纸图冷却（秒）
    paimon_ysp_cd: int = 10
    # 派蒙聊天&机器学习开启群组
    paimon_chat_group: List[int] = []

    # 派蒙猜语音持续时间
    paimon_guess_voice: int = 30
    # 原神日历开启群组
    paimon_calender_group: List[int] = []

    # 以下为机器学习聊天模块配置
    # mongodb数据库连接url
    paimon_mongodb_url: str = None
    # 派蒙聊天屏蔽用户
    paimon_chat_ban: List[int] = []
    # 派蒙聊天学习阈值，越小学习越快
    paimon_answer_threshold: int = 3
    # 派蒙聊天上限阈值
    paimon_answer_limit_threshold: int = 25
    # N个群有相同的回复，就跨群作为全局回复
    paimon_cross_group_threshold: int = 2
    # 复读的阈值
    paimon_repeat_threshold: int = 3
    # 主动发言阈值，越小话越多
    paimon_speak_threshold: int = 3
    # 喝醉的概率
    paimon_drunk_probability: float = 0.07
    # 用文字转语音来回复的概率
    paimon_voice_probability: float = 0.03
    # 连续主动说话的概率
    paimon_speak_continuously_probability: float = 0.5
    # 主动说话加上随机戳一戳群友的概率
    paimon_speak_poke_probability: float = 0.5
    # 连续主动说话最多几句话
    paimon_speak_continuously_max_len: int = 3
    # 禁用词 (如果需要禁用@某人的话格式为 '[CQ:at,qq=(这个人的QQ号)]' 
    # 如: paimon_chat_word_ban: List[str] = ['[CQ:at,qq=12345678]'])
    # 如需禁用全部的@可以填写为 '[CQ:at' , 'at' 等等
    paimon_chat_word_ban: List[str] = []
    # 派蒙收到好友申请或群邀请时是否向超级管理员发通知
    paimon_request_remind: bool = True
    # 是否自动通过好友请求
    paimon_add_friend: bool = False
    # 是否自动通过群组请求
    paimon_add_group: bool = False
    # 禁用群新成员欢迎语和龙王提醒的群号列表
    paimon_greet_ban: List[int] = []


driver = get_driver()
global_config = driver.config
config: PluginConfig = PluginConfig.parse_obj(global_config.dict())
