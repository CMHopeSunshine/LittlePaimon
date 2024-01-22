from amis import (
    Action,
    Divider,
    Form,
    InputText,
    LevelEnum,
    Page,
    PageSchema,
    Switch,
    Remark,
    InputNumber,
    InputTime,
    InputTimeRange,
    Alert,
    Editor,
    Select,
    InputTag
)

action_button = [Action(label='保存', level=LevelEnum.success, type='submit'),
                 Action(label='重置', level=LevelEnum.warning, type='reset')]

cookie_web_form = Form(
    title='Web端配置',
    api='/LittlePaimon/api/set_config',
    visibleOn='${select == 1}',
    body=[
        Switch(
            label='是否启用CookieWeb',
            name='启用CookieWeb',
            value='${启用CookieWeb}',
            labelRemark=Remark(shape='circle', content='是否启用为用户提供的绑定Cookie的网页'),
            onText='启用',
            offText='关闭'
        ),
        InputText(
            label='CookieWeb地址',
            name='CookieWeb地址',
            value='${CookieWeb地址}',
            labelRemark=Remark(shape='circle', content='只是设置对用户显示的CookieWeb地址，要填写实际的地址')
        ),
        Select(
            label='浏览器内核',
            name='浏览器内核',
            value='${浏览器内核}',
            labelRemark=Remark(shape='circle', content='用于生成原神日历的浏览器内核'),
            options=[
                {
                    'label': '火狐FireFox',
                    'value': 'firefox'
                },
                {
                    'label': '谷歌Chormium',
                    'value': 'chromium'
                },
                {
                    'label': 'WebKit',
                    'value': 'webkit'
                }
            ]
        ),
        Switch(
            label='是否启用Web端',
            name='启用Web端',
            value='${启用Web端}',
            labelRemark=Remark(shape='circle', content='即本Web管理页面，注意，关闭后刷新本页面将不再能访问'),
            onText='启用',
            offText='关闭'
        ),
        Select(
            label='Web端主题',
            name='Web端主题',
            value='${Web端主题}',
            labelRemark=Remark(shape='circle', content='Web端及CookieWeb的外观主题，刷新页面生效'),
            options=[
                {
                    'label': '云舍',
                    'value': 'default'
                },
                {
                    'label': '仿AntD',
                    'value': 'antd'
                },
                {
                    'label': 'ang',
                    'value': 'ang'
                },
                {
                    'label': '暗黑',
                    'value': 'dark'
                },
            ]
        ),
        InputText(
            label='Web端管理员密码',
            name='Web端管理员密码',
            value='${Web端管理员密码}',
            labelRemark=Remark(shape='circle', content='用于超级用户登录该Web端，修改后重启生效')
        ),
        InputText(
            label='Web端token密钥',
            name='Web端token密钥',
            value='${Web端token密钥}',
            labelRemark=Remark(shape='circle',
                               content='用于对Web端身份认证的token进行加密，为32位字符串，请不要保持为默认密钥，务必进行修改，修改后重启生效')
        ),
    ],
    actions=action_button
)

sim_gacha_form = Form(
    title='模拟抽卡',
    api='/LittlePaimon/api/set_config',
    visibleOn='${select == 2}',
    body=[
        InputNumber(
            label='群冷却',
            name='模拟抽卡群冷却',
            value='${模拟抽卡群冷却}',
            labelRemark=Remark(shape='circle', content='每个群在多少秒内只能进行一次抽卡'),
            displayMode='enhance',
            suffix='秒',
            min=0,
        ),
        InputNumber(
            label='群员冷却',
            name='模拟抽卡群员冷却',
            value='${模拟抽卡群员冷却}',
            labelRemark=Remark(shape='circle', content='在上一个配置的基础上，每位群员在多少秒内只能进行一次抽卡'),
            displayMode='enhance',
            suffix='秒',
            min=0,
        ),
        InputNumber(
            label='单次最多十连数',
            name='模拟抽卡单次最多十连数',
            value='${模拟抽卡单次最多十连数}',
            labelRemark=Remark(shape='circle', content='单次模拟抽卡同时最多的十连数，推荐不超过6次'),
            displayMode='enhance',
            suffix='次',
            min=1
        )
    ],
    actions=action_button
)

