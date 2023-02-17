import datetime
import random

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from nonebot.rule import Rule

from LittlePaimon.database import GenshinVoice, GuessVoiceRank
from LittlePaimon.utils import logger, scheduler
from LittlePaimon.utils.alias import get_alias_by_name
from LittlePaimon.utils.requests import aiorequests

from .draw import draw_voice_list

gaming = {}


class GuessVoice:
    game_time: int
    group_id: int
    language: str

    def __init__(
        self, group_id: int, bot: Bot, game_time: int = 30, language: str = '中'
    ):
        self.group_id = group_id
        self.game_time = game_time
        self.language = language
        self.bot = bot

    @property
    def is_gaming(self):
        return self.group_id in gaming

    async def start(self):
        if self.is_gaming:
            return '当前已经有一个游戏正在进行中啦！'
        voice_list = await GenshinVoice.filter(language=self.language)
        if not voice_list:
            return '当前没有语音资源，请先让超级用户[更新原神语音资源]'
        voice = random.choice(voice_list)
        gaming[self.group_id] = voice.character
        create_guess_matcher(self.group_id, voice.character, self.game_time)
        if scheduler.get_job(f'Guess_voice_{self.group_id}'):
            scheduler.remove_job(f'Guess_voice_{self.group_id}')
        scheduler.add_job(
            self.end,
            'date',
            run_date=datetime.datetime.now()
            + datetime.timedelta(seconds=self.game_time),
            id=f'Guess_voice_{self.group_id}',
            misfire_grace_time=10,
        )
        return await get_record(voice.voice_url)

    async def end(self, exception: bool = False):
        if not exception and self.is_gaming:
            answer = gaming[self.group_id]
            del gaming[self.group_id]
            msg = f'还没有人猜中呢，正确答案是：{answer}！'
            try:
                await self.bot.send_group_msg(group_id=self.group_id, message=msg)
            except Exception as e:
                logger.warning('原神猜语音', '➤发送结果时出错', str(e))
            logger.info(
                '原神猜语音', f'➤群<m>{self.group_id}</m>猜语音游戏结束，答案为<m>{answer}</m>，没有人猜对'
            )
        elif exception:
            logger.warning('原神猜语音', f'➤群<m>{self.group_id}</m>猜语音游戏发送语音出错， 异常结束')
            del gaming[self.group_id]


async def get_rank(group_id: int):
    records = await GuessVoiceRank.filter(
        group_id=group_id,
        guess_time__gte=datetime.datetime.now() - datetime.timedelta(days=7),
    )
    if not records:
        return '本群本周暂无排行榜数据哦！'
    rank = {}
    for record in records:
        if record.user_id in rank:
            rank[record.user_id] += 1
        else:
            rank[record.user_id] = 1
    msg = '本周猜语音排行榜\n'
    for i, (user_id, count) in enumerate(
        sorted(rank.items(), key=lambda x: x[1], reverse=True), start=1
    ):
        msg += f'{i}.{user_id}: {count}次\n'
    return msg


def create_guess_matcher(group_id, role_name, game_time):
    """
    创建一个猜语音的正则匹配matcher，正则内容为角色的别名
    :param role_name: 角色名
    :param game_time: 结束时间（秒）
    :param group_id: 进行的群组
    """

    def check_group(event: GroupMessageEvent):
        return event.group_id == group_id

    if '旅行者' in role_name:
        role_name = role_name.replace('旅行者（', '').replace('）', '')
    alias_list = get_alias_by_name(role_name)
    re_str = '|'.join(alias_list)
    guess_matcher = on_regex(
        f'^{re_str}$',
        temp=True,
        rule=Rule(check_group),
        expire_time=datetime.timedelta(seconds=game_time),
    )
    guess_matcher.plugin_name = "Genshin_Voice"

    @guess_matcher.handle()
    async def _(event: GroupMessageEvent):
        await GuessVoiceRank.create(
            user_id=event.user_id,
            group_id=event.group_id,
            answer=role_name,
            guess_time=datetime.datetime.now(),
        )
        del gaming[event.group_id]
        if scheduler.get_job(f'Guess_voice_{event.group_id}'):
            scheduler.remove_job(f'Guess_voice_{event.group_id}')
        logger.info(
            '原神猜语音',
            f'➤群<m>{event.group_id}</m>猜语音游戏结束，答案为<m>{role_name}</m>，由<m>{event.sender.card}</m>猜对',
        )
        msg = Message(
            MessageSegment.text('恭喜')
            + MessageSegment.at(event.user_id)
            + MessageSegment.text(f'猜对了！\n正确答案是：{role_name}')
        )
        await guess_matcher.finish(msg)


async def get_character_voice(character: str, language: str = '中'):
    voice = await GenshinVoice.filter(character=character, language=language).first()
    if voice:
        return MessageSegment.record(voice.voice_url)
    else:
        return MessageSegment.text(f'暂无{character}的{language}语音资源，让超级用户[更新原神语音资源]吧！')


async def get_voice_list(character: str, language: str = '中'):
    voice_list = await GenshinVoice.filter(character=character, language=language).all()
    return (
        await draw_voice_list(voice_list)
        if voice_list
        else MessageSegment.text(f'暂无{character}的{language}语音资源，让超级用户[更新原神语音资源]吧！')
    )


async def get_record(url: str) -> MessageSegment.record:
    resp = await aiorequests.get(url)
    resp.raise_for_status()
    voice = resp.content
    return MessageSegment.record(voice)
