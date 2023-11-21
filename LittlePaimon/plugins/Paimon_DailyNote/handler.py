import asyncio
import datetime
import random
import re
import time

import nonebot
import pytz
from nonebot import get_bot
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg, Depends

from LittlePaimon.config import config
from LittlePaimon.database import DailyNoteSub, Player, LastQuery, PrivateCookie
from LittlePaimon.utils import logger, scheduler
from LittlePaimon.utils.api import get_mihoyo_private_data, mihoyo_headers, get_cookie, DAILY_NOTE_API, \
    mihoyo_sign_headers, mihoyo_verify_verification_headers
from .draw import draw_daily_note_card
from ...utils.requests import aiorequests


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


async def geetest_verify_verification(api: str, cookie: str, validate: dict):
    geetest_challenge = validate['challenge']
    geetest_seccode = validate['seccode']
    geetest_validate = validate['validate']
    body = {
        "geetest_challenge": geetest_challenge,
        "geetest_seccode": geetest_seccode,
        "geetest_validate": geetest_validate
    }
    header = mihoyo_verify_verification_headers(cookie=cookie, request_body=body)
    url = api + "/game_record/app/card/wapi/verifyVerification"
    resp = await aiorequests.post(url=url, headers=header, json=body)
    return resp.json()


async def geetest_create_verification(api: str, cookie: str):
    url = api + "/game_record/app/card/wapi/createVerification?is_high=true"
    header = mihoyo_headers(cookie=cookie, q="is_high=true")
    result = await aiorequests.get(url=url, headers=header)
    return result.json()


async def geetest_handle_init(api_key: str,
                              api_endpoint: str,
                              gt: str,
                              challenge: str,
                              page_url: str):
    # TODO: Please modify this function according to the captcha resolver you are using
    raise NotImplementedError


async def geetest_handle(user_id: str, uid: str, ssbq_data: dict):
    global_config = nonebot.get_driver().config
    captcha_enable = global_config.captcha_enabled
    superuser = global_config.superusers
    if not captcha_enable:
        if user_id not in superuser:
            logger.warning('原神实时便签', '➤', '非特权用户试图绕过验证码失败：未开启验证码绕过')
            return 1, f'服务器返回1034，疑似验证码。请联系管理员开启验证码绕过程序。'
        else:
            logger.warning('原神实时便签', '➤', '特权用户试图绕过验证码失败：未开启验证码绕过')
            return 1, f'服务器返回1034，疑似验证码，请配置验证码绕过程序。'
    cookie_info = await get_cookie(user_id=user_id, uid=uid, check=True)
    if not cookie_info:
        logger.warning('原神实时便签', '➤', '用户试图绕过验证码失败：cookie失效')
        return 1, f'当前uid{uid}cookie已失效，请使用[原神扫码绑定]/[ysb]绑定私人cookie/联系管理员添加私人cookie或公共cookie'
    api_endpoint = 'https://api-takumi-record.mihoyo.com'
    geetest_create = await geetest_create_verification(api=api_endpoint, cookie=cookie_info.cookie)
    captcha_api_endpoint = ""
    captcha_api_key = global_config.captcha_api_key
    gt = geetest_create['data']['gt']
    challenge = geetest_create['data']['challenge']
    page_url = "https://webstatic.mihoyo.com/app/community-game-records/"
    token, err_message = await geetest_handle_init(api_key=captcha_api_key,
                                                  api_endpoint=captcha_api_endpoint,
                                                  gt=gt,
                                                  challenge=challenge,
                                                  page_url=page_url)
    if err_message != "":
        logger.warning('原神实时便签', '➤', f'用户试图绕过验证码失败：打码平台返回错误{err_message}')
        return 1, f'{uid}查询实时便签失败，米哈游服务器返回1034疑似验证码，绕过验证码失败：{err_message}'
    geetest_verify = await geetest_verify_verification(api=api_endpoint, validate=token, cookie=cookie_info.cookie)
    if geetest_verify['retcode'] != 0:
        logger.warning('原神实时便签', '➤',
                       f'用户试图绕过验证码失败：米哈游服务器返回验证码结果{geetest_verify["message"]}')
        return 1, f'{uid}查询实时便签失败，米哈游服务器返回1034疑似验证码，绕过验证码失败：米哈游服务器返回验证码结果{geetest_verify["message"]}'
    return 0, challenge


