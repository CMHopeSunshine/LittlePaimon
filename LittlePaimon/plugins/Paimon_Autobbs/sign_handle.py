import asyncio
import datetime
import random
import time
from collections import defaultdict
from typing import Tuple, Union

import nonebot
from nonebot import get_bot

from LittlePaimon.config import config
from LittlePaimon.database import MihoyoBBSSub, LastQuery, PrivateCookie
from LittlePaimon.utils import logger, scheduler, DRIVER
from LittlePaimon.utils.api import get_mihoyo_private_data, get_sign_reward_list, mihoyo_sign_headers, check_retcode
from LittlePaimon.utils.requests import aiorequests
from .draw import SignResult, draw_result

SIGN_ACTION_API = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'
GEETEST_HEADER = {"Accept": "*/*",
                  "X-Requested-With": "com.mihoyo.hyperion",
                  "User-Agent": 'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) '
                                'Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36 miHoYoBBS/2.35.2',
                  "Referer": "https://webstatic.mihoyo.com/",
                  "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
                  }
sign_reward_list: dict = {}


async def sign_action(user_id: str, uid: str) -> Union[dict, str]:
    server_id = 'cn_qd01' if uid[0] == '5' else 'cn_gf01'
    cookie_info = await PrivateCookie.get_or_none(user_id=user_id, uid=uid)
    resp = await aiorequests.post(SIGN_ACTION_API, headers=mihoyo_sign_headers(cookie_info.cookie),
                                  json={
                                      'act_id': 'e202009291139501',
                                      'uid': uid,
                                      'region': server_id
                                  })
    data = resp.json()
    if await check_retcode(data, cookie_info, user_id, uid):
        return data
    else:
        return f'你的UID{uid}的cookie疑似失效了'


async def mhy_bbs_sign(user_id: str, uid: str) -> Tuple[SignResult, str]:
    """
    执行米游社原神签到，返回签到成功天数或失败原因
    :param user_id: 用户id
    :param uid: 原神uid
    :return: 签到成功天数或失败原因
    """
    await LastQuery.update_or_create(user_id=user_id,
                                     defaults={'uid': uid, 'last_time': datetime.datetime.now()})
    sign_info = await get_mihoyo_private_data(uid, user_id, 'sign_info')
    if isinstance(sign_info, str):
        logger.info('米游社原神签到', '➤', {'用户': user_id, 'UID': uid}, '未绑定私人cookie或已失效', False)
        await MihoyoBBSSub.filter(user_id=user_id, uid=uid).delete()
        return SignResult.INVALID, sign_info
    elif sign_info['data']['is_sign']:
        signed_days = sign_info['data']['total_sign_day'] - 1
        logger.info('米游社原神签到', '➤', {'用户': user_id, 'UID': uid}, '今天已经签过了', True)
        if sign_reward_list:
            return SignResult.DONE, f'UID{uid}今天已经签过了，获得的奖励为\n{sign_reward_list[signed_days]["name"]}*{sign_reward_list[signed_days]["cnt"]}'
        else:
            return SignResult.DONE, f'UID{uid}今天已经签过了'
    message = None
    for i in range(3):
        sign_data = await sign_action(user_id, uid)
        if isinstance(sign_data, str):
            logger.info('米游社原神签到', '➤', {'用户': user_id, 'UID': uid}, f'获取数据失败, {sign_data}', False)
            return SignResult.FAIL, f'{uid}签到失败，{sign_data}\n'
        elif sign_data['retcode'] == -5003:
            signed_days = sign_info['data']['total_sign_day'] - 1
            logger.info('米游社原神签到', '➤', {'用户': user_id, 'UID': uid}, '今天已经签过了', True)
            if sign_reward_list:
                return SignResult.DONE, f'UID{uid}今天已经签过了，获得的奖励为\n{sign_reward_list[signed_days]["name"]}*{sign_reward_list[signed_days]["cnt"]}'
            else:
                return SignResult.DONE, f'UID{uid}今天已经签过了'
        elif sign_data['retcode'] != 0:
            logger.info('米游社原神签到', '➤', {'用户': user_id, 'UID': uid},
                        f'获取数据失败，code为{sign_data["retcode"]}， msg为{sign_data["message"]}', False)
            return SignResult.FAIL, f'{uid}获取数据失败，签到失败，msg为{sign_data["message"]}\n'
        else:
            if sign_data['data']['success'] == 0:
                logger.info('米游社原神签到', '➤', {'用户': user_id, 'UID': uid}, '签到成功', True)
                signed_days = sign_info['data']['total_sign_day']
                if sign_reward_list:
                    return SignResult.SUCCESS, f'签到成功，获得的奖励为\n{sign_reward_list[signed_days]["name"]}*{sign_reward_list[signed_days]["cnt"]}'
                else:
                    return SignResult.SUCCESS, '签到成功'
            else:
                result, message = await geetest_verify(user_id=user_id, uid=uid, sign_data=sign_data)
                if result == SignResult.INVALID:
                    return SignResult.INVALID, f'{uid}签到失败，你的UID{uid}的cookie疑似失效了'
                elif result == SignResult.FAIL:
                    logger.warning('米游社原神签到', '➤', f'{uid}第{i}次签到失败，正在重试，报错信息：{message}')
                elif result == SignResult.SUCCESS:
                    return SignResult.SUCCESS, '签到成功'
                else:
                    logger.warning('米游社原神签到', '➤', f'{uid}第{i}次签到失败，正在重试，报错信息：{message}')
    return SignResult.FAIL, f'{uid}签到失败，报错信息{message}'


