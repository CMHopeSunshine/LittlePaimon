from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from nonebot.adapters.onebot.v11.helpers import HandleCancellation
from nonebot.rule import Rule
from nonebot.params import ArgPlainText, CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from LittlePaimon import NICKNAME
from LittlePaimon.database import PlayerAlias, LastQuery
from LittlePaimon.utils import logger
from LittlePaimon.utils.path import YSC_TEMP_IMG_PATH
from LittlePaimon.utils.message import CommandPlayer, CommandCharacter, CommandUID
from LittlePaimon.utils.genshin import GenshinInfoManager
from LittlePaimon.utils.tool import freq_limiter
from LittlePaimon.utils.typing import CHARACTERS

from .draw_player_card import draw_player_card
from .draw_character_bag import draw_chara_bag
from .draw_character_detail import draw_chara_detail
from .draw_character_card import draw_chara_card

__plugin_meta__ = PluginMetadata(
    name='原神信息查询',
    description='原神信息查询',
    usage='...',
    extra={
        'author': '惜月',
        'version': '3.0',
        'priority': 1,
    },
)


def has_raw_rule(event: MessageEvent) -> bool:
    return bool(
        event.reply and (YSC_TEMP_IMG_PATH / f'{event.reply.message_id}.jpg').exists()
    )


ys = on_command(
    'ys',
    aliases={'原神卡片', '个人卡片'},
    priority=10,
    block=True,
    state={
        'pm_name': 'ys',
        'pm_description': '查看原神个人信息卡片',
        'pm_usage': 'ys(uid)',
        'pm_priority': 1,
    },
)
ysa = on_command(
    'ysa',
    aliases={'角色背包', '练度统计'},
    priority=10,
    block=True,
    state={
        'pm_name': 'ysa',
        'pm_description': '查看角色背包及练度排行',
        'pm_usage': 'ysa(uid)',
        'pm_priority': 2,
    },
)
ysc = on_command(
    'ysc',
    aliases={'角色图', '角色卡片'},
    priority=10,
    block=True,
    state={
        'pm_name': 'ysc',
        'pm_description': '随机角色同人图+角色信息卡片',
        'pm_usage': 'ysc(uid)<角色名>',
        'pm_priority': 4,
    },
)
ysd = on_command(
    'ysd',
    aliases={'角色详情', '角色信息', '角色面板'},
    priority=10,
    block=True,
    state={
        'pm_name': 'ysd',
        'pm_description': '查看指定角色的详细面板数据及伤害计算',
        'pm_usage': 'ysd(uid)<角色名>',
        'pm_priority': 5,
    },
)
update_info = on_command(
    'udi',
    aliases={'更新角色信息', '更新面板', '更新玩家信息'},
    priority=10,
    block=True,
    state={
        'pm_name': 'udi',
        'pm_description': '更新你的原神玩家和角色数据，绑定cookie后数据更详细，加上"天赋"可以更新天赋等级',
        'pm_usage': '更新角色信息[天赋](uid)',
        'pm_priority': 6,
    },
)
add_alias = on_command(
    '设置别名',
    priority=10,
    block=True,
    state={
        'pm_name': '角色别名设置',
        'pm_description': '设置专属于你的角色别名，例如【设置别名钟离 老公】',
        'pm_usage': '设置别名<角色> <别名>',
        'pm_priority': 7,
    },
)
delete_alias = on_command(
    '删除别名',
    priority=10,
    block=True,
    state={
        'pm_name': '角色别名删除',
        'pm_description': '删除你已设置的角色别名',
        'pm_usage': '删除别名<别名>',
        'pm_priority': 8,
    },
)
show_alias = on_command(
    '查看别名',
    priority=10,
    block=True,
    state={
        'pm_name': '角色别名查看',
        'pm_description': '查看你已设置的角色别名',
        'pm_usage': '查看别名',
        'pm_priority': 9,
    },
)
raw_img_cmd = on_command(
    '原图',
    priority=10,
    block=True,
    rule=Rule(has_raw_rule),
    state={
        'pm_name': 'ysc原图',
        'pm_description': '获取ysc指令卡片中的原神同人图',
        'pm_usage': '(回复ysc消息) 原图',
        'pm_priority': 10,
    },
)


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
            logger.info(
                '原神角色背包', '➤ ', {'用户': players[0].user_id, 'UID': players[0].uid}
            )
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
                except AttributeError:
                    msg += F'UID{player.uid}制图时出错，请尝试使用命令[更新角色信息]后重试\n'
                except Exception as e:
                    logger.info('原神角色背包', '➤➤➤', {}, f'制图出错:{e}', False)
                    msg += F'UID{player.uid}制图时出错：{e}\n'
            running_ysa.remove(f'{player.user_id}-{player.uid}')
    if msg:
        await ysa.finish(msg, at_sender=True)


