import os
import asyncio
import random
import sys
from pathlib import Path

from nonebot import on_command, get_bot
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me
from nonebot.params import CommandArg, ArgPlainText, Arg
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent, ActionFailed
from nonebot.adapters.onebot.v11.helpers import convert_chinese_to_bool
from LittlePaimon.utils import NICKNAME, DRIVER, __version__
from LittlePaimon.utils.files import save_json, load_json
from LittlePaimon.utils.update import check_update, update

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
broadcast = on_command('广播', permission=SUPERUSER, rule=to_me(), priority=1, block=True, state={
    'pm_name':        'broadcast',
    'pm_description': '向指定或所有群发送消息，需超级用户权限',
    'pm_usage':       '@bot 广播<内容>',
    'pm_priority':    5
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
        save_json({'session_type': event.message_type,
                   'session_id':   event.group_id if isinstance(event, GroupMessageEvent) else event.user_id},
                  Path() / 'rebooting.json')
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
        result = (stdout or stderr).decode('gb2312')
    except Exception:
        result = str(stdout or stderr)
    await run_cmd.finish(f'{cmd}\n运行结果：\n{result}')


@broadcast.handle()
async def _(event: MessageEvent, state: T_State, msg: Message = CommandArg()):
    if msg:
        state['msg'] = msg
    else:
        await broadcast.finish('请给出要广播的消息', at_sender=True)


@broadcast.got('groups', prompt='要广播到哪些群呢？多个群以空格隔开，或发送"全部"向所有群广播')
async def _(event: MessageEvent, bot: Bot, msg: Message = Arg('msg'), groups: str = ArgPlainText('groups')):
    group_list = await bot.get_group_list()
    group_list = [g['group_id'] for g in group_list]
    if groups in {'全部', '所有', 'all'}:
        send_groups = group_list
    else:
        groups = groups.split(' ')
        send_groups = [int(group) for group in groups if group.isdigit() and int(group) in group_list]
    if not send_groups:
        await broadcast.finish('要广播的群未加入或参数不对', at_sender=True)
    else:
        await broadcast.send(f'开始向{len(send_groups)}个群发送广播，每群间隔5~10秒', at_sender=True)
        for group in send_groups:
            try:
                await bot.send_group_msg(group_id=group, message=msg)
                await asyncio.sleep(random.randint(5, 10))
            except ActionFailed:
                await broadcast.send(f'群{group}发送消息失败')
        await broadcast.finish('消息广播发送完成', at_sender=True)


@DRIVER.on_bot_connect
async def _():
    if (Path() / 'rebooting.json').exists():
        info = load_json(Path() / 'rebooting.json')
        if info['session_type'] == 'group':
            await get_bot().send_group_msg(group_id=info['session_id'], message=f'{NICKNAME}已重启完成，当前版本为{__version__}')
        else:
            await get_bot().send_private_msg(user_id=info['session_id'], message=f'{NICKNAME}已重启完成，当前版本为{__version__}')
        (Path() / 'rebooting.json').unlink()
