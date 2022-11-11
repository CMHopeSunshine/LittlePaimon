import datetime
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from LittlePaimon.database import PublicCookie, PrivateCookie, LastQuery, CookieCache
from LittlePaimon.utils.api import get_bind_game_info, get_stoken_by_cookie
from .utils import authentication

route = APIRouter()


class BindCookie(BaseModel):
    id: Optional[int]
    user_id: Optional[int]
    uid: Optional[int]
    mys_id: Optional[int]
    cookie: str
    stoken: Optional[str]


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


@route.post('/set_public_cookie', response_class=JSONResponse, dependencies=[authentication()])
async def set_public_cookie(id: int):
    cookie = await PublicCookie.get_or_none(id=id)
    if cookie.status != 3:
        await CookieCache.filter(cookie=cookie.cookie).delete()
        cookie.status = 3
        await cookie.save()
        return {
            'status': 0,
            'msg': f'{id}号公共Cookie暂停使用成功'
        }
    else:
        cookie.status = 1
        await cookie.save()
        return {
            'status': 0,
            'msg': f'{id}号公共Cookie恢复使用成功'
        }


@route.get('/get_private_cookies', response_class=JSONResponse, dependencies=[authentication()])
async def get_private_cookies(
        page: int = 1,
        perPage: int = 10,
        orderBy: str = 'id',
        orderDir: str = 'asc',
        status: Optional[int] = None,
        user_id: Optional[int] = None,
        uid: Optional[int] = None,
        mys_id: Optional[int] = None):
    orderBy = orderBy if orderDir == 'asc' else f'-{orderBy}' if orderBy else 'id'
    query = {f'{k}__contains': v for k, v in {'user_id': user_id, 'uid': uid, 'mys_id': mys_id}.items() if
             v is not None}
    if status is not None:
        query['status'] = status
    return {
        'status': 0,
        'msg':    'ok',
        'data':   {
            'items': await PrivateCookie.filter(**query).order_by(orderBy).offset((page - 1) * perPage).limit(
                perPage).values(),
            'total': await PrivateCookie.filter(**query).count()
        }
    }


@route.get('/get_private_cookie', response_class=JSONResponse, dependencies=[authentication()])
async def get_private_cookie(id: int):
    return await PrivateCookie.get_or_none(id=id).values()


@route.delete('/delete_cookie', response_class=JSONResponse, dependencies=[authentication()])
async def delete_public_cookie(cookie_type: str, id: int):
    if cookie_type == 'public':
        cookie = await PublicCookie.get(id=id)
        await CookieCache.filter(cookie=cookie.cookie).delete()
        await cookie.delete()
        return {'status': 0, 'msg': f'{id}号公共Cookie删除成功'}
    else:
        await PrivateCookie.filter(id=id).delete()
        return {'status': 0, 'msg': f'{id}号私人Cookie删除成功'}


@route.post('/add_cookie', response_class=JSONResponse, dependencies=[authentication()])
async def add_public_cookie(cookie_type: str, force: bool, data: BindCookie):
    if cookie_type == 'public':
        if force or await get_bind_game_info(data.cookie, True):
            new_cookie = await PublicCookie.create(cookie=data.cookie)
            return {'status': 0, 'msg': f'{new_cookie.id}号公共Cookie添加成功'}
        elif not force:
            return {'status': 200, 'msg': '该Cookie无效，请根据教程重新获取'}
    else:
        if force:
            await PrivateCookie.update_or_create(user_id=data.user_id, uid=data.uid, mys_id=data.mys_id,
                                                 defaults={'cookie': data.cookie, 'stoken': data.stoken})
            return {'status': 0, 'msg': f'QQ{data.user_id}的UID{data.uid}的Cookie强制修改成功。'}
        elif game_info := await get_bind_game_info(data.cookie):
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


@route.post('/update_private_cookie', response_class=JSONResponse, dependencies=[authentication()])
async def update_cookie(force: bool, data: BindCookie):
    if force:
        await PrivateCookie.filter(id=data.id).update(**data.dict(exclude={'id'}))
        return {'status': 0, 'msg': f'QQ{data.user_id}的UID{data.uid}的Cookie强制修改成功。'}
    elif game_info := await get_bind_game_info(data.cookie):
        game_uid = game_info['game_role_id']
        mys_id = game_info['mys_id']
        await LastQuery.update_or_create(user_id=data.user_id,
                                         defaults={'uid': game_uid, 'last_time': datetime.datetime.now()})
        if 'login_ticket' in data.cookie and (stoken := await get_stoken_by_cookie(data.cookie)):
            await PrivateCookie.filter(id=data.id).update(user_id=data.user_id, uid=game_uid, mys_id=mys_id,
                                                          cookie=data.cookie, stoken=f'stuid={mys_id};stoken={stoken};')
            return {'status': 0, 'msg': f'QQ{data.user_id}的UID{game_uid}的Cookie以及Stoken添加/保存成功。'}
        else:
            await PrivateCookie.filter(id=data.id).update(user_id=data.user_id, uid=game_uid, mys_id=mys_id,
                                                          cookie=data.cookie, stoken=None)
            return {'status': 0, 'msg': f'QQ{data.user_id}的UID{game_uid}的Cookie添加/保存成功，但未获取到stoken。'}
    else:
        return {'status': 200, 'msg': '该Cookie无效，请根据教程重新获取'}