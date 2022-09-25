from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.plugin import PluginMetadata

from LittlePaimon.utils.brower import AsyncPlaywright

__plugin_meta__ = PluginMetadata(
    name='实用工具',
    description='一些实用的工具插件',
    usage='',
    extra={
        'author':   '惜月',
        'version':  '3.0',
        'priority': 99,
    }
)

screenshot_cmd = on_command('网页截图', priority=10, block=True, state={
    'pm_name':        '网页截图',
    'pm_description': '对指定链接页面进行截图，例：【网页截图www.baidu.com】，可选指定网页元素',
    'pm_usage':       '网页截图<链接> [元素]',
    'pm_priority':    1
})


@screenshot_cmd.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    await screenshot_cmd.send('正在尝试截图，请稍等...')
    msg = msg.extract_plain_text().strip().split(' ')
    url = msg[0]
    element = msg[1:] if len(msg) > 1 else None
    img = await AsyncPlaywright.screenshot(url, element=element)
    await screenshot_cmd.finish(img)
