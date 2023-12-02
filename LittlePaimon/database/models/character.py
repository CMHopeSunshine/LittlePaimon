import datetime
import re
from typing import Optional, Dict, Iterator

from tortoise import fields
from tortoise.models import Model

from LittlePaimon.utils.path import JSON_DATA
from LittlePaimon.utils.alias import get_name_by_id, get_weapon_icon, get_artifact_icon, get_constellation_icon
from LittlePaimon.utils.files import load_json
from LittlePaimon.utils.typing import *

# 加载map数据
role_skill_map = load_json(JSON_DATA / 'role_skill.json')
role_talent_map = load_json(JSON_DATA / 'role_talent.json')
role_datas_map = load_json(JSON_DATA / 'roles_data.json')
weapon_map = load_json(JSON_DATA / 'weapon.json')
prop_list_map = load_json(JSON_DATA / 'prop.json')
artifact_map = load_json(JSON_DATA / 'artifact.json')
score_talent_map = load_json(JSON_DATA / 'score.json')
enka_icon_map = load_json(JSON_DATA / 'genshin_info.json')
reaction_coefficient = {
    '蒸发': 0,
    '融化': 0,
    '超载': 0,
    '燃烧': 0,
    '冻结': 0,
    '感电': 0,
    '绽放': 0,
    '超导': 0,
    '激化': 0,
    '扩散': 0,
    '结晶': 0
}


class EquipProperty(BaseModel):
    """
    装备属性类
    """
    name: str
    """属性名"""
    value: float
    """属性值"""


class CharacterProperty(BaseModel):
    """
    角色面板数据
    """
    base_health: int
    """基础生命值"""
    extra_health: int
    """额外生命值"""
    base_attack: int
    """基础攻击力"""
    extra_attack: int
    """额外攻击力"""
    base_defense: int
    """基础防御力"""
    extra_defense: int
    """额外防御力"""
    crit_rate: float
    """暴击率"""
    crit_damage: float
    """暴击伤害"""
    elemental_mastery: int
    """元素精通"""
    elemental_efficiency: float
    """元素充能效率"""
    healing_bonus: float
    """治疗加成"""
    incoming_healing_bonus: float
    """受治疗加成"""
    shield_strength: float = 0
    """护盾强效"""
    dmg_bonus: Dict[Literal['火', '水', '冰', '雷', '风', '岩', '草', '物理'], float]
    """物理和元素伤害加成"""
    reaction_coefficient: Optional[
        Dict[Literal['蒸发', '融化', '超载', '燃烧', '冻结', '感电', '绽放', '超导', '激化', '扩散', '结晶'], float]]
    """反应加成系数"""

    @property
    def health(self) -> int:
        """总生命值"""
        return self.base_health + self.extra_health

    @property
    def attack(self) -> int:
        """总攻击力"""
        return self.base_attack + self.extra_attack

    @property
    def defense(self) -> int:
        """总防御力"""
        return self.base_defense + self.extra_defense


class Weapon(BaseModel):
    """武器数据"""
    name: str
    """武器名称"""
    type: Literal['单手剑', '双手剑', '长柄武器', '弓', '法器']
    """武器类型"""
    level: int
    """武器等级"""
    rarity: Optional[int]
    """武器星级"""
    promote_level: Optional[int]
    """突破等级"""
    affix_level: Optional[int]
    """精炼等级"""
    icon: Optional[str]
    """武器图标"""
    base_attack: Optional[int]
    """基础攻击力"""
    extra_prop: Optional[EquipProperty]
    """额外属性"""


class Artifact(BaseModel):
    """圣遗物数据"""
    name: str
    """圣遗物名称"""
    level: int
    """圣遗物等级"""
    rarity: int
    """圣遗物星级"""
    part: Optional[str]
    """部位"""
    suit: Optional[str]
    """所属套装"""
    icon: str
    """图标"""
    main_property: Optional[EquipProperty]
    """主属性"""
    prop_list: Optional[List[EquipProperty]]
    """副词条"""


class Artifacts(BaseModel):
    """圣遗物列表数据"""
    artifact_list: List[Artifact] = []
    """圣遗物列表"""

    def __len__(self):
        return len(self.artifact_list)

    def __getitem__(self, item):
        return self.artifact_list[item]

    def __setitem__(self, key, value):
        self.artifact_list[key] = value

    def __delitem__(self, key):
        del self.artifact_list[key]

    def __iter__(self) -> Iterator[Artifact]:
        return iter(self.artifact_list)

    def __reversed__(self):
        return reversed(self.artifact_list)

    def append(self, artifact: Artifact):
        self.artifact_list.append(artifact)

    def index(self, artifact: Artifact) -> int:
        return self.artifact_list.index(artifact)


