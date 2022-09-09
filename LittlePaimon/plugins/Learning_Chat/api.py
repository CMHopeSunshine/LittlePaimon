import time

from nonebot import get_bot
from nonebot.adapters.onebot.v11 import Bot


async def is_shutup(self_id: int, group_id: int) -> bool:
    """
    判断账号是否在禁言
    :param self_id: 自身id
    :param group_id: 群id
    """
    bot: Bot = get_bot(str(self_id))
    info = await bot.get_group_member_info(user_id=self_id, group_id=group_id)

    return info['shut_up_timestamp'] > int(time.time())
