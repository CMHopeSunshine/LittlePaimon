from typing import Literal, List

from pydantic import BaseModel, Field


class ConfigModel(BaseModel):
    CookieWeb_enable: bool = Field(True, alias='启用CookieWeb')
    CookieWeb_url: str = Field('http://127.0.0.1:13579/LittlePaimon/cookie', alias='CookieWeb地址')
    qrcode_bind_use_url: bool = Field(False, alias='绑定二维码以链接形式发送')

    img_use_cache: bool = Field(True, alias='图片资源缓存开关')
    reboot_card_enable: List[int] = Field([], alias='重启时修改群名片群列表')

    sim_gacha_cd_group: int = Field(30, alias='模拟抽卡群冷却')
    sim_gacha_cd_member: int = Field(60, alias='模拟抽卡群员冷却')
    sim_gacha_max: int = Field(5, alias='模拟抽卡单次最多十连数')

    auto_myb_enable: bool = Field(True, alias='米游币自动获取开关')
    auto_myb_hour: int = Field(8, alias='米游币开始执行时间(小时)')
    auto_myb_minute: int = Field(0, alias='米游币开始执行时间(分钟)')

    auto_sign_enable: bool = Field(False, alias='米游社自动签到开关')
    auto_sign_hour: int = Field(0, alias='米游社签到开始时间(小时)')
    auto_sign_minute: int = Field(5, alias='米游社签到开始时间(分钟)')

    ssbq_enable: bool = Field(True, alias='实时便签检查开关')
    ssbq_begin: int = Field(0, alias='实时便签停止检查开始时间')
    ssbq_end: int = Field(6, alias='实时便签停止检查结束时间')
    ssbq_check: int = Field(16, alias='实时便签检查间隔')

    ys_auto_update: int = Field(24, alias='ys自动更新小时')
    ysa_auto_update: int = Field(24, alias='ysa自动更新小时')
    ysd_auto_update: int = Field(6, alias='ysd自动更新小时')

    cloud_genshin_enable: bool = Field(True, alias='云原神自动签到开关')
    cloud_genshin_hour: int = Field(7, alias='云原神签到时间(小时)')

    request_event: bool = Field(True, alias='启用好友和群请求通知')
    auto_add_friend: bool = Field(False, alias='自动接受好友请求')
    auto_add_group: bool = Field(False, alias='自动接受群邀请')
    notice_event: bool = Field(True, alias='启用好友和群欢迎消息')

    screenshot_enable: bool = Field(False, alias='启用网页截图权限')

    guess_voice_time: int = Field(30, alias='原神猜语音时间')

    admin_enable: bool = Field(True, alias='启用Web端')
    admin_password: str = Field('admin', alias='Web端管理员密码')
    secret_key: str = Field('49c294d32f69b732ef6447c18379451ce1738922a75cd1d4812ef150318a2ed0', alias='Web端token密钥')
    admin_theme: Literal['default', 'antd', 'ang', 'dark'] = Field('default', alias='Web端主题')

    command_alias_enable: bool = Field(True, alias='启用命令别名')
    browser_type: Literal['chromium', 'firefox', 'webkit'] = Field('firefox', alias='浏览器内核')

    # 早报60s
    morning_news: str = Field('https://api.vvhan.com/api/60s', alias='早报60s')

    github_proxy: str = Field('https://github.cherishmoon.fun/', alias='github资源地址')

    @property
    def alias_dict(self):
        return {v.alias: k for k, v in self.__fields__.items()}

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__fields__:
                self.__setattr__(key, value)
            elif key in self.alias_dict:
                self.__setattr__(self.alias_dict[key], value)
