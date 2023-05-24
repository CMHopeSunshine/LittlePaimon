import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel
from tortoise import fields
from tortoise.models import Model

from LittlePaimon.utils.typing import DataSourceType


class Player(BaseModel):
    """
    原神信息查询对象
    """
    user_id: str
    """查询对象的user_id"""
    uid: str
    """查询对象的原神uid"""


class PlayerBaseInfo(BaseModel):
    """
    玩家基础数据信息，比如神瞳数、宝箱数等
    """
    activate_days: Optional[int]
    """活跃天数"""
    achievements: Optional[int]
    """成就数"""
    abyss_floor: Optional[str]
    """深渊到达层数"""
    way_point: Optional[int]
    """传送点解锁数"""
    domain_num: Optional[int]
    """秘境解锁数"""
    anemoculus: Optional[int]
    """风神瞳收集数"""
    geoculus: Optional[int]
    """岩神瞳收集数"""
    electroculus: Optional[int]
    """雷神瞳收集数"""
    dendroculus: Optional[int]
    """草神瞳收集数"""
    character_num: Optional[int]
    """角色收集数数"""
    luxurious_chest: Optional[int]
    """华丽宝箱收集数"""
    precious_chest: Optional[int]
    """珍贵宝箱收集数"""
    exquisite_chest: Optional[int]
    """精致宝箱收集数"""
    common_chest: Optional[int]
    """普通宝箱收集数"""
    magic_chest: Optional[int]
    """奇馈宝箱收集数"""


class PlayerWorldInfo(BaseModel):
    """
    玩家世界探索数据，如探索度、声望等级等
    """
    name: str
    """地区名称"""
    unlock: bool
    """是否解锁"""
    percent: Optional[int]
    """探索度，100%以1000显示，注意转换"""
    level: Optional[int]
    """声望等级"""
    tree_level: Optional[int]
    """神樱树或忍冬之树等级"""
    stone_level: Optional[int]
    """流明石等级"""


class PlayerWorldInfos(BaseModel):
    MengDe: Optional[PlayerWorldInfo]
    """蒙德"""
    LiYue: Optional[PlayerWorldInfo]
    """璃月"""
    DaoQi: Optional[PlayerWorldInfo]
    """稻妻"""
    SnowMountain: Optional[PlayerWorldInfo]
    """龙脊雪山"""
    ChasmsMaw: Optional[PlayerWorldInfo]
    """层岩巨渊"""
    ChasmsMawBelow: Optional[PlayerWorldInfo]
    """层岩巨渊地下"""
    Enkanomiya: Optional[PlayerWorldInfo]
    """渊下宫"""
    Xumi: Optional[PlayerWorldInfo]
    """须弥"""

    def list(self):
        return [self.MengDe, self.LiYue, self.DaoQi, self.SnowMountain, self.ChasmsMaw, self.ChasmsMawBelow,
                self.Enkanomiya, self.Xumi]


class PlayerHomeInfo(BaseModel):
    """
    玩家尘歌壶数据
    """
    level: int
    """信任等阶"""
    visit_num: int
    """访客次数"""
    comfort_value: int
    """最高洞天仙力"""
    item_num: int
    """获得摆设数"""
    unlock: List[Literal['罗浮洞', '翠黛峰', '清琼岛', '绘绮庭', '妙香林']]
    """已解锁洞天列表"""


