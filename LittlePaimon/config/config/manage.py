from LittlePaimon.utils.files import load_yaml, save_yaml
from LittlePaimon.utils.path import PAIMON_CONFIG
from .model import ConfigModel


class ConfigManager:
    if PAIMON_CONFIG.exists():
        config = ConfigModel.parse_obj(load_yaml(PAIMON_CONFIG))
    else:
        config = ConfigModel()
        save_yaml(config.dict(by_alias=True), PAIMON_CONFIG)

    @classmethod
    def set_config(cls, config_name: str, value: any):
        """
        设置派蒙配置项
            :param config_name: 配置名
            :param value: 新配置值
        """
        if config_name not in cls.config.dict(by_alias=True).keys():
            return f"没有配置项为{config_name}"
        if (
            "启用" in config_name
            or "开关" in config_name
            or config_name in {"自动接受好友请求", "自动接受群邀请", "绑定二维码以链接形式发送"}
        ):
            if value not in ["开", "关", "true", "false", "on", "off"]:
                return "参数错误"
            value = value in ["开", "true", "on"]
        elif config_name == "重启时修改群名片群列表":
            return "该配置项暂时不支持此方法修改，请在后台管理页面进行更改"
        elif config_name not in ["CookieWeb地址", "Web端管理员密码", "Web端token密钥", "github资源地址"]:
            if not value.isdigit():
                return "配置项不合法，必须为数字"
            value = int(value)
        cls.config.update(**{config_name: value})
        cls.save()
        return f"成功设置{config_name}为{value}"

    @classmethod
    def save(cls):
        save_yaml(cls.config.dict(by_alias=True), PAIMON_CONFIG)


config = ConfigManager.config
