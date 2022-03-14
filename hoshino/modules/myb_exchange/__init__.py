import hoshino,json,os,traceback,asyncio
from hoshino import R,MessageSegment,aiorequests,logger
from hoshino.typing import CQEvent, Message
from PIL import Image
from io import BytesIO
import datetime
from nonebot import scheduler

from . import get_goods_list,get_address_id

sv=hoshino.Service('米游币抢兑')

myb_info = {}
goods_list = {}

def load_data():
    path = os.path.join(os.path.dirname(__file__), 'myb_info.json')
    if not os.path.exists(path):
        with open(path,'w',encoding='UTF-8') as f:
            json.dump(myb_info,f,ensure_ascii=False)
    else:
        try:
            with open(path, encoding='utf8') as f:
                data = json.load(f)
                for k, v in data.items():
                    myb_info[k] = v
        except:
            traceback.print_exc()

def save_data():
    path = os.path.join(os.path.dirname(__file__), 'myb_info.json')
    try:
        with open(path, 'w', encoding='utf8') as f:
            json.dump(myb_info, f, ensure_ascii=False, indent=2)
    except:
        traceback.print_exc()

add_list_all = {}

@sv.on_fullmatch('米游币兑换')
async def mys(bot,ev):
    qid = str(ev.user_id)
    if ev.message_type != 'private':
        await bot.send(ev,'想要派蒙帮抢米游币商品吗？请私聊派蒙 米游币兑换 来使用哦！',at_sender=True)
        return
    res = "Hi旅行者！想要派蒙帮你抢米游社商品吗，请听派蒙的一步步指引哦：\n1.给派蒙发送你的cookie\n2.派蒙会列出你的收货地址，选择要收货的地址\n3.给派蒙发送你要兑换的商品4.告诉派蒙兑换开始的时间\n简单的步骤就是这样啦，接下来派蒙会一步步提示你使用指令\n\ncookie的获取方法如下：\n1.使用浏览器(安卓端用via浏览器，PC端随意)登录网页版米游社\n2.在地址栏删掉原本的链接，粘贴以下代码:\njavascript:(function(){let domain=document.domain;let cookie=document.cookie;prompt('Cookies: '+domain, cookie)})();\n(pc浏览器可能会将前面的javascript:给去掉，手动打上即可)\n3.点击回车前往，弹窗出现的一串字符就是cookie。"
    #res = '诶嘿派蒙帮抢'
    await bot.send(ev,res)
    await asyncio.sleep(2)
    await bot.send(ev,'---1.请发送指令[mybcookie (cookie)],()内为你要填入的信息---')

@sv.on_prefix('mybcookie')
async def choose_cookie(bot,ev):
    qid = str(ev.user_id)
    cookie = ev.message.extract_plain_text()
    if ev.message_type != 'private':
        await bot.send(ev,'这个功能只能私聊使用哦，请撤回并私聊派蒙')
        return
    add_list = await get_address_id.get_address(cookie)
    if add_list is None:
        await bot.send(ev,'该cookie不能正确获取收获地址，请重新获取')
    elif not add_list:
        await bot.send(ev,'该cookie账号下没有收货地址，请先去添加')
    else:
        myb_info[qid] = {}
        myb_info[qid]['cookie'] = cookie
        save_data()
        add_list_all[qid] = add_list
        msg = ''
        for add in add_list.items():
            msg += f'id:{add[0]} {add[1]}\n'
        await bot.send(ev,'---2.请发送指令[myb地址 (地址id)]来选择收货地址，如 myb地址10---')
        await asyncio.sleep(1)
        await bot.send(ev,msg)

@sv.on_prefix('myb地址')
async def choose_address(bot,ev):
    if ev.message_type != 'private':
        await bot.send(ev,'这个功能只能私聊使用哦，请撤回并私聊派蒙',at_sender=True)
        return
    qid = str(ev.user_id)
    add = ev.message.extract_plain_text()
    if qid not in add_list_all:
        await bot.send(ev,'你还未输入cookie')
    elif add not in add_list_all[qid]:
        await bot.send(ev,'你的收货地址列表没有该地址id')
    else:
        if qid not in myb_info:
            myb_info[qid] = {}
        myb_info[qid]['address_id'] = add
        save_data()
        await bot.send(ev,'---3.请发送指令[myb商品 (商品关键词)]，派蒙会列出含有关键词的商品名和id---')

@sv.on_prefix('myb商品')
async def choose_goods(bot,ev):
    if ev.message_type != 'private':
        await bot.send(ev,'这个功能只能私聊使用哦，请撤回并私聊派蒙',at_sender=True)
        return
    qid = str(ev.user_id)
    if qid not in myb_info:
        myb_info[qid] = {}
    keyword = ev.message.extract_plain_text().strip()
    goods_list_match = {}
    for good in goods_list.items():
        if keyword in good[0]:
            goods_list_match[good[0]] = good[1]
    msg = '找到的商品有：\n'
    for good in goods_list_match.items():
        msg += f'-名：{good[0]} id：{good[1]}-\n'
    await bot.send(ev,msg)
    await asyncio.sleep(1)
    await bot.send(ev,'---4.请发送指令[myb商品选择 (商品的id)]来添加要兑换的商品，多个商品id间用空格隔开，---')

