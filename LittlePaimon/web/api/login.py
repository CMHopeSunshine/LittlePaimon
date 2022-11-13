from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from LittlePaimon.utils import SUPERUSERS
from LittlePaimon.config import config
from .utils import create_token

PASSWORD = config.admin_password


class UserModel(BaseModel):
    user_id: int
    password: str


route = APIRouter()


@route.post('/login', response_class=JSONResponse)
async def login(user: UserModel):
    if user.user_id not in SUPERUSERS or user.password != PASSWORD:
        return {
            'status': -100,
            'msg':    '登录失败，请确认用户ID和密码无误'
        }
    token = create_token(user.user_id)
    return {
        'status': 0,
        'msg':    '登录成功',
        'data':   {
            'token': token
        }
    }
