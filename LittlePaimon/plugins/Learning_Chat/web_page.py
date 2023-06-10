from amis import ColumnList, AmisList, ActionType, TableCRUD, TableColumn
from amis import Dialog, PageSchema, Page, Switch, Remark, InputNumber, InputTag, Action
from amis import Form, LevelEnum, Select, InputArray, Alert
from LittlePaimon.utils import NICKNAME
from LittlePaimon.web.pages import admin_app

global_config_form = Form(
    title="全局配置",
    name="global_config",
    initApi="/LittlePaimon/api/chat_global_config",
    api="post:/LittlePaimon/api/chat_global_config",
    interval=None,
    body=[
        Switch(
            label="群聊学习总开关",
            name="total_enable",
            value="${total_enable}",
            onText="开启",
            offText="关闭",
            labelRemark=Remark(
                shape="circle", content="关闭后，全局都将不会再学习和回复(但是仍会对收到的消息进行记录)。"
            ),
        ),
        InputNumber(
            label="单句关键词数量",
            name="KEYWORDS_SIZE",
            value="${KEYWORDS_SIZE}",
            visibleOn="${total_enable}",
            min=2,
            labelRemark=Remark(
                shape="circle", content="单句语句标签数量，影响对一句话的主题词提取效果，建议保持默认为3。"
            ),
        ),
        InputNumber(
            label="跨群回复阈值",
            name="cross_group_threshold",
            value="${cross_group_threshold}",
            visibleOn="${total_enable}",
            min=1,
            labelRemark=Remark(
                shape="circle", content="当学习到的一种回复在N个群都有，那么这个回复就会变为全局回复。"
            ),
        ),
        InputNumber(
            label="最高学习次数",
            name="learn_max_count",
            value="${learn_max_count}",
            visibleOn="${total_enable}",
            min=2,
            labelRemark=Remark(
                shape="circle",
                content="学习的回复最高能累计到的次数，值越高，这个回复就会学习得越深，越容易进行回复，如果不想每次都大概率固定回复某一句话，可以将该值设低点。",
            ),
        ),
        InputTag(
            label="全局屏蔽词",
            name="ban_words",
            value="${ban_words}",
            enableBatchAdd=True,
            placeholder="添加全局屏蔽词",
            visibleOn="${total_enable}",
            joinValues=False,
            extractValue=True,
            labelRemark=Remark(
                shape="circle",
                content="全局屏蔽词，含有这些词的消息不会学习和回复，默认已屏蔽at、分享、语音、和视频等消息。(回车进行添加)",
            ),
        ),
        InputTag(
            label="全局屏蔽用户",
            source="${member_list}",
            name="ban_users",
            value="${ban_users}",
            enableBatchAdd=True,
            placeholder="添加全局屏蔽用户",
            visibleOn="${total_enable}",
            joinValues=False,
            extractValue=True,
            labelRemark=Remark(
                shape="circle", content="全局屏蔽用户，和这些用户有关的消息不会学习和回复。(回车进行添加)"
            ),
        ),
        InputTag(
            label="自定义词典",
            name="dictionary",
            value="${dictionary}",
            enableBatchAdd=True,
            placeholder="添加自定义词语",
            visibleOn="${total_enable}",
            joinValues=False,
            extractValue=True,
            labelRemark=Remark(
                shape="circle",
                content="添加自定义词语，让分词能够识别未收录的词汇，提高学习的准确性。你可以添加特殊名词，这样学习时就会将该词看作一个整体，目前词典中已默认添加部分原神相关词汇。(回车进行添加)",
            ),
        ),
    ],
    actions=[
        Action(label="保存", level=LevelEnum.success, type="submit"),
        Action(label="重置", level=LevelEnum.warning, type="reset"),
    ],
)
group_select = Select(
    label="分群配置", name="group_id", source="${group_list}", placeholder="选择群"
)
group_config_form = Form(
    title="分群配置",
    visibleOn="group_id != null",
    initApi="/LittlePaimon/api/chat_group_config?group_id=${group_id}",
    api="post:/LittlePaimon/api/chat_group_config?group_id=${group_id}",
    interval=None,
    body=[
        Switch(
            label="群聊学习开关",
            name="enable",
            value="${enable}",
            onText="开启",
            offText="关闭",
            labelRemark=Remark(shape="circle", content="针对该群的群聊学习开关，关闭后，仅该群不会学习和回复。"),
        ),
        InputNumber(
            label="回复阈值",
            name="answer_threshold",
            value="${answer_threshold}",
            visibleOn="${enable}",
            min=2,
            labelRemark=Remark(shape="circle", content="可以理解为学习成功所需要的次数，值越低学得越快。"),
        ),
        InputArray(
            label="回复阈值权重",
            name="answer_threshold_weights",
            value="${answer_threshold_weights}",
            items=InputNumber(min=1, max=100, value=25, suffix="%"),
            inline=True,
            visibleOn="${enable}",
            labelRemark=Remark(
                shape="circle",
                content="影响回复阈值的计算方式，以默认的回复阈值4、权重[10, 30, 60]为例，在计算阈值时，60%概率为4，30%概率为3，10%概率为2。",
            ),
        ),
        InputNumber(
            label="复读阈值",
            name="repeat_threshold",
            value="${repeat_threshold}",
            visibleOn="${enable}",
            min=2,
            labelRemark=Remark(
                shape="circle", content=f"跟随复读所需要的阈值，有N个人复读后，{NICKNAME}就会跟着复读。"
            ),
        ),
        InputNumber(
            label="打断复读概率",
            name="break_probability",
            value="${break_probability}",
            min=0,
            max=100,
            suffix="%",
            visibleOn="${AND(enable, speak_enable)}",
            labelRemark=Remark(shape="circle", content="达到复读阈值时，打断复读而不是跟随复读的概率。"),
        ),
        InputTag(
            label="屏蔽词",
            name="ban_words",
            value="${ban_words}",
            enableBatchAdd=True,
            placeholder="添加屏蔽词",
            visibleOn="${enable}",
            joinValues=False,
            extractValue=True,
            labelRemark=Remark(shape="circle", content="含有这些词的消息不会学习和回复。(回车进行添加)"),
        ),
        InputTag(
            label="屏蔽用户",
            source="${member_list}",
            name="ban_users",
            value="${ban_users}",
            enableBatchAdd=True,
            placeholder="添加屏蔽用户",
            visibleOn="${enable}",
            joinValues=False,
            extractValue=True,
            labelRemark=Remark(shape="circle", content="和该群中这些用户有关的消息不会学习和回复。(回车进行添加)"),
        ),
        Switch(
            label="主动发言开关",
            name="speak_enable",
            value="${speak_enable}",
            visibleOn="${enable}",
            labelRemark=Remark(
                shape="circle",
                content=f"是否允许{NICKNAME}在该群主动发言，主动发言是指每隔一段时间挑选一个热度较高的群，主动发一些学习过的内容。",
            ),
        ),
        InputNumber(
            label="主动发言阈值",
            name="speak_threshold",
            value="${speak_threshold}",
            visibleOn="${AND(enable, speak_enable)}",
            min=0,
            labelRemark=Remark(shape="circle", content="值越低，主动发言的可能性越高。"),
        ),
        InputNumber(
            label="主动发言最小间隔",
            name="speak_min_interval",
            value="${speak_min_interval}",
            min=0,
            visibleOn="${AND(enable, speak_enable)}",
            suffix="秒",
            labelRemark=Remark(shape="circle", content="进行主动发言的最小时间间隔。"),
        ),
        InputNumber(
            label="连续主动发言概率",
            name="speak_continuously_probability",
            value="${speak_continuously_probability}",
            min=0,
            max=100,
            suffix="%",
            visibleOn="${AND(enable, speak_enable)}",
            labelRemark=Remark(shape="circle", content="触发主动发言时，连续进行发言的概率。"),
        ),
        InputNumber(
            label="最大连续主动发言句数",
            name="speak_continuously_max_len",
            value="${speak_continuously_max_len}",
            visibleOn="${AND(enable, speak_enable)}",
            min=1,
            labelRemark=Remark(shape="circle", content="连续主动发言的最大句数。"),
        ),
        InputNumber(
            label="主动发言附带戳一戳概率",
            name="speak_poke_probability",
            value="${speak_poke_probability}",
            min=0,
            max=100,
            suffix="%",
            visibleOn="${AND(enable, speak_enable)}",
            labelRemark=Remark(
                shape="circle", content="主动发言时附带戳一戳的概率，会在最近5个发言者中随机选一个戳。"
            ),
        ),
    ],
    actions=[
        Action(label="保存", level=LevelEnum.success, type="submit"),
        ActionType.Ajax(
            label="保存至所有群",
            level=LevelEnum.primary,
            confirmText="确认将当前配置保存至所有群？",
            api="post:/LittlePaimon/api/chat_group_config?group_id=all",
        ),
        Action(label="重置", level=LevelEnum.warning, type="reset"),
    ],
)

