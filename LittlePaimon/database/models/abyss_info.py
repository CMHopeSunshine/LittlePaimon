import datetime
from typing import Optional, List, Iterator, Dict, Union

from pydantic import BaseModel
from tortoise import fields
from tortoise.models import Model

from LittlePaimon.utils.alias import get_name_by_id
from LittlePaimon.utils.files import save_json
from .player_info import PlayerInfo


def timestamp_to_datetime(timestamp: Optional[Union[int, str]]) -> Optional[datetime.datetime]:
    if timestamp is None:
        return None
    if isinstance(timestamp, str):
        timestamp = int(timestamp)
    return datetime.datetime.fromtimestamp(timestamp)


class AbyssCharacter(BaseModel):
    name: str
    """角色名称"""
    character_id: int
    """角色id"""
    rarity: Optional[int]
    """稀有度"""
    level: Optional[int]
    """等级"""
    icon: Optional[str]
    """图标"""
    value: Optional[int]
    """数值"""


class AbyssCharacters(BaseModel):
    characters: List[AbyssCharacter] = []
    """角色列表"""

    def __len__(self):
        return len(self.characters)

    def __getitem__(self, item):
        return self.characters[item]

    def __setitem__(self, key, value):
        self.characters[key] = value

    def __delitem__(self, key):
        del self.characters[key]

    def __iter__(self) -> Iterator[AbyssCharacter]:
        return iter(self.characters)

    def __reversed__(self):
        return reversed(self.characters)

    def append(self, character: AbyssCharacter):
        self.characters.append(character)

    def pop(self, index=-1):
        self.characters.pop(index)


class FloorInfo(BaseModel):
    index: int
    """楼层数"""
    is_unlock: bool = True
    """是否已解锁"""
    stars: List[int]
    """星星数"""
    battles_up: Optional[List[AbyssCharacters]]
    """上半出战阵容"""
    battles_down: Optional[List[AbyssCharacters]]
    """下半出战阵容"""
    end_times_up: Optional[List[datetime.datetime]]
    """上半结束时间"""
    end_times_down: Optional[List[datetime.datetime]]
    """下半结束时间"""


class Floors(BaseModel):
    floors: Dict[int, Optional[FloorInfo]] = {}

    def __len__(self):
        return len(self.floors)

    def __getitem__(self, item) -> Optional[FloorInfo]:
        return self.floors[item]

    def __setitem__(self, key, value):
        self.floors[key] = value

    def __delitem__(self, key):
        del self.floors[key]

    def items(self):
        return self.floors.items()

    def keys(self):
        return self.floors.keys()

    def values(self):
        return self.floors.values()

    def get(self, index, default=None):
        return self.floors.get(index, default)


