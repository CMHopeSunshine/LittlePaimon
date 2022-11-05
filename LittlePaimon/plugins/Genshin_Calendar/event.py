import asyncio
import math
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from dateutil.relativedelta import relativedelta
from LittlePaimon.utils.requests import aiorequests

res = Path(__file__).parent / 'template'
# type 0 普通常驻任务深渊 1 新闻 2 蛋池 3 限时活动H5
event_data = {
    'cn': [],
}

event_updated = {
    'cn': '',
}

lock = {
    'cn': asyncio.Lock(),
}

ignored_key_words = [
    "修复",
    "内容专题页",
    "米游社",
    "调研",
    "防沉迷",
    "问卷",
    "公平运营",
    "有奖活动",
    "反馈功能"
]

ignored_ann_ids = [
    423,  # 《原神》玩家社区一览
    495,  # 有奖问卷调查开启！
    762,  # 《原神》公平运营声明
    1263,  # 米游社《原神》专属工具一览
    2388,  # 原神问卷调查
    2522,  # 《原神》防沉迷系统说明
    2911,  # 功能反馈
]

list_api = 'https://hk4e-api.mihoyo.com/common/hk4e_cn/announcement/api/getAnnList?game=hk4e&game_biz=hk4e_cn&lang=zh-cn&bundle_id=hk4e_cn&platform=pc&region=cn_gf01&level=55&uid=100000000'
detail_api = 'https://hk4e-api.mihoyo.com/common/hk4e_cn/announcement/api/getAnnContent?game=hk4e&game_biz=hk4e_cn&lang=zh-cn&bundle_id=hk4e_cn&platform=pc&region=cn_gf01&level=55&uid=100000000'


async def query_data(url) -> Optional[dict]:
    try:
        req = await aiorequests.get(url)
        return req.json()
    except Exception:
        return None


async def load_event_cn():
    result = await query_data(url=list_api)
    detail_result = await query_data(url=detail_api)
    if result and 'retcode' in result and result['retcode'] == 0 and detail_result and 'retcode' in detail_result and \
            detail_result['retcode'] == 0:
        event_data['cn'] = []
        event_detail = {detail['ann_id']: detail for detail in detail_result['data']['list']}

        datalist = result['data']['list']
        for data in datalist:
            for item in data['list']:
                if item['type'] == 2:
                    ignore = any(ann_id == item["ann_id"] for ann_id in ignored_ann_ids)
                    if ignore:
                        continue
                    for keyword in ignored_key_words:
                        if keyword in item['title']:
                            ignore = True
                            break
                    if ignore:
                        continue
                start_time = datetime.strptime(item['start_time'], "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(item['end_time'], "%Y-%m-%d %H:%M:%S")
                if event_detail[item["ann_id"]]:
                    content = event_detail[item["ann_id"]]['content']
                    searchObj = re.search('(\d+)\/(\d+)\/(\d+)\s(\d+):(\d+):(\d+)', content, re.M | re.I)

                    try:
                        datelist = searchObj.groups()
                        if datelist and len(datelist) >= 6:
                            ctime = datetime.strptime(
                                f'{datelist[0]}-{datelist[1]}-{datelist[2]} {datelist[3]}:{datelist[4]}:{datelist[5]}',
                                "%Y-%m-%d %H:%M:%S")

                            if start_time < ctime < end_time:
                                start_time = ctime
                    except Exception as e:
                        pass
                event = {'title':  item['title'], 'start': start_time, 'end': end_time, 'forever': False, 'type': 0,
                         'banner': item['banner'], 'color': '#2196f3'}

                if '任务' in item['title']:
                    event['forever'] = True
                    event['color'] = '#f764ad'
                    event['banner'] = item['banner']
                if item['type'] == 1:
                    event['type'] = 1
                if '扭蛋' in item['tag_label']:
                    event['type'] = 2
                    event['color'] = '#ffc107'
                    event['banner'] = item['banner']
                if '双倍' in item['title']:
                    event['type'] = 3
                    event['banner'] = item['banner']
                    event['color'] = '#580dda'
                event_data['cn'].append(event)
        for i in range(2):
            curmon = datetime.now() + relativedelta(months=i)
            nextmon = curmon + relativedelta(months=1)
            event_data['cn'].append({'title':   '「深境螺旋」· 上半段',
                                     'start':   datetime.strptime(curmon.strftime("%Y/%m/01 04:00"), "%Y/%m/%d %H:%M"),
                                     'end':     datetime.strptime(curmon.strftime("%Y/%m/16 03:59"), "%Y/%m/%d %H:%M"),
                                     'forever': False, 'type': 3, 'color': '#580dda', 'banner': res / 'sy.jpg'})

            event_data['cn'].append({'title':   '「深境螺旋」· 下半段 ',
                                     'start':   datetime.strptime(curmon.strftime("%Y/%m/16 04:00"), "%Y/%m/%d %H:%M"),
                                     'end':     datetime.strptime(nextmon.strftime("%Y/%m/01 03:59"), "%Y/%m/%d %H:%M"),
                                     'forever': False, 'type': 3, 'color': '#580dda', 'banner': res / 'sy.jpg'})

        return 0
    return 1


async def load_event(server):
    return await load_event_cn() if server == 'cn' else 1


def get_pcr_now(offset):
    pcr_now = datetime.now()
    if pcr_now.hour < 4:
        pcr_now -= timedelta(days=1)
    pcr_now = pcr_now.replace(
        hour=18, minute=0, second=0, microsecond=0)  # 用晚6点做基准
    pcr_now = pcr_now + timedelta(days=offset)
    return pcr_now


async def get_events(server, offset, days):
    events = []
    pcr_now = datetime.now()
    if pcr_now.hour < 4:
        pcr_now -= timedelta(days=1)
    pcr_now = pcr_now.replace(hour=18, minute=0, second=0, microsecond=0)
    await lock[server].acquire()
    try:
        t = pcr_now.strftime('%y%m%d')
        if event_updated[server] != t and await load_event(server) == 0:
            event_updated[server] = t
    finally:
        lock[server].release()
    start = pcr_now + timedelta(days=offset)
    end = start + timedelta(days=days)
    end -= timedelta(hours=18)
    for event in event_data[server]:
        if end > event['start'] and start < event['end']:
            event['start_days'] = math.ceil((event['start'] - start) / timedelta(days=1))
            event['left_days'] = math.floor((event['end'] - start) / timedelta(days=1))
            events.append(event)
    events.sort(key=lambda item: item["type"] * 100 - item['left_days'], reverse=True)

    return events


if __name__ == '__main__':
    async def main():
        await load_event_cn()


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
