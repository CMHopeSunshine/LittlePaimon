import random
import asyncio
from .api import get_sign_info,mihoyo_bbs_sign,get_validate,get_sign_list,SIGN_URL,get_pass_challenge,query_score
import time
from collections import defaultdict
from nonebot import get_bot
from LittlePaimon.database import MihoyoBBSSub,Player,PrivateCookie
from .config import config
from LittlePaimon.utils import logger, scheduler
from LittlePaimon.plugins.Paimon_DailyNote.draw import draw_daily_note_card
from LittlePaimon.utils.api import get_mihoyo_private_data,get_ds,get_cookie
from LittlePaimon.utils.requests import aiorequests

already = 0

# 签到函数
async def sign_in(user_id,uid) -> str:
    logger.info(f'[签到] {uid} 开始执行签到')
    cookie = await get_cookie(user_id, uid, True, True)
    if not cookie:
        return False ,'未绑定私人cookies，绑定方法二选一：\n1.通过米游社扫码绑定：\n请发送指令[原神扫码绑定]\n2.获取cookies的教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1\n获取后，使用[ysb cookie]指令绑定'
    # 获得签到信息
    sign_info = await get_sign_info(user_id,uid,cookie.cookie)
    # 获取签到列表
    sign_list = await get_sign_list()
    # 初步校验数据
    if sign_info and 'data' in sign_info and sign_info['data']:
        sign_info = sign_info['data']
    else:
        logger.info('米游社签到', '➤', {'用户': user_id, 'UID': uid}, '出错, 请检查Cookies是否过期！', False)
        return False ,'签到失败...请检查Cookies是否过期！'
    # 检测是否已签到
    if sign_info['is_sign']:
        logger.info('米游社签到', '➤', {'用户': user_id, 'UID': uid}, '今天已经签过了', True)
        global already
        already += 1
        getitem = sign_list['data']['awards'][int(sign_info['total_sign_day'])-1]['name']
        getnum = sign_list['data']['awards'][int(sign_info['total_sign_day'])-1]['cnt']
        get_im = f'签到获得{getitem}x{getnum}'
        sign_missed = sign_info['sign_cnt_missed']
        return True ,f'今日已签到!\n{get_im}\n本月漏签次数：{sign_missed}'
    # 实际进行签到
    Header = {}
    for index in range(4):
        # 进行一次签到
        sign_data = await mihoyo_bbs_sign(user_id=user_id,uid=uid, Header=Header)
        # 检测数据
        if (
            sign_data
            and 'data' in sign_data
            and sign_data['data']
            and 'risk_code' in sign_data['data']
        ):
            # 出现校验码
            if sign_data['data']['risk_code'] == 375:
                logger.info('米游社[验证]签到', '➤', {'用户': user_id, 'UID': uid}, f'该用户出现校验码，开始尝试进行验证...，开始重试第 {index + 1} 次！', True)
                gt = sign_data['data']['gt']
                challenge = sign_data['data']['challenge']
                validate,challeng = get_validate(gt, challenge,SIGN_URL)
                if validate != 'j' and challeng != 'j':
                    delay = 50 + random.randint(1, 50)
                    Header['x-rpc-challenge'] = challeng
                    Header['x-rpc-validate'] = validate
                    Header['x-rpc-seccode'] = f'{validate}|jordan'
                    logger.info('米游社[验证]签到', '➤', {'用户': user_id, 'UID': uid}, f'已获取验证码, 等待时间{delay}秒', True)
                    await asyncio.sleep(delay)
                else:
                    delay = 600 + random.randint(1, 60)
                    logger.info('米游社签到', '➤', {'用户': user_id, 'UID': uid}, f'未获取验证码,等待{delay}秒后重试...', False)
                    await asyncio.sleep(delay)
                continue
            # 成功签到!
            else:
                if index == 0:
                    logger.info('米游社签到', '➤', {'用户': user_id, 'UID': uid}, f'该用户无校验码!', True)
                    result ='[无验证]'
                else:
                    logger.info('米游社[验证]签到', '➤', {'用户': user_id, 'UID': uid}, f'该用户重试 {index} 次验证成功!', True)
                    result ='[有验证]'
                break
        # 重试超过阈值
        else:
            logger.info('米游社[验证]签到', '➤', {'用户': user_id, 'UID': uid}, f'超过请求阈值...', False)
            return False , '签到失败...请求失败!\n请过段时间使用签到或手动至米游社进行签到'
    # 签到失败
    else:
        result = '签到失败!'
        logger.info('米游社签到', '➤', {'用户': user_id, 'UID': uid}, f'签到失败, 结果: {result}', False)
        return False, result
    # 获取签到列表
    status = sign_data['message']
    getitem = sign_list['data']['awards'][int(sign_info['total_sign_day'])]['name']
    getnum = sign_list['data']['awards'][int(sign_info['total_sign_day'])]['cnt']
    get_im = f'本次签到获得{getitem}x{getnum}'
    new_sign_info = await get_sign_info(user_id,uid,cookie.cookie)
    new_sign_info = new_sign_info['data']
    if new_sign_info['is_sign']:
        mes_im = '签到成功'
    else:
        result = f'签到失败, 状态为:{status}'
        return False, result
    sign_missed = sign_info['sign_cnt_missed']
    result = f'{mes_im}{result}!\n{get_im}\n本月漏签次数：{sign_missed}'
    logger.info('米游社签到', '➤', {'用户': user_id, 'UID': uid}, f'签到完成, 结果: {mes_im}, 漏签次数: {sign_missed}', True)
    return True, result

