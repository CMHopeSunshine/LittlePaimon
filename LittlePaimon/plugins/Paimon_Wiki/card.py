import contextlib
import difflib
from LittlePaimon.utils import scheduler
from LittlePaimon.utils.requests import aiorequests

card_list = []
CARD_RESOURCES_API = 'https://api.github.com/repos/Nwflower/genshin-atlas/contents/card'
CARD_API = 'https://ghproxy.com/https://raw.githubusercontent.com/Nwflower/genshin-atlas/master/card/{}.png'


async def update_card_list():
    with contextlib.suppress(Exception):
        resp = await aiorequests.get(CARD_RESOURCES_API)
        if resp.status_code == 200:
            for card in resp.json():
                if (name := card['name'].replace('.png', '')) not in card_list:
                    card_list.append(name)
    return None


async def get_card_list():
    if not card_list:
        await update_card_list()
    return '七圣召唤原牌列表：\n' + '\n'.join([' '.join(card_list[i:i + 3]) for i in range(0, len(card_list), 3)])


async def get_match_card(name: str):
    if not card_list:
        await update_card_list()
    return difflib.get_close_matches(name, card_list, cutoff=0.6, n=10) if card_list else None


@scheduler.scheduled_job('cron', minute='*/30')
async def _():
    await update_card_list()
