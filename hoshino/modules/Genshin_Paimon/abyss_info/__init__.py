import json,os,re
from hoshino import R,MessageSegment,logger, Service
from hoshino.typing import CQEvent, Message
from ..util import get_uid_by_qq, get_cookie, update_last_query_to_qq
from ..get_data import get_abyss_data
from .get_img import draw_abyss_card

sv = Service('原神深渊查询')

@sv.on_prefix(('sy','深渊查询','深境螺旋查询'))
async def main(bot,ev):
    msg = ev.message.extract_plain_text().strip().split(' ')
    uid = ''
    if len(msg[0]) == 9 and msg[0].isdigit():
        uid = msg[0]
        del msg[0]
    if not msg:
        abyss_floor = []
    else:
        abyss_floor = msg
    abyss_floor_true = []
    for floor in abyss_floor:
        if floor.isdigit() and (int(floor) <= 12 and int(floor) >= 9):
            abyss_floor_true.append(int(floor))
    abyss_floor_true.sort()
    if len(abyss_floor_true)>2:
        abyss_floor_true = [abyss_floor_true[0],abyss_floor_true[1]]
    qq = str(ev.user_id)
    # nickname = ev['sender']['nickname']
    if ev.message_type == 'guild':
        rm = str(ev.message)
    else:
        rm = str(ev.raw_message)
    match = re.search(r"\[CQ:at,qq=(.*)\]", rm)
    if match:
        uid = ''
        qq = str(match.group(1))
        # try:
        #     qq_info = await bot.get_group_member_info(group_id=ev.group_id,
        #                                             user_id=qid)
        # except:
        #     qq_info = await bot.get_guild_member_profile(guild_id=ev.guild_id,
        #                                             user_id=qid)
        # nickname = qq_info['nickname']
    if not uid:
        uid = get_uid_by_qq(qq)
        if not uid:
            await bot.send(ev,'请把uid给派蒙哦，比如sy100000001',at_sender=True)
            return
    cookie = await get_cookie(qq, uid)
    update_last_query_to_qq(qq, uid)
    if not cookie:
        await bot.send(ev,'当前cookie池中没有可用的cookie，请联系开发者',at_sender=True)
    else:
        try:
            data = await get_abyss_data(uid, cookie)
            abyss_card = await draw_abyss_card(data, uid, abyss_floor_true)
            await bot.send(ev,abyss_card,at_sender=True)
        except Exception as e:
            await bot.send(ev, f'派蒙出现了问题：{e}',at_sender=True)

        
    
