import json,os,re
from hoshino import R,MessageSegment,logger, Service
from hoshino.typing import CQEvent, Message
from ..util import get_uid_by_qq, get_cookie, check_uid_by_qq, update_last_query_to_qq
from ..get_data import get_player_card_data, get_chara_detail_data, get_chara_skill_data
from .get_img import draw_player_card, draw_all_chara_card, draw_chara_card
from ..character_alias import get_id_by_alias

sv = Service('原神信息查询')

@sv.on_prefix('ys')
async def player_card(bot,ev):
    uid = ev.message.extract_plain_text().strip()
    qq = str(ev.user_id)
    if ev.message_type == 'guild':
        rm = str(ev.message)
    else:
        rm = str(ev.raw_message)
    match = re.search(r"\[CQ:at,qq=(.*)\]", rm)
    if match:
        uid = ''
        qq = str(match.group(1))
    if not uid:
        uid = get_uid_by_qq(qq)
        if not uid:
            await bot.send(ev,'请把uid给派蒙哦，比如ys100000001',at_sender=True)
            return
    if len(uid) != 9 or not uid.isdigit():
        await bot.send(ev,f'uid {uid} 不合规,是不是打错了呀',at_sender=True)
        return
    cookie = await get_cookie(qq, uid)
    update_last_query_to_qq(qq, uid)
    if not cookie:
        await bot.send(ev,'这个uid的cookie信息好像失效了，请给派蒙重新绑定！',at_sender=True)
    else:
        try:
            if ev.message_type == 'group':
                user_info = await bot.get_group_member_info(group_id=ev.group_id,user_id=int(qq))
                nickname = user_info['card'] or user_info['nickname']
            else:
                nickname = ev.sender['nickname']
            data = await get_player_card_data(uid, cookie)
            chara_data = await get_chara_detail_data(uid, cookie) or []
            player_card = await draw_player_card(data, chara_data, uid, nickname)
            await bot.send(ev, player_card, at_sender=True)
        except Exception as e:
            await bot.send(ev, f'派蒙出现了问题：{e}',at_sender=True)

@sv.on_prefix('ysa')
async def all_characters(bot,ev):
    uid = ev.message.extract_plain_text().strip()
    qq = str(ev.user_id)
    if ev.message_type == 'guild':
        rm = str(ev.message)
    else:
        rm = str(ev.raw_message)
    match = re.search(r"\[CQ:at,qq=(.*)\]", rm)
    if match:
        uid = ''
        qq = str(match.group(1))
    if not uid:
        uid = get_uid_by_qq(qq)
        if not uid:
            await bot.send(ev,'请把uid给派蒙哦，比如ysa100000001',at_sender=True)
            return
    if len(uid) != 9 or not uid.isdigit():
        await bot.send(ev,f'uid {uid} 不合规,是不是打错了呀',at_sender=True)
        return
    cookie = await get_cookie(qq, uid)
    update_last_query_to_qq(qq, uid)
    if not cookie:
        await bot.send(ev,'这个uid的cookie信息好像失效了，请给派蒙重新绑定！',at_sender=True)
    else:
        try:
            chara_data = await get_chara_detail_data(uid, cookie) or []
            player_card = await draw_all_chara_card(chara_data, uid)
            await bot.send(ev, player_card, at_sender=True)
        except Exception as e:
            await bot.send(ev, f'派蒙出现了问题：{e}',at_sender=True)


#chara_list=['云堇','申鹤','荒泷一斗','五郎','优菈','阿贝多','托马','胡桃','达达利亚','雷电将军','珊瑚宫心海','埃洛伊','宵宫','神里绫华','枫原万叶','温迪','刻晴','莫娜','可莉','琴','迪卢克','七七','魈','钟离','甘雨','旅行者','早柚','九条裟罗','凝光','菲谢尔','班尼特','丽莎','行秋','迪奥娜','安柏','重云','雷泽','芭芭拉','罗莎莉亚','香菱','凯亚','北斗','诺艾尔','砂糖','辛焱','烟绯','八重神子','神里绫人']
@sv.on_prefix('ysc')
async def my_characters(bot,ev):
    msg = ev.message.extract_plain_text().strip().split(' ')
    qq = str(ev.user_id)
    uid = ''
    if len(msg[0]) == 9 and msg[0].isdigit():
        uid = msg[0]
        if len(msg) >= 2:
            chara = msg[1]
        else:
            await bot.send(ev,'要把想查询的角色名告诉我哦！',at_sender=True)
            return
    else:
        chara = msg[0]
    chara_name = get_id_by_alias(chara)
    if not chara_name:
        await bot.send(ev,f'没有角色名叫{chara}哦！',at_sender=True)
        return
    if ev.message_type == 'guild':
        rm = str(ev.message)
    else:
        rm = str(ev.raw_message)
    match = re.search(r"\[CQ:at,qq=(.*)\]", rm)
    if match:
        qq = str(match.group(1))
    if not uid:
        uid = get_uid_by_qq(qq)
        if not uid:
            await bot.send(ev,'请把uid给派蒙哦，比如ysc100000001 钟离',at_sender=True)
            return
    if len(uid) != 9 or not uid.isdigit():
        await bot.send(ev,f'uid {uid} 不合规,是不是打错了呀',at_sender=True)
        return
    cookie = await get_cookie(qq, uid)
    update_last_query_to_qq(qq, uid)
    if not cookie:
        await bot.send(ev,'你没有绑定cookie或者cookie失效了噢！',at_sender=True)
    else:
        try:
            chara_data = await get_chara_detail_data(uid, cookie)
            skill_data = await get_chara_skill_data(uid, chara_name[0], cookie)
            chara_card = await draw_chara_card(chara_data, skill_data, chara_name, uid)
            await bot.send(ev, chara_card, at_sender=True)
        except Exception as e:
            await bot.send(ev, f'派蒙出现了问题：{e}',at_sender=True)
    
