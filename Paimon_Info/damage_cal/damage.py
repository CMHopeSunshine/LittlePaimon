from .zhongli import draw_zhongli_dmg
from .hutao import draw_hutao_dmg
from .leishen import draw_leishen_dmg

# 支持的角色列表
roles_list = {
    '钟离': draw_zhongli_dmg,
    '胡桃': draw_hutao_dmg,
    '雷电将军': draw_leishen_dmg
}


def get_role_dmg(role_name: str, data: dict):
    if role_name in roles_list:
        return roles_list[role_name](data)
    else:
        return None
