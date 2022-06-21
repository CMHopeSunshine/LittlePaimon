from urllib.parse import quote
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.plugin import PluginMetadata

from utils.auth_util import FreqLimiter
from utils.message_util import get_message_id
from utils.config import config
from utils import aiorequests


__plugin_meta__ = PluginMetadata(
    name="对对联",
    description="人工智能和你对对联",
    usage=(
        "对对联 <对联内容>"
    ),
    extra={
        'type':    '娱乐',
        'range':   ['private', 'group', 'guild'],
        "author":  "惜月 <277073121@qq.com>",
        "version": "1.0.0",
    },
)

couplets = on_command('对联', aliases={'对对联'}, priority=13, block=True)
couplets.__paimon_help__ = {
        "usage":  "对对联 <对联内容>",
        "introduce": "人工智能和你对对联",
        "priority": 8
    }

couplets_limit = FreqLimiter(config.paimon_couplets_cd)


@couplets.handle()
async def couplets_handler(event: MessageEvent, msg=CommandArg()):
    if not msg:
        await couplets.finish('请输入对联内容')
    if not couplets_limit.check(get_message_id(event)):
        await couplets.finish(f'对联冷却ing(剩余{couplets_limit.left_time(get_message_id(event))}秒)')
    else:
        msg = str(msg).split(' ')
        word = msg[0].strip()
        try:
            num = int(msg[1]) if len(msg) > 1 else 1
        except:
            num = 1
        num = num if num < 10 else 10
        couplets_limit.start_cd(get_message_id(event), config.paimon_couplets_cd)
        text = quote(str(word))
        url = f'https://seq2seq-couplet-model.rssbrain.com/v0.2/couplet/{text}'
        res = await aiorequests.get(url=url)
        res = res.json()
        result = ''
        for n in range(0, num):
            result += res['output'][n] + '\n'
        await couplets.finish(f'上联：{word}\n下联：{result}')