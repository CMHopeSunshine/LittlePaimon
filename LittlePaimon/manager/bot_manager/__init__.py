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
from nonebot.adapters.onebot.v11 import Message, MessageEvent, GroupMessageEvent
from nonebot.adapters.onebot.v11.helpers import convert_chinese_to_bool
from LittlePaimon import NICKNAME, DRIVER, SUPERUSERS, __version__
from LittlePaimon.utils.files import save_json, load_json
from .handler import check_update, update

__plugin_meta__ = PluginMetadata(
    name='小派蒙管理',
    description='小派蒙管理',
    usage='...',
    extra={
        'author':   '惜月',
        'version':  '3.0',
        'priority': 99,
    }
)

update_cmd = on_command('更新', permission=SUPERUSER, rule=to_me(), priority=1, block=True, state={
    'pm_name':        'bot_update',
    'pm_description': '从Git中更新bot，需超级用户权限',
    'pm_usage':       '@bot 更新',
    'pm_priority':    2
})
check_update_cmd = on_command('检查更新', permission=SUPERUSER, rule=to_me(), priority=1, block=True, state={
    'pm_name':        'bot_check_update',
    'pm_description': '从Git检查bot更新情况，需超级用户权限',
    'pm_usage':       '@bot 检查更新',
    'pm_priority':    1
})
reboot_cmd = on_command('重启', permission=SUPERUSER, rule=to_me(), priority=1, block=True, state={
    'pm_name':        'bot_restart',
    'pm_description': '执行重启操作，需超级用户权限',
    'pm_usage':       '@bot 重启',
    'pm_priority':    3
})
run_cmd = on_command('cmd', permission=SUPERUSER, rule=to_me(), priority=1, block=True, state={
    'pm_name':        'bot_cmd',
    'pm_description': '运行终端命令，需超级用户权限',
    'pm_usage':       '@bot cmd<命令>',
    'pm_priority':    4
})


@update_cmd.handle()
async def _(event: MessageEvent):
    await update_cmd.send(f'{NICKNAME}开始更新', at_sender=True)
    result = await update()
    await update_cmd.finish(result, at_sender=True)
    # p = await asyncio.subprocess.create_subprocess_shell('git pull', stdout=asyncio.subprocess.PIPE,
    #                                                      stderr=asyncio.subprocess.PIPE)
    # stdout, stderr = await p.communicate()
    # results = (stdout or stderr).decode('utf-8').split('\n')
    # result_msg = ''.join(result.split('|')[0].strip(' ') + '\n' for result in results)
    # await update_cmd.finish(f'更新结果：{result_msg}')


@check_update_cmd.handle()
async def _(event: MessageEvent):
    result = await check_update()
    await check_update_cmd.finish(result, at_sender=True)


@reboot_cmd.got('confirm', prompt='确定要重启吗？(是|否)')
async def _(event: MessageEvent):
    if convert_chinese_to_bool(event.message):
        await reboot_cmd.send(f'{NICKNAME}开始执行重启，请等待{NICKNAME}的归来', at_sender=True)
        save_json({'session_type': event.message_type, 'session_id': event.group_id if isinstance(event, GroupMessageEvent) else event.user_id}, Path() / 'rebooting.json')
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
    try:
        result = (stdout or stderr).decode('utf-8')
    except Exception:
        result = str(stdout or stderr)
    await run_cmd.finish(f'{cmd}\n运行结果：\n{result}')


@DRIVER.on_bot_connect
async def _():
    if (Path() / 'rebooting.json').exists():
        info = load_json(Path() / 'rebooting.json')
        if info['session_type'] == 'group':
            await get_bot().send_group_msg(group_id=info['session_id'], message=f'{NICKNAME}已重启完成，当前版本为{__version__}')
        else:
            await get_bot().send_private_msg(user_id=info['session_id'], message=f'{NICKNAME}已重启完成，当前版本为{__version__}')
        (Path() / 'rebooting.json').unlink()
