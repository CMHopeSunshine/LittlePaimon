import re
from hoshino import Service
from ..util import get_uid_in_msg
from ..get_data import get_daily_note_data
from .get_img import draw_daily_note_card
from ..db_util import update_note_remind2, update_note_remind, get_note_remind, delete_note_remind, update_day_remind_count
from hoshino import get_bot, logger
from datetime import datetime, timedelta
from asyncio import sleep

help_msg='''
[ssbq/实时便签 (uid)]查询当前树脂、洞天宝钱、派遣状况等
[ssbq (uid) 开启提醒(树脂数)/关闭提醒]开启/关闭树脂提醒，达到树脂数时会在群里艾特你
*绑定私人cookie之后才能使用
'''
sv = Service('派蒙实时便签', bundle='派蒙', help_=help_msg)

@sv.on_prefix(('ssbq','实时便笺','实时便签'))
async def main(bot,ev):
    uid, msg, user_id, use_cache = await get_uid_in_msg(ev)
    find_remind_enable = re.search(r'(?P<action>开启提醒|关闭提醒|删除提醒)((?P<num>\d{1,3})|(?:.*))', msg)
    if find_remind_enable:
        if find_remind_enable.group('action') == '开启提醒':
            if find_remind_enable.group('num'):
                await update_note_remind2(user_id, uid, str(ev.group_id), True, find_remind_enable.group('num'))
                await bot.send(ev, f'开启提醒成功,派蒙会在你的树脂达到{find_remind_enable.group("num")}时在群里提醒你的', at_sender=True)
            else:
                await update_note_remind2(user_id, uid, str(ev.group_id), True)
                await bot.send(ev, '开启提醒成功', at_sender=True)
        elif find_remind_enable.group('action') == '关闭提醒':
            await bot.send(ev, '关闭提醒成功', at_sender=True)
            await update_note_remind2(user_id, uid, str(ev.group_id), False)
        elif find_remind_enable.group('action') == '删除提醒':
            await bot.send(ev, '删除提醒成功', at_sender=True)
            await delete_note_remind(user_id, uid)
    else:
        try:
            data = await get_daily_note_data(uid)
            if isinstance(data, str):
                await bot.send(ev, data, at_sender=True)
            else:
                daily_note_card = await draw_daily_note_card(data, uid)
                await bot.send(ev, daily_note_card, at_sender=True)
        except Exception as e:
            await bot.send(ev, f'派蒙出现了问题：{e}',at_sender=True)

@sv.scheduled_job('cron', minute='*/8')
async def check_note():
    data = await get_note_remind()
    if data:
        now_time = datetime.now()
        logger.info('---派蒙开始检查实时便签树脂提醒---')
        for user_id, uid, count, remind_group, enable, last_remind_time, today_remind_count  in data:
            if last_remind_time:
                last_remind_time = datetime.strptime(last_remind_time, '%Y%m%d %H:%M:%S')
                if now_time - last_remind_time > timedelta(minutes=30):
                    time_e = True
                else:
                    time_e = False
            else:
                time_e = True
            if enable and ((today_remind_count and today_remind_count < 3) or not today_remind_count) and time_e:
                now_data = await get_daily_note_data(uid)
                if isinstance(now_data, str):
                    try:                    
                        await get_bot().send_group_msg(group_id=remind_group, message=f'[CQ:at,qq={user_id}]你的cookie失效了哦,派蒙没办法帮你检查树脂,先帮你删除了,请重新添加ck后再叫派蒙开启提醒')
                    except Exception as e:
                        logger.error(f'---派蒙发送树脂提醒失败:{e}---')
                else:
                    if now_data['data']['current_resin'] >= count:
                        logger.info(f'---用户{user_id}的uid{uid}的树脂已经达到阈值了,发送提醒---')
                        if today_remind_count:
                            today_remind_count += 1
                        else:
                            today_remind_count = 1
                        now_time_str = now_time.strftime('%Y%m%d %H:%M:%S')
                        try:
                            await update_note_remind(user_id, uid, count, remind_group, enable, now_time_str, today_remind_count)
                            await get_bot().send_group_msg(group_id=remind_group, message=f'[CQ:at,qq={user_id}]⚠️你的树脂已经达到了{now_data["data"]["current_resin"]}，派蒙30分钟后还会帮你检查⚠️')
                        except Exception as e:
                            logger.error(f'---派蒙发送树脂提醒失败:{e}---')
                await sleep(2)

@sv.scheduled_job('cron', hour='0')
async def delete_day_limit():
    logger.info('---清空今日树脂提醒限制---')
    await update_day_remind_count()