async def handle_ssbq(player: Player):
    await LastQuery.update_last_query(player.user_id, player.uid)
    data = await get_mihoyo_private_data(player.uid, player.user_id, 'daily_note')
    if isinstance(data, str):
        logger.info('原神实时便签', '➤', {'用户': player.user_id, 'UID': player.uid}, f'获取数据失败, {data}', False)
        return f'{player.uid}{data}\n'
    elif data['retcode'] == 1034:
        logger.info('原神实时便签', '➤', {'用户': player.user_id, 'UID': player.uid},
                    '获取数据失败，状态码为1034，疑似验证码', False)
        status, result = await geetest_handle(user_id=player.user_id, uid=player.uid, ssbq_data=data)
        if status == 0:
            data = await get_mihoyo_private_data(uid=player.uid, user_id=player.user_id, mode='daily_note',
                                                 geetest_challenge=result)
            logger.info('原神实时便签', '➤', {'用户': player.user_id, 'UID': player.uid}, '获取数据成功', True)
            try:
                img = await draw_daily_note_card(data['data'], player.uid)
                logger.info('原神实时便签', '➤➤', {'用户': player.user_id, 'UID': player.uid}, '绘制图片成功', True)
                return img
            except Exception as e:
                logger.info('原神实时便签', '➤➤', {'用户': player.user_id, 'UID': player.uid}, f'绘制图片失败，{e}',
                            False)
                return f'{player.uid}绘制图片失败，{e}\n'
        else:
            return result
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
    logger.info('原神实时便签',
                f'开始执行定时检查，共<m>{len(subs)}</m>个任务，预计花费<m>{round(6 * len(subs) / 60, 2)}</m>分钟')
    for sub in subs:
        limit_num = 5 if sub.resin_num and sub.coin_num else 3
        if sub.today_remind_num <= limit_num and (
                sub.last_remind_time is None or (sub.last_remind_time is not None and (
                sub.last_remind_time + datetime.timedelta(minutes=30) <= datetime.datetime.now().replace(
                tzinfo=pytz.timezone('Asia/Shanghai'))))):
            data = await get_mihoyo_private_data(sub.uid, str(sub.user_id), 'daily_note')
            if isinstance(data, str):
                logger.info('原神实时便签', '➤', {'用户': sub.user_id, 'UID': sub.uid}, 'Cookie未绑定或已失效，删除任务',
                            False)
                try:
                    if sub.remind_type == 'group':
                        await get_bot().send_group_msg(group_id=sub.group_id,
                                                       message=f'[CQ:at,qq={sub.user_id}]你的UID{sub.uid}️未绑定Cookie'
                                                               f'或已失效，无法继续为你检查实时便签')
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
                    logger.info('原神实时便签', '➤', {'用户': sub.user_id, 'UID': sub.uid},
                                f'{result_log}达到了阈值，发送提醒', True)
                else:
                    logger.info('原神实时便签', '➤➤', {'用户': sub.user_id, 'UID': sub.uid}, '检查完成，未达到阈值',
                                True)
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
                        logger.info('原神实时便签', '➤➤', {'用户': sub.user_id, 'UID': sub.uid}, f'发送提醒失败，{e}',
                                    False)
                # 等待一会再检查下一个，防止检查过快
                await asyncio.sleep(random.randint(4, 8))
    logger.info('原神实时便签', f'树脂检查完成，共花费<m>{round((time.time() - time_now) / 60, 2)}</m>分钟')
