import inspect
import json
import os
import random
import re
import sys
from typing import Dict, TypedDict

import aiohttp
import lxml.html
from littlepaimon_utils.tools import FreqLimiter
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata


__plugin_meta__ = PluginMetadata(
    name="点餐",
    description="点餐查看食物图片",
    usage=(
        "点餐 食物名"
    ),
    extra={
        'type':    '娱乐',
        'range':   ['private', 'group', 'guild'],
        "author":  "惜月 <277073121@qq.com>",
        "version": "1.0.1",
    },
)

order_pic = on_command('点菜', aliases={'点餐', '食谱', '我想吃'}, priority=13, block=True)
order_pic.__paimon_help__ = {
    "usage":     "点餐<食品名>",
    "introduce": "群主，来一份派蒙！",
    "priority": 11
}

order_lmt = FreqLimiter(10)
PATH_ROOT = os.path.dirname(os.path.abspath(__file__))
PATH_CONFIG = os.path.join(PATH_ROOT, 'config.json')


class TypeFood(TypedDict):
    name:  str
    image: str

class base():
    def __init__(self):
        self.default_haaders = {
            'User-Agent':      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
            'Accept':          'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
        }

    async def request(self, method: str, url: str, ctype: str, **kwargs) -> str:
        async with aiohttp.ClientSession(headers=self.default_haaders, raise_for_status=True) as session:
            async with session.request(method, url, **kwargs) as resp:
                if ctype == 'text':
                    ret = await resp.text()
                elif ctype == 'json':
                    ret = await resp.json(content_type=None)
                else:
                    raise Exception('Unknow content type')
        return ret

    async def order(self, name: str) -> TypeFood:
        raise NotImplementedError


# 心食谱
class xinshipu(base):

    URL_QUERY = 'https://www.xinshipu.com/doSearch.html?q=%s'

    async def order(self, name: str) -> TypeFood:
        text = await self.request('GET', self.URL_QUERY % name, 'text')
        html = lxml.html.fromstring(text)
        nodes = html.cssselect('a.shipu > div.v-pw > img')
        if not nodes:
            return {}
        node = random.choice(nodes)
        image = node.get('src')
        image_new = re.sub('@196w_126h_99q_1e_1c.jpg', '', image)
        return {
            'name':  node.get('alt'),
            'image': 'https:' + image_new,
        }


def load_config(filename: str) -> Dict:
    if not os.path.isfile(filename):
        return {}
    with open(filename, 'r') as f:
        return json.load(f)

config = load_config(PATH_CONFIG)

waiters = dict(filter(
    lambda x: issubclass(x[1], base) and x[1] != base,
    inspect.getmembers(sys.modules[__name__], inspect.isclass)
))
waiter = waiters[config.get('source', 'xinshipu')]() # 使用心食谱进行点餐


@order_pic.handle()
async def order_pic_handler(event: MessageEvent, msg=CommandArg()):
    msg = str(msg).strip()
    info = await waiter.order(msg)
    print(info)
    if not msg:
        return
    if not order_lmt.check(event.user_id):
        await order_pic.finish(f'点餐冷却ing(剩余{order_lmt.left_time(event.user_id)}秒)')
    else:
        if info.get('image'):
            image = info['image']
            msg_ = MessageSegment.image(image) + info.get('name', '')
            await order_pic.send(msg_, at_sender=True)
            order_lmt.start_cd(event.user_id, 10)
        else:
            await order_pic.finish('派蒙没有找到这种食品哦')