@ysc.handle()
async def _(
    event: MessageEvent,
    players=CommandPlayer(only_cn=False),
    characters=CommandCharacter(),
):
    logger.info('原神角色卡片', '开始执行')
    msg = Message()
    temp_img = None
    if len(players) == 1:
        # 当查询对象只有一个时，查询所有角色
        gim = GenshinInfoManager(players[0].user_id, players[0].uid)
        await LastQuery.update_last_query(players[0].user_id, players[0].uid)
        logger.info('原神角色卡片', '➤', {'用户': players[0].user_id, 'UID': players[0].uid})
        for character in characters:
            character_info = await gim.get_character(name=character)
            if not character_info:
                logger.info('原神角色卡片', '➤➤', {'角色': character}, '没有该角色信息，发送随机图', True)
                msg += MessageSegment.image(
                    f'https://genshin-res.cherishmoon.fun/img?name={character}'
                )
            else:
                img, temp_img = await draw_chara_card(character_info)
                logger.info('原神角色卡片', '➤➤', {'角色': character}, '制图完成', True)
                msg += img
    else:
        # 当查询对象有多个时，只查询第一个角色
        for player in players:
            gim = GenshinInfoManager(player.user_id, player.uid)
            await LastQuery.update_last_query(player.user_id, player.uid)
            logger.info('原神角色卡片', '➤', {'用户': player.user_id, 'UID': player.uid})
            character_info = await gim.get_character(name=characters[0])
            if not character_info:
                logger.info(
                    '原神角色卡片', '➤➤', {'角色': characters[0]}, '没有该角色信息，发送随机图', True
                )
                msg += MessageSegment.image(
                    f'https://genshin-res.cherishmoon.fun/img?name={characters[0]}'
                )
            else:
                img, temp_img = await draw_chara_card(character_info)
                logger.info('原神角色卡片', '➤➤', {'角色': characters[0]}, '制图完成', True)
                msg += img
    send_result = await ysd.send(msg, at_sender=True)
    if temp_img:
        temp_img.convert('RGB').save(
            YSC_TEMP_IMG_PATH / f'{send_result["message_id"]}.jpg',
        )


@raw_img_cmd.handle()
async def _(event: MessageEvent):
    with open(YSC_TEMP_IMG_PATH / f'{event.reply.message_id}.jpg', 'rb') as f:
        await raw_img_cmd.finish(MessageSegment.image(f.read()))


@ysd.handle()
async def _(
    event: MessageEvent,
    players=CommandPlayer(only_cn=False),
    characters=CommandCharacter(),
):
    logger.info('原神角色面板', '开始执行')
    msg = Message()
    try:
        if len(players) == 1:
            # 当查询对象只有一个时，查询所有角色
            gim = GenshinInfoManager(players[0].user_id, players[0].uid)
            await LastQuery.update_last_query(players[0].user_id, players[0].uid)
            logger.info(
                '原神角色面板', '➤', {'用户': players[0].user_id, 'UID': players[0].uid}
            )
            for character in characters:
                character_info = await gim.get_character(
                    name=character, data_source='enka'
                )
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
                await LastQuery.update_last_query(player.user_id, player.uid)
                logger.info('原神角色面板', '➤', {'用户': player.user_id, 'UID': player.uid})
                character_info = await gim.get_character(
                    name=characters[0], data_source='enka'
                )
                if not character_info:
                    msg += f'\n暂无{player.uid}的{characters[0]}信息，请在游戏内展柜放置该角色'
                else:
                    img = await draw_chara_detail(player.uid, character_info)
                    logger.info('原神角色面板', '➤➤➤', {}, '制图完成', True)
                    msg += img
    except KeyError as e:
        msg = f'获取角色信息失败，缺少{e}的数据，可能是Enka.Network接口出现问题'
    except Exception as e:
        msg = f'获取角色信息失败，错误信息：{e}'
    await ysd.finish(msg, at_sender=True)


