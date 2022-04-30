import json
import os
import re
from typing import Union
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent
from ..utils.util import get_uid_in_msg
from .gacha_logs import get_data
from .get_img import get_gacha_log_img
from .api import toApi, checkApi

__usage__ = '''
1.[获取抽卡记录 (uid) (url)]提供url，获取原神抽卡记录，需要一定时间
2.[查看抽卡记录 (uid)]查看抽卡记录分析
3.[导出抽卡记录 (uid) (xlsx/json)]导出抽卡记录文件，上传到群文件中
'''
__help_version__ = '0.9.0'


gacha_log_export = on_command('ckjldc', aliases={'抽卡记录导出', '导出抽卡记录'}, priority=5, block=True)
gacha_log_update = on_command('ckjlgx', aliases={'抽卡记录更新', '更新抽卡记录', '获取抽卡记录'}, priority=5, block=True)
gacha_log_show = on_command('ckjl', aliases={'抽卡记录', '查看抽卡记录'}, priority=5, block=True)

data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_data', 'gacha_log_data')
if not os.path.exists(data_path):
    os.makedirs(data_path)
if not os.path.exists(os.path.join(data_path, 'user_gacha_log.json')):
    with open(os.path.join(data_path, 'user_gacha_log.json'), 'w', encoding='UTF-8') as f:
        json.dump({}, f, ensure_ascii=False)


@gacha_log_export.handle()
async def ckjl(bot: Bot, event: Union[MessageEvent, GroupMessageEvent], msg: Message = CommandArg()):
    if event.message_type != 'group':
        await gacha_log_export.finish('在群聊中才能导出抽卡记录文件哦！')
    uid, msg, user_id, use_cache = await get_uid_in_msg(event, msg)
    if not uid:
        await gacha_log_export.finish('请把uid给派蒙哦，比如导出抽卡记录100000001 xlsx', at_sender=True)
    find_filetype = r'(?P<filetype>xlsx|json)'
    match = re.search(find_filetype, msg)
    filetype = match.group('filetype') if match else 'xlsx'
    if filetype == 'xlsx':
        filetype = f'gachaExport-{uid}.xlsx'
    else:
        filetype = f'UIGF_gachaData-{uid}.json'
    local_data = os.path.join(data_path, filetype)
    if not os.path.exists(local_data):
        await gacha_log_export.finish('你在派蒙这里还没有抽卡记录哦，使用 更新抽卡记录 吧！', at_sender=True)
    else:
        await bot.upload_group_file(group_id=event.group_id, file=local_data, name=filetype)


@gacha_log_update.handle()
async def update_ckjl(event: MessageEvent, msg: Message = CommandArg()):
    uid, msg, user_id, use_cache = await get_uid_in_msg(event, msg)
    if not uid:
        await gacha_log_update.finish('请把uid给派蒙哦，比如获取抽卡记录100000001 链接', at_sender=True)
    if msg:
        match = re.search(r'(https://webstatic.mihoyo.com/.*#/log)', msg)
        if match:
            url = str(match.group(1))
        else:
            await gacha_log_update.finish('你这个抽卡链接不对哦，应该是以https://开头、#/log结尾的！', at_sender=True)
    else:
        with open(os.path.join(data_path, 'user_gacha_log.json'), 'r', encoding="utf-8") as f:
            user_data = json.load(f)
            if user_id in user_data and uid in user_data[user_id]:
                url = user_data[user_id][uid]
                await gacha_log_update.send('发现历史抽卡记录链接，尝试使用...')
            else:
                await gacha_log_update.finish('拿到游戏抽卡记录链接后，对派蒙说[获取抽卡记录 uid 链接]就可以啦\n获取抽卡记录链接的方式和vx小程序的是一样的，还请旅行者自己搜方法',
                                              at_sender=True)
    with open(os.path.join(data_path, 'user_gacha_log.json'), 'r', encoding="utf-8") as f:
        user_data = json.load(f)
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id][uid] = url
    with open(os.path.join(data_path, 'user_gacha_log.json'), 'w', encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, sort_keys=False, indent=4)

    url = toApi(url)
    apiRes = await checkApi(url)
    if apiRes != 'OK':
        await gacha_log_update.finish(apiRes, at_sender=True)
    await gacha_log_update.send('抽卡记录开始获取，请给派蒙一点时间...')
    await get_data(url)

    local_data = os.path.join(data_path, f'gachaData-{uid}.json')
    with open(local_data, 'r', encoding="utf-8") as f:
        gacha_data = json.load(f)
    gacha_img = await get_gacha_log_img(gacha_data, 'all')
    await gacha_log_update.finish(gacha_img, at_sender=True)


@gacha_log_show.handle()
async def get_ckjl(event: MessageEvent, msg: Message = CommandArg()):
    uid, msg, user_id, use_cache = await get_uid_in_msg(event, msg)
    if not uid:
        await gacha_log_update.finish('请把uid给派蒙哦，比如获取抽卡记录100000001 链接', at_sender=True)
    match = re.search(r'(all|角色|武器|常驻|新手)', msg)
    pool = match.group(1) if match else 'all'
    local_data = os.path.join(data_path, f'gachaData-{uid}.json')
    if not os.path.exists(local_data):
        await gacha_log_update.finish('你在派蒙这里还没有抽卡记录哦，对派蒙说 获取抽卡记录 吧！', at_sender=True)
    with open(local_data, 'r', encoding="utf-8") as f:
        gacha_data = json.load(f)
    gacha_img = await get_gacha_log_img(gacha_data, pool)
    await gacha_log_update.finish(gacha_img, at_sender=True)