class PlayerInfo(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    user_id: str = fields.CharField(max_length=255)
    """玩家qid"""
    uid: str = fields.CharField(max_length=255)
    """原神uid"""
    nickname: str = fields.CharField(max_length=255, null=True)
    """玩家昵称"""
    level: int = fields.IntField(null=True)
    """玩家等级"""
    world_level: Optional[int] = fields.IntField(null=True)
    """世界等级"""
    signature: Optional[str] = fields.CharField(max_length=255, null=True)
    """个性签名"""
    profile_id: Optional[int] = fields.IntField(null=True)
    """头像id"""
    namecard_id: Optional[int] = fields.IntField(null=True)
    """名片id"""
    avatars: Optional[List[int]] = fields.JSONField(null=True)
    """展示角色列表"""
    namecards: Optional[List[int]] = fields.JSONField(null=True)
    """展示名片列表"""
    base_info: Optional[PlayerBaseInfo] = fields.JSONField(encoder=PlayerBaseInfo.json,
                                                           decoder=PlayerBaseInfo.parse_raw, null=True)
    """玩家基本信息，如宝箱、神瞳等"""
    world_explore: Optional[PlayerWorldInfos] = fields.JSONField(encoder=PlayerWorldInfos.json,
                                                                 decoder=PlayerWorldInfos.parse_raw, null=True)
    """世界探索数据"""
    home: Optional[PlayerHomeInfo] = fields.JSONField(encoder=PlayerHomeInfo.json, decoder=PlayerHomeInfo.parse_raw,
                                                      null=True)
    """尘歌壶数据"""
    update_time: datetime.datetime = fields.DatetimeField(null=True)
    """更新时间"""

    class Meta:
        table = 'player_info'
        table_description = '原神玩家信息表'

    @classmethod
    async def update_info(cls, user_id: str, uid: str, data: dict, data_source: DataSourceType):
        info, _ = await cls.get_or_create(user_id=user_id, uid=uid)
        if data_source == 'enka':
            info.nickname = data.get('nickname')
            info.level = data.get('level')
            info.world_level = data.get('worldLevel')
            info.signature = data.get('signature', '')
            info.profile_id = data.get('profilePicture', {}).get('avatarId')
            info.namecard_id = data.get('nameCardId')
            avatars = [a.get('avatarId') for a in data.get('showAvatarInfoList', {})]
            if info.avatars is None or len(info.avatars) < len(avatars):
                info.avatars = avatars
            info.namecards = data.get('showNameCardIdList')
            if info.base_info is None:
                info.base_info = PlayerBaseInfo()
            info.base_info.achievements = data.get('finishAchievementNum')
            info.base_info.abyss_floor = f'{data.get("towerFloorIndex")}-{data.get("towerLevelIndex")}'
        elif data_source == 'mihoyo':
            info.nickname = data['role']['nickname']
            info.level = data['role']['level']
            if not info.avatars:
                info.avatars = [c['id'] for c in data['avatars'][:8]]
            info.base_info = PlayerBaseInfo(
                activate_days=data['stats']['active_day_number'],
                achievements=data['stats']['achievement_number'],
                abyss_floor=data['stats']['spiral_abyss'],
                anemoculus=data['stats']['anemoculus_number'],
                geoculus=data['stats']['geoculus_number'],
                electroculus=data['stats']['electroculus_number'],
                dendroculus=data['stats']['dendroculus_number'],
                way_point=data['stats']['way_point_number'],
                domain_num=data['stats']['domain_number'],
                precious_chest=data['stats']['precious_chest_number'],
                luxurious_chest=data['stats']['luxurious_chest_number'],
                exquisite_chest=data['stats']['exquisite_chest_number'],
                common_chest=data['stats']['common_chest_number'],
                magic_chest=data['stats']['magic_chest_number'],
                character_num=data['stats']['avatar_number'])
            if 'homes' in data and data['homes']:
                info.home = PlayerHomeInfo(level=data['homes'][0]['level'],
                                           visit_num=data['homes'][0]['visit_num'],
                                           comfort_value=data['homes'][0]['comfort_num'],
                                           item_num=data['homes'][0]['item_num'],
                                           unlock=[h['name'] for h in data['homes']])
            else:
                info.home = PlayerHomeInfo(level=0,
                                           visit_num=0,
                                           comfort_value=0,
                                           item_num=0,
                                           unlock=[])
            info.world_explore = PlayerWorldInfos()
            if 'world_explorations' in data:
                info.world_explore = PlayerWorldInfos()
                if mengde_data := list(filter(lambda h: h['name'] == '蒙德', data['world_explorations'])):
                    mengde_data = mengde_data[0]
                    info.world_explore.MengDe = PlayerWorldInfo(name='蒙德', unlock=True, level=mengde_data['level'],
                                                                percent=mengde_data['exploration_percentage'])
                else:
                    info.world_explore.MengDe = PlayerWorldInfo(name='蒙德', unlock=False)
                if liyue_data := list(filter(lambda h: h['name'] == '璃月', data['world_explorations'])):
                    liyue_data = liyue_data[0]
                    info.world_explore.LiYue = PlayerWorldInfo(name='璃月', unlock=True, level=liyue_data['level'],
                                                               percent=liyue_data['exploration_percentage'])
                else:
                    info.world_explore.LiYue = PlayerWorldInfo(name='璃月', unlock=False)
                if snow_data := list(filter(lambda h: h['name'] == '龙脊雪山', data['world_explorations'])):
                    snow_data = snow_data[0]
                    info.world_explore.SnowMountain = PlayerWorldInfo(name='龙脊雪山', unlock=True,
                                                                      tree_level=snow_data['offerings'][0]['level'],
                                                                      percent=snow_data['exploration_percentage'])
                else:
                    info.world_explore.SnowMountain = PlayerWorldInfo(name='龙脊雪山', unlock=False)
                if daoqi_data := list(filter(lambda h: h['name'] == '稻妻', data['world_explorations'])):
                    daoqi_data = daoqi_data[0]
                    info.world_explore.DaoQi = PlayerWorldInfo(name='稻妻', unlock=True, level=daoqi_data['level'],
                                                               tree_level=daoqi_data['offerings'][0]['level'],
                                                               percent=daoqi_data['exploration_percentage'])
                else:
                    info.world_explore.DaoQi = PlayerWorldInfo(name='稻妻', unlock=False)
                if yxg_data := list(filter(lambda h: h['name'] == '渊下宫', data['world_explorations'])):
                    yxg_data = yxg_data[0]
                    info.world_explore.Enkanomiya = PlayerWorldInfo(name='渊下宫', unlock=True,
                                                                    percent=yxg_data['exploration_percentage'])
                else:
                    info.world_explore.Enkanomiya = PlayerWorldInfo(name='渊下宫', unlock=False)
                if cy_data := list(filter(lambda h: h['name'] == '层岩巨渊', data['world_explorations'])):
                    cy_data = cy_data[0]
                    info.world_explore.ChasmsMaw = PlayerWorldInfo(name='层岩巨渊', unlock=True,
                                                                   stone_level=cy_data['offerings'][0]['level'],
                                                                   percent=cy_data['exploration_percentage'])
                else:
                    info.world_explore.ChasmsMaw = PlayerWorldInfo(name='层岩巨渊', unlock=False)
                if cyx_data := list(filter(lambda h: h['name'] == '层岩巨渊·地下矿区', data['world_explorations'])):
                    cyx_data = cyx_data[0]
                    info.world_explore.ChasmsMawBelow = PlayerWorldInfo(name='层岩巨渊·地下矿区', unlock=True,
                                                                        percent=cyx_data['exploration_percentage'])
                else:
                    info.world_explore.ChasmsMawBelow = PlayerWorldInfo(name='层岩巨渊·地下矿区', unlock=False)
                if xm_data := list(filter(lambda h: h['name'] == '须弥', data['world_explorations'])):
                    xm_data = xm_data[0]
                    info.world_explore.Xumi = PlayerWorldInfo(name='须弥', unlock=True,
                                                              level=xm_data['level'],
                                                              percent=xm_data['exploration_percentage'],
                                                              tree_level=xm_data['offerings'][0]['level'])
                else:
                    info.world_explore.ChasmsMawBelow = PlayerWorldInfo(name='须弥', unlock=False)

        info.update_time = datetime.datetime.now()
        await info.save()


class PlayerAlias(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    user_id: str = fields.CharField(max_length=255)
    """玩家qid"""
    alias: str = fields.CharField(max_length=255)
    """别名"""
    character: str = fields.CharField(max_length=255)
    """实际角色"""
