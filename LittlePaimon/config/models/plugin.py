from typing import Literal, DefaultDict
from collections import defaultdict
from pydantic import BaseModel


class Statistics(BaseModel):
    """
    插件调用统计
    """
    month: DefaultDict[int, int] = defaultdict(lambda: 0)
    """月统计"""
    week: DefaultDict[int, int] = defaultdict(lambda: 0)
    """周统计"""
    day: DefaultDict[int, int] = defaultdict(lambda: 0)
    """日统计"""

    def add(self, user_id: int):
        """
        增加统计数据
        :param user_id: 用户id
        """
        self.day[user_id] += 1
        self.week[user_id] += 1
        self.month[user_id] += 1

    def clear(self, type: Literal['month', 'week', 'day']):
        """
        清除统计数据
        :param type: 统计类型
        """
        if type == 'month':
            self.month.clear()
        elif type == 'week':
            self.week.clear()
        elif type == 'day':
            self.day.clear()

