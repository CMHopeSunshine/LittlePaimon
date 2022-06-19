from pathlib import Path
import datetime

from utils.alias_handler import get_name_by_id
from utils.file_handler import load_json, save_json

role_element = load_json(path=Path(__file__).parent / 'json' / 'role_element.json')
role_skill = load_json(path=Path(__file__).parent / 'json' / 'role_skill.json')
role_talent = load_json(path=Path(__file__).parent / 'json' / 'role_talent.json')
weapon = load_json(path=Path(__file__).parent / 'json' / 'weapon.json')
prop_list = load_json(path=Path(__file__).parent / 'json' / 'prop.json')
artifact_list = load_json(path=Path(__file__).parent / 'json' / 'artifact.json')
ra_score = load_json(path=Path(__file__).parent / 'json' / 'score.json')


class PlayerInfo:
    def __init__(self, uid: str):
        self.path = Path(__file__).parent.parent / 'user_data' / 'player_info' / f'{uid}.json'
        self.data = load_json(path=self.path)
        self.player_info = self.data['玩家信息'] if '玩家信息' in self.data else {}
        self.roles = self.data['角色'] if '角色' in self.data else {}
        # self.artifacts = self.data['圣遗物'] if '圣遗物' in self.data else transform_artifacts(self.roles)

    def set_player(self, data: dict):
        self.player_info['昵称'] = data.get('nickname', 'unknown')
        self.player_info['等级'] = data.get('level', 'unknown')
        self.player_info['世界等级'] = data.get('worldLevel', 'unknown')
        self.player_info['签名'] = data.get('signature', 'unknown')
        self.player_info['成就'] = data.get('finishAchievementNum', 'unknown')
        self.player_info['角色列表'] = dictList_to_list(data.get('showAvatarInfoList'))
        self.player_info['名片列表'] = data.get('showNameCardIdList', 'unknown')
        self.player_info['头像'] = data['profilePicture']['avatarId']
        self.player_info['更新时间'] = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

    def set_role(self, data: dict):
        role_info = {}
        role_name = get_name_by_id(str(data['avatarId']))
        if role_name not in ['荧', '空']:
            role_info['名称'] = role_name
            role_info['角色ID'] = data['avatarId']
            role_info['等级'] = int(data['propMap']['4001']['val'])
            role_info['好感度'] = data['fetterInfo']['expLevel']
            role_info['元素'] = role_element[role_name]

            role_info['天赋'] = []
            if 'talentIdList' in data:
                if len(data['talentIdList']) >= 3:
                    data['skillLevelMap'][list(data['skillLevelMap'].keys())[ra_score['Talent'][role_name][0]]] += 3
                if len(data['talentIdList']) >= 5:
                    data['skillLevelMap'][list(data['skillLevelMap'].keys())[ra_score['Talent'][role_name][1]]] += 3
            for skill in data['skillLevelMap']:
                skill_detail = {'名称': role_skill['Name'][skill], '等级': data['skillLevelMap'][skill],
                                '图标': role_skill['Icon'][skill]}
                role_info['天赋'].append(skill_detail)
            if role_name == '神里绫华':
                role_info['天赋'][0], role_info['天赋'][-1] = role_info['天赋'][-1], role_info['天赋'][0]
                role_info['天赋'][2], role_info['天赋'][-1] = role_info['天赋'][-1], role_info['天赋'][2]

            role_info['命座'] = []
            if 'talentIdList' in data:
                for talent in data['talentIdList']:
                    talent_detail = {'名称': role_talent['Name'][str(talent)], '图标': role_talent['Icon'][str(talent)]}
                    role_info['命座'].append(talent_detail)

            prop = {}
            prop['基础生命'] = round(data['fightPropMap']['1'])
            prop['额外生命'] = round(data['fightPropMap']['2000'] - prop['基础生命'])
            prop['基础攻击'] = round(data['fightPropMap']['4'])
            prop['额外攻击'] = round(data['fightPropMap']['2001'] - prop['基础攻击'])
            prop['基础防御'] = round(data['fightPropMap']['7'])
            prop['额外防御'] = round(data['fightPropMap']['2002'] - prop['基础防御'])
            prop['暴击率'] = round(data['fightPropMap']['20'], 3)
            prop['暴击伤害'] = round(data['fightPropMap']['22'], 3)
            prop['元素精通'] = round(data['fightPropMap']['28'])
            prop['元素充能效率'] = round(data['fightPropMap']['23'], 3)
            prop['治疗加成'] = round(data['fightPropMap']['26'], 3)
            prop['受治疗加成'] = round(data['fightPropMap']['27'], 3)
            prop['伤害加成'] = [round(data['fightPropMap']['30'], 3)]
            for i in range(40, 47):
                prop['伤害加成'].append(round(data['fightPropMap'][str(i)], 3))
            role_info['属性'] = prop

            weapon_info = {}
            weapon_data = data['equipList'][-1]
            weapon_info['名称'] = weapon['Name'][weapon_data['flat']['nameTextMapHash']]
            weapon_info['图标'] = weapon_data['flat']['icon']
            weapon_info['类型'] = weapon['Type'][weapon_data['flat']['nameTextMapHash']]
            weapon_info['等级'] = weapon_data['weapon']['level']
            weapon_info['星级'] = weapon_data['flat']['rankLevel']
            if 'promoteLevel' in weapon_data['weapon']:
                weapon_info['突破等级'] = weapon_data['weapon']['promoteLevel']
            else:
                weapon_info['突破等级'] = 0
            if 'affixMap' in weapon_data['weapon']:
                weapon_info['精炼等级'] = list(weapon_data['weapon']['affixMap'].values())[0] + 1
            else:
                weapon_info['精炼等级'] = 1
            weapon_info['基础攻击'] = weapon_data['flat']['weaponStats'][0]['statValue']
            try:
                weapon_info['副属性'] = {'属性名': prop_list[weapon_data['flat']['weaponStats'][1]['appendPropId']],
                                      '属性值': weapon_data['flat']['weaponStats'][1]['statValue']}
            except IndexError:
                weapon_info['副属性'] = {'属性名': '无属性', '属性值': 0}
            weapon_info['特效'] = '待补充'
            role_info['武器'] = weapon_info

            artifacts = []
            for artifact in data['equipList'][:-1]:
                artifact_info = {}
                artifact_info['名称'] = artifact_list['Name'][artifact['flat']['icon']]
                artifact_info['图标'] = artifact['flat']['icon']
                artifact_info['部位'] = artifact_list['Piece'][artifact['flat']['icon'].split('_')[-1]][1]
                artifact_info['所属套装'] = artifact_list['Mapping'][artifact_info['名称']]
                artifact_info['等级'] = artifact['reliquary']['level'] - 1
                artifact_info['星级'] = artifact['flat']['rankLevel']
                artifact_info['主属性'] = {'属性名': prop_list[artifact['flat']['reliquaryMainstat']['mainPropId']],
                                        '属性值': artifact['flat']['reliquaryMainstat']['statValue']}
                artifact_info['词条'] = []
                for reliquary in artifact['flat']['reliquarySubstats']:
                    artifact_info['词条'].append({'属性名': prop_list[reliquary['appendPropId']],
                                                '属性值': reliquary['statValue'],
                                                '评分':  artifact_score(role_name, prop_list[reliquary['appendPropId']],
                                                                      reliquary['statValue'], artifact_info['部位'])})
                artifacts.append(artifact_info)
            role_info['圣遗物'] = artifacts
            role_info['更新时间'] = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            self.roles[role_name] = role_info
            # self.set_artifacts(data)

    # def set_artifacts(self, data):
    #     for artifact in data['equipList'][:-1]:
    #         artifact_info = {}
    #         artifact_info['名称'] = artifact_list['Name'][artifact['flat']['icon']]
    #         artifact_info['图标'] = artifact['flat']['icon']
    #         artifact_info['部位'] = artifact_list['Piece'][artifact['flat']['icon'].split('_')[-1]][1]
    #         artifact_info['所属套装'] = artifact_list['Mapping'][artifact_info['名称']]
    #         artifact_info['等级'] = artifact['reliquary']['level'] - 1
    #         artifact_info['星级'] = artifact['flat']['rankLevel']
    #         artifact_info['主属性'] = {'属性名': prop_list[artifact['flat']['reliquaryMainstat']['mainPropId']],
    #                                 '属性值': artifact['flat']['reliquaryMainstat']['statValue']}
    #         artifact_info['词条'] = []
    #         for reliquary in artifact['flat']['reliquarySubstats']:
    #             artifact_info['词条'].append({'属性名': prop_list[reliquary['appendPropId']],
    #                                         '属性值': reliquary['statValue']})
    #         artifact_info['角色名'] = get_name_by_id(str(data['avatarId']))
    #         if artifact_info not in self.artifacts:
    #             self.artifacts.append(artifact_info)

    def get_player_info(self):
        return self.player_info

    def get_update_roles_list(self):
        return self.player_info['角色列表']

    def get_roles_list(self):
        return list(self.roles.keys())

    def get_roles_info(self, role_name):
        if role_name in self.roles:
            return self.roles[role_name]
        else:
            return None

    def save(self):
        self.data['玩家信息'] = self.player_info
        self.data['角色'] = self.roles
        save_json(data=self.data, path=self.path)


