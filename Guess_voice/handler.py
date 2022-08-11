import datetime
import json
import os
import random
from pathlib import Path
from typing import List

from apscheduler.triggers.date import DateTrigger
from nonebot import get_bot, require, logger
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment, escape
from nonebot.rule import Rule
from sqlitedict import SqliteDict

from .download_data import voice_list_by_mys, voice_detail_by_mys
from .util import get_path, require_file
from ..utils.alias_handler import get_alias_by_name

scheduler = require('nonebot_plugin_apscheduler').scheduler

dir_data = Path() / 'data' / 'LittlePaimon' / 'guess_voice' / 'data'
data_path = Path() / 'data' / 'LittlePaimon' / 'guess_voice' / 'voice'
data2_path = Path() / 'data' / 'LittlePaimon' / 'guess_voice' / 'voice2'

dir_data.mkdir(parents=True, exist_ok=True)

db = {}


def init_db(db_dir, db_name='db.sqlite', tablename='unnamed') -> SqliteDict:
    db_cache_key = db_name + tablename
    if db.get(db_cache_key):
        return db[db_cache_key]
    db[db_cache_key] = SqliteDict(str(get_path(db_dir, db_name)),
                                  tablename=tablename,
                                  encode=json.dumps,
                                  decode=json.loads,
                                  autocommit=True)
    return db[db_cache_key]


user_db = init_db('data', 'user.sqlite')
voice_db = init_db('data', 'voice.sqlite')
voice2_db = init_db('data', 'voice2.sqlite', tablename='voice')
process = {}

with open(os.path.join(os.path.dirname(__file__), 'character.json'), 'r', encoding="utf-8") as f:
    character_json: dict = json.loads(f.read())


def create_guess_matcher(role_name, second, group_id):
    """
    创建一个猜语音的正则匹配matcher，正则内容为角色的别名
    :param role_name: 角色名
    :param second: 结束时间（秒）
    :param group_id: 进行的群组
    :return: None
    """
    def check_group(event: GroupMessageEvent):
        if event.group_id == group_id:
            return True
        return False

    alias_list = get_alias_by_name(role_name)
    re_str = '|'.join(alias_list)
    guess_matcher = on_regex(re_str, temp=True, rule=Rule(check_group))
    guess_matcher.plugin_name = "Guess_voice"
    guess_matcher.expire_time = datetime.datetime.now() + datetime.timedelta(seconds=second)

    @guess_matcher.handle()
    async def _(event: GroupMessageEvent):
        guess = Guess(event.group_id, time=second)
        if guess.is_start():
            await guess.add_answer(event.user_id, event.message.extract_plain_text())


def get_voice_by_language(data, language_name):
    if language_name == '中':
        return data['chn']
    elif language_name == '日':
        return data['jap']
    elif language_name == '英':
        return data['eng']
    elif language_name == '韩':
        return data['kor']


def char_name_by_name(name):
    names = character_json.keys()
    # 是否就是正确的名字
    if name in names:
        return name
    #
    for item in names:
        nickname = character_json[item]
        if name in nickname:
            return item
    return name


async def get_random_voice(name, language='中'):
    char_name = char_name_by_name(name)
    if language == '中':
        # 如果是中文 则选择米游社的源
        mys_list = await voice_list_by_mys()
        char_voices = mys_list.get(char_name)
        if not char_voices:
            return
        voice_list = await voice_detail_by_mys(char_voices['content_id'])
    else:
        voice_list = voice_db.get(char_name)

    if not voice_list:
        return
    temp_voice_list = []
    for v in voice_list:
        voice_path = get_voice_by_language(v, language)
        if voice_path:
            temp_voice_list.append(voice_path)
    if not temp_voice_list:
        return

    voice_path = random.choice(temp_voice_list)

    if language == '中':
        # 如果是中文 则选择米游社的源
        path = os.path.join(data_path, language, char_name, os.path.basename(voice_path))
        await require_file(file=path, url=voice_path)
    else:
        path = os.path.join(data_path, voice_path)

    return path


