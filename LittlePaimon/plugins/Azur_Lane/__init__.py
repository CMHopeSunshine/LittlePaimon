from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule

from LittlePaimon import SUPERUSERS
from LittlePaimon.config import config
from LittlePaimon.utils.brower import blhx_screenshot

from urllib.parse import quote
import string

async def permission_check(event: MessageEvent) -> bool:
    return True if config.screenshot_enable else event.user_id not in SUPERUSERS


__plugin_meta__ = PluginMetadata(
    name='碧蓝航线wiki',
    description='碧蓝航线wiki',
    usage='',
    extra={
        'author':   '(๑•小丫头片子•๑)',
        'version':  '0.1',
        'priority': 99,
    }
)

screenshot_cmd = on_command('碧蓝航线wiki', priority=10, block=True, rule=Rule(permission_check), state={
    'pm_name':        '碧蓝航线wiki',
    'pm_description': '截图获取碧蓝任意角色武器或其它模块的wiki',
    'pm_usage':       '碧蓝航线wiki<角色名|武器名|其它>',
    'pm_priority':    1
})


@screenshot_cmd.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    url1 = 'https://wiki.biligame.com/blhx/'
    url2 = msg.extract_plain_text().strip()
    url = url1 + url2
    url = quote(url, safe = string.printable)
    await screenshot_cmd.send(f'正在尝试获取wiki，请稍等...更多信息请访问原文{url}')
    try:
        img = await blhx_screenshot(url)
        await screenshot_cmd.send(MessageSegment.image(img))
    except Exception:
        await screenshot_cmd.send('wiki获取失败，无法访问该网页，请稍候再试')
