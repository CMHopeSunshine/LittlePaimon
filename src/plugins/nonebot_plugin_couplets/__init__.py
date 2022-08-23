from typing import List

import httpx
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.adapters.onebot.v11.helpers import Numbers
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

__plugin_meta__ = PluginMetadata(
    name="对对联",
    description="人工智能和你对对联",
    usage="对联<内容>(数量)",
    extra={
        'type':    '娱乐',
        "author":  "惜月 <277073121@qq.com>",
        "version": "1.0.0",
    },
)

couplets = on_command('对联', aliases={'对对联'}, priority=13, block=True, state={
    'pm_usage': '对联<内容>(数量)',
    'pm_describe': '人工智能和你对对联',
    'pm_priority': 15
})


@couplets.handle()
async def _(event: MessageEvent, state: T_State, msg: Message = CommandArg(), num: List[float] = Numbers()):
    msg = msg.extract_plain_text().strip()
    if msg:
        for n in num:
            msg = msg.replace(str(int(n)), '')
    if msg:
        state['text'] = msg
    if num:
        state['num'] = int(num[0]) if num[0] <= 10 else 10
    else:
        state['num'] = 1


@couplets.got('text', prompt='请输入上联内容')
async def couplets_handler(event: MessageEvent, state: T_State):
    url = f'https://seq2seq-couplet-model.rssbrain.com/v0.2/couplet/{state["text"]}'
    async with httpx.AsyncClient() as client:
        res = await client.get(url=url)
    res = res.json()
    result = '\n'.join(['➤' + res['output'][n] for n in range(state['num'])])
    await couplets.finish(f'上联：\n➤{state["text"]}\n下联：\n{result}')
