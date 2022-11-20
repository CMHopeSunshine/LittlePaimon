from fastapi import APIRouter
from fastapi.responses import JSONResponse

from tortoise.queryset import Q
from LittlePaimon.database import CommandAlias
from LittlePaimon.config import ConfigManager
from LittlePaimon.config.command import modify_msg

from .utils import authentication

route = APIRouter()


@route.get('/command_alias', response_class=JSONResponse, dependencies=[authentication()])
async def get_command_alias():
    alias = await CommandAlias.all().order_by('priority').values()
    return {
        'status': 0,
        'msg':    'ok',
        'data':   {
            'command_alias_enable': ConfigManager.config.command_alias_enable,
            'items': alias,
        }
    }


@route.post('/command_alias', response_class=JSONResponse, dependencies=[authentication()])
async def add_command_alias(data: dict):
    ConfigManager.config.update(command_alias_enable=data['command_alias_enable'])
    ConfigManager.save()
    data = data['items']
    await CommandAlias.filter(id__not_in=[a['id'] for a in data if a.get('id')]).delete()
    for alias in data:
        alias['priority'] = data.index(alias)
        if alias.get('id'):
            await CommandAlias.filter(id=alias.pop('id')).update(**alias)
        else:
            await CommandAlias.create(**alias)
    return {
        'status': 0,
        'msg':    '命令别名保存成功'
    }


@route.get('/test_command_alias', response_class=JSONResponse, dependencies=[authentication()])
async def test_command_alias(group_id: str, message: str):
    all_alias = await CommandAlias.filter(Q(group_id=group_id) | Q(group_id='all')).order_by('priority')
    msg = modify_msg(all_alias, message)
    return {
        'status': 0,
        'msg':    '测试成功',
        'data':   {
            'new_msg': msg
        }
    }
