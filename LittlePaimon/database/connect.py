from typing import List
from tortoise import Tortoise
from nonebot.log import logger
from tortoise.exceptions import OperationalError
from LittlePaimon.config import DB_PATH

db_url = 'sqlite:///' + str(DB_PATH)

# models: List[str] = []
#
#
# def register_model(model: str):
#     models.append(model)
#     logger.opt(colors=True).success(f"<y>数据库:</y><r>载入模型{model.split('.')[-1]}</r>")


async def connect():
    try:
        await Tortoise.init(db_url=db_url, modules={"models": ["LittlePaimon.database.models"]})
        await Tortoise.generate_schemas()
        logger.opt(colors=True).success(f"<y>数据库连接</y><r>成功</r>")
    except OperationalError as e:
        logger.opt(colors=True).warning(f"<y>数据库连接</y><r>失败:{e}</r>")
        raise e


async def disconnect():
    await Tortoise.close_connections()
    logger.opt(colors=True).success(f"<y>数据库连接</y><r>已断开</r>")
