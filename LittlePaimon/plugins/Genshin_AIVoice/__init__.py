from typing import Union
from nonebot import on_regex
from nonebot.plugin import PluginMetadata
from nonebot.params import RegexDict
from nonebot.rule import Rule
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, MessageSegment
from nonebot.typing import T_State
from LittlePaimon.utils.tool import freq_limiter
from LittlePaimon.utils.filter import filter_msg
from LittlePaimon.manager.plugin_manager import plugin_manager as pm

__plugin_meta__ = PluginMetadata(
    name='原神语音合成',
    description='原神语音合成',
    usage='...',
    extra={
        'author':   '惜月',
        'version':  '3.0',
        'priority': 8,
    }
)

SUPPORTS_CHARA = ['派蒙', '凯亚', '安柏', '丽莎', '琴', '香菱', '枫原万叶', '迪卢克', '温迪', '可莉', '早柚', '托马', '芭芭拉',
                  '优菈', '云堇', '钟离', '魈', '凝光', '雷电将军', '北斗', '甘雨', '七七', '刻晴', '神里绫华', '戴因斯雷布', '雷泽',
                  '神里绫人', '罗莎莉亚', '阿贝多', '八重神子', '宵宫', '荒泷一斗', '九条裟罗', '夜兰', '珊瑚宫心海', '五郎', '散兵',
                  '女士', '达达利亚', '莫娜', '班尼特', '申鹤', '行秋', '烟绯', '久岐忍', '辛焱', '砂糖', '胡桃', '重云', '菲谢尔',
                  '诺艾尔', '迪奥娜', '鹿野院平藏']

CHARA_RE = '|'.join(SUPPORTS_CHARA)


def is_paimon(event: Union[GroupMessageEvent, PrivateMessageEvent], state: T_State) -> bool:
    if '_matched_dict' in state:
        if not state['_matched_dict']['chara'] and event.is_tome():
            state['_matched_dict']['chara'] = '派蒙'
        return True
    return False


voice_cmd = on_regex(rf'^(?P<chara>({CHARA_RE})?)说(?P<text>[\w，。！？、：；“”‘’〔（）〕——!\?,\.`\'"\(\)\[\]{{}}~\s]+)',
                     priority=90, block=True,
                     state={
                         'pm_name':        '原神语音合成',
                         'pm_description': 'AI语音合成，让原神角色说任何话！',
                         'pm_usage':       '<角色名>说<话>',
                         'pm_priority':    10
                     }, rule=Rule(is_paimon))


@voice_cmd.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent], regex_dict: dict = RegexDict()):
    regex_dict['text'] = filter_msg(regex_dict['text'].replace('\r', '').replace('\n', ''), '星')
    if not freq_limiter.check(
            f'genshin_ai_voice_{event.group_id if isinstance(event, GroupMessageEvent) else event.user_id}'):
        await voice_cmd.finish(
            f'原神语音合成冷却中...剩余{freq_limiter.left(f"genshin_ai_voice_{event.group_id if isinstance(event, GroupMessageEvent) else event.user_id}")}秒')
    freq_limiter.start(f'genshin_ai_voice_{event.group_id if isinstance(event, GroupMessageEvent) else event.user_id}',
                       pm.config.AI_voice_cooldown)
    await voice_cmd.finish(MessageSegment.record(
        f'http://233366.proxy.nscc-gz.cn:8888/?text={regex_dict["text"]}&speaker={regex_dict["chara"]}'))
