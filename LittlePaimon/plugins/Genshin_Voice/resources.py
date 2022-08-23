import asyncio
import contextlib
from typing import Union, Dict

from lxml import etree

from LittlePaimon.database.models import GenshinVoice
from LittlePaimon.utils import aiorequests
from LittlePaimon.utils import logger


async def get_character_list() -> Union[Dict[str, str], str]:
    """
    从米游社观测枢获取人物链接列表
    :return:
    """
    try:
        resp = await aiorequests.get(url='https://bbs.mihoyo.com/ys/obc/channel/map/189/25?bbs_presentation_style=no_header')

        html = etree.HTML(resp.text)
        character_dict = {}
        character_list = html.xpath('//*[@id="__layout"]/div/div[2]/div[2]/div/div[1]/div[2]/ul/li/div/ul/li[1]/div/div/a[@class="collection-avatar__item"]')

        for character in character_list:
            with contextlib.suppress(IndexError):
                character_name = character.xpath('./div/text()')[0]
                character_url = character.xpath('./@href')[0]
                character_dict[character_name] = character_url
        return character_dict
    except Exception as e:
        return str(e)


async def get_voice(character_name: str, character_url: str):
    """
    获取单个角色的四国语音
    :param character_name: 角色名称
    :param character_url: 角色链接
    """
    try:
        resp = await aiorequests.get(url=f'https://bbs.mihoyo.com{character_url}')
        html = etree.HTML(resp.text)
        lang = ['中', '英', '日', '韩']
        for i in range(1, 5):
            voice_list = html.xpath(f'////*[@class="obc-tmpl__part obc-tmpl-character obc-tmpl__part--voiceTab obc-tmpl__part--align-banner"]/ul[2]/li[{i}]/table[2]/tbody/tr')

            for voice in voice_list:
                with contextlib.suppress(IndexError):
                    voice_name = voice.xpath('./td/text()')[0]
                    voice_url = voice.xpath('./td/div/div/audio/source/@src')[0]
                    voice_content = voice.xpath('./td/div/span/text()')[0].strip()
                    await GenshinVoice.update_or_create(character=character_name, voice_name=voice_name, language=lang[i - 1], defaults={'voice_content': voice_content, 'voice_url': voice_url})

            if voice_list:
                logger.info('原神猜语音', f'➤➤角色<m>{character_name}</m>的<m>{lang[i - 1]}文语音</m><g>获取成功</g>')
            else:
                logger.info('原神猜语音', f'➤➤角色<m>{character_name}</m>的<m>{lang[i - 1]}文语音</m><r>获取失败</r>')

    except Exception as e:
        logger.warning('原神猜语音', f'➤➤获取<m>{character_name}</m>的语音资源时出错：', str(e))


async def update_voice_resources():
    logger.info('原神猜语音', '开始更新原神语音资源')
    character_list = await get_character_list()
    if isinstance(character_list, str):
        logger.warning('原神猜语音', '➤更新语音资源时出错：</m>', character_list)
        return f'更新语音资源时出错：{character_list}'
    for character_name, character_url in character_list.items():
        await get_voice(character_name, character_url)
        await asyncio.sleep(1)
    voice_num = await GenshinVoice.all().count()
    return f'更新语音资源成功，当前数据库中共有{voice_num}条语音资源'
