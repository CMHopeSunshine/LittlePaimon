from .zhongli import draw_zhongli_dmg
from .hutao import draw_hutao_dmg
from .leishen import draw_leishen_dmg
from .xiao import draw_xiao_dmg
from .xiangling import draw_xiangling_dmg
from .shenhe import draw_shenhe_dmg

# 支持的角色列表
roles_list = {
    '钟离': draw_zhongli_dmg,
    '胡桃': draw_hutao_dmg,
    '雷电将军': draw_leishen_dmg,
    '魈': draw_xiao_dmg,
    '香菱': draw_xiangling_dmg,
    '申鹤': draw_shenhe_dmg
}


def get_role_dmg(role_name: str, data: dict):
    if role_name in roles_list:
        return roles_list[role_name](data)
    else:
        return None
