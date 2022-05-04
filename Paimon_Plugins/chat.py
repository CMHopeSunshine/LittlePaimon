from nonebot import on_regex, logger
from nonebot.exception import FinishedException
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from ..utils.util import FreqLimiter2
from pathlib import Path
import random
import os

chat_list = {
    '确实':   {'pattern': r'.*(雀食|确实).*', 'cooldown': 60, 'pro': 0.6, 'files': ['雀食', '确实']},
    '坏了':   {'pattern': r'.*派蒙.*坏.*', 'cooldown': 60, 'pro': 0.6, 'files': ['你才坏！', '瞎说啥呢？', '派蒙怎么可能会坏！']},
    '诶嘿':   {'pattern': r'.*(诶嘿|哎嘿|欸嘿).*', 'cooldown': 120, 'pro': 0.5, 'files': ['诶嘿.mp3', '诶嘿cn.mp3']},
    '进不去':  {'pattern': r'.*进不?(来|去).*', 'cooldown': 180, 'pro': 0.5, 'files': ['进不去.mp3']},
    '派蒙是谁': {'pattern': r'.*(派蒙.*是(什么|谁))|((什么|谁)是?.*派蒙).*', 'cooldown': 240, 'pro': 1,
             'files': ['嘿嘿你猜.mp3', '中二派蒙.mp3', '伙伴.mp3']},
    '大佬':   {'pattern': r'.*((大|巨)佬)|带带|帮帮|邦邦.*', 'cooldown': 240, 'pro': 0.6, 'files': ['大佬nb.mp3']},
    '好色':   {'pattern': r'.*好色|变态(哦|噢)?', 'cooldown': 300, 'pro': 0.5, 'files': ['好色哦.mp3', '好变态.mp3']},
    '无语':   {'pattern': r'.*(\.{3,9})|(\。{3,9})|无语|无话可说.*', 'cooldown': 300, 'pro': 0.6, 'files': ['无语.mp3', '冷淡反应.mp3']},
    '祝福':   {'pattern': r'.*派蒙.*(祝福|吟唱|施法).*', 'cooldown': 360, 'pro': 1, 'files': ['来个祝福.mp3']},
    '相信':   {'pattern': r'.*信?不信|信我.*', 'cooldown': 360, 'pro': 0.5, 'files': ['我信你个鬼.mp3', '真的假的.mp3']},
    '憨批':   {'pattern': r'.*(憨批|傻(逼|B|b)).*', 'cooldown': 360, 'pro': 0.5, 'files': ['憨批.mp3']},
    '可爱':   {'pattern': r'.*可爱|卡哇伊', 'cooldown': 360, 'pro': 0.5, 'files': ['真是个小可爱.mp3']},
    '绿茶':   {'pattern': r'.*派蒙.*(giegie|绿茶).*', 'cooldown': 360, 'pro': 1, 'files': ['绿茶派.mp3']},
    '不是吧':  {'pattern': r'不(是|会)吧', 'cooldown': 300, 'pro': 0.5, 'files': ['不是吧阿sir.mp3']},
    '好耶':   {'pattern': r'好耶|太(好|棒)(了|啦)|好(\!|\！)', 'cooldown': 180, 'pro': 0.75, 'files': ['好耶.mp3', '太好啦.mp3']},
    '好听':   {'pattern': r'(好|真|非常)?好听(\!|\！)?', 'cooldown': 360, 'pro': 0.4, 'files': ['好听.mp3']},
    '耽误时间': {'pattern': r'快{1,4}|gkd|搞?快点|赶紧的?|(.*耽误.*时间.*)', 'cooldown': 360, 'pro': 0.6, 'files': ['耽误时间.mp3']},
    '不可以':  {'pattern': r'不(可以|行|能)(吧|的|噢)?', 'cooldown': 180, 'pro': 0.6, 'files': ['不可以.mp3']},
    '好意思':  {'pattern': r'.*好意思.*', 'cooldown': 300, 'pro': 0.5, 'files': ['好意思.mp3']},
    '不要啊':  {'pattern': r'不(好|要)(吧|啊)?', 'cooldown': 180, 'pro': 0.5, 'files': ['不要啊.mp3']},
    '羡慕':   {'pattern': r'.*羡慕.*', 'cooldown': 180, 'pro': 0.5, 'files': ['羡慕.mp3']},
    '过分':   {'pattern': r'.*过分.*', 'cooldown': 300, 'pro': 0.5, 'files': ['好过分.mp3']},
    '不明白':  {'pattern': r'.*明白.*', 'cooldown': 300, 'pro': 0.5, 'files': ['不明白.mp3']},
    '哪里不对': {'pattern': r'(是|对)(吧|吗)', 'cooldown': 300, 'pro': 0.5, 'files': ['哪里不对.mp3']}
}

res_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'res', 'voice')
chat_lmt = FreqLimiter2(60)


def create_matcher(chat_word: str, pattern: str, cooldown: int, pro: float, responses):
    hammer = on_regex(pattern, priority=16, temp=True)

    @hammer.handle()
    async def handler(event: GroupMessageEvent):
        if not chat_lmt.check(event.group_id, chat_word):
            return
        else:
            if not random.random() < pro:
                return
            else:
                try:
                    chat_lmt.start_cd(event.group_id, chat_word, cooldown)
                    response = random.choice(responses)
                    if '.mp3' not in response:
                        await hammer.finish(response)
                    else:
                        print(os.path.join(res_path, response))
                        await hammer.finish(MessageSegment.record(file=Path(os.path.join(res_path, response))))
                except FinishedException:
                    raise
                except Exception as e:
                    logger.error('派蒙发送语音失败', e)


for k, v in chat_list.items():
    create_matcher(k, v['pattern'], v['cooldown'], v['pro'], v['files'])

