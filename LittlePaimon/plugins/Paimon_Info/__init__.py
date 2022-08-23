from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.internal.params import Arg
from nonebot.plugin import PluginMetadata

from LittlePaimon.utils import logger
from LittlePaimon.utils.message import CommandPlayer, CommandCharacter, CommandUID
from LittlePaimon.utils.genshin import GenshinInfoManager
from LittlePaimon.utils.tool import freq_limiter

from .draw_player_card import draw_player_card
from .draw_character_bag import draw_chara_bag
from .draw_character_detail import draw_chara_detail
from .draw_character_card import draw_chara_card
from .draw_abyss import draw_abyss_card

__plugin_meta__ = PluginMetadata(
    name='原神信息查询',
    description='原神信息查询',
    usage='...',
    extra={
        'author':   '惜月',
        'version':  '3.0',
        'priority': 1,
    }
)

ys = on_command('ys', aliases={'原神卡片', '个人卡片'}, priority=10, block=True, state={
    'pm_name':        'ys',
    'pm_description': '查看原神个人信息卡片',
    'pm_usage':       'ys(uid)',
    'pm_priority':    1
})
ysa = on_command('ysa', aliases={'角色背包', '练度统计'}, priority=10, block=True, state={
    'pm_name':        'ysa',
    'pm_description': '查看角色背包及练度排行',
    'pm_usage':       'ysa(uid)',
    'pm_priority':    2
})
sy = on_command('sy', aliases={'深渊战报', '深渊信息'}, priority=10, block=True, state={
    'pm_name':        'sy',
    'pm_description': '查看本期|上期的深渊战报',
    'pm_usage':       'sy(uid)(本期|上期)',
    'pm_priority':    3
})
ysc = on_command('ysc', aliases={'角色图'}, priority=10, block=True, state={
    'pm_name':        'ysc',
    'pm_description': '随机角色同人图+角色信息卡片',
    'pm_usage':       'ysc(uid)<角色名>',
    'pm_priority':    4
})
ysd = on_command('ysd', aliases={'角色详情', '角色信息', '角色面板'}, priority=10, block=True, state={
    'pm_name':        'ysd',
    'pm_description': '查看指定角色的详细面板数据及伤害计算',
    'pm_usage':       'ysd(uid)<角色名>',
    'pm_priority':    5
})
update_info = on_command('udi', aliases={'更新角色信息', '更新面板', '更新玩家信息'}, priority=10, block=True, state={
    'pm_name':        'udi',
    'pm_description': '更新你的原神玩家和角色数据，绑定cookie后数据更详细',
    'pm_usage':       '更新角色信息(uid)',
    'pm_priority':    6
})


@ys.handle()
async def _(event: MessageEvent, players=CommandPlayer()):
    logger.info('原神信息查询', '开始执行')
    msg = Message()
    for player in players:
        logger.info('原神信息查询', '➤ ', {'用户': player.user_id, 'UID': player.uid})
        gim = GenshinInfoManager(player.user_id, player.uid)
        player_info, characters_list = await gim.get_player_info()
        if isinstance(player_info, str):
            logger.info('原神信息查询', '➤➤', {}, player_info, False)
            msg += f'UID{player.uid}{player_info}\n'
        else:
            logger.info('原神信息查询', '➤➤', {}, '数据获取成功', True)
            try:
                img = await draw_player_card(player, player_info, characters_list)
                logger.info('原神信息查询', '➤➤➤', {}, '制图完成', True)
                msg += img
            except Exception as e:
                logger.info('原神信息查询', '➤➤➤', {}, f'制图出错:{e}', False)
                msg += F'UID{player.uid}制图时出错：{e}\n'
    await ys.finish(msg, at_sender=True)


running_ysa = []

@ysa.handle()
async def _(event: MessageEvent, players=CommandPlayer(2)):
    logger.info('原神角色背包', '开始执行')
    msg = Message()
    await ysa.send('开始绘制角色背包卡片，请稍等...')
    for player in players:
        if f'{player.user_id}-{player.uid}' in running_ysa:
            await ysa.send(f'UID{player.uid}正在绘制角色背包，请勿重复发送指令')
        else:
            running_ysa.append(f'{player.user_id}-{player.uid}')
            logger.info('原神角色背包', '➤ ', {'用户': players[0].user_id, 'UID': players[0].uid})
            gim = GenshinInfoManager(player.user_id, player.uid)
            player_info, characters_list = await gim.get_chara_bag()
            if isinstance(player_info, str):
                logger.info('原神角色背包', '➤➤', {}, player_info, False)
                msg += f'UID{player.uid}{player_info}\n'
            else:
                logger.info('原神角色背包', '➤➤', {}, '数据获取成功', True)
                try:
                    img = await draw_chara_bag(player, player_info, characters_list)
                    logger.info('原神角色背包', '➤➤➤', {}, '制图完成', True)
                    msg += img
                except Exception as e:
                    logger.info('原神角色背包', '➤➤➤', {}, f'制图出错:{e}', False)
                    msg += F'UID{player.uid}制图时出错：{e}\n'
            running_ysa.remove(f'{player.user_id}-{player.uid}')
    if msg:
        await ysa.finish(msg, at_sender=True)


