import shutil
from pathlib import Path

from tortoise import Tortoise
from nonebot.log import logger
from LittlePaimon.utils import scheduler, logger as my_logger
from LittlePaimon.utils.path import GENSHIN_DB_PATH, SUB_DB_PATH, GENSHIN_VOICE_DB_PATH, MANAGER_DB_PATH, YSC_TEMP_IMG_PATH
from .models import *

DATABASE = {
    "connections": {
        "paimon_genshin":       {
            "engine":      "tortoise.backends.sqlite",
            "credentials": {"file_path": GENSHIN_DB_PATH},
        },
        "paimon_subscription":  {
            "engine":      "tortoise.backends.sqlite",
            "credentials": {"file_path": SUB_DB_PATH},
        },
        'paimon_genshin_voice': {
            "engine":      "tortoise.backends.sqlite",
            "credentials": {"file_path": GENSHIN_VOICE_DB_PATH},
        },
        'paimon_manager':       {
            "engine":      "tortoise.backends.sqlite",
            "credentials": {"file_path": MANAGER_DB_PATH},
        }
    },
    "apps":        {
        "paimon_genshin":       {
            "models":             ['LittlePaimon.database.models.player_info',
                                   'LittlePaimon.database.models.abyss_info',
                                   'LittlePaimon.database.models.character',
                                   'LittlePaimon.database.models.cookie'],
            "default_connection": "paimon_genshin",
        },
        "paimon_subscription":  {
            "models":             ['LittlePaimon.database.models.subscription'],
            "default_connection": "paimon_subscription",
        },
        "paimon_genshin_voice": {
            "models":             ['LittlePaimon.database.models.genshin_voice'],
            "default_connection": "paimon_genshin_voice",
        },
        "paimon_manager":       {
            "models":             ['LittlePaimon.database.models.manager'],
            "default_connection": "paimon_manager",
        }
    },
}


def register_database(db_name: str, models: List[Union[str, Path]], db_path: Optional[Union[str, Path]]):
    """
    注册数据库
    """
    if db_name in DATABASE['connections'] and db_name in DATABASE['apps']:
        DATABASE['apps'][db_name]['models'].extend(models)
    else:
        DATABASE['connections'][db_name] = {
            "engine":      "tortoise.backends.sqlite",
            "credentials": {"file_path": db_path},
        }
        DATABASE['apps'][db_name] = {
            "models":             models,
            "default_connection": db_name,
        }


async def connect():
    """
    建立数据库连接
    """
    try:
        await Tortoise.init(DATABASE)
        await Tortoise.generate_schemas()
        logger.opt(colors=True).success("<u><y>[数据库]</y></u><g>连接成功</g>")
    except Exception as e:
        logger.opt(colors=True).warning(f"<u><y>[数据库]</y></u><r>连接失败:{e}</r>")
        raise e


async def disconnect():
    """
    断开数据库连接
    """
    await Tortoise.close_connections()
    logger.opt(colors=True).success("<u><y>[数据库]</y></u><r>连接已断开</r>")


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
