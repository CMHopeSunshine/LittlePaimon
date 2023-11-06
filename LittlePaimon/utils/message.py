import random
import re
import time
from io import BytesIO
from pathlib import Path
from typing import Union, Optional, Tuple, List

from PIL import Image
from nonebot import get_bot
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment, GroupMessageEvent
from nonebot.rule import Rule
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Depends
from nonebot.typing import T_State

from LittlePaimon.database import LastQuery, PrivateCookie, Player, PlayerAlias
from . import NICKNAME
from .alias import get_match_alias
from .filter import filter_msg
from .image import PMImage, load_image
from .requests import aiorequests
from .typing import CHARACTERS, MALE_CHARACTERS, FEMALE_CHARACTERS, GIRL_CHARACTERS, BOY_CHARACTERS, \
    LOLI_CHARACTERS


class MessageBuild:

    @classmethod
    def Image(cls,
              img: Union[Image.Image, PMImage, Path, str],
              *,
              size: Optional[Union[Tuple[int, int], float]] = None,
              crop: Optional[Tuple[int, int, int, int]] = None,
              quality: Optional[int] = 100,
              mode: Optional[str] = None
              ) -> MessageSegment:
        """
        说明：
        图片预处理并构造成MessageSegment
            :param img: 图片Image对象或图片路径
            :param size: 预处理尺寸
            :param crop: 预处理裁剪大小
            :param quality: 预处理图片质量
            :param mode: 预处理图像模式
            :return: MessageSegment.image
        """
        if isinstance(img, (str, Path)):
            img = load_image(path=img, size=size, mode=mode, crop=crop)
        else:
            if isinstance(img, PMImage):
                img = img.image
            if size:
                if isinstance(size, float):
                    img = img.resize((int(img.size[0] * size), int(img.size[1] * size)), Image.LANCZOS)
                elif isinstance(size, tuple):
                    img = img.resize(size, Image.LANCZOS)
            if crop:
                img = img.crop(crop)
            if mode:
                img = img.convert(mode)
        bio = BytesIO()
        img.save(bio, format='JPEG' if img.mode == 'RGB' else 'PNG', quality=quality)
        return MessageSegment.image(bio)

    @classmethod
    def Text(cls, text: str) -> MessageSegment:
        """
        过滤文本中的敏感违禁词，并构造成MessageSegment
            :param text: 文本
            :return: MessageSegment.text
        """
        return MessageSegment.text(filter_msg(text))

    @classmethod
    def Record(cls, path: str) -> MessageSegment:
        return MessageSegment.record(path)

    @classmethod
    async def StaticRecord(cls, url: str) -> MessageSegment:
        """
        从url中下载音频文件，并构造成MessageSegment，如果本地已有该音频文件，则直接读取本地文件
            :param url: 语音url
            :return: MessageSegment.record
        """
        path = Path() / 'data' / url
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            resp = await aiorequests.get(url=f'https://static.cherishmoon.fun/{url}')
            content = resp.content
            path.write_bytes(content)
        return MessageSegment.record(file=path)

    @classmethod
    def Video(cls, path: str) -> MessageSegment:
        return MessageSegment.video(path)


def fullmatch(msg: Message = CommandArg()) -> bool:
    return not bool(msg)

fullmatch_rule = Rule(fullmatch)


def CommandPlayer(limit: int = 3, only_cn: bool = True) -> List[Player]:
    """
    获取查询操作中的user_id、uid和图片，并将过滤uid后的msg存放到T_State中
        :param limit: 限制个数
        :param only_cn: 是否只接受国服uid
        :return: 查询对象列表
    """

    async def _player(event: MessageEvent, matcher: Matcher, state: T_State, msg: Message = CommandArg()) -> List[
        Player]:
        query_list: List[Player] = []
        users: List[str] = [str(seg.data['qq']) for seg in msg['at']]
        info: str = ''
        extra_info = msg.extract_plain_text().strip()
        if not users:
            users = [str(event.user_id)]
        if len(users) > 1 and isinstance(event, GroupMessageEvent):
            for u in users:
                if uid := await get_uid(user_id=u, group_id=event.group_id):
                    query_list.append(Player(user_id=u, uid=uid))
                else:
                    info += f'{u}尚未提供uid\n'
            if info:
                await matcher.finish(info, at_sender=True)
        else:
            user = users[0]
            uids: List[str] = []
            if uid := re.findall(r'[1258]\d{8}', extra_info):
                uids = uid
            elif uid := await get_uid(event=event, user_id=user):
                uids = [uid]
            else:
                await matcher.finish('第一次查询请把UID加在指令后面', at_sender=True)
            extra_info = replace_all(extra_info, uids)
            for uid in uids:
                query_list.append(Player(user_id=user, uid=uid))

        if len(query_list) > limit:
            query_list = query_list[:limit]
        if only_cn:
            query_list = [q for q in query_list if q.uid.startswith(('1', '2', '5'))]
        state['clear_msg'] = extra_info.strip()
        return query_list

    return Depends(_player)


