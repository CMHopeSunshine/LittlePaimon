import asyncio
from pathlib import Path
from typing import Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, MessageSegment, Bot, MessageEvent, \
    Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

from utils.config import config
from . import download_data
from . import util
from .handler import Guess, get_random_voice

setting_time = config.paimon_guess_voice  # 游戏持续时间

dir_name = Path() / 'data' / 'LittlePaimon' / 'guess_voice' / 'voice'


__plugin_meta__ = PluginMetadata(
    name="原神猜语音",
    description="小派蒙的原神猜语音模块",
    usage=(
        "原神猜语音[语言]\n"
        "原神语音[语言]<角色名>\n"
        "更新原神语音资源\n"
    ),
    extra={
        'type':    '娱乐',
        'range':   ['private', 'group'],
        "author":  "惜月 <277073121@qq.com>",
        "version": "1.0.0",
    },
)

guess_game = on_command('原神猜语音', priority=12, block=True)
guess_game.__paimon_help__ = {
    "usage":     "原神猜语音[语言]",
    "introduce": "来一起猜语音吧",
    "priority":  5
}
ys_voice = on_command('原神语音', priority=12, block=True)
ys_voice.__paimon_help__ = {
    "usage":     "原神语音[语言]<角色名>",
    "introduce": "随机发一条该角色的语音",
    "priority":  6
}
update_ys_voice = on_command('更新原神语音资源', priority=12, permission=SUPERUSER, block=True)


async def download_voice(bot: Bot, event: MessageEvent):
    if not dir_name.exists():
        dir_name.mkdir(parents=True, exist_ok=True)
        await bot.send(event, '资源尚未初始化，现在开始下载资源，这需要较长的时间，请耐心等待')
        await download_data.update_voice_data()
        await bot.send(event, '资源下载完成，请重新发送指令开始游戏')


@guess_game.handle()
async def guess_genshin_voice(bot: Bot, event: GroupMessageEvent, msg: Message = CommandArg()):
    await download_voice(bot, event)
    keyword = msg.extract_plain_text().strip()
    guess = Guess(event.group_id, time=setting_time)

    hard_mode = False

    if keyword == '排行榜':
        await guess_game.finish(await guess.get_rank(bot, event))
    if keyword in ['中', '中国', '汉语', '中文', '中国话', 'Chinese', 'cn'] or not keyword:
        keyword = '中'
    elif keyword in ['日', '日本', '日语', '霓虹', '日本语', 'Japanese', 'jp']:
        keyword = '日'
    elif keyword in ['韩', '韩国', '韩语', '棒子', '南朝鲜', '南朝鲜语']:
        keyword = '韩'
    elif keyword in ['英', '英文', '英语', '洋文', 'English', 'en']:
        keyword = '英'
    elif keyword in ['2', '难', '困难', '地狱']:
        hard_mode = True
    else:
        await guess_game.finish(f'没有找到{keyword}的语音')
    if guess.is_start():
        await guess_game.finish('游戏正在进行中哦')
    guess.set_start()
    await guess_game.send(f'即将发送一段原神语音,将在{setting_time}秒后公布答案')
    await asyncio.sleep(1)
    try:
        if hard_mode:
            await guess_game.finish(await guess.start2())
        else:
            res = await guess.start(keyword.split())
            await guess_game.finish(res)
    except FinishedException:
        pass
    except Exception as e:
        guess.set_end()
        await guess_game.finish('出错了，可能是该角色缺少语音资源：' + str(e))


@ys_voice.handle()
async def get_genshin_voice(bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent], msg: Message = CommandArg()):
    name = msg.extract_plain_text().strip()
    if name.startswith('日'):
        language = '日'
        name = name[1:]
    elif name.startswith('韩'):
        language = '韩'
        name = name[1:]
    elif name.startswith('英'):
        language = '英'
        name = name[1:]
    else:
        language = '中'
        name = name.replace('中', '')
    name = name.strip()
    await download_voice(bot, event)
    path = await get_random_voice(name, language)
    if not path:
        await ys_voice.finish(f'没有找到{name}的语音呢')
    await ys_voice.finish(MessageSegment.record(file=Path(path)))


@update_ys_voice.handle()
async def update_genshin_voice(bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent]):
    await update_ys_voice.send('将在后台开始更新原神语音资源，请耐心等待资源下载完成后再使用原神语音')
    await download_data.update_voice_data()
    await update_ys_voice.finish('原神语音资源更新完成')