auto_mys_form = Form(
    title='自动任务',
    api='/LittlePaimon/api/set_config',
    visibleOn='${select == 3}',
    body=[
        Switch(
            label='米游社自动签到开关',
            name='米游社自动签到开关',
            value='${米游社自动签到开关}',
            onText='开启',
            offText='关闭'
        ),
        InputTime(
            label='米游社自动签到开始时间',
            name='米游社签到开始时间',
            value='${米游社签到开始时间}',
            labelRemark=Remark(shape='circle', content='会在每天这个时间点进行米游社自动签到任务，修改后重启生效'),
            inputFormat='HH时mm分',
            format='HH:mm'
        ),
        Divider(),
        Switch(
            label='米游币自动获取开关',
            name='米游币自动获取开关',
            value='${米游币自动获取开关}',
            onText='开启',
            offText='关闭'
        ),
        InputTime(
            label='米游币自动获取开始时间',
            name='米游币开始执行时间',
            value='${米游币开始执行时间}',
            labelRemark=Remark(shape='circle', content='会在每天这个时间点进行米游币自动获取任务，修改后重启生效'),
            inputFormat='HH时mm分',
            format='HH:mm'
        ),
        Divider(),
        Switch(
            label='云原神自动签到开关',
            name='云原神自动签到开关',
            value='${云原神自动签到开关}',
            onText='开启',
            offText='关闭'
        ),
        InputTime(
            label='云原神签到开始时间',
            name='云原神签到开始时间',
            value='${云原神签到开始时间}',
            labelRemark=Remark(shape='circle', content='会在每天这个时间点进行云原神自动签到，修改后重启生效'),
            inputFormat='HH时',
            timeFormat='HH',
            format='HH'
        ),
    ],
    actions=action_button)

ssbq_form = Form(
    title='实时便签',
    api='/LittlePaimon/api/set_config',
    visibleOn='${select == 4}',
    body=[
        Switch(
            label='实时便签检查开关',
            name='实时便签检查开关',
            value='${实时便签检查开关}',
            onText='开启',
            offText='关闭'
        ),
        InputTimeRange(
            label='实时便签停止检查时间段',
            name='实时便签停止检查时间段',
            value='${实时便签停止检查时间段}',
            labelRemark=Remark(shape='circle',
                               content='在这段时间(例如深夜)不进行实时便签检查，注意开始时间不要晚于结束时间，不然会有问题'),
            timeFormat='HH',
            format='HH',
            inputFormat='HH时'
        ),
        InputNumber(
            label='实时便签检查间隔',
            name='实时便签检查间隔',
            value='${实时便签检查间隔}',
            labelRemark=Remark(shape='circle', content='每多少分钟检查进行一次实时便签，推荐不快于8分钟，修改后重启生效'),
            displayMode='enhance',
            suffix='分钟',
            min=1,
        )
    ],
    actions=action_button
)

