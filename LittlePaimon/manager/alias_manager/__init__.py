from argparse import Namespace
from nonebot import on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.plugin import PluginMetadata
from nonebot.params import ShellCommandArgs
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, PrivateMessageEvent

from .handler import handle, get_id
from .alias_list import aliases

__plugin_meta__ = PluginMetadata(
    name="命令别名",
    description="为机器人指令创建别名",
    usage=(
        "添加别名：alias {name}={command}\n"
        "查看别名：alias {name}\n"
        "别名列表：alias -p\n"
        "删除别名：unalias {name}\n"
        "清空别名：unalias -a"
    ),
    extra={
        "unique_name": "alias",
        "example": "alias '喷水'='echo 呼风唤雨'\nunalias '喷水'",
        "author": "meetwq <meetwq@gmail.com>",
        "version": "0.3.2",
    },
)


alias_parser = ArgumentParser()
alias_parser.add_argument("-p", "--print", action="store_true")
alias_parser.add_argument("-g", "--globally", action="store_true")
alias_parser.add_argument("names", nargs="*")

alias = on_shell_command("alias", parser=alias_parser, priority=10, block=True)

unalias_parser = ArgumentParser()
unalias_parser.add_argument("-a", "--all", action="store_true")
unalias_parser.add_argument("-g", "--globally", action="store_true")
unalias_parser.add_argument("names", nargs="*")

unalias = on_shell_command("unalias", parser=unalias_parser, priority=10)


@alias.handle()
async def _(bot: Bot, event: MessageEvent, args: Namespace = ShellCommandArgs()):
    gl = args.globally
    id = "global" if gl else get_id(event)
    word = "全局别名" if gl else "别名"

    if args.print:
        message = "全局别名：" if gl else ""
        alias_all = aliases.get_alias_all(id)
        for name in sorted(alias_all):
            message += f"\n{name}='{alias_all[name]}'"
        if not gl:
            alias_all_gl = aliases.get_alias_all("global")
            if alias_all_gl:
                message += "\n全局别名："
                for name in sorted(alias_all_gl):
                    message += f"\n{name}='{alias_all_gl[name]}'"
        message = message.strip()
        if message:
            await alias.finish(message)
        else:
            await alias.finish(f"尚未添加任何{word}")

    is_admin = event.sender.role in ["admin", "owner"]
    is_superuser = str(event.user_id) in bot.config.superusers
    is_private = isinstance(event, PrivateMessageEvent)

    if gl and not is_superuser:
        await alias.finish("管理全局别名需要超级用户权限！")

    if not (is_admin or is_superuser or is_private):
        await alias.finish("管理别名需要群管理员权限！")

    message = ""
    names = args.names
    for name in names:
        if "=" in name:
            name, command = name.split("=", 1)
            if name and command and aliases.add_alias(id, name, command):
                message += f"成功添加{word}：{name}='{command}'\n"
        else:
            command = aliases.get_alias(id, name)
            if command:
                message += f"{name}='{command}'\n"
            else:
                message += f"不存在的{word}：{name}\n"

    message = message.strip()
    if message:
        await alias.send(message)


@unalias.handle()
async def _(bot: Bot, event: MessageEvent, args: Namespace = ShellCommandArgs()):
    gl = args.globally
    id = "global" if gl else get_id(event)
    word = "全局别名" if gl else "别名"

    is_admin = event.sender.role in ["admin", "owner"]
    is_superuser = str(event.user_id) in bot.config.superusers
    is_private = isinstance(event, PrivateMessageEvent)

    if gl and not is_superuser:
        await alias.finish("管理全局别名需要超级用户权限！")

    if not (is_admin or is_superuser or is_private):
        await alias.finish("管理别名需要群管理员权限！")

    if args.all and aliases.del_alias_all(id):
        await unalias.finish(f"成功删除所有{word}")

    message = ""
    names = args.names
    for name in names:
        if aliases.get_alias(id, name):
            if aliases.del_alias(id, name):
                message += f"成功删除{word}：{name}\n"
        else:
            message += f"不存在的{word}：{name}\n"

    message = message.strip()
    if message:
        await unalias.send(message)