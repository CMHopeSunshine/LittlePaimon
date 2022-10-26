from amis import Page, PageSchema, Html, Property, Service, Flex, ActionType, LevelEnum, Divider
from LittlePaimon import __version__

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


# log_page = Log(
#     height=500,
#     autoScroll=True,
#     placeholder='日志加载中...',
#     operation=['stop', 'filter'],
#     source='/LittlePaimon/api/log'
# )
# log_button = ActionType.Dialog(
#     label='查看日志',
#     dialog=Dialog(
#         title='Nonebot日志',
#         body=log_page,
#         size='lg')
# )
# text = Tpl(tpl='接收消息数：${msg_received} | 发送消息数：${msg_sent}')

# page_detail = Page(title='主页',
#                    initApi='/LittlePaimon/api/status',
#                    body=[text, log_button])
page_detail = Page(title='', body=[logo, operation_button, Divider(), status])
page = PageSchema(url='/home', label='首页', icon='fa fa-home', isDefaultPage=True, schema=page_detail)