def dictList_to_list(data):
    if not isinstance(data, list):
        return 'unknown'
    new_data = {}
    for d in data:
        name = get_name_by_id(str(d['avatarId']))
        if name not in ['荧', '空']:
            new_data[name] = d['avatarId']
    return new_data


# def transform_artifacts(data):
#     artifacts = []
#     for role in data.values():
#         for artifact in role['圣遗物']:
#             artifacts_temp = {}
#             artifacts_temp['名称'] = artifact['名称']
#             artifacts_temp['图标'] = artifact['图标']
#             artifacts_temp['部位'] = artifact['部位']
#             artifacts_temp['所属套装'] = artifact['所属套装']
#             artifacts_temp['等级'] = artifact['等级']
#             artifacts_temp['星级'] = artifact['星级']
#             artifacts_temp['主属性'] = artifact['主属性']
#             artifacts_temp['词条'] = []
#             for reliquary in artifact['词条']:
#                 artifacts_temp['词条'].append({'属性名': reliquary['属性名'],
#                                             '属性值': reliquary['属性值']})
#             artifacts_temp['角色名'] = role['名称']
#             artifacts.append(artifacts_temp)
#     return artifacts


def artifact_score(role_name, prop_name, prop_value, artifact_type):
    effective = ra_score['Role'][role_name]
    score = 0
    if '攻击力' in effective:
        if prop_name == '攻击力':
            score = prop_value * 0.24
        elif prop_name == '百分比攻击力':
            score = prop_value * 1
    if '生命值' in effective:
        if prop_name == '生命值':
            score = prop_value * 0.014
        elif prop_name == '百分比生命值':
            score = prop_value * 0.86
    if '防御力' in effective:
        if prop_name == '防御力':
            score = prop_value * 0.18
        elif prop_name == '百分比防御力':
            score = prop_value * 0.7
    if '元素精通' in effective and prop_name == '元素精通':
        score = prop_value * 0.25
    if '元素充能效率' in effective and prop_name == '元素充能效率':
        score = prop_value * 0.65
    if '暴击率' in effective and prop_name == '暴击率':
        if artifact_type == '理之冠':
            score = prop_value * 3
        else:
            score = prop_value * 2
    if '暴击伤害' in effective and prop_name == '暴击伤害':
        if artifact_type == '理之冠':
            score = prop_value * 1.5
        else:
            score = prop_value * 1
    return round(score, 2)


def check_effective(role_name, prop_name):
    effective = ra_score['Role'][role_name]
    if '攻击力' in effective and '攻击力' in prop_name:
        return True
    if '生命值' in effective and '生命值' in prop_name:
        return True
    if '防御力' in effective and '防御力' in prop_name:
        return True
    return prop_name in effective


def artifact_total_score(data):
    score = 0
    for i in data:
        score += i['评分']
    return round(score, 1)
