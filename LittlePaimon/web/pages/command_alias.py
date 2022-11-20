from amis import Form, Switch, InputSubForm, Hidden, ButtonGroupSelect, InputText, Radios, Checkbox, Select, Static, Alert, Html, PageSchema, Page

main_form = Form(
    title='命令别名',
    initApi='get:/LittlePaimon/api/command_alias',
    api='post:/LittlePaimon/api/command_alias',
    submitText='保存',
    body=[
        Switch(name='command_alias_enable', label='功能开关', onText='全局启用', offText='全局关闭'),
        InputSubForm(
            name='items',
            label='已设置的命令别名',
            multiple=True,
            btnLabel='${alias} >> ${command}',
            draggable=True,
            addable=True,
            removable=True,
            addButtonText='添加命令别名',
            showErrorMsg=False,
            form=Form(
                title='命令别名',
                body=[
                    Hidden(name='id'),
                    ButtonGroupSelect(name='is_regex', label='匹配模式', value=False,
                                      options=[
                                          {'label': '普通匹配', 'value': False},
                                          {'label': '正则匹配', 'value': True}
                                      ]),
                    InputText(name='alias', label='命令别名', required=True),
                    InputText(name='command', label='原命令', required=True),
                    Radios(name='mode', label='匹配位置', value='前缀', hiddenOn='${is_regex == true}', required=True,
                           options=[
                               {
                                   'label': '前缀',
                                   'value': '前缀'
                               },
                               {
                                   'label': '后缀',
                                   'value': '后缀'
                               },
                               {
                                   'label': '全匹配',
                                   'value': '全匹配'
                               }
                           ]),
                    Checkbox(name='is_reverse', label='是否反转', hiddenOn='${is_regex == true}'),
                    Select(name='group_id', label='设置群', value='all', required=True,
                           source='${group_list}')
                ]
            )
        )
    ]
)

test_form = Form(
    title='测试',
    api='get:/LittlePaimon/api/test_command_alias?group_id=${group_id}&message=${message}',
    submitText='测试',
    body=[
        Select(name='group_id', label='测试群', value='all', required=True, source='${group_list}'),
        InputText(name='message', label='测试消息', required=True),
        Static(className='text-red-600', name='new_msg', label='命令别名修改后消息', visibleOn="typeof data.new_msg !== 'undefined'")
    ]
)

tips = Alert(level='info',
             body=Html(html='命令别名的详细用法和配置例子可以在<a href="https://docs.paimon.cherishmoon.fun/configs/manage/plugin-manage.html#%E8%87%AA%E5%AE%9A%E4%B9%89%E5%91%BD%E4%BB%A4%E5%88%AB%E5%90%8D" target="_blank">文档</a>中查看，配置保存后，可以在下方的"测试"一栏进行实时测试。'))


page = PageSchema(url='/bot_config/command_alias', icon='fa  fa-angle-double-right', label='命令别名',
                  schema=Page(title='', initApi='/LittlePaimon/api/get_group_list?include_all=true', body=[tips, main_form, test_form]))
