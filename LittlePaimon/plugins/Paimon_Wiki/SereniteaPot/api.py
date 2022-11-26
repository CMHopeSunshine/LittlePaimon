from typing import List, Union, Optional, Tuple

from LittlePaimon.database import PublicCookie, PrivateCookie
from LittlePaimon.utils import logger
from LittlePaimon.utils.requests import aiorequests

from pydantic import parse_obj_as
from .models import Item

HEADER = {
    'Host':            'api-takumi.mihoyo.com',
    'Origin':          'https://webstatic.mihoyo.com',
    'Connection':      'keep-alive',
    'Accept':          'application/json, text/plain, */*',
    'User-Agent':      'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
    'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
    'Referer':         'https://webstatic.mihoyo.com/',
    'Accept-Encoding': 'gzip, deflate, br'
}
CODE_API = 'https://api-takumi.mihoyo.com/event/e20200928calculate/v1/furniture/blueprint'
MATERIAL_API = 'https://api-takumi.mihoyo.com/event/e20200928calculate/v1/furniture/compute'


async def get_blueprint_data(share_code: int, user_id: Optional[str]) -> Tuple[Union[List[Item], str, int, None], Optional[str]]:
    cookies: List[Union[PrivateCookie, PublicCookie]] = []
    if user_id and (private_cookies := await PrivateCookie.filter(user_id=user_id, status=1).all()):
        cookies.extend(private_cookies)
    if public_cookies := await PublicCookie.filter(status__in=[1, 2]).all():
        cookies.extend(public_cookies)
    if not cookies:
        return None, None
    headers = HEADER.copy()
    for cookie in cookies:
        headers['Cookie'] = cookie.cookie
        resp = await aiorequests.get(CODE_API,
                                     params={
                                         'share_code': share_code
                                     },
                                     headers=headers)
        data = resp.json()
        if data['retcode'] == 0:
            items = parse_obj_as(List[Item], data['data']['list'])
            items.sort(key=lambda i: (i.num, i.level), reverse=True)
            logger.info('尘歌壶摹本', f'摹数<m>{share_code}</m>数据<g>获取成功</g>')
            return items, cookie.cookie
        elif data['retcode'] != -100:
            logger.info('尘歌壶摹本', f'摹数<m>{share_code}</m>数据<r>获取失败，{data["message"] or str(data["retcode"])}</r>')
            return data['message'] or str(data['retcode']), None
    logger.info('尘歌壶摹本', f'摹数<m>{share_code}</m>数据<r>获取失败，没有可用的Cookie</r>')
    return None, None


async def get_blueprint_material_data(items: List[Item], cookie: Optional[str]) -> Union[List[Item], str, int, None]:
    if cookie is None:
        return None
    item_list = {
        'list': [
            {
                'cnt': item.num,
                'id':  item.id
            } for item in items
        ]
    }
    headers = HEADER.copy()
    headers['Cookie'] = cookie
    resp = await aiorequests.post(MATERIAL_API,
                                  json=item_list,
                                  headers=headers)
    data = resp.json()
    if data['retcode'] == 0:
        items = parse_obj_as(List[Item], data['data']['list'])
        items.sort(key=lambda i: (i.num, i.level), reverse=True)
        return items
    elif data['retcode'] != -100:
        return data['message'] or str(data['retcode'])
    else:
        return None
