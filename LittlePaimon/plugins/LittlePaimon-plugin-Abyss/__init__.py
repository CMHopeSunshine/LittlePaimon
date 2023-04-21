from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent,GroupMessageEvent,Bot
from LittlePaimon.utils import logger
from LittlePaimon.utils.message import CommandUID, CommandSwitch, CommandPlayer
from typing import Union
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me
from nonebot.plugin import PluginMetadata
from .sign_handle import sign_in,handle_ssbq
from LittlePaimon.database import PrivateCookie,MihoyoBBSSub
from .sign_handle import bbs_auto_sign
from nonebot.typing import T_State
from .coin_handle import mhy_bbs_coin, bbs_auto_coin
from .config import config

from . import web_page,web_api

__plugin_meta__ = PluginMetadata(
    name='原神加强签到',
    description='原神加强签到',
    usage='原神加强签到',
    extra={
        'author':   'Edelweiss',
        'version':  '1.0',
        'priority': 7,
    }
)


sign = on_command('验证签到', priority=8, block=True, state={
        'pm_name':        '验证签到',
        'pm_description': '*执行米游社签到操作',
        'pm_usage':       '验证签到',
        'pm_priority':    1
    })


all_sign = on_command('全部验证重签', priority=8, block=True, permission=SUPERUSER, rule=to_me(), state={
        'pm_name':        '米游社验证重签',
        'pm_description': '重签全部米游社签到任务，需超级用户权限',
        'pm_usage':       '@Bot 全部验证重签',
        'pm_priority':    2
    })

ti = on_command('验证体力', priority=8, block=True, state={
        'pm_name':        '体力',
        'pm_description': '*验证体力',
        'pm_usage':       '验证体力',
        'pm_priority':    3
    })

get_coin = on_command('验证米游币获取', priority=8, block=True, state={
        'pm_name':        '验证米游币获取',
        'pm_description': '*执行米游币任务操作，或开启每日自动获取米游币',
        'pm_usage':       '验证米游币获取(uid)[on|off]',
        'pm_priority':    4
    })

all_coin = on_command('全部验证重做', priority=8, block=True, permission=SUPERUSER, rule=to_me(), state={
        'pm_name':        '全部验证重做',
        'pm_description': '重做全部米游币获取任务，需超级用户权限',
        'pm_usage':       '@Bot 全部验证重做',
        'pm_priority':    5
    })


list = []

@sign.handle()
async def _(bot:Bot,event: GroupMessageEvent, uid=CommandUID(), switch=CommandSwitch()):
    if (event.group_id in config.whitelist) or (event.user_id in config.whlist) or (str(event.user_id) in bot.config.superusers):
        if switch is None:
            if f'{event.user_id}-{uid}' in list:
                await sign.finish('你已经有验证任务了，请勿重复发送', at_sender=True)
            else:
                await sign.send(f'开始为UID{uid}执行[验证]米游社签到，请稍等...', at_sender=True)
                logger.info('米游社原神签到', '', {'user_id': event.user_id, 'uid': uid, '执行签到': ''})
                list.append(f'{event.user_id}-{uid}')
                _, result = await sign_in(str(event.user_id), uid)
                list.remove(f'{event.user_id}-{uid}')
                await sign.finish(result, at_sender=True)
        else:
            sub_data = {
                'user_id':    event.user_id,
                'uid':        uid,
                'sub_event': '米游社验证签到'
            }
            if switch:
                # switch为开启，则添加订阅
                if await PrivateCookie.get_or_none(user_id=str(event.user_id), uid=uid):
                    await  MihoyoBBSSub.update_or_create(**sub_data, defaults={
                        'group_id': event.group_id if isinstance(event, GroupMessageEvent) else event.user_id})
                    logger.info('米游社[验证]签到', '', {'user_id': event.user_id, 'uid': uid}, '开启成功', True)
                    await sign.finish(f'UID{uid}开启米游社[验证]签到', at_sender=True)
                else:
                    await sign.finish(f'UID{uid}尚未绑定Cookie！请先使用ysb指令绑定吧！', at_sender=True)
            else:
                # switch为关闭，则取消订阅
                if sub := await  MihoyoBBSSub.get_or_none(**sub_data):
                    await sub.delete()
                    logger.info('米游社[验证]签到', '', {'user_id': event.user_id, 'uid': uid}, '关闭成功', True)
                    await sign.finish(f'UID{uid}关闭米游社[验证]自动签到成功', at_sender=True)
                else:
                    await sign.finish(f'UID{uid}尚未开启米游社[验证]自动签到，无需关闭！', at_sender=True)               
    else:
        await sign.finish(config.hfu, at_sender=True)

