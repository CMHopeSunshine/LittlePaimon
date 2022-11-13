import asyncio
import datetime
import os
import sys
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from nonebot import get_bot
from nonebot.adapters.onebot.v11 import Bot

from LittlePaimon.utils import SUPERUSERS
from LittlePaimon.utils.files import save_json
from LittlePaimon.utils.tool import cache
from LittlePaimon.utils.update import update
from .utils import authentication

route = APIRouter()


@route.get('/get_group_list', response_class=JSONResponse, dependencies=[authentication()])
async def get_group_list():
    try:
        group_list = await get_bot().get_group_list()
        return [{'label': f'{group["group_name"]}({group["group_id"]})', 'value': group['group_id']} for group in group_list]
    except ValueError:
        return {
            'status': -100,
            'msg':    '获取群和好友列表失败，请确认已连接GOCQ'
        }


@route.get('/get_group_members', response_class=JSONResponse, dependencies=[authentication()])
async def get_group_members(group_id: int):
    try:
        return await get_bot().get_group_member_list(group_id=group_id)
    except ValueError:
        return {
            'status': -100,
            'msg':    '获取群和好友列表失败，请确认已连接GOCQ'
        }


@route.get('/get_groups_and_members', response_class=JSONResponse, dependencies=[authentication()])
@cache(datetime.timedelta(minutes=10))
async def get_groups_and_members():
    result = []
    try:
        bot: Bot = get_bot()
    except ValueError:
        return {
            'status': -100,
            'msg':    '获取群和好友列表失败，请确认已连接GOCQ'
        }
    group_list = await bot.get_group_list()
    friend_list = await bot.get_friend_list()
    for group in group_list:
        group_members = await bot.get_group_member_list(group_id=group['group_id'])
        result.append({
            'left_label':  f'{group["group_name"]}({group["group_id"]})',
            'right_label': f'{group["group_name"]}(群{group["group_id"]})',
            'value':       f'群{group["group_id"]}',
            'children':    [{'left_label':  f'{m["card"] or m["nickname"]}({m["user_id"]})',
                             'right_label': f'群({group["group_name"]}) - {m["card"] or m["nickname"]}({m["user_id"]})',
                             'value':       f'群{group["group_id"]}.{m["user_id"]}'} for m in group_members if
                            str(m['user_id']) != bot.self_id]
        })
        await asyncio.sleep(0.2)
    result = [
        {
            'label':      '群组',
            'selectMode': 'tree',
            'searchable': True,
            'children':   result
        },
        {
            'label':      '好友',
            'selectMode': 'list',
            'searchable': True,
            'children':   [{
                'left_label':  f'{f["nickname"]}({f["user_id"]})',
                'right_label': f'{f["nickname"]}({f["user_id"]})',
                'value':       f'{f["user_id"]}'
            } for f in friend_list if str(f['user_id']) != bot.self_id]
        }]
    return result


@route.get('/get_friend_list', response_class=JSONResponse, dependencies=[authentication()])
@cache(datetime.timedelta(minutes=10))
async def get_friend_list():
    try:
        bot: Bot = get_bot()
        friend_list = await bot.get_friend_list()
        return [{'label': f'{friend["nickname"]}({friend["user_id"]})', 'value': friend['user_id']} for friend in
                friend_list]
    except ValueError:
        return {
            'status': -100,
            'msg':    '获取群和好友列表失败，请确认已连接GOCQ'
        }


@route.post('/bot_update', response_class=JSONResponse, dependencies=[authentication()])
async def bot_update():
    result = await update()
    return {
        'status': 0,
        'msg':    result
    }


@route.post('/bot_restart', response_class=JSONResponse, dependencies=[authentication()])
async def bot_restart():
    save_json({'session_type': 'private',
               'session_id':   SUPERUSERS[0]},
              Path() / 'rebooting.json')
    if sys.argv[0].endswith('nb'):
        sys.argv[0] = 'bot.py'
    os.execv(sys.executable, ['python'] + sys.argv)