blacklist_table = TableCRUD(
    mode="table",
    title="",
    syncLocation=False,
    api="/LittlePaimon/api/get_chat_blacklist",
    interval=15000,
    headerToolbar=[
        ActionType.Ajax(
            label="取消所有禁用",
            level=LevelEnum.warning,
            confirmText="确定要取消所有禁用吗？",
            api="put:/LittlePaimon/api/delete_all?type=blacklist",
        )
    ],
    itemActions=[
        ActionType.Ajax(
            tooltip="取消禁用",
            icon="fa fa-check-circle-o text-info",
            confirmText="取消该被禁用的内容/关键词，但是仍然需要重新学习哦！",
            api="delete:/LittlePaimon/api/delete_chat?type=blacklist&id=${id}",
        )
    ],
    footable=True,
    columns=[
        TableColumn(
            type="tpl",
            tpl="${keywords|truncate:20}",
            label="内容/关键词",
            name="keywords",
            searchable=True,
            popOver={
                "mode": "dialog",
                "title": "全文",
                "className": "break-all",
                "body": {"type": "tpl", "tpl": "${keywords}"},
            },
        ),
        TableColumn(label="已禁用的群", name="bans", searchable=True),
    ],
)
message_table = TableCRUD(
    mode="table",
    title="",
    syncLocation=False,
    api="/LittlePaimon/api/get_chat_messages",
    interval=12000,
    headerToolbar=[
        ActionType.Ajax(
            label="删除所有聊天记录",
            level=LevelEnum.warning,
            confirmText="确定要删除所有聊天记录吗？",
            api="put:/LittlePaimon/api/delete_all?type=message",
        )
    ],
    itemActions=[
        ActionType.Ajax(
            tooltip="禁用",
            icon="fa fa-ban text-danger",
            confirmText="禁用该聊天记录相关的学习内容和回复",
            api="put:/LittlePaimon/api/ban_chat?type=message&id=${id}",
        ),
        ActionType.Ajax(
            tooltip="删除",
            icon="fa fa-times text-danger",
            confirmText="删除该条聊天记录",
            api="delete:/LittlePaimon/api/delete_chat?type=message&id=${id}",
        ),
    ],
    footable=True,
    columns=[
        TableColumn(label="消息ID", name="message_id"),
        TableColumn(label="群ID", name="group_id", searchable=True),
        TableColumn(label="用户ID", name="user_id", searchable=True),
        TableColumn(
            type="tpl",
            tpl="${raw_message|truncate:20}",
            label="消息",
            name="message",
            searchable=True,
            popOver={
                "mode": "dialog",
                "title": "消息全文",
                "className": "break-all",
                "body": {"type": "tpl", "tpl": "${raw_message}"},
            },
        ),
        TableColumn(
            type="tpl",
            tpl="${time|date:YYYY-MM-DD HH\\:mm\\:ss}",
            label="时间",
            name="time",
            sortable=True,
        ),
    ],
)
answer_table = TableCRUD(
    mode="table",
    syncLocation=False,
    footable=True,
    api="/LittlePaimon/api/get_chat_answers",
    interval=12000,
    headerToolbar=[
        ActionType.Ajax(
            label="删除所有已学习的回复",
            level=LevelEnum.warning,
            confirmText="确定要删除所有已学习的回复吗？",
            api="put:/LittlePaimon/api/delete_all?type=answer",
        )
    ],
    itemActions=[
        ActionType.Ajax(
            tooltip="禁用",
            icon="fa fa-ban text-danger",
            confirmText="禁用并删除该已学回复",
            api="put:/LittlePaimon/api/ban_chat?type=answer&id=${id}",
        ),
        ActionType.Ajax(
            tooltip="删除",
            icon="fa fa-times text-danger",
            confirmText="仅删除该已学回复，不会禁用，所以依然能继续学",
            api="delete:/LittlePaimon/api/delete_chat?type=answer&id=${id}",
        ),
    ],
    columns=[
        TableColumn(label="ID", name="id", visible=False),
        TableColumn(label="群ID", name="group_id", searchable=True),
        TableColumn(
            type="tpl",
            tpl="${keywords|truncate:20}",
            label="内容/关键词",
            name="keywords",
            searchable=True,
            popOver={
                "mode": "dialog",
                "title": "内容全文",
                "className": "break-all",
                "body": {"type": "tpl", "tpl": "${keywords}"},
            },
        ),
        TableColumn(
            type="tpl",
            tpl="${time|date:YYYY-MM-DD HH\\:mm\\:ss}",
            label="最后学习时间",
            name="time",
            sortable=True,
        ),
        TableColumn(label="次数", name="count", sortable=True),
        ColumnList(
            label="完整消息",
            name="messages",
            breakpoint="*",
            source="${messages}",
            listItem=AmisList.Item(body=[AmisList.Item.ListBodyField(name="msg")]),
        ),
    ],
)
answer_table_on_context = TableCRUD(
    mode="table",
    syncLocation=False,
    footable=True,
    api="/LittlePaimon/api/get_chat_answers?context_id=${id}&page=${page}&perPage=${perPage}&orderBy=${orderBy}&orderDir=${orderDir}",
    interval=12000,
    headerToolbar=[
        ActionType.Ajax(
            label="删除该内容所有回复",
            level=LevelEnum.warning,
            confirmText="确定要删除该条内容已学习的回复吗？",
            api="put:/LittlePaimon/api/delete_all?type=answer&id=${id}",
        )
    ],
    itemActions=[
        ActionType.Ajax(
            tooltip="禁用",
            icon="fa fa-ban text-danger",
            confirmText="禁用并删除该已学回复",
            api="put:/LittlePaimon/api/ban_chat?type=answer&id=${id}",
        ),
        ActionType.Ajax(
            tooltip="删除",
            icon="fa fa-times text-danger",
            confirmText="仅删除该已学回复，但不禁用，依然能继续学",
            api="delete:/LittlePaimon/api/delete_chat?type=answer&id=${id}",
        ),
    ],
    columns=[
        TableColumn(label="ID", name="id", visible=False),
        TableColumn(label="群ID", name="group_id"),
        TableColumn(
            type="tpl",
            tpl="${keywords|truncate:20}",
            label="内容/关键词",
            name="keywords",
            searchable=True,
            popOver={
                "mode": "dialog",
                "title": "内容全文",
                "className": "break-all",
                "body": {"type": "tpl", "tpl": "${keywords}"},
            },
        ),
        TableColumn(
            type="tpl",
            tpl="${time|date:YYYY-MM-DD HH\\:mm\\:ss}",
            label="最后学习时间",
            name="time",
            sortable=True,
        ),
        TableColumn(label="次数", name="count", sortable=True),
        ColumnList(
            label="完整消息",
            name="messages",
            breakpoint="*",
            source="${messages}",
            listItem=AmisList.Item(body=[AmisList.Item.ListBodyField(name="msg")]),
        ),
    ],
)
context_table = TableCRUD(
    mode="table",
    title="",
    syncLocation=False,
    api="/LittlePaimon/api/get_chat_contexts",
    interval=12000,
    headerToolbar=[
        ActionType.Ajax(
            label="删除所有学习内容",
            level=LevelEnum.warning,
            confirmText="确定要删除所有已学习的内容吗？",
            api="put:/LittlePaimon/api/delete_all?type=context",
        )
    ],
    itemActions=[
        ActionType.Dialog(
            tooltip="回复列表",
            icon="fa fa-book text-info",
            dialog=Dialog(title="回复列表", size="lg", body=answer_table_on_context),
        ),
        ActionType.Ajax(
            tooltip="禁用",
            icon="fa fa-ban text-danger",
            confirmText="禁用并删除该学习的内容及其所有回复",
            api="put:/LittlePaimon/api/ban_chat?type=context&id=${id}",
        ),
        ActionType.Ajax(
            tooltip="删除",
            icon="fa fa-times text-danger",
            confirmText="仅删除该学习的内容及其所有回复，但不禁用，依然能继续学",
            api="delete:/LittlePaimon/api/delete_chat?type=context&id=${id}",
        ),
    ],
    footable=True,
    columns=[
        TableColumn(label="ID", name="id", visible=False),
        TableColumn(
            type="tpl",
            tpl="${keywords|truncate:20}",
            label="内容/关键词",
            name="keywords",
            searchable=True,
            popOver={
                "mode": "dialog",
                "title": "内容全文",
                "className": "break-all",
                "body": {"type": "tpl", "tpl": "${keywords}"},
            },
        ),
        TableColumn(
            type="tpl",
            tpl="${time|date:YYYY-MM-DD HH\\:mm\\:ss}",
            label="最后学习时间",
            name="time",
            sortable=True,
        ),
        TableColumn(label="已学次数", name="count", sortable=True),
    ],
)