class AbyssInfo(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    user_id: str = fields.CharField(max_length=255)
    """用户id"""
    uid: str = fields.CharField(max_length=255)
    """原神uid"""
    nickname: str = fields.CharField(max_length=255, null=True)
    """玩家昵称"""
    start_time: datetime.datetime = fields.DatetimeField(null=True)
    """开始时间"""
    end_time: datetime.datetime = fields.DatetimeField(null=True)
    """结束时间"""
    total_battle: int = fields.IntField(null=True)
    """总战斗次数"""
    total_star: int = fields.IntField(null=True)
    """总星数"""
    max_floor: str = fields.CharField(max_length=255, null=True)
    """到达层数"""
    max_battle: AbyssCharacters = fields.JSONField(encoder=AbyssCharacters.json, decoder=AbyssCharacters.parse_raw,
                                                   null=True)
    """出战次数最多"""
    max_defeat: AbyssCharacter = fields.JSONField(encoder=AbyssCharacter.json, decoder=AbyssCharacter.parse_raw,
                                                  null=True)
    """击败最多"""
    max_damage: AbyssCharacter = fields.JSONField(encoder=AbyssCharacter.json, decoder=AbyssCharacter.parse_raw,
                                                  null=True)
    """伤害最高"""
    max_take_damage: AbyssCharacter = fields.JSONField(encoder=AbyssCharacter.json, decoder=AbyssCharacter.parse_raw,
                                                       null=True)
    """承受伤害最高"""
    max_normal_skill: AbyssCharacter = fields.JSONField(encoder=AbyssCharacter.json, decoder=AbyssCharacter.parse_raw,
                                                        null=True)
    """元素战技释放最多"""
    max_energy_skill: AbyssCharacter = fields.JSONField(encoder=AbyssCharacter.json, decoder=AbyssCharacter.parse_raw,
                                                        null=True)
    """元素爆发释放最多"""
    floors: Floors = fields.JSONField(encoder=Floors.json, decoder=Floors.parse_raw, default=Floors())
    """楼层具体信息"""
    update_time: datetime.datetime = fields.DatetimeField(null=True)
    """更新时间"""

    class Meta:
        table = 'abyss_info'
        table_description = '原神玩家深渊信息表'

    @classmethod
    async def update_info(cls, user_id: str, uid: str, data: dict):
        await cls.filter(user_id=user_id, uid=uid).delete()
        info, _ = await cls.get_or_create(user_id=user_id, uid=uid)
        if player_info := await PlayerInfo.get_or_none(user_id=user_id, uid=uid):
            info.nickname = player_info.nickname
        else:
            info.nickname = None
        info.start_time = timestamp_to_datetime(data.get('start_time'))
        info.end_time = timestamp_to_datetime(data.get('end_time'))
        info.total_battle = data.get('total_battle_times')
        info.total_star = data.get('total_win_times') * 3
        info.max_floor = data.get('max_floor')
        if 'reveal_rank' in data and data['reveal_rank']:
            info.max_battle = AbyssCharacters(characters=[
                AbyssCharacter(name=get_name_by_id(c['avatar_id']),
                               character_id=c['avatar_id'],
                               icon=c['avatar_icon'].split('/')[-1].replace('.png', ''),
                               rarity=c['rarity'],
                               value=c['value']) for c in data['reveal_rank']
            ])
        if 'defeat_rank' in data and data['defeat_rank']:
            info.max_defeat = AbyssCharacter(name=get_name_by_id(data['defeat_rank'][0]['avatar_id']),
                                             character_id=data['defeat_rank'][0]['avatar_id'],
                                             icon=data['defeat_rank'][0]['avatar_icon'].split('/')[-1].replace('.png',
                                                                                                               '').replace(
                                                 'Side_', ''),
                                             rarity=data['defeat_rank'][0]['rarity'],
                                             value=data['defeat_rank'][0]['value'])
        if 'damage_rank' in data and data['damage_rank']:
            info.max_damage = AbyssCharacter(name=get_name_by_id(data['damage_rank'][0]['avatar_id']),
                                             character_id=data['damage_rank'][0]['avatar_id'],
                                             icon=data['damage_rank'][0]['avatar_icon'].split('/')[-1].replace('.png',
                                                                                                               '').replace(
                                                 'Side_', ''),
                                             rarity=data['damage_rank'][0]['rarity'],
                                             value=data['damage_rank'][0]['value'])
        if 'take_damage_rank' in data and data['take_damage_rank']:
            info.max_take_damage = AbyssCharacter(name=get_name_by_id(data['take_damage_rank'][0]['avatar_id']),
                                                  character_id=data['take_damage_rank'][0]['avatar_id'],
                                                  icon=data['take_damage_rank'][0]['avatar_icon'].split('/')[
                                                      -1].replace(
                                                      '.png', '').replace('Side_', ''),
                                                  rarity=data['take_damage_rank'][0]['rarity'],
                                                  value=data['take_damage_rank'][0]['value'])
        if 'normal_skill_rank' in data and data['normal_skill_rank']:
            info.max_normal_skill = AbyssCharacter(name=get_name_by_id(data['normal_skill_rank'][0]['avatar_id']),
                                                   character_id=data['normal_skill_rank'][0]['avatar_id'],
                                                   icon=data['normal_skill_rank'][0]['avatar_icon'].split('/')[
                                                       -1].replace(
                                                       '.png', '').replace('Side_', ''),
                                                   rarity=data['normal_skill_rank'][0]['rarity'],
                                                   value=data['normal_skill_rank'][0]['value'])
        if 'energy_skill_rank' in data and data['energy_skill_rank']:
            info.max_energy_skill = AbyssCharacter(name=get_name_by_id(data['energy_skill_rank'][0]['avatar_id']),
                                                   character_id=data['energy_skill_rank'][0]['avatar_id'],
                                                   icon=data['energy_skill_rank'][0]['avatar_icon'].split('/')[
                                                       -1].replace(
                                                       '.png', '').replace('Side_', ''),
                                                   rarity=data['energy_skill_rank'][0]['rarity'],
                                                   value=data['energy_skill_rank'][0]['value'])
        if 'floors' in data and data['floors']:
            info.total_star = 0
            for floor in data['floors']:
                floor_info = FloorInfo(index=floor['index'],
                                       is_unlock=floor['is_unlock'],
                                       stars=[l['star'] for l in floor['levels']])
                battles_up = []
                battles_down = []
                end_times_up = []
                end_times_down = []
                for level in floor['levels']:
                    if not level['battles']:
                        break
                    end_times_up.append(timestamp_to_datetime(level['battles'][0]['timestamp']))
                    end_times_down.append(timestamp_to_datetime(level['battles'][1]['timestamp']))
                    battles_up.append(AbyssCharacters(characters=[AbyssCharacter(
                        name=get_name_by_id(c['id']),
                        character_id=c['id'],
                        icon=c['icon'].split('/')[-1].replace('.png', ''),
                        rarity=c['rarity'],
                        level=c['level']) for c in level['battles'][0]['avatars']]))
                    battles_down.append(AbyssCharacters(characters=[AbyssCharacter(
                        name=get_name_by_id(c['id']),
                        character_id=c['id'],
                        icon=c['icon'].split('/')[-1].replace('.png', ''),
                        rarity=c['rarity'],
                        level=c['level']) for c in level['battles'][1]['avatars']]))
                floor_info.battles_up = battles_up
                floor_info.battles_down = battles_down
                floor_info.end_times_up = end_times_up
                floor_info.end_times_down = end_times_down
                info.floors[floor['index']] = floor_info
                if floor['index'] in [9, 10, 11, 12]:
                    info.total_star += sum(int(l['star']) for l in floor['levels'])

        info.update_time = datetime.datetime.now()
        await info.save()
