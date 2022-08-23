import shlex
from expandvars import expand, ExpandvarsException

from .alias_list import aliases


def parse_msg(msg: str, id: str) -> str:
    alias_all = aliases.get_alias_all(id)
    alias_all_gl = aliases.get_alias_all("global")
    alias_all_gl.update(alias_all)
    for name in sorted(alias_all_gl, reverse=True):
        if msg.startswith(name):
            return replace_msg(name, msg, alias_all_gl[name])
    return msg


def replace_msg(cmd: str, msg: str, alias: str) -> str:
    if "$" not in alias:
        return alias + msg[len(cmd):]

    args = parse_args(cmd, msg)
    env = set_env(args)
    return parse_alias(alias, env)


def parse_args(cmd: str, msg: str) -> list:
    if cmd.strip() == msg.strip():
        return []
    arg = msg[len(cmd):]
    try:
        return shlex.split(arg)
    except ValueError:
        return [arg]


def set_env(args: list) -> dict:
    env = {}
    for i, arg in enumerate(args, start=1):
        env[str(i)] = arg
    env["a"] = " ".join(args)
    return env


def parse_alias(alias: str, env: dict = {}) -> str:
    try:
        return expand(alias, environ=env)
    except ExpandvarsException:
        return alias
