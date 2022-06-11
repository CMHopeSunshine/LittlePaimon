# # 点餐功能
# from .order import *
#
# # 新闻功能
# from .news import *
#
# # 随机图片功能
# from .random_img import *
#
# # 处理好友和群请求功能
# from .auto_handle import *
#
# # 对联功能
# from .couplets import *
#
# from .help import help_


# 如果不需要某项功能，将其from xx import * 注释掉即可

from nonebot import load_plugins
import os
load_plugins(os.path.dirname(__file__))





