import math
from collections import defaultdict
from enum import IntEnum, auto

from LittlePaimon.utils.image import PMImage, font_manager as fm, load_image
from LittlePaimon.utils.message import MessageBuild
from LittlePaimon.utils.path import RESOURCE_BASE_PATH


class SignResult(IntEnum):
    SUCCESS = auto()
    DONE = auto()
    FAIL = auto()


async def draw_result(group_id: int, data: list):
    img = PMImage(await load_image(RESOURCE_BASE_PATH / 'player_card' / 'white_bg.png'))
    success_list = [d for d in data if d['result'] in [SignResult.SUCCESS, SignResult.DONE]]
    fail_list = [d['uid'] for d in data if d['result'] == SignResult.FAIL]
    same_reward = defaultdict(list)
    for s in success_list:
        same_reward[s['reward']].append(s['uid'])
    total_height = len(same_reward) * 40 + 2 * 45 + 240
    for uids in same_reward.values():
        total_height += 45 * math.ceil(len(uids) / 3)
    total_height += 45 * math.ceil(len(fail_list) / 3)
    await img.stretch((50, img.height - 50), total_height, 'height')
    await img.stretch((60, 415), 0, 'width')

    text_width = [70, 290, 510]

    await img.text('米游社自动签到结果', 50, 30, fm.get('优设标题黑', 60), '#252525')
    await img.text(str(group_id), 50, 85, fm.get('优设标题黑', 48), '#252525')
    await img.text(f'本群已开启自动签到共{len(data)}人', 50, 145, fm.get('优设标题黑', 36), '#252525')

    await img.paste(await load_image(RESOURCE_BASE_PATH / 'icon' / 'success.png', size=(50, 50)), (50, 220))
    await img.text('签到成功：', 110, 230, fm.get('优设标题黑', 36), '#00921b')
    now_height = 270
    for reward in same_reward:
        await img.text(f'{reward}', (0, img.width), now_height, fm.get('优设标题黑', 30), '#252525', 'center')
        now_height += 45
        i = 0
        for uid in same_reward[reward]:
            await img.text(str(uid), text_width[i % 3], now_height + (i // 3) * 45, fm.get('优设标题黑', 25), '#252525')
            i += 1
        now_height += math.ceil(len(same_reward[reward]) / 3) * 45
    now_height += 20
    await img.paste(await load_image(RESOURCE_BASE_PATH / 'icon' / 'fail.png', size=(50, 50)), (50, now_height))
    await img.text('签到失败(CK失效或出现验证码)：', 110, now_height + 10, fm.get('优设标题黑', 36), '#d60623')
    now_height += 60
    i = 0
    for uid in fail_list:
        await img.text(str(uid), text_width[i % 3], now_height + (i // 3) * 45, fm.get('优设标题黑', 25), '#252525')
        i += 1
    await img.text('Powered by LittlePaimon', (0, img.width), img.height - 65, fm.get('优设标题黑', 30), '#252525', 'center')

    return MessageBuild.Image(img, quality=70, mode='RGB')