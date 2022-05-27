from pydantic import BaseModel
from nonebot import get_driver
from typing import List



class PluginConfig(BaseModel):
    enable_group: List[int] = []


config: PluginConfig = PluginConfig.parse_obj(get_driver().config.dict())
