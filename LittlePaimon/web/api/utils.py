import datetime
from typing import Optional

from fastapi import Header, HTTPException, Depends
from jose import jwt

from LittlePaimon.utils import SUPERUSERS
from LittlePaimon.config import config

SECRET_KEY = config.secret_key
ALGORITHM = 'HS256'
TOKEN_EXPIRE_MINUTES = 30


def authentication():
    def inner(token: Optional[str] = Header(...)):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            if not (user_id := payload.get('user_id')) or int(user_id) not in SUPERUSERS:
                raise HTTPException(status_code=400, detail='登录验证失败或已失效，请重新登录')
        except (jwt.JWTError, jwt.ExpiredSignatureError, AttributeError):
            raise HTTPException(status_code=400, detail='登录验证失败或已失效，请重新登录')

    return Depends(inner)


def create_token(user_id: int):
    data = {'user_id': user_id, 'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=TOKEN_EXPIRE_MINUTES)}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
