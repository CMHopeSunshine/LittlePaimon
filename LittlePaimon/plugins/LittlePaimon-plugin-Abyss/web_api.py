import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from .config import ConfigManager
from LittlePaimon.web.api import BaseApiRouter
from LittlePaimon.web.api.utils import authentication

route = APIRouter()

@route.get('/abyss_config_g', response_class=JSONResponse, dependencies=[authentication()])
async def abyss_config_g():
    config = ConfigManager.config.dict(by_alias=True)
    config['验证米游社签到开始时间'] = datetime.datetime(1970, 1, 1, hour=config['验证米游社签到开始时间(小时)'], minute=config['验证米游社签到开始时间(分钟)']).strftime('%H:%M')
    config['验证米游币开始执行时间'] = datetime.datetime(1970, 1, 1, hour=config['验证米游币开始执行时间(小时)'], minute=config['验证米游币开始执行时间(分钟)']).strftime('%H:%M')
    return {
        'status': 0,
        'msg':    'ok',
        'data': config
    }

@route.post('/abyss_config', response_class=JSONResponse, dependencies=[authentication()])
async def abyss_config(data: dict):
    if '验证米游社签到开关' in data:
        temp_time = datetime.datetime.strptime(data['验证米游社签到开始时间'], '%H:%M')
        data['验证米游社签到开始时间(小时)'] = temp_time.hour
        data['验证米游社签到开始时间(分钟)'] = temp_time.minute
    if '验证米游币获取开关' in data:
        temp_time = datetime.datetime.strptime(data['验证米游币开始执行时间'], '%H:%M')
        data['验证米游币开始执行时间(小时)'] = temp_time.hour
        data['验证米游币开始执行时间(分钟)'] = temp_time.minute
    ConfigManager.config.update(**data)
    ConfigManager.save()
    return {
        'status': 0,
        'msg':    '保存成功'
    }

BaseApiRouter.include_router(route)