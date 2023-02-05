from amis import App, PageSchema, Tpl, Page, Flex, Log
from LittlePaimon.utils import __version__
from .config_manage import page as config_page
from .home_page import page as home_page
from .plugin_manage import page as plugin_manage_page
from .private_cookie import page as private_cookie_page
from .public_cookie import page as public_cookie_page
from .command_alias import page as command_alias_page


github_logo = Tpl(
    className='w-full',
    tpl='<div class="flex justify-between"><div></div><div><a href="https://github.com/CMHopeSunshine/LittlePaimon" target="_blank" title="Copyright"><i class="fa fa-github fa-2x"></i></a></div></div>',
)
header = Flex(
    className='w-full', justify='flex-end', alignItems='flex-end', items=[github_logo]
)


admin_app = App(
    brandName='LittlePaimon',
    logo='https://s1.ax1x.com/2023/02/05/pS62DJK.png',
    header=header,
    pages=[
        {
            'children': [
                home_page,
                PageSchema(
                    label='Cookie管理',
                    icon='fa fa-key',
                    children=[public_cookie_page, private_cookie_page],
                ),
                PageSchema(
                    label='机器人配置',
                    icon='fa fa-wrench',
                    children=[plugin_manage_page, config_page, command_alias_page],
                ),
            ]
        }
    ],
    footer=f'<div class="p-2 text-center bg-blue-100">Copyright © 2021 - 2022 <a href="https://github.com/CMHopeSunshine/LittlePaimon" target="_blank" class="link-secondary">LittlePaimon v{__version__}</a> X<a target="_blank" href="https://github.com/baidu/amis" class="link-secondary" rel="noopener"> amis v2.2.0</a></div>',
)

blank_page = Page(title='LittlePaimon 404', body='该页面未开启或不存在')
