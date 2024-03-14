import datetime
from typing import List, Dict, Tuple, Optional

from pydantic import BaseModel

from LittlePaimon.utils.alias import get_chara_icon, get_weapon_icon

GACHA_TYPE_LIST = {'100': '新手祈愿', '200': '常驻祈愿', '302': '武器祈愿', '301': '角色祈愿', '400': '角色祈愿', '500': '集录祈愿'}


class FiveStarItem(BaseModel):
    name: str
    icon: Optional[str]
    count: int
    type: str


class FourStarItem(BaseModel):
    name: str
    icon: Optional[str]
    type: str
    num: Dict[str, int] = {
        '角色祈愿': 0,
        '武器祈愿': 0,
        '常驻祈愿': 0,
        '新手祈愿': 0,
        '集录祈愿': 0}


class GachaItem(BaseModel):
    id: str
    name: str
    gacha_type: str
    item_type: str
    rank_type: str
    time: datetime.datetime


class GachaLogInfo(BaseModel):
    user_id: str
    uid: str
    update_time: datetime.datetime
    item_list: Dict[str, List[GachaItem]] = {
        '角色祈愿': [],
        '武器祈愿': [],
        '常驻祈愿': [],
        '新手祈愿': [],
        '集录祈愿': []
    }

    def get_record_time(self) -> Dict[str, Tuple[datetime.datetime, datetime.datetime]]:
        return {
            '角色祈愿': (self.item_list['角色祈愿'][0].time, self.item_list['角色祈愿'][-1].time) if self.item_list['角色祈愿'] else (None, None),
            '武器祈愿': (self.item_list['武器祈愿'][0].time, self.item_list['武器祈愿'][-1].time) if self.item_list['武器祈愿'] else (None, None),
            '常驻祈愿': (self.item_list['常驻祈愿'][0].time, self.item_list['常驻祈愿'][-1].time) if self.item_list['常驻祈愿'] else (None, None),
            '新手祈愿': (self.item_list['新手祈愿'][0].time, self.item_list['新手祈愿'][-1].time) if self.item_list['新手祈愿'] else (None, None),
            '集录祈愿': (self.item_list['集录祈愿'][0].time, self.item_list['集录祈愿'][-1].time) if self.item_list['集录祈愿'] else (None, None),
        }

    def get_statistics(self) -> Tuple[Dict[str, List[FiveStarItem]], Dict[str, FourStarItem],  Dict[str, int]]:
        gacha_data_five: Dict[str, List[FiveStarItem]] = {
            '角色祈愿': [],
            '武器祈愿': [],
            '常驻祈愿': [],
            '新手祈愿': [],
            '集录祈愿': []
        }
        gacha_data_four: Dict[str, FourStarItem] = {}
        gacha_not_out: Dict[str, int] = {}
        for pool_name, item_list in self.item_list.items():
            count_now = 0
            for item in item_list:
                if item.rank_type == '5':
                    gacha_data_five[pool_name].append(
                        FiveStarItem(
                            name=item.name,
                            icon=get_chara_icon(name=item.name) if item.item_type == '角色' else get_weapon_icon(
                                item.name),
                            count=count_now + 1,
                            type=item.item_type))
                    count_now = 0
                else:
                    count_now += 1
                    if item.rank_type == '4':
                        if item.name in gacha_data_four:
                            gacha_data_four[item.name].num[pool_name] += 1
                        else:
                            gacha_data_four[item.name] = FourStarItem(
                                name=item.name,
                                icon=get_chara_icon(name=item.name) if item.item_type == '角色' else get_weapon_icon(
                                    item.name),
                            type=item.item_type)
                            gacha_data_four[item.name].num[pool_name] = 1
            gacha_not_out[pool_name] = count_now
        return gacha_data_five, gacha_data_four, gacha_not_out
