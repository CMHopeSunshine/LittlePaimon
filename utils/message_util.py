import re
from io import BytesIO
from pathlib import Path
from time import time
from typing import Union, Optional, Tuple

from PIL import Image
from littlepaimon_utils import aiorequests
from littlepaimon_utils.files import load_image
from nonebot import get_bot, logger
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment

from .db_util import get_last_query, update_last_query

# 加载敏感违禁词列表
ban_word = []
with open(Path(__file__).parent / 'json_data' / 'ban_word.txt', 'r', encoding='utf-8') as f:
    for line in f:
        ban_word.append(line.strip())


class MessageBuild:

    @classmethod
    def Image(cls,
              img: Union[Image.Image, Path, str],
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
        img.save(bio, format='JPEG' if img.mode == 'RGB' else 'PNG', quality=quality)
        return MessageSegment.image(bio)

    @classmethod
    async def StaticImage(cls,
                          url: str,
                          size: Optional[Tuple[int, int]] = None,
                          crop: Optional[Tuple[int, int, int, int]] = None,
                          quality: Optional[int] = 100,
                          mode: Optional[str] = None,
                          tips: Optional[str] = None,
                          is_check_time: Optional[bool] = True,
                          check_time_day: Optional[int] = 3
                          ):
        """
            从url下载图片，并预处理并构造成MessageSegment，如果url的图片已存在本地，则直接读取本地图片
            :param url: 图片url
            :param size: 预处理尺寸
            :param crop: 预处理裁剪大小
            :param quality: 预处理图片质量
            :param mode: 预处理图像模式
            :param tips: url中不存在该图片时的提示语
            :param is_check_time: 是否检查本地图片最后修改时间
            :param check_time_day: 检查本地图片最后修改时间的天数，超过该天数则重新下载图片
            :return: MessageSegment.image
        """
        path = Path() / 'resources' / url
        if path.exists() and (
                not is_check_time or (is_check_time and not check_time(path.stat().st_mtime, check_time_day))):
            img = Image.open(path)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            img = await aiorequests.get_img(url='https://static.cherishmoon.fun/' + url, save_path=path)
            if img == 'No Such File':
                return MessageBuild.Text(tips or '缺少该静态资源')
        if size:
            img = img.resize(size)
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
            过滤文本中的敏感违禁词
            :param text: 文本
            :return: MessageSegment.text
        """
        for word in ban_word[2:]:
            if word and word in text:
                text = text.replace(word, '*' * len(word))
        return MessageSegment.text(text)

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
            resp = await aiorequests.get(url='https://static.cherishmoon.fun/' + url)
            content = resp.content
            path.write_bytes(content)
        return MessageSegment.record(file=path)

    @classmethod
    def Video(cls, path: str) -> MessageSegment:
        return MessageSegment.video(path)

    @classmethod
    async def StaticVideo(cls, url: str) -> MessageSegment:
        """
            从url中下载视频文件，并构造成MessageSegment，如果本地已有该视频文件，则直接读取本地文件
            :param url: 视频url
            :return: MessageSegment.video
        """
        path = Path() / 'data' / url
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            resp = await aiorequests.get(url='https://static.cherishmoon.fun/' + url)
            content = resp.content
            path.write_bytes(content)
        return MessageSegment.video(file=path)


async def get_at_target(msg):
    for msg_seg in msg:
        if msg_seg.type == "at":
            return msg_seg.data['qq']
    return None


# message预处理，获取uid、干净的msg、user_id、是否缓存
async def get_uid_in_msg(event: MessageEvent, msg: Union[Message, str]):
    if isinstance(msg, Message):
        msg = msg.extract_plain_text().strip()
    if not msg:
        uid = await get_last_query(str(event.user_id))
        return uid, '', str(event.user_id), True
    user_id = await get_at_target(event.message) or str(event.user_id)
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
    if not msg:
        return None
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
