from hoshino.typing import CQEvent, Message,CQHttpError
import hoshino
from nonebot import scheduler
from hoshino import Service, R, aiorequests,util
import requests, random, os, json,datetime,re
from os import path

sv=hoshino.Service('派蒙聊天')
res_dir = path.join(path.dirname(__file__), 'res')

ban_word = ['禁言','ys','ssbq','十连']
word_cooldown = {'确实':{},'坏了':{},'诶嘿':{},'进不去':{},'派蒙是谁':{},'大佬':{},'好色':{},'无语':{},'祝福':{},'相信':{},'憨批':{},'可爱':{},'绿茶':{},'不是吧':{},'好耶':{},'好听':{},'耽误时间':{},'不可以':{},'好意思':{},'不要啊':{},'羡慕':{},'过分':{},'不明白':{},'哪里不对':{}}
word_cooldowntime = {'确实':60,'坏了':60,'诶嘿':180,'进不去':240,'派蒙是谁':480,'大佬':300,'好色':300,'无语':300,'祝福':480,'相信':600,'憨批':480,'可爱':480,'绿茶':600,'不是吧':300,'好耶':180,'好听':600,'耽误时间':600,'不可以':180,'好意思':300,'不要啊':180,'羡慕':180,'过分':300,'不明白':300,'哪里不对':300}
word_pro = {'确实':0.6,'坏了':0.6,'诶嘿':0.5,'进不去':0.5,'派蒙是谁':1,'大佬':0.6,'好色':0.5,'无语':0.6,'祝福':1,'相信':0.5,'憨批':0.5,'可爱':0.5,'绿茶':1,'不是吧':0.5,'好耶':0.75,'好听':0.4,'耽误时间':0.6,'不可以':0.6,'好意思':0.5,'不要啊':0.5,'羡慕':0.6,'过分':0.5,'不明白':0.5,'哪里不对':0.5}

PROB_A = 1.6
group_stat = {}
check_rep = {}
@sv.on_message()
async def random_repeater(bot, ev: CQEvent):
    if ev.message_type == 'group':
        gid = str(ev.group_id)
    elif ev.message_type == 'guild':
        gid = str(ev.channel_id)
    else:
        return
    msg = str(ev.message)

    if gid not in group_stat:
        group_stat[gid] = (msg, False, 0)
        return
    if gid not in check_rep:
        check_rep[gid] = False

    last_msg, is_repeated, p = group_stat[gid]
    if last_msg == msg and msg not in ban_word:     # 群友正在复读
        check_rep[gid] = True
        if not is_repeated:     # 机器人尚未复读过，开始测试复读
            if random.random() < p:    # 概率测试通过，复读并设flag
                try:
                    group_stat[gid] = (msg, True, 0)
                    await bot.send(ev, util.filt_message(ev.message))
                except CQHttpError as e:
                    hoshino.logger.error(f'复读失败: {type(e)}')
                    hoshino.logger.exception(e)
            else:                      # 概率测试失败，蓄力
                p = 1 - (1 - p) / PROB_A
                group_stat[gid] = (msg, False, p)
    else:   # 不是复读，重置
        group_stat[gid] = (msg, False, 0)
        check_rep[gid] = False


