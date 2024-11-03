try:
    from __main__ import app
except ImportError:
    from main import app

import src.tools.repositories   as repositories

from flask                      import request
from src.tools.loadconfig       import loadConfig
from src.tools.response         import jsonRsp, jsonRspWithMsg
from src.tools.logger.system    import logger                   as sys_log

# ===================== Api功能 ===================== #
# Api-Config(https://sandbox-sdk-os.hoyoverse.com)
@app.route("/combo/granter/api/loadConfig", methods=["GET"])
@app.route("/hk4e_cn/combo/granter/api/loadConfig", methods=["GET"])
@app.route("/hk4e_global/combo/granter/api/loadConfig", methods=["GET"])
def combo_granter_api_config():
    return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{
            "data": {
                "log_level": "INFO",
                "announce_url": "https://sdk.hoyoverse.com/hk4e/announcement/index.html?sdk_presentation_style=fullscreen\u0026announcement_version=1.40\u0026sdk_screen_transparent=true\u0026game_biz=hk4e_global\u0026auth_appid=announcement\u0026game=hk4e#/",
                "disable_ysdk_guard": loadConfig()["Player"]["disable_ysdk_guard"],
                "enable_announce_pic_popup": loadConfig()["Player"]["enable_announce_pic_popup"],
                "protocol": loadConfig()["Player"]["protocol"],
                "qr_enabled": loadConfig()["Player"]["qr_enabled"],
                "app_name": "原神",
                "qr_enabled_apps": {
                    "bbs": loadConfig()["Player"]["qr_bbs"],
                    "cloud": loadConfig()["Player"]["qr_cloud"],
                },
                "qr_app_icons": {"app": "", "bbs": "", "cloud": ""},
                "qr_cloud_display_name": "云·原神",
                "enable_user_center": loadConfig()["Player"]["enable_user_center"],
                "functional_switch_configs": {},
            }
        },
    )


# 登录相关
@app.route("/mdk/shield/api/loadConfig", methods=["GET", "POST"])
@app.route("/hk4e_cn/mdk/shield/api/loadConfig", methods=["GET", "POST"])
@app.route("/hk4e_global/mdk/shield/api/loadConfig", methods=["GET", "POST"])
def mdk_shield_api_loadConfig():
    client = request.args.get("client", "")  # 提供默认值为空字符串
    game_key = request.args.get("game_key")
    sys_log.info(f"主机 {request.remote_addr} 获取登录页配置: 平台: {client} 客户端类型: {game_key}")

    if client.isdigit():
        client = repositories.PLATFORM_TYPE[int(client)]
    return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{
            "data": {
                "id": 6,
                "game_key": game_key,
                "client": client,
                "identity": "I_IDENTITY",
                "guest": loadConfig()["Auth"]["enable_guest"],
                "ignore_versions": "",
                "scene": repositories.SCENE_ACCOUNT,
                "name": "原神",
                "disable_regist": loadConfig()["Login"]["disable_regist"],
                "enable_email_captcha": loadConfig()["Login"]["enable_email_captcha"],
                "thirdparty": ["tp", "fb", "tw"],  # taptap facebook twitter
                "disable_mmt": loadConfig()["Login"]["disable_mmt"],
                "server_guest": loadConfig()["Auth"]["enable_guest"],
                "thirdparty_ignore": {},
                "enable_ps_bind_account": loadConfig()["Login"]["enable_ps_bind_account"],
                "thirdparty_login_configs": {
                    "fb": {
                        "token_type": "TK_GAME_TOKEN",
                        "game_token_expires_in": 2592000,
                    },
                    "tw": {
                        "token_type": "TK_GAME_TOKEN",
                        "game_token_expires_in": 2592000,
                    },
                },
                "initialize_firebase": loadConfig()["Login"]["initialize_firebase"],
                "bbs_auth_login": loadConfig()["Login"]["bbs_auth_login"],
                "bbs_auth_login_ignore": [],
                "fetch_instance_id": loadConfig()["Login"]["fetch_instance_id"],
                "enable_flash_login": loadConfig()["Login"]["enable_flash_login"],
            }
        },
    )


# 获取协议信息
@app.route("/hk4e_cn/mdk/agreement/api/getAgreementInfos", methods=["GET"])
@app.route("/hk4e_global/mdk/agreement/api/getAgreementInfos", methods=["GET"])
def mdk_agreement_api_get():
    return jsonRspWithMsg(
        repositories.RES_SUCCESS, "OK", {"data": {"marketing_agreements": []}}
    )


