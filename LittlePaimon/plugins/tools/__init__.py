from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.rule import Rule
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata
from LittlePaimon import SUPERUSERS
from LittlePaimon.manager.plugin_manager import plugin_manager as pm
from LittlePaimon.utils.brower import get_browser


async def permission_check(event: MessageEvent) -> bool:
    if pm.config.screenshot_enable:
        return True
    return event.user_id not in SUPERUSERS and event.sender.role not in ['admin', 'owner']


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

baidu_cmd = on_command('百度一下', priority=10, block=True, state={
    'pm_name':        '百度一下',
    'pm_description': '百度一下，你就知道',
    'pm_usage':       '百度一下<关键词>',
    'pm_priority':    2
})


@screenshot_cmd.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    await screenshot_cmd.send('正在尝试截图，请稍等...')
    url = msg.extract_plain_text().split(' ')[0]
    try:
        brower = await get_browser()
        page = await brower.new_page()
        await page.goto(url, wait_until='networkidle')
        img = await page.screenshot(full_page=True)
        await screenshot_cmd.send(MessageSegment.image(img))
    except Exception:
        await screenshot_cmd.finish('截图失败，无法访问该网页，请稍后再试')


@baidu_cmd.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    await baidu_cmd.send('正在为你百度，请稍等...')
    keyword = msg.extract_plain_text()
    try:
        brower = await get_browser()
        page = await brower.new_page()
        await page.goto(f'https://www.baidu.com/s?wd={keyword}', wait_until='networkidle', timeout=15000)
        context = await page.query_selector('#content_left')
        img = await context.screenshot()
        await baidu_cmd.send(MessageSegment.image(img))
    except Exception:
        await baidu_cmd.finish('百度失败，请稍后再试')

