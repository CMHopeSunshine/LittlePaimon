from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageEvent

from LittlePaimon.database.models import LastQuery, PublicCookie

test_q = on_command('最后查询')
pc = on_command('公共')
pca = on_command('添加')
pcs = on_command('设置')


@test_q.handle()
async def _(event: MessageEvent):
    await test_q.finish(await LastQuery.get_uid(str(event.user_id)))


@pc.handle()
async def _(event: MessageEvent):
    ck = await PublicCookie.get_cookie()
    ck = ck if ck else '没有ck'
    await pc.finish(ck)


@pca.handle()
async def _(event: MessageEvent, msg=CommandArg()):
    if msg:
        msg = msg.extract_plain_text().strip()
        await PublicCookie.add_cookie(msg)


@pcs.handle()
async def _(event: MessageEvent, msg=CommandArg()):
    if msg:
        msg = msg.extract_plain_text().strip()
        await PublicCookie.set_status(cookie=msg, status='OK')