@sy.handle()
async def _(event: MessageEvent, players=CommandPlayer(), msg: str = Arg('msg')):
    logger.info('原神深渊战报', '开始执行')
    abyss_index = 2 if any(i in msg for i in ['上', 'last']) else 1
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
    await ysa.finish(msg, at_sender=True)


@ysc.handle()
async def _(event: MessageEvent, players=CommandPlayer(only_cn=False), characters=CommandCharacter()):
    logger.info('原神角色卡片', '开始执行')
    msg = Message()
    if len(players) == 1:
        # 当查询对象只有一个时，查询所有角色
        gim = GenshinInfoManager(players[0].user_id, players[0].uid)
        await gim.set_last_query()
        logger.info('原神角色卡片', '➤', {'用户': players[0].user_id, 'UID': players[0].uid})
        for character in characters:
            character_info = await gim.get_character(name=character)
            if not character_info:
                logger.info('原神角色卡片', '➤➤', {'角色': character}, '没有该角色信息', False)
                msg += f'\n暂无你{character}信息，请先更新角色信息'
            else:
                img = await draw_chara_card(character_info)
                logger.info('原神角色卡片', '➤➤', {}, '制图完成', True)
                msg += img
    else:
        # 当查询对象有多个时，只查询第一个角色
        for player in players:
            gim = GenshinInfoManager(player.user_id, player.uid)
            await gim.set_last_query()
            logger.info('原神角色卡片', '➤', {'用户': player.user_id, 'UID': player.uid})
            character_info = await gim.get_character(name=characters[0])
            if not character_info:
                msg += f'\n暂无{player.uid}的{characters[0]}信息，请先更新角色信息'
            else:
                img = await draw_chara_card(character_info)
                logger.info('原神角色卡片', '➤➤', {}, '制图完成', True)
                msg += img
    await ysd.finish(msg, at_sender=True)


@ysd.handle()
async def _(event: MessageEvent, players=CommandPlayer(only_cn=False), characters=CommandCharacter()):
    logger.info('原神角色面板', '开始执行')
    msg = Message()
    if len(players) == 1:
        # 当查询对象只有一个时，查询所有角色
        gim = GenshinInfoManager(players[0].user_id, players[0].uid)
        await gim.set_last_query()
        logger.info('原神角色面板', '➤', {'用户': players[0].user_id, 'UID': players[0].uid})
        for character in characters:
            character_info = await gim.get_character(name=character, data_source='enka')
            if not character_info:
                logger.info('原神角色面板', '➤➤', {'角色': character}, '没有该角色信息', False)
                msg += f'\n暂无你{character}信息，请在游戏内展柜放置该角色'
            else:
                img = await draw_chara_detail(players[0].uid, character_info)
                logger.info('原神角色面板', '➤➤➤', {}, '制图完成', True)
                msg += img
    else:
        # 当查询对象有多个时，只查询第一个角色
        for player in players:
            gim = GenshinInfoManager(player.user_id, player.uid)
            await gim.set_last_query()
            logger.info('原神角色面板', '➤', {'用户': player.user_id, 'UID': player.uid})
            character_info = await gim.get_character(name=characters[0], data_source='enka')
            if not character_info:
                msg += f'\n暂无{player.uid}的{characters[0]}信息，请在游戏内展柜放置该角色'
            else:
                img = await draw_chara_detail(player.uid, character_info)
                logger.info('原神角色面板', '➤➤➤', {}, '制图完成', True)
                msg += img
    await ysd.finish(msg, at_sender=True)


running_udi = []


@update_info.handle()
async def _(event: MessageEvent, uid=CommandUID(), msg: str = Arg('msg')):
    if not freq_limiter.check(f'udi{uid}'):
        await update_info.finish(f'UID{uid}: 更新信息冷却剩余{freq_limiter.left(f"udi{uid}")}秒\n', at_sender=True)
    elif f'{event.user_id}-{uid}' in running_udi:
        await update_info.finish(f'UID{uid}正在更新信息中，请勿重复发送指令')
    else:
        running_udi.append(f'{event.user_id}-{uid}')
        include_talent = any(i in msg for i in ['全部', '技能', '天赋', 'talent', 'all'])
        await update_info.send('开始更新原神信息，请稍后...')
        logger.info('原神信息', '➤开始更新', {'用户': event.user_id, 'UID': uid})
        freq_limiter.start(f'udi{uid}', 180)
        gim = GenshinInfoManager(str(event.user_id), uid)
        result = await gim.update_all(include_talent)
        running_udi.remove(f'{event.user_id}-{uid}')
        await update_info.finish(f'UID{uid}:\n {result}', at_sender=True)
