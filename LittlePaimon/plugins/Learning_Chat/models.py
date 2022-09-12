import random
import re
import time
from functools import cached_property, cmp_to_key
from typing import Generator, List, Optional, Union, Tuple, Dict, Any

try:
    import jieba_fast.analyse as jieba_analyse
except ImportError:
    import jieba.analyse as jieba_analyse
import pypinyin
from dataclasses import dataclass
from collections import defaultdict
import threading

from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent

from LittlePaimon import NICKNAME
from LittlePaimon.database.models import Message, Context, BlackList, Answers, Answer, BanWord
from .config import config_manager

config = config_manager.config


@dataclass
class MessageData:
    group_id: int
    user_id: int
    raw_message: str
    plain_text: str
    time: int
    bot_id: int

    @cached_property
    def is_plain_text(self) -> bool:
        """
        判断消息是否为纯文本
        """
        return '[CQ:' not in self.raw_message and len(self.plain_text) != 0

    @cached_property
    def is_image(self) -> bool:
        """
        判断消息是否为图片
        """
        return '[CQ:image,' in self.raw_message or '[CQ:face,' in self.raw_message

    @cached_property
    def _keywords_list(self):
        """
        获取纯文本部分的关键词结果
        """
        if not self.is_plain_text and len(self.plain_text) == 0:
            return []

        return jieba_analyse.extract_tags(
            self.plain_text, topK=config.KEYWORDS_SIZE)

    @cached_property
    def keywords_len(self) -> int:
        """
        获取关键词数量
        :return:
        """
        return len(self._keywords_list)

    @cached_property
    def keywords(self) -> str:
        """将关键词列表字符串"""
        if not self.is_plain_text and len(self.plain_text) == 0:
            return self.raw_message

        if self.keywords_len < 2:
            return self.plain_text
        else:
            # keywords_list.sort()
            return ' '.join(self._keywords_list)

    @cached_property
    def keywords_pinyin(self) -> str:
        """将关键词拼音列表字符串"""
        return ''.join([item[0] for item in pypinyin.pinyin(
            self.keywords, style=pypinyin.NORMAL, errors='default')]).lower()

    @cached_property
    def to_me(self) -> bool:
        """判断是否为艾特机器人"""
        return self.plain_text.startswith(NICKNAME)


