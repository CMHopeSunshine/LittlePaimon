from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class Avatar(BaseModel):
    id: str
    name: str
    icon: str


class ChallengeData(BaseModel):
    maze_group_id: int
    maze_group_index: int
    pre_maze_group_index: int

class SpaceInfo(BaseModel):
    challenge_data: ChallengeData
    pass_area_progress: int
    light_cone_count: int
    avatar_count: int
    achievement_count: int


class Player(BaseModel):
    uid: str
    nickname: str
    level: int
    world_level: int
    friend_count: int
    avatar: Avatar
    signature: str
    is_display: bool
    space_info: SpaceInfo


class Element(BaseModel):
    id: str
    name: str
    color: str
    icon: str

class Path(BaseModel):
    id: str
    name: str
    icon: str

class SkillType(str, Enum):
    Normal = "Normal"
    """普攻"""
    BPSkill = "BPSkill"
    """战技"""
    Ultra = "Ultra"
    """终结技"""
    Talent = "Talent"
    """天赋"""
    MazeNormal = "MazeNormal"
    """dev_连携"""
    Maze = "Maze"
    """秘技"""


class Skill(BaseModel):
    id: str
    name: str
    level: int
    max_level: int
    element: Optional[Element]
    type: SkillType
    type_text: str
    effect: str
    simple_desc: str
    desc: str
    icon: str


class SkillTree(BaseModel):
    id: str
    level: int
    icon: str


class Attribute(BaseModel):
    field: str
    name: str
    icon: str
    value: float
    display: str
    percent: bool

class Property(BaseModel):
    type: str
    field: str
    name: str
    icon: str
    value: float
    display: str
    percent: bool


class LightCone(BaseModel):
    id: str
    name: str
    rarity: int
    rank: int
    level: int
    promotion: int
    icon: str
    preview: str
    portrait: str
    path: Path
    attributes: List[Attribute]
    properties: List[Property]


class RelicAffix(BaseModel):
    type: str
    field: str
    name: str
    icon: str
    value: float
    display: str
    percent: bool


class Relic(BaseModel):
    id: str
    name: str
    set_id: str
    set_name: str
    rarity: int
    level: int
    icon: str
    main_affix: RelicAffix
    sub_affix: List[RelicAffix]


class RelicSet(BaseModel):
    id: str
    name: str
    icon: str
    num: int
    desc: str
    properties: List[Property]


class Character(BaseModel):
    id: str
    name: str
    rarity: int
    rank: int
    level: int
    promotion: int
    icon: str
    preview: str
    portrait: str
    rank_icons: List[str]
    path: Path
    element: Element
    skills: List[Skill]
    skill_trees: List[SkillTree]
    light_cone: LightCone
    relics: List[Relic]
    relic_sets: List[RelicSet]
    attributes: List[Attribute]
    additions: List[Attribute]
    properties: List[Property]


class StarRailInfo(BaseModel):
    player: Player
    characters: List[Character]


# class SubAffix(BaseModel):
#     affix_id: int = Field(alias="affixId")
#     cnt: int
#     step: Optional[int]


# class Relic(BaseModel):
#     exp: Optional[int]
#     type: int
#     tid: int
#     sub_affix_list: List[SubAffix] = Field(alias="subAffixList")
#     level: int
#     main_affix_id: int = Field(alias="mainAffixId")


# class SkillTree(BaseModel):
#     point_id: int
#     level: int


# class Equipment(BaseModel):
#     level: int
#     tid: int
#     promotion: int
#     rank: int


# class AvatarDetail(BaseModel):
#     pos: Optional[int]
#     avatar_id: int = Field(alias="avatarId")
#     promotion: int
#     skill_tree_list: List[SkillTree] = Field(alias="skillTreeList")
#     relic_list: List = Field(alias="relicList")
#     equipment: Equipment
#     rank: Optional[int]
#     level: int



# class ChallengeInfo(BaseModel):
#     schedule_max_level: int = Field(alias="scheduleMaxLevel")
#     schedule_group_id: int = Field(alias="scheduleGroupId")
#     none_schedule_max_level: int = Field(alias="noneScheduleMaxLevel")


# class RecordInfo(BaseModel):
#     achievement_count: int = Field(alias="achievementCount")
#     challenge_info: ChallengeInfo = Field(alias="challengeInfo")
#     equipment_count: int = Field(alias="equipmentCount")
#     max_rogue_challenge_score: int = Field(alias="maxRogueChallengeScore")
#     avatar_count: int = Field(alias="avatarCount")


# class StarRailInfo(BaseModel):
#     world_level: int = Field(alias="worldLevel")
#     platform: str
#     friend_count: int = Field(alias="friendCount")
#     signature: str
#     is_display_list: bool = Field(alias="isDisplayList")
#     avatar_detail_list: List[AvatarDetail] = Field(alias="avatarDetailList")
#     record_info: RecordInfo = Field(alias="recordInfo")
#     head_icon: int = Field(alias="headIcon")
#     nickname: str
#     assist_avatar_detail: AvatarDetail = Field(alias="assistAvatarDetail")
#     level: int
#     uid: int