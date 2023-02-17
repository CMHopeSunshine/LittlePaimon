from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageEvent
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from LittlePaimon.utils import logger
from LittlePaimon.utils.genshin import GenshinInfoManager
from LittlePaimon.utils.message import CommandPlayer

from .abyss_statistics import get_statistics
from .draw_abyss import draw_abyss_card
from .youchuang import draw_team

__plugin_meta__ = PluginMetadata(
    name='原神深渊查询',
    description='原神深渊查询',
    usage='...',
    extra={
        'author': '惜月',
        'version': '3.0',
        'priority': 2,
    },
)

sy = on_command(
    'sy',
    aliases={'深渊战报', '深渊信息'},
    priority=10,
    block=True,
    state={
        'pm_name': 'sy',
        'pm_description': '查看本期|上期的深渊战报',
        'pm_usage': 'sy(uid)(本期|上期)',
        'pm_priority': 1,
    },
)
abyss_stat = on_command(
    '深渊统计',
    aliases={'深渊群数据', '深渊群排行'},
    priority=10,
    block=True,
    state={
        'pm_name': '深渊统计',
        'pm_description': '查看本群深渊统计，仅群可用',
        'pm_usage': '深渊统计',
        'pm_priority': 2,
    },
)
abyss_team = on_command(
    '深渊配队',
    aliases={'配队推荐', '深渊阵容'},
    priority=10,
    block=True,
    state={
        'pm_name': '深渊配队',
        'pm_description': '查看深渊配队推荐，数据来源于游创工坊',
        'pm_usage': '深渊配队',
        'pm_priority': 3,
    },
)


@sy.handle()
async def _(event: MessageEvent, players=CommandPlayer(), msg: Message = CommandArg()):
    logger.info('原神深渊战报', '开始执行')
    abyss_index = 2 if any(i in msg.extract_plain_text() for i in ['上', 'last']) else 1
    msg = Message()
    for player in players:
        logger.info('原神深渊战报', '➤ ', {'用户': players[0].user_id, 'UID': players[0].uid})
        gim = GenshinInfoManager(player.user_id, player.uid)
        abyss_info = await gim.get_abyss_info(abyss_index)
        if isinstance(abyss_info, str):
            logger.info('原神深渊战报', '➤➤', {}, abyss_info, False)
            msg += f'UID{player.uid}{abyss_info}\n'
        else:
            logger.info('原神深渊战报', '➤➤', {}, '数据获取成功', True)
            try:
                img = await draw_abyss_card(abyss_info)
                logger.info('原神深渊战报', '➤➤➤', {}, '制图完成', True)
                msg += img
            except Exception as e:
                logger.info('原神深渊战报', '➤➤➤', {}, f'制图出错:{e}', False)
                msg += F'UID{player.uid}制图时出错：{e}\n'
    await sy.finish(msg, at_sender=True)


@abyss_stat.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    try:
        result = await get_statistics(event.group_id, bot)
    except Exception as e:
        result = f'制作深渊统计时出错：{e}'
    await abyss_stat.finish(result)


@abyss_team.handle()
async def _(event: MessageEvent):
    try:
        result = await draw_team(str(event.user_id))
    except Exception as e:
        result = f'制作深渊配队时出错：{e}'
    await abyss_team.finish(result, at_sender=True)
