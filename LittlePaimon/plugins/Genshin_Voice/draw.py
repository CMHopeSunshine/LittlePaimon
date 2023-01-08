import asyncio
from typing import List

from LittlePaimon.database import GenshinVoice
from LittlePaimon.utils.image import PMImage, font_manager as fm, load_image
from LittlePaimon.utils.message import MessageBuild
from LittlePaimon.utils.path import RESOURCE_BASE_PATH


async def draw_table_line(img: PMImage, voice_id: int, voice_name: str, voice_content: str, i: int):
    await img.draw_line((60, 164 + 30 * i), (1020, 164 + 30 * i), '#ddcdba', 2)
    await img.text(str(voice_id), (60, 180), (164 + 30 * i, 194 + 30 * i),
                   fm.get('hywh', 28), 'black', 'center')
    await img.text(voice_name[:10], (180, 460), (164 + 30 * i, 194 + 30 * i),
                   fm.get('hywh', 28), 'black', 'center')
    await img.text(voice_content[:19].replace('\n', ''), (460, 1020), (164 + 30 * i, 194 + 30 * i),
                   fm.get('hywh', 28), 'black', 'center')


async def draw_voice_list(voice_list: List[GenshinVoice]):
    img = PMImage(await load_image(RESOURCE_BASE_PATH / 'player_card' / 'white_bg.png'))
    voice_table_length = 30 * len(voice_list) + 30 + 40
    await img.stretch((144, img.height - 72), voice_table_length, 'height')
    await img.text(f'{voice_list[0].character}{voice_list[0].language}文语音列表', (0, img.width), 55,
                   fm.get('hywh', 60), 'black', 'center')
    await img.text('发送[原神语音 序号]可以获取对应语音', (0, img.width), img.height - 80,
                   fm.get('hywh', 36), 'black', 'center')
    await img.draw_line((60, 164), (60, 124 + voice_table_length), '#ddcdba', 2)
    await img.draw_line((180, 164), (180, 124 + voice_table_length), '#ddcdba', 2)
    await img.draw_line((460, 164), (460, 124 + voice_table_length), '#ddcdba', 2)
    await img.draw_line((1020, 164), (1020, 124 + voice_table_length), '#ddcdba', 2)
    await img.draw_line((60, 164), (1020, 164), '#ddcdba', 2)
    await img.text('序号', (60, 180), (164, 194), fm.get('hywh', 28), 'black', 'center')
    await img.text('语音名称', (180, 460), (164, 194), fm.get('hywh', 28), 'black', 'center')
    await img.text('语音内容', (460, 1020), (164, 194), fm.get('hywh', 28), 'black', 'center')
    await asyncio.gather(*[draw_table_line(img, voice_list[i - 1].id, voice_list[i - 1].voice_name, voice_list[i - 1].voice_content, i) for i in range(1, len(voice_list) + 1)])
    await img.draw_line((60, 164 + 30 * (len(voice_list) + 1)), (1020, 164 + 30 * (len(voice_list) + 1)), '#ddcdba', 2)

    return MessageBuild.Image(img, quality=35, mode='RGB')


