import jinja2
from LittlePaimon.utils.browser import get_new_page
from .data_source import *
from datetime import datetime, timedelta

body = []
weeks = []
weekList = ['一', '二', '三', '四', '五', '六', '日']
template_path = str(Path(__file__).parent / 'template')
template_name = "calendar.html"
env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path), enable_async=True)


async def generate_day_schedule(server='cn', **kwargs):
    events = await get_events(server, 0, 15)
    has_prediction = False
    """ 追加数据前先执行清除，以防数据叠加 """
    body.clear()
    weeks.clear()
    t = datetime.now()

    for i in range(7):
        d2 = (t + timedelta(days=i)).strftime("%Y-%m-%d")
        """ 分割 [年|月|日]"""
        date_full = str(d2).split("-")
        current = 'm-events-calendar__table-header-current' if t.strftime("%d") == date_full[2] else ""
        date = re.search(r'0\d+', date_full[1]).group(0).replace('0', '') if re.search(r'0\d+', date_full[1]) else \
            date_full[1]

        week = datetime(int(date_full[0]), int(date_full[1]), int(date_full[2])).isoweekday()
        weeks.append({
            'week': f'星期{weekList[week - 1]}',
            'date': f'{date}.{date_full[2]}',
            'current': current
        })

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
    content = await template.render_async(body=body, css_path=template_path, week=weeks)

    async with get_new_page(**kwargs) as page:
        await page.goto('file://' + template_path + "/" + template_name)
        await page.set_content(content, wait_until='networkidle')
        await page.wait_for_timeout(0)
        pic = await page.screenshot(full_page=True)
    return pic
