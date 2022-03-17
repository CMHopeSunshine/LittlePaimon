from hoshino import Service, priv, __version__
from hoshino.typing import CQEvent

sv = Service('_help_', manage_priv=priv.SUPERUSER, visible=False)

TOP_MANUAL = f'''
====================
= 惜月的小派蒙{__version__} =
发送[]内的关键词触发
有#的，#也要输入
带*号的仅绑定cookie后可用
====== 常用指令 ======
[ys uid]原神个人信息卡片
[ysa uid]原神角色背包一览
[ysc uid 角色名]原神角色详情
[sy uid]原神个人深渊信息
*[ssbq]原神实时便签
*[myzj 月份]原神每月札记
[抽n十连xx]原神模拟抽卡
[原神日历]原神活动日历
[原神运势]原神运势
[code 语言 (-i) (输入) 代码]运行代码
[#点歌 歌曲名]搜歌点歌(仅群)
[#表白 对象]发一篇表白小作文
[#续写 内容]ai续写文章
[#青年大学习]查看最新期答案
[xx疫情查询]顾名思义
[#亲亲/贴贴/拍拍/给爷爬/吃掉/扔掉/撕掉/精神支柱
/要我一直+@人/qq号/图片]:好玩的gif图表情包生成
=====================
'''.strip()
#[#喜加一资讯 n]查看n条喜加一资讯

def gen_service_manual(service: Service, gid: int):
    spit_line = '=' * max(0, 18 - len(service.name))
    manual = [f"|{'○' if service.check_enabled(gid) else '×'}| {service.name} {spit_line}"]
    if service.help:
        manual.append(service.help)
    return '\n'.join(manual)


def gen_bundle_manual(bundle_name, service_list, gid):
    manual = [bundle_name]
    service_list = sorted(service_list, key=lambda s: s.name)
    for s in service_list:
        if s.visible:
            manual.append(gen_service_manual(s, gid))
    return '\n'.join(manual)


@sv.on_prefix('#帮助')
async def send_help(bot, ev: CQEvent):
    gid = ev.group_id
    arg = ev.message.extract_plain_text().strip()
    bundles = Service.get_bundles()
    services = Service.get_loaded_services()
    if not arg:
        await bot.send(ev, TOP_MANUAL)
    elif arg in bundles:
        msg = gen_bundle_manual(arg, bundles[arg], gid)
        await bot.send(ev, msg)
    elif arg in services:
        s = services[arg]
        msg = gen_service_manual(s, gid)
        await bot.send(ev, msg)
    # else: ignore
