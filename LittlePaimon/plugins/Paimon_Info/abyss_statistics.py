import datetime
from collections import defaultdict
from nonebot import get_bot
from LittlePaimon.database.models import AbyssInfo
from LittlePaimon.utils.image import PMImage, font_manager as fm
from LittlePaimon.utils.message import MessageBuild


async def get_statistics(group_id: int):
    if not (info_list := await AbyssInfo.all()):
        return '本群还没有深渊战斗数据哦！'
    member_list = await get_bot().get_group_member_list(group_id=group_id)
    member_id_list = [str(member['user_id']) for member in member_list]
    info_list = [info for info in info_list if info.user_id in member_id_list and info.total_battle and info.total_star and info.max_damage and info.max_take_damage]
    now = datetime.datetime.now()
    if 1 <= now.day < 15:
        left_day = 1
        right_day = 15
    else:
        left_day = 16
        right_day = 31
    info_list = [info for info in info_list if left_day <= info.update_time.day <= right_day]
    if not info_list:
        return '本群还没有深渊战斗数据哦！'
    # 数据数
    info_num = len(info_list)
    # 满星人数
    full_star_num = len([info for info in info_list if info.total_star >= 36])
    # 平均星数
    average_star = round(sum(info.total_star for info in info_list) / info_num, 1)
    # 平均战斗次数
    average_battle_num = round(sum(info.total_battle for info in info_list) / info_num, 1)
    # 最高伤害角色
    max_damage = max(info_list, key=lambda x: x.max_damage.value)
    # print(max_damage)
    # return '123'
    max_damage_user = [m for m in member_list if str(m['user_id']) == max_damage.user_id][0]
    max_damage_user = max_damage_user['card'] or max_damage_user['nickname']
    # 最多承伤角色
    max_take_damage = max(info_list, key=lambda x: x.max_take_damage.value)
    max_take_damage_user = [m for m in member_list if str(m['user_id']) == max_take_damage.user_id][0]
    max_take_damage_user = max_take_damage_user['card'] or max_take_damage_user['nickname']
    # 11、12层阵容
    battle_characters_up11 = defaultdict(lambda: 0)
    battle_characters_down11 = defaultdict(lambda: 0)
    battle_characters_up12 = defaultdict(lambda: 0)
    battle_characters_down12 = defaultdict(lambda: 0)
    for info in info_list:
        if floor11 := info.floors.get(11):
            for battles in floor11.battles_up:
                for character in battles.characters:
                    battle_characters_up11[character.name] += 1
            for battles in floor11.battles_down:
                for character in battles.characters:
                    battle_characters_down11[character.name] += 1
        if floor12 := info.floors.get(12):
            for battles in floor12.battles_up:
                for character in battles.characters:
                    battle_characters_up12[character.name] += 1
            for battles in floor12.battles_down:
                for character in battles.characters:
                    battle_characters_down12[character.name] += 1
    up_sort11 = [character[0] for character in
                 sorted(battle_characters_up11.items(), key=lambda x: x[1], reverse=True)[:4]]
    down_sort11 = [character[0] for character in
                   sorted(battle_characters_down11.items(), key=lambda x: x[1], reverse=True)[:4]]
    up_sort12 = [character[0] for character in
                 sorted(battle_characters_up12.items(), key=lambda x: x[1], reverse=True)[:4]]
    down_sort12 = [character[0] for character in
                   sorted(battle_characters_down12.items(), key=lambda x: x[1], reverse=True)[:4]]

    text = f'本群群友{now.strftime("%m月%d日")}深渊统计情况：\n满星人数/总人数：  {full_star_num}/{info_num}\n平均星数：  {average_star}\n平均战斗次数：  {average_battle_num}\n最高伤害角色：  {max_damage_user}的{max_damage.max_damage.name}({max_damage.max_damage.value})\n' \
           f'最高承伤角色：  {max_take_damage_user}的{max_take_damage.max_take_damage.name}({max_take_damage.max_take_damage.value})\n' \
           f'11层出场率最高角色：\n  上半：{" ".join(up_sort11)}\n  下半：{" ".join(down_sort11)}\n' \
           f'12层出场率最高角色：\n  上半：{" ".join(up_sort12)}\n  下半：{" ".join(down_sort12)}\n' \
           f'Created by LittlePaimon'

    img = PMImage(size=(500, 33 * 15), color=(255, 255, 255, 255))
    await img.text_box(text.replace('\n', '^'), (10, 490), (10, 33 * 15 - 10), fm.get('hywh', 25), 'black')
    return MessageBuild.Image(img, mode='RGB')
