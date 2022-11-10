from amis import Page, PageSchema, ActionType, LevelEnum, Dialog, Form, Textarea, TableCRUD, TableColumn, \
    ColumnOperation
from .constants import status_map, status_filter

add_button = ActionType.Dialog(label='添加公共Cookie',
                               level=LevelEnum.primary,
                               dialog=Dialog(title='添加公共Cookie',
                                             body=Form(api='post:/LittlePaimon/api/add_public_cookie?force=false',
                                                       body=[Textarea(name='cookie', label='Cookie', required=True,
                                                                      showCounter=False)])))
add_button_force = ActionType.Dialog(label='强制添加公共Cookie',
                                     level=LevelEnum.warning,
                                     confirmText='强制添加公共Cookie不会对Cookie有效性进行校验，如果你不确定是否正确有效，请不要强制添加。',
                                     dialog=Dialog(title='强制添加公共Cookie',
                                                   body=Form(api='post:/LittlePaimon/api/add_public_cookie?force=true',
                                                             body=[
                                                                 Textarea(name='cookie', label='Cookie', required=True,
                                                                          showCounter=False)])))
delete_button = ActionType.Ajax(label='删除', level=LevelEnum.danger,
                                confirmText='确认删除该公共Cookie',
                                api='delete:/LittlePaimon/api/delete_public_cookie?id=${id}')
table = TableCRUD(mode='table',
                  title='',
                  syncLocation=False,
                  api='/LittlePaimon/api/get_public_cookies',
                  columns=[TableColumn(label='ID', name='id', width='8%'),
                           TableColumn(label='Cookie', name='cookie', width='64%'),
                           TableColumn(type='mapping', label='状态', name='status', filterable=status_filter,
                                       map=status_map, width='12%'),
                           ColumnOperation(label='操作', buttons=[delete_button], width='16%')],
                  headerToolbar=[add_button, add_button_force])
page = PageSchema(label='公共Cookie', icon='fa fa-key', url='/cookie/public',
                  schema=Page(title='公共Cookie', body=table))
