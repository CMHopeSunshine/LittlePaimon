import json
import re

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent
from nonebot.params import CommandArg, Arg
from nonebot.plugin import PluginMetadata

from LittlePaimon.config import GACHA_LOG
from LittlePaimon.utils.files import load_json, save_json
from LittlePaimon.utils.message import CommandPlayer
from .api import toApi, checkApi
from .gacha_logs import get_data
from .get_img import get_gacha_log_img

__plugin_meta__ = PluginMetadata(
    name="原神抽卡记录分析",
    description="小派蒙的原神抽卡记录模块",
    usage=(
        "1.[获取抽卡记录 (uid) (url)]提供url，获取原神抽卡记录，需要一定时间"
        "2.[查看抽卡记录 (uid)]查看抽卡记录分析"
        "3.[导出抽卡记录 (uid) (xlsx/json)]导出抽卡记录文件，上传到群文件中"
    ),
    extra={
        'type':    '原神抽卡记录',
        "author":  "惜月 <277073121@qq.com>",
        "version": "0.1.3",
        'priority': 10,
    },
)

gacha_log_export = on_command('ckjldc', aliases={'抽卡记录导出', '导出抽卡记录'}, priority=12, block=True, state={
        'pm_name':        '抽卡记录导出',
        'pm_description': '将抽卡记录导出到群文件中',
        'pm_usage':       '抽卡记录导出(uid)[xlsx/json]',
        'pm_priority':    3
    })
gacha_log_update = on_command('ckjlgx', aliases={'抽卡记录更新', '更新抽卡记录', '获取抽卡记录'}, priority=12, block=True, state={
        'pm_name':        '获取抽卡记录',
        'pm_description': '从抽卡链接获取抽卡记录，链接可以通过祈愿页面断网取得',
        'pm_usage':       '获取抽卡记录(uid)<链接>',
        'pm_priority':    1
    })
gacha_log_show = on_command('ckjl', aliases={'抽卡记录', '查看抽卡记录'}, priority=12, block=True, state={
        'pm_name':        '查看抽卡记录',
        'pm_description': '查看你的抽卡记录分析',
        'pm_usage':       '查看抽卡记录',
        'pm_priority':    2
    })


@gacha_log_export.handle()
async def ckjl(bot: Bot, event: GroupMessageEvent, player=CommandPlayer(1), msg: str = Arg('msg')):
    player = player[0]
    if match := re.search(r'(?P<filetype>xlsx|json)', msg):
        filetype = match['filetype']
    else:
        filetype = 'xlsx'
    filetype = f'gachaExport-{player.uid}.xlsx' if filetype == 'xlsx' else f'UIGF_gachaData-{player.uid}.json'
    local_data = GACHA_LOG / filetype
    if not local_data.exists():
        await gacha_log_export.finish('你在派蒙这里还没有抽卡记录哦，使用 更新抽卡记录 吧！', at_sender=True)
    else:
        await bot.upload_group_file(group_id=event.group_id, file=local_data, name=filetype)


@gacha_log_update.handle()
async def update_ckjl(event: MessageEvent, msg: Message = CommandArg()):
    url = None
    if msg := msg.extract_plain_text().strip():
        if log_url := re.search(r'(https://webstatic.mihoyo.com/.*#/log)', msg):
            url = log_url[1]
            msg = msg.replace(url, '')
        if not url:
            await gacha_log_update.finish('你这个抽卡链接不对哦，应该是以https://开头、#/log结尾的！', at_sender=True)
    user_data = load_json(GACHA_LOG / 'gacha_log_url.json')
    if not url and str(event.user_id) in user_data:
        url = user_data[str(event.user_id)]
        await gacha_log_update.send('发现历史抽卡记录链接，尝试使用...')
    else:
        await gacha_log_update.finish('拿到游戏抽卡记录链接后，对派蒙说[获取抽卡记录 uid 链接]就可以啦\n获取抽卡记录链接的方式和vx小程序的是一样的，还请旅行者自己搜方法',
                                      at_sender=True)
    if str(event.user_id) not in user_data:
        user_data[str(event.user_id)] = url
    save_json(user_data, path=GACHA_LOG / 'gacha_log_url.json')

    url = toApi(url)
    apiRes = await checkApi(url)
    if apiRes != 'OK':
        await gacha_log_update.finish(apiRes, at_sender=True)
    await gacha_log_update.send('抽卡记录开始获取，请给派蒙一点时间...')
    uid = await get_data(url)

    local_data = GACHA_LOG / f'gachaData-{uid}.json'
    gacha_data = load_json(local_data)
    gacha_img = await get_gacha_log_img(gacha_data, 'all')
    await gacha_log_update.finish(gacha_img, at_sender=True)


@gacha_log_show.handle()
async def get_ckjl(event: MessageEvent, player=CommandPlayer(1), msg: str = Arg('msg')):
    player = player[0]
    if pool_type := re.search(r'(all|角色|武器|常驻|新手)', msg):
        pool_type = pool_type[1]
    else:
        pool_type = 'all'
    local_data = GACHA_LOG / f'gachaData-{player.uid}.json'
    if not local_data.exists():
        await gacha_log_update.finish('你在派蒙这里还没有抽卡记录哦，对派蒙说 获取抽卡记录 吧！', at_sender=True)
    with open(local_data, 'r', encoding="utf-8") as f:
        gacha_data = json.load(f)
    gacha_img = await get_gacha_log_img(gacha_data, pool_type)
    await gacha_log_update.finish(gacha_img, at_sender=True)
