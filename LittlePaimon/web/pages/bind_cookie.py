from LittlePaimon.utils import __version__
from amis import AmisAPI, Collapse, Form, InputNumber, Textarea, Action, LevelEnum, Divider, Page, Html

collapse_text = "<h2>重要提醒：</h2>Cookie的作用相当于账号密码，非常重要，如是非可信任的机器人，请勿绑定！！<br><h2>获取方法：</h2>详见<a href='https://docs.qq.com/doc/DQ3JLWk1vQVllZ2Z1'>Cookie获取教程</a>"
api = AmisAPI(method='post', url='/LittlePaimon/api/bind_cookie')
collapse = Collapse(header='Cookie说明及获取方法', body=Html(html=collapse_text))
form = Form(title='绑定Cookie', api=api, body=[
    InputNumber(name='user_id', label='QQ号', required=True),
    Textarea(name='cookie', label='Cookie', required=True, clearable=True,showCounter=False),
    # Checkboxes(name='function', label='同时开启以下功能', options=[
    #     {'label': '米游社自动签到', 'value': 'sign'},
    #     {'label': '米游币自动获取', 'value': 'coin'}
    # ], joinValues=False, extractValue=True)
], actions=[Action(label='绑定', level=LevelEnum.success, confirmText='我已知晓Cookie的重要性，确认绑定', type='submit'),
            Action(label='重置', level=LevelEnum.warning, type='reset')])
footer = Html(html=f'<div class="p-2 text-center bg-blue-100">Copyright © 2021 - 2022 <a href="https://github.com/CMHopeSunshine/LittlePaimon" target="_blank" class="link-secondary">LittlePaimon v{__version__}</a> X<a target="_blank" href="https://github.com/baidu/amis" class="link-secondary" rel="noopener"> amis v2.2.0</a></div>')
bind_cookie_page = Page(title='绑定Cookie', body=[collapse, Divider(), form, footer])
