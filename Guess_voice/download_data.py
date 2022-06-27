# -*- coding: UTF-8 -*-
"""
该脚本可以直接获取wiki上的语音文件 并保存进数据库中
"""

import json
import os
from pathlib import Path

from bs4 import BeautifulSoup
from nonebot import logger
from sqlitedict import SqliteDict  # TODO 加入requirements

from utils import aiorequests
from .util import get_path

# OUT_PUT = Path(__file__).parent / 'voice'
OUT_PUT = Path() / 'data' / 'LittlePaimon' / 'guess_voice' / 'voice'

BASE_URL = 'https://wiki.biligame.com/ys/'
BASE_URL_MYS = 'https://bbs.mihoyo.com'
BASE_URL_MYS_CHARACTERS_LIST = '/ys/obc/channel/map/189/25?bbs_presentation_style=no_header'

API = {'character_list': '角色', 'voice': '%s语音'}

config = {
    # 日 英 韩
    'voice_language': ['日', '英', '韩']
}

# dir_data = os.path.join(os.path.dirname(__file__), 'data')
dir_data = Path() / 'data' / 'LittlePaimon' / 'guess_voice' / 'data'

# if not os.path.exists(dir_data):
#     os.makedirs(dir_data)
dir_data.mkdir(parents=True, exist_ok=True)


############

def init_db(db_dir, db_name='db.sqlite') -> SqliteDict:
    return SqliteDict(str(get_path(db_dir, db_name)),
                      encode=json.dumps,
                      decode=json.loads,
                      autocommit=True)


db = init_db('data', 'voice.sqlite')


############

# 获取角色列表
async def get_character_list():
    html = await aiorequests.get(url=(BASE_URL + API['character_list']))
    soup = BeautifulSoup(html.text, 'lxml')
    char_list = soup.find(attrs={
        'class': 'resp-tab-content',
        'style': 'display:block;'
    })
    char_list1 = char_list.find_all(attrs={'class': 'g C5星'})
    res = list(set(map(lambda x: x.find('div', class_='L').text, char_list1)))
    char_list2 = char_list.find_all(attrs={'class': 'g C5'})
    res.extend(list(set(map(lambda x: x.find('div', class_='L').text, char_list2))))
    char_list3 = char_list.find_all(attrs={'class': 'g C4星'})
    res.extend(list(set(map(lambda x: x.find('div', class_='L').text, char_list3))))
    res.sort()
    return res


# 获取角色语音
async def get_voice_info(character_name: str):
    logger.info('获取数据: %s' % character_name)
    html = await aiorequests.get(url=(BASE_URL + API['voice'] % character_name))
    soup = BeautifulSoup(html.text, 'lxml')
    if soup.find(text='本页面目前没有内容。您可以在其他页面中'):
        return None
    voice_list = soup.find_all(attrs={'class': 'visible-md'})[2:]
    info_list = []
    for item in voice_list:
        item_tab = item.find_all(attrs={'class': ''})[1:]
        if isinstance(item_tab[1].next, str):
            return info_list
        info_list.append({
            'title': item_tab[0].text,
            'text': item_tab[5].text,
            '中': item_tab[1].next.attrs.get('data-src', ''),
            '日': item_tab[2].next.attrs.get('data-src', ''),
            '英': item_tab[3].next.attrs.get('data-src', ''),
            '韩': item_tab[4].next.attrs.get('data-src', ''),
        })
    return info_list


