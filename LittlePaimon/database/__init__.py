from tortoise import Tortoise
from nonebot.log import logger
from LittlePaimon.config import GENSHIN_DB_PATH, SUB_DB_PATH, GENSHIN_VOICE_DB_PATH, MANAGER_DB_PATH, LEARNING_CHAT_DB_PATH


DATABASE = {
    "connections": {
        "genshin": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": GENSHIN_DB_PATH},
        },
        "subscription": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": SUB_DB_PATH},
        },
        'genshin_voice': {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": GENSHIN_VOICE_DB_PATH},
        },
        'manager': {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": MANAGER_DB_PATH},
        },
        'learning_chat': {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": LEARNING_CHAT_DB_PATH},
        },
    },
    "apps": {
        "genshin": {
            "models": ['LittlePaimon.database.models.player_info', 'LittlePaimon.database.models.abyss_info', 'LittlePaimon.database.models.character', 'LittlePaimon.database.models.cookie'],
            "default_connection": "genshin",
        },
        "subscription": {
            "models": ['LittlePaimon.database.models.subscription'],
            "default_connection": "subscription",
        },
        "genshin_voice": {
            "models": ['LittlePaimon.database.models.genshin_voice'],
            "default_connection": "genshin_voice",
        },
        "manager": {
            "models": ['LittlePaimon.database.models.manager'],
            "default_connection": "manager",
        },
        "learning_chat": {
            "models": ['LittlePaimon.database.models.learning_chat'],
            "default_connection": "learning_chat",
        }
    },
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
        logger.opt(colors=True).warning("<u><y>[数据库]</y></u><r>连接失败:{e}</r>")
        raise e


async def disconnect():
    """
    断开数据库连接
    """
    await Tortoise.close_connections()
    logger.opt(colors=True).success("<u><y>[数据库]</y></u><r>连接已断开</r>")
