from LittlePaimon.utils import __version__
from LittlePaimon.config import config
from amis import (
    Page,
    PageSchema,
    Html,
    Property,
    Service,
    Flex,
    ActionType,
    LevelEnum,
    Divider,
    ButtonGroupSelect,
    Log,
    Alert,
    Form,
    Dialog,
    Select,
    Group,
    InputText,
    DisplayModeEnum,
    Horizontal,
)

logo = Html(
    html=f'''
<p align="center">
    <a href="https://github.com/CMHopeSunshine/LittlePaimon/">
        <img src="https://s1.ax1x.com/2023/02/05/pS62DJK.png"
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
'''
)
select_log_num = Select(
    label='日志数量',
    name='log_num',
    value=100,
    options=[
        {'label': 100, 'value': 100},
        {'label': 200, 'value': 200},
        {'label': 300, 'value': 300},
        {'label': 400, 'value': 400},
        {'label': 500, 'value': 500},
    ],
)

select_log_level = ButtonGroupSelect(
    label='日志等级',
    name='log_level',
    btnLevel=LevelEnum.light,
    btnActiveLevel=LevelEnum.info,
    value='info',
    options=[{'label': 'INFO', 'value': 'info'}, {'label': 'DEBUG', 'value': 'debug'}],
)

log_page = Log(
    autoScroll=True,
    placeholder='暂无日志数据...',
    operation=['stop', 'showLineNumber', 'filter'],
    source={
        'method': 'get',
        'url': '/LittlePaimon/api/log?level=${log_level | raw}&num=${log_num | raw}',
        'headers': {'token': config.secret_key[:16]},
    },
)

cmd_input = Form(
    mode=DisplayModeEnum.horizontal,
    horizontal=Horizontal(left=0),
    wrapWithPanel=False,
    body=[
        InputText(
            name='command',
            required=True,
            clearable=True,
            addOn=ActionType.Dialog(
                label='执行',
                level=LevelEnum.primary,
                dialog=Dialog(
                    title='命令执行结果',
                    size='xl',
                    body=Log(
                        autoScroll=True,
                        placeholder='执行命令中，请稍候...',
                        operation=['stop', 'showLineNumber', 'filter'],
                        source={
                            'method': 'get',
                            'url': '/LittlePaimon/api/run_cmd?cmd=${command | raw}',
                            'headers': {'token': config.secret_key[:16]},
                        },
                    ),
                ),
            ),
        )
    ],
)

operation_button = Flex(
    justify='center',
    items=[
        ActionType.Ajax(
            label='更新',
            api='/LittlePaimon/api/bot_update',
            confirmText='该操作将会对Bot进行检查并尝试更新，请在更新完成后重启Bot使更新生效',
            level=LevelEnum.info,
        ),
        ActionType.Ajax(
            label='重启',
            className='m-l',
            api='/LittlePaimon/api/bot_restart',
            confirmText='该操作将会使Bot重启，在完成重启之前，该页面也将无法访问（也可能会弹出报错，可无视），请耐心等待重启',
            level=LevelEnum.danger,
        ),
        ActionType.Dialog(
            label='日志',
            className='m-l',
            level=LevelEnum.primary,
            dialog=Dialog(
                title='查看日志',
                size='xl',
                actions=[],
                body=[
                    Alert(
                        level=LevelEnum.info,
                        body='查看最近最多500条日志，不会自动刷新，需要手动点击两次"暂停键"来进行刷新，DEBUG日志需要Nonebot日志模式为DEBUG才能查看。',
                    ),
                    Form(
                        body=[Group(body=[select_log_num, select_log_level]), log_page]
                    ),
                ],
            ),
        ),
        ActionType.Dialog(
            label='执行命令',
            className='m-l',
            level=LevelEnum.warning,
            dialog=Dialog(title='执行命令', size='lg', actions=[], body=[cmd_input]),
        ),
    ],
)

status = Service(
    api='/LittlePaimon/api/status',
    body=Property(
        title='机器人信息',
        column=2,
        items=[
            Property.Item(label='Bot昵称', content='${nickname}'),
            Property.Item(label='Bot qq号', content='${bot_id}'),
            Property.Item(label='Bot启动时间', content='${start_time}'),
            Property.Item(label='系统启动时间', content='${system_start_time}'),
            Property.Item(label='已接收信息', content='${msg_received}'),
            Property.Item(label='已发送信息', content='${msg_sent}'),
            Property.Item(label='CPU占用率', content='${cpu_percent}'),
            Property.Item(label='RAM占用率', content='${ram_percent}'),
            Property.Item(label='SWAP占用率', content='${swap_percent}', span=2),
        ],
    ),
)

page_detail = Page(title='', body=[logo, operation_button, Divider(), status])
page = PageSchema(
    url='/home', label='首页', icon='fa fa-home', isDefaultPage=True, schema=page_detail
)
