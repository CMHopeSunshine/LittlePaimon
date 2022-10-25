from LittlePaimon import __version__
from amis import App, PageSchema, Tpl, Page, DropDownButton, ActionType, LevelEnum, Flex
from .public_cookie import page as public_cookie_page
from .private_cookie import page as private_cookie_page
from .plugin_manage import page as plugin_manage_page
from .home_page import page as home_page
from .config_manage import page as config_page

# from .learning_chat_manage import page as learning_chat_page

# dropdown = DropDownButton(
#     buttons=[
#         ActionType.Dialog(label='用户信息',
#                           dialog=Dialog(title='用户信息',
#                                         body='待定')),
#         ActionType.Url(label='退出登录',
#                        url='/LittlePaimon/api/logout')
#     ]
# )

action_button = DropDownButton(
    label='操作',
    trigger='hover',
    buttons=[
        ActionType.Ajax(
            label='更新',
            api='/LittlePaimon/api/bot_update',
            confirmText='该操作将会对Bot进行检查并尝试更新，请在更新完成后重启Bot使更新生效',
        ),
        ActionType.Ajax(
            label='重启',
            api='/LittlePaimon/api/bot_restart',
            confirmText='该操作将会使Bot重启，在完成重启之前，该页面也将无法访问，请耐心等待重启',
        )
    ]
)
github_logo = Tpl(className='w-full',
                            tpl='<div class="flex justify-between"><div></div><div><a href="https://github.com/CMHopeSunshine/LittlePaimon" target="_blank" title="Copyright"><i class="fa fa-github fa-2x"></i></a></div></div>')
header = Flex(className='w-full', justify='flex-end', alignItems='flex-end', items=[action_button, github_logo])


admin_app = App(brandName='LittlePaimon',
                logo='http://static.cherishmoon.fun/LittlePaimon/readme/logo.png',
                header=header,
                pages=[{
                    'children': [
                        home_page,
                        PageSchema(label='Cookie管理', url='/cookie', icon='fa fa-key',
                                   children=[public_cookie_page, private_cookie_page]),
                        PageSchema(label='机器人配置', url='/config', icon='fa fa-wrench',
                                   children=[plugin_manage_page, config_page]),
                    ]}],
                footer=f'<div class="p-2 text-center bg-blue-100">Copyright © 2021 - 2022 <a href="https://github.com/CMHopeSunshine/LittlePaimon" target="_blank" class="link-secondary">LittlePaimon v{__version__}</a> X<a target="_blank" href="https://github.com/baidu/amis" class="link-secondary" rel="noopener"> amis v2.2.0</a></div>')

blank_page = Page(title='LittlePaimon', body='该页面未开启或不存在')
