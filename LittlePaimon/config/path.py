from pathlib import Path

# 资源路径
RESOURCE_BASE_PATH = Path() / 'resources' / 'LittlePaimon'
RESOURCE_BASE_PATH.mkdir(parents=True, exist_ok=True)
# 用户数据路径
DATA_BASE_PATH = Path() / 'data' / 'LittlePaimon' / 'user_data'
DATA_BASE_PATH.mkdir(parents=True, exist_ok=True)
# 数据库路径
DB_PATH = Path().cwd() / 'data' / 'LittlePaimon' / 'user_data' / 'paimon_db.db'
# enka用户数据路径
ENKA_INFO = DATA_BASE_PATH / 'player_info'
# enka制图资源路径
ENKA_RES = RESOURCE_BASE_PATH / 'enka_card'
# 原神表情路径
GEMO = RESOURCE_BASE_PATH / 'emoticons'
# 原神模拟抽卡资源路径
GACHA_RES = RESOURCE_BASE_PATH / 'gacha_res'
# 原神模拟抽卡记录数据路径
GACHA_SIM = DATA_BASE_PATH / 'gacha_sim_data'
# 原神抽卡记录数据路径
GACHA_LOG = DATA_BASE_PATH / 'gacha_log_data'
# 字体路径
FONTS_PATH = Path() / 'resources' / 'fonts'
FONTS_PATH.mkdir(parents=True, exist_ok=True)
# JSON数据路径
JSON_DATA = Path(__file__).parent / 'data'
# TEMP临时下载资源路径
TEMP = RESOURCE_BASE_PATH / 'temp'

# 插件管理器文件存放目录
PLUGINMANAGER = Path() / 'data' / 'LittlePaimon' / 'manager' / 'plugins.yaml'



# class PathManager:
#     def __init__(self):
#         self.paths = {
#             'resources': RESOURCE_BASE_PATH,
#             'enka_info': DATA_BASE_PATH / 'player_info',
#             'enka':      RESOURCE_BASE_PATH / 'enka_card',
#             'database':  DATA_BASE_PATH / 'user_data.db',
#             'emoticons': RESOURCE_BASE_PATH / 'emoticons',
#             'blue':      RESOURCE_BASE_PATH / 'blue',
#             'gacha':     RESOURCE_BASE_PATH / 'gacha_res',
#             'skill':     RESOURCE_BASE_PATH / 'temp' / 'skill',
#             'talent':    RESOURCE_BASE_PATH / 'temp' / 'talent',
#             'artifact':  RESOURCE_BASE_PATH / 'temp' / 'artifact',
#             'weapon':    RESOURCE_BASE_PATH / 'temp' / 'weapon',
#             'fonts':     RESOURCE_BASE_PATH / 'fonts',
#             'json':      Path(__file__).parent / 'data',
#         }
#
#     def get(self, name: str) -> Path:
#         name = name.lower()
#         if name not in self.paths:
#             raise KeyError(f'{name} is not in path manager')
#         return self.paths[name]
#
#     def set(self, name: str, path: Path):
#         name = name.lower()
#         self.paths[name] = path
#
#
# path_manager = PathManager()
