import os
import subprocess
import sys

from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import MessageEvent
from LittlePaimon import NICKNAME

update_cmd = on_command('更新', permission=SUPERUSER, rule=to_me(), priority=1)
reboot_cmd = on_command('重启', permission=SUPERUSER, rule=to_me(), priority=1)

__plugin_meta__ = PluginMetadata(
    name='机器人管理',
    description='机器人管理',
    usage='...',
    extra={
        'priority': 16,
        'show': False
    }
)


@update_cmd.handle()
async def _(event: MessageEvent):
    await update_cmd.send(f'{NICKNAME}开始执行git pull更新', at_sender=True)
    p = subprocess.run(['git', 'pull'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    await update_cmd.finish('更新结果：' + (p.stdout if p.returncode == 0 else p.stderr).decode('utf-8').strip())


@reboot_cmd.handle()
async def _(event: MessageEvent):
    await reboot_cmd.send(f'{NICKNAME}开始执行重启，请等待{NICKNAME}的归来', at_sender=True)
    if sys.argv[0].endswith('nb'):
        sys.argv[0] = 'bot.py'
    os.execv(sys.executable, ['python'] + sys.argv)
