from pathlib import Path

# 资源路径
RESOURCE_BASE_PATH = Path() / 'resources' / 'LittlePaimon'
ARTIFACT = RESOURCE_BASE_PATH / 'artifact'
ARTIFACT.mkdir(parents=True, exist_ok=True)
AVATAR = RESOURCE_BASE_PATH / 'avatar'
AVATAR.mkdir(parents=True, exist_ok=True)
AVATAR_SIDE = RESOURCE_BASE_PATH / 'avatar_side'
AVATAR_SIDE.mkdir(parents=True, exist_ok=True)
TALENT = RESOURCE_BASE_PATH / 'talent'
TALENT.mkdir(parents=True, exist_ok=True)
WEAPON = RESOURCE_BASE_PATH / 'weapon'
WEAPON.mkdir(parents=True, exist_ok=True)
SPLASH = RESOURCE_BASE_PATH / 'splash'
SPLASH.mkdir(parents=True, exist_ok=True)

# 用户数据路径
USER_DATA_PATH = Path() / 'data' / 'LittlePaimon' / 'user_data'
USER_DATA_PATH.mkdir(parents=True, exist_ok=True)
DATABASE_PATH = Path().cwd() / 'data' / 'LittlePaimon' / 'database'
DATABASE_PATH.mkdir(parents=True, exist_ok=True)
# 数据库路径
GENSHIN_DB_PATH = DATABASE_PATH / 'genshin.db'
SUB_DB_PATH = DATABASE_PATH / 'subscription.db'
GENSHIN_VOICE_DB_PATH = DATABASE_PATH / 'genshin_voice.db'
MANAGER_DB_PATH = DATABASE_PATH / 'manager.db'
# enka制图资源路径
ENKA_RES = RESOURCE_BASE_PATH / 'enka_card'
# 原神表情路径
GEMO = RESOURCE_BASE_PATH / 'emoticons'
# 原神模拟抽卡资源路径
GACHA_RES = RESOURCE_BASE_PATH / 'gacha_res'
# 原神模拟抽卡记录数据路径
GACHA_SIM = USER_DATA_PATH / 'gacha_sim_data'
# 原神抽卡记录数据路径
GACHA_LOG = USER_DATA_PATH / 'gacha_log_data'
GACHA_LOG.mkdir(parents=True, exist_ok=True)
# 字体路径
FONTS_PATH = Path() / 'resources' / 'fonts'
FONTS_PATH.mkdir(parents=True, exist_ok=True)
# JSON数据路径
JSON_DATA = Path(__file__).parent.parent / 'config' / 'data'
# 插件管理器文件存放目录
PLUGIN_CONFIG = Path() / 'config' / 'plugins'
PLUGIN_CONFIG.mkdir(parents=True, exist_ok=True)
PAIMON_CONFIG = Path() / 'config' / 'paimon_config.yml'
# 问候语配置文件
GREET_CONFIG = Path() / 'config' / 'paimon_greet.yml'
GREET_CONFIG_DEFAULT = Path() / 'config' / 'paimon_greet_default.yml'
# 群聊学习配置文件
LEARNING_CHAT_CONFIG = Path() / 'config' / 'learning_chat.yml'
# 米游社帖子订阅文件，未用上
MIHOYO_BBS_POST_PATH = Path() / 'data' / 'LittlePaimon' / '米游社帖子订阅.json'
# ysc原图临时目录
YSC_TEMP_IMG_PATH = Path() / 'data' / 'LittlePaimon' / 'temp_img'
YSC_TEMP_IMG_PATH.mkdir(parents=True, exist_ok=True)