# 获取角色语音，通过米游社途径。可获取完整的中日英韩语音。
async def get_voice_info_mys(character_name: str):
    character_name = character_name.strip()
    logger.info('获取数据: %s' % character_name)
    html = await aiorequests.get(url=(BASE_URL_MYS + BASE_URL_MYS_CHARACTERS_LIST))
    soup = BeautifulSoup(html.text, 'lxml')
    soup_char_container = soup.select('.collection-avatar')[0]
    url_char_page = None
    for char_soup in soup_char_container.select('.collection-avatar__title'):
        if char_soup.text.find(character_name) != -1:
            url_char_page = char_soup.parent.attrs.get('href', None)
            break
    if url_char_page is None:
        return None
    html = await aiorequests.get(url=(BASE_URL_MYS + url_char_page))
    soup = BeautifulSoup(html.text, 'lxml')
    soup_voice_languages, soup_voice_lists = soup.select('[data-part="voiceTab"] > ul')
    language_tab_indices = {
        '中': -1,
        '日': -1,
        '英': -1,
        '韩': -1
    }
    for soup_lan in soup_voice_languages.select('li'):
        language = soup_lan.text
        language_tab_index = int(soup_lan.attrs.get('data-index'))
        if language.find('中') != -1 or language.find('汉') != -1:
            language_tab_indices['中'] = language_tab_index
        elif language.find('日') != -1:
            language_tab_indices['日'] = language_tab_index
        elif language.find('英') != -1:
            language_tab_indices['英'] = language_tab_index
        elif language.find('韩') != -1:
            language_tab_indices['韩'] = language_tab_index
    language_voices = {
        '中': [],
        '日': [],
        '英': [],
        '韩': []
    }
    for lan, voice_list in language_voices.items():
        for soup_row in soup_voice_lists.select(f'li[data-index="{language_tab_indices[lan]}"] > table:nth-of-type(2) > tbody > tr'):
            soup_source = soup_row.select('audio > source')
            voice_list.append(soup_source[0].attrs.get('src') if len(soup_source) != 0 else '')

    info_list = []
    soup_title = soup_voice_lists.select('li:first-child > table:nth-of-type(2) > tbody > tr td:nth-child(1)')
    soup_text = soup_voice_lists.select('li:first-child > table:nth-of-type(2) > tbody > tr td:nth-child(2) > div > span')
    for index in range(len(soup_title)):
        info_list.append({
            'title': soup_title[index].text.strip(),
            'text': soup_text[index].text.strip(),
            '中': language_voices['中'][index],
            '日': language_voices['日'][index],
            '英': language_voices['英'][index],
            '韩': language_voices['韩'][index],
        })
    return info_list


# 下载音频文件到本地
async def download(url, path):
    res = await aiorequests.get(url=url, timeout=30)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(res.read())


async def update_voice_data():
    # 获取全部人物列表
    char_list = await get_character_list()
    for char in char_list:
        info = await get_voice_info_mys(char)
        if not info:
            continue
        data = []
        for v in info:
            chn = ''
            jap = ''
            eng = ''
            kor = ''
            for language in config['voice_language']:
                url = v[language]
                if not url:
                    continue
                path = str(Path() / language / char / Path(url).name)
                out_path = OUT_PUT / path
                out = str(out_path)
                if not out_path.exists():
                    await download(url, out)

                if language == '中':
                    chn = path
                elif language == '日':
                    jap = path
                elif language == '英':
                    eng = path
                elif language == '韩':
                    kor = path

                logger.info('下载成功: %s -> %s' % (char, path))

            data.append({
                'title': v['title'],
                'text': v['text'],
                'chn': chn,
                'jap': jap,
                'eng': eng,
                'kor': kor
            })
        # 存入数据库
        db[char] = data


async def voice_list_by_mys():
    url = 'https://api-static.mihoyo.com/common/blackboard/ys_obc/v1/home/content/list?app_sn=ys_obc&channel_id=84'
    resp = await aiorequests.get(url=url, timeout=30)
    json_data = resp.json()
    if json_data['retcode']:
        raise Exception(json_data['message'])
    try:
        data_list = json_data['data']['list'][0]['list']
    except KeyError as e:
        raise Exception('获取语音列表失败, 请联系作者修复')

    return {x['title'].split()[0]: x for x in data_list}


async def voice_detail_by_mys(content_id):
    url = 'https://bbs.mihoyo.com/ys/obc/content/%s/detail?bbs_presentation_style=no_header' % content_id
    res = await aiorequests.get(url=url, timeout=30)
    soup = BeautifulSoup(res.text, 'lxml')
    paragraph_box = soup.select('.obc-tmpl__paragraph-box')

    return [{
        'text': x.get_text(),
        'chn': x.find('source').attrs['src']
    } for x in paragraph_box]
