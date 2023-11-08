from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.adapters.onebot.utils import rich_unescape

from LittlePaimon.utils.message import MessageBuild
from .data_handle import set_uid, get_uid, update_info, get_info
from .draw import draw_character


__plugin_meta__ = PluginMetadata(
    name='星穹铁道面板查询',
    description='星穹铁道面板查询',
    usage='...',
    extra={
        'author': '惜月',
        'version': '3.0',
        'priority': 6,
    },
)

panel_cmd = on_command("星铁面板", aliases={"崩铁面板", "星穹铁道面板", "sr"}, priority=1, block=True, state={
    'pm_name':        '星穹铁道面板',
    'pm_description': '查询星穹铁道面板',
    'pm_usage':       '星铁面板',
    'pm_priority':    1
})


update_cmd = on_command("更新星铁面板", aliases={"更新崩铁面板", "更新星穹铁道面板", "sr update"}, priority=1, block=True, state={
    'pm_name':        '星穹铁道面板更新',
    'pm_description': '绑定星穹面板更新',
    'pm_usage':       '更新星铁面板 uid',
    'pm_priority':    2
})

bind_cmd = on_command("星铁绑定", aliases={"崩铁绑定", "星穹铁道绑定", "srb", "绑定星铁", "绑定崩铁", "绑定星穹铁道"}, priority=1, block=True, state={
    'pm_name':        '星穹铁道绑定',
    'pm_description': '绑定星穹铁道uid',
    'pm_usage':       '星铁绑定uid',
    'pm_priority':    3
})

@panel_cmd.handle()
async def panel_cmd_handler(event: MessageEvent, args: Message = CommandArg()):
    if (at_msg := args['at']) and 'qq' in at_msg[0].data:
        user_id = str(at_msg[0].data['qq'])
    else:
        user_id = str(event.user_id)
    name = rich_unescape(args.extract_plain_text().strip())
    if not name:
        await panel_cmd.finish("请给出要查询的角色名全称~")
    uid = get_uid(user_id)
    if not uid:
        await panel_cmd.finish("请先使用命令[星铁绑定 uid]来绑定星穹铁道UID")
    data = get_info(uid, name)
    if not data:
        await panel_cmd.finish("还没有该角色的面板数据哦，请将该角色放在游戏支援角色或星海同行中，使用命令[更新星铁面板]来更新")
    try:
        image = await draw_character(data, uid)
    except Exception as e:
        await panel_cmd.finish(f"绘制星穹铁道面板时出现了错误：{e}")
    await panel_cmd.finish(MessageBuild.Image(image, quality=80, mode='RGB'), at_sender=True)



@bind_cmd.handle()
async def bind_cmd_handler(event: MessageEvent, args: Message = CommandArg()):
    uid = args.extract_plain_text().strip()
    if not uid:
        await bind_cmd.finish("请给出要绑定的uid")
    if not (uid.isdigit() and len(uid) == 9):
        await bind_cmd.finish("UID格式不对哦~")
    set_uid(str(event.user_id), uid)
    await bind_cmd.finish(f"成功绑定星铁UID{uid}", at_sender=True)


@update_cmd.handle()
async def update_cmd_handler(event: MessageEvent, args: Message = CommandArg()):
    uid = args.extract_plain_text().strip()
    if not uid:
        uid = get_uid(str(event.user_id))
    elif not (uid.isdigit() and len(uid) == 9):
        await update_cmd.finish("UID格式不对哦~")
    if not uid:
        await update_cmd.finish("请先绑定UID或在本命令后面加上UID")
    set_uid(str(event.user_id), uid)
    msg = await update_info(uid)
    await update_cmd.finish(msg, at_sender=True)