def CommandUID(only_cn: bool = True) -> str:
    """
    从消息中提取uid
        :param only_cn: 是否只接受国服uid
        :return: uid
    """

    async def _uid(event: MessageEvent, state: T_State, matcher: Matcher, msg: Message = CommandArg()):
        msg = msg.extract_plain_text().strip()
        if only_cn and (uid := re.findall(r'[125]\d{8}', msg)):
            uid = uid[0]
        elif not only_cn and (uid := re.findall(r'[1258]\d{8}', msg)):
            uid = uid
        elif uid := await get_uid(event=event):
            uid = uid
        else:
            await matcher.finish('第一次查询请把UID加在指令后面')
        state['clear_msg'] = event.message.extract_plain_text().replace(uid, '')
        return uid

    return Depends(_uid)


def CommandCharacter(limit: int = 3) -> List[str]:
    """
    从命令中提取出原神的角色，需配合CommandUID使用
        :param limit: 限制个数
        :return: 角色名列表
    """

    async def _character(matcher: Matcher, state: T_State, event: MessageEvent, msg: Message = CommandArg()):
        # 获取艾特列表的第一个人或是事件触发者的qq
        user_id = users[0] if (users := [str(seg.data['qq']) for seg in msg['at']]) else str(event.user_id)
        # 去除消息中的uid
        msg = re.sub(r'[125]\d{8}', '', msg.extract_plain_text())
        # 没有消息的话，就随机选择一个角色
        if not (msg := msg.strip()):
            return [random.choice(CHARACTERS)]
        character_list = []
        # 按空格分割消息
        for character_name in msg.split(' '):
            # 如果有设置别名
            if character_match := await PlayerAlias.get_or_none(user_id=user_id, alias=character_name):
                character_list.append(character_match.character)
                msg.replace(character_name, '')
            # 如果在预设别名列表
            elif character_name in ['老婆', '老公', '女儿', '儿子', '爸爸', '妈妈']:
                if character_name == '老公':
                    character_list.append(random.choice(MALE_CHARACTERS + BOY_CHARACTERS))
                elif character_name == '老婆':
                    character_list.append(random.choice(FEMALE_CHARACTERS + GIRL_CHARACTERS))
                elif character_name == '女儿':
                    character_list.append(random.choice(GIRL_CHARACTERS + LOLI_CHARACTERS))
                elif character_name == '儿子':
                    character_list.append(random.choice(BOY_CHARACTERS))
                elif character_name == '爸爸':
                    character_list.append(random.choice(MALE_CHARACTERS))
                elif character_name == '妈妈':
                    character_list.append(random.choice(FEMALE_CHARACTERS))
                msg.replace(character_name, '')
            # 如果有匹配别名
            elif character_match := get_match_alias(character_name, ['角色'], True):
                character_list.append(character_match[0])
                msg.replace(character_name, '')
        # 没有匹配到角色时，结束事件
        if not character_list:
            await matcher.finish(f'没有名为{msg}的角色！')
        if len(character_list) > limit:
            character_list = character_list[:limit]
        return character_list

    return Depends(_character)


def CommandObjectID() -> int:
    """
    根据消息事件的类型获取对象id
    私聊->用户id
    群聊->群id
    频道->子频道id
        :return: 对象id
    """

    def _event_id(event):
        if event.message_type == 'private':
            return event.user_id
        elif event.message_type == 'group':
            return event.group_id
        elif event.message_type == 'guild':
            return event.channel_id

    return Depends(_event_id)


def CommandSwitch() -> Optional[bool]:
    """
    获取消息中的开关类型，如果没有则返回None
        :return: Optional[bool]
    """

    def _switch(event: MessageEvent, msg: Message = CommandArg()):
        msg = msg.extract_plain_text().strip()
        if msg:
            if re.search('开|启用|on|open|enable', msg):
                return True
            elif re.search('关|禁用|取消|off|close|disable', msg):
                return False
        return None

    return Depends(_switch)


