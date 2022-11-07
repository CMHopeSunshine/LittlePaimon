import datetime
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from LittlePaimon.config import ConfigManager, PluginManager, PluginInfo
from LittlePaimon.database import PluginPermission

try:
    from LittlePaimon.plugins.plugin_manager import cache_help
except Exception:
    cache_help = None

from .utils import authentication

route = APIRouter()


@route.get('/get_plugins', response_class=JSONResponse, dependencies=[authentication()])
async def get_plugins():
    plugins = await PluginManager.get_plugin_list_for_admin()
    return {
        'status': 0,
        'msg': 'ok',
        'data': {
            'rows': plugins,
            'total': len(plugins)
        }
    }


@route.post('/set_plugin_status', response_class=JSONResponse, dependencies=[authentication()])
async def set_plugin_status(data: dict):
    module_name = data.get('plugin')
    status = data.get('status')
    if cache_help:
        cache_help.clear()
    await PluginPermission.filter(name=module_name).update(status=status)
    return {'status': 0, 'msg': f'成功设置{module_name}插件状态为{status}'}


@route.get('/get_plugin_bans', response_class=JSONResponse, dependencies=[authentication()])
async def get_plugin_status(module_name: str):
    result = []
    bans = await PluginPermission.filter(name=module_name).all()
    for ban in bans:
        if ban.session_type == 'group':
            result.extend(f'群{ban.session_id}.{b}' for b in ban.ban)
            if not ban.status:
                result.append(f'群{ban.session_id}')
        elif ban.session_type == 'user' and not ban.status:
            result.append(f'{ban.session_id}')
    return {
        'status': 0,
        'msg':    'ok',
        'data':   {
            'module_name': module_name,
            'bans': result
        }
    }


@route.post('/set_plugin_bans', response_class=JSONResponse, dependencies=[authentication()])
async def set_plugin_bans(data: dict):
    bans = data['bans']
    name = data['module_name']
    await PluginPermission.filter(name=name).update(status=True, ban=[])
    for ban in bans:
        if ban.startswith('群'):
            if '.' in ban:
                group_id = int(ban.split('.')[0][1:])
                user_id = int(ban.split('.')[1])
                plugin = await PluginPermission.filter(name=name, session_type='group', session_id=group_id).first()
                plugin.ban.append(user_id)
                await plugin.save()
            else:
                await PluginPermission.filter(name=name, session_type='group', session_id=int(ban[1:])).update(
                    status=False)
        else:
            await PluginPermission.filter(name=name, session_type='user', session_id=int(ban)).update(status=False)
    if cache_help:
        cache_help.clear()
    return {
        'status': 0,
        'msg':    '插件权限设置成功'
    }


@route.post('/set_plugin_detail', response_class=JSONResponse, dependencies=[authentication()])
async def set_plugin_detail(plugin_info: PluginInfo):
    PluginManager.plugins[plugin_info.module_name] = plugin_info
    PluginManager.save()
    if cache_help:
        cache_help.clear()
    return {
        'status': 0,
        'msg':    '插件信息设置成功'
    }


@route.get('/get_config', response_class=JSONResponse, dependencies=[authentication()])
async def get_config():
    config = ConfigManager.config.dict(by_alias=True)
    config['米游社签到开始时间'] = datetime.datetime(1970, 1, 1, hour=config['米游社签到开始时间(小时)'], minute=config['米游社签到开始时间(分钟)']).strftime('%H:%M')
    config['米游币开始执行时间'] = datetime.datetime(1970, 1, 1, hour=config['米游币开始执行时间(小时)'], minute=config['米游币开始执行时间(分钟)']).strftime('%H:%M')
    config['实时便签停止检查时间段'] = (f'0{config["实时便签停止检查开始时间"]}' if config['实时便签停止检查开始时间'] < 10 else str(config['实时便签停止检查开始时间'])) + \
        ':00,' + (f'0{config["实时便签停止检查结束时间"]}' if config['实时便签停止检查结束时间'] < 10 else str(config['实时便签停止检查结束时间'])) + ':00'
    config['云原神签到开始时间'] = f'0{config["云原神签到时间(小时)"]}' if config['云原神签到时间(小时)'] < 10 else str(config['云原神签到时间(小时)'])
    return {
        'status': 0,
        'msg':    'ok',
        'data': config
    }


@route.post('/set_config', response_class=JSONResponse, dependencies=[authentication()])
async def set_config(data: dict):
    if '米游社签到开始时间' in data:
        temp_time = datetime.datetime.strptime(data['米游社签到开始时间'], '%H:%M')
        data['米游社签到开始时间(小时)'] = temp_time.hour
        data['米游社签到开始时间(分钟)'] = temp_time.minute
    if '米游币开始执行时间' in data:
        temp_time = datetime.datetime.strptime(data['米游币开始执行时间'], '%H:%M')
        data['米游币开始执行时间(小时)'] = temp_time.hour
        data['米游币开始执行时间(分钟)'] = temp_time.minute
    if '实时便签停止检查时间段' in data:
        temp_time_split = data['实时便签停止检查时间段'].split(',')
        data['实时便签停止检查开始时间'] = int(temp_time_split[0][:2])
        data['实时便签停止检查结束时间'] = int(temp_time_split[1][:2])
    if '云原神签到开始时间' in data:
        data['云原神签到时间(小时)'] = int(data['云原神签到开始时间'])
    ConfigManager.config.update(**data)
    ConfigManager.save()
    return {
        'status': 0,
        'msg':    '保存成功'
    }


@route.get('/env_config', response_class=JSONResponse, dependencies=[authentication()])
async def env_config(file_name: str):
    return {
        'status': 0,
        'msg':    'ok',
        'data':   {
            'data': (Path() / file_name).read_text(encoding='utf-8')
        }
    }


@route.post('/env_config', response_class=JSONResponse, dependencies=[authentication()])
async def env_config(file_name: str, data: dict):
    with open(Path() / file_name, 'w', encoding='utf-8') as f:
        f.write(data['editor'])
    return {
        'status': 0,
        'msg':    f'{file_name}文件保存成功'
    }