import re
from typing import Union, Tuple, Set

from nonebot import on_command, on_regex, on_endswith, on_keyword, on_startswith
import nonebot
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, log
from nonebot.adapters.onebot import v11

"""
通过猴子补丁，为nonebot的部分matcher注入其命令到默认state中
"""


def on_command_(cmd: Union[str, Tuple[str, ...]], state: dict = None, *args, **kwargs):
    if state is None:
        state = {}
    if 'pm_name' not in state:
        state['pm_name'] = cmd if isinstance(cmd, str) else cmd[0]
    return on_command(cmd=cmd, state=state, _depth=1, *args, **kwargs)


def on_endswith_(msg: Union[str, Tuple[str, ...]], state: dict = None, *args, **kwargs):
    if state is None:
        state = {}
    if 'pm_name' not in state:
        state['pm_name'] = msg if isinstance(msg, str) else msg[0]
    return on_endswith(msg=msg, state=state, _depth=1, *args, **kwargs)


def on_startswith_(msg: Union[str, Tuple[str, ...]], state: dict = None, *args, **kwargs):
    if state is None:
        state = {}
    if 'pm_name' not in state:
        state['pm_name'] = msg if isinstance(msg, str) else msg[0]
    return on_startswith(msg=msg, state=state, _depth=1, *args, **kwargs)


def on_regex_(pattern: str, state: dict = None, *args, **kwargs):
    if state is None:
        state = {}
    if 'pm_name' not in state:
        state['pm_name'] = pattern
    return on_regex(pattern=pattern, state=state, _depth=1, *args, **kwargs)


def on_keyword_(keywords: Set[str], state: dict = None, *args, **kwargs):
    if state is None:
        state = {}
    if 'pm_name' not in state:
        state['pm_name'] = list(keywords)[0]
    return on_keyword(keywords=keywords, state=state, _depth=1, *args, **kwargs)


def _check_nickname(bot: Bot, event: MessageEvent) -> None:
    """检查消息开头是否存在昵称，去除并赋值 `event.to_me`。

    参数:
        bot: Bot 对象
        event: MessageEvent 对象
    """
    first_msg_seg = event.message[0]
    if first_msg_seg.type != "text":
        return

    if nicknames := set(filter(lambda n: n, bot.config.nickname)):
        # check if the user is calling me with my nickname
        nickname_regex = "|".join(nicknames)
        first_text = first_msg_seg.data["text"]

        if m := re.search(rf"^({nickname_regex})([\s,，]*|$)", first_text, re.IGNORECASE):
            nickname = m[1]
            log("DEBUG", f"User is calling me {nickname}")
            event.to_me = True
            # first_msg_seg.data["text"] = first_text[m.end():]


nonebot.on_command = on_command_
nonebot.on_regex = on_regex_
nonebot.on_startswith = on_startswith_
nonebot.on_endswith = on_endswith_
nonebot.on_keyword = on_keyword_
v11.bot._check_nickname = _check_nickname
