try:
    from __main__ import app
except ImportError:
    from main import app

import yaml
import src.tools.repositories as repositories

from flask                      import jsonify, request, send_from_directory, render_template, url_for
from src.tools.action.dbGet     import getMysqlConn
from src.tools.response         import jsonRsp, jsonRspWithMsg
from src.tools.loadconfig       import loadConfig
from src.tools.logger.system    import logger              as sys_log

# ====================SDKServer====================#
# 首页
@app.route("/", methods=["GET"])
@app.route("/sandbox/index.html", methods=["GET"])
def account_index():
    return render_template("account/index.tmpl")


# 检查SDK配置(https://testing-abtest-api-data-sg.mihoyo.com) 不知道什么用 不写config
@app.route("/config", methods=["GET", "POST"])
@app.route("/data_abtest_api/config/experiment/list", methods=["GET", "POST"])
def abtest_config_experiment_list():
    return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{
            "data": [
                {
                    "code": 1000,
                    "type": 2,
                    "config_id": "246",
                    "period_id": "5147_328",
                    "version": "2",
                    "configs": {
                        "cardType": "native",
                        "cashierId": "34b2b997-b1c7-412b-b5f2-eeef09a03d92",
                    },
                },
                {
                    "code": 1000,
                    "type": 2,
                    "config_id": "245",
                    "period_id": "5145_536",
                    "version": "1",
                    "configs": {"foldOther": "true"},  # 简化界面？
                },
                {
                    "code": 1000,
                    "type": 2,
                    "config_id": "244",
                    "period_id": "5144_535",
                    "version": "1",
                    "configs": {"expandMixedQRcode": "true"},  # 二维码
                },
                {
                    "code": 1010,
                    "type": 2,
                    "config_id": "243",
                    "period_id": "",
                    "version": "",
                    "configs": {"disableMarket": "false"},  # 市场？
                },
            ]
        },
    )


# ===================== 状态收集 ===================== #
# log收集
@app.route("/log", methods=["POST"])
@app.route("/v1/events", methods=["POST"])
@app.route("/h5/upload", methods=["POST"])
@app.route("/log/sdk/upload", methods=["POST"])
@app.route("/crash/dataUpload", methods=["POST"])
@app.route("/client/event/dataUpload", methods=["POST"])
@app.route("/sdk/dataUpload", methods=["POST"])
@app.route("/common/h5log/log/batch", methods=["POST"])
def sdk_log():
    # 启用则接收客户端传入日志
    if loadConfig()['Setting']['high_frequency_logs']:
        sys_log.info(f"主机 {request.remote_addr} 日志收集: {request.json}")

    return jsonRsp(repositories.RES_SUCCESS, {})


# 红点配置 一般infos为空 特别写的
@app.route("/hk4e_cn/combo/red_dot/list", methods=["POST"])
@app.route("/hk4e_global/combo/red_dot/list", methods=["POST"])
def red_dot():
    return jsonRspWithMsg(repositories.RES_SUCCESS, "ok", {"infos": []})


"""
def red_dot():
    return jsonRsp(define.RES_SUCCESS, "ok", {
        "infos": [
            {
                "red_point_type": 2201,
                "content_id": 184,
                "display": loadConfig()["Reddot"]["display"]
            }
        ]
    })
"""


# ====================== mi18n ====================== #
@app.route("/admin/mi18n/plat_cn/m2020030410/m2020030410-version.json", methods=["GET"])
@app.route("/admin/mi18n/plat_oversea/m202003049/m202003049-version.json", methods=["GET"])
@app.route("/admin/mi18n/plat_oversea/m2020030410/m2020030410-version.json", methods=["GET"])
@app.route("/admin/mi18n/bh3_usa/20190628_5d15ba66cd922/20190628_5d15ba66cd922-version.json",methods=["GET"],)
def mi18n_version():
    return jsonRsp(repositories.RES_SUCCESS, {"version": 79})


@app.route("/admin/mi18n/plat_os/m09291531181441/m09291531181441-version.json", methods=["GET"])
def min18_os_version():
    return jsonRsp(repositories.RES_SUCCESS, {"version": 16})


@app.route("/admin/mi18n/plat_cn/m2020030410/m2020030410-<language>.json", methods=["GET"])
@app.route("/admin/mi18n/plat_oversea/m2020030410/m2020030410-<language>.json", methods=["GET"])
@app.route("/admin/mi18n/bh3_global/20190812_5d51512fdef47/20190812_5d51512fdef47-<language>.json", methods=["GET"])
def mi18n_serve(language):
    return send_from_directory(repositories.MI18N_PATH, f"{language}.json")


@app.route("/hk4e_cn/game/config.yaml", methods=["GET"])
@app.route("/hk4e_global/game/config.yaml", methods=["GET"])
def view_config():
    config_path = repositories.CONFIG_FILE_PATH
    sys_log.warning(f"主机 {request.remote_addr} 获取 config 配置")
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config_data = yaml.safe_load(file)
        return config_data
    except FileNotFoundError:
        return "Config file not found"
    except Exception as e:
        return f"Error reading config file: {str(e)}"


@app.route("/hk4e_cn/game/keys/<name>", methods=["GET"])
@app.route("/hk4e_global/game/keys/<name>", methods=["GET"])
def view_keys_pem(name):
    sys_log.warning(f"主机 {request.remote_addr} 获取 {name} 配置")
    cursor = getMysqlConn().cursor()
    if name == "authverify":
        cursor.execute("SELECT * FROM `t_verifykey_config` WHERE `type` = 'authkey'")
        authkeys = cursor.fetchall()
        return authkeys
    if name == "password":
        cursor.execute("SELECT * FROM `t_verifykey_config` WHERE `type` = 'rsakey'")
        rsakeys = cursor.fetchall()
        return rsakeys


@app.route("/hk4e_cn/game/map", methods=["GET"])
@app.route("/hk4e_global/game/map", methods=["GET"])
def site_map():
    output = []
    seen_routes = set()
    sys_log.warning(f"主机 {request.remote_addr} 获取全局路由配置")
    for rule in app.url_map.iter_rules():
        methods = ",".join(sorted(rule.methods - {"OPTIONS", "HEAD"}))

        try:
            url = url_for(rule.endpoint, **(rule.defaults or {}))
        except Exception:
            url = str(rule)

        route_id = (url, methods)
        if route_id not in seen_routes:
            output.append(
                {
                    "url": url,
                    "methods": methods,
                    "function": rule.endpoint,  # 方法名
                    "parameters": list(rule.arguments),
                }
            )
            seen_routes.add(route_id)
    return jsonify(output)