# 协议比较(https://sandbox-sdk-os.hoyoverse.com)
# 包含CBT2-3
@app.route("/combo/granter/api/getProtocol", methods=["POST", "GET"])
@app.route("/hk4e_cn/combo/granter/api/compareProtocolVersion", methods=["POST", "GET"])
@app.route("/hk4e_cn/combo/granter/api/getProtocol", methods=["POST", "GET"])
@app.route("/hk4e_global/combo/granter/api/compareProtocolVersion", methods=["POST", "GET"])
@app.route("/hk4e_global/combo/granter/api/getProtocol", methods=["POST", "GET"])
def combo_granter_api_protocol():
    return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{
            "data": {
                "modified": loadConfig()["Other"]["modified"],
                "protocol": {
                    "id": 0,
                    "app_id": 4,
                    "language": "zh-cn",
                    "user_proto": "",
                    "priv_proto": "",
                    "major": 12,
                    "minimum": 0,
                    "create_time": "0",
                    "teenager_proto": "",
                    "third_proto": "",
                    "full_priv_proto": "",
                },
            }
        },
    )


# 获取SDKCombo配置信息
@app.route("/combo/box/api/config/sdk/combo", methods=["GET"])
def combo_box_api_config_sdk_combo():
    return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{
            "data": {
                "vals": {
                    "telemetry_config": '{\n"dataupload_enable": 1\n}',
                    "new_register_page_enable": loadConfig()["Other"]["new_register_page_enable"],
                    "disable_email_bind_skip": loadConfig()["Login"]["disable_email_bind_skip"],
                    "kcp_enable": loadConfig()["Other"]["kcp_enable"],
                    "enable_web_dpi": loadConfig()["Other"]["enable_web_dpi"],
                    "network_report_config": '{ "enable": 1, "status_codes": [206], "url_paths": ["dataUpload"] }',
                    "email_bind_remind_interval": "7",  # 不知道
                    "kibana_pc_config": '{ "enable": 1, "level": "Info", "modules": ["download"] }',
                    "pay_payco_centered_host": "bill.payco.com",
                    "list_price_tierv2_enable": loadConfig()["Other"]["list_price_tierv2_enable"],
                    "email_bind_remind": loadConfig()["Login"]["email_bind_remind"],
                    "payment_cn_config": '{ "h5_cashier_enable": 0, "h5_cashier_timeout": 3}',
                }
            }
        },
    )


# 预加载
@app.route("/combo/box/api/config/sw/precache", methods=["GET"])
def combo_box_api_config_sw_precache():
    return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{
            "data": {
                "vals": {
                    "url": "https://webstatic.mihoyo.com/sw.html",
                    "enable": loadConfig()["Other"]["serviceworker"],  # 是否加载ServiceWorker进行分析
                }
            }
        },
    )


# 问卷调查
@app.route("/device-fp/api/getExtList", methods=["GET"])
def device_fp_get_ext_list():
    return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{
            "data": {
                "code": 200,
                "msg": "ok",
                "ext_list": [
                    "userAgent",
                    "browserScreenSize",
                    "maxTouchPoints",
                    "isTouchSupported",
                    "browserLanguage",
                    "browserPlat",
                    "browserTimeZone",
                    "webGlRender",
                    "webGlVendor",
                    "numOfPlugins",
                    "listOfPlugins",
                    "screenRatio",
                    "deviceMemory",
                    "hardwareConcurrency",
                    "cpuClass",
                    "ifNotTrack",
                    "ifAdBlock",
                    "hasLiedLanguage",
                    "hasLiedResolution",
                    "hasLiedOs",
                    "hasLiedBrowser",
                ],
                "pkg_list": [],
                "pkg_str": "",
            }
        },
    )


# 设备上报
@app.route("/device-fp/api/getFp", methods=["POST"])
def device_report():
    return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{"data": {"device_fp": "38d7ecd67b187", "code": 200, "msg": "ok"}},)  # 假的


# 抓出来的我也不知道是什么 似乎是玩家登录信息
@app.route("/combo/guard/api/ping", methods=["POST"])
@app.route("/hk4e_cn/combo/guard/api/ping", methods=["POST"])
@app.route("/hk4e_cn/combo/guard/api/ping2", methods=["POST"])
@app.route("/hk4e_global/combo/guard/api/ping", methods=["POST"])
@app.route("/hk4e_global/combo/guard/api/ping2", methods=["POST"])
def pingResponse():
    return jsonRsp(repositories.RES_SUCCESS, {})


# 消费提醒
@app.route("/common/hk4e_cn/announcement/api/consumeRemind", methods=["GET"])
@app.route("/common/hk4e_global/announcement/api/consumeRemind", methods=["GET"])
def consume_remind():
    return jsonRspWithMsg(repositories.RES_SUCCESS, "OK", {"data": []})
