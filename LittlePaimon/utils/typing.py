import re
from typing import Literal, List

from pydantic import BaseModel, parse_raw_as

try:
    import ujson as json
except ImportError:
    import json

from . import DRIVER

command_start = list(DRIVER.config.command_start)
command_start_new = [re.escape(c) for c in command_start if c != '']
COMMAND_START_RE = (
    '^(' + '|'.join(command_start_new) + ')' if command_start_new else '^'
)
if command_start_new and '' in command_start:
    COMMAND_START_RE += '?'

ElementType = Literal['火', '水', '冰', '雷', '风', '岩', '草', '物理']
WeaponType = Literal['单手剑', '双手剑', '长柄武器', '弓', '法器']
DataSourceType = Literal['mihoyo', 'enka']
RegionType = Literal['蒙德', '璃月', '稻妻', '须弥', '枫丹', '纳塔', '至冬', '其它']
TalentType = Literal['name', 'level', 'icon']
ConstellationType = Literal['name', 'icon']
EquipType = Literal['name', 'value']
PropType = Literal[
    '基础生命', '额外生命', '基础攻击', '额外攻击', '基础防御', '额外防御', '暴击率', '暴击伤害', '元素精通', '元素充能效率', '治疗加成', '受治疗加成', '护盾强效', '伤害加成']

CN_NUMBER = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二']

CHARACTERS = ['神里绫华', '琴', '丽莎', '芭芭拉', '凯亚', '迪卢克', '雷泽', '安柏', '温迪', '香菱', '北斗', '行秋',
              '魈', '凝光', '可莉', '钟离',
              '菲谢尔', '班尼特', '达达利亚', '诺艾尔', '七七', '重云', '甘雨', '阿贝多', '迪奥娜', '莫娜', '刻晴',
              '砂糖', '辛焱', '罗莎莉亚', '胡桃',
              '枫原万叶', '烟绯', '宵宫', '托马', '优菈', '雷电将军', '早柚', '珊瑚宫心海', '五郎', '九条裟罗',
              '荒泷一斗', '八重神子', '夜兰', '埃洛伊',
              '申鹤', '云堇', '久岐忍', '神里绫人', '鹿野院平藏', '提纳里', '柯莱', '多莉', '赛诺', '坎蒂丝', '妮露',
              '纳西妲', '莱依拉', '流浪者', '珐露珊', '艾尔海森', '瑶瑶', '迪希雅', '米卡', '白术', '卡维', '绮良良', '琳妮特', '林尼', '菲米尼', '莱欧斯利', '那维莱特', '夏洛蒂', '芙宁娜', '夏沃蕾', '娜维娅', '嘉明', '闲云', '千织']
"""全角色"""
MALE_CHARACTERS = ['凯亚', '迪卢克', '钟离', '达达利亚', '托马', '荒泷一斗', '神里绫人', '艾尔海森', '白术', '卡维', '莱欧斯利', '那维莱特']
"""成男角色"""
FEMALE_CHARACTERS = ['琴', '丽莎', '北斗', '凝光', '罗莎莉亚', '优菈', '雷电将军', '九条裟罗', '八重神子', '夜兰',
                     '申鹤', '坎蒂丝', '迪希雅', '闲云']
"""成女角色"""
GIRL_CHARACTERS = ['神里绫华', '芭芭拉', '安柏', '香菱', '菲谢尔', '诺艾尔', '甘雨', '莫娜', '刻晴', '砂糖', '辛焱',
                   '胡桃', '烟绯', '宵宫', '珊瑚宫心海', '埃洛伊', '云堇', '久岐忍', '柯莱', '妮露', '莱依拉', '珐露珊', '绮良良', '琳妮特', '夏洛蒂', '芙宁娜', '夏沃蕾', '娜维娅', '千织']
"""少女角色"""
BOY_CHARACTERS = ['雷泽', '温迪', '行秋', '魈', '班尼特', '重云', '阿贝多', '枫原万叶', '五郎', '鹿野院平藏', '提纳里',
                  '赛诺', '流浪者', '米卡', '林尼', '菲米尼', '嘉明']
"""少男角色"""
LOLI_CHARACTERS = ['七七', '可莉', '迪奥娜', '早柚', '多莉', '纳西妲', '瑶瑶']
"""萝莉"""

CHARA_RE = '|'.join(CHARACTERS)


class PydanticListModel(BaseModel):
    @classmethod
    def encoder(cls, models: List['PydanticListModel']):
        return json.dumps(models, default=cls.dict)

    @classmethod
    def decoder(cls, json_data: str):
        return parse_raw_as(List[cls], json_data)
