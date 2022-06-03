import re
from time import time

from PIL import Image
from pathlib import Path
from typing import Union, Optional, Tuple
from io import BytesIO

from nonebot import get_bot, logger
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment

from .db_util import get_last_query, update_last_query
from .file_handler import load_image
from . import aiorequests


class MessageBuild:

    @classmethod
    def Image(cls,
              img: Union[Image.Image, Path, str],
              *,
              size: Optional[Union[Tuple[int, int], float]] = None,
              crop: Optional[Tuple[int, int, int, int]] = None,
              quality: Optional[int] = 100,
              mode: Optional[str] = 'RGB'
              ) -> MessageSegment:
        if isinstance(img, str) or isinstance(img, Path):
            img = load_image(path=img, size=size, mode=mode, crop=crop)
        else:
            if size:
                if isinstance(size, float):
                    img = img.resize((int(img.size[0] * size), int(img.size[1] * size)), Image.ANTIALIAS)
                elif isinstance(size, tuple):
                    img = img.resize(size, Image.ANTIALIAS)
            if crop:
                img = img.crop(crop)
            if mode:
                img = img.convert(mode)
        bio = BytesIO()
        img = img.convert(mode)
        img.save(bio, format='JPEG' if mode == 'RGB' else 'PNG', quality=quality)
        return MessageSegment.image(bio)

    @classmethod
    async def StaticImage(cls,
                          url: str,
                          size: Optional[Tuple[int, int]] = None,
                          crop: Optional[Tuple[int, int, int, int]] = None,
                          quality: Optional[int] = 100,
                          mode: Optional[str] = 'RGB',
                          tips: Optional[str] = None
                          ):
        path = Path() / 'data' / url
        if path.exists() and not check_time(path.stat().st_mtime, 3):
            img = Image.open(path)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            img = await aiorequests.get_img(url='https://static.cherishmoon.fun/' + url, save_path=path)
            if img == 'No Such File':
                return MessageSegment.text(tips or '缺少该静态资源')
        if size:
            img = img.resize(size)
        if crop:
            img = img.crop(crop)
        bio = BytesIO()
        img = img.convert(mode)
        img.save(bio, format='JPEG' if mode == 'RGB' else 'PNG', quality=quality)
        return MessageSegment.image(bio)

    @classmethod
    def Text(cls, text: str) -> MessageSegment:
        # TODO 过滤负面文本
        return MessageSegment.text(text)

    @classmethod
    def Record(cls, path: str) -> MessageSegment:
        # TODO 网络语音
        return MessageSegment.record(path)

    @classmethod
    async def StaticRecord(cls, url: str) -> MessageSegment:
        path = Path() / 'data' / url
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            resp = await aiorequests.get(url='https://static.cherishmoon.fun/' + url)
            content = resp.content
            path.write_bytes(content)
        return MessageSegment.record(file=path)


async def get_at_target(msg):
    for msg_seg in msg:
        if msg_seg.type == "at":
            return msg_seg.data['qq']
    return None


# message预处理，获取uid、干净的msg、user_id、是否缓存
async def get_uid_in_msg(event: MessageEvent, msg: Message):
    msg = str(msg).strip()
    if not msg:
        uid = await get_last_query(str(event.user_id))
        return uid, '', str(event.user_id), True
    user_id = await get_at_target(event.message) or str(event.user_id)
    msg = re.sub(r'\[CQ.*?\]', '', msg)
    use_cache = False if '-r' in msg else True
    msg = msg.replace('-r', '').strip()
    find_uid = r'(?P<uid>(1|2|5)\d{8})'
    for msg_seg in event.message:
        if msg_seg.type == 'text':
            match = re.search(find_uid, msg_seg.data['text'])
            if match:
                await update_last_query(user_id, match.group('uid'), 'uid')
                return match.group('uid'), msg.replace(match.group('uid'), '').strip(), user_id, use_cache
    uid = await get_last_query(user_id)
    return uid, msg.strip(), user_id, use_cache


# 向超级用户私聊发送cookie删除信息
async def send_cookie_delete_msg(cookie_info):
    msg = ''
    if cookie_info['type'] == 'public':
        msg = f'公共池的{cookie_info["no"]}号cookie已失效'
    elif cookie_info['type'] == 'private':
        if cookie_info['uid']:
            msg = f'用户{cookie_info["user_id"]}的uid{cookie_info["uid"]}的cookie已失效'
        elif cookie_info['mys_id']:
            msg = f'用户{cookie_info["user_id"]}的mys_id{cookie_info["mys_id"]}的cookie已失效'
    if msg:
        logger.info(f'---{msg}---')
        for superuser in get_bot().config.superusers:
            try:
                await get_bot().send_private_msg(user_id=superuser, message=msg + '，派蒙帮你删除啦!')
            except Exception as e:
                logger.error(f'发送cookie删除消息失败: {e}')


def get_message_id(event):
    if event.message_type == 'private':
        return event.user_id
    elif event.message_type == 'group':
        return event.group_id
    elif event.message_type == 'guild':
        return event.channel_id


def uid_userId_to_dict(uid, user_id) -> Tuple[dict, Message]:
    total_result = Message()
    query_dict = {}
    if isinstance(uid, str) and isinstance(user_id, str):
        query_dict[uid] = user_id
    elif isinstance(uid, list) and isinstance(user_id, str):
        for u in uid:
            query_dict[u] = user_id
    elif isinstance(uid, list) and isinstance(user_id, list):
        for u, us in zip(uid, user_id):
            if u is not None:
                query_dict[u] = us
            else:
                total_result += MessageSegment.text(f'派蒙没有{us}的{u}信息哦，请把uid给派蒙吧~')
    return query_dict, total_result


def replace_all(raw_text: str, text_list: Union[str, list]):
    if not text_list:
        return raw_text
    else:
        if isinstance(text_list, str):
            text_list = [text_list]
        for text in text_list:
            raw_text = raw_text.replace(text, '')
        return raw_text


def transform_uid(msg):
    if isinstance(msg, Message):
        msg = msg.extract_plain_text().strip()
    check_uid = msg.split(' ')
    uid_list = []
    for check in check_uid:
        uid = re.search(r'(?P<uid>(1|2|5)\d{8})', check)
        if uid:
            uid_list.append(uid.group('uid'))
    return uid_list if len(uid_list) > 1 else uid_list[0] if uid_list else None


# 检查该时间戳和当前时间戳相差是否超过n天， 超过则返回True
def check_time(time_stamp, n=1):
    time_stamp = int(time_stamp)
    now = int(time())
    if (now - time_stamp) / 86400 > n:
        return True
    else:
        return False

