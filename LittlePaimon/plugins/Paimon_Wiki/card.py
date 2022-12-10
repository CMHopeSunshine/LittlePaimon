import contextlib
import difflib
import re
from typing import Optional

from ruamel import yaml
from LittlePaimon.config import config
from LittlePaimon.utils.requests import aiorequests

CARD_RESOURCES_API = '{}https://raw.githubusercontent.com/Nwflower/Atlas/master/resource/text/card.yaml'
CARD_API = '{}https://raw.githubusercontent.com/Nwflower/genshin-atlas/master/card/{}.png'
card_pic_url = "https://raw.githubusercontent.com/KimigaiiWuyi/GenshinUID/main/GenshinUID/genshinuid_guide/card/"
card_dict ={}

punctuation = '！？!,;:?"\''


def removePunctuation(text):
    punc = '~`!#$%^&*()_+-=|\';":/.,?><~·！@#￥%……&*（）——+-=“：’；、。，？》《{}'
    text = re.sub(r"[%s]+" %punc, "",text)
    return text


def convert_name(Chinese_name):
    Chinese_word = ["食物", '道具', '伙伴', '地点', '事件', '武器', '角色', '共鸣', '圣遗物']
    English_word = ['food', 'support', 'support', 'support',
                    'event', 'weapon', 'char', 'with', 'artifact']
    English_name = str(Chinese_name)
    for i in range(0, len(Chinese_word)):
        English_name = English_name.replace(Chinese_word[i], English_word[i])
    return English_name


async def get_card_resources() -> Optional[dict]:
    with contextlib.suppress(Exception):
        resp = await aiorequests.get(CARD_RESOURCES_API.format(config.github_proxy))
        data = yaml.load(resp.content, Loader=yaml.Loader)
        data.pop('召唤')
        global card_dict
        card_dict = data
        return data
    return None


async def get_match_card(name: str):
    if not (data := await get_card_resources()):
        return None
    matches = []
    for cards in data.values():
        matches.extend(difflib.get_close_matches(name, cards, cutoff=0.6, n=10))
    return matches


def get_card_pic(name: str):
    keylist = list(card_dict)
    for key in keylist:
        for value in card_dict[key]:
            if (value == name):
                picurl = card_pic_url
                picurl += convert_name(key) + "/"
                picurl += removePunctuation(name) + ".jpg"        
    return picurl