@all_sign.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    await all_sign.send('开始执行全部验证重签，需要一定时间...')
    await bbs_auto_sign()



@ti.handle()
async def _(bot:Bot,event: GroupMessageEvent, state: T_State, players=CommandPlayer()):
    if (event.group_id in config.whitelist) or (event.user_id in config.whlist) or (str(event.user_id) in bot.config.superusers):
        logger.info('原神体力', '开始执行查询')
        for player in players:
            if f'{event.user_id}-{player.uid}' in list:
                await sign.finish('你已经有验证任务了，请勿重复发送', at_sender=True)
            else:
               list.append(f'{event.user_id}-{player.uid}')
               result = await handle_ssbq(player)
               list.remove(f'{event.user_id}-{player.uid}')
        await ti.finish(result, at_sender=True)
    else:
        await sign.finish(config.hfu, at_sender=True)


@get_coin.handle()
async def _(bot:Bot,event: GroupMessageEvent, uid=CommandUID(), switch=CommandSwitch()):
    if (event.group_id in config.whitelist) or (event.user_id in config.whlist) or (str(event.user_id) in bot.config.superusers):
        if switch is None:
            # 没有开关参数，手动执行米游币获取
            if f'{event.user_id}-{uid}' in list:
                await get_coin.finish('你已经有验证任务了，请勿重复发送', at_sender=True)
            else:
                await get_coin.send(f'开始为UID{uid}执行[验证]米游币获取，请稍等...', at_sender=True)
                logger.info('[验证]米游币自动获取', '', {'user_id': event.user_id, 'uid': uid, '执行获取': ''})
                list.append(f'{event.user_id}-{uid}')
                result = await mhy_bbs_coin(str(event.user_id), uid)
                list.remove(f'{event.user_id}-{uid}')
                await get_coin.finish(result, at_sender=True)
        else:
            sub_data = {
                'user_id':   event.user_id,
                'uid':       uid,
                'sub_event': '米游币验证获取'
            }
            if switch:
                # switch为开启，则添加订阅
                if (ck := await PrivateCookie.get_or_none(user_id=str(event.user_id), uid=uid)) and ck.stoken is not None:
                    await MihoyoBBSSub.update_or_create(**sub_data, defaults={
                        'group_id': event.group_id if isinstance(event, GroupMessageEvent) else event.user_id})
                    logger.info('米游币自动获取', '', {'user_id': event.user_id, 'uid': uid}, '开启成功', True)
                    await sign.finish(f'UID{uid}开启[验证]米游币自动获取成功', at_sender=True)
                else:
                    await get_coin.finish(f'UID{uid}尚未绑定Cookie或Cookie中没有login_ticket！请先使用ysb指令绑定吧！', at_sender=True)
            else:
                # switch为关闭，则取消订阅
                if sub := await MihoyoBBSSub.get_or_none(**sub_data):
                    await sub.delete()
                    logger.info('米游币自动获取', '', {'user_id': event.user_id, 'uid': uid}, '关闭成功', True)
                    await sign.finish(f'UID{uid}关闭[验证]米游币自动获取成功', at_sender=True)
                else:
                    await sign.finish(f'UID{uid}尚未开启[验证]米游币自动获取，无需关闭！', at_sender=True)
    else:
        await sign.finish(config.hfu, at_sender=True)

@all_coin.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    await all_coin.send('开始执行[验证]myb全部重做，需要一定时间...')
    await bbs_auto_coin()
