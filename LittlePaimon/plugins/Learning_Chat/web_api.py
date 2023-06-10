from typing import Optional, Union

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from nonebot import get_bot

from LittlePaimon.plugins.Learning_Chat.models import (
    ChatMessage,
    ChatContext,
    ChatAnswer,
    ChatBlackList,
)
from LittlePaimon.web.api import BaseApiRouter
from LittlePaimon.web.api.utils import authentication

try:
    import jieba_fast as jieba
except ImportError:
    import jieba

from .handler import LearningChat
from .config import config_manager

route = APIRouter()


@route.get(
    "/chat_global_config", response_class=JSONResponse, dependencies=[authentication()]
)
async def get_chat_global_config():
    try:
        bot = get_bot()
        groups = await bot.get_group_list()
        member_list = []
        for group in groups:
            members = await bot.get_group_member_list(group_id=group["group_id"])
            member_list.extend(
                [
                    {
                        "label": f'{member["nickname"] or member["card"]}({member["user_id"]})',
                        "value": member["user_id"],
                    }
                    for member in members
                ]
            )
        config = config_manager.config.dict(exclude={"group_config"})
        config["member_list"] = member_list
        return config
    except ValueError:
        return {"status": -100, "msg": "获取群和好友列表失败，请确认已连接GOCQ"}


@route.post(
    "/chat_global_config", response_class=JSONResponse, dependencies=[authentication()]
)
async def post_chat_global_config(data: dict):
    config_manager.config.update(**data)
    config_manager.save()
    await ChatContext.filter(count__gt=config_manager.config.learn_max_count).update(
        count=config_manager.config.learn_max_count
    )
    await ChatAnswer.filter(count__gt=config_manager.config.learn_max_count).update(
        count=config_manager.config.learn_max_count
    )
    jieba.load_userdict(config_manager.config.dictionary)
    return {"status": 0, "msg": "保存成功"}


@route.get(
    "/chat_group_config", response_class=JSONResponse, dependencies=[authentication()]
)
async def get_chat_global_config(group_id: int):
    try:
        members = await get_bot().get_group_member_list(group_id=group_id)
        member_list = [
            {
                "label": f'{member["nickname"] or member["card"]}({member["user_id"]})',
                "value": member["user_id"],
            }
            for member in members
        ]
        config = config_manager.get_group_config(group_id).dict()
        config["break_probability"] = config["break_probability"] * 100
        config["speak_continuously_probability"] = (
            config["speak_continuously_probability"] * 100
        )
        config["speak_poke_probability"] = config["speak_poke_probability"] * 100
        config["member_list"] = member_list
        return config
    except ValueError:
        return {"status": -100, "msg": "获取群和好友列表失败，请确认已连接GOCQ"}


@route.post(
    "/chat_group_config", response_class=JSONResponse, dependencies=[authentication()]
)
async def post_chat_global_config(group_id: Union[int, str], data: dict):
    if not data["answer_threshold_weights"]:
        return {"status": 400, "msg": "回复阈值权重不能为空，必须至少有一个数值"}
    else:
        data["break_probability"] = data["break_probability"] / 100
        data["speak_continuously_probability"] = (
            data["speak_continuously_probability"] / 100
        )
        data["speak_poke_probability"] = data["speak_poke_probability"] / 100
        if group_id != "all":
            groups = [{"group_id": group_id}]
        else:
            groups = await get_bot().get_group_list()
        for group in groups:
            config = config_manager.get_group_config(group["group_id"])
            config.update(**data)
            config_manager.config.group_config[group["group_id"]] = config
        config_manager.save()
        return {"status": 0, "msg": "保存成功"}


@route.get(
    "/get_chat_messages", response_class=JSONResponse, dependencies=[authentication()]
)
async def get_chat_messages(
    page: int = 1,
    perPage: int = 10,
    orderBy: str = "time",
    orderDir: str = "desc",
    group_id: Optional[str] = None,
    user_id: Optional[str] = None,
    message: Optional[str] = None,
):
    orderBy = (
        (orderBy or "time")
        if (orderDir or "desc") == "asc"
        else f'-{orderBy or "time"}'
    )
    filter_args = {
        f"{k}__contains": v
        for k, v in {
            "group_id": group_id,
            "user_id": user_id,
            "raw_message": message,
        }.items()
        if v
    }
    return {
        "status": 0,
        "msg": "ok",
        "data": {
            "items": await ChatMessage.filter(**filter_args)
            .order_by(orderBy)
            .offset((page - 1) * perPage)
            .limit(perPage)
            .values(),
            "total": await ChatMessage.filter(**filter_args).count(),
        },
    }


