import json,os,re
from hoshino import R,MessageSegment,logger, Service
from hoshino.typing import CQEvent, Message
from ..util import get_uid_by_qq, update_last_query_to_qq
from .gacha_logs import get_data
from .get_img import get_gacha_log_img
from .api import toApi, checkApi

sv = Service('原神抽卡记录导出')

data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'user_data', 'gacha_log_data')
if not os.path.exists(data_path):
    os.makedirs(data_path)
if not os.path.exists(os.path.join(data_path, 'user_gacha_log.json')):
    with open(os.path.join(data_path, 'user_gacha_log.json'),'w',encoding='UTF-8') as f:
        json.dump({},f,ensure_ascii=False)

@sv.on_prefix('导出抽卡记录', 'dcckjl', 'exportgachalog')
async def ckjl(bot,ev):
    if ev.message_type != 'group':
        await bot.send(ev,'在群聊中才能导出抽卡记录文件哦！')
        return
    msg = ev.message.extract_plain_text().strip().split(' ')
    uid = ''
    if len(msg[0]) == 9 and msg[0].isdigit():
        uid = msg[0]
        if len(msg) >= 2:
            filetype = msg[1]
        else:
            filetype = 'xlsx'
    else:
        filetype = msg[0]
    if not filetype or filetype not in ['xlsx', 'json']:
        filetype = 'xlsx'
    qq = str(ev.user_id)
    if ev.message_type == 'guild':
        rm = str(ev.message)
    else:
        rm = str(ev.raw_message)
    match = re.search(r"\[CQ:at,qq=(.*)\]", rm)
    if match:
        uid = ''
        qq = str(match.group(1))
    if not uid:
        uid = get_uid_by_qq(qq)
        if not uid:
            await bot.send(ev,'请把uid给派蒙哦，比如抽卡记录导出100000001 xlsx',at_sender=True)
            return
    update_last_query_to_qq(qq, uid)
    if filetype == 'xlsx':
        filetype = f'gachaExport-{uid}.xlsx'
    else:
        filetype = f'UIGF_gachaData-{uid}.json'
    local_data = os.path.join(data_path, filetype)
    if not os.path.exists(local_data):
        await bot.send(ev, '你在派蒙这里还没有抽卡记录哦，使用 更新抽卡记录 吧！', at_sender=True)
        return
    await bot.upload_group_file(group_id=ev.group_id, file=local_data, name=filetype)

@sv.on_prefix(('更新抽卡记录', '获取抽卡记录', 'updategachalog', 'gxckjl'))
async def update_ckjl(bot,ev):
    msg = ev.message.extract_plain_text().strip().split(' ')
    uid = ''
    if len(msg[0]) == 9 and msg[0].isdigit():
        uid = msg[0]
        if len(msg) >= 2:
            url = msg[1]
        else:
            url = ''
    else:
        url = msg[0]
    qq = str(ev.user_id)
    if not uid:
        uid = get_uid_by_qq(qq)
        if not uid:
            await bot.send(ev,'请把uid给派蒙哦，比如获取抽卡记录100000001 链接',at_sender=True)
            return
    if url:
        match = re.search(r'(https://webstatic.mihoyo.com/.*#/log)', url)
        if match:
            url = str(match.group(1))
        else:
            await bot.send(ev,'你这个抽卡链接不对哦，应该是以https://开头、#/log结尾的！', at_sender=True)
            return
    else:
        with open(os.path.join(data_path, 'user_gacha_log.json'), 'r', encoding="utf-8") as f:
            user_data = json.load(f)
            if qq in user_data and uid in user_data[qq]:
                url = user_data[qq][uid]
                await bot.send(ev,'发现历史抽卡记录链接，尝试使用...')
            else:
                await bot.send(ev, '拿到游戏抽卡记录链接后，对派蒙说[获取抽卡记录 uid 链接]就可以啦\n获取抽卡记录链接的方式和vx小程序的是一样的，还请旅行者自己搜方法', at_sender=True)
                return
    with open(os.path.join(data_path, 'user_gacha_log.json'), 'r', encoding="utf-8") as f:
        user_data = json.load(f)
    if qq not in user_data:
        user_data[qq] = {}
    user_data[qq][uid] = url
    with open(os.path.join(data_path, 'user_gacha_log.json'), 'w', encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, sort_keys=False, indent=4)
    
    url = toApi(url)
    apiRes = await checkApi(url)
    if apiRes != 'OK':
        await bot.send(ev,apiRes,at_sender=True)
        return
    await bot.send(ev, '抽卡记录开始获取，请给派蒙一点时间...')
    await get_data(url)

    local_data = os.path.join(data_path, f'gachaData-{uid}.json')
    with open(local_data, 'r', encoding="utf-8") as f:
        gacha_data = json.load(f)
    gacha_img = await get_gacha_log_img(gacha_data, 'all')
    await bot.send(ev, gacha_img, at_sender=True)

@sv.on_prefix('查看抽卡记录', 'ckjl', 'gachalog')
async def get_ckjl(bot,ev):
    msg = ev.message.extract_plain_text().strip().split(' ')
    uid = ''
    if len(msg[0]) == 9 and msg[0].isdigit():
        uid = msg[0]
        if len(msg) >= 2:
            pool = msg[1]
        else:
            pool = 'all'
    else:
        pool = msg[0]
    if not pool or pool not in ['all', '角色', '武器', '常驻', '新手']:
        pool = 'all'
    qq = str(ev.user_id)
    if ev.message_type == 'guild':
        rm = str(ev.message)
    else:
        rm = str(ev.raw_message)
    match = re.search(r"\[CQ:at,qq=(.*)\]", rm)
    if match:
        uid = ''
        qq = str(match.group(1))
    if not uid:
        uid = get_uid_by_qq(qq)
        if not uid:
            await bot.send(ev,'请把uid给派蒙哦，比如抽卡记录100000001 all',at_sender=True)
            return
    update_last_query_to_qq(qq, uid)

    local_data = os.path.join(data_path, f'gachaData-{uid}.json')
    if not os.path.exists(local_data):
        await bot.send(ev, '你在派蒙这里还没有抽卡记录哦，对派蒙说 获取抽卡记录 吧！', at_sender=True)
        return
    with open(local_data, 'r', encoding="utf-8") as f:
        gacha_data = json.load(f)
    gacha_img = await get_gacha_log_img(gacha_data, pool)
    await bot.send(ev, gacha_img, at_sender=True)