ys_form = Form(
    title='原神信息',
    api='/LittlePaimon/api/set_config',
    visibleOn='${select == 5}',
    body=[
        Alert(level='info',
              body='当这些指令原神信息数据最后更新时间距今已超过对应小时数时，就自动进行一次更新后再返回信息'),
        InputNumber(
            label='ys自动更新小时数',
            name='ys自动更新小时',
            value='${ys自动更新小时}',
            displayMode='enhance',
            suffix='小时',
            min=1,
        ),
        InputNumber(
            label='ysa自动更新小时数',
            name='ysa自动更新小时',
            value='${ysa自动更新小时}',
            displayMode='enhance',
            suffix='小时',
            min=1,
        ),
        InputNumber(
            label='ysd自动更新小时数',
            name='ysd自动更新小时',
            value='${ysd自动更新小时}',
            displayMode='enhance',
            suffix='小时',
            min=1,
        )
    ],
    actions=action_button
)
notice_form = Form(
    title='好友和群事件',
    api='/LittlePaimon/api/set_config',
    visibleOn='${select == 6}',
    body=[
        Switch(
            label='启用好友和群请求通知',
            name='启用好友和群请求通知',
            value='${启用好友和群请求通知}',
            labelRemark=Remark(shape='circle', content='开启后，会在机器人收到好友或群添加、拉群等请求时向超管发消息'),
            onText='开启',
            offText='关闭'
        ),
        Switch(
            label='自动接受好友请求',
            name='自动接受好友请求',
            value='${自动接受好友请求}',
            labelRemark=Remark(shape='circle', content='开启后，机器人会自动接受所有好友请求'),
            onText='开启',
            offText='关闭'
        ),
        Switch(
            label='自动接受群邀请',
            name='自动接受群邀请',
            value='${自动接受群邀请}',
            labelRemark=Remark(shape='circle', content='开启后，机器人会自动接受所有拉群请求'),
            onText='开启',
            offText='关闭'
        ),
        Switch(
            label='启用好友和群欢迎消息',
            name='启用好友和群欢迎消息',
            value='${启用好友和群欢迎消息}',
            labelRemark=Remark(shape='circle', content='开启后，会向新添加的好友以及新进入的群发送欢迎消息'),
            onText='开启',
            offText='关闭'
        ),
    ],
    actions=action_button
)
other_form = Form(
    title='其他配置',
    api='/LittlePaimon/api/set_config',
    visibleOn='${select == 7}',
    body=[
        Switch(
            label='图片资源缓存',
            name='图片资源缓存开关',
            value='${图片资源缓存开关}',
            labelRemark=Remark(shape='circle',
                               content='开启时，会将制图所需的图片资源加载到内存中进行缓存，以提高制图速度，如果机器内存较小，建议关闭'),
            onText='开启',
            offText='关闭'
        ),
        InputTag(
                label='启用重启时修改群名片群列表',
                name='启用重启时修改群名片群列表',
                value='${启用重启时修改群名片群列表}',
                enableBatchAdd=True,
                placeholder='添加启用群名片修改的群号',
                joinValues=False, 
                extractValue=True,
                labelRemark=Remark(shape='circle', content='这些群会在重启时在bot自己的群名片中增加"重启中"作为提示，在重启完成后修改回来')
        ),
        Switch(
            label='网页截图权限',
            name='启用网页截图权限',
            value='${启用网页截图权限}',
            labelRemark=Remark(shape='circle', content='开启后，任何人都能使用网页截图，关闭后则只有超管能使用'),
            onText='所有人',
            offText='仅超级用户'
        ),
        Switch(
            label='原神绑定二维码发送形式',
            name='绑定二维码以链接形式发送',
            value='${绑定二维码以链接形式发送}',
            labelRemark=Remark(shape='circle', content='选择原神绑定二维码的发送形式(直接图片发送或者链接形式发送)'),
            onText='链接',
            offText='图片'
        ),
        InputNumber(
            label='原神猜语音时间',
            name='原神猜语音时间',
            value='${原神猜语音时间}',
            labelRemark=Remark(shape='circle', content='原神猜语音小游戏的持续时间'),
            displayMode='enhance',
            suffix='秒',
            min=5,
        ),
        InputText(
            label='早报60s',
            name='早报60s',
            value='${早报60s}',
            placeholder='请填写早报60s的API地址',
            labelRemark=Remark(shape='circle', content='修改早报60s的API地址，不填则使用默认地址')
        ),
        Select(
            label='github资源地址',
            name='github资源地址',
            value='${github资源地址}',
            labelRemark=Remark(shape='circle',
                               content='本bot部分资源托管在github，如果下载缓慢或无法正常访问，可以尝试更换地址，或者添加你自己的代理地址，注意最后要有/'),
            creatable=True,
            options=[
                {
                    'label': 'ghproxy.com代理',
                    'value': 'https://ghproxy.com/'
                },
                {
                    'label': 'github.cherishmoon.fun代理',
                    'value': 'https://github.cherishmoon.fun/'
                },
                {
                    'label': 'github.91chi.fun代理',
                    'value': 'https://github.91chi.fun/'
                },
                {
                    'label': 'github原地址',
                    'value': ''
                }
            ]
        )
    ],
    actions=action_button
)

nonebot_form = Form(
    title='Nonebot配置',
    initApi='get:/LittlePaimon/api/env_config?file_name=${file_name}',
    api='post:/LittlePaimon/api/env_config?file_name=${file_name}',
    visibleOn='${select == 8}',
    body=[
        Select(
            name='file_name',
            label='选择文件',
            value='.env.prod',
            options=[
                {
                    'label': '.env',
                    'value': '.env'
                },
                {
                    'label': '.env.prod',
                    'value': '.env.prod'
                },
                {
                    'label': '.env.dev',
                    'value': '.env.dev'
                }
            ]
        ),
        Editor(
            name='editor',
            label='编辑',
            value='${data}',
            placeholder='暂无内容'
        )
    ],
    actions=[action_button[0]]
)

select = Select(label='选择配置类',
                size='sm',
                name='select',
                value=1,
                options=[
                    {
                        'label': 'Web端配置',
                        'value': 1},
                    {
                        'label': '模拟抽卡',
                        'value': 2},
                    {
                        'label': '自动任务',
                        'value': 3
                    },
                    {
                        'label': '实时便签',
                        'value': 4
                    },
                    {
                        'label': '原神信息',
                        'value': 5
                    },
                    {
                        'label': '好友和群事件',
                        'value': 6
                    },
                    {
                        'label': '其他配置',
                        'value': 7
                    },
                    {
                        'label': 'Nonebot配置',
                        'value': 8
                    }
                ])
page = PageSchema(url='/bot_config/configs', icon='fa fa-wrench', label='配置项管理',
                  schema=Page(title='配置项管理', initApi='/LittlePaimon/api/get_config',
                              body=[select, cookie_web_form, sim_gacha_form, auto_mys_form, ssbq_form, ys_form,
                                    notice_form, other_form, nonebot_form]))
