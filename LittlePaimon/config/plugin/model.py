from typing import Optional, List

from pydantic import BaseModel


class MatcherInfo(BaseModel):
    pm_name: str
    """命令名称"""
    pm_description: Optional[str]
    """命令描述"""
    pm_usage: Optional[str]
    """命令用法"""
    pm_priority: int = 99
    """命令优先级"""
    pm_show: bool = True
    """是否展示"""


class PluginInfo(BaseModel):
    name: str
    """插件名称"""
    module_name: str
    """插件模块名称"""
    description: Optional[str]
    """插件描述"""
    usage: Optional[str]
    """插件用法"""
    status: Optional[bool]
    """插件状态（无用项）"""
    show: bool = True
    """是否展示"""
    priority: int = 99
    """展示优先级"""
    matchers: Optional[List[MatcherInfo]] = []
    """命令列表"""
