import re

from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, Message
from nonebot.params import CommandArg, T_State, Arg
from nonebot.plugin import PluginMetadata

from .data_source import get_address, get_goods, save_exchange_info, get_exchange_info, delete_exchange_info

__plugin_meta__ = PluginMetadata(
    name="米游币商品自动兑换插件",
    description="录入米游币兑换计划，Bot会在对应时间自动帮你抢兑商品",
    usage=(
        "myb 跟随Bot的指引录入兑换计划\n"
        "myb_info 查看当前的兑换计划\n"
        "myb_delete 删除你的所有兑换计划\n"
    ),
    extra={
        "author":  "惜月 <277073121@qq.com>",
        "version": "1.0.0",
    },
)

myb_exchange = on_command('myb', aliases={'米游币兑换', '米游币商品兑换', '米游社商品兑换'}, priority=6, state={
    'pm_name': '米游币兑换',
    'pm_usage': 'myb',
    'pm_show': True,
    'pm_priority': 15,
    'pm_description': '录入米游币商品自动兑换计划',
})
myb_info = on_command('myb_info', aliases={'米游币兑换信息', '米游币兑换计划'}, priority=6, state={
    'pm_name': '米游币兑换信息',
    'pm_usage': 'myb_info',
    'pm_show': True,
    'pm_priority': 16,
    'pm_description': '查看你的米游币兑换计划',
})
myb_delete = on_command('myb_delete', aliases={'米游币兑换删除', '米游币兑换取消'}, priority=6, state={
    'pm_name': '米游币兑换删除',
    'pm_usage': 'myb_delete',
    'pm_show': True,
    'pm_priority': 17,
    'pm_description': '取消你的米游币兑换计划',
})


@myb_exchange.handle()
async def _(event: PrivateMessageEvent, state: T_State, msg: Message = CommandArg()):
    if msg:
        msg = msg.extract_plain_text().strip()
        if '虚拟' in msg:
            state['商品类型'] = '虚拟'
        elif '实体' in msg:
            state['商品类型'] = '实体'
            state['uid'] = None


@myb_exchange.got('商品类型', prompt='请给出要抢的商品类型(虚拟|实体)，例如原石属于虚拟')
async def _(event: PrivateMessageEvent, state: T_State, type: Message = Arg('商品类型')):
    type = type.extract_plain_text().strip()
    if '虚拟' in type:
        state['商品类型'] = '虚拟'
        print(state)
    elif '实体' in type:
        state['商品类型'] = '实体'
        state['uid'] = None
    else:
        await myb_exchange.reject('请给出要抢的商品类型(虚拟|实体)，例如原石属于虚拟')


@myb_exchange.got('uid', prompt='请把虚拟商品要兑换到的游戏uid告诉我')
async def _(event: PrivateMessageEvent, state: T_State, uid: Message = Arg('uid')):
    uid = uid.extract_plain_text().strip()
    if find_uid := re.search(r'(?P<uid>[125]\d{8})', uid):
        state['uid'] = find_uid['uid']
    else:
        await myb_exchange.reject('这不是有效的uid')


@myb_exchange.got('cookie', prompt='请把米游币cookie给我，cookie获取方式详见：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1')
async def _(event: PrivateMessageEvent, state: T_State, cookie: Message = Arg('cookie')):
    cookie = cookie.extract_plain_text().strip()
    address = await get_address(cookie)
    if address is None:
        await myb_exchange.reject('这个cookie无效，请检查是否以按照正常方法获取')
    elif len(address) == 0:
        await myb_exchange.finish('你的账号还没有填写收货地址哦，请先去填写收货地址重新再来')
    else:
        state['cookie'] = cookie
        if len(address) == 1:
            state['address_id'] = address[0]
        else:
            state['address_list'] = address
        if state['商品类型'] == '虚拟' and 'login_ticket' not in cookie and 'stoken' not in cookie:
            await myb_exchange.reject('你的cookie中没有login_ticket字段哦，请尝试退出后重新登录再获取cookie')


@myb_exchange.got('address_id', prompt='回复任意文字继续，接下来回复选择你的收货地址的ID')
async def _(event: PrivateMessageEvent, state: T_State, address_id: Message = Arg('address_id')):
    address_id = address_id.extract_plain_text().strip()
    flag = False
    for add in state['address_list']:
        if address_id == add['id']:
            state['address_id'] = add
            flag = True
            break
    if not flag:
        address_list = ''.join(f'ID：{add["id"]}，{add["地址"]}\n' for add in state['address_list'])
        await myb_exchange.reject(f'请选择收货地址ID：\n{address_list}')


@myb_exchange.got('game', prompt='请给出要抢的商品所属游戏名称，有崩坏3|原神|崩坏学园2|未定事件簿|米游社')
async def _(event: PrivateMessageEvent, state: T_State, game: Message = Arg('game')):
    game = game.extract_plain_text().strip()
    if game in ['崩坏3', 'bh3', '崩崩崩', '三崩子']:
        state['goods_list'] = await get_goods('崩坏3')
    elif game in ['原神', 'ys']:
        state['goods_list'] = await get_goods('原神')
    elif game in ['崩坏学园2', 'bh2', '二崩子', '崩坏学院2', '崩崩']:
        state['goods_list'] = await get_goods('崩坏学园2')
    elif game in ['未定事件簿', 'wdsjb', '未定']:
        state['goods_list'] = await get_goods('未定事件簿')
    elif game in ['米游社', 'mys']:
        state['goods_list'] = await get_goods('米游社')
    else:
        await myb_exchange.reject('请给出要抢的商品所属游戏名称，有崩坏3|原神|崩坏学园2|未定事件簿|米游社')


@myb_exchange.got('goods_search', prompt='请给出要兑换的商品名，或者其含有的关键词')
async def _(event: PrivateMessageEvent, state: T_State, goods_search: Message = Arg('goods_search')):
    goods_search = goods_search.extract_plain_text().strip()
    match_goods = [good for good in state['goods_list'] if goods_search in good['name']]
    if len(match_goods) == 1:
        state['goods'] = match_goods[0]
        save_exchange_info(event.user_id, state)
        await myb_exchange.finish('兑换计划录入成功，到时候会帮你兑换并告诉你结果，发送 myb_info 可以再次确认兑换信息，发送 myb_delete 可以取消兑换计划')

    elif len(match_goods) > 1:
        state['goods_search_result'] = match_goods
    else:
        await myb_exchange.reject('没有相关可兑换的商品，请重新输入')


@myb_exchange.got('goods', prompt='回复任意文字继续，接下来回复选择你想要兑换的商品的ID')
async def _(event: PrivateMessageEvent, state: T_State, msg: Message = Arg('goods')):
    msg = msg.extract_plain_text().strip()
    for good in state['goods_search_result']:
        if msg == good['id']:
            state['goods'] = good
            save_exchange_info(event.user_id, state)
            await myb_exchange.finish('兑换计划录入成功，到时候会帮你兑换并告诉你结果，发送 myb_info 可以再次确认兑换信息，发送 myb_delete 可以取消兑换计划')

    good_str = ''.join(f'ID：{good["id"]}, 商品名：{good["name"]}\n' for good in state['goods_search_result'])
    await myb_exchange.reject('请选择商品ID：\n' + good_str)


@myb_info.handle()
async def _(event: PrivateMessageEvent):
    info = get_exchange_info(str(event.user_id))
    await myb_info.finish(info)


@myb_delete.handle()
async def _(event: PrivateMessageEvent):
    delete_exchange_info(str(event.user_id))
    await myb_delete.finish('米游币兑换计划已全部取消')
