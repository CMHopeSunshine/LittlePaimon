import os
import subprocess
import sys
from pathlib import Path

from nonebot import on_command, get_bot
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import MessageEvent
from LittlePaimon import NICKNAME, DRIVER, SUPERUSERS, __version__

update_cmd = on_command('更新', permission=SUPERUSER, rule=to_me(), priority=1)
reboot_cmd = on_command('重启', permission=SUPERUSER, rule=to_me(), priority=1)

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
    p = subprocess.run(['git', 'pull'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    results = (p.stdout if p.returncode == 0 else p.stderr).decode('utf-8').split('\n')
    result_msg = ''.join(result.split('|')[0].strip(' ') + '\n' for result in results)
    await update_cmd.finish(f'更新结果：{result_msg}')


@reboot_cmd.handle()
async def _(event: MessageEvent):
    await reboot_cmd.send(f'{NICKNAME}开始执行重启，请等待{NICKNAME}的归来', at_sender=True)
    (Path() / 'rebooting.json').open('w').close()
    if sys.argv[0].endswith('nb'):
        sys.argv[0] = 'bot.py'
    os.execv(sys.executable, ['python'] + sys.argv)


@DRIVER.on_bot_connect
async def _():
    if (Path() / 'rebooting.json').exists():
        await get_bot().send_private_msg(user_id=SUPERUSERS[0], message=f'{NICKNAME}已重启完成，当前版本为{__version__}')
        (Path() / 'rebooting.json').unlink()
