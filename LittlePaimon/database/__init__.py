import shutil
from pathlib import Path

from tortoise import Tortoise
from nonebot.log import logger
from LittlePaimon.utils import scheduler, logger as my_logger
from LittlePaimon.utils.path import GENSHIN_DB_PATH, SUB_DB_PATH, GENSHIN_VOICE_DB_PATH, MANAGER_DB_PATH, \
    YSC_TEMP_IMG_PATH
from .models import *

from nonebot import get_driver
from pydantic import BaseModel, Extra, Field, validator
class Config(BaseModel, extra=Extra.ignore):
    ai_draw_api: str = "https://lulu.uedbq.xyz"
    ai_draw_token: str = ""
    ai_draw_cooldown: int = 60
    ai_draw_daily: int = 30
    ai_draw_timeout: int = 60
    ai_draw_revoke: int = 0
    ai_draw_message: Literal["mix", "part", "image"] = "mix"
    ai_draw_rank: int = Field(default=10, ge=0)
    ai_draw_data: Path = Path(__file__).parent
    ai_draw_text: str = "\n图像种子: {seed}\n提示标签: {tags}"
    ai_draw_database: bool = True

    @validator("ai_draw_data")
    def check_path(cls, v: Path):
        if v.exists() and not v.is_dir():
            raise ValueError("必须是有效的文件目录")
        return v
plugin_config = Config.parse_obj(get_driver().config)
data_path = plugin_config.ai_draw_data / "data"
data_path.mkdir(parents=True, exist_ok=True)
sqlite_path = data_path / "aidraw.sqlite"

DATABASE = {
    'connections': {
        'paimon_genshin':       {
            'engine':      'tortoise.backends.sqlite',
            'credentials': {'file_path': GENSHIN_DB_PATH},
        },
        'paimon_subscription':  {
            'engine':      'tortoise.backends.sqlite',
            'credentials': {'file_path': SUB_DB_PATH},
        },
        'paimon_genshin_voice': {
            'engine':      'tortoise.backends.sqlite',
            'credentials': {'file_path': GENSHIN_VOICE_DB_PATH},
        },
        'paimon_manage':       {
            'engine':      'tortoise.backends.sqlite',
            'credentials': {'file_path': MANAGER_DB_PATH},
        },
        "aidraw": {
                "engine": "tortoise.backends.sqlite",
                "credentials": {"file_path": sqlite_path},
        },
        # 'memory_db': 'sqlite://:memory:'
    },
    'apps':        {
        'paimon_genshin':       {
            'models':             [player_info.__name__,
                                   abyss_info.__name__,
                                   character.__name__,
                                   cookie.__name__],
            'default_connection': 'paimon_genshin',
        },
        'paimon_subscription':  {
            'models':             [subscription.__name__],
            'default_connection': 'paimon_subscription',
        },
        'paimon_genshin_voice': {
            'models':             [genshin_voice.__name__],
            'default_connection': 'paimon_genshin_voice',
        },
        'paimon_manage':        {
            'models':             [manage.__name__],
            'default_connection': 'paimon_manage',
        },
        "aidraw": {
                "models": [__name__],
                "default_connection": "aidraw",
        },
        # 'memory_db':            {
        #     'models':             [memory_db.__name__],
        #     'default_connection': 'memory_db',
        # }
    },
    'use_tz': False,
    'timezone': 'Asia/Shanghai'
}


def register_database(db_name: str, models: str, db_path: Optional[Union[str, Path]]):
    """
    注册数据库
    """
    if db_name in DATABASE['connections'] and db_name in DATABASE['apps']:
        DATABASE['apps'][db_name]['models'].append(models)
    else:
        DATABASE['connections'][db_name] = {
            'engine':      'tortoise.backends.sqlite',
            'credentials': {'file_path': db_path},
        }
        DATABASE['apps'][db_name] = {
            'models':             [models],
            'default_connection': db_name,
        }


async def connect():
    """
    建立数据库连接
    """
    try:
        await Tortoise.init(DATABASE)
        await Tortoise.generate_schemas()
        logger.opt(colors=True).success('<u><y>[数据库]</y></u><g>连接成功</g>')
    except Exception as e:
        logger.opt(colors=True).warning(f'<u><y>[数据库]</y></u><r>连接失败:{e}</r>')
        raise e


async def disconnect():
    """
    断开数据库连接
    """
    await Tortoise.close_connections()
    logger.opt(colors=True).success('<u><y>[数据库]</y></u><r>连接已断开</r>')


@scheduler.scheduled_job('cron', hour=0, minute=0, misfire_grace_time=10)
async def daily_reset():
    """
    重置数据库相关设置
    """
    now = datetime.datetime.now()

    my_logger.info('原神实时便签', '重置每日提醒次数限制')
    await DailyNoteSub.all().update(today_remind_num=0)

    my_logger.info('原神Cookie', '清空每日Cookie缓存和限制')
    await CookieCache.all().delete()
    await PublicCookie.filter(status=2).update(status=1)

    my_logger.info('功能调用统计', '清除超过一个月的统计数据')
    await PluginStatistics.filter(time__lt=now - datetime.timedelta(days=30)).delete()

    if now.weekday() == 0:
        my_logger.info('原神猜语音', '清空每周排行榜')
        await GuessVoiceRank.all().delete()

    if YSC_TEMP_IMG_PATH.exists():
        shutil.rmtree(YSC_TEMP_IMG_PATH)
    YSC_TEMP_IMG_PATH.mkdir(parents=True, exist_ok=True)

    # await MysAuthKey.filter()
