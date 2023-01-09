import asyncio
import datetime
from typing import Optional, List, Union, Tuple

import pytz

from LittlePaimon.config import config
from LittlePaimon.database import Artifact, CharacterProperty, Artifacts, Talents, Talent
from LittlePaimon.database import PlayerInfo, Character, LastQuery, PrivateCookie, AbyssInfo
from .alias import get_name_by_id
from .api import get_enka_data, get_mihoyo_public_data, get_mihoyo_private_data
from .files import load_json
from .logger import logger
from .path import JSON_DATA
from .typing import CHARACTERS
from .typing import DataSourceType

ra_score = load_json(JSON_DATA / 'score.json')
talent_map = load_json(JSON_DATA / 'role_skill.json')


class GenshinInfoManager:
    """
    原神信息管理器
    """

    def __init__(self, user_id: str, uid: str):
        self.user_id = user_id
        self.uid = uid

    async def is_bind(self) -> bool:
        """
        检查是否已绑定私人cookie
            :return: bool
        """
        return await PrivateCookie.filter(user_id=self.user_id, uid=self.uid).exists()

    async def update_all(self, include_talent: bool = False) -> str:
        """
        更新所有原神信息
        """
        result = ''
        await LastQuery.update_last_query(self.user_id, self.uid)
        mihoyo_result = await self.update_from_mihoyo()
        result += f'米游社数据：{mihoyo_result}\n'

        if include_talent:
            if await self.is_bind():
                talent_result = await self.update_talent()
                result += f'天赋数据：{talent_result}\n'
            else:
                result += '天赋数据：未绑定私人Cookie\n'

        enka_result = await self.update_from_enka()
        result += f'Enka数据：{enka_result}'
        return result or enka_result

    async def update_from_enka(self) -> str:
        """
        从enka.network更新原神数据
            :return: 更新结果
        """
        data = await get_enka_data(self.uid)
        if not data:
            logger.info('原神信息', f'无法获取到<m>{self.uid}</m>的数据，可能是<r>Enka.Network接口服务出现问题</r>')
            return '无法从Enka.Network获取该uid的信息，可能是接口服务出现问题，请稍候再试'
        await PlayerInfo.update_info(self.user_id, self.uid, data['playerInfo'], 'enka')
        if 'avatarInfoList' not in data:
            return '未在游戏中打开角色展柜，请打开后3分钟后再试'
        for character in data['avatarInfoList']:
            await Character.update_info(self.user_id, self.uid, character, 'enka')
        logger.info('原神信息', f'➤UID<m>{self.uid}</m><g>更新Enka成功</g>')
        return '更新以下角色成功：\n' + ' '.join(
            [get_name_by_id(str(c['avatarId'])) for c in data['playerInfo']['showAvatarInfoList']])

    async def update_talent(self) -> str:
        """
        从mihoyo api中更新每一个角色的天赋信息
            :return: 更新结果
        """
        characters = await Character.filter(user_id=self.user_id, uid=self.uid, data_source='mihoyo').all()
        for character in characters:
            data = await get_mihoyo_private_data(self.uid, self.user_id, 'role_skill', str(character.character_id))
            if not isinstance(data, dict):
                return data
            elif data['retcode'] != 0:
                logger.info('原神信息',
                            f'更新<m>{self.uid}</m>的<m>{character.name}</m>角色天赋时出错，消息为<r>{data["message"]}</r>')
                return data['message']
            data = data['data']['skill_list']
            cname = f'{character.element}主' if character.name in ['荧', '空'] else character.name
            if len(character.constellation) >= 3:
                data[ra_score['Talent'][cname][0]]['level_current'] += 3
            if len(character.constellation) >= 5:
                data[ra_score['Talent'][cname][1]]['level_current'] += 3
            length = 4 if character.name in ['莫娜', '神里绫华'] else 3
            if character.name == '安柏':
                data[0], data[2] = data[2], data[0]
            character.talents = Talents(talent_list=[Talent(
                name=t['name'],
                level=t['level_current'],
                icon=talent_map['Icon'][str(t['id'])]
            ) for t in data[:length]])
            await character.save()
            await asyncio.sleep(0.3)
        logger.info('原神信息', f'➤UID<m>{self.uid}</m><g>更新角色天赋成功</g>')
        return '更新成功'

    async def update_from_mihoyo(self) -> str:
        """
        从米游社api更新原神数据
            :return: 更新结果
        """
        data = await get_mihoyo_public_data(self.uid, self.user_id, 'player_card')
        if not isinstance(data, dict):
            return data
        elif data['retcode'] == 1034:
            logger.info('原神信息', f'更新<m>{self.uid}</m>的玩家数据时出错，状态码为1034，<r>疑似验证码</r>')
            return (
                '遇验证码阻拦，需手动前往米游社进行验证后才能继续使用'
                if await self.is_bind()
                else '未绑定私人Cookie，更新米游社数据时遇验证码阻拦而失败'
            )
        elif data['retcode'] != 0:
            logger.info('原神信息', f'更新<m>{self.uid}</m>的玩家数据时出错，消息为<r>{data["message"]}</r>')
            return data['message']
        await PlayerInfo.update_info(self.user_id, self.uid, data['data'], 'mihoyo')
        chara_data = await get_mihoyo_public_data(self.uid, self.user_id, 'role_detail')
        if not isinstance(chara_data, dict):
            return chara_data
        elif chara_data['retcode'] != 0:
            logger.info('原神信息', f'更新<m>{self.uid}</m>的玩家角色数据时出错，消息为<r>{chara_data["message"]}</r>')
            return chara_data['message']
        for character in chara_data['data']['avatars']:
            await Character.update_info(self.user_id, self.uid, character, 'mihoyo')
        logger.info('原神信息', f'➤UID<m>{self.uid}</m><g>更新玩家信息成功</g>')
        return '更新成功'

    async def update_abyss_info(self, abyss_index: int) -> str:
        data = await get_mihoyo_public_data(self.uid, self.user_id, 'abyss', schedule_type=str(abyss_index))
        if not isinstance(data, dict):
            return data
        elif data['retcode'] != 0:
            logger.info('原神信息', f'更新<m>{self.uid}</m>的玩家数据时出错，消息为<r>{data["message"]}</r>')
            return data['message']
        await AbyssInfo.update_info(self.user_id, self.uid, data['data'])
        logger.info('原神信息', f'➤UID<m>{self.uid}</m><g>更新深渊信息成功</g>')
        return '更新成功'

    async def get_info(self) -> Optional[PlayerInfo]:
        """
        获取原神玩家总体信息
            :return: 玩家信息
        """
        await LastQuery.update_last_query(self.user_id, self.uid)
        return await PlayerInfo.get_or_none(user_id=self.user_id, uid=self.uid)

    async def get_character(self, name: Optional[str] = None, character_id: Optional[int] = None,
                            data_source: Optional[DataSourceType] = None) -> Optional[Character]:
        """
        根据角色名或角色id（二选一）获取角色信息
            :param name: 角色名
            :param character_id: 角色id
            :param data_source: 数据来源(mihoyo/enka)，不指定时返回最近更新的
            :return: 角色信息
        """
        query = {'user_id': self.user_id, 'uid': self.uid}
        if name:
            query['name'] = name
        elif character_id:
            query['character_id'] = character_id
        else:
            raise ValueError('name or character_id must be specified')
        if data_source == 'enka':
            """如果角色不存在或者角色的更新时间在6小时前，则更新角色信息"""
            character = await Character.get_or_none(**query, data_source='enka')
            if not character or character.update_time < (
                    datetime.datetime.now() - datetime.timedelta(hours=config.ysd_auto_update)).replace(
                    tzinfo=pytz.timezone('Asia/Shanghai')):
                try:
                    await self.update_from_enka()
                except Exception as e:
                    logger.info('原神角色面板', '➤➤', {'角色': name or character_id}, f'数据更新失败，可能是Enka.Network接口出现问题:{e}', False)
                    if character:
                        return character
                    else:
                        raise e
                if character := await Character.get_or_none(**query, data_source='enka'):
                    logger.info('原神角色面板', '➤➤', {'角色': name or character_id}, '数据更新成功', True)
                else:
                    logger.info('原神角色面板', '➤➤', {'角色': name or character_id}, '不在游戏内展示柜中，更新失败',
                                False)
            else:
                logger.info('原神角色面板', '➤➤', {'角色': name or character_id}, '数据获取成功', True)
            return character
        elif data_source == 'mihoyo':
            return await Character.get_or_none(**query, data_source='mihoyo')
        else:
            characters = await Character.filter(**query).order_by('data_source')
            return characters[0] if characters else None

    async def get_chara_bag(self) -> Tuple[Union[PlayerInfo, str], List[Character]]:
        """
        获取原神角色背包信息
            :return: 原神玩家信息和角色列表
        """
        await LastQuery.update_last_query(self.user_id, self.uid)
        player_info = await PlayerInfo.get_or_none(user_id=self.user_id, uid=self.uid)
        if player_info is None or player_info.update_time is None or player_info.update_time < (
                datetime.datetime.now() - datetime.timedelta(hours=config.ysa_auto_update)).replace(
            tzinfo=pytz.timezone('Asia/Shanghai')):
            result = await self.update_from_mihoyo()
            if result != '更新成功':
                return result, []
        if (player_info := await PlayerInfo.get_or_none(user_id=self.user_id, uid=self.uid)) is None:
            return '获取原神信息失败', []
        character_list = []
        for character_name in CHARACTERS:
            if character := await self.get_character(name=character_name):
                character_list.append(character)
        return player_info, character_list

    async def get_player_info(self) -> Tuple[Union[PlayerInfo, str], Optional[List[Character]]]:
        await LastQuery.update_last_query(self.user_id, self.uid)
        player_info = await PlayerInfo.get_or_none(user_id=self.user_id, uid=self.uid)
        if player_info is None or player_info.update_time is None or player_info.update_time < (
                datetime.datetime.now() - datetime.timedelta(hours=config.ys_auto_update)).replace(
            tzinfo=pytz.timezone('Asia/Shanghai')):
            result = await self.update_from_mihoyo()
            if result != '更新成功':
                return result, None
            await self.update_from_enka()
        if (player_info := await PlayerInfo.get_or_none(user_id=self.user_id, uid=self.uid)) is None:
            return '获取原神信息失败', None
        characters_list = []
        for chara in player_info.avatars:
            if c := await self.get_character(character_id=chara):
                characters_list.append(c)
        return player_info, characters_list

    async def get_abyss_info(self, abyss_index: int = 1) -> Union[AbyssInfo, str]:
        await LastQuery.update_last_query(self.user_id, self.uid)
        await AbyssInfo.filter(user_id=self.user_id, uid=self.uid).delete()
        result = await self.update_abyss_info(abyss_index)
        if result != '更新成功':
            return result
        return await AbyssInfo.get_or_none(user_id=self.user_id, uid=self.uid)

    async def export_data(self) -> dict:
        """
        导出原神数据为字典
            :return: 原神数据字典
        """
        data = {}
        if player_info := await PlayerInfo.get_or_none(user_id=self.user_id, uid=self.uid).values():
            data['player_info'] = player_info
        if characters := await Character.filter(user_id=self.user_id, uid=self.uid).values():
            data['characters'] = characters
        return data