def CommandLang() -> str:
    def _lang(event: MessageEvent, msg: Message = CommandArg()):
        msg = msg.extract_plain_text().strip()
        if msg:
            if re.search('中|汉|普通话|国|cn|chinese', msg):
                return '中'
            elif re.search('英|美|en|english', msg):
                return '英'
            elif re.search('日|霓虹|jp|japanese', msg):
                return '日'
            elif re.search('韩|南朝鲜|kor|korean', msg):
                return '韩'
        return '中'

    return Depends(_lang)


def CommandTime() -> Optional[Tuple[int, int]]:
    """
    获取消息中的小时:分钟格式时间元组，如果没有则返回None
        :return: (小时, 分钟)
    """

    def _datetime(msg: Message = CommandArg()):
        msg = msg.extract_plain_text().strip()
        if match := re.search(r'(\d{1,2}):(\d{2})', msg):
            return match[1], match[2]
        return None

    return Depends(_datetime)


async def get_uid(event: Optional[MessageEvent] = None, user_id: Optional[str] = None,
                  group_id: Optional[int] = None) -> Optional[str]:
    """
    根据event或者用户id获取uid
        :param event: 消息事件
        :param user_id: 用户id
        :param group_id: 用户所在群id
        :return: uid
    """
    if event and not user_id:
        user_id = event.sender.user_id
    elif user_id:
        pass
    else:
        return None
    if cache_uid := await LastQuery.get_or_none(user_id=user_id):
        return cache_uid.uid
    elif bind_uid := await PrivateCookie.get_or_none(user_id=user_id):
        return bind_uid.uid
    else:
        if event:
            if nickname_uid := re.search(r'[1258]\d{8}', event.sender.card or event.sender.nickname):
                return nickname_uid.group()
        else:
            if group_id:
                nickname = (await get_bot().get_group_member_info(group_id=group_id, user_id=int(user_id)))['card']
                if nickname_uid := re.search(r'[1258]\d{8}', nickname):
                    return nickname_uid.group()
    return None


def replace_all(raw_text: str, text_list: Union[str, list]) -> str:
    """
    删除字符串中指定的所有子字符串
        :param raw_text: 原字符串
        :param text_list: 待删除的子字符串
        :return: 新字符串
    """
    if text_list:
        if isinstance(text_list, str):
            text_list = [text_list]
        for text in text_list:
            raw_text = raw_text.replace(text, '')
    return raw_text


def check_time(time_stamp: float, days: int = 1):
    """
    检查时间戳是否在指定天数内
        :param time_stamp: 时间戳
        :param days: 天数
        :return: True/False
    """
    time_stamp = int(time_stamp)
    now = int(time.time())
    return (now - time_stamp) / 86400 > days


async def recall_message(event: MessageEvent) -> bool:
    """
    撤回指定群消息（需管理员权限且权限大于发送者）
        :param event: 消息事件
        :return: 是否撤回成功
    """
    bot = get_bot(str(event.self_id))
    if not isinstance(event, GroupMessageEvent):
        return False
    info = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
    permission_type = {
        'owner':  3,
        'admin':  2,
        'member': 1
    }
    if permission_type[info['role']] < permission_type['admin'] or permission_type[info['role']] <= permission_type[
        event.sender.role]:
        return False
    await bot.delete_msg(message_id=event.message_id)
    return True


def format_message(text: str, **kwargs) -> Message:
    msg = Message()
    texts = re.split(r'({(?:\w+|(?:img|voice|video):[^{}]+|face:\d+)})', text)
    for text in texts:
        if text == '{nickname}':
            msg += MessageSegment.text(NICKNAME)
        elif text == '{at_user}':
            msg += MessageSegment.at(kwargs['user_id']) if 'user_id' in kwargs else MessageSegment.text('{at_user}')
        elif text.startswith(('{img', '{voice', '{video')):
            url = text.split(':', 1)[1].strip('}')
            if url.startswith('.'):
                url = Path().cwd().as_uri() + url[1:].replace('\\', '/')
            if text.startswith('{img'):
                msg += MessageSegment.image(url)
            elif text.startswith('{voice'):
                msg += MessageSegment.record(url)
            elif text.startswith('{video'):
                msg += MessageSegment.video(url)
        elif text.startswith('{face:'):
            face_id = text.split(':', 1)[1].strip('}')
            msg += MessageSegment.face(int(face_id))
        elif text.startswith('{') and text.endswith('}'):
            type_ = text.strip('{').strip('}')
            msg += MessageSegment.text(kwargs.get(type_, text))
        else:
            msg += MessageSegment.text(text.replace('\\n', '\n'))
    return msg
