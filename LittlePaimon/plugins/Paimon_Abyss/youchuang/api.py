from typing import List, Tuple

from pydantic import parse_obj_as

from LittlePaimon.utils.requests import aiorequests
from .models import TeamRateResult, TeamRate

#  API均来自微信公众号`原神创意工坊`，感谢坊主提供的API
BASE_API = 'https://www.youchuang.fun'
TEAM_RATE_API = f'{BASE_API}/gamerole/formationRate'

VERSION_API = 'https://api-cloudgame-static.mihoyo.com/hk4e_cg_cn/gamer/api/getFunctionShieldNew?client_type=1'
VERSION = 3.7
HEADERS = {
    'Host':         'www.youchuang.fun',
    'Referer':      'https://servicewechat.com/wxce4dbe0cb0f764b3/91/page-frame.html',
    'User-Agent':   'Mozilla/5.0 (iPad; CPU OS 15_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                    'Mobile/15E148 MicroMessenger/8.0.20(0x1800142f) NetType/WIFI Language/zh_CN',
    'content-type': 'application/json'
}


# async def get_game_version() -> float:
#     data = await aiorequests.get(VERSION_API)
#     data = data.json()
#     return float(data['data']['config']['cg.key_function_queue_news']['versions'][0].replace('.0', ''))


async def get_team_rate() -> Tuple[TeamRateResult, float]:
    # version = await get_game_version()
    data_up = (await aiorequests.post(TEAM_RATE_API, json={
        'version': VERSION,
        'layer':   1
    }, headers=HEADERS)).json()['result']
    data_down = (await aiorequests.post(TEAM_RATE_API, json={
        'version': VERSION,
        'layer':   2
    }, headers=HEADERS)).json()['result']
    return TeamRateResult(rateListUp=parse_obj_as(List[TeamRate], data_up['rateList']),
                          rateListDown=parse_obj_as(List[TeamRate], data_down['rateList']),
                          userCount=data_up['userCount']), VERSION
