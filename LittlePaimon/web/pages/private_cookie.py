from amis import Page, PageSchema, ActionType, LevelEnum, Dialog, Form, InputNumber, Textarea, Action, Static, \
    TableCRUD, TableColumn, ColumnOperation
from .constants import status_map, status_filter

add_button = ActionType.Dialog(label='添加私人Cookie',
                               level=LevelEnum.primary,
                               dialog=Dialog(title='添加私人Cookie',
                                             body=Form(
                                                 api='post:/LittlePaimon/api/add_cookie?cookie_type=private&force=false',
                                                 body=[InputNumber(name='user_id', label='QQ号', required=True),
                                                       Textarea(name='cookie', label='Cookie', required=True,
                                                                showCounter=False)])))
force_add_button = ActionType.Dialog(label='强制添加私人Cookie',
                                     level=LevelEnum.warning,
                                     confirmText='强制修改Cookie不会对Cookie有效性和与uid的关联性进行校验，如果你不确定是否正确有效，请不要强制修改。',
                                     dialog=Dialog(title='强制添加私人Cookie',
                                                   body=Form(
                                                       api='post:/LittlePaimon/api/add_cookie?cookie_type=private&force=true',
                                                       body=[InputNumber(name='user_id', label='QQ号', required=True),
                                                             InputNumber(name='uid', label='UID', required=True),
                                                             InputNumber(name='mys_id', label='米游社ID',
                                                                         required=True),
                                                             Textarea(name='cookie', label='Cookie', required=True,
                                                                      showCounter=False),
                                                             Textarea(name='stoken', label='Stoken', showCounter=False)
                                                             ])))
delete_button = ActionType.Ajax(label='删除', level=LevelEnum.danger,
                                confirmText='确认删除该私人Cookie',
                                api='delete:/LittlePaimon/api/delete_cookie?cookie_type=private&id=${id}')
save_action_button = Action(label='保存修改', level=LevelEnum.warning, type='submit')
cancel_action_button = Action(label='关闭', level=LevelEnum.default, actionType='close')
detail_button = ActionType.Dialog(label='修改',
                                  level=LevelEnum.info,
                                  dialog=Dialog(title='Cookie详情',
                                                body=Form(
                                                    api='post:/LittlePaimon/api/update_private_cookie?force=false',
                                                    body=[Static(name='id', label='ID'),
                                                          InputNumber(name='user_id', label='QQ号', required=True),
                                                          Static(name='uid', label='UID'),
                                                          Static(name='mys_id', label='米游社ID'),
                                                          Textarea(name='cookie', label='Cookie', required=True,
                                                                   showCounter=False),
                                                          Static(name='stoken', label='Stoken')]),
                                                actions=[cancel_action_button, save_action_button]))
force_button = ActionType.Dialog(label='强制修改',
                                 level=LevelEnum.warning,
                                 confirmText='强制修改Cookie不会对Cookie有效性和与uid的关联性进行校验，如果你不确定是否正确有效，请不要强制修改。',
                                 dialog=Dialog(title='Cookie详情强制修改',
                                               body=Form(
                                                   api='post:/LittlePaimon/api/update_private_cookie?force=true',
                                                   body=[Static(name='id', label='ID'),
                                                         InputNumber(name='user_id', label='QQ号', required=True),
                                                         InputNumber(name='uid', label='UID', required=True),
                                                         InputNumber(name='mys_id', label='米游社ID', required=True),
                                                         Textarea(name='cookie', label='Cookie', required=True,
                                                                  showCounter=False),
                                                         Textarea(name='stoken', label='Stoken', showCounter=False)]),
                                               actions=[cancel_action_button,
                                                        save_action_button]))
table = TableCRUD(mode='table',
                  title='',
                  syncLocation=False,
                  api='/LittlePaimon/api/get_private_cookies',
                  footable=True,
                  columns=[TableColumn(label='ID', name='id'),
                           TableColumn(label='QQ号', name='user_id', searchable=True),
                           TableColumn(label='UID', name='uid', searchable=True),
                           TableColumn(label='米游社ID', name='mys_id', searchable=True),
                           TableColumn(type='mapping', label='状态', name='status', filterable=status_filter,
                                       map=status_map),
                           TableColumn(label='Cookie', name='cookie', breakpoint='*'),
                           TableColumn(label='Stoken', name='stoken', breakpoint='*'),
                           ColumnOperation(label='操作', buttons=[detail_button, force_button, delete_button])],
                  headerToolbar=[add_button, force_add_button],
                  footerToolbar=['switch-per-page', 'pagination'])

page = PageSchema(url='/cookie/private', icon='fa fa-key', label='私人Cookie',
                  schema=Page(title='私人Cookie', body=table))
