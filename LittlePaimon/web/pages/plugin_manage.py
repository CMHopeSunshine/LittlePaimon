from amis import Form, Transfer, ActionType, Dialog, InputSubForm, DisplayModeEnum, InputText, Textarea, Switch, \
    InputNumber, Alert, Card, Tpl, CardsCRUD, Static, PageSchema, Page

# -------------插件使用权限设置------------------
ban_form = Form(title='',
                api='post:/LittlePaimon/api/set_plugin_bans',
                initApi='get:/LittlePaimon/api/get_plugin_bans?module_name=${module_name}',
                body=[
                    Transfer(
                        type='tabs-transfer',
                        name='bans',
                        value='${bans}',
                        label='',
                        resultTitle='已被禁用列表',
                        selectMode='tree',
                        joinValues=False,
                        extractValue=True,
                        statistics=True,
                        multiple=True,
                        menuTpl='${left_label}',
                        valueTpl='${right_label}',
                        source='get:/LittlePaimon/api/get_groups_and_members',
                    )])

permission_button = ActionType.Dialog(label='使用权限',
                                      icon='fa fa-pencil',
                                      # visibleOn='${isLoad}',
                                      dialog=Dialog(title='${name}使用权限设置', size='lg', body=ban_form))
# -------------插件使用权限设置------------------

# -------------插件帮助图设置------------------
command_form = InputSubForm(name='matchers',
                            label='命令列表',
                            multiple=True,
                            btnLabel='${pm_name}',
                            value='${matchers}',
                            description='该插件下具体的命令使用方法设置',
                            addButtonText='添加命令',
                            form=Form(
                                title='命令信息设置',
                                mode=DisplayModeEnum.horizontal,
                                labelAlign='right',
                                body=[
                                    InputText(label='命令标识名称', name='pm_name', value='${pm_name}', required=True,
                                              description='仅用于标识命令，不会显示在帮助图中，所以若是本身已有的命令，请勿修改！'),
                                    InputText(label='命令用法', name='pm_usage', value='${pm_usage}',
                                              description='命令的使用方法，建议不要太长'),
                                    Textarea(label='命令详细描述', name='pm_description', value='${pm_description}',
                                             description='命令的详细描述，可以用^强制换行', showCounter=False),
                                    Switch(label='是否展示', name='pm_show', value='${pm_show}',
                                           description='是否在帮助图中展示该命令'),
                                    InputNumber(label='展示优先级', name='pm_priority', value='${pm_priority}',
                                                description='在帮助图中展示的优先级，数字越小越靠前', min=0, max=99,
                                                displayMode='enhance'),
                                ]
                            ))
detail_form = Form(title='',
                   api='post:/LittlePaimon/api/set_plugin_detail',
                   submitText='保存修改',
                   mode=DisplayModeEnum.horizontal,
                   labelAlign='right',
                   body=[
                       InputText(label='插件名称', name='name', value='${name}', required=True,
                                 description='插件显示的名称，建议不要过长'),
                       Static(label='插件模块名', name='module_name', value='${module_name}'),
                       Textarea(label='插件描述', name='description', value='${description}', clearable=True,
                                description='仅用于在本管理页面中显示，不会在帮助图中显示', showCounter=False),
                       Textarea(label='插件使用说明', name='usage', value='${usage}', clearable=True,
                                description='会在该插件没有具体命令的使用说明时，显示在帮助图中', showCounter=False),
                       Switch(label='是否展示', name='show', value='${show}',
                              description='是否在帮助图中展示该插件'),
                       InputNumber(label='展示优先级', name='priority', value='${priority}',
                                   description='在帮助图及本管理页面中展示的顺序，数字越小越靠前',
                                   min=0, max=99, displayMode='enhance'),
                       command_form
                   ])
tips_alert = Alert(level='info',
                   body='以下设置用于在本管理页面以及help帮助图中显示插件的信息，不会影响插件的实际使用，你可以修改这些信息来自定义帮助图效果。')
detail_button = ActionType.Dialog(label='信息',
                                  size='lg',
                                  icon='fa fa-pencil',
                                  dialog=Dialog(title='${name}信息设置', size='lg', body=[tips_alert, detail_form]))

card = Card(
    header=Card.Header(title='$name',
                       subTitle='$module_name',
                       description='$description',
                       avatarText='$name',
                       avatarTextClassName='overflow-hidden'),
    actions=[detail_button, permission_button],
    toolbar=[
        Tpl(tpl='未加载', className='label label-warning', hiddenOn='${isLoad}'),
        Switch(name='enable',
               value='${status}',
               onText='启用',
               offText='禁用',
               visibleOn='${isLoad}',
               onEvent={
                   'change': {
                       'actions': {
                           'actionType': 'ajax',
                           'args':       {
                               'api':      {
                                   'url':    '/LittlePaimon/api/set_plugin_status',
                                   'method': 'post'
                               },
                               'messages': {
                                   'success': '${name}插件全局开关已设置为${event.data.value}',
                                   'failed':  '插件设置失败'
                               },
                               'status':   '${event.data.value}',
                               'plugin':   '${module_name}'
                           }
                       }
                   }
               })
    ])

cards_curd = CardsCRUD(mode='cards',
                       title='',
                       syncLocation=False,
                       api='/LittlePaimon/api/get_plugins',
                       loadDataOnce=True,
                       source='${rows | filter:name:match:keywords_name | filter:description:match:keywords_description}',
                       filter={
                           'body': [
                               InputText(name='keywords_name', label='插件名'),
                               InputText(name='keywords_description', label='插件描述')
                           ]
                       },
                       perPage=12,
                       autoJumpToTopOnPagerChange=True,
                       placeholder='暂无插件信息',
                       footerToolbar=['switch-per-page', 'pagination'],
                       columnsCount=3,
                       card=card)
page = PageSchema(url='/bot_config/plugins', icon='fa fa-cube', label='插件管理', schema=Page(title='插件管理', body=cards_curd))
