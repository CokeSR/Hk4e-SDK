try:
    from __main__ import app
except ImportError:
    from main import app

import os
import src.tools.repositories       as repositories

from flask                          import render_template, send_file
from src.tools.loadconfig           import loadConfig
from src.tools.response             import jsonRspWithMsg
from src.tools.action.announceSend  import announce_send


def send_res(file_path):
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "Not found"


# ===================== 公告模块 ===================== #
# 公告功能
@app.route("/common/hk4e_cn/announcement/api/getAlertAnn", methods=["GET"])
@app.route("/common/hk4e_global/announcement/api/getAlertAnn", methods=["GET"])
def get_alertann():
    return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{
            "data": {
                "alert": loadConfig()["Announce"]["alert"],
                "alert_id": 0,
                "remind": loadConfig()["Announce"]["remind"],
                "extra_remind": loadConfig()["Announce"]["extra_remind"],
            }
        },
    )


# 蓝贴
@app.route("/admin/swpreload/hk4e_cn/zh-cn.json", methods=["GET"])
def blue_post():
    file_path = repositories.ANNOUNCE_BLUE_PATH
    return send_res(file_path)


# 获取公告(进门前获取content和list，进门后获取ann pic content 用是否有level字段来区分)
@app.route("/common/hk4e_cn/announcement/api/getAlertPic", methods=["GET"])
@app.route("/common/hk4e_global/announcement/api/getAlertPic", methods=["GET"])
# 进门前 getAnnList 没有 level
@app.route("/common/hk4e_cn/announcement/api/getAnnList", methods=["GET"])
@app.route("/common/hk4e_global/announcement/api/getAnnList", methods=["GET"])
def get_ann_list():
    level = ""
    return announce_send(level)


# 游戏外level=undefined 要注意一下
@app.route("/common/hk4e_cn/announcement/api/getAnnContent", methods=["GET"])
@app.route("/common/hk4e_global/announcement/api/getAnnContent", methods=["GET"])
def get_ann_content():
    level = "undefined"
    return announce_send(level)


# 公告模块
@app.route("/hk4e/announcement/index.html", methods=["GET"])
def handle_announcement():
    return render_template("announce/announcement.tmpl")


# 获取字体
@app.route("/hk4e_cn/combo/granter/api/getFont", methods=["GET"])
@app.route("/hk4e_global/combo/granter/api/getFont", methods=["GET"])
def get_font():
    file_path = repositories.ANNOUNCE_FONT_PATH
    return send_res(file_path)


@app.route("/upload/font-lib/2023/03/01/<name>.ttf", methods=["GET"])
def get_font_cncb(name):
    if name == "2c148f36573625fc03c82579abd26fb1_1167469228143141125":
        file_path = repositories.CB_LOGIN_FONT_PATH_01
    elif name == "4398dec1a0ffa3d3ce99ef1424107550_4765013443347169028":
        file_path = repositories.CB_LOGIN_FONT_PATH_02
    else:
        return f"Not Found vaule: {name}.ttf"
    return send_res(file_path)


# 资源文件
@app.route("/hk4e/announcement/<name>.js", methods=["GET"])
def get_javascript_res(name):
    if name == "2_2e4d2779ad3d19e6406f":
        file_path = repositories.ANNOUNCE_JS_PATH1
    elif name == "vendors_3230378b06826ebc94d3":
        file_path = repositories.ANNOUNCE_JS_PATH2
    elif name == "bundle_9f9d2fd05b63fd8decfc":
        file_path = repositories.ANNOUNCE_JS_PATH3
    else:
        return f"Not Found vaule: {name}.js"
    return send_res(file_path)


@app.route("/hk4e/announcement/<name>.css", methods=["GET"])
def get_css_res(name):
    if name == "2_cb04d2d72d7555e2ab83":
        file_path = repositories.ANNOUNCE_CSS_PATH1
    elif name == "bundle_dad917ca6970b9fa0ec0":
        file_path = repositories.ANNOUNCE_CSS_PATH2
    else:
        return f"Not Found vaule: {name}.css"
    return send_res(file_path)


@app.route("/dora/lib/firebase-performance/8.2.7/<name>.js", methods=["GET"])
def get_fprjs(name):
    if name == "firebase-performance-standalone-cn":
        file_path = repositories.ANNOUNCE_FPTJS_PATH
    elif name == "firebase-performance-standalone":
        file_path = repositories.ANNOUNCE_FPTJS_PATH
    else:
        return f"Not Found vaule: {name}.js"
    return send_res(file_path)


@app.route("/dora/lib/vue/2.6.11/vue.min.js", methods=["GET"])
def get_vue_min():
    file_path = repositories.ANNOUNCE_VUEMIN_PATH
    return send_res(file_path)


@app.route("/dora/biz/mihoyo-analysis/v2/main.js", methods=["GET"])
def get_mainjs():
    file_path = repositories.ANNOUNCE_MAINJS_PATH
    return send_res(file_path)


@app.route("/dora/biz/mihoyo-h5log/v1.0/main.js", methods=["GET"])
def get_mainh5js():
    file_path = repositories.ANNOUNCE_MAINH5JS_PATH
    return send_res(file_path)
