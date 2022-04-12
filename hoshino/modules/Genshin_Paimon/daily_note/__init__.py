import json,os,re
from hoshino import R,MessageSegment,logger, Service
from hoshino.typing import CQEvent, Message
from hoshino.util import filt_message
from ..util import get_uid_in_msg
from ..get_data import get_daily_note_data
from .get_img import draw_daily_note_card

help_msg='''
[ssbq/实时便签 (uid)]查询当前树脂、洞天宝钱、派遣状况等
*绑定私人cookie之后才能使用
'''
sv = Service('派蒙实时便签', bundle='派蒙', help_=help_msg)

@sv.on_prefix(('ssbq','实时便笺','实时便签'))
async def main(bot,ev):
    uid, msg, user_id, use_cache = await get_uid_in_msg(ev)
    try:
        data = await get_daily_note_data(uid)
        if isinstance(data, str):
            await bot.send(ev, data, at_sender=True)
        else:
            daily_note_card = await draw_daily_note_card(data, uid)
            await bot.send(ev, daily_note_card, at_sender=True)
    except Exception as e:
        await bot.send(ev, f'派蒙出现了问题：{e}',at_sender=True)
