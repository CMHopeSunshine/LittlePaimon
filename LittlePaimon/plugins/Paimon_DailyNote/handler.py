import asyncio
import datetime
import random
import re
import time

import pytz
from nonebot import get_bot
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg, Depends

from LittlePaimon.config import config
from LittlePaimon.database import DailyNoteSub, Player, LastQuery
from LittlePaimon.utils import logger, scheduler
from LittlePaimon.utils.api import get_mihoyo_private_data
from .draw import draw_daily_note_card


def SubList() -> dict:
    async def _sub(msg: Message = CommandArg()):
        msg = msg.extract_plain_text().strip()
        subs = {}
        if s := re.findall(r'(树脂|体力|尘歌壶|银币|钱币|壶币)(\d*)', msg):
            for name, num in s:
                if name in ['尘歌壶', '银币', '壶币', '钱币']:
                    subs['coin_num'] = int(num or 2400)
                if name in ['树脂', '体力']:
                    subs['resin_num'] = int(num or 160)
        elif num := re.search(r'(\d+)', msg):
            subs['resin_num'] = int(num[1])
        else:
            subs['resin_num'] = 160
        return subs

    return Depends(_sub)


async def get_subs(**kwargs) -> str:
    subs = await DailyNoteSub.get_or_none(**kwargs)
    result = ''
    if subs.resin_num:
        result += f'树脂达到{subs.resin_num}，'
    if subs.coin_num:
        result += f'银币达到{subs.coin_num}，'
    return f'会在{result.strip("，")}时向你发送提醒' if result else '当前没有订阅'


async def handle_ssbq(player: Player):
    await LastQuery.update_last_query(player.user_id, player.uid)
    data = await get_mihoyo_private_data(player.uid, player.user_id, 'daily_note')
    if isinstance(data, str):
        logger.info('原神实时便签', '➤', {'用户': player.user_id, 'UID': player.uid}, f'获取数据失败, {data}', False)
        return f'{player.uid}{data}\n'
    elif data['retcode'] == 1034:
        logger.info('原神实时便签', '➤', {'用户': player.user_id, 'UID': player.uid},
                    '获取数据失败，状态码为1034，疑似验证码', False)
        return f'{player.uid}遇验证码阻拦，需手动前往米游社进行验证后才能继续使用\n'
    elif data['retcode'] != 0:
        logger.info('原神实时便签', '➤', {'用户': player.user_id, 'UID': player.uid},
                    f'获取数据失败，code为{data["retcode"]}， msg为{data["message"]}', False)

        return f'{player.uid}获取数据失败，msg为{data["message"]}\n'
    else:
        logger.info('原神实时便签', '➤', {'用户': player.user_id, 'UID': player.uid}, '获取数据成功', True)

        try:
            img = await draw_daily_note_card(data['data'], player.uid)
            logger.info('原神实时便签', '➤➤', {'用户': player.user_id, 'UID': player.uid}, '绘制图片成功', True)

            return img
        except Exception as e:
            logger.info('原神实时便签', '➤➤', {'用户': player.user_id, 'UID': player.uid}, f'绘制图片失败，{e}', False)

            return f'{player.uid}绘制图片失败，{e}\n'


@scheduler.scheduled_job('cron', minute=f'*/{config.ssbq_check}', misfire_grace_time=10)
async def check_note():
    if not config.ssbq_enable:
        return
    # 特定时间段不做检查
    if config.ssbq_begin <= datetime.datetime.now().hour <= config.ssbq_end:
        return
    if not (subs := await DailyNoteSub.all()):
        return
    time_now = time.time()
    logger.info('原神实时便签', f'开始执行定时检查，共<m>{len(subs)}</m>个任务，预计花费<m>{round(6 * len(subs) / 60, 2)}</m>分钟')
    for sub in subs:
        limit_num = 5 if sub.resin_num and sub.coin_num else 3
        if sub.today_remind_num <= limit_num and (
                sub.last_remind_time is None or (sub.last_remind_time is not None and (
                sub.last_remind_time + datetime.timedelta(minutes=30) <= datetime.datetime.now().replace(
                tzinfo=pytz.timezone('Asia/Shanghai'))))):
            data = await get_mihoyo_private_data(sub.uid, str(sub.user_id), 'daily_note')
            if isinstance(data, str):
                logger.info('原神实时便签', '➤', {'用户': sub.user_id, 'UID': sub.uid}, 'Cookie未绑定或已失效，删除任务', False)
                try:
                    if sub.remind_type == 'group':
                        await get_bot().send_group_msg(group_id=sub.group_id,
                                                       message=f'[CQ:at,qq={sub.user_id}]你的UID{sub.uid}️未绑定Cookie或已失效，无法继续为你检查实时便签')
                    else:
                        await get_bot().send_private_msg(user_id=sub.user_id,
                                                         message=f'你的UID{sub.uid}未绑定Cookie或已失效，无法继续为你检查实时便签')
                except Exception as e:
                    logger.info('原神实时便签', '➤➤', {'用户': sub.user_id, 'UID': sub.uid}, f'发送提醒失败，{e}', False)
                await sub.delete()
            elif data['retcode'] == 1034:
                logger.info('原神实时便签', '➤', {'用户': sub.user_id, 'UID': sub.uid},
                            '获取数据失败，状态码为1034， 疑似验证码', False)
            elif data['retcode'] != 0:
                logger.info('原神实时便签', '➤', {'用户': sub.user_id, 'UID': sub.uid},
                            f'获取数据失败，状态码为{data["retcode"]}， msg为{data["message"]}', False)
            else:
                result = result_log = ''
                if sub.resin_num is not None and data['data']['current_resin'] > sub.resin_num:
                    result += f'树脂达到了{str(data["data"]["current_resin"])}，'
                    result_log += '树脂'
                if sub.coin_num is not None and data['data']['current_home_coin'] > sub.coin_num:
                    result += f'银币达到了{str(data["data"]["current_home_coin"])}，'
                    result_log += '银币'
                if result_log:
                    logger.info('原神实时便签', '➤', {'用户': sub.user_id, 'UID': sub.uid}, f'{result_log}达到了阈值，发送提醒', True)
                else:
                    logger.info('原神实时便签', '➤➤', {'用户': sub.user_id, 'UID': sub.uid}, '检查完成，未达到阈值', True)
                if result:
                    sub.last_remind_time = datetime.datetime.now()
                    sub.today_remind_num += 1
                    await sub.save()
                    try:
                        if sub.remind_type == 'group':
                            await get_bot().send_group_msg(group_id=sub.group_id,
                                                           message=f'[CQ:at,qq={sub.user_id}]⚠️你的UID{sub.uid}{result}记得清理哦⚠️')
                        else:
                            await get_bot().send_private_msg(user_id=sub.user_id,
                                                             message=f'⚠️你的UID{sub.uid}{result}记得清理哦⚠️')
                    except Exception as e:
                        logger.info('原神实时便签', '➤➤', {'用户': sub.user_id, 'UID': sub.uid}, f'发送提醒失败，{e}', False)
                # 等待一会再检查下一个，防止检查过快
                await asyncio.sleep(random.randint(4, 8))
    logger.info('原神实时便签', f'树脂检查完成，共花费<m>{round((time.time() - time_now) / 60, 2)}</m>分钟')
