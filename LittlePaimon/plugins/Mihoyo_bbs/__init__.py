from nonebot import on_regex
from nonebot.params import RegexMatched
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata

from LittlePaimon.utils import logger
from LittlePaimon.utils.browser import screenshot

__plugin_meta__ = PluginMetadata(
    name='米游社',
    description='米游社',
    usage='',
    extra={
        'author':   '惜月',
        'version':  '3.0',
        'priority': 20,
    }
)

post_screenshot = on_regex(r'(https://)?((m\.)?bbs.mihoyo|www.miyoushe).com/.+/article/\d+', priority=20, block=False, state={
    'pm_name':        '米游社帖子截图',
    'pm_description': '(被动技能)自动对消息中的米游社帖子链接内容进行截图发送',
    'pm_usage':       '米游社帖子截图',
    'pm_priority':    1
})


@post_screenshot.handle()
async def _(event: MessageEvent, url: str = RegexMatched()):
    logger.info('米游社', f'开始截图帖子<m>{url}</m>')
    try:
        img = await screenshot(url, elements=['.mhy-article-page__main'], timeout=180000)
    except Exception:
        logger.info('米游社', f'帖子<m>{url}</m>截图失败')
        await post_screenshot.finish('米游社帖子截图超时失败了~~')
    await post_screenshot.finish(MessageSegment.image(img))
