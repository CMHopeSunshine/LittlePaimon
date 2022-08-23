from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent
from nonebot.message import event_preprocessor

from .parser import parse_msg


@event_preprocessor
async def handle(event: MessageEvent):
    msgs = event.get_message()
    if len(msgs) < 1 or msgs[0].type != "text":
        return
    msg = str(msgs[0]).lstrip()
    if not msg:
        return


    try:
        msg = parse_msg(msg, get_id(event))
        event.message[0].data["text"] = msg
    except Exception:
        return


def get_id(event: MessageEvent) -> str:
    if event.message_type == 'group':
        return 'group_' + str(event.group_id)
    elif event.message_type == 'guild':
        return 'guild_' + str(event.guild_id)
    else:
        return 'private_' + str(event.user_id)