@scheduler.scheduled_job('cron', hour=config.enable_hour, minute=config.enable_minute,
                         misfire_grace_time=10)
async def _():
    await bbs_auto_sign()

async def bbs_auto_sign():
    """
    指定时间，执行所有米游社原神签到任务
    """
    if not config.enable:
        return
    t = time.time()  # 计时用
    subs = await MihoyoBBSSub.filter(sub_event='米游社验证签到').all()
    if not subs:
        # 如果没有米游社原神签到订阅，则不执行签到任务
        return
    coin_result_group = defaultdict(list)
    for sub in subs:
        im, result = await sign_in(str(sub.user_id), sub.uid)
        result =result if im else f'UID{sub.uid}{result}'
        if sub.user_id != sub.group_id:
            coin_result_group[sub.group_id].append({
                'user_id': sub.user_id,
                'uid': sub.uid,
                'result': '失败' not in result and 'Cookies' not in result
            })
        await asyncio.sleep(random.randint(15, 25))
    if config.vaapikai:
        jifen = '第三方验证'
    else:    
        _,jifen = query_score()
    for group_id, result_list in coin_result_group.items():
        result_num = len(result_list)
        if result_fail := len([result for result in result_list if not result['result']]):
            fails = '\n'.join(result['uid'] for result in result_list if not result['result'])
            msg = f'本群米游社签到共{result_num}个任务，{jifen}，其中成功{result_num - result_fail}个，失败{result_fail}个，失败的UID列表：\n{fails}'
        else:
            msg = f'本群米游社签到共{result_num}个任务，{jifen}，已全部完成'
        try:
            await get_bot().send_group_msg(group_id=int(group_id), message=msg)
        except Exception as e:
            logger.info('米游社签到', '➤➤', {'群': group_id}, f'发送结果失败: {e}', False)
        await asyncio.sleep(random.randint(3, 6))

    logger.info('米游社签到', f'获取完成，共花费<m>{round((time.time() - t) / 60, 2)}</m>分钟')

def mihoyo_headers(cookie,challenge, q='', b=None) -> dict:
    return {
        'DS':                get_ds(q, b),
        'Origin':            'https://webstatic.mihoyo.com',
        'Cookie':            cookie,
        'x-rpc-app_version': "2.11.1",
        'User-Agent':        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS '
                             'X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer':           'https://webstatic.mihoyo.com/',
        "x-rpc-challenge" :  challenge
    }

DAILY_NOTE_API = 'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/dailyNote'
async def handle_ssbq(player: Player):
    data = await get_mihoyo_private_data(player.uid, player.user_id, 'daily_note')
    if isinstance(data, str):
        logger.info('原神体力', '➤', {'用户': player.user_id, 'UID': player.uid}, f'获取数据失败, {data}', False)
        return f'{player.uid}{data}\n'
    elif data['retcode'] == 1034:
        logger.info('原神体力', '➤', {'用户': player.user_id, 'UID': player.uid},'获取数据失败，状态码为1034，疑似验证码', False)
        challenge = await get_pass_challenge(player.uid, player.user_id)
        logger.info('原神体力', '➤', {'用户': player.user_id, 'UID': player.uid},'成功获取challenge', True)
        if challenge is not None:
            server_id = 'cn_qd01' if player.uid[0] == '5' else 'cn_gf01'
            #cookie_info = await PrivateCookie.get_or_none(user_id=player.user_id, uid=player.uid)
            cookie_info = await get_cookie(player.user_id, player.uid, True, True)
            res = await aiorequests.get(url=DAILY_NOTE_API,
                                    headers=mihoyo_headers(q=f'role_id={player.uid}&server={server_id}',
                                                        cookie=cookie_info.cookie,challenge=challenge),
                                    params={
                                        "server":  server_id,
                                        "role_id": player.uid
                                    })
            data = res.json()
            try:
                img = await draw_daily_note_card(data['data'], player.uid)
                logger.info('原神体力', '➤➤', {'用户': player.user_id, 'UID': player.uid}, '绘制图片成功', True)
                return img
            except Exception as e:
                logger.info('原神体力', '➤➤', {'用户': player.user_id, 'UID': player.uid}, f'绘制图片失败，{e}', False)
                return f'{player.uid}绘制图片失败，{e}'
        else:
            return f'{player.uid}无法越过验证码'
    elif data['retcode'] != 0:
        logger.info('原神体力', '➤', {'用户': player.user_id, 'UID': player.uid},
                    f'获取数据失败，code为{data["retcode"]}， msg为{data["message"]}', False)
        return f'{player.uid}获取数据失败，msg为{data["message"]}\n'
    else:
        logger.info('原神体力', '➤', {'用户': player.user_id, 'UID': player.uid}, '获取数据成功', True)
        try:
            img = await draw_daily_note_card(data['data'], player.uid)
            logger.info('原神体力', '➤➤', {'用户': player.user_id, 'UID': player.uid}, '绘制图片成功', True)
            return img
        except Exception as e:
            logger.info('原神体力', '➤➤', {'用户': player.user_id, 'UID': player.uid}, f'绘制图片失败，{e}', False)
            return f'{player.uid}绘制图片失败，{e}'