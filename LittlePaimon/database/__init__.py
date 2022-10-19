from pathlib import Path
from typing import List, Optional, Union

from tortoise import Tortoise
from nonebot.log import logger
from LittlePaimon.config import GENSHIN_DB_PATH, SUB_DB_PATH, GENSHIN_VOICE_DB_PATH, MANAGER_DB_PATH, LEARNING_CHAT_DB_PATH


# DATABASE = {
#     "connections": {
#         "genshin": {
#             "engine": "tortoise.backends.sqlite",
#             "credentials": {"file_path": GENSHIN_DB_PATH},
#         },
#         "subscription": {
#             "engine": "tortoise.backends.sqlite",
#             "credentials": {"file_path": SUB_DB_PATH},
#         },
#         'genshin_voice': {
#             "engine": "tortoise.backends.sqlite",
#             "credentials": {"file_path": GENSHIN_VOICE_DB_PATH},
#         },
#         'manager': {
#             "engine": "tortoise.backends.sqlite",
#             "credentials": {"file_path": MANAGER_DB_PATH},
#         },
#         'learning_chat': {
#             "engine": "tortoise.backends.sqlite",
#             "credentials": {"file_path": LEARNING_CHAT_DB_PATH},
#         },
#     },
#     "apps": {
#         "genshin": {
#             "models": ['LittlePaimon.database.models.player_info', 'LittlePaimon.database.models.abyss_info', 'LittlePaimon.database.models.character', 'LittlePaimon.database.models.cookie'],
#             "default_connection": "genshin",
#         },
#         "subscription": {
#             "models": ['LittlePaimon.database.models.subscription'],
#             "default_connection": "subscription",
#         },
#         "genshin_voice": {
#             "models": ['LittlePaimon.database.models.genshin_voice'],
#             "default_connection": "genshin_voice",
#         },
#         "manager": {
#             "models": ['LittlePaimon.database.models.manager'],
#             "default_connection": "manager",
#         },
#         "learning_chat": {
#             "models": ['LittlePaimon.database.models.learning_chat'],
#             "default_connection": "learning_chat",
#         }
#     },
# }
DATABASE = [
    {
        'db_url': f'sqlite://{GENSHIN_DB_PATH}',
        'models': ['LittlePaimon.database.models.player_info', 'LittlePaimon.database.models.abyss_info', 'LittlePaimon.database.models.character', 'LittlePaimon.database.models.cookie'],
    },
    {
        'db_url': f'sqlite://{SUB_DB_PATH}',
        'models': ['LittlePaimon.database.models.subscription'],
    },
    {
        'db_url': f'sqlite://{GENSHIN_VOICE_DB_PATH}',
        'models': ['LittlePaimon.database.models.genshin_voice'],
    },
    {
        'db_url': f'sqlite://{MANAGER_DB_PATH}',
        'models': ['LittlePaimon.database.models.manager'],
    },
    {
        'db_url': f'sqlite://{LEARNING_CHAT_DB_PATH}',
        'models': ['LittlePaimon.database.models.learning_chat'],
    },
]


def register_database(db_path: Optional[Union[str, Path]], models: List[Union[str, Path]]):
    """
    注册数据库
    """
    DATABASE.append({
        'db_url': f'sqlite://{db_path}',
        'models': models,
    })


async def connect():
    """
    建立数据库连接
    """
    try:
        for db in DATABASE:
            await Tortoise.init(
                db_url=db['db_url'],
                modules={'models': db['models']},
            )
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