@sv.on_prefix('myb商品选择')
async def choose_goods_id(bot,ev):
    if ev.message_type != 'private':
        await bot.send(ev,'这个功能只能私聊使用哦，请撤回并私聊派蒙',at_sender=True)
        return
    qid = str(ev.user_id)
    if qid not in myb_info:
        myb_info[qid] = {}
    if 'goods_id' not in myb_info[qid]:
        myb_info[qid]['goods_id'] = []
    goods_id = ev.message.extract_plain_text().strip()
    goods_id = goods_id.split(' ')
    for good in goods_id:
        if good not in goods_list.values():
            await bot.send(ev,f'{good}不在可兑换的商品中')
        else:
            myb_info[qid]['goods_id'].append(good)
    await asyncio.sleep(1)
    await bot.send(ev,'---5.请发送指令[myb时间 (时间)]，格式：米游币时间 2022年02月10日12:00:00---')

@sv.on_prefix('myb时间')
async def choose_date(bot,ev):
    if ev.message_type != 'private':
        await bot.send(ev,'这个功能只能私聊使用哦，请撤回并私聊派蒙',at_sender=True)
        return
    qid = str(ev.user_id)
    date = ev.message.extract_plain_text().strip()
    if qid not in myb_info:
        myb_info[qid] = {}
    try:
        datet = datetime.datetime.strptime(date,'%Y年%m月%d日%H:%M:%S')
    except Exception as e:
        await bot.send(ev,f'时间格式错误，正确格式：myb时间 2022年02月10日12:00:00')
        return
    myb_info[qid]['date'] = date
    save_data()
    try:
        cookie, address, goods = myb_info[qid]['cookie'],myb_info[qid]['address_id'],myb_info[qid]['goods_id']
    except Exception as e:
        del myb_info[info[0]]
        logger.error(f'{info[0]}的信息不全，已删除')
        save_data()
        return
    scheduler.add_job(
                    exchange,
                    'date',
                    args=(qid,cookie,address,goods),
                    run_date = datet
                )
    await asyncio.sleep(1)
    await bot.send(ev,'---已成功调好闹钟准备兑换啦！届时会将兑换结果私聊给你---')

@sv.on_fullmatch('myb取消')
async def deletemyb(bot,ev):
    qid = str(ev.user_id)
    if qid in myb_info:
        del myb_info[qid]
        save_data()
        await bot.send(ev,'派蒙已经取消你的商品帮抢')
    else:
        await bot.send(ev,'你没有设置过派蒙帮抢哦')

async def exchange(qid,cookie,address,goods):
    url = "https://api-takumi.mihoyo.com/mall/v1/web/goods/exchange"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "Connection": "keep-alive",
        "Content-Length": "88",
        "Content-Type": "application/json;charset=utf-8",
        "Cookie": cookie,
        "Host": "api-takumi.mihoyo.com",
        "Origin": "https://webstatic.mihoyo.com",
        "Referer": "https://webstatic.mihoyo.com/",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.14.1","x-rpc-app_version": "2.14.1",
        "x-rpc-channel": "appstore",
        "x-rpc-client_type": "1",
        "x-rpc-device_id": "35543DDE-7C18-4584-BF4B-51217D3C8670",
        "x-rpc-device_model": "iPhone10,2",
        "x-rpc-device_name": "%E4%B8%A4%E6%B1%9F%E6%80%BB%E7%9D%A3",
        "x-rpc-sys_version": "15.1"
    }
    for good in goods:
        data = {
            "app_id": 1,
            "point_sn": "myb",
            "goods_id": good,
            "exchange_num": 1,
            "address_id": address
        }
        try:
            bot = hoshino.get_bot()
            res = await aiorequests.post(url=url,headers=headers,json=data)
            mes = await res.json()
            good_name = [k for k,v in goods_list.items() if v==good][0]
            logger.info(f'用户{qid}的商品{good_name}兑换操作成功，结果：{mes}')
            mes = f'你的{good}兑换结果：\n{mes["message"]}'
            try:
                await bot.send_private_msg(user_id=qid,message=mes)
            except Exception as e:
                logger.error(f'商品兑换：向{qid}发送消息失败：{e}')
        except Exception as e:
            logger.error(f'商品兑换：用户{qid}的商品{good}兑换时网络出错：{e}')
    del myb_info[qid]
    save_data()

async def makeaction():
    if myb_info:
        for info in myb_info.items():
            try:
                date = datetime.datetime.strptime(info[1]['date'],'%Y年%m月%d日%H:%M:%S')
                qid, cookie, address, goods = info[0], info[1]['cookie'], info[1]['address_id'], info[1]['goods_id']
            except Exception as e:
                del myb_info[info[0]]
                save_data()
                logger.error(f'{info[0]}的信息不全，已删除')
                break
            scheduler.add_job(
                    exchange,
                    'date',
                    args=(qid,cookie,address,goods),
                    run_date = date
                )
@sv.scheduled_job('date',run_date=datetime.datetime.now())
async def startup():
    load_data()
    await makeaction()
    logger.info('加载米游币兑换信息...')
goods_list = get_goods_list.get_goods_list()




