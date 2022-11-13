from LittlePaimon.utils import __version__
from amis import Page, PageSchema, Html, Property, Service, Flex, ActionType, LevelEnum, Divider, ButtonGroupSelect, Log, Alert, Form, Dialog

logo = Html(html=f'''
<p align="center">
    <a href="https://github.com/CMHopeSunshine/LittlePaimon/">
        <img src="http://static.cherishmoon.fun/LittlePaimon/readme/logo.png"
         width="256" height="256" alt="LittlePaimon">
    </a>
</p>
<h1 align="center">LittlePaimon 控制台 V{__version__}</h1>
<div align="center">
    <a href="https://github.com/CMHopeSunshine/LittlePaimon" target="_blank">
    Github仓库</a> &nbsp; · &nbsp;
    <a href="https://docs.paimon.cherishmoon.fun/"
     target="_blank">文档</a>
</div>
<br>
''')
select_log = ButtonGroupSelect(
    label='日志等级',
    name='log_level',
    btnLevel=LevelEnum.light,
    btnActiveLevel=LevelEnum.info,
    value='/LittlePaimon/api/log?level=info',
    options=[
        {
            'label': 'INFO',
            'value': '/LittlePaimon/api/log?level=info'
        },
        {
            'label': 'DEBUG',
            'value': '/LittlePaimon/api/log?level=debug'
        }
    ]
)

log_page = Log(
    autoScroll=True,
    placeholder='暂无日志数据...',
    operation=['stop', 'showLineNumber', 'filter'],
    source='${log_level | raw}'
)

operation_button = Flex(justify='center', items=[
    ActionType.Ajax(
        label='更新',
        api='/LittlePaimon/api/bot_update',
        confirmText='该操作将会对Bot进行检查并尝试更新，请在更新完成后重启Bot使更新生效',
        level=LevelEnum.info
    ),
    ActionType.Ajax(
        label='重启',
        className='m-l',
        api='/LittlePaimon/api/bot_restart',
        confirmText='该操作将会使Bot重启，在完成重启之前，该页面也将无法访问（也可能会弹出报错，可无视），请耐心等待重启',
        level=LevelEnum.danger
    ),
    ActionType.Dialog(
        label='日志',
        className='m-l',
        level=LevelEnum.primary,
        dialog=Dialog(title='查看日志',
                      size='xl',
                      actions=[],
                      body=[
                          Alert(level=LevelEnum.info,
                                body='查看最近最多500条日志，不会自动刷新，需要手动点击两次"暂停键"来进行刷新。'),
                          Form(
                              body=[select_log, log_page]
                          )])
    )
])

status = Service(
    api='/LittlePaimon/api/status',
    body=Property(
        title='机器人信息',
        column=2,
        items=[
            Property.Item(
                label='Bot昵称',
                content='${nickname}'
            ),
            Property.Item(
                label='Bot qq号',
                content='${bot_id}'
            ),
            Property.Item(
                label='Bot启动时间',
                content='${start_time}'
            ),
            Property.Item(
                label='系统启动时间',
                content='${system_start_time}'
            ),
            Property.Item(
                label='已接收信息',
                content='${msg_received}'
            ),
            Property.Item(
                label='已发送信息',
                content='${msg_sent}'
            ),
            Property.Item(
                label='CPU占用率',
                content='${cpu_percent}'
            ),
            Property.Item(
                label='RAM占用率',
                content='${ram_percent}'
            ),
            Property.Item(
                label='SWAP占用率',
                content='${swap_percent}',
                span=2
            ),
        ]
    )
)

page_detail = Page(title='', body=[logo, operation_button, Divider(), status])
page = PageSchema(url='/home', label='首页', icon='fa fa-home', isDefaultPage=True, schema=page_detail)