async def sign_action_after_geetest(user_id: str,
                                    uid: str,
                                    geetest_challenge: str,
                                    geetest_validate: str,
                                    geetest_seccode: str):
    server_id = 'cn_qd01' if uid[0] == '5' else 'cn_gf01'
    cookie_info = await PrivateCookie.get_or_none(user_id=user_id, uid=uid)
    headers = mihoyo_sign_headers(cookie_info.cookie)
    headers["x-rpc-validate"] = geetest_validate
    headers["x-rpc-challenge"] = geetest_challenge
    headers["x-rpc-seccode"] = geetest_seccode
    resp = await aiorequests.post(url=SIGN_ACTION_API, headers=headers,
                                  json={
                                      'act_id': 'e202009291139501',
                                      'uid': uid,
                                      'region': server_id
                                  })
    data = resp.json()
    if await check_retcode(data, cookie_info, user_id, uid):
        return data
    else:
        return f'你的UID{uid}的cookie疑似失效了'


async def geetest_verify(user_id: str, uid: str, sign_data: dict):
    global_config = nonebot.get_driver().config
    captcha_enable = global_config.captcha_enabled
    superuser = global_config.superusers
    if not captcha_enable:
        logger.info('米游社原神签到➤',
                    '未开启验证码绕过，请添加captcha_api_key并根据需求修改geetest_verify(), sign_action_after_geetest(), '
                    'geetest_handle_init(), 以及geetest_handle_finish()函数')
        if user_id not in superuser:
            return SignResult.FAIL, f'{uid}签到失败，请联系管理员检查后台日志并开启验证码绕过'
        else:
            return SignResult.FAIL, f'{uid}签到失败，请检查后台日志开启验证码绕过'
    api_key = global_config.captcha_api_key
    api_endpoint = global_config.captcha_api_endpoint
    gt = sign_data['data']['gt']
    challenge = sign_data['data']['challenge']
    page_url = f'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id' \
               f'=e202009291139501&ltuid={uid}'
    token, err_message = await geetest_handle_init(api_key=api_key, gt=gt, challenge=challenge,
                                                  page_url=page_url, api_endpoint=api_endpoint)
    if err_message == "":
        sign_result = await sign_action_after_geetest(user_id=user_id,
                                                      uid=uid,
                                                      geetest_challenge=token['challenge'],
                                                      geetest_seccode=token['seccode'],
                                                      geetest_validate=token['validate'])
        if sign_result == f'你的UID{uid}的cookie疑似失效了':
            return SignResult.INVALID, f'你的UID{uid}的cookie疑似失效了'
        else:
            return SignResult.SUCCESS, '签到成功'
    else:
        return SignResult.FAIL, f'{uid}平台返回错误{err_message}'


