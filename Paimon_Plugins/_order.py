import random

from littlepaimon_utils import aiorequests
from littlepaimon_utils.tools import FreqLimiter
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

"""
由于点餐api已经失效，本功能暂不可用，直到找到其他可用的点餐api
"""

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
        "version": "1.0.0",
    },
)

order_pic = on_command('点菜', aliases={'点餐', '食谱', '我想吃'}, priority=13, block=True)
order_pic.__paimon_help__ = {
    "usage":     "点餐<食品名>",
    "introduce": "群主，来一份派蒙！",
    "priority": 11
}

order_lmt = FreqLimiter(10)


@order_pic.handle()
async def order_pic_handler(event: MessageEvent, msg=CommandArg()):
    msg = str(msg).strip()
    if not msg:
        return
    if not order_lmt.check(event.user_id):
        await order_pic.finish(f'点餐冷却ing(剩余{order_lmt.left_time(event.user_id)}秒)')
    else:
        url = 'https://api.iyk0.com/shipu/?key=' + msg
        res = await aiorequests.get(url=url)
        res = res.json()
        if res['code'] == 202:
            await order_pic.finish('没有找到这种食品哦~')
        order_lmt.start_cd(event.user_id, 10)
        number = random.randint(1, 3)
        recipe_list = []
        for i in range(0, number):
            recipe = random.choice(res['data'])
            if recipe not in recipe_list:
                recipe_list.append(recipe)
        mes = Message()
        for recipe in recipe_list:
            mes += MessageSegment.text(recipe['name'] + '\n') + MessageSegment.image(recipe['img']) + '\n'
        await order_pic.finish(mes, at_sender=True)
