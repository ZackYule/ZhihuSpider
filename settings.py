KEYWORD = "找对象"  # 搜索内容
ACCOUNT = "+86176xxxxxxxx"  # 账号
PASSWORD = "xxxxxxx"  # 密码
ENV = "PRO" # "PRO" "DEV"
MAX_REFRESH_TIMES = 3 if ENV == "PRO" else 1
LOGGER_LEVEL = "INFO" if ENV == "PRO" else "DEBUG"
SLOW_MO_V = 0 if ENV == "PRO" else 100
HEAD_V = True if ENV == "PRO" else False