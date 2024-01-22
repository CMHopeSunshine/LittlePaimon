from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule

from LittlePaimon import SUPERUSERS
from LittlePaimon.config import config
from LittlePaimon.utils.browser import screenshot


async def permission_check(event: MessageEvent) -> bool:
    return config.screenshot_enable or event.user_id in SUPERUSERS


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

screenshot_cmd = on_command('网页截图', priority=10, block=True, rule=Rule(permission_check), state={
    'pm_name':        '网页截图',
    'pm_description': '对指定链接页面进行截图，例：【网页截图www.baidu.com】',
    'pm_usage':       '网页截图<链接>',
    'pm_priority':    1
})


@screenshot_cmd.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    await screenshot_cmd.send('正在尝试截图，请稍等...')
    url = msg.extract_plain_text().strip()
    try:
        img = await screenshot(url)
        await screenshot_cmd.send(MessageSegment.image(img))
    except Exception:
        await screenshot_cmd.send('尝试网页截图失败，无法访问该网页，请稍候再试')
