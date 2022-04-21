from hoshino import logger, Service
from hoshino.util import filt_message
from ..util import get_uid_in_msg, get_at_target
from ..get_data import get_player_card_data, get_chara_detail_data, get_chara_skill_data
from .get_img import draw_player_card, draw_all_chara_card, draw_chara_card
from ..character_alias import get_id_by_alias

help_msg='''
1.[ys (uid)]查看原神个人卡片(包含宝箱、探索度等数据)
2.[ysa (uid)]查看所有公开的8角色的简略信息
3.[ysc (uid) 角色名]查看公开的8角色的详细信息
*绑定私人cookie之后就可以查看所有角色啦
'''
sv = Service('派蒙原神信息查询', bundle='派蒙', help_=help_msg)

@sv.on_prefix('ys')
async def player_card(bot,ev):
    uid, msg, user_id, use_cache = await get_uid_in_msg(ev)
    if not uid:
        await bot.send(ev,'请把正确的uid给派蒙哦,例如ys100123456!',at_sender=True)
        return 
    try:
        data = await get_player_card_data(user_id, uid, use_cache=use_cache)
        if isinstance(data, str):
            await bot.send(ev, data, at_sender=True)
        else:
            if ev.message_type == 'group':
                user_info = await bot.get_group_member_info(group_id=ev.group_id,user_id=int(user_id))
                nickname = user_info['card'] or user_info['nickname']
            else:
                nickname = ev.sender['nickname']
            chara_data = await get_chara_detail_data(user_id, uid, use_cache=use_cache)
            chara_data = None if isinstance(chara_data, str) else chara_data
            player_card = await draw_player_card(data, chara_data, uid, nickname)
            await bot.send(ev, player_card, at_sender=True)
    except ActionFailed:
        await bot.send(ev, '派蒙可能被风控，发不出消息')
    except TypeError or AttributeError:
        await bot.send(ev, '派蒙好像没有该UID的绑定信息')
    except IndexError or KeyError:
        await bot.send(ev, '派蒙获取信息失败，可能是米游社API有变动，请联系开发者')
    except JSONDecodeError:
        await bot.send(ev, '派蒙获取信息失败，重试一下吧')
    except Exception as e:
        await bot.send(ev, f'派蒙出现了问题：{e}')

@sv.on_prefix('ysa')
async def all_characters(bot,ev):
    uid, msg, user_id, use_cache = await get_uid_in_msg(ev)
    if not uid:
        await bot.send(ev,'请把正确的uid给派蒙哦,例如ysa100123456!',at_sender=True)
        return
    try:
        chara_data = await get_chara_detail_data(user_id, uid, use_cache=use_cache)
        if isinstance(chara_data, str):
            await bot.send(ev, chara_data, at_sender=True)
        else:
            player_card = await draw_all_chara_card(chara_data, uid)
            await bot.send(ev, player_card, at_sender=True)
    except ActionFailed:
        await bot.send(ev, '派蒙可能被风控，发不出消息')
    except TypeError or AttributeError:
        await bot.send(ev, '派蒙好像没有该UID的绑定信息')
    except IndexError or KeyError:
        await bot.send(ev, '派蒙获取信息失败，可能是米游社API有变动，请联系开发者')
    except JSONDecodeError:
        await bot.send(ev, '派蒙获取信息失败，重试一下吧')
    except Exception as e:
        await bot.send(ev, f'派蒙出现了问题：{e}')

@sv.on_prefix('ysc')
async def my_characters(bot,ev):
    uid, msg, user_id, use_cache = await get_uid_in_msg(ev)
    if not uid:
        await bot.send(ev,'请把正确的uid给派蒙哦,例如ysc100123456钟离',at_sender=True)
        return
    if not msg:
        await bot.send(ev,f'要把角色名给派蒙呀!例如ysc100123456钟离',at_sender=True)
        return
    chara = msg.split(' ')[0]
    chara_name = get_id_by_alias(chara)
    if not chara_name:
        await bot.send(ev,f'没有角色名叫{filt_message(chara)}哦！',at_sender=True)
        return
    try:
        chara_data = await get_chara_detail_data(user_id, uid, use_cache=use_cache)
        if isinstance(chara_data, str):
            await bot.send(ev, chara_data, at_sender=True)
        else:
            skill_data = await get_chara_skill_data(uid, chara_name[0], use_cache=use_cache)
            chara_card = await draw_chara_card(chara_data, skill_data, chara_name, uid)
            await bot.send(ev, chara_card, at_sender=True)
    except ActionFailed:
        logger.exception('账号可能被风控')
        await bot.send(ev, '派蒙可能被风控，发不出消息')
    except TypeError or AttributeError:
        await bot.send(ev, '派蒙好像没有该UID的绑定信息')
    except IndexError or KeyError:
        await bot.send(ev, '派蒙获取信息失败，可能是米游社API有变动，请联系开发者')
    except JSONDecodeError:
        await bot.send(ev, '派蒙获取信息失败，重试一下吧')
    except Exception as e:
        await bot.send(ev, f'派蒙出现了问题：{e}')
    
