
import base64
from io import BytesIO
from .event import *
from .draw import *


def im2base64str(im):
    io = BytesIO()
    im.save(io, 'png')
    base64_str = f"base64://{base64.b64encode(io.getvalue()).decode()}"
    return base64_str


async def generate_day_schedule(server='cn'):
    events = await get_events(server, 0, 15)

    has_prediction = False
    for event in events:
        if event['start_days'] > 0:
            has_prediction = True
    if has_prediction:
        im = create_image(len(events) + 2)
    else:
        im = create_image(len(events) + 1)

    title = f'原神日历'
    pcr_now = get_pcr_now(0)
    draw_title(im, 0, title, pcr_now.strftime('%Y/%m/%d'), '正在进行')

    if len(events) == 0:
        draw_item(im, 1, 1, '无数据', 0, False)
    i = 1
    for event in events:
        if event['start_days'] <= 0:
            draw_item(im, i, event['type'], event['title'],
                      event['left_days'], event['forever'])
            i += 1
    if has_prediction:
        draw_title(im, i, right='即将开始')
        for event in events:
            if event['start_days'] > 0:
                i += 1
                draw_item(im, i, event['type'], event['title'], -
                          event['start_days'], event['forever'])
    return im