class GenshinTools:
    """
    原神相关工具类
    """

    @staticmethod
    def artifact_single_score(role_prop: dict, prop_name: str, prop_value: float, effective: dict):
        """
        计算圣遗物单词条的有效词条数
            :param role_prop: 角色基础属性
            :param prop_name: 属性名
            :param prop_value: 属性值
            :param effective: 有效词条列表
            :return: 评分
        """
        prop_map = {'攻击力':       4.975, '生命值': 4.975, '防御力': 6.2, '暴击率': 3.3, '暴击伤害': 6.6,
                    '元素精通':     19.75, '元素充能效率': 5.5}

        if prop_name in effective and prop_name in {'攻击力', '生命值', '防御力'}:
            return round(prop_value / role_prop[prop_name] * 100 / prop_map[prop_name] * effective[prop_name], 2)

        if prop_name.replace('百分比', '') in effective:
            return round(
                prop_value / prop_map[prop_name.replace('百分比', '')] * effective[prop_name.replace('百分比', '')],
                2)

        return 0

    @staticmethod
    def artifact_score(prop: CharacterProperty, artifact: Artifact, effective: dict) -> Tuple[float, float]:
        """
        计算圣遗物总有效词条数以及评分
            :param prop: 角色基础属性
            :param artifact: 圣遗物信息
            :param effective: 有效词条列表
            :return: 总词条数，评分
        """
        if not artifact.prop_list:
            return 0, 0
        new_role_prop = {'攻击力': prop.base_attack, '生命值': prop.base_health, '防御力': prop.base_defense}

        value = sum(
            GenshinTools.artifact_single_score(new_role_prop, i.name, i.value, effective) for i in artifact.prop_list)

        value = round(value, 2)
        return value, round(value / GenshinTools.get_expect_score(effective) * 100, 1)

    @staticmethod
    def artifacts_total_score(character: Character, artifacts: Artifacts) -> Tuple[Optional[float], Optional[float]]:
        if not character.prop:
            return None, None
        effective = GenshinTools.get_effective(character)
        total_score = 0
        total_value = 0
        for artifact in artifacts:
            a, b = GenshinTools.artifact_score(character.prop, artifact, effective)
            total_score += a
            total_value += b
        return None if total_score == 0 else round(total_score, 2), None if total_value == 0 else round(
            total_value / len(artifacts), 2)

    @staticmethod
    def get_expect_score(effective: dict):
        """
        计算单个圣遗物小毕业所需的期望词条数
            :param effective: 有效词条列表
            :return: 期望词条数
        """
        if len(effective.keys()) == 2:
            average = 15 / 5
        elif effective.keys() == '西风':
            average = 17 / 5
        elif len(effective.keys()) == 3:
            average = 24 / 5
        elif len(effective.keys()) == 4:
            average = 28 / 5
        else:
            average = 30 / 5
        total = sum(value * average for value in effective.values())
        return round(total / len(effective.keys()), 2)

    @staticmethod
    def get_artifact_suit(artifacts: Artifacts) -> List[Tuple[str, str]]:
        """
        获取圣遗物套装
            :param artifacts: 圣遗物列表
            :return: 套装列表
        """
        suit2 = []
        final_suit = []
        suit = [artifact.suit for artifact in artifacts]
        for s in suit:
            if s not in suit2 and 1 < suit.count(s) < 4:
                suit2.append(s)
            if suit.count(s) >= 4:
                for r in artifacts:
                    if r.suit == s:
                        return [(s, r.icon), (s, r.icon)]
        for r in artifacts:
            if r.suit in suit2:
                final_suit.append((r.suit, r.icon))
                suit2.remove(r.suit)
        return final_suit

    @staticmethod
    def get_effective(character: Character):
        """
        根据角色的武器、圣遗物来判断获取该角色有效词条列表
            :param character: 角色信息
            :return: 有效词条列表
        """
        role_name = f'{character.element}主' if character.name in {'荧', '空'} else character.name
        if role_name not in ra_score['Role']:
            return {'攻击力': 1, '暴击率': 1, '暴击伤害': 1}
        artifacts = character.artifacts
        if len(artifacts) < 5:
            return ra_score['Role'][role_name]['常规']
        if artifacts[-2].main_property.name == '岩元素伤害加成':
            if role_name == '钟离':
                return ra_score['Role'][role_name]['岩伤']
        elif artifacts[-2].main_property.name in ['物理伤害加成', '火元素伤害加成', '冰元素伤害加成']:
            if role_name == '钟离':
                return ra_score['Role'][role_name]['武神']
        if role_name == '班尼特' and artifacts[-2].main_property.name == '火元素伤害加成':
            return ra_score['Role'][role_name]['输出']
        if role_name == '甘雨':
            suit = GenshinTools.get_artifact_suit(artifacts)
            if suit and ('乐团' in suit[0][0] or len(suit) == 2 and '乐团' in suit[1][0]):
                return ra_score['Role'][role_name]['融化']
        if role_name == '申鹤' and artifacts[-2].main_property.name == '冰元素伤害加成':
            return ra_score['Role'][role_name]['输出']
        if role_name == '七七' and artifacts[-2].main_property.name == '物理伤害加成':
            return ra_score['Role'][role_name]['输出']
        if role_name in ['枫原万叶', '温迪', '砂糖'] and artifacts[-2].main_property.name == '风元素伤害加成':
            return ra_score['Role'][role_name]['输出']
        if '西风' in character.weapon.name and '西风' in ra_score['Role'][role_name]:
            return ra_score['Role'][role_name]['西风']
        return ra_score['Role'][role_name]['常规']

    @staticmethod
    def check_effective(prop_name: str, effective: dict):
        """
        检查词条是否有效
            :param prop_name: 词条属性名
            :param effective: 有效词条列表
            :return: 是否有效
        """
        if '攻击力' in effective and '攻击力' in prop_name:
            return True
        if '生命值' in effective and '生命值' in prop_name:
            return True
        if '防御力' in effective and '防御力' in prop_name:
            return True
        return prop_name in effective
