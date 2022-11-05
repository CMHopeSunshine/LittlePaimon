import asyncio
import contextlib
from typing import Dict, Optional

from lxml import etree

from LittlePaimon.database import GenshinVoice
from LittlePaimon.utils import logger
from LittlePaimon.utils.requests import aiorequests


async def get_character_list() -> Optional[Dict[str, int]]:
    """
    从米游社观测枢获取人物链接列表
    :return:
    """
    try:
        resp = await aiorequests.get(url='https://api-static.mihoyo.com/common/blackboard/ys_obc/v1/home/content/list?app_sn=ys_obc&channel_id=189')
        data = resp.json()
        if data['retcode'] != 0:
            return None
        data = data['data']['list'][0]['children'][0]['list']
        return {c['title']: c['content_id'] for c in data}
    except Exception:
        return None


async def get_voice(character_name: str, content_id: int):
    """
    获取单个角色的四国语音
    :param character_name: 角色名称
    :param content_id: 角色id
    """
    try:
        resp = await aiorequests.get(url=f'https://api-static.mihoyo.com/common/blackboard/ys_obc/v1/content/info?app_sn=ys_obc&content_id={content_id}',
                                     headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'})
        data = resp.json()
        if data['retcode'] != 0:
            return None
        data = data['data']['content']['contents'][2]
        html = etree.HTML(data['text'])
        for i in range(1, 5):
            voice_type = html.xpath(f'//*[@class="obc-tmpl__part obc-tmpl-character obc-tmpl__part--voiceTab obc-tmpl__part--align-banner"]/ul[1]/li[{i}]/text()')[0]
            voice_type = voice_type[0] if voice_type[0] != '汉' else '中'
            voice_list = html.xpath(f'//*[@class="obc-tmpl__part obc-tmpl-character obc-tmpl__part--voiceTab obc-tmpl__part--align-banner"]/ul[2]/li[{i}]/table[2]/tbody/tr')
            for voice in voice_list:
                with contextlib.suppress(IndexError):
                    voice_name = voice.xpath('./td/text()')[0]
                    voice_url = voice.xpath('./td/div/div/audio/source/@src')[0]
                    voice_content = voice.xpath('./td/div/span/text()')[0].strip()
                    character_name = character_name.replace('旅行者（', '').replace('）', '')
                    await GenshinVoice.update_or_create(character=character_name, voice_name=voice_name, language=voice_type, defaults={'voice_content': voice_content, 'voice_url': voice_url})
            if voice_list:
                logger.info('原神猜语音', f'➤➤角色<m>{character_name}</m>的<m>{voice_type}文语音</m><g>获取成功</g>')
            else:
                logger.info('原神猜语音', f'➤➤角色<m>{character_name}</m>的<m>{voice_type}文语音</m><r>获取失败</r>')
    except Exception as e:
        logger.warning('原神猜语音', f'➤➤获取<m>{character_name}</m>的语音资源时出错：', str(e))


async def update_voice_resources():
    logger.info('原神猜语音', '开始更新原神语音资源')
    character_list = await get_character_list()
    if character_list is None:
        logger.warning('原神猜语音', '➤更新语音资源出错')
        return '更新语音资源出错'
    for name, content_id in character_list.items():
        await get_voice(name, content_id)
        await asyncio.sleep(1)
    voice_num = await GenshinVoice.all().count()
    return f'更新语音资源成功，当前数据库中共有{voice_num}条语音资源'
