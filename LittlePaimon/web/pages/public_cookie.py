from amis import Page, PageSchema, ActionType, LevelEnum, Dialog, Form, Textarea, TableCRUD, TableColumn, ColumnOperation
from .constants import status_map, status_filter

add_button = ActionType.Dialog(label='添加公共Cookie',
                               level=LevelEnum.primary,
                               dialog=Dialog(title='添加公共Cookie',
                                             body=Form(api='post:/LittlePaimon/api/add_public_cookie',
                                                       body=[Textarea(name='cookie', label='Cookie', required=True,showCounter=False)])))
delete_button = ActionType.Ajax(label='删除', level=LevelEnum.danger,
                                confirmText='确认删除该公共Cookie',
                                api='delete:/LittlePaimon/api/delete_public_cookie?id=${id}')
table = TableCRUD(mode='table',
                  title='',
                  syncLocation=False,
                  api='/LittlePaimon/api/get_public_cookies',
                  columns=[TableColumn(label='ID', name='id', width='8%'),
                           TableColumn(label='Cookie', name='cookie', width='64%'),
                           TableColumn(type='mapping', label='状态', name='status', filterable=status_filter, map=status_map, width='12%'),
                           ColumnOperation(label='操作', buttons=[delete_button], width='16%')],
                  headerToolbar=[add_button])
page = PageSchema(label='公共Cookie', url='public_cookie', schema=Page(title='公共Cookie', body=table))
