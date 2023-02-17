import random
from typing import Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    PrivateMessageEvent,
)
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

from LittlePaimon.config import config
from LittlePaimon.database import GenshinVoice
from LittlePaimon.utils.alias import get_match_alias
from LittlePaimon.utils.message import CommandCharacter, CommandLang, MessageBuild

from .handler import (
    GuessVoice,
    get_character_voice,
    get_rank,
    get_record,
    get_voice_list,
)
from .resources import update_voice_resources

__plugin_meta__ = PluginMetadata(
    name='原神语音',
    description='原神语音',
    usage='原神猜语音',
    extra={
        'author': '惜月',
        'version': '3.0',
        'priority': 6,
    },
)

guess_voice = on_command(
    '原神猜语音',
    priority=12,
    block=True,
    state={
        'pm_name': '原神猜语音',
        'pm_description': '原神猜语音小游戏',
        'pm_usage': '原神猜语音[语言][排行榜]',
        'pm_priority': 1,
    },
)
get_voice = on_command(
    '原神语音',
    priority=12,
    block=True,
    state={
        'pm_name': '原神语音',
        'pm_description': '获取指定角色的指定语音',
        'pm_usage': '原神语音<名|序号>[语言]',
        'pm_priority': 3,
    },
)
voice_list = on_command(
    '原神语音列表',
    priority=12,
    block=True,
    state={
        'pm_name': '原神语音列表',
        'pm_description': '查看角色的语音列表',
        'pm_usage': '原神语音列表<名><语言>',
        'pm_priority': 2,
    },
)
update_voice = on_command(
    '更新原神语音资源',
    priority=12,
    permission=SUPERUSER,
    block=True,
    state={
        'pm_name': '更新原神语音资源',
        'pm_description': '更新原神语音资源',
        'pm_usage': '更新原神语音资源',
        'pm_show': False,
        'pm_priority': 4,
    },
)


@guess_voice.handle()
async def _(
    bot: Bot, event: GroupMessageEvent, msg: Message = CommandArg(), lang=CommandLang()
):
    msg = msg.extract_plain_text().strip()
    if 'rank' in msg or '排行' in msg:
        result = await get_rank(event.group_id)
        await guess_voice.finish(result)
    else:
        game = GuessVoice(event.group_id, bot, config.guess_voice_time, lang)
        result = await game.start()
        await guess_voice.send(f'即将发送一段语音，将在{config.guess_voice_time}秒后公布答案')
        try:
            await guess_voice.finish(result)
        except ActionFailed:
            await game.end(exception=True)
            await guess_voice.finish('发送语音失败，请检查是否已安装FFmpeg')


@get_voice.handle()
async def _(
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    lang=CommandLang(),
    msg: Message = CommandArg(),
):
    msg = msg.extract_plain_text().strip().split(' ')[0]
    if msg.isdigit():
        voice = await GenshinVoice.get_or_none(id=int(msg))
        await get_voice.finish(
            await get_record(voice.voice_url)
            if voice
            else MessageBuild.Text(f'没有{msg}号原神语音')
        )
    else:
        if chara := get_match_alias(msg, ['角色'], True):
            chara = chara[0]
        else:
            await get_voice.finish(MessageBuild.Text(f'没有叫{chara}的角色'))
        voices = await GenshinVoice.filter(character=chara, language=lang).all()
        if voices:
            await get_voice.finish(await get_record(random.choice(voices).voice_url))
        else:
            await get_voice.finish(
                MessageBuild.Text(f'暂无{chara}的{lang}文语音资源，让超级用户[更新原神语音资源]吧！')
            )


@voice_list.handle()
async def _(
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    character=CommandCharacter(1),
    lang=CommandLang(),
):
    result = await get_voice_list(character[0], lang)
    await get_voice.finish(result)


@update_voice.handle()
async def _(event: MessageEvent):
    await update_voice.send('开始更新原神语音资源，请稍等...')
    result = await update_voice_resources()
    await update_voice.finish(result)