@sv.on_message()
async def paimonchat(bot, ev:CQEvent):
    if ev.message_type == 'group':
        gid = str(ev.group_id)
    elif ev.message_type == 'guild':
        return
    else:
        gid = str(ev.user_id)
    msg = str(ev.message)
    if gid not in check_rep:
        check_rep[gid] = False
    if check_rep[gid]:
        return
    if re.match(r'.*派蒙.*坏.*',msg):
        word = '坏了'
        reply = random.choice(['你才坏！','瞎说啥呢？','派蒙怎么可能会坏！']) + '[CQ:face,id=146]'
    elif re.match(r'.*(雀食|确实).*',msg):
        word = '确实'
        reply = '雀食' if '雀食' in msg else '确实'
    elif re.match(r'.*(诶嘿|哎嘿|欸嘿).*',msg):
        word = '诶嘿'
        path = res_dir + random.choice(['/诶嘿.mp3','/诶嘿cn.mp3'])
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'.*进不?(来|去).*',msg):
        word = '进不去'
        path = res_dir + '/进不去.mp3'
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'.*(派蒙.*是(什么|谁))|((什么|谁)是?.*派蒙).*',msg):
        word = '派蒙是谁'
        path = res_dir + random.choice(['/嘿嘿你猜.mp3','/中二派蒙.mp3','/伙伴.mp3'])
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'.*((大|巨)?佬)|带带|帮帮|邦邦.*',msg):
        word = '大佬'
        path = res_dir + '/大佬nb.mp3'
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'.*好色|变态(哦|噢)?',msg):
        word = '好色'
        path = res_dir + random.choice(['/好色哦.mp3','/好变态.mp3'])
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'.*(\.{3,9})|(\。{3,9})|无语|无话可说.*',msg):
        word = '无语'
        path = res_dir + random.choice(['/无语.mp3','/冷淡反应.mp3'])
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'.*派蒙.*(祝福|吟唱|施法).*',msg):
        word = '祝福'
        path = res_dir + '/来个祝福.mp3'
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'.*信?不信|信我.*',msg):
        word = '相信'
        path = res_dir + random.choice(['/我信你个鬼.mp3','/真的假的.mp3'])
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'.*(憨批|傻(逼|B|b)).*',msg):
        word = '憨批'
        path = res_dir + '/憨批.mp3'
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'.*可爱|卡哇伊',msg):
        word = '可爱'
        path = res_dir + '/真是个小可爱.mp3'
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'.*派蒙.*(giegie|绿茶).*',msg):
        word = '绿茶'
        path = res_dir + '/绿茶派.mp3'
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'不(是|会)吧',msg):
        word = '不是吧'
        path = res_dir + '/不是吧阿sir.mp3'
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'好耶|太(好|棒)(了|啦)|好(\!|\！)',msg):
        word = '好耶'
        path = res_dir + random.choice(['/好耶.mp3','/太好啦.mp3'])
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'(好|真|非常)?好听(\!|\！)?',msg):
        word = '好听'
        path = res_dir + '/好听.mp3'
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'快{1,4}|gkd|搞?快点|赶紧的?|(.*耽误.*时间.*)',msg):
        word = '耽误时间'
        path = res_dir + '/耽误时间.mp3'
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'不(可以|行|能)(吧|的|噢)?',msg):
        word = '不可以'
        path = res_dir + '/不可以.mp3'
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'不(好|要)(吧|啊)?',msg):
        word = '不要啊'
        path = res_dir + '/不要啊.mp3'
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'.*好意思.*',msg):
        word = '好意思'
        path = res_dir + '/好意思.mp3'
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'.*羡慕.*',msg):
        word = '羡慕'
        path = res_dir + '/羡慕.mp3'
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'.*过分.*',msg):
        word = '过分'
        path = res_dir + '/好过分.mp3'
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'.*明白.*',msg):
        word = '不明白'
        path = res_dir + '/不明白.mp3'
        reply = f'[CQ:record,file=file:///{path}]'
    elif re.match(r'(是|对)(吧|吗)',msg):
        word = '哪里不对'
        path = res_dir + '/哪里不对.mp3'
        reply = f'[CQ:record,file=file:///{path}]'
    else:
        return
    if gid not in word_cooldown[word]:
        word_cooldown[word][gid] = True
    if ev.group == 914302664:
        p = word_pro[word]/2
    else:
        p = word_pro[word]
    if word_cooldown[word][gid] and random.random() < p:
        try:
            await bot.send(ev,reply)
            word_cooldown[word][gid] = False
            end_time = datetime.datetime.now() + datetime.timedelta(seconds=word_cooldowntime[word])#冷却时间
            scheduler.add_job(
                resetTime,
                'date',
                args=(word,gid,),
                run_date=end_time
            )
        except:
            hoshino.logger.error('派蒙聊天失败')

def resetTime(word,gid):
    word_cooldown[word][gid] = True