@route.get(
    "/get_chat_contexts", response_class=JSONResponse, dependencies=[authentication()]
)
async def get_chat_context(
    page: int = 1,
    perPage: int = 10,
    orderBy: str = "time",
    orderDir: str = "desc",
    keywords: Optional[str] = None,
):
    orderBy = (
        (orderBy or "time")
        if (orderDir or "desc") == "asc"
        else f'-{orderBy or "time"}'
    )
    filter_arg = {"keywords__contains": keywords} if keywords else {}
    return {
        "status": 0,
        "msg": "ok",
        "data": {
            "items": await ChatContext.filter(**filter_arg)
            .order_by(orderBy)
            .offset((page - 1) * perPage)
            .limit(perPage)
            .values(),
            "total": await ChatContext.filter(**filter_arg).count(),
        },
    }


@route.get(
    "/get_chat_answers", response_class=JSONResponse, dependencies=[authentication()]
)
async def get_chat_answers(
    context_id: Optional[int] = None,
    page: int = 1,
    perPage: int = 10,
    orderBy: str = "count",
    orderDir: str = "desc",
    keywords: Optional[str] = None,
):
    filter_arg = {"context_id": context_id} if context_id else {}
    if keywords:
        filter_arg["keywords__contains"] = keywords  # type: ignore
    orderBy = (
        (orderBy or "count")
        if (orderDir or "desc") == "asc"
        else f'-{orderBy or "count"}'
    )
    return {
        "status": 0,
        "msg": "ok",
        "data": {
            "items": list(
                map(
                    lambda x: x.update(
                        {"messages": [{"msg": m} for m in x["messages"]]}
                    )
                    or x,
                    await ChatAnswer.filter(**filter_arg)
                    .order_by(orderBy)
                    .offset((page - 1) * perPage)
                    .limit(perPage)
                    .values(),
                )
            ),
            "total": await ChatAnswer.filter(**filter_arg).count(),
        },
    }


@route.get(
    "/get_chat_blacklist", response_class=JSONResponse, dependencies=[authentication()]
)
async def get_chat_blacklist(
    page: int = 1,
    perPage: int = 10,
    keywords: Optional[str] = None,
    bans: Optional[str] = None,
):
    filter_arg = {"keywords__contains": keywords} if keywords else {}
    items = (
        await ChatBlackList.filter(**filter_arg)
        .offset((page - 1) * perPage)
        .limit(perPage)
        .values()
    )
    for item in items:
        item["bans"] = "全局禁用" if item["global_ban"] else str(item["ban_group_id"][0])
    if bans:
        items = list(filter(lambda x: bans in x["bans"], items))
    return {
        "status": 0,
        "msg": "ok",
        "data": {
            "items": items,
            "total": await ChatBlackList.filter(**filter_arg).count(),
        },
    }


@route.delete(
    "/delete_chat", response_class=JSONResponse, dependencies=[authentication()]
)
async def delete_chat(id: int, type: str):
    try:
        if type == "message":
            await ChatMessage.filter(id=id).delete()
        elif type == "context":
            c = await ChatContext.get(id=id)
            await ChatAnswer.filter(context=c).delete()
            await c.delete()
        elif type == "answer":
            await ChatAnswer.filter(id=id).delete()
        elif type == "blacklist":
            await ChatBlackList.filter(id=id).delete()
        return {"status": 0, "msg": "删除成功"}
    except Exception as e:
        return {"status": 500, "msg": f"删除失败，{e}"}


@route.put("/ban_chat", response_class=JSONResponse, dependencies=[authentication()])
async def ban_chat(id: int, type: str):
    try:
        if type == "message":
            data = await ChatMessage.get(id=id)
        elif type == "context":
            data = await ChatContext.get(id=id)
        else:
            data = await ChatAnswer.get(id=id)
        await LearningChat.add_ban(data)
        return {"status": 0, "msg": "禁用成功"}
    except Exception as e:
        return {"status": 500, "msg": f"禁用失败: {e}"}


@route.put("/delete_all", response_class=JSONResponse, dependencies=[authentication()])
async def delete_all(type: str, id: Optional[int] = None):
    try:
        if type == "message":
            await ChatMessage.all().delete()
        elif type == "context":
            await ChatContext.all().delete()
        elif type == "answer":
            if id:
                await ChatAnswer.filter(context_id=id).delete()
            else:
                await ChatAnswer.all().delete()
        elif type == "blacklist":
            await ChatBlackList.all().delete()
        return {"status": 0, "msg": "操作成功"}
    except Exception as e:
        return {"status": 500, "msg": f"操作失败，{e}"}


BaseApiRouter.include_router(route)