class LearningChat:
    reply_cache = defaultdict(lambda: defaultdict(list))
    """回复的消息缓存"""
    message_cache = {}
    """群消息缓存"""

    _reply_lock = threading.Lock()
    _message_lock = threading.Lock()
    _save_reserve_size = 100  # 保存时，给内存中保留的大小
    _late_save_time = 0  # 上次保存（消息数据持久化）的时刻 ( time.time(), 秒 )

    def __init__(self, event: Union[GroupMessageEvent, MessageData]):
        if isinstance(event, GroupMessageEvent):
            self.message = MessageData(
                group_id=event.group_id,
                user_id=event.user_id,
                raw_message=re.sub(r',subType=\d+,url=.+]', r']', event.raw_message),
                plain_text=event.get_plaintext(),
                time=event.time,
                bot_id=event.self_id)
        else:
            self.message = event

    async def learn(self) -> bool:
        """学习这句话"""
        if not len(self.message.raw_message.strip()):
            return False

        if self.message.group_id in LearningChat.message_cache:
            group_msgs = LearningChat.message_cache[self.message.group_id]
            # 将群里上一条发言插入数据库
            group_pre_msg = group_msgs[-1] if group_msgs else None
            await self._update_context(group_pre_msg)

            if group_pre_msg and group_pre_msg['user_id'] != self.message.user_id:
                # 该用户在群里的上一条发言（倒序三句之内）
                for msg in group_msgs[:-3:-1]:
                    if msg['user_id'] == self.message.user_id:
                        await self._update_context(msg)
                        break
        await self._update_message()
        return True

    async def answer(self) -> Optional[Generator[Union[Message, Message], None, None]]:
        """获取这句话的回复"""
        if self.message.is_plain_text and len(self.message.plain_text) <= 1:
            """不回复单个字的对话"""
            return None

        if not (results := await self._get_context()):
            return None
        group_id = self.message.group_id
        raw_message = self.message.raw_message
        keywords = self.message.keywords
        bot_id = self.message.bot_id

        group_bot_replies = LearningChat.reply_cache[group_id][bot_id]
        with LearningChat._reply_lock:
            group_bot_replies.append({
                'time':            int(time.time()),
                'pre_raw_message': raw_message,
                'pre_keywords':    keywords,
                'reply':           '[LearningChat: Reply]',  # flag
                'reply_keywords':  '[LearningChat: Reply]',  # flag
            })

        def yield_results(results_: Tuple[List[str], str]) -> Generator[Message, None, None]:
            answer_list, answer_keywords = results_

            for item in answer_list:
                with LearningChat._reply_lock:
                    LearningChat.reply_cache[group_id][bot_id].append({
                        'time':            int(time.time()),
                        'pre_raw_message': raw_message,
                        'pre_keywords':    keywords,
                        'reply':           item,
                        'reply_keywords':  answer_keywords,
                    })
                if '[CQ:' not in item and len(item) > 1 and random.random() < config.voice_probability:
                    yield MessageSegment.record(f'http://233366.proxy.nscc-gz.cn:8888/?text={item}&speaker=派蒙')
                else:
                    yield item

            with LearningChat._reply_lock:
                LearningChat.reply_cache[self.message.group_id][self.message.bot_id] = \
                    LearningChat.reply_cache[self.message.group_id][
                        self.message.bot_id][
                    -self._save_reserve_size:]

        return yield_results(results)

    @staticmethod
    async def speak() -> Optional[Tuple[int, int, List[Message]]]:
        """
        主动发言，返回当前最希望发言的 bot 账号、群号、发言消息 List，也有可能不发言
        """
        basic_msgs_len = 10
        basic_delay = 600

        def group_popularity_cmp(lhs: Tuple[int, List[Dict[str, Any]]],
                                 rhs: Tuple[int, List[Dict[str, Any]]]) -> int:
            def cmp(a: Any, b: Any):
                return (a > b) - (a < b)

            lhs_group_id, lhs_msgs = lhs
            rhs_group_id, rhs_msgs = rhs
            lhs_len = len(lhs_msgs)
            rhs_len = len(rhs_msgs)
            if lhs_len < basic_msgs_len or rhs_len < basic_msgs_len:
                return cmp(lhs_len, rhs_len)

            lhs_duration = lhs_msgs[-1]['time'] - lhs_msgs[0]['time']
            rhs_duration = rhs_msgs[-1]['time'] - rhs_msgs[0]['time']

            if not lhs_duration or not rhs_duration:
                return cmp(lhs_len, rhs_len)

            return cmp(lhs_len / lhs_duration,
                       rhs_len / rhs_duration)

        # 按群聊热度排序
        popularity = sorted(LearningChat.message_cache.items(),
                            key=cmp_to_key(group_popularity_cmp))
        cur_time = time.time()
        for group_id, group_msgs in popularity:
            group_replies = LearningChat.reply_cache[group_id]
            if not len(group_replies) or len(group_msgs) < basic_msgs_len:
                continue

            group_replies_front = list(group_replies.values())[0]
            if not len(group_replies_front) or group_replies_front[-1]['time'] > group_msgs[-1]['time']:
                continue

            msgs_len = len(group_msgs)
            latest_time = group_msgs[-1]['time']
            duration = latest_time - group_msgs[0]['time']
            avg_interval = duration / msgs_len

            if cur_time - latest_time < avg_interval * config.speak_threshold + basic_delay:
                continue
            # append 一个 flag, 防止这个群热度特别高，但压根就没有可用的 context 时，每次 speak 都查这个群，浪费时间
            with LearningChat._reply_lock:
                group_replies_front.append({
                    'time':            int(cur_time),
                    'pre_raw_message': '[PallasBot: Speak]',
                    'pre_keywords':    '[PallasBot: Speak]',
                    'reply':           '[PallasBot: Speak]',
                    'reply_keywords':  '[PallasBot: Speak]',
                })

            available_time = cur_time - 24 * 3600
            speak_context = await Context.filter(count__gt=config.answer_threshold,
                                                 time__gt=available_time).all()
            speak_context_right = []
            for context in speak_context:
                for answer in context.answers:
                    if answer.group_id == group_id and answer.time > available_time and answer.count > config.answer_threshold:
                        speak_context_right.append(context)
                        break
            if not speak_context_right:
                continue
            speak_context_right.sort(key=lambda x: len(x.ban))

            ban_keywords = await LearningChat._get_ban_keywords(speak_context_right[0], group_id)
            messages = [answer.messages
                        for answer in speak_context_right[0].answers
                        if answer.count >= config.answer_threshold
                        and answer.keywords not in ban_keywords
                        and answer.group_id == group_id]
            if not messages:
                continue
            speak = random.choice(random.choice(messages))

            bot_id = random.choice([bid for bid in group_replies.keys() if bid])
            with LearningChat._reply_lock:
                group_replies[bot_id].append({
                    'time':            int(cur_time),
                    'pre_raw_message': '[PallasBot: Speak]',
                    'pre_keywords':    '[PallasBot: Speak]',
                    'reply':           speak,
                    'reply_keywords':  '[PallasBot: Speak]',
                })

            speak_list = [speak]
            while random.random() < config.speak_continuously_probability and len(
                    speak_list) < config.speak_continuously_max_len:
                pre_msg = str(speak_list[-1])
                answer = await LearningChat(MessageData(group_id=group_id,
                                                        user_id=0,
                                                        raw_message=pre_msg,
                                                        plain_text=pre_msg,
                                                        time=int(cur_time),
                                                        bot_id=0)).answer()
                if not answer:
                    break
                speak_list.extend(answer)

            if random.random() < config.speak_poke_probability:
                target_id = random.choice(LearningChat.message_cache[group_id])['user_id']
                speak_list.append(f'[CQ:poke,qq={target_id}]')

            return bot_id, group_id, speak_list

        return None

    @staticmethod
    async def ban(group_id: int, bot_id: int, ban_raw_message: str, reason: str) -> bool:
        """
        禁止以后回复这句话，仅对该群有效果
        """

        if group_id not in LearningChat.reply_cache:
            return False

        ban_reply = None
        reply_data = LearningChat.reply_cache[group_id][bot_id][::-1]

        for reply in reply_data:
            cur_reply = reply['reply']
            # 为空时就直接 ban 最后一条回复
            if not ban_raw_message or ban_raw_message in cur_reply:
                ban_reply = reply
                break

        # 这种情况一般是有些 CQ 码，牛牛发送的时候，和被回复的时候，里面的内容不一样
        if not ban_reply:
            if search := re.search(r'(\[CQ:[a-zA-z0-9-_.]+)', ban_raw_message):
                type_keyword = search[1]
                for reply in reply_data:
                    cur_reply = reply['reply']
                    if type_keyword in cur_reply:
                        ban_reply = reply
                        break

        if not ban_reply:
            return False

        pre_keywords = reply['pre_keywords']
        keywords = reply['reply_keywords']

        ban, _ = await Context.get_or_create(keywords=pre_keywords)
        ban.ban.append(BanWord(keywords=keywords,
                               group_id=group_id,
                               reason=reason,
                               time=int(time.time())))
        await ban.save()
        blacklist, _ = await BlackList.get_or_create(group_id=group_id)
        if keywords in blacklist.answers_reserve:
            blacklist.answers.append(keywords)
        else:
            blacklist.answers_reserve.append(keywords)

        return True

    @staticmethod
    async def persistence(cur_time: int = int(time.time())):
        """
        持久化
        """
        with LearningChat._message_lock:
            if save_list := [msg for group_msgs in LearningChat.message_cache.values() for msg in group_msgs if
                             msg['time'] > LearningChat._late_save_time]:
                LearningChat.message_cache = {group_id: group_msgs[-LearningChat._save_reserve_size:] for
                                              group_id, group_msgs in LearningChat.message_cache.items()}
                LearningChat._late_save_time = cur_time
            else:
                return

        await Message.bulk_create([Message(**msg) for msg in save_list])

    async def _get_context(self):
        """获取上下文消息"""
        if msgs := LearningChat.message_cache.get(self.message.group_id):
            # 是否在复读中
            if len(msgs) >= config.repeat_threshold and all(
                    item['raw_message'] == self.message.raw_message for item in msgs[-config.repeat_threshold + 1:]):
                # 说明当前群里正在复读
                group_bot_replies = LearningChat.reply_cache[self.message.group_id][self.message.bot_id]
                if len(group_bot_replies) and group_bot_replies[-1]['reply'] != self.message.raw_message:
                    return [self.message.raw_message, ], self.message.keywords
                else:
                    # 已经复读过了，不回复
                    return None
        if not (context := await Context.get_or_none(keywords=self.message.keywords)):
            return None

        # 喝醉了的处理，先不做了
        answer_threshold_choice_list = list(
            range(config.answer_threshold - len(config.answer_threshold_weights) + 1, config.answer_threshold + 1))
        answer_count_threshold = random.choices(answer_threshold_choice_list, weights=config.answer_threshold_weights)[
            0]
        if self.message.keywords_len == config.KEYWORDS_SIZE:
            answer_count_threshold -= 1

        cross_group_threshold = 1 if self.message.to_me else config.cross_group_threshold
        ban_keywords = await LearningChat._get_ban_keywords(context, self.message.group_id)

        candidate_answers: Dict[str, Answer] = {}
        other_group_cache: Dict[str, Answer] = {}
        answers_count = defaultdict(int)

        def candidate_append(dst: Dict[str, Answer], answer_: Answer):
            if answer_.keywords not in dst:
                dst[answer_.keywords] = answer_
            else:
                dst[answer_.keywords].count += answer_.count
                dst[answer_.keywords].messages += answer_.messages

        for answer in context.answers:
            if answer.count < answer_count_threshold:
                continue
            if answer.keywords in ban_keywords:
                continue
            sample_msg = answer.messages[0]
            if self.message.is_image and '[CQ:' not in sample_msg:
                # 图片消息不回复纯文本
                continue
            if not self.message.to_me and sample_msg.startswith(NICKNAME):
                continue
            if any(i in sample_msg for i in{'[CQ:xml', '[CQ:json', '[CQ:at', '[CQ:video', '[CQ:record', '[CQ:share'}):
                # 不学xml、json和at
                continue

            if answer.group_id == self.message.group_id:
                candidate_append(candidate_answers, answer)
            else:
                answers_count[answer.keywords] += 1
                cur_count = answers_count[answer.keywords]
                if cur_count < cross_group_threshold:
                    candidate_append(other_group_cache, answer)
                elif cur_count == cross_group_threshold:
                    if cur_count > 1:
                        candidate_append(candidate_answers, other_group_cache[answer.keywords])
                    candidate_append(candidate_answers, answer)
                else:
                    candidate_append(candidate_answers, answer)
        if not candidate_answers:
            return None

        final_answer = random.choices(list(candidate_answers.values()),
                                      weights=[min(answer.count, 10) for answer in candidate_answers.values()])[0]
        answer_str = random.choice(final_answer.messages)
        answer_keywords = final_answer.keywords

        if 0 < answer_str.count('，') <= 3 and '[CQ:' not in answer_str and random.random() < config.split_probability:
            return answer_str.split('，'), answer_keywords
        return [answer_str, ], answer_keywords

    async def _update_context(self, pre_msg):
        if not pre_msg:
            return

        # 在复读，不学
        if pre_msg['raw_message'] == self.message.raw_message:
            return
        # 回复别人的，不学
        if '[CQ:reply' in self.message.raw_message:
            return
        if context := await Context.filter(keywords=pre_msg['keywords']).first():
            context.count += 1
            context.time = self.message.time
            answer_index = next((idx for idx, answer in enumerate(context.answers)
                                 if answer.group_id == self.message.group_id
                                 and answer.keywords == self.message.keywords), -1)
            if answer_index == -1:
                context.answers.append(
                    Answer(
                        keywords=self.message.keywords,
                        group_id=self.message.group_id,
                        count=1,
                        time=self.message.time,
                        messages=[self.message.raw_message]
                    )
                )
            else:
                context.answers[answer_index].count += 1
                context.answers[answer_index].time = self.message.time
                if self.message.is_plain_text:
                    context.answers[answer_index].messages.append(self.message.raw_message)
            await context.save()
        else:
            answer = Answer(
                keywords=self.message.keywords,
                group_id=self.message.group_id,
                count=1,
                time=self.message.time,
                messages=[self.message.raw_message]
            )
            await Context.create(keywords=pre_msg['keywords'],
                                 time=self.message.time,
                                 count=1,
                                 answers=Answers(answers=[answer]))

    async def _update_message(self):
        with LearningChat._message_lock:
            if self.message.group_id not in LearningChat.message_cache:
                LearningChat.message_cache[self.message.group_id] = []
            LearningChat.message_cache[self.message.group_id].append(
                {
                    'group_id':      self.message.group_id,
                    'user_id':       self.message.user_id,
                    'raw_message':   self.message.raw_message,
                    'is_plain_text': self.message.is_plain_text,
                    'plain_text':    self.message.plain_text,
                    'keywords':      self.message.keywords,
                    'time':          self.message.time,
                }
            )

        cur_time = self.message.time
        if LearningChat._late_save_time == 0:
            LearningChat._late_save_time = cur_time - 1
            return

        if len(LearningChat.message_cache[self.message.group_id]) > config.save_count_threshold:
            await LearningChat.persistence(cur_time)
        elif cur_time - LearningChat._late_save_time > config.save_time_threshold:
            await LearningChat.persistence(cur_time)

    @staticmethod
    async def _get_ban_keywords(context: Context, group_id: int) -> set:
        """
        找到在 group_id 群中对应 context 不能回复的关键词
        """
        ban_keywords, _ = await BlackList.get_or_create(group_id=group_id)
        if context.ban:
            ban_count = defaultdict(int)
            for ban in context.ban:
                ban_key = ban.keywords
                if ban.group_id == group_id:
                    ban_keywords.answers.append(ban_key)
                else:
                    ban_count[ban_key] += 1
                    if ban_count[ban_key] == config.cross_group_threshold:
                        ban_keywords.answers.append(ban_key)
        await ban_keywords.save()
        return set(ban_keywords.answers)

    @staticmethod
    async def clear_up_context():
        """
        清理所有超过 15 天没人说、且没有学会的话
        """
        cur_time = int(time.time())
        expiration = cur_time - 15 * 24 * 3600  # 15 天前
        await Context.filter(time__lt=expiration, count__lt=config.answer_threshold).delete()
        contexts = await Context.filter(count__gt=100, clear_time__lt=expiration).all()
        for context in contexts:
            answers = [answer
                       for answer in context.answers
                       if answer.count > 1 or answer.time > expiration]
            context.answers = answers
            context.clear_time = cur_time
            await context.save()
