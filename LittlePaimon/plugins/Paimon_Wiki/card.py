import contextlib
import difflib
from typing import Optional

from ruamel import yaml
from LittlePaimon.config import config
from LittlePaimon.utils.requests import aiorequests

CARD_RESOURCES_API = '{}https://raw.githubusercontent.com/Nwflower/Atlas/master/resource/text/card.yaml'
CARD_API = '{}https://raw.githubusercontent.com/Nwflower/genshin-atlas/master/card/{}.png'


async def get_card_resources() -> Optional[dict]:
    with contextlib.suppress(Exception):
        resp = await aiorequests.get(CARD_RESOURCES_API.format(config.github_proxy))
        data = yaml.load(resp.content, Loader=yaml.Loader)
        data.pop('召唤')
        return data
    return None


async def get_match_card(name: str):
    if not (data := await get_card_resources()):
        return None
    matches = []
    for cards in data.values():
        matches.extend(difflib.get_close_matches(name, cards, cutoff=0.6, n=10))
    return matches