class Constellation(BaseModel):
    """命座数据"""
    name: str
    """命座名"""
    icon: str
    """命座图标"""


class Constellations(BaseModel):
    """命座列表数据"""
    constellation_list: List[Constellation] = []
    """命座列表"""

    def __len__(self):
        return len(self.constellation_list)

    def __getitem__(self, item):
        return self.constellation_list[item]

    def __setitem__(self, key, value):
        self.constellation_list[key] = value

    def __delitem__(self, key):
        del self.constellation_list[key]

    def __iter__(self) -> Iterator[Constellation]:
        return iter(self.constellation_list)

    def __reversed__(self):
        return reversed(self.constellation_list)

    def append(self, constellation: Constellation):
        self.constellation_list.append(constellation)


class Talent(BaseModel):
    """天赋数据"""
    name: str
    """天赋名称"""
    level: int
    """天赋等级"""
    icon: str
    """天赋图标"""


class Talents(BaseModel):
    """天赋列表数据"""
    talent_list: List[Talent] = []
    """天赋列表"""

    def __len__(self):
        return len(self.talent_list)

    def __getitem__(self, item):
        return self.talent_list[item]

    def __setitem__(self, key, value):
        self.talent_list[key] = value

    def __delitem__(self, key):
        del self.talent_list[key]

    def __iter__(self) -> Iterator[Talent]:
        return iter(self.talent_list)

    def __reversed__(self):
        return reversed(self.talent_list)

    def append(self, talent: Talent):
        self.talent_list.append(talent)

    def pop(self, index=-1):
        self.talent_list.pop(index)


