from LittlePaimon.database import Player
from LittlePaimon.utils import logger
from LittlePaimon.utils.api import get_mihoyo_private_data
from .draw import draw_monthinfo_card


async def handle_myzj(player: Player, month: str):
    data = await get_mihoyo_private_data(player.uid, player.user_id, 'month_info', month=month)
    if isinstance(data, str):
        logger.info('原神每月札记', '➤', {'用户': player.user_id, 'UID': player.uid}, f'获取数据失败, {data}', False)

        return f'{player.uid}{data}\n'
    elif data['retcode'] != 0:
        logger.info('原神每月札记', '➤', {'用户': player.user_id, 'UID': player.uid},
                    f'获取数据失败，code为{data["retcode"]}， msg为{data["message"]}', False)

        return f'{player.uid}获取数据失败，msg为{data["message"]}\n'
    else:
        logger.info('原神每月札记', '➤', {'用户': player.user_id, 'UID': player.uid}, '获取数据成功', True)

        try:
            img = await draw_monthinfo_card(data['data'])
            logger.info('原神每月札记', '➤➤', {'用户': player.user_id, 'UID': player.uid}, '绘制图片成功', True)

            return img
        except Exception as e:
            logger.info('原神每月札记', '➤➤', {'用户': player.user_id, 'UID': player.uid}, f'绘制图片失败，{e}', False)

            return f'{player.uid}绘制图片失败，{e}\n'
