import asyncio
import random
from collections import defaultdict

from nonebot import get_bot

from LittlePaimon.config import config
from LittlePaimon.database import CloudGenshinSub
from LittlePaimon.utils import scheduler, logger
from .api import get_Info, check_token, get_Notification


async def get_cloud_genshin_info(user_id: str, uid: str):
    if not (info := await CloudGenshinSub.get_or_none(user_id=user_id, uid=uid)):
        return f'你的UID{uid}还没有绑定云原神账户哦~请使用[云原神绑定]命令绑定账户'
    result = await get_Info(info.uuid, info.token)
    if result['retcode'] != 0:
        return '你的云原神token已失效，请重新绑定'
    coins = result['data']['coin']['coin_num']
    free_time = result['data']['free_time']['free_time']
    card = result['data']['play_card']['short_msg']
    return f'======== UID: {uid} ========\n' \
           f'剩余米云币: {coins}\n' \
           f'剩余免费时间: {free_time}分钟\n' \
           f'畅玩卡状态: {card}'


@scheduler.scheduled_job('cron', hour=config.cloud_genshin_hour, misfire_grace_time=10)
async def _():
    if not config.cloud_genshin_enable:
        return
    subs = await CloudGenshinSub.all()
    if not subs:
        return
    logger.info('云原神', f'开始执行云原神自动，共<m>{len(subs)}</m>个任务，预计花费<m>{round(75 * len(subs) / 60, 2)}</m>分钟')

    result_list = {
        'group':   defaultdict(list),
        'private': defaultdict(list)
    }
    for sub in subs:
        if await check_token(sub.uuid, sub.token):
            info = await get_Info(sub.uuid, sub.token)
            if info['data']['free_time']['free_time'] == 600:
                msg = '云原神签到失败，免费时长已达上限'
            else:
                sign = await get_Notification(sub.uuid, sub.token)
                msg = '云原神签到成功' if sign['data']['list'] else '云原神今日已签到'
            result_list['private' if sub.user_id == str(sub.group_id) else 'group'][str(sub.group_id)].append(
                {
                    'uid':    sub.uid,
                    'msg':    f'UID{sub.uid}{msg}',
                    'result': True
                })
        else:
            result_list['private' if sub.user_id == str(sub.group_id) else 'group'][str(sub.group_id)].append(
                {
                    'uid':    sub.uid,
                    'msg':    f'UID{sub.uid}云原神token已失效，请重新绑定',
                    'result': False
                })
        await asyncio.sleep(random.randint(3, 5))

    for group_id, result_list in result_list['group'].items():
        result_num = len(result_list)
        if result_fail := len([result for result in result_list if not result['result']]):
            fails = '\n'.join(result['uid'] for result in result_list if not result['result'])
            msg = f'本群云原神自动签到共{result_num}个任务，其中成功{result_num - result_fail}个，失败{result_fail}个，失败的UID列表：\n{fails}'
        else:
            msg = f'本群云原神自动签到共{result_num}个任务，已全部完成'
        try:
            await get_bot().send_group_msg(group_id=int(group_id), message=msg)
        except Exception as e:
            logger.info('云原神', '➤➤', {'群': group_id}, f'发送云原神自动结果失败: {e}', False)
        await asyncio.sleep(random.randint(3, 6))

    for user_id, result_list in result_list['private'].items():
        for result in result_list:
            try:
                await get_bot().send_private_msg(user_id=int(user_id), message=result['msg'])
            except Exception as e:
                logger.info('云原神', '➤➤', {'用户': user_id}, f'发送云原神自动结果失败: {e}', False)
            await asyncio.sleep(random.randint(3, 6))
