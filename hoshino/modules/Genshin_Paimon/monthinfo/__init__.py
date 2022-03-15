import json,os,re,datetime
from hoshino import R,MessageSegment,logger, Service
from hoshino.typing import CQEvent, Message
from ..util import get_uid_by_qq, get_cookie, check_uid_by_qq, update_last_query_to_qq
from ..get_data import get_monthinfo_data
from .get_img import draw_monthinfo_card

sv = Service('原神每月札记')

@sv.on_prefix(('myzj','每月札记'))
async def main(bot,ev):
    msg = ev.message.extract_plain_text().strip().split(' ')
    uid = ''
    if len(msg[0]) == 9 and msg[0].isdigit():
        uid = msg[0]
        month = msg[1]
    else:
        month = msg[0]
    if month and not month.isdigit():
        await bot.send(ev,'月份是不是写错了呀，要阿拉伯数字哦',at_sender=True)
        return
    if not month:
        month = datetime.datetime.now().month
    qq = str(ev.user_id)
    if ev.message_type == 'guild':
        rm = str(ev.message)
    else:
        rm = str(ev.raw_message)
    match = re.search(r"\[CQ:at,qq=(.*)\]", rm)
    if match:
        uid = ''
        qq = str(match.group(1))
    if uid and not check_uid_by_qq(qq, uid):
        await bot.send(ev,'派蒙没有这个uid的绑定信息哦',at_sender=True)
        return
    if not uid:
        uid = get_uid_by_qq(qq)
        if not uid:
            await bot.send(ev,'你还没把信息绑定给派蒙哦',at_sender=True)
            return
    if len(uid) != 9 or not uid.isdigit():
        await bot.send(ev,f'uid {uid} 不合规,是不是打错了呀',at_sender=True)
        return
    cookie = await get_cookie(qq, uid, only_private = True, only_match_uid = True)
    update_last_query_to_qq(qq, uid)
    if not cookie:
        await bot.send(ev,'你没有绑定cookie或者cookie失效了噢！',at_sender=True)
    else:
        try:
            data = await get_monthinfo_data(uid, month, cookie)
            monthinfo_card = await draw_monthinfo_card(data)
            await bot.send(ev, monthinfo_card, at_sender=True)
        except Exception as e:
            await bot.send(ev, f'派蒙出现了问题：{e}',at_sender=True)
