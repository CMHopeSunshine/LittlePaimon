import random
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from ..utils.util import FreqLimiter
from ..utils.http_util import aiorequests

order_pic = on_command('点菜', aliases={'点餐', '食谱', '我想吃'}, priority=13, block=True)
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
