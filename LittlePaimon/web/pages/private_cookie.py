from amis import Page, PageSchema, ActionType, LevelEnum, Dialog, Form, InputNumber, Textarea, Action, Static, TableCRUD, TableColumn, ColumnOperation
from .constants import status_map, status_filter

add_button = ActionType.Dialog(label='添加私人Cookie',
                               level=LevelEnum.primary,
                               dialog=Dialog(title='添加私人Cookie',
                                             body=Form(api='post:/LittlePaimon/api/save_private_cookie',
                                                       body=[InputNumber(name='user_id', label='QQ号', required=True),
                                                             Textarea(name='cookie', label='Cookie', required=True,showCounter=False)])))
delete_button = ActionType.Ajax(label='删除', level=LevelEnum.danger,
                                confirmText='确认删除该私人Cookie',
                                api='delete:/LittlePaimon/api/delete_private_cookie?id=${id}')
save_action_button = Action(label='保存修改', level=LevelEnum.warning, type='submit')
cancel_action_button = Action(label='关闭', level=LevelEnum.default, actionType='close')
detail_button = ActionType.Dialog(label='详情',
                                  level=LevelEnum.info,
                                  dialog=Dialog(title='Cookie详情',
                                                body=Form(
                                                    api='post:/LittlePaimon/api/save_private_cookie',
                                                    body=[Static(name='id', label='ID'),
                                                          InputNumber(name='user_id', label='QQ号', required=True),
                                                          Static(name='uid', label='UID'),
                                                          Static(name='mys_id', label='米游社ID'),
                                                          Textarea(name='cookie', label='Cookie', required=True,showCounter=False),
                                                          Static(name='stoken', label='Stoken')]),
                                                actions=[cancel_action_button, save_action_button]))
table = TableCRUD(mode='table',
                  title='',
                  syncLocation=False,
                  api='/LittlePaimon/api/get_private_cookies',
                  columns=[TableColumn(label='ID', name='id'),
                           TableColumn(label='QQ号', name='user_id', searchable=True),
                           TableColumn(label='UID', name='uid', searchable=True),
                           TableColumn(label='米游社ID', name='mys_id', searchable=True),
                           TableColumn(type='mapping', label='状态', name='status', filterable=status_filter,
                                       map=status_map),
                           ColumnOperation(label='操作', buttons=[detail_button, delete_button])],
                  headerToolbar=[add_button],
                  footerToolbar=['switch-per-page', 'pagination'])

page = PageSchema(url='/private_cookie', label='私人Cookie', schema=Page(title='私人Cookie', body=table))
