import hoshino,os
from PIL import Image
from hoshino import R,MessageSegment,aiorequests,logger,Service
from hoshino.typing import CQEvent, Message
from ..character_alias import get_id_by_alias
from .blue import get_blue_pic
from ..util import pil2b64

sv=hoshino.Service('原神角色wiki')
res_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'res')

@sv.on_prefix('角色攻略')
@sv.on_suffix('角色攻略')
async def genshinguide(bot,ev):
    name = ev.message.extract_plain_text().strip()
    chara_name = get_id_by_alias(name)
    if not chara_name:
        await bot.send(ev,f'没有找到{name}的攻略',at_sender=True)
    elif chara_name[1][0] == '八重神子':
        path = os.path.join(res_path, 'role_guide','八重神子.png')
        cq_img = f'[CQ:image,file=file:///{path}]'
        await bot.send(ev,cq_img,at_sender=True)
    else:
        img = f'[CQ:image,file=https://adachi-bot.oss-cn-beijing.aliyuncs.com/Version2/guide/{chara_name[1][0]}.png]'
        await bot.send(ev,img)

@sv.on_prefix('角色材料')
@sv.on_suffix('角色材料')
async def genshinmaterial(bot,ev):
    name = ev.message.extract_plain_text().strip()
    name = get_id_by_alias(name)
    if not name:
        await bot.send(ev,f'没有找到{name}的材料',at_sender=True)
    else:
        path = os.path.join(res_path, 'role_material',f'{name[1][0]}材料.png')
        cq_img = f'[CQ:image,file=file:///{path}]'
        await bot.send(ev,cq_img,at_sender=True)

@sv.on_prefix('参考面板')
@sv.on_suffix('参考面板')
async def genshinAttribute(bot,ev):
    name = ev.message.extract_plain_text().strip()
    if name != '风主' or name != '岩主' or name != '雷主':
        name = get_id_by_alias(name)
        if not name:
            await bot.send(ev,f'没有找到{name}的参考面板',at_sender=True)
            return
        name = name[1][0]
    pic_data = get_blue_pic(name)
    pic = Image.open(os.path.join(res_path, 'blue', f'{pic_data[0]}.jpg'))
    pic = pic.crop((0, pic_data[1][0], 1080, pic_data[1][1]))
    pic = pil2b64(pic, 85)
    pic = MessageSegment.image(pic)
    await bot.send(ev,pic,at_sender=True)
        

@sv.on_prefix('收益曲线')
@sv.on_suffix('收益曲线')
async def genshinAttribute2(bot,ev):
    name = ev.message.extract_plain_text().strip()
    if name != '风主' or name != '岩主' or name != '雷主':
        name = get_id_by_alias(name)
        if not name:
            await bot.send(ev,f'没有找到{name}的参考面板',at_sender=True)
            return
        name = name[1][0]
    pic = Image.open(os.path.join(res_path, 'blue', f'{name}.png'))
    pic = pil2b64(pic, 85)
    pic = MessageSegment.image(pic)
    await bot.send(ev,pic,at_sender=True)