class Guess:
    time: int
    group_id: int
    group = {}
    retry_count = 0

    def __init__(self, group_id: int, time=30):
        self.time = time
        self.group_id = group_id
        self.group = process.get(self.group_id)

    def is_start(self):
        if not self.group:
            return False
        return self.group['start']

    def set_start(self):
        process[self.group_id] = {'start': True}

    def set_end(self):
        process[self.group_id] = {}

    async def start(self, language: List[str] = None):
        if not language:
            language = ['中']
        # 随机一个语言
        language = random.choice(language)
        # 随机选择一个语音
        if language == '中':
            # 如果是中文 则选择米游社的源
            mys_list = await voice_list_by_mys()

            answer = random.choice(list(mys_list.keys()))
            try:
                db_dict = {
                    answer: await
                            voice_detail_by_mys(mys_list[answer]['content_id'])
                }

                self.retry_count = 0
            except KeyError as e:
                if self.retry_count == 4:
                    self.retry_count = 0
                    raise Exception('获取语音数据失败')
                self.retry_count += 1
                return await self.start([language])

        else:
            answer = random.choice(list(voice_db.keys()))
            db_dict = voice_db

        temp_voice_list = []
        for v in db_dict[answer]:
            if not (answer in v['text']):
                voice_path = get_voice_by_language(v, language)
                if voice_path:
                    temp_voice_list.append(voice_path)

        if not temp_voice_list:
            logger.info('随机到了个哑巴,, 重新随机.. 如果反复出现这个 你应该检查一下数据库')
            return await self.start([language])

        voice_path = random.choice(temp_voice_list)

        if language == '中':
            # 如果是中文 则选择米游社的源
            path = os.path.join(data_path, language, answer, os.path.basename(voice_path))
            await require_file(file=path, url=voice_path)
        else:
            path = os.path.join(data_path, voice_path)

        # 记录答案
        process[self.group_id] = {
            'start':  True,
            'answer': answer,
            'ok':     set()
        }

        job_id = str(self.group_id) + '_guess_voice'
        if scheduler.get_job(job_id, 'default'):
            scheduler.remove_job(job_id, 'default')

        now = datetime.datetime.now()
        notify_time = now + datetime.timedelta(seconds=self.time)
        scheduler.add_job(self.end_game, trigger=DateTrigger(notify_time),
                          id=job_id,
                          misfire_grace_time=60,
                          coalesce=True,
                          jobstore='default',
                          max_instances=1)
        create_guess_matcher(answer, self.time, self.group_id)
        return MessageSegment.record(file=Path(path))

    async def start2(self):
        # hard mode
        if not os.path.exists(data2_path):
            print('请到github下载genshin_voice压缩包解压到 ' + data2_path)
            raise Exception('困难模式语音文件夹不存在')

        names = list(voice2_db.keys())
        if not names:
            raise Exception('数据库错误. 请重新下载数据库文件')

        names.remove('')
        names.remove('派蒙')
        names.remove('旅行者')
        answer = random.choice(names)
        answer_info = None
        while True:
            info = random.choice(voice2_db[answer])
            if answer not in info['text']:
                answer_info = info
                break

        if not answer_info:
            return await self.start2()

        # 记录答案
        process[self.group_id] = {
            'start':  True,
            'answer': answer,
            'ok':     set()
        }

        job_id = str(self.group_id) + '_guess_voice'
        if scheduler.get_job(job_id, 'default'):
            scheduler.remove_job(job_id, 'default')

        now = datetime.datetime.now()
        notify_time = now + datetime.timedelta(seconds=self.time)
        scheduler.add_job(self.end_game, trigger=DateTrigger(notify_time),
                          id=job_id,
                          misfire_grace_time=60,
                          coalesce=True,
                          jobstore='default',
                          max_instances=1)

        path = os.path.join(data2_path, answer_info['file'] + '.mp3')

        return MessageSegment.record(file=Path(path))

    async def end_game(self):
        self.group = process.get(self.group_id)
        ok_list = list(process[self.group_id]['ok'])
        if len(ok_list) > 1:  # 只允许1个人猜对
            return
        if not ok_list:
            msg = '还没有人猜中呢'
        else:
            msg = '回答正确的人: ' + ' '.join([str(MessageSegment.at(qq)) for qq in ok_list])
        msg = '正确答案是 %s\n%s' % (self.group['answer'], msg)
        try:
            await get_bot().send_group_msg(group_id=self.group_id, message=msg)
        except Exception as e:
            logger.error(e)

        # 清理记录
        process[self.group_id] = {}

        # 记录到数据库给之后奖励做处理
        user_group = user_db.get(self.group_id, {})
        if not user_group:
            user_db[self.group_id] = {}

        for user in ok_list:
            info = user_group.get(str(user), {'count': 0})
            info['count'] += 1
            user_group[user] = info
        user_db[self.group_id] = user_group

    # 只添加正确的答案
    async def add_answer(self, qq: int, msg: str):
        if self.group.get('answer'):
            process[self.group_id]['ok'].add(qq)
            job_id = str(self.group_id) + '_guess_voice'
            if scheduler.get_job(job_id, 'default'):
                scheduler.remove_job(job_id, 'default')
            await self.end_game()

    # 获取排行榜
    async def get_rank(self, bot, event):
        user_list = user_db.get(self.group_id, {})

        user_list = sorted(user_list.items(), key=lambda v: v[1]['count'])
        user_list.reverse()
        num = 0
        msg = '本群猜语音排行榜:'
        for user, data in user_list[:10]:
            try:
                user = await bot.get_group_member_info(group_id=event.group_id, user_id=user)
            except:
                user = {'card': user, 'nickname': user}
            num += 1
            msg += f"\n第{num}名: {escape(user['card']) or escape(user['nickname'])}, 猜对{data['count']}次"
        return msg
