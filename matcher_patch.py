from typing import Union, Tuple, Set

from nonebot import on_command, on_regex, on_endswith, on_keyword
import nonebot

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


nonebot.on_command = on_command_
nonebot.on_regex = on_regex_
nonebot.on_endswith = on_endswith_
nonebot.on_keyword = on_keyword_
