import os
import asyncio
import sys
from pathlib import Path

from nonebot import on_command, get_bot
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me
from nonebot.params import CommandArg, ArgPlainText
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.adapters.onebot.v11.helpers import convert_chinese_to_bool
from LittlePaimon import NICKNAME, DRIVER, SUPERUSERS, __version__

update_cmd = on_command('更新', permission=SUPERUSER, rule=to_me(), priority=1, block=True)
reboot_cmd = on_command('重启', permission=SUPERUSER, rule=to_me(), priority=1, block=True)
run_cmd = on_command('cmd', permission=SUPERUSER, rule=to_me(), priority=1, block=True)

__plugin_meta__ = PluginMetadata(
    name='机器人管理',
    description='机器人管理',
    usage='...',
    extra={
        'priority': 16,
        'show':     False
    }
)


@update_cmd.handle()
async def _(event: MessageEvent):
    await update_cmd.send(f'{NICKNAME}开始执行git pull更新', at_sender=True)
    p = await asyncio.subprocess.create_subprocess_shell('git pull', stdout=asyncio.subprocess.PIPE,
                                                         stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await p.communicate()
    results = (stdout or stderr).decode('utf-8').split('\n')
    result_msg = ''.join(result.split('|')[0].strip(' ') + '\n' for result in results)
    await update_cmd.finish(f'更新结果：{result_msg}')


@reboot_cmd.got('confirm', prompt='确定要重启吗？(是|否)')
async def _(event: MessageEvent):
    if convert_chinese_to_bool(event.message):
        await reboot_cmd.send(f'{NICKNAME}开始执行重启，请等待{NICKNAME}的归来', at_sender=True)
        (Path() / 'rebooting.json').open('w').close()
        if sys.argv[0].endswith('nb'):
            sys.argv[0] = 'bot.py'
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        await reboot_cmd.finish('取消重启')


@run_cmd.handle()
async def _(event: MessageEvent, state: T_State, cmd: Message = CommandArg()):
    if cmd:
        state['cmd'] = cmd


@run_cmd.got('cmd', prompt='你输入你要运行的命令')
async def _(event: MessageEvent, cmd: str = ArgPlainText('cmd')):
    await run_cmd.send(f'开始执行{cmd}...', at_sender=True)
    p = await asyncio.subprocess.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE,
                                                         stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await p.communicate()
    await run_cmd.finish(f'{cmd}\n运行结果：\n{(stdout or stderr).decode("utf-8")}')


@DRIVER.on_bot_connect
async def _():
    if (Path() / 'rebooting.json').exists():
        await get_bot().send_private_msg(user_id=SUPERUSERS[0], message=f'{NICKNAME}已重启完成，当前版本为{__version__}')
        (Path() / 'rebooting.json').unlink()