running_udi = []


@update_info.handle()
async def _(event: MessageEvent, state: T_State, uid=CommandUID()):
    msg = state['clear_msg']
    if not freq_limiter.check(f'udi{uid}'):
        await update_info.finish(
            f'UID{uid}: 更新信息冷却剩余{freq_limiter.left(f"udi{uid}")}秒\n', at_sender=True
        )
    elif f'{event.user_id}-{uid}' in running_udi:
        await update_info.finish(f'UID{uid}正在更新信息中，请勿重复发送指令')
    else:
        running_udi.append(f'{event.user_id}-{uid}')
        try:
            include_talent = any(i in msg for i in ['全部', '技能', '天赋', 'talent', 'all'])
            await update_info.send('开始更新原神信息，请稍后...')
            logger.info('原神信息', '➤开始更新', {'用户': event.user_id, 'UID': uid})
            freq_limiter.start(f'udi{uid}', 60)
            gim = GenshinInfoManager(str(event.user_id), uid)
            result = await gim.update_all(include_talent)
        except KeyError as e:
            result = f'更新失败，缺少{e}的数据，可能是Enka.Network接口出现问题'
        except Exception as e:
            result = f'更新失败，错误信息：{e}'
        finally:
            running_udi.remove(f'{event.user_id}-{uid}')
        await update_info.finish(f'UID{uid}:\n{result}', at_sender=True)


@add_alias.handle()
async def _(event: MessageEvent, state: T_State, msg: Message = CommandArg()):
    msg = msg.extract_plain_text().strip().split(' ')
    if msg[0] in CHARACTERS:
        state['chara'] = Message(msg[0])
    else:
        await add_alias.finish(f'{NICKNAME}不认识{msg[0]}哦，请使用角色全称', at_sender=True)
    if len(msg) > 1:
        state['alias'] = Message(msg[1])


@add_alias.got(
    'alias',
    prompt=Message.template('你想把{chara}设置为你的谁呢？'),
    parameterless=[HandleCancellation(f'好吧，有事再找{NICKNAME}吧')],
)
async def _(
    event: MessageEvent,
    chara: str = ArgPlainText('chara'),
    alias: str = ArgPlainText('alias'),
):
    await PlayerAlias.update_or_create(
        user_id=str(event.user_id), alias=alias, defaults={'character': chara}
    )
    await add_alias.finish(f'设置成功，{NICKNAME}知道{chara}是你的{alias}啦..')


@delete_alias.handle()
async def _(event: MessageEvent, state: T_State, msg: Message = CommandArg()):
    if msg:
        state['alias'] = msg
    elif aliases := await PlayerAlias.filter(user_id=str(event.user_id)).all():
        state['msg'] = (
            '你已设置以下别名:\n'
            + '\n'.join([f'{i.alias} -> {i.character}' for i in aliases])
            + '\n请输入你想删除的别名或发送"全部"删除全部别名'
        )
    else:
        await delete_alias.finish('你还没有设置任何别名哦')


@delete_alias.got(
    'alias',
    prompt=Message.template('{msg}'),
    parameterless=[HandleCancellation(f'好吧，有事再找{NICKNAME}吧')],
)
async def _(event: MessageEvent, msg: str = ArgPlainText('alias')):
    if msg == '全部':
        await PlayerAlias.filter(user_id=str(event.user_id)).delete()
        await delete_alias.finish('已删除你设置的全部别名')
    elif alias := await PlayerAlias.get_or_none(user_id=str(event.user_id), alias=msg):
        await alias.delete()
        await delete_alias.finish(f'别名{msg}删除成功!', at_sender=True)
    else:
        await delete_alias.reject(f'你并没有将{msg}设置为某个角色的别名，回复"取消"取消删除', at_sender=True)


@show_alias.handle()
async def _(event: MessageEvent):
    if aliases := await PlayerAlias.filter(user_id=str(event.user_id)).all():
        await show_alias.finish(
            '你已设以下别名:'
            + '\n'.join(f'{alias.alias}->{alias.character}' for alias in aliases),
            at_sender=True,
        )
    else:
        await show_alias.finish('你还没有设置过角色别名哦', at_sender=True)
