import base64
from io import BytesIO

from nonebot_plugin_htmlrender import html_to_pic
import jinja2

from .event import *
from .draw import *

body = []
template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Paimon_Calendar/template')
env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path), enable_async=True)


def im2base64str(im):
    io = BytesIO()
    im.save(io, 'png')
    base64_str = f"base64://{base64.b64encode(io.getvalue()).decode()}"
    return base64_str


async def generate_day_schedule(server='cn'):

    events = await get_events(server, 0, 15)
    has_prediction = False
    """ 追加数据前先执行清除，以防数据叠加 """
    body.clear()

    for event in events:
        if event['start_days'] > 0:
            has_prediction = True

    template = env.get_template('calendar.html')
    for event in events:
        if event['start_days'] <= 0:
            time = '即将结束' if event["left_days"] == 0 else f'{str(event["left_days"])}天后结束'
            body.append({
                'title': event['title'],
                'time': time,
                'online': f'{datetime.strftime(event["start"], r"%m-%d")} ~ {datetime.strftime(event["end"], r"%m-%d")}',
                'color': event['color'],
                'banner': event['banner']
            })
    if has_prediction:
        for event in events:
            if event['start_days'] > 0:
                time = '即将开始' if event["start_days"] == 0 else f'{str(event["start_days"])}天后开始'
                body.append({
                    'title': event['title'],
                    'time': time,
                    'online': f'{datetime.strftime(event["start"], r"%m-%d")} ~ {datetime.strftime(event["end"], r"%m-%d")}',
                    'color': event['color'],
                    'banner': event['banner']
                })

    content = await template.render_async(body=body, css_path=template_path)
    return await html_to_pic(content, wait=0, viewport={"width": 600, "height": 100})


