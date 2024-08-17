# 文件目录
MI18N_PATH = "./data/mi18n"
CONFIG_FILE_PATH = "./config.yaml"
CONFIG_FILE_JSON_PATH = "./data/config.json"
GEOIP2_DB_PATH = "./data/GeoLite2-Country.mmdb"

DISPATCH_KEY = "./data/key/bins/dispatchkey.bin"
DISPATCH_SEED = "./data/key/bins/dispatchseed.bin"

GACHA_TEXTMAP_PATH = "./data/gacha/textmap"
GACHA_SCHEDULE_PATH = "./data/gacha/schedule"

SHOPWINDOW_TIERS_PATH_CN = "./data/shopwindow/cn/tiers_cn.json"
SHOPWINDOW_PAY_TYPES_PATH_CN = "./data/shopwindow/cn/pay_types_cn.json"
SHOPWINDOW_TIERS_PATH_OS = "./data/shopwindow/os/tiers_os.json"
SHOPWINDOW_PAY_TYPES_PATH_OS = "./data/shopwindow/os/pay_types_os.json"

ANNOUNCE_BLUE_PATH = "./data/announce/zh-cn.json"
ANNOUNCE_FONT_PATH = "./data/announce/font.json"
ANNOUNCE_JS_PATH1 = "./data/static/js/announce/2_2e4d2779ad3d19e6406f.js"
ANNOUNCE_JS_PATH2 = "./data/static/js/announce/vendors_3230378b06826ebc94d3.js"
ANNOUNCE_JS_PATH3 = "./data/static/js/announce/bundle_9f9d2fd05b63fd8decfc.js"
ANNOUNCE_CSS_PATH1 = "./data/static/css/announce/2_cb04d2d72d7555e2ab83.css"
ANNOUNCE_CSS_PATH2 = "./data/static/css/announce/bundle_dad917ca6970b9fa0ec0.css"
ANNOUNCE_MAINJS_PATH = "./data/static/js/announce/main.js"
ANNOUNCE_VUEMIN_PATH = "./data/static/js/announce/vue.min.js"
ANNOUNCE_MAINH5JS_PATH = "./data/static/js/announce/main-h5log.js"
ANNOUNCE_FPTJS_PATH = "./data/static/js/announce/firebase-performance-standalone.js"

CB_LOGIN_FONT_PATH_01 = (
    "./data/static/fonts/2c148f36573625fc03c82579abd26fb1_1167469228143141125.ttf"
)
CB_LOGIN_FONT_PATH_02 = (
    "./data/static/fonts/4398dec1a0ffa3d3ce99ef1424107550_4765013443347169028.ttf"
)

# 账号类型
ACCOUNT_TYPE_GUEST = 0
ACCOUNT_TYPE_NORMAL = 1

# 官服 B服
CHANNEL_ID_MIHOYO = 1
CHANNEL_ID_BILIBILI = 14

# 登录场景
SCENE_NORMAL = "S_NORMAL"  # 手机号+用户名 默认手机号
SCENE_ACCOUNT = "S_ACCOUNT"  # 手机号+用户名 默认用户名
SCENE_USER = "S_USER"  # 仅账号
SCENE_TEMPLE = "S_TEMPLE"  # 仅账号 无需注册

# 客户端平台
PLATFORM_TYPE = {
    0: "EDITOR",
    1: "IOS",
    2: "ANDROID",
    3: "PC",
    4: "PS4",
    5: "SERVER",
    6: "CLOUD_ANDROID",
    7: "CLOUD_IOS",
    8: "PS5",
    9: "CLOUD_WEB",
    10: "CLOUD_TV",
    11: "CLOUD_MAC",
    12: "CLOUD_PC",
    13: "CLOUD_THIRD_PARTY_MOBILE",
    14: "CLOUD_THIRD_PARTY_PC",
}

# 返回的状态码
RES_SUCCESS = 0
RES_FAIL = -1
RES_CANCEL = -2
RES_NO_SUCH_METHOD = -10
RES_LOGIN_BASE = -100
RES_LOGIN_FAILED = -101
RES_LOGIN_CANCEL = -102
RES_LOGIN_ERROR = -103
RES_LOGOUT_FAILED = -104
RES_LOGOUT_CANCEL = -105
RES_LOGOUT_ERROR = 106
RES_PAY_FAILED = -107
RES_PAY_CANCEL = -108
RES_PAY_ERROR = -109
RES_PAY_LAUNCH = -120
RES_PAY_UNKNOWN = -116
RES_EXIT_FAILED = -110
RES_EXIT_NO_DIALOG = -111
RES_EXIT_CANCEL = -112
RES_EXIT_ERROR = -113
RES_INIT_FAILED = -114
RES_INIT_ERROR = -115
RES_LOGIN_FORBIDDED = -117
RES_NEED_REALNAME = -118
RES_NEED_GUARDIAN = -119
RES_EOS_DLL_ERROR = -1001
RES_EOS_TOKEN_ERROR = -1002
RES_GOOGLE_PC_TOKEN_ERROR = -1003
RES_CDK_EXCHANGE_SUCC = 0
RES_CDK_EXCHANGE_FAIL = -2003
RES_SDK_VERIFY_SUCC = 0
RES_SDK_VERIFY_FAIL = 1

# risky
RISKY_ACTION_NONE = "ACTION_NONE"

# Display
SDK_STATUS_SUCC = "\033[92m>> [succ] \033[0m"
SDK_STATUS_FAIL = "\033[91m>> [Error] \033[0m"
SDK_STATUS_WARING = "\033[91m>> [Waring] \033[0m"
