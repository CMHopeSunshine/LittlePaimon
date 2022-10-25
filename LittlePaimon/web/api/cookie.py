import datetime
from typing import Optional
from LittlePaimon.database.models import PublicCookie, PrivateCookie, LastQuery
from fastapi.responses import JSONResponse
from fastapi import APIRouter
from pydantic import BaseModel

from LittlePaimon.utils.api import get_bind_game_info, get_stoken_by_cookie
from .utils import authentication

route = APIRouter()


class BindCookie(BaseModel):
    user_id: int
    cookie: str


@route.post('/bind_cookie', response_class=JSONResponse)
async def bind_cookie(data: BindCookie):
    if game_info := await get_bind_game_info(data.cookie):
        game_uid = game_info['game_role_id']
        mys_id = game_info['mys_id']
        await LastQuery.update_or_create(user_id=data.user_id,
                                         defaults={'uid': game_uid, 'last_time': datetime.datetime.now()})
        if 'login_ticket' in data.cookie and (stoken := await get_stoken_by_cookie(data.cookie)):
            await PrivateCookie.update_or_create(user_id=data.user_id, uid=game_uid, mys_id=mys_id,
                                                 defaults={'cookie': data.cookie,
                                                           'stoken': f'stuid={mys_id};stoken={stoken};'})
            return {'status': 0, 'msg': f'QQ{data.user_id}的UID{game_uid}的Cookie以及Stoken绑定成功。'}
        else:
            await PrivateCookie.update_or_create(user_id=data.user_id, uid=game_uid, mys_id=mys_id,
                                                 defaults={'cookie': data.cookie})
            return {'status': 0, 'msg': f'QQ{data.user_id}的UID{game_uid}绑定Cookie成功，但未绑定stoken。'}
    else:
        return {'status': 200, 'msg': '该Cookie无效，请根据教程重新获取'}


@route.get('/get_public_cookies', response_class=JSONResponse, dependencies=[authentication()])
async def get_public_cookies(status: Optional[int] = None):
    if status is None:
        return await PublicCookie.all().values()
    else:
        return await PublicCookie.filter(status=status).values()


@route.get('/get_private_cookies', response_class=JSONResponse, dependencies=[authentication()])
async def get_private_cookies(page: int = 1, perPage: int = 10, user_id: Optional[str] = None,
                              uid: Optional[str] = None, mys_id: Optional[str] = None, status: Optional[int] = None):
    query = {'user_id__contains': user_id} if user_id else {'uid__contains': uid} if uid else {
        'mys_id__contains': mys_id} if mys_id else {}
    if status is not None:
        query['status'] = status
    data = await PrivateCookie.filter(**query).offset((page - 1) * perPage).limit(perPage).values()
    return {
        'status': 0,
        'msg':    'ok',
        'data':   {
            'items': data,
            'total': await PrivateCookie.filter(**query).count()
        }
    }


@route.get('/get_private_cookie', response_class=JSONResponse, dependencies=[authentication()])
async def get_private_cookie(id: int):
    return await PrivateCookie.get_or_none(id=id).values()


@route.delete('/delete_public_cookie', response_class=JSONResponse, dependencies=[authentication()])
async def delete_public_cookie(id: int):
    await PublicCookie.filter(id=id).delete()
    return {'status': 0, 'msg': f'{id}号公共Cookie删除成功'}


@route.delete('/delete_private_cookie', response_class=JSONResponse, dependencies=[authentication()])
async def delete_private_cookie(id: int):
    await PrivateCookie.filter(id=id).delete()
    return {'status': 0, 'msg': f'{id}号私人Cookie删除成功'}


@route.post('/add_public_cookie', response_class=JSONResponse, dependencies=[authentication()])
async def add_public_cookie(data: dict):
    cookie = data.get('cookie')
    if not cookie:
        return {'status': 100, 'msg': '参数错误'}
    if await get_bind_game_info(cookie, True):
        new_cookie = await PublicCookie.create(cookie=cookie)
        return {'status': 0, 'msg': f'{new_cookie.id}号公共Cookie添加成功'}
    else:
        return {'status': 200, 'msg': '该Cookie无效'}


@route.post('/save_private_cookie', response_class=JSONResponse, dependencies=[authentication()])
async def save_private_cookie(data: BindCookie):
    if game_info := await get_bind_game_info(data.cookie):
        game_uid = game_info['game_role_id']
        mys_id = game_info['mys_id']
        await LastQuery.update_or_create(user_id=data.user_id,
                                         defaults={'uid': game_uid, 'last_time': datetime.datetime.now()})
        if 'login_ticket' in data.cookie and (stoken := await get_stoken_by_cookie(data.cookie)):
            await PrivateCookie.update_or_create(user_id=data.user_id, uid=game_uid, mys_id=mys_id,
                                                 defaults={'cookie': data.cookie,
                                                           'stoken': f'stuid={mys_id};stoken={stoken};'})
            return {'status': 0, 'msg': f'QQ{data.user_id}的UID{game_uid}的Cookie以及Stoken添加/保存成功。'}
        else:
            await PrivateCookie.update_or_create(user_id=data.user_id, uid=game_uid, mys_id=mys_id,
                                                 defaults={'cookie': data.cookie})
            return {'status': 0, 'msg': f'QQ{data.user_id}的UID{game_uid}的Cookie添加/保存成功，但未绑定stoken。'}
    else:
        return {'status': 200, 'msg': '该Cookie无效，请根据教程重新获取'}
