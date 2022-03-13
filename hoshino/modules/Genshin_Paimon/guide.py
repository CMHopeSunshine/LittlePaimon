import hoshino,os
from hoshino import R,MessageSegment,aiorequests,logger,Service
from hoshino.typing import CQEvent, Message
from hoshino.util import pic2b64
from .character_alias import get_id_by_alias

sv=hoshino.Service('原神角色wiki')
res_dir = os.path.join(os.path.dirname(__file__), 'res')

role_list=['云堇','申鹤','荒泷一斗','五郎','优菈','阿贝多','托马','胡桃','达达利亚','雷电将军','珊瑚宫心海','埃洛伊','宵宫','神里绫华','枫原万叶','温迪','刻晴','莫娜','可莉','琴','迪卢克','七七','魈','钟离','甘雨','旅行者','早柚','九条裟罗','凝光','菲谢尔','班尼特','丽莎','行秋','迪奥娜','安柏','重云','雷泽','芭芭拉','罗莎莉亚','香菱','凯亚','北斗','诺艾尔','砂糖','辛焱','烟绯','八重神子','神里绫人']

@sv.on_prefix('角色攻略')
@sv.on_suffix('角色攻略')
async def genshinguide(bot,ev):
    if ev.message_type == 'guild' and (ev.channel_id != '2219931' and ev.channel_id != '1916789'):
        return
    name = ev.message.extract_plain_text().strip()
    chara_name = get_id_by_alias(name)
    if not chara_name:
        await bot.send(ev,f'没有找到{name}的攻略',at_sender=True)
    elif chara_name[1][0] == '八重神子':
        path = os.path.join(res_dir, 'role_guide','八重神子.png')
        cq_img = f'[CQ:image,file=file:///{path}]'
        await bot.send(ev,cq_img,at_sender=True)
    else:
        img = f'[CQ:image,file=https://adachi-bot.oss-cn-beijing.aliyuncs.com/Version2/guide/{chara_name[1][0]}.png]'
        await bot.send(ev,img)

@sv.on_prefix('角色材料')
@sv.on_suffix('角色材料')
async def genshinmaterial(bot,ev):
    if ev.message_type == 'guild' and (ev.channel_id != '2219931' and ev.channel_id != '1916789'):
        return
    name = ev.message.extract_plain_text().strip()
    name = get_id_by_alias(name)
    if not name:
        await bot.send(ev,'没有找到该角色的材料图',at_sender=True)
    else:
        path = os.path.join(res_dir, 'role_material',f'{name[1][0]}材料.png')
        cq_img = f'[CQ:image,file=file:///{path}]'
        await bot.send(ev,cq_img,at_sender=True)