message_page = PageSchema(
    url="/chat/messages",
    icon="fa fa-comments",
    label="群聊消息",
    schema=Page(
        title="群聊消息",
        body=[
            Alert(
                level=LevelEnum.info,
                className="white-space-pre-wrap",
                body=(
                    f"此数据库记录了{NICKNAME}收到的除指令外的聊天记录。\n"
                    '· 点击"禁用"可以将某条聊天记录进行禁用，这样其相关的学习就会列入禁用列表。\n'
                    '· 点击"删除"可以删除某条记录，但不会影响它的学习。\n'
                    f"· 可以通过搜索{NICKNAME}的QQ号，来查看它的回复记录。"
                ),
            ),
            message_table,
        ],
    ),
)
context_page = PageSchema(
    url="/chat/contexts",
    icon="fa fa-comment",
    label="学习内容",
    schema=Page(
        title="内容",
        body=[
            Alert(
                level=LevelEnum.info,
                className="white-space-pre-wrap",
                body=(
                    f"此数据库记录了{NICKNAME}所学习的内容。\n"
                    '· 点击"回复列表"可以查看该条内容已学习到的可能的回复。\n'
                    '· 点击"禁用"可以将该学习进行禁用，以后不会再学。\n'
                    '· 点击"删除"可以删除该学习，让它重新开始学习这句话。'
                ),
            ),
            context_table,
        ],
    ),
)
answer_page = PageSchema(
    url="/chat/answers",
    icon="fa fa-commenting-o",
    label="内容回复",
    schema=Page(
        title="回复",
        body=[
            Alert(
                level=LevelEnum.info,
                className="white-space-pre-wrap",
                body=(
                    f'此数据库记录了{NICKNAME}已学习到的所有回复，但看不到这些回复属于哪些内容，推荐到"学习内容"表进行操作。\n'
                    '· 点击"禁用"可以将该回复进行禁用，以后不会再学。\n'
                    '· 点击"删除"可以删除该回复，让它重新开始学习。'
                ),
            ),
            answer_table,
        ],
    ),
)
blacklist_page = PageSchema(
    url="/chat/blacklist",
    icon="fa fa-ban",
    label="禁用列表",
    schema=Page(
        title="禁用列表",
        interval=60000,
        body=[
            Alert(
                level=LevelEnum.info,
                className="white-space-pre-wrap",
                body=f"此数据库记录了{NICKNAME}被禁用的内容/关键词。\n"
                "· 可以取消禁用，使其能够重新继续学习。\n"
                "· 不能在此添加禁用，只能在群中回复[不可以]或者在<配置>中添加屏蔽词来达到禁用效果。",
            ),
            blacklist_table,
        ],
    ),
)
database_page = PageSchema(
    label="数据库",
    icon="fa fa-database",
    children=[message_page, context_page, answer_page, blacklist_page],
)
config_page = PageSchema(
    url="/chat/configs",
    icon="fa fa-wrench",
    label="配置",
    schema=Page(
        title="配置",
        initApi="/LittlePaimon/api/get_group_list",
        body=[global_config_form, group_select, group_config_form],
    ),
)
chat_page = PageSchema(
    label="群聊学习", icon="fa fa-wechat (alias)", children=[config_page, database_page]
)
admin_app.pages[0].children.append(chat_page)
