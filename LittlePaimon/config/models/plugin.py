from typing import List, Dict, Literal, DefaultDict, Optional
from collections import defaultdict
from pydantic import BaseModel


# class Ban(BaseModel):
#     """插件屏蔽列表"""
#     all_groups: bool = False
#     """屏蔽所有群组"""
#     group: List[int] = []
#     """屏蔽群组列表"""
#     all_privates: bool = False
#     """屏蔽所有群组"""
#     private: List[int] = []
#     """屏蔽私聊列表"""
#     group_member: List[str] = []
#     """屏蔽群组中特定成员列表"""
#     all_guilds: bool = False
#     """屏蔽所有频道"""
#     guild: List[int] = []
#     """屏蔽频道列表"""
#     guild_channel: List[str] = []
#     """屏蔽频道中特定子频道列表"""
#     invert_selection: Dict[Literal['group', 'private', 'group_member', 'guild', 'guild_channel'], bool] = {
#         'group':         False,
#         'private':       False,
#         'group_member':  False,
#         'guild':         False,
#         'guild_channel': False}
#     """是否反选"""
#
#     def check(self, event: MessageEvent) -> bool:
#         if isinstance(event, GroupMessageEvent):
#             if self.all_groups:
#                 return False
#             if event.group_id in self.group:
#                 return self.invert_selection['group']
#             if f'{event.group_id}_{event.user_id}' in self.group_member:
#                 return self.invert_selection['group_member']
#             return True
#         elif isinstance(event, PrivateMessageEvent):
#             if self.all_privates:
#                 return False
#             if event.user_id in self.private:
#                 return self.invert_selection['private']
#             return True
#         elif event.message_type == 'guild':
#             if self.all_guilds:
#                 return False
#             if event.guild_id in self.guild:
#                 return self.invert_selection['guild']
#             if f'{event.guild_id}_{event.channel_id}' in self.guild_channel:
#                 return self.invert_selection['guild_channel']
#             return True
#         else:
#             raise TypeError(f'{event.message_type} is not supported by plugin manager')


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

