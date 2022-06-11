import json
import re
import uuid
from typing import Union
from nonebot import on_command, require, get_bot
from nonebot.adapters.onebot.v11 import MessageEvent, Message, GroupMessageEvent
from nonebot.params import CommandArg
from .data_source import get_Info, get_Notification, check_token
from LittlePaimon.utils.decorator import exception_handler
from LittlePaimon.utils.file_handler import load_json, save_json
from LittlePaimon.utils.config import config
from LittlePaimon.utils.message_util import get_message_id

HELP_STR = '''
云原神相关功能
云原神 绑定/bind : 绑定云原神的token
云原神 信息/info: 查询云原神账户信息
'''.strip()


cloud_ys = on_command('mhyy', aliases={'云原神', 'mhyy'}, priority=16, block=True)
cloud_ys.__paimon_help__ = {
    "usage": "云原神",
    "introduce": "查询云原神账户信息, 绑定token进行签到",
    "priority": 99
}
scheduler = require('nonebot_plugin_apscheduler').scheduler
uuid = str(uuid.uuid4())


async def cloud_genshin_send(user_id, data):
    token = data['token']
    uuid = data['uuid']

    if await check_token(uuid, token):
        """ 签到云原神 """
        d1 = await get_Notification(uuid, token)
        """ 获取免费时间 """
        d2 = await get_Info(uuid, token)
        """ 解析签到返回信息 """
        signInfo = json.loads(d1['data']['list'][0]['msg'])
        if d2['data']['free_time']['free_time'] == '600':
            await get_bot().send_private_msg(user_id=user_id, message='免费签到时长已达上限,无法继续签到')
        elif not signInfo:
            await get_bot().send_private_msg(user_id=user_id, message=f'签到成功~ {signInfo["msg"]}: {signInfo["num"]}分钟')
    await get_bot().send_private_msg(user_id=user_id, message='token已过期,请重新自行抓包并绑定')


@cloud_ys.handle()
@exception_handler()
async def _(event: Union[GroupMessageEvent, MessageEvent], msg: Message = CommandArg(), uuid=uuid):
    param = msg.extract_plain_text().strip()
    user_id = str(event.user_id)
    data = load_json('user_data.json')

    action = re.search(r'(?P<action>(信息|info)|(绑定|bind))', param)

    if event.message_type == 'guild':
        await cloud_ys.finish('该功能不支持群组或频道推送哦~', at_sender=True)

    if str(get_message_id(event)) not in config.paimon_cloudys_group:
        await cloud_ys.finish(f'尚未在群 {str(get_message_id(event))} 开启本功能')

    if not param:
        await cloud_ys.finish('请输入具体指令或参数!', at_sender=True)
    else:
        if action.group('action') in ['绑定', 'bind']:
            match = re.search(r'oi=\d+', param.split(" ")[1])
            if match:
                uid = str(match.group()).split('=')[1]

            data[user_id] = {
                'uid': uid,
                'uuid': uuid,
                'token': param.split(" ")[1]
            }

            if scheduler.get_job('cloud_genshin_' + user_id):
                scheduler.remove_job("cloud_genshin_" + user_id)

            """ 保存数据 """
            save_json(data, 'user_data.json')
            """ 添加推送任务 """
            scheduler.add_job(
                func=cloud_genshin_send,
                trigger='cron',
                hour=0,
                id="cloud_genshin_" + user_id,
                args=(user_id, data[user_id]),
                misfire_grace_time=10
            )
            await cloud_ys.finish(f'[UID:{uid}]已绑定token, 将在每天0点为你自动签到!', at_sender=True)

        elif action.group('action') in ['信息', 'info']:

            token = data[user_id]['token']
            uid = data[user_id]['uid']
            uuid = data[user_id]['uuid']

            result = await get_Info(uuid, token)

            """ 米云币 """
            coins = result['data']['coin']['coin_num']
            """ 免费时间 """
            free_time = result['data']['free_time']['free_time']
            """ 畅玩卡 """
            card = result['data']['play_card']['short_msg']

            message = '======== UID: {0} ========\n' \
                      '剩余米云币: {1}\n' \
                      '剩余免费时间: {2}分钟\n' \
                      '畅玩卡状态: {3}'.format(uid, coins, free_time, card)
            await cloud_ys.finish(message)
        #elif action.group('action') in ['签到', 'sign']:

            #    token = data[user_id]['token']
            #    uuid = data[user_id]['uuid']

            #    if await check_token(uuid, token):
        #        d1 = await get_Notification(uuid, token)
        #        signInfo = json.loads(d1['data']['list'][0]['msg'])
        #        if not list(d1['data']['list']):
        #            await cloud_ys.finish('今天已签到了哦~', at_sender=True)
        #        elif signInfo:
        #            await cloud_ys.finish(f'签到成功~ {signInfo["msg"]}: {signInfo["num"]}分钟', at_sender=True)

        else:
            await cloud_ys.finish('参数错误！', at_sender=True)


for user_id, data in load_json('user_data.json').items():
    scheduler.add_job(
        func=cloud_genshin_send,
        trigger='cron',
        hour=0,
        id="cloud_genshin_" + user_id,
        args=(user_id, data),
        misfire_grace_time=10
    )
