from LittlePaimon.utils import __version__
from amis import (
    Form,
    InputText,
    InputPassword,
    DisplayModeEnum,
    Horizontal,
    Remark,
    Html,
    Page,
    AmisAPI,
    Wrapper,
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
<br>
'''
)
login_api = AmisAPI(
    url='/LittlePaimon/api/login',
    method='post',
    adaptor='''
        if (payload.status == 0) {
            localStorage.setItem("token", payload.data.token);
        }
        return payload;
    ''',
)

login_form = Form(
    api=login_api,
    title='',
    body=[
        InputText(
            name='user_id',
            label='用户ID',
            labelRemark=Remark(shape='circle', content='超级用户的QQ号，在.env.prod文件中配置'),
        ),
        InputPassword(
            name='password',
            label='密码',
            labelRemark=Remark(
                shape='circle', content='默认为admin，可以在paimon_config.json中修改'
            ),
        ),
        # Switch(name='is_admin', label='身份组', onText='管理员', offText='用户', labelRemark=Remark(shape='circle', content='是否以管理员身份登录'))
    ],
    mode=DisplayModeEnum.horizontal,
    horizontal=Horizontal(left=3, right=9, offset=5),
    redirect='/LittlePaimon/admin',
)
body = Wrapper(className='w-2/5 mx-auto my-0 m:w-full', body=login_form)
login_page = Page(title='', body=[logo, body])