class Character(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    user_id: str = fields.CharField(max_length=255)
    """用户id"""
    uid: str = fields.CharField(max_length=255)
    """原神uid"""
    name: str = fields.CharField(max_length=255)
    """角色名"""
    character_id: int = fields.IntField(null=True)
    """角色id"""
    level: int = fields.IntField(null=True)
    """等级"""
    rarity: int = fields.IntField(null=True)
    """星级"""
    promote_level: int = fields.IntField(null=True)
    """突破等级"""
    fetter: int = fields.IntField(null=True)
    """好感等级"""
    element: ElementType = fields.CharField(max_length=2, null=True)
    """元素"""
    region: RegionType = fields.CharField(max_length=2, null=True)
    """所属地区"""
    talents: Optional[Talents] = fields.JSONField(encoder=Talents.json, decoder=Talents.parse_raw, null=True)
    """天赋"""
    constellation: Optional[Constellations] = fields.JSONField(encoder=Constellations.json,
                                                               decoder=Constellations.parse_raw, null=True)
    """命之座"""
    weapon: Optional[Weapon] = fields.JSONField(encoder=Weapon.json, decoder=Weapon.parse_raw, null=True)
    """武器"""
    artifacts: Optional[Artifacts] = fields.JSONField(encoder=Artifacts.json, decoder=Artifacts.parse_raw, null=True)
    """圣遗物"""
    prop: Optional[CharacterProperty] = fields.JSONField(encoder=CharacterProperty.json,
                                                         decoder=CharacterProperty.parse_raw, null=True)
    """属性"""
    data_source: DataSourceType = fields.CharField(max_length=6, null=True)
    """数据来源"""
    update_time: datetime.datetime = fields.DatetimeField(default=datetime.datetime.now)

    class Meta:
        table = 'character'
        table_description = '原神玩家角色信息表'

    def __repr__(self):
        return f'<{self.name}-LV.{self.level}>'

    def __str__(self):
        return self.__repr__()

    @classmethod
    async def update_info(cls, user_id: str, uid: str, data: dict, data_source: DataSourceType):
        """
        更新角色信息
        :param user_id: 用户id
        :param uid: 原神uid
        :param data: 数据
        :param data_source: 数据来源(mihoyo/enka)
        """
        if data_source == 'enka':
            name = get_name_by_id(str(data['avatarId']))
            character, _ = await cls.get_or_create(user_id=user_id, uid=uid, name=name, data_source=data_source)
            character.character_id = data['avatarId']
            character.level = int(data['propMap']['4001']['val'])
            character.fetter = data['fetterInfo']['expLevel']
            character.promote_level = int(data['propMap']['1002'].get('val', 0))
            if name in ['荧', '空']:
                character.region = '未知'
                character.rarity = 5
                traveler_skill = role_skill_map['Name'][list(data['skillLevelMap'].keys())[-1]]
                find_element = re.search(r'[风雷岩草流火冰]', traveler_skill).group()
                character.element = find_element if find_element != "流" else "水"
                role_name = character.element + '主'
            else:
                character.region = role_datas_map[name]['region']
                character.rarity = role_datas_map[name]['star']
                role_name = character.name
                character.element = role_datas_map[name]['element']

            if 'talentIdList' in data:
                if len(data['talentIdList']) >= 3:
                    data['skillLevelMap'][
                        list(data['skillLevelMap'].keys())[score_talent_map['Talent'][role_name][0]]] += 3
                if len(data['talentIdList']) >= 5:
                    data['skillLevelMap'][
                        list(data['skillLevelMap'].keys())[score_talent_map['Talent'][role_name][1]]] += 3

            character.talents = Talents(talent_list=[Talent(name=role_skill_map['Name'][talent],
                                                            level=data['skillLevelMap'][talent],
                                                            icon=role_skill_map['Icon'][talent]) for talent in
                                                     data['skillLevelMap']])
            if character.name == '神里绫华':
                character.talents[0], character.talents[-1] = character.talents[-1], character.talents[0]
                character.talents[2], character.talents[-1] = character.talents[-1], character.talents[2]
            if character.name == '安柏':
                character.talents[0], character.talents[-1] = character.talents[-1], character.talents[0]
            if character.name in ['空', '荧']:
                character.talents[0], character.talents[-1] = character.talents[-1], character.talents[0]
                character.talents[1], character.talents[-1] = character.talents[-1], character.talents[1]
            if character.name == '达达利亚':
                character.talents[0].level += 1

            if 'talentIdList' in data and data['talentIdList']:
                character.constellation = Constellations(
                    constellation_list=[Constellation(name=role_talent_map['Name'][str(con)],
                                                      icon=role_talent_map['Icon'][str(con)])
                                        for con in data['talentIdList']])
            else:
                character.constellation = Constellations(constellation_list=[])

            character.prop = CharacterProperty(
                base_health=round(data['fightPropMap']['1']),
                extra_health=round(data['fightPropMap']['2000'] - round(data['fightPropMap']['1'])),
                base_attack=round(data['fightPropMap']['4']),
                extra_attack=round(data['fightPropMap']['2001'] - round(data['fightPropMap']['4'])),
                base_defense=round(data['fightPropMap']['7']),
                extra_defense=round(data['fightPropMap']['2002'] - round(data['fightPropMap']['7'])),
                crit_rate=round(data['fightPropMap']['20'], 3),
                crit_damage=round(data['fightPropMap']['22'], 3),
                elemental_mastery=round(data['fightPropMap']['28']),
                elemental_efficiency=round(data['fightPropMap']['23'], 3),
                healing_bonus=round(data['fightPropMap']['26'], 3),
                incoming_healing_bonus=round(data['fightPropMap']['27'], 3),
                shield_strength=0,
                dmg_bonus={
                    '物理': round(data['fightPropMap']['30'], 3),
                    '火':  round(data['fightPropMap']['40'], 3),
                    '雷':  round(data['fightPropMap']['41'], 3),
                    '水':  round(data['fightPropMap']['42'], 3),
                    '草':  round(data['fightPropMap']['43'], 3),
                    '风':  round(data['fightPropMap']['44'], 3),
                    '岩':  round(data['fightPropMap']['45'], 3),
                    '冰':  round(data['fightPropMap']['46'], 3),
                },
                reaction_coefficient=reaction_coefficient)
            weapon_c = data['equipList'][-1]
            try:
                extra_prop = EquipProperty(name=prop_list_map[weapon_c['flat']['weaponStats'][1]['appendPropId']],
                                           value=weapon_c['flat']['weaponStats'][1]['statValue'])
            except IndexError:
                extra_prop = None
            character.weapon = Weapon(
                name=(weapon_name := weapon_map['Name'][str(weapon_c['flat']['nameTextMapHash'])]),
                type=weapon_map['Type'][weapon_name],
                level=weapon_c['weapon']['level'],
                rarity=weapon_c['flat']['rankLevel'],
                promote_level=weapon_c['weapon']['promoteLevel'] if 'promoteLevel' in weapon_c['weapon'] else 0,
                affix_level=list(weapon_c['weapon']['affixMap'].values())[0] + 1 if 'affixMap' in weapon_c[
                    'weapon'] else 1,
                icon=weapon_c['flat']['icon'],
                base_attack=weapon_c['flat']['weaponStats'][0]['statValue'],
                extra_prop=extra_prop)

            character.artifacts = Artifacts()
            for artifact in data['equipList'][:-1]:
                if 'reliquarySubstats' in artifact['flat']:
                    prop_list = [EquipProperty(name=prop_list_map[reliquary['appendPropId']],
                                               value=reliquary['statValue']) for reliquary in
                                 artifact['flat']['reliquarySubstats']]
                else:
                    prop_list = []
                character.artifacts.append(Artifact(
                    name=artifact_map['Name'][artifact['flat']['icon']],
                    level=artifact['reliquary']['level'] - 1,
                    rarity=artifact['flat']['rankLevel'],
                    part=artifact_map['Piece'][artifact['flat']['icon'].split('_')[-1]][1],
                    suit=artifact_map['Mapping'][artifact_map['Name'][artifact['flat']['icon']]],
                    icon=artifact['flat']['icon'],
                    main_property=EquipProperty(
                        name=prop_list_map[artifact['flat']['reliquaryMainstat']['mainPropId']],
                        value=artifact['flat']['reliquaryMainstat']['statValue']),
                    prop_list=prop_list
                ))

            character.update_time = datetime.datetime.now()
            await character.save()
        else:
            if data['id'] == 10000007:
                data['name'] = '荧'
            elif data['id'] == 10000005:
                data['name'] = '空'
            character, _ = await cls.get_or_create(user_id=user_id, uid=uid, name=data['name'], data_source=data_source)
            character.character_id = data['id']
            character.level = data['level']
            character.rarity = data['rarity'] if data['rarity'] != 105 else 5
            character.promote_level = 0 if character.level < 20 else 1 if character.level < 40 else 2 if character.level < 50 else 3 if character.level < 60 else 4 if character.level < 70 else 5 if character.level < 80 else 6
            character.constellation = Constellations(constellation_list=[
                Constellation(name=data['constellations'][i]['name'],
                              icon=get_constellation_icon(data['constellations'][i]['name'])) for i in
                range(data['actived_constellation_num'])
            ])
            if character.name in ['荧', '空']:
                character.fetter = 10
                character.element = '岩' if data['element'] == 'Geo' else '风' if data['element'] == 'Anemo' else '草' if data['element'] == 'Dendro' else '雷'
                role_name = character.element + '主'
                character.region = '其它'
            else:
                character.fetter = data['fetter']
                character.element = role_datas_map[character.name]['element']
                character.region = role_datas_map[character.name]['region']
                role_name = character.name
            if 'skill_list' in data:
                if len(data['talentIdList']) >= 3:
                    data['skill_list'][score_talent_map['Talent'][role_name][0]]['level_current'] += 3
                if len(data['talentIdList']) >= 5:
                    data['skill_list'][score_talent_map['Talent'][role_name][1]]['level_current'] += 3
                talents_list = data['skill_list']
                if character.name == '达达利亚':
                    talents_list[0]['level_current'] += 1
                character.talents = Talents(talent_list=[Talent(name=t['name'],
                                                                level=t['level_current'],
                                                                icon=enka_icon_map['Skills'][
                                                                    enka_icon_map['SkillOrder'][talents_list.index(t)]])
                                                         for t
                                                         in talents_list])
            if 'weapon' in data:
                character.weapon = Weapon(
                    name=data['weapon']['name'],
                    type=data['weapon']['type_name'],
                    icon=get_weapon_icon(data['weapon']['name']),
                    level=data['weapon']['level'],
                    rarity=data['weapon']['rarity'],
                    affix_level=data['weapon']['affix_level'],
                    promote_level=data['weapon']['promote_level'])
            if 'reliquaries' in data:
                character.artifacts = Artifacts(artifact_list=[Artifact(
                    name=a['name'],
                    icon=get_artifact_icon(a['name']),
                    level=a['level'],
                    rarity=a['rarity'],
                    suit=a['set']['name'],
                    part=a['pos_name']) for a in data['reliquaries']])
            character.update_time = datetime.datetime.now()
            await character.save()

    @classmethod
    async def get_character(cls, user_id: str, uid: str, name: Optional[str] = None, character_id: Optional[int] = None,
                            data_source: Optional[DataSourceType] = None) -> 'Character':
        """
        根据角色名或角色id（二选一）获取角色信息
        :param user_id: 角色所属用户id
        :param uid: 角色所属uid
        :param name: 角色名
        :param character_id: 角色id
        :param data_source: 数据来源(mihoyo/enka)
        :return: 角色信息
        """
        query = {'user_id': user_id, 'uid': uid}
        if name:
            query['name'] = name
        elif character_id:
            query['character_id'] = character_id
        else:
            query['name'] = '香菱'
        query['data_source'] = data_source or 'enka'
        return await cls.get_or_none(**query)
