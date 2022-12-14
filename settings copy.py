KEYWORD = "西安"  # 搜索内容
ACCOUNT = "+"  # 账号
PASSWORD = "?"  # 密码
ENV = "PRO"  # "PRO" "DEV"
MAX_INVALID_REFRESH_TIMES = 3 if ENV == "PRO" else 2
LOGGER_LEVEL = "INFO" if ENV == "PRO" else "DEBUG"
SLOW_MO_V = 0 if ENV == "PRO" else 100
HEAD_V = True if ENV == "PRO" else False
MAX_NUM_OF_QUESTIONS = 99 if ENV == "PRO" else 10
MAX_NUM_OF_ANSWERS = 999000 if ENV == "PRO" else 10
USER_INFO_TITLE = [
    '昵称', '性别', '签名', 'ip属地', '居住地', '所在行业', '职业经历', '教育经历', '个人简介', '认证',
    '获得', '参与', '知乎', '关注了', '关注者', '主页', '状态'
]
