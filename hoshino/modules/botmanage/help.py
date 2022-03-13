from hoshino import Service, priv
from hoshino.typing import CQEvent

sv = Service('_help_', manage_priv=priv.SUPERUSER, visible=False)

TOP_MANUAL = '''
====================
= 惜月的小派蒙使用说明 =
发送[]内的关键词触发
(仅频道)说明只能在qq频道里触发
怎么进qq频道？让管理员发邀请
(仅群)说明频道里用不了
有#的，#也要输入
====== 常用指令 ======
[抽n十连xx]原神模拟抽卡(仅频道)
[刷副本xx]原神模拟刷圣遗物(仅频道)
[原神日历]查看原神活动日历
[原神运势]原神运势
[抽签/解签]原神抽签解签(仅频道)
[ys/ysa+uid]查看原神uid信息
[#原神猜语音]顾名思义猜语音(仅群)
[#点歌 歌曲名]搜歌点歌(仅群)
[#表白 对象]发一篇表白小作文
[#续写 内容]ai续写文章
[#rua@xxx]rua一下其他头像
[#青年大学习]查看最新期答案
[#code 语言 (-i) (输入) 代码]在线运行代码
[#搜天气 城市名]看城市天气
[#翻译中|英|日 内容]翻译
[xx疫情查询]顾名思义查城市疫情
[亲亲/贴贴/拍拍/给爷爬/吃掉/扔掉/撕掉/精神支柱/要我一直
+@人/qq号/图片]:好玩的gif图表情包生成
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
