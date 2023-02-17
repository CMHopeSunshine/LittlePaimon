import contextlib
import difflib
from typing import Optional

from ruamel import yaml
from LittlePaimon.config import config
from LittlePaimon.utils.requests import aiorequests

CARD_RESOURCES_API = '{proxy}https://raw.githubusercontent.com/Nwflower/genshin-atlas/master/index/card.yaml'
CARD_API = '{proxy}https://raw.githubusercontent.com/Nwflower/genshin-atlas/master/{name}'
RESOURCES_API = '{proxy}https://raw.githubusercontent.com/Nwflower/genshin-atlas/master/path.json'


async def get_card_resources() -> Optional[dict]:
    with contextlib.suppress(Exception):
        resp = await aiorequests.get(CARD_RESOURCES_API.format(proxy=config.github_proxy))
        data = yaml.load(resp.content, Loader=yaml.Loader)
        data.pop('召唤')
        return data
    return None


async def get_atlas_full_path(name: str, type: str) -> str:
    with contextlib.suppress(Exception):
        resp = await aiorequests.get(RESOURCES_API.format(proxy=config.github_proxy))
        data = resp.json()
        return data[type][name]
    return name


async def get_match_card(name: str) -> Optional[list]:
    if not (data := await get_card_resources()):
        return None
    matches = []
    if name == '全部':
        return data
    for cards in data.values():
        matches.extend(difflib.get_close_matches(name, cards, cutoff=0.6, n=10))
    return matches


async def get_all_specialty() -> Optional[list]:
    with contextlib.suppress(Exception):
        resp = await aiorequests.get(RESOURCES_API.format(proxy=config.github_proxy))
        return resp.json()['specialty'].keys()
    return None


async def get_match_specialty(name: str) -> Optional[list]:
    with contextlib.suppress(Exception):
        resp = await aiorequests.get(RESOURCES_API.format(proxy=config.github_proxy))
        data = resp.json()['specialty']
        return (
            difflib.get_close_matches(name, list(data.keys()), cutoff=0.6, n=10)
            if name != '全部'
            else list(data.keys())
        )
    return None
