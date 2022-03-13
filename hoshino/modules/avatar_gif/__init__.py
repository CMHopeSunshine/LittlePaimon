import re,random,datetime
from io import BytesIO
from os import path

from PIL import Image

from hoshino import Service, aiorequests
from hoshino.typing import HoshinoBot, CQEvent 
from .data_source import *
from ._res import Res as R

HELP_MSG = '''
头像相关表情包制作
摸摸|亲亲|吃掉|贴贴|拍拍|给爷爬|撕掉|精神支柱|扔掉|要我一直+@人/qq号/图片
戳一戳随机概率触发
'''
sv = Service('表情包', bundle='娱乐', help_=HELP_MSG)
data_dir = path.join(path.dirname(__file__), 'resources')

last_check = {}
cool_down = datetime.timedelta(seconds=20)

@sv.on_rex(r'^#(rua|摸摸|亲亲|吃掉|贴贴|拍拍|给爷爬|撕掉|精神支柱|扔掉|要我一直)(?P<name>.*?)$')
async def main(bot,ev):
    name = ev['match'].group('name')
    if ev.message_type == 'guild':
        rm = str(ev.message)
    else:
        rm = str(ev.raw_message)
    if name == '':
        match = re.search(r"\[CQ:at,qq=(.*)\]", rm)
        if not match:
            match2 = re.search(r"\[CQ:image,file=(.*),url=(.*)\]", str(ev.message))
            try:
                action = rm.split('[CQ')[0].strip(' ')
                resp = await aiorequests.get(match2.group(2))
                resp_cont = await resp.content
                head = Image.open(BytesIO(resp_cont))
            except:
                await bot.send(ev,'指令出错，请艾特或接图片',at_sender=True)
                return
        else:
            if ev.message_type == 'guild':
                await bot.send(ev,'频道无法用艾特噢',at_sender=True)
                return
            head = await get_avatar(match.group(1))
            action = str(ev.message).split('[CQ')[0].strip(' ')
    elif name.isdigit():
        head = await get_avatar(name)
        action = rm.split(name)[0].strip(' ')
    elif name == '#自己':
        head = await get_avatar(str(ev.user_id))
        action = rm.split(name)[0].strip(' ')
    else:
        await bot.send(ev,'指令出错，请艾特或接图片',at_sender=True)
        return
    if action == '#亲亲':
        my_head = await get_avatar(str(ev.user_id))
        res = await kiss(data_dir,head,my_head)
    elif action == '#吃掉':
        res = await eat(data_dir,head)
    elif action == '#摸摸' or action == '#rua':
        res = await rua(data_dir,head)
    elif action == '#贴贴':
        my_head = await get_avatar(str(ev.user_id))
        res = await rub(data_dir,head,my_head)
    elif action == '#拍拍':
        res = await pat(data_dir,head)
    elif action == '#给爷爬':
        res = await crawl(data_dir,head)
    elif action == '#撕掉':
        res = await rip(data_dir,head)
    elif action == '#精神支柱':
        res = await support(data_dir,head)
    elif action == '#扔掉':
        res = await throw(data_dir,head)
    elif action == '#要我一直':
        res = await always(data_dir,head)
    await bot.send(ev,R.image(res))
    
@sv.on_notice('notify.poke')
async def poke_back(session):
    uid = session.ctx['user_id']
    tid = session.ctx['target_id']
    gid = session.ctx['group_id']
    if str(gid) in last_check:
        intervals = datetime.datetime.now() - last_check[str(gid)]
        if intervals < cool_down:
            return
    if random.random() <= 0.4:
        if tid == session.ctx['self_id']:
            if random.random() <= 0.5:
                path = data_dir + random.choice(['/这个仇.mp3','/好生气.mp3','/好气哦.mp3','/好变态.mp3','/坏蛋.mp3','/不要啊.mp3','/好过分.mp3'])
                res = f'[CQ:record,file=file:///{path}]'
                await session.send(res)
        else:
            if random.random() <= 0.3:
                my_head = await get_avatar(str(uid))
                head = await get_avatar(str(tid))
                res = await random.choice(data_source.avatarFunList1)(data_dir,head,my_head)
                await session.send(R.image(res))
            else:
                head = await get_avatar(str(tid))
                res = await random.choice(data_source.avatarFunList2)(data_dir,head)
                await session.send(R.image(res))
        last_check[str(gid)] = datetime.datetime.now()


async def get_avatar(qq):
    url = f'http://q1.qlogo.cn/g?b=qq&nk={qq}&s=160'
    resp = await aiorequests.get(url)
    resp_cont = await resp.content
    avatar = Image.open(BytesIO(resp_cont)).convert("RGBA")
    return avatar
    