async def geetest_handle_init(api_key: str,
                              api_endpoint: str,
                              gt: str,
                              challenge: str,
                              page_url: str):
    # TODO: Please modify this function according to the captcha resolver you are using
    raise NotImplementedError

@scheduler.scheduled_job('cron', hour=config.auto_sign_hour, minute=config.auto_sign_minute,
                         misfire_grace_time=10)
async def _():
    await bbs_auto_sign()


async def bbs_auto_sign():
    """
    指定时间，执行所有米游社原神签到任务， 并将结果分群绘图发送
    """
    if not config.auto_sign_enable:
        return
    t = time.time()  # 计时用
    subs = await MihoyoBBSSub.filter(sub_event='米游社原神签到').all()
    if not subs:
        # 如果没有米游社原神签到订阅，则不执行签到任务
        return
    logger.info('米游社原神签到',
                f'开始执行米游社自动签到，共<m>{len(subs)}</m>个任务，预计花费<m>{len(subs) * 2}</m>分钟')
    sign_result_group = defaultdict(list)
    sign_result_private = defaultdict(list)
    for sub in subs:
        result, msg = await mhy_bbs_sign(str(sub.user_id), sub.uid)  # 执行签到
        # 将签到结果分群或个人添加到结果列表中
        if sub.user_id != sub.group_id:
            sign_result_group[sub.group_id].append({
                'user_id': sub.user_id,
                'uid': sub.uid,
                'result': result,
                'reward': msg.split('\n')[-1] if result in [SignResult.SUCCESS, SignResult.DONE] else ''
            })
        else:
            sign_result_private[sub.user_id].append({
                'uid': sub.uid,
                'result': result,
                'reward': msg.split('\n')[-1] if result in [SignResult.SUCCESS, SignResult.DONE] else ''
            })
        if result == SignResult.DONE:
            await asyncio.sleep(random.randint(5, 10))
        else:
            await asyncio.sleep(random.randint(60, 90))

    for group_id, sign_result in sign_result_group.items():
        # 发送签到结果到群
        img = await draw_result(group_id, sign_result)
        try:
            await get_bot().send_group_msg(group_id=int(group_id), message=img)
        except Exception as e:
            logger.info('米游社原神签到', '➤➤', {'群': group_id}, f'发送签到结果失败: {e}', False)
        await asyncio.sleep(random.randint(3, 6))

    for user_id, sign_result in sign_result_private.items():
        for result in sign_result:
            try:
                await get_bot().send_private_msg(user_id=int(user_id),
                                                 message=f'你的UID{result["uid"]}签到'
                                                         f'{"成功" if result["result"] != SignResult.FAIL else "失败"}'
                                                         f'{"" if result["result"] == SignResult.FAIL else "，获得奖励：" + result["reward"]}')
            except Exception as e:
                logger.info('米游社原神签到', '➤➤', {'用户': user_id}, f'发送签到结果失败: {e}', False)
        await asyncio.sleep(random.randint(3, 6))

    logger.info('米游社原神签到', f'签到完成，共花费<m>{round((time.time() - t) / 60, 2)}</m>分钟')


@DRIVER.on_startup
async def init_reward_list():
    """
    初始化签到奖励列表
    """
    global sign_reward_list
    try:
        sign_reward_list = await get_sign_reward_list()
        sign_reward_list = sign_reward_list['data']['awards']
    except Exception:
        logger.info('米游社原神签到', '初始化签到奖励列表<r>失败</r>')
