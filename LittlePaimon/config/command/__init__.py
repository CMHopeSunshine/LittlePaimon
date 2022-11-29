import re
from typing import List

from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent
from nonebot.message import event_preprocessor
from tortoise.queryset import Q

from LittlePaimon.config import config
from LittlePaimon.database import CommandAlias, AliasMode


@event_preprocessor
async def handle_command_alias(event: MessageEvent):
    if not config.command_alias_enable:
        return
    msgs = event.get_message()
    if len(msgs) < 1 or msgs[0].type != 'text':
        return
    msg = str(msgs[0]).lstrip()
    if not msg:
        return
    if isinstance(event, GroupMessageEvent):
        filter_arg = Q(group_id=str(event.group_id)) | Q(group_id='all')
    else:
        filter_arg = Q(group_id='all')
    all_alias = await CommandAlias.filter(filter_arg).order_by('priority')
    new_msg = modify_msg(all_alias, msg)
    event.message[0].data['text'] = new_msg


def combine_msg(new_command: str, extra_msg: str, is_reverse: bool):
    return extra_msg + new_command if is_reverse else new_command + extra_msg


def modify_msg(all_alias: List[CommandAlias], msg: str):
    for alias in all_alias:
        if alias.is_regex:
            msg = re.sub(alias.alias, alias.command, msg)
        elif alias.mode == AliasMode.prefix and msg.startswith(alias.alias):
            msg = combine_msg(alias.command, msg[len(alias.alias):], alias.is_reverse)
        elif alias.mode == AliasMode.suffix and msg.endswith(alias.alias):
            msg = combine_msg(msg[:-len(alias.alias)], alias.command, alias.is_reverse)
        elif alias.mode == AliasMode.full_match and msg == alias.alias:
            msg = alias.command